"""Reconstruct catalogue selection and audit preserved searches; no new transit search.
Run with --repo, --downloads, --reruns and --out. Dependencies: numpy, pandas, astropy.
Catalogue downloads must match the hashes preserved before submission.
"""
import argparse, csv, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from astropy.io import fits
p=argparse.ArgumentParser()
for key in ('repo','downloads','reruns','out'): p.add_argument('--'+key,type=Path,required=True)
a=p.parse_args(); root=a.repo; kb=root/'evidence/codex/database_expansion/kbonus'
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={}
for name,prov in [('mstars.fits','catalog_provenance.json'),('source-catalog.fits','source_catalog_provenance.json')]:
    saved=json.loads((kb/prov).read_text()); got=hashfile(a.downloads/name)
    assert got==saved['sha256'], (name,'catalogue changed')
    inputs[name]={'url':saved['url'],'sha256':got}
with fits.open(a.downloads/'mstars.fits') as h: ids=set(h[1].data['gaia_designation'])
with fits.open(a.downloads/'source-catalog.fits') as h:
    d=h[1].data; mask=np.isin(d['gaia_designation'],list(ids))
    counts={'published_mstar_entries':len(ids),'matched_source_catalogue':int(mask.sum())}
    cuts=[('psffrac_gt_0_5',d['psffrac']>.5),('crowdsap_gt_0_7',d['crowdsap']>.7),
          ('at_least_8_psf_quarters',np.array([str(x).count('1') for x in d['psf_avail']])>=8),
          ('kic_differs_from_tpf_origin',d['kic']!=d['tpforg'])]
    for name,c in cuts: mask &= c; counts[name]=int(mask.sum())
    e=pd.read_csv(kb/'eligible_before_catalogcheck.csv',dtype={'gaia_designation':str})
    assert set(d['gaia_designation'][mask])==set(e.gaia_designation)
    ex=pd.read_csv(kb/'mstar_primary_exclusion_check.csv')
    primary=set(ex[ex.is_kepler_primary.astype(str).str.lower().eq('true')].gaia_designation)
    selected=e[~e.gaia_designation.isin(primary)].sort_values(['phot_g_mean_mag','gaia_designation'])
    pilot=pd.read_csv(kb/'pilot_targets.csv')
    assert list(selected.gaia_designation[:64])==list(pilot.gaia_designation)
    counts['after_saved_primary_exclusions']=len(selected)
    counts['first_64_order_reproduced']=True
    counts['primary_exclusion_source']='preserved mstar_primary_exclusion_check.csv; not a fresh archive primary-target query'
search=[]; combined=[]
for label,folder,filename,flag in [('pilot',kb,'pilot_summary.csv','screen_pass'),
 ('ranks65-576',root/'analysis/kbonus-extension-20261011','signals_real_and_inverted.csv','first_screen_pass'),
 ('ranks577-1800',root/'analysis/kbonus-extension-20261011/ranks577-1800','signals_real_and_inverted.csv','first_screen_pass')]:
    rows=list(csv.DictReader((folder/filename).open()))
    for inv in ('False','True'):
        s=[x for x in rows if x['inverted']==inv]; ok=[x for x in s if x[flag]=='True']
        search.append({'stage':label,'inverted':inv=='True','sources_with_signal_records':len(set(x['source_id'] for x in s)),
          'first_screen_signals':len(ok),'first_screen_sources':len(set(x['source_id'] for x in ok))})
    for x in rows:
        if x['inverted']=='True' and x[flag]=='True' and float(x['period_d'])>1.5 and float(x['bls_snr'])>=26.7 and float(x['holdout_snr'])>=15.5:
            combined.append({k:x[k] for k in ['source_id','kic','period_d','bls_snr','holdout_snr']})
checks={}
for n in ('summary.json','events.csv','sectors.json'):
    original=root/'analysis/archive-followup-20261012/tess/results'/n
    rerun=a.reruns/'tess-rerun'/n
    assert original.read_bytes()==rerun.read_bytes(),n
    checks['tess_'+n]={'identical_bytes':True,'sha256':hashfile(rerun)}
p1=root/'analysis/archive-exhaustion-20261012/tglc_results/summary.json'
p2=a.reruns/'tglc-rerun/tglc_results/summary.json'
assert json.loads(p1.read_text())==json.loads(p2.read_text())
checks['tglc_summary']={'identical_json_values':True,'rerun_sha256':hashfile(p2)}
tess=json.loads((a.reruns/'tess-rerun/summary.json').read_text())
tglc=json.loads(p2.read_text())['2103792461826460288_cal_psf_flux']
barber=a.downloads/'table5.dat'; lines=barber.read_text().splitlines()
row=[(i+1,x) for i,x in enumerate(lines) if x.startswith('2103792461826460288 ')]
assert len(row)==1
result={'catalogue_inputs':inputs,'selection':counts,'search_counts':search,'inverted_stronger_screen':combined,
 'rerun_checks':checks,'tess_nominal':{k:{n:v[n] for n in ('depth_ppm','error_ppm','n_events','control_depth_std_ppm')} for k,v in tess.items()},
 'tglc_cal_psf':{n:tglc[n] for n in ('depth_ppm','error_ppm','n_events','control_depth_std_ppm')},
 'barber':{'url':'https://cdsarc.cds.unistra.fr/ftp/J/AJ/164/88/table5.dat','sha256':hashfile(barber),'line':row[0][0],'row':row[0][1], 'identifier_release':'EDR3 (per catalogue ReadMe)'},
 'limits':['Reproduces preserved estimators; not an independent reduction or validation.', 'No calibrated false-alarm probability or blind-search completeness.', 'No joint period/epoch covariance propagation or time-dependent TESS scene model.']}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'selection':counts,'search_counts':search,'stronger_inverted':combined,'checks':checks},indent=2))
