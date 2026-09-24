"""Verify already-serialized oracle panels. No sampling or model inference."""
import pathlib,json,argparse
from reproduce_table1 import verify_transfer_oracle
from reproduce_table2 import verify_external_oracle
def verify(root):
 result={'transfer':verify_transfer_oracle(root),'external':verify_external_oracle(root)}
 root=pathlib.Path(root);(root/'reproduced').mkdir(exist_ok=True)
 (root/'reproduced/oracle_checks.json').write_text(json.dumps(result,indent=2),encoding='utf8')
 print('PASS oracle identities: transfer Z/P and external n=10/15');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[1]);verify(p.parse_args().root)
