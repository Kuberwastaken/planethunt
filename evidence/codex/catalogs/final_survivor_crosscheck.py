"""Final limited catalog screen of non-control search_summary survivors."""
from pathlib import Path
from fractions import Fraction
from datetime import datetime,timezone
import pandas as pd
import numpy as np
import hashlib,json,re
R=Path(__file__).resolve().parent
summary=R.parent/'search_summary.csv'
knownfile=R/'known_signals.csv'
signals=pd.read_csv(summary)
signals=signals[signals.screen_pass & ~signals.inverted & ~signals.positive_control]
known=pd.read_csv(knownfile,low_memory=False)
try: neighbors=pd.read_csv(R/'selected_neighbor_prior_matches.csv')
except pd.errors.EmptyDataError: neighbors=pd.DataFrame()
aliases=sorted(set(Fraction(m,n) for m in range(1,5) for n in range(1,5)))
rows=[];allmatches=[]
for s in signals.itertuples():
    exact=known[known.TIC==s.tic].copy();near=neighbors[neighbors.TIC==s.tic].copy() if len(neighbors) else pd.DataFrame()
    detailed=R/f'tic{s.tic}_neighbor_known_signals.csv'
    if detailed.exists():
        try: near=pd.concat([near,pd.read_csv(detailed)],ignore_index=True)
        except pd.errors.EmptyDataError:pass
    hits=[]
    for candidate in exact.itertuples():
        if not np.isfinite(candidate.period) or candidate.period<=0:continue
        alias=min(aliases,key=lambda a:abs(s.period_d/candidate.period-float(a)))
        rel=abs(s.period_d/(candidate.period*float(alias))-1)
        if rel<.01:
            offset=((s.epoch_btjd+2457000-candidate.epoch_BJD+candidate.period/2)%candidate.period)-candidate.period/2
            hit=dict(tic=s.tic,rank=s.rank,our_period=s.period_d,known_period=candidate.period,
                     alias=str(alias),relative_period_difference=rel,catalog=candidate.catalog,
                     epoch_offset_at_reference_hours=offset*24,source_file=candidate.source_file)
            hits.append(hit);allmatches.append(hit)
    identfile=R/f'tic{s.tic}_simbad.txt'
    identity='unresolved in SIMBAD exact TIC query'
    if identfile.exists():
        m=re.search(r'^Object (.*?)\s+---',identfile.read_text(),re.M)
        if m:identity=m.group(1)
    novelty='no matching period found in checked catalogs; novelty unestablished'
    if hits:novelty='prior SPOC near-period detection and harmonic; novelty not established'
    if s.tic==94753488:disposition='unresolved; broad signal, crowded aperture, inconclusive pixels'
    elif s.tic==456716455:disposition='unresolved; broad signal and close physical companion'
    elif hits:disposition='prior-detection warning; independent validation required'
    elif 'weak_fixed_ephemeris_holdout' in str(s.vet_flags):disposition='fails current independent holdout; not a planet candidate'
    else:disposition='unresolved; not independently validated'
    rows.append(dict(tic=s.tic,rank=s.rank,period_days=s.period_d,simbad_identity=identity,
                     same_host_catalog_rows=len(exact),prior_period_alias_matches=len(hits),
                     known_neighbor_records=len(near),prior_periods_days=';'.join(str(x['known_period']) for x in hits),
                     catalog_disposition=novelty,scientific_disposition=disposition,
                     source=';'.join(sorted(set(x['source_file'] for x in hits))) or 'known_signals.csv;selected_neighbor_prior_matches.csv',
                     limitation='catalog absence is not proof of novelty; full TCE-neighbor coordinate coverage incomplete'))
pd.DataFrame(rows).to_csv(R/'final_survivor_dispositions.csv',index=False)
pd.DataFrame(allmatches).to_csv(R/'final_survivor_prior_period_matches.csv',index=False)
provenance={'checked_utc':datetime.now(timezone.utc).isoformat(),'input_sha256':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in [summary,knownfile,R/'selected_neighbor_prior_matches.csv']},'signals':len(signals),'hosts':int(signals.tic.nunique()),'aliases':[str(x) for x in aliases],'relative_period_tolerance':.01,'positive_control_excluded':True,'epoch_note':'Reference epoch offsets only. Period precision/drift across baseline prevents definitive equality from approximate TCE values.'}
(R/'final_survivor_dispositions.provenance.json').write_text(json.dumps(provenance,indent=2))
print(pd.DataFrame(rows)[['tic','rank','prior_period_alias_matches','scientific_disposition']].to_string(index=False))
