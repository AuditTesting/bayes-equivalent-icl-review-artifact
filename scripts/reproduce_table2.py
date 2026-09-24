"""Reconstruct S24 from saved predictions and saved resampling indices; no RNG."""
import csv,json,pathlib,argparse
import numpy as np
METRICS=['R_APPROX','E_PAIR','E_SHARED','E_WITHIN','F_WITHIN','ABS_DELTA','RMS_DELTA']
def load(path):
 with np.load(path,allow_pickle=False) as z:return {k:z[k] for k in z.files}
def stats(c):
 m=c.mean(0);return np.array([m[0],m[1],m[2],m[3],m[3]/m[1],m[4],np.sqrt(m[5])])
def reproduce(root):
 root=pathlib.Path(root);f=root/'frozen/table2_external'
 co=list(csv.DictReader(open(f/'COHORT_RESULTS.csv',encoding='utf8')));ci=list(csv.DictReader(open(f/'BOOTSTRAP_INTERVALS.csv',encoding='utf8')));out=[]
 for n in (10,15):
  a=load(f/('predictions_n%d.npz'%n));idx=load(f/('bootstrap_indices_n%d.npz'%n))['indices'];m0=a['m0'];m1=a['m1'];mb=a['mB'];delta=m1-m0
  assert m0.shape==(4096,) and idx.shape==(2000,4096)
  assert np.array_equal(a['selected_demo_row'],np.arange(4096)%n)
  c=np.column_stack(((m0-mb)**2,((m0-mb)**2+(m1-mb)**2)/2,((m0+m1)/2-mb)**2,delta**2/4,abs(delta),delta**2))
  v=stats(c);b=np.array([stats(c[i]) for i in idx]);lo,hi=np.quantile(b,[.025,.975],axis=0)
  assert abs(v[1]-v[2]-v[3])<1e-10
  assert abs(v[4]-v[6]**2/(4*v[1]))<1e-10
  counts=np.bincount(a['selected_demo_row'],minlength=n)
  assert all(np.array_equal(np.bincount(a['selected_demo_row'][i],minlength=n),counts) for i in idx)
  ref=next(r for r in co if int(r['n'])==n)
  for k,value,l,h in zip(METRICS,v,lo,hi):
   ir=next(r for r in ci if int(r['n'])==n and r['metric']==k)
   shown=(('%.2f%% [%.2f%%, %.2f%%]'%(100*value,100*l,100*h)) if k=='F_WITHIN' else ('%.4f [%.4f, %.4f]'%(value,l,h))) if k in ('R_APPROX','RMS_DELTA','F_WITHIN') else 'Supplement: full precision in artifact'
   out.append(dict(item='Table 2',metric=k,context='n=%d'%n,estimate=float(value),lower95=float(l),upper95=float(h),expected_estimate=float(ref[k]),expected_lower95=float(ir['lower95']),expected_upper95=float(ir['upper95']),source_file='frozen/table2_external/predictions_n%d.npz'%n,source_section=k+'; n=%d'%n,uncertainty_source='S24 saved bootstrap_indices_n%d.npz'%n,draws=2000,sampling_unit='paired base episode',strata='selected demonstration position',percentile='linear 2.5/97.5',reproduction_level=3,tolerance=1e-10,displayed_value=shown))
  for key,val in [('task_MSE',np.mean((m0-a['yq'])**2)),('minimum_norm_task_MSE',np.mean((mb-a['yq'])**2)),('mean_posterior_variance',a['vB'].mean())]:
   out.append(dict(item='Table 2',metric=key,context='n=%d'%n,estimate=float(val),lower95=None,upper95=None,expected_estimate=float(ref[key]),expected_lower95=None,expected_upper95=None,source_file='frozen/table2_external/predictions_n%d.npz'%n,source_section=key,uncertainty_source='none;point estimate',draws=0,sampling_unit='base episode',strata='none',percentile='none',reproduction_level=2,tolerance=1e-10,displayed_value='%.2f'%val))
 return out
def verify_external_oracle(root):
 root=pathlib.Path(root);out={}
 for n in (10,15):
  a=load(root/'frozen/table2_external'/('panel_n%d.npz'%n));pred=load(root/'frozen/table2_external'/('predictions_n%d.npz'%n));x=a['x'];y=a['y'];xp=a['xp'];yp=a['yp'];rows=a['selected_demo_row'];ii=np.arange(4096)
  xx=x.copy();yy=y.copy();xx[ii,rows]*=-1;yy[ii,rows]*=-1
  assert xx.tobytes()==xp.tobytes() and yy.tobytes()==yp.tobytes()
  xx[ii,rows]*=-1;yy[ii,rows]*=-1;assert xx.tobytes()==x.tobytes() and yy.tobytes()==y.tobytes()
  maxima=np.zeros(6)
  for start in range(0,4096,256):
   end=start+256;states=[]
   for X,Y in [(x[start:end,:n].astype(float),y[start:end,:n].astype(float)),(xp[start:end,:n].astype(float),yp[start:end,:n].astype(float))]:
    u,s,vh=np.linalg.svd(X,full_matrices=False);assert np.all((s>20*np.finfo(float).eps*s[:,:1]).sum(1)==n)
    pinv=(vh.transpose(0,2,1)/s[:,None,:])@u.transpose(0,2,1);mu=(pinv@Y[:,:,None])[:,:,0];P=pinv@X;q=x[start:end,n].astype(float)
    m=np.einsum('bi,bi->b',q,mu);v=np.einsum('bi,bij,bj->b',q,np.eye(20)[None]-P,q);states.append((mu,P,m,v))
   errors=[np.max(abs(states[0][j]-states[1][j])) for j in range(4)]+[np.max(abs(states[0][2]-pred['mB'][start:end])),np.max(abs(states[0][3]-pred['vB'][start:end]))]
   maxima=np.maximum(maxima,errors)
  assert maxima.max()<1e-10
  out[str(n)]={'bases':4096,'rank_failures':0,'bitwise_sign_and_involution':'PASS','posterior_mean_max':maxima[0],'projector_max':maxima[1],'predictive_mean_max':maxima[2],'predictive_variance_max':maxima[3],'stored_mB_max':maxima[4],'stored_vB_max':maxima[5]}
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[1]);args=p.parse_args();rows=reproduce(args.root)
 for r in rows:
  for a,b in [('estimate','expected_estimate'),('lower95','expected_lower95'),('upper95','expected_upper95')]:assert r[a] is None or abs(r[a]-r[b])<=r['tolerance']
 (args.root/'reproduced').mkdir(exist_ok=True);(args.root/'reproduced/table2.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print('PASS Table 2:',len(rows),'mapped metrics')
