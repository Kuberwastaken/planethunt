"""Independent checks of root original-pixel localization products."""
import json,sys
from pathlib import Path
import numpy as np
from astropy.io import fits
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'kbonus'))
from pixel_localize import LocalPRF,P
r=json.loads((P/'pixels/localization.json').read_text());rows=[]
for qrow in r['quarters']:
 q=qrow['quarter'];f=next(f for f in (P/'pixels').glob('*_lpd-targ.fits.gz') if fits.getheader(f)['QUARTER']==q)
 with fits.open(f) as h:
  shape=h[1].data['FLUX'].shape[1:];col=h[2].header['CRVAL1P'];row=h[2].header['CRVAL2P'];channel=h[0].header['CHANNEL']
 d=np.load(P/'pixels'/f'difference_q{q}.npz');y=d['difference'].ravel();e=d['error'].ravel();valid=np.isfinite(y)&np.isfinite(e)&(e>0)
 prf=LocalPRF(channel=channel,shape=shape,column=col,row=row)
 def template(pos):return prf.evaluate(col+pos[0]+.5,row+pos[1]+.5).ravel()
 xx,yy=np.meshgrid(np.arange(shape[1]),np.arange(shape[0]));checks={}
 for shifted in (False,True):
  off=np.array(qrow['mean_astrometric_offset']) if shifted else np.zeros(2)
  for plane in (False,True):
   nuisance=[np.ones(len(y))]+([xx.ravel(),yy.ravel()] if plane else [])
   out=[]
   for xy in (qrow['target_xy'],qrow['primary_xy']):
    X=np.column_stack([template(np.array(xy)+off)]+nuisance);A=X[valid]/e[valid,None];beta=np.linalg.lstsq(A,y[valid]/e[valid],rcond=None)[0];res=A@beta-y[valid]/e[valid]
    out.append({'amplitude':float(beta[0]),'chi2':float(res@res)})
   checks[f'{"mean_shift" if shifted else "no_shift"}_{"plane" if plane else "constant"}']={'target':out[0],'primary':out[1],'delta_chi2_primary_minus_target':out[1]['chi2']-out[0]['chi2']}
 rows.append({'quarter':q,'checks':checks})
summ={name:{'sum_delta_chi2':float(sum(v['checks'][name]['delta_chi2_primary_minus_target'] for v in rows)),'n_target_preferred':sum(v['checks'][name]['delta_chi2_primary_minus_target']>0 for v in rows),'minimum_target_amplitude':float(min(v['checks'][name]['target']['amplitude'] for v in rows))} for name in rows[0]['checks']}
out={'source_id':r['source_id'],'scope':'Independent re-fit of root saved per-quarter difference images, tests no empirical WCS shift and spatial-plane nuisance. This shares root event differences, so not a fully independent pixel extraction.','pixel_coordinate_audit':'FITSCRPIX1P/2P=1,CRVAL1P/2P detector origin. WCS all_world2pix(origin0) returns zero-based center coordinates. LightkurvePRF uses detector sample coordinates column+0.5,row+0.5, therefore root conversion plus0.5 correct.','calibration_caution':'PRF interpolation inverse-distance positions and detector channel supplied correctly. Unmodeled faint neighbors, PRF mismatch, interpixel covariance remain. No planetFPP interpretation.','summary':summ,'quarters':rows}
(ROOT/'kbonus_independent_audit/pixel_localization_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(summ,indent=2))
