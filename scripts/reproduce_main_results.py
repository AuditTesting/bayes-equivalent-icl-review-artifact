"""Offline CPU numerical reconstruction of frozen results; no RNG or model calls."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('MKL_NUM_THREADS','1')
import pathlib,json,csv,time,importlib,sys
from verify_hashes import verify as verify_hashes
def main():
 root=pathlib.Path(__file__).resolve().parents[1];start=time.perf_counter();verify_hashes(root)
 expected=list(csv.DictReader(open(root/'expected/main_result_values.csv',encoding='utf8')))
 expected={(r['item'],r['context'],r['metric']):r for r in expected};allrows=[];checks=0;failures=[]
 for name in ['figure2','figure3','figure4','table1','table2']:
  rows=importlib.import_module('reproduce_'+name).reproduce(root)
  for r in rows:
   key=(r['item'],r['context'],r['metric']);ref=expected.pop(key);status='PASS'
   for actual,desired in [('estimate','full_precision_value'),('lower95','lower95'),('upper95','upper95')]:
    if r[actual] is None:
     if ref[desired] not in ('','None'):status='FAIL'
    else:
     checks+=1
     if abs(float(r[actual])-float(ref[desired]))>float(ref['tolerance']):status='FAIL'
   if status!='PASS':failures.append(key)
   r['status']=status;allrows.append(r)
   print(status,r['item'],r['context'],r['metric'])
 if expected:raise ValueError('Mapped claims not reconstructed: '+str(list(expected)))
 (root/'reproduced').mkdir(exist_ok=True)
 (root/'reproduced/main_results.json').write_text(json.dumps(allrows,indent=2),encoding='utf8')
 with open(root/'reproduced/main_results.csv','w',newline='',encoding='utf8') as f:
  fields=['item','context','metric','estimate','lower95','upper95','status'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(allrows)
 from verify_oracle_identities import verify
 verify(root)
 result={'status':'FAIL' if failures else 'PASS','mapped_claims':len(allrows),'numeric_comparisons':checks,'failures':failures,'seconds':time.perf_counter()-start,'new_random_draws':0,'model_forwards':0,'training_updates':0}
 (root/'reproduced/verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result))
 if failures:sys.exit(1)
if __name__=='__main__':main()
