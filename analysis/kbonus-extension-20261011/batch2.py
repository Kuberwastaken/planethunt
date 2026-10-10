"""Batch 2 (ranks 65-192 by frozen Gaia G-mag priority; same rule as pilot, nothing about photometry used)."""
import sys,json,argparse
import pandas as pd,requests
import pilot as P
a=argparse.ArgumentParser();a.add_argument('--lo',type=int,default=64);a.add_argument('--hi',type=int,default=192);a.add_argument('--workers',type=int,default=2);a=a.parse_args()
d=pd.read_csv(P.ROOT/'eligible_before_catalogcheck.csv',dtype={'psf_avail':str})
ex=pd.read_csv(P.ROOT/'mstar_primary_exclusion_check.csv')
prim=set(ex[ex.is_kepler_primary==True].gaia_designation)
d=d[~d.gaia_designation.isin(prim)].sort_values(['phot_g_mean_mag','gaia_designation']).reset_index(drop=True)
pilot=pd.read_csv(P.ROOT/'pilot_targets.csv')
assert list(d.gaia_designation[:64])==list(pilot.gaia_designation[:64]) or print('WARN first64 mismatch',sum(d.gaia_designation[:64].values==pilot.gaia_designation[:64].values))
d=d.iloc[a.lo:a.hi].copy();d['source_id']=d.gaia_designation.str.split().str[-1]
d.to_csv(P.ROOT/'batch2_targets.csv',index=False)
req={'service':'Mast.Caom.Filtered','format':'json','pagesize':50000,'page':1,'params':{'columns':'*','filters':[{'paramName':'provenance_name','values':['KBONUS-BKG']},{'paramName':'target_name','values':d.gaia_designation.tolist()}]}}
j=requests.post('https://mast.stsci.edu/api/v0/invoke',data={'request':json.dumps(req)},timeout=90).json()
obs=pd.DataFrame(j['data']).drop_duplicates('target_name');obs.to_csv(P.ROOT/'batch2_observations.csv',index=False)
d=d.merge(obs[['target_name','dataURL']],left_on='gaia_designation',right_on='target_name')
print(len(d),'targets',flush=True)
for f in ('fits','lightcurves','results','manifests'):(P.ROOT/f).mkdir(exist_ok=True)
import time
from concurrent.futures import ProcessPoolExecutor,as_completed
with ProcessPoolExecutor(a.workers) as ex_:
 for fu in as_completed([ex_.submit(P.one,r,False) for r in d.to_dict('records')]):
  r=fu.result();print(json.dumps({k:r.get(k) for k in ('source_id','kic','status','error','seconds')}|{'signals':[{'period':round(s['period'],4),'snr':round(s['bls_snr'],1),'hold':round(s['holdout']['snr'],1),'pass':s['screen_pass']} for s in r['signals']]}),flush=True)
