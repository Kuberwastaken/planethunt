"""Acquire public TESS data; never submits candidates. Original research wrapper.
Uses read_lc_fits and mast_url from Eumemic's MIT-licensed pipeline.
"""
import os,sys,json,time,hashlib,io,argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor,as_completed
import numpy as np,pandas as pd,requests
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'upstream-eumemic/pipeline'))
from common import mast_url
from improvements.read_lc import read_lc_fits

def targets():
 p=pd.read_csv(ROOT/'catalogs/unsearched_ranked_excluding_known.csv')
 high=p[(p.n_sectors<=16)&(p.Rad<0.9)&(p.n_sectors>=4)].head(80).copy();high['branch']='high_sensitivity_usp'
 partial=p[p.has_2min & (p.n_2min<=3)&(p.n_sectors>=5)&(p.n_sectors<=16)].head(40).copy();partial['branch']='partial_2min'
 ffi=p[(~p.has_2min)&(p.snr_ref<10)].head(60).copy();ffi['branch']='lower_rank_ffi'
 out=pd.concat([high,partial,ffi]).drop_duplicates('TIC')
 out.to_csv(ROOT/'targets.csv',index=False)
 print('targets',len(out),out.branch.value_counts().to_dict(),flush=True)
 return out

def query(ids):
 req={'service':'Mast.Caom.Filtered','format':'json','pagesize':50000,'page':1,'params':{'columns':'*','filters':[{'paramName':'target_name','values':list(map(str,ids))},{'paramName':'dataproduct_type','values':['timeseries']},{'paramName':'provenance_name','values':['SPOC','TESS-SPOC','QLP']}]}}
 r=requests.post('https://mast.stsci.edu/api/v0/invoke',data={'request':json.dumps(req)},timeout=90);r.raise_for_status();d=r.json()
 if d.get('status')!='COMPLETE':raise RuntimeError(str(d)[:300])
 return d

def fetch(row):
 url=mast_url(row['dataURL']); rec={'uri':row['dataURL'],'url':url,'provenance':row['provenance_name'],'sector':int(row['sequence_number'])}
 for attempt in range(2):
  try:
   r=requests.get(url,timeout=40);r.raise_for_status()
   if r.content[:6]!=b'SIMPLE':raise ValueError('Not FITS')
   rec.update(sha256=hashlib.sha256(r.content).hexdigest(),bytes=len(r.content),fetched_utc=pd.Timestamp.now(tz='UTC').isoformat())
   return r.content,rec
  except Exception as e:rec['error']=str(e)
 return None,rec

def download(job):
 tic,rows=job; path=ROOT/'lightcurves'/f'{tic}.npz'
 if path.exists():return {'tic':tic,'status':'cached'}
 parts=[];manifest=[]
 with ThreadPoolExecutor(2) as ex:
  for blob,rec in ex.map(fetch,rows):
   manifest.append(rec)
   if blob is None:continue
   try:
    d=read_lc_fits(io.BytesIO(blob),rec['provenance'])
    for key in ['flux_column','error_source','exposure_source','raw_flux_fallback','quality_column_missing']:rec[key]=d.get(key)
    if len(d['time'])<100:raise ValueError('Too few valid points')
    n=len(d['time']);d['sector']=np.full(n,rec['sector']);d['exptime']=np.full(n,d['exptime']);parts.append(d)
   except Exception as e:rec['parse_error']=str(e)
 (ROOT/'manifests'/f'{tic}.json').write_text(json.dumps(manifest,indent=2))
 if not parts:return {'tic':tic,'status':'failed','errors':manifest}
 keys=['time','flux','flux_err','sector','exptime','cx','cy','bkg'];arrays={k:np.concatenate([d[k] for d in parts]) for k in keys}
 order=np.argsort(arrays['time']);arrays={k:v[order] for k,v in arrays.items()}
 tmp=path.with_suffix('.tmp.npz')
 np.savez_compressed(tmp,**arrays,authors=np.array([f"{m['sector']}:{m['provenance']}" for m in manifest if not m.get('error') and not m.get('parse_error')]))
 tmp.replace(path)
 return {'tic':tic,'status':'ok','n_points':len(order),'sectors':len(parts)}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=4);a=ap.parse_args()
 tg=pd.read_csv(ROOT/'targets.csv') if (ROOT/'targets.csv').exists() else targets()
 mf=ROOT/'manifests/selected_products.csv'
 if not mf.exists():
  raw=query(tg.TIC.astype(int).tolist());(ROOT/'manifests/mast_observations.json').write_text(json.dumps(raw))
  m=pd.DataFrame(raw['data']);m=m[m.dataURL.fillna('').str.endswith(('lc.fits','llc.fits'))].copy()
  m['TIC']=m.target_name.astype(int);m['rank']=m.provenance_name.map({'SPOC':0,'TESS-SPOC':1,'QLP':2})
  m=m[~((m.provenance_name=='SPOC')&(m.t_exptime<100))]
  m=m[(m.sequence_number>=1)&(m.sequence_number<=200)]
  m=m.sort_values(['TIC','sequence_number','rank','t_exptime']).drop_duplicates(['TIC','sequence_number']);m.to_csv(mf,index=False)
 else:m=pd.read_csv(mf)
 print('selected products',len(m),'stars',m.TIC.nunique(),flush=True)
 groups={int(k):v.to_dict('records') for k,v in m.groupby('TIC')}
 jobs=[(int(k),groups[int(k)]) for k in tg.TIC if int(k) in groups]
 with ProcessPoolExecutor(a.workers) as ex:
  for fut in as_completed([ex.submit(download,j) for j in jobs]):
   rec=fut.result();print(json.dumps(rec),flush=True)
   with open(ROOT/'download_log.jsonl','a') as f:f.write(json.dumps(rec)+'\n')
