"""Exploratory search with predeclared final-season holdout and matched inverted controls.
Candidate generation uses Eumemic MIT search.py + Paras Chopra MIT lcsearch.py.
Not a validated planet classifier. Null controls estimate pipeline artifacts, not a formal FAP.
"""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
import sys,json,time,traceback,argparse,hashlib
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'upstream-tess/pipeline'))
import lcsearch as L
sys.path.insert(0,str(ROOT.parent/'upstream-eumemic/pipeline'))
import search as E
from fastbls import seasons

def subset(d,m):return {k:v[m] for k,v in d.items() if isinstance(v,np.ndarray) and v.shape==d['time'].shape}

def one(job):
 row,mode,inverted=job; tic=int(row['TIC']);tag=f'{tic}_{mode}'+('_inverted' if inverted else '')
 path=ROOT/'results'/f'{tag}.json'
 if path.exists():
  cached=json.loads(path.read_text())
  current=ROOT/'lightcurves'/f'{tic}.npz'
  if cached.get('status')=='ok' and cached.get('pipeline_version')==3 and cached.get('input_sha256')==hashlib.sha256(current.read_bytes()).hexdigest():return cached
 start=time.time();out={'tic':tic,'mode':mode,'inverted':inverted,'status':'started','signals':[],'pipeline_version':3,'holdout_caveat':'Previously processed targets have retrospective holdout after parser correction; inspect results_v1 to identify them.'}
 try:
  lcpath=ROOT/'lightcurves'/f'{tic}.npz'
  out['input_sha256']=hashlib.sha256(lcpath.read_bytes()).hexdigest()
  d=dict(np.load(lcpath));bad=[]
  rawgroups=seasons(d['time'])
  # Freeze split before searching. Latest chronological observing season is untouched by search.
  holdsectors=sorted(np.unique(d['sector'][rawgroups[-1]]).astype(int).tolist())
  hold=np.isin(d['sector'],holdsectors)
  out.update(holdout_sectors=holdsectors,discovery_sectors=sorted(np.unique(d['sector'][~hold]).astype(int).tolist()),rejected_sectors=bad)
  (ROOT/'manifests'/f'{tic}_split.json').write_text(json.dumps({'tic':tic,'rule':'last season separated by >20d gaps','holdout_sectors':holdsectors,'discovery_sectors':out['discovery_sectors']},indent=2))
  if len(rawgroups)<2 or (~hold).sum()<1000:raise ValueError('Insufficient separate discovery and holdout data')
  # Negate normalized input BEFORE identical detrending and clipping for null controls.
  if inverted:d['flux']=2-d['flux']
  # Per-sector operations do not mix the holdout into discovery processing.
  discovery,bad,noise=L.reject_bad_sectors(subset(d,~hold))
  out['rejected_discovery_sectors']=bad
  train=L.bin_lc(L.clean(discovery),bin_s=300 if mode=='usp' else 600)
  test=L.bin_lc(L.clean(subset(d,hold)),bin_s=300 if mode=='usp' else 600)
  
  t,y,e=train['time'],train['flux']-1,train['flux_err']
  rho=float(np.clip(row['Mass']/row['Rad']**3,0.2,100))
  if not np.isfinite(rho):rho=1.
  pmin,pmax=(0.2,0.5) if mode=='usp' else (0.5,25.)
  pmax=min(pmax,np.ptp(t)/3)
  out.update(n_train=len(t),n_holdout=len(test['time']),rho_sun=rho,pmin=pmin,pmax=pmax)
  keep=np.ones(len(t),dtype=bool)
  for rank in range(2):
   tt,yy,ee=t[keep],y[keep],e[keep]
   pc,coarse,nper,z=E.semicoherent_peak(tt,yy,ee,rho,pmin,pmax,k_peaks=40)
   if pc is None:break
   p,t0,dur,dep,snr=E.refine(tt,yy,ee,pc,rho,np.ptp(tt))
   st=E.event_stats(tt,yy,ee,p,t0,dur)
   ht=E.event_stats(test['time'],test['flux']-1,test['flux_err'],p,t0,dur)
   rec={'rank':rank+1,'period':p,'t0':t0,'duration_hr':dur*24,'depth_ppm':dep*1e6,'bls_snr':snr,'coarse_snr':coarse,'coarse_grid_count':int(nper),'rp_earth_approx':float(np.sqrt(max(dep,0))*row['Rad']/0.009168),'discovery':st,'holdout':ht}
   rec['screen_pass']=bool(snr>=8 and st['n_good_events']>=3 and ht['n_good_events']>=2 and ht['snr']>=3 and st['odd_even_sigma']<3 and abs(st['secondary']/st['secondary_err'])<3 and st['max_ses_frac']<0.65)
   out['signals'].append(rec)
   if snr<7.5:break
   keep &= np.abs(((t-t0+0.5*p)%p)-0.5*p)>dur
  out['status']='ok'
 except Exception as ex:out.update(status='error',error=str(ex),trace=traceback.format_exc())
 out['seconds']=round(time.time()-start,2)
 path.write_text(json.dumps(out,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)))
 return out

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=5);ap.add_argument('--limit',type=int,default=0);ap.add_argument('--mode',choices=['usp','regular','both'],default='both');ap.add_argument('--inverted',action='store_true');ap.add_argument('--tic',type=int);a=ap.parse_args()
 tg=pd.read_csv(ROOT/'targets.csv');tg=tg[[ (ROOT/'lightcurves'/f'{int(t)}.npz').exists() for t in tg.TIC]]
 if a.tic:tg=tg[tg.TIC==a.tic]
 if a.limit:tg=tg.head(a.limit)
 jobs=[]
 for row in tg.to_dict('records'):
  modes=['usp','regular'] if a.mode=='both' else [a.mode]
  for mode in modes:
   path=ROOT/'results'/f"{int(row['TIC'])}_{mode}{'_inverted' if a.inverted else ''}.json"
   valid=False
   if path.exists():
    try:
     rec=json.loads(path.read_text());valid=rec.get('pipeline_version')==3 and rec.get('status')=='ok' and rec.get('input_sha256')==hashlib.sha256((ROOT/'lightcurves'/f"{int(row['TIC'])}.npz").read_bytes()).hexdigest()
    except Exception:pass
   if not valid:jobs.append((row,mode,a.inverted))
 print('jobs',len(jobs),'workers',a.workers,flush=True)
 with ProcessPoolExecutor(a.workers) as ex:
  for fut in as_completed([ex.submit(one,j) for j in jobs]):
   r=fut.result();print(json.dumps({k:r.get(k) for k in ['tic','mode','inverted','status','seconds','error']}|{'signals':[{'period':s['period'],'snr':s['bls_snr'],'holdout_snr':s['holdout']['snr'],'screen_pass':s['screen_pass']} for s in r['signals']]}),flush=True)
