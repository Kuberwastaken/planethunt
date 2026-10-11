import glob, json, numpy as np, pandas as pd
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u
R=json.load(open('/root/ph/work/kcentroid_tpf.json'))['per_quarter']; byq={r['q']:r for r in R}
g=pd.read_csv('/root/ph/planethunt/evidence/codex/catalogs/tickbonus2103792461826460288_gaia_cone.csv')
tc=SkyCoord(285.90782692874626*u.deg,40.94198844296448*u.deg)
gc=SkyCoord(g.ra.values*u.deg,g.dec.values*u.deg); g['sep']=gc.separation(tc).arcsec
g=g[g.sep<30].sort_values('sep').reset_index(drop=True); gc=SkyCoord(g.ra.values*u.deg,g.dec.values*u.deg)
fit=json.load(open('/root/ph/work/kfit_psf.json')); P=fit['P'][0]; T0=fit['T0_btjd'][0]; dur=2.2/24
chi=np.zeros(len(g)); dof=0
for f in sorted(glob.glob('/root/ph/rel/kx/planet-search/database_expansion/kbonus/pixels/kplr005689116-*_lpd-targ.fits.gz')):
    h=fits.open(f); q=h[0].header['QUARTER']
    if q not in byq: continue
    r=byq[q]; w=WCS(h[2].header); d=h[1].data
    good=(d['QUALITY']==0)&np.isfinite(d['TIME']); F=d['FLUX'][good].astype(float)
    pixok=np.all(np.isfinite(F),axis=0)&(np.nanmedian(F,axis=0)>0); ny,nx=F.shape[1:]; Y,X=np.mgrid[0:ny,0:nx]
    Fm=np.median(F[:,pixok],axis=0); c=np.array([(Fm*X[pixok]).sum()/Fm.sum(),(Fm*Y[pixok]).sum()/Fm.sum()])
    xy=np.array(w.world_to_pixel(gc),float).T
    dap=r['depth_ap_ppm']*1e-6; meas=np.array(r['meas_mpix'])*1e-3; err=np.array(r['err_mpix'])*1e-3
    pred=-dap*(xy-c)
    chi+=np.sum(((meas-pred)/err)**2,axis=1); dof+=2
g['centroid_chi2']=chi; g['dchi2_vs_target']=chi-chi[0]
print(g[['source_id','sep','phot_g_mean_mag','centroid_chi2','dchi2_vs_target']].to_string())
g[['source_id','sep','phot_g_mean_mag','centroid_chi2','dchi2_vs_target']].assign(source_id=lambda d:d.source_id.astype(str)).to_csv('/root/ph/work/kcentroid_all_sources.csv',index=False)
