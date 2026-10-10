"""Fixed-ephemeris independent extraction and original-pixel retrieval."""
import json,sys,re,hashlib
from concurrent.futures import ThreadPoolExecutor
import requests,pandas as pd
from pilot import ROOT,acquire,dump
from improvements.independent_vet import vet
sid='2103792461826460288'
r=json.loads((ROOT/'results'/f'{sid}.json').read_text());s=r['signals'][0]
out=[]
for o in json.loads((ROOT/'candidate_neighbor_mast.json').read_text())['data']:
 nid=o['target_name'].split()[-1];kic=5689116 if nid=='2103792427466721792' else 5689163
 d=acquire({'source_id':nid,'dataURL':o['dataURL'],'kic':kic,'tpforg':kic},min_quarters=1)
 v=vet({k:d[k] for k in ['time','flux','flux_err','sector','exptime']},s['period'],s['t0_btjd'],s['duration_hr']/24,holdout=tuple(r['holdout_quarters']),controls=0)
 out.append({'source_id':nid,'kic':kic,'vet':v});print(nid,v['primary'],flush=True)
dump(ROOT/'candidate_neighbor_vetting.json',out)
prod=pd.read_csv(ROOT/'candidate_primary_products.csv')
prod=prod[prod.productFilename.str.endswith('_lpd-targ.fits.gz')].copy()
(ROOT/'pixels').mkdir(exist_ok=True)
def get(row):
 f=ROOT/'pixels'/row['productFilename'];url='https://mast.stsci.edu/api/v0.1/Download/file?uri='+row['dataURI']
 if not f.exists():
  rr=requests.get(url,timeout=120);rr.raise_for_status();f.write_bytes(rr.content)
 return {'file':f.name,'url':url,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
with ThreadPoolExecutor(4) as ex:man=list(ex.map(get,prod.to_dict('records')))
dump(ROOT/'pixels/manifest.json',man);print('pixel quarters',len(man),flush=True)
