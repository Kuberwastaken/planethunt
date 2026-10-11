"""In-transit SAP centroid shift test for KIC 5689121 using KBonus CENTROID_COLUMN/ROW
(flux-weighted centroids of the SAP aperture). If the dip is on the target, the
aperture centroid moves AWAY from the contaminating flux, i.e. toward the target position;
if the dip were on the bright neighbour KIC 5689116 it would move toward the neighbour."""
import numpy as np, json, glob
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u
fp='/root/ph/rel/kx/planet-search/database_expansion/kbonus/fits/2103792461826460288.fits'
fit=json.load(open('/root/ph/work/kfit_psf.json')); P=fit['P'][0]; T0=fit['T0_btjd'][0]; dur=2.2/24
tgt=SkyCoord(285.90782692874626*u.deg,40.94198844296448*u.deg)
g=__import__('pandas').read_csv('/root/ph/planethunt/evidence/codex/database_expansion/kbonus/2103792461826460288_gaia_contaminants.csv')
nb=SkyCoord(g.ra.values[0]*u.deg,g.dec.values[0]*u.deg)
tpfs={}
for f in glob.glob('/root/ph/rel/kx/planet-search/database_expansion/kbonus/pixels/kplr005689116-*_lpd-targ.fits.gz'):
    h=fits.open(f); tpfs[h[0].header['QUARTER']]=WCS(h[2].header)
h=fits.open(fp); rows=[]
for hd in h:
    if not hd.name.startswith('LIGHTCURVE_Q'): continue
    q=hd.header['QUARTER']; d=hd.data
    gd=(d['SAP_QUALITY']==0)&np.isfinite(d['CENTROID_COLUMN'])&np.isfinite(d['CENTROID_ROW'])&np.isfinite(d['SAP_FLUX'])
    t=d['TIME'][gd]-2167; cx=d['CENTROID_COLUMN'][gd]; cy=d['CENTROID_ROW'][gd]
    n=np.round((t-T0)/P); dt=t-(T0+n*P); dcol=[];drow=[]
    for k in np.unique(n[np.abs(dt)<0.4]):
        s=(n==k)&(np.abs(dt)<0.4); i=s&(np.abs(dt)<dur*0.4); o=s&(np.abs(dt)>dur/2+0.03)
        if i.sum()<2 or o.sum()<8: continue
        for arr,lst in ((cx,dcol),(cy,drow)):
            c=np.polyfit(dt[o],arr[o],1); lst.append(np.mean(arr[i]-np.polyval(c,dt[i])))
    dcol,drow=np.array(dcol),np.array(drow)
    if q not in tpfs or len(dcol)<2: continue
    w=tpfs[q]
    # TPF WCS is 0-based within the stamp; convert to CCD coords using the TPF header offsets
    th=fits.open(glob.glob('/root/ph/rel/kx/planet-search/database_expansion/kbonus/pixels/kplr005689116-*_lpd-targ.fits.gz')[0])
    rows.append(dict(q=q,n=len(dcol),dcol=dcol.mean(),dcol_e=dcol.std(ddof=1)/np.sqrt(len(dcol)),drow=drow.mean(),drow_e=drow.std(ddof=1)/np.sqrt(len(drow)),
        cen_col=float(np.median(cx)),cen_row=float(np.median(cy)),
        tgt_pix=[float(v) for v in w.world_to_pixel(tgt)],nb_pix=[float(v) for v in w.world_to_pixel(nb)]))
json.dump(rows,open('/root/ph/work/kcentroid_raw.json','w'),indent=1)
for r in rows: print(r)
