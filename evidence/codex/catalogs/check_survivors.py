"""Snapshot corrected pipeline survivors and broad known-signal period screening.

This screening uses generous 1% period agreement for aliases m/n with m,n<=4.
Potential matches require subsequent epoch/uncertainty assessment; no matches is
not a novelty certification. LHS 3844 is an explicit positive control.
"""
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction
import hashlib,json
import pandas as pd
import numpy as np
R=Path(__file__).resolve().parent
known_path=R/'known_signals.csv'
known=pd.read_csv(known_path,low_memory=False)
targets=pd.read_csv(R.parent/'targets.csv').set_index('TIC')
signals=[dict(tic=259999047,period=0.496673,source='parent preliminary request, may be obsolete',pipeline_version=None)]
for file in sorted((R.parent/'results').glob('*.json')):
    try: data=json.loads(file.read_text())
    except (ValueError,OSError):continue
    if data.get('pipeline_version')!=3 or data.get('inverted') or data.get('tic') in [410153553,95431305]:continue
    for signal in data.get('signals',[]):
        if signal.get('screen_pass'):
            signals.append(dict(tic=data['tic'],period=signal['period'],t0_BTJD=signal['t0'],
                                duration_hr=signal['duration_hr'],rank=signal['rank'],
                                source=str(file),pipeline_version=3,
                                source_sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
aliases=sorted(set(Fraction(m,n) for m in range(1,5) for n in range(1,5)))
report=[]
for s in signals:
    tic=s['tic']; pool=known[known.TIC==tic].copy(); pool['separation_arcsec']=0
    if tic in targets.index:
        t=targets.loc[tic]; pos=known.dropna(subset=['ra','dec'])
        r1,d1,r2,d2=map(np.deg2rad,[t.ra,t.dec,pos.ra.to_numpy(),pos.dec.to_numpy()])
        h=np.sin((d2-d1)/2)**2+np.cos(d1)*np.cos(d2)*np.sin((r2-r1)/2)**2
        sep=2*np.arcsin(np.sqrt(np.clip(h,0,1)))*180/np.pi*3600
        nearby=pos[(sep<120)&(pos.TIC!=tic)].copy()
        nearby['separation_arcsec']=sep[(sep<120)&(pos.TIC.to_numpy()!=tic)]
        pool=pd.concat([pool,nearby],ignore_index=True)
    matches=[]
    for row in pool.itertuples():
        if not np.isfinite(row.period) or row.period<=0:continue
        alias=min(aliases,key=lambda f:abs(s['period']/row.period-float(f)))
        delta=abs(s['period']-row.period*float(alias))/(row.period*float(alias))
        if delta<.01:
            matches.append(dict(known_TIC=row.TIC,known_period=row.period,catalog=row.catalog,
                                source_file=row.source_file,alias=str(alias),relative_period_difference=delta,
                                epoch_BJD=row.epoch_BJD,separation_arcsec=row.separation_arcsec))
    report.append({**s,'known_exact_host_records':int((pool.TIC==tic).sum()),
                   'known_coordinate_neighbor_records':int((pool.TIC!=tic).sum()),
                   'broad_period_alias_matches':matches,
                   'novelty_status':'not established; only initial catalog screening'})
out={'checked_utc':datetime.now(timezone.utc).isoformat(),
     'known_signals_sha256':hashlib.sha256(known_path.read_bytes()).hexdigest(),
     'screening_aliases':[str(x) for x in aliases], 'relative_period_tolerance':.01,
     'missing_checks':['TCE neighbor coordinates','Gaia epoch propagation','all recent preprints','targeted ExoMiner/T16'],
     'signals':report}
(R/'survivor_catalog_checks.json').write_text(json.dumps(out,indent=2,default=str))
for item in report:print(item['tic'],item['period'],'records',item['known_exact_host_records'],'alias matches',len(item['broad_period_alias_matches']))
