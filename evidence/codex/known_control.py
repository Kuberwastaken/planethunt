"""Positive control: rediscover published LHS 3844 b; never a new candidate."""
import json
import pandas as pd
from acquire import ROOT,query,download
from run_search import one
if __name__=='__main__':
 tic=410153553
 raw=query([tic]);m=pd.DataFrame(raw['data']);m=m[m.dataURL.fillna('').str.endswith(('lc.fits','llc.fits')) & m.sequence_number.between(1,200)].copy()
 m['rank']=m.provenance_name.map({'SPOC':0,'TESS-SPOC':1,'QLP':2});m=m[~((m.provenance_name=='SPOC')&(m.t_exptime<100))]
 m=m.sort_values(['sequence_number','rank','t_exptime']).drop_duplicates('sequence_number')
 # Fixed small calibration sample: two earliest, two middle, two latest sectors.
 ix=sorted(set([0,1,len(m)//2,len(m)//2+1,len(m)-2,len(m)-1]));m=m.iloc[ix]
 print('Control acquisition',download((tic,m.to_dict('records'))),flush=True)
 stars=pd.read_csv(ROOT.parent/'upstream-tess/data/catalogs/tic_nearby.csv');r=stars[stars.TIC==tic].iloc[0].to_dict()
 r['TIC']=tic
 out=one((r,'usp',False));out['positive_control']='Known LHS 3844 b; NASA P=0.46293 days; not novel'
 (ROOT/'positive_control.json').write_text(json.dumps(out,indent=2));print('Control',[(x['period'],x['bls_snr'],x['holdout']['snr']) for x in out.get('signals',[])],flush=True)
