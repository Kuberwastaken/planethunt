"""Kepler Bonus background-M-star pilot. Exploratory, not a planet classifier.

Dates are explicitly converted BKJD -> BTJD by subtracting 2167 days.
Last ceil(25%) usable quarters reserved before period search. Flux selection
uses documented PSF FLUX, quality==0, positive errors and PSFFRAC>=0.5.
The search uses an assumed rho=5 solar (not a measured stellar parameter).
No radii/planet validation are inferred from that approximation.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,hashlib,io,json,sys,time,traceback
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np,pandas as pd,requests
from astropy.io import fits
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
sys.path.insert(0,str(PROJECT))
import run_search as R
from improvements.independent_vet import vet
import fastbls
_seasons=fastbls.seasons
def short_blocks(t,gap=20.,max_len=None):return _seasons(t,gap=gap,max_len=90. if max_len is None else max_len)
fastbls.seasons=short_blocks

def dump(p,d):
 p.write_text(json.dumps(d,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)))

def select(limit):
 d=pd.read_csv(ROOT/'eligible_before_catalogcheck.csv',dtype={'psf_avail':str})
 primary=pd.read_csv(ROOT.parent/'kepler_primary_targets.csv')
 d=d[~d.kic.isin(primary.kepid)]
 # Frozen catalog-based priority, before looking at any photometry.
 d=d.sort_values(['phot_g_mean_mag','gaia_designation']).head(limit).copy()
 d['source_id']=d.gaia_designation.str.split().str[-1]
 d.to_csv(ROOT/'pilot_targets.csv',index=False)
 req={'service':'Mast.Caom.Filtered','format':'json','pagesize':50000,'page':1,'params':{'columns':'*','filters':[{'paramName':'provenance_name','values':['KBONUS-BKG']},{'paramName':'target_name','values':d.gaia_designation.tolist()}]}}
 r=requests.post('https://mast.stsci.edu/api/v0/invoke',data={'request':json.dumps(req)},timeout=90);r.raise_for_status();j=r.json()
 if j.get('status')!='COMPLETE':raise ValueError(j.get('status'))
 dump(ROOT/'pilot_observations.json',j)
 obs=pd.DataFrame(j['data']);obs=obs.drop_duplicates('target_name');obs.to_csv(ROOT/'pilot_observations.csv',index=False)
 return d.merge(obs[['target_name','dataURL']],left_on='gaia_designation',right_on='target_name')

def acquire(row,min_quarters=6):
 sid=str(row['source_id']);npz=ROOT/'lightcurves'/f'{sid}.npz';fp=ROOT/'fits'/f'{sid}.fits'
 if npz.exists():return dict(np.load(npz))
 url='https://mast.stsci.edu/api/v0.1/Download/file?uri='+row['dataURL']
 if not fp.exists():
  r=requests.get(url,timeout=90);r.raise_for_status()
  if r.content[:6]!=b'SIMPLE':raise ValueError('Not FITS')
  fp.write_bytes(r.content)
 parts=[];quarters=[]
 with fits.open(fp,memmap=False) as h:
  exp=float(h[0].header.get('XPOSURE',1765.464))
  for hd in h:
   if not hd.name.startswith('LIGHTCURVE_Q'):continue
   q=int(hd.header['QUARTER']);frac=float(hd.header.get('PSFFRAC',0));d=hd.data
   if frac<.5:continue
   t=np.asarray(d['TIME'],float)-2167;f=np.asarray(d['FLUX'],float);e=np.asarray(d['FLUX_ERR'],float)
   good=(d['SAP_QUALITY']==0)&np.isfinite(t)&np.isfinite(f)&np.isfinite(e)&(e>0)
   if good.sum()<300:continue
   med=np.median(f[good])
   if med<=0:continue
   n=good.sum();sap=np.asarray(d['SAP_FLUX'],float);sm=np.nanmedian(sap[good])
   parts.append({'time':t[good],'flux':f[good]/med,'flux_err':e[good]/med,'sector':np.full(n,q),'exptime':np.full(n,exp),'sap_flux':sap[good]/sm if sm>0 else np.full(n,np.nan),'cx':np.asarray(d['CENTROID_COLUMN'])[good],'cy':np.asarray(d['CENTROID_ROW'])[good]})
   quarters.append({'quarter':q,'psffrac':frac,'crowdsap':float(hd.header.get('CROWDSAP',0)),'points':int(n)})
 if len(parts)<min_quarters:raise ValueError(f'Fewer than {min_quarters} usable quarters')
 d={k:np.concatenate([a[k] for a in parts]) for k in parts[0]};o=np.argsort(d['time']);d={k:v[o] for k,v in d.items()}
 np.savez_compressed(npz,**d)
 dump(ROOT/'manifests'/f'{sid}.json',{'source_id':sid,'url':url,'fits_sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'quarters':quarters,'time':'BTJD = BKJD - 2167; TDB','quality':'SAP_QUALITY == 0','flux_column':'FLUX (corrected PSF)','fetched_utc':pd.Timestamp.now(tz='UTC').isoformat()})
 return d

def one(row,inverted=False):
 sid=str(row['source_id']);dest=ROOT/'results'/f'{sid}{"_inverted" if inverted else ""}.json'
 if dest.exists():return json.loads(dest.read_text())
 out={'source_id':sid,'kic':int(row['kic']),'tpforg':int(row['tpforg']),'inverted':inverted,'signals':[],'pipeline':'kbonus_pilot_v1','status':'started'};start=time.time()
 try:
  d=acquire(row);out['input_sha256']=hashlib.sha256((ROOT/'lightcurves'/f'{sid}.npz').read_bytes()).hexdigest()
  qs=sorted(np.unique(d['sector']));hold=qs[-max(2,int(np.ceil(len(qs)*.25))):];out['holdout_quarters']=list(map(int,hold));out['discovery_quarters']=list(map(int,qs[:-len(hold)]))
  dump(ROOT/'manifests'/f'{sid}_split.json',{'holdout_quarters':out['holdout_quarters'],'rule':'last ceil(25%) usable quarters, minimum2, chosen before search'})
  raw={k:d[k].copy() for k in ('time','flux','flux_err','sector','exptime')}
  if inverted:
   d['flux']=2-d['flux'];raw['flux']=2-raw['flux'];d['sap_flux']=2-d['sap_flux']
  m=np.isin(d['sector'],hold);train=R.L.clean(R.subset(d,~m),window=1.);test=R.L.clean(R.subset(d,m),window=1.)
  t,y,e=train['time'],train['flux']-1,train['flux_err'];keep=np.ones(len(t),bool)
  for rank in range(2):
   tt,yy,ee=t[keep],y[keep],e[keep]
   p,coarse,ngrid,z=R.E.semicoherent_peak(tt,yy,ee,5.,.5,25.,k_peaks=40)
   if p is None:break
   p,t0,dur,depth,snr=R.E.refine(tt,yy,ee,p,5.,np.ptp(tt))
   st=R.E.event_stats(tt,yy,ee,p,t0,dur);ht=R.E.event_stats(test['time'],test['flux']-1,test['flux_err'],p,t0,dur)
   passed=bool(snr>=9 and st['n_good_events']>=3 and ht['n_good_events']>=3 and ht['snr']>=4 and st['odd_even_sigma']<3 and abs(st['secondary']/st['secondary_err'])<3 and st['max_ses_frac']<.5)
   s={'rank':rank+1,'period':p,'t0_btjd':t0,'duration_hr':dur*24,'depth_ppm':depth*1e6,'bls_snr':snr,'discovery':st,'holdout':ht,'screen_pass':passed}
   if passed:
    s['independent_vet']=vet(raw,p,t0,dur,holdout=tuple(hold),controls=24,holdout_was_unseen=True)
    # Independent extraction, not an independent telescope. No BLS fitting on SAP.
    sap=dict(raw);sap['flux']=d['sap_flux'];valid=np.isfinite(sap['flux']);sap={k:v[valid] for k,v in sap.items()}
    if len(sap['time'])>100:s['sap_fixed_ephemeris_vet']=vet(sap,p,t0,dur,holdout=tuple(hold),controls=0,holdout_was_unseen=True)
   out['signals'].append(s)
   if snr<9:break
   keep&=np.abs((t-t0+p/2)%p-p/2)>dur
  out['status']='ok'
 except Exception as ex:out.update(status='error',error=repr(ex),trace=traceback.format_exc())
 out['seconds']=time.time()-start;dump(dest,out)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=64);ap.add_argument('--workers',type=int,default=5);ap.add_argument('--inverted',action='store_true');a=ap.parse_args()
 for folder in ('fits','lightcurves','results','manifests'):(ROOT/folder).mkdir(exist_ok=True)
 if (ROOT/'pilot_observations.csv').exists() and len(pd.read_csv(ROOT/'pilot_targets.csv'))>=a.limit:
  d=pd.read_csv(ROOT/'pilot_targets.csv',dtype={'source_id':str}).merge(pd.read_csv(ROOT/'pilot_observations.csv')[['target_name','dataURL']],left_on='gaia_designation',right_on='target_name').head(a.limit)
 else:d=select(a.limit)
 with ProcessPoolExecutor(a.workers) as ex:
  for f in as_completed([ex.submit(one,row,a.inverted) for row in d.to_dict('records')]):
   r=f.result();print(json.dumps({k:r.get(k) for k in ('source_id','kic','status','error','seconds')}|{'signals':[{'period':s['period'],'snr':s['bls_snr'],'holdout_snr':s['holdout']['snr'],'pass':s['screen_pass']} for s in r['signals']]}),flush=True)
if __name__=='__main__':main()
