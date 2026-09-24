"""Verify every distributed file against the published SHA256 manifest."""
import pathlib,hashlib,argparse
def verify(root):
 root=pathlib.Path(root).resolve();count=0;listed=set()
 for line in (root/'MANIFEST.sha256').read_text(encoding='utf8').splitlines():
  digest,name=line.split('  ',1);p=(root/name).resolve()
  if root not in p.parents:raise ValueError('Unsafe manifest path')
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b)
  if h.hexdigest()!=digest:raise ValueError('Hash mismatch: '+name)
  listed.add(name);count+=1
 actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and not set(p.relative_to(root).parts).intersection({'reproduced','__pycache__','.venv','.git'}) and p.name!='MANIFEST.sha256'}
 if actual!=listed:raise ValueError('Unlisted/missing files: '+str(sorted(actual.symmetric_difference(listed))))
 print('PASS integrity:',count,'files');return count
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[1]);verify(p.parse_args().root)
