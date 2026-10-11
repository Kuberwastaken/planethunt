import json,pandas as pd,pilot as P
from concurrent.futures import ProcessPoolExecutor,as_completed
d=pd.read_csv(P.ROOT/'eligible_before_catalogcheck.csv',dtype={'psf_avail':str})
ex=pd.read_csv(P.ROOT/'mstar_primary_exclusion_check.csv');prim=set(ex[ex.is_kepler_primary==True].gaia_designation)
d=d[~d.gaia_designation.isin(prim)].sort_values(['phot_g_mean_mag','gaia_designation']).reset_index(drop=True).iloc[576:1800].copy()
d['source_id']=d.gaia_designation.str.split().str[-1]
import os
d=d[[os.path.exists(P.ROOT/'lightcurves'/f'{s}.npz') for s in d.source_id]];d['dataURL']=''
print(len(d),'inverted targets',flush=True)
with ProcessPoolExecutor(2) as e:
 for f in as_completed([e.submit(P.one,r,True) for r in d.to_dict('records')]):
  r=f.result();print(json.dumps({'source_id':r['source_id'],'kic':r['kic'],'status':r['status'],'signals':[{'p':round(s['period'],4),'snr':round(s['bls_snr'],1),'hold':round(s['holdout']['snr'],1),'pass':s['screen_pass']} for s in r['signals']]}),flush=True)
