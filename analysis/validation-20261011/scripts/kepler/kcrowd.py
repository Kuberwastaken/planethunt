import numpy as np, json, sys
sys.path.insert(0,'/root/ph/work'); from kdepth import depth
from astropy.io import fits
fp='/root/ph/rel/kx/planet-search/database_expansion/kbonus/fits/2103792461826460288.fits'
h=fits.open(fp)
fit=json.load(open('/root/ph/work/kfit_psf.json')); P=fit['P'][0]; T0=fit['T0_btjd'][0]; dur=2.2/24
rows=[]
for hd in h:
    if not hd.name.startswith('LIGHTCURVE_Q'): continue
    H=hd.header; q=H['QUARTER']; d=hd.data
    g=(d['SAP_QUALITY']==0)&np.isfinite(d['TIME'])&np.isfinite(d['FLUX'])&np.isfinite(d['SAP_FLUX'])
    t=d['TIME'][g]-2167.
    a=depth(t,d['FLUX'][g]/np.median(d['FLUX'][g]),P,T0,dur); b=depth(t,d['SAP_FLUX'][g]/np.median(d['SAP_FLUX'][g]),P,T0,dur)
    ap=h['APERTURE_Q%d'%q].data
    rows.append(dict(q=q,crowdsap=H.get('CROWDSAP'),flfrcsap=H.get('FLFRCSAP'),psffrac=H.get('PSFFRAC'),npix=int(np.sum(ap>0)) if ap is not None else None,
        med_psf=float(np.median(d['FLUX'][g])),med_sap=float(np.median(d['SAP_FLUX'][g])),psf=a,sap=b,ratio=b[1]/a[1]))
    print('Q%-2d CROWDSAP %.3f FLFRCSAP %.3f PSFFRAC %.3f npix %s  PSF %6.0f+/-%4.0f  SAP %6.0f+/-%4.0f  SAP/PSF %.2f  medSAP/medPSF %.2f'%(q,H.get('CROWDSAP',np.nan),H.get('FLFRCSAP',np.nan),H.get('PSFFRAC',np.nan),rows[-1]['npix'],a[1],a[2],b[1],b[2],rows[-1]['ratio'],rows[-1]['med_sap']/rows[-1]['med_psf']))
print([k for k in h['LIGHTCURVE_Q1'].header.keys()][-40:])
json.dump(rows,open('/root/ph/work/kcrowd.json','w'),indent=1,default=float)
