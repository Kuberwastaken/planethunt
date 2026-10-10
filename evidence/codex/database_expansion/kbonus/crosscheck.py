"""Conservative catalog comparison; no-match is not proof of novelty."""
import json
from pathlib import Path
import numpy as np,pandas as pd
from astropy.coordinates import SkyCoord,search_around_sky
import astropy.units as u
P=Path(__file__).resolve().parent
t=pd.read_csv(P/'pilot_targets.csv',dtype={'source_id':str})
s=pd.read_csv(P.parent/'kepler_known_signals.csv',dtype={'gaia_dr3_id':str},low_memory=False)
s=s[s.ra.notna()&s.dec.notna()].reset_index(drop=True)
a=SkyCoord(t.ra.to_numpy()*u.deg,t.dec.to_numpy()*u.deg);b=SkyCoord(s.ra.to_numpy()*u.deg,s.dec.to_numpy()*u.deg)
i,j,sep,_=search_around_sky(a,b,30*u.arcsec);out=[]
for x,y,z in zip(i,j,sep.arcsec):
 out.append({'source_id':t.iloc[x].source_id,'target_kic':int(t.iloc[x].kic),'target_aperture_kic':int(t.iloc[x].tpforg),'separation_arcsec':z,**s.iloc[y].to_dict()})
ne=pd.DataFrame(out);ne.to_csv(P/'pilot_known_neighborhood.csv',index=False)
rows=[];matches=[]
for f in (P/'results').glob('*.json'):
 d=json.loads(f.read_text());sid=d['source_id']
 if sid not in set(t.source_id):continue
 for v in d.get('signals',[]):
  own=ne[ne.source_id==sid] if len(ne) else ne
  prior=[]
  for _,r in own.iterrows():
   p=float(r.period_days)
   if not np.isfinite(p) or p<=0:continue
   ratio=v['period']/p
   harm=min((1/3,.5,1.,2.,3.),key=lambda x:abs(ratio/x-1))
   if abs(ratio/harm-1)<.002:
    m={'source_id':sid,'rank':v['rank'],'found_period':v['period'],'period_ratio':ratio,'nearest_harmonic':harm,**r.to_dict()};matches.append(m);prior.append(m)
  iv=v.get('independent_vet',{});hv=iv.get('holdout',{}).get('measurement',{});ap=v.get('sap_fixed_ephemeris_vet',{})
  rows.append({'source_id':sid,'kic':d['kic'],'inverted':d['inverted'],'rank':v['rank'],'period_d':v['period'],'duration_hr':v['duration_hr'],'depth_ppm':v['depth_ppm'],'bls_snr':v['bls_snr'],'holdout_snr':v['holdout']['snr'],'screen_pass':v['screen_pass'],'raw_local_snr':iv.get('primary',{}).get('local_snr'),'raw_holdout_snr':hv.get('local_snr'),'flags':';'.join(iv.get('flags',[])),'sap_local_snr':ap.get('primary',{}).get('local_snr'),'nearby_prior_period_matches':len(prior),'disposition':'needs_source_localization_and_literature_vet' if v['screen_pass'] else 'failed_initial_screen'})
pd.DataFrame(rows).to_csv(P/'pilot_summary.csv',index=False);pd.DataFrame(matches).to_csv(P/'pilot_prior_period_matches.csv',index=False)
print(json.dumps({'target_neighborhoods_with_prior_reports':len(set(i)),'nearby_report_rows':len(out),'search_signal_records':len(rows),'screen_passes':sum(r['screen_pass'] for r in rows),'nearby_period_matches':len(matches)}))
