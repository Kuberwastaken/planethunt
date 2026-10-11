"""Independent flux-weighted centroid test from the raw KIC 5689116 target pixel files
(which contain both KIC 5689116 and the candidate KIC 5689121 ~7" away).
Aperture: all stamp pixels with finite flux in every good cadence. Predictions:
 signal on star j  ->  in-transit centroid shift = -delta_ap * (x_j - c)   (first order)
where delta_ap is the in-transit fractional dip of the summed aperture flux."""
import glob, json, numpy as np, pandas as pd
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u
fit=json.load(open('/root/ph/work/kfit_psf.json')); P=fit['P'][0]; T0=fit['T0_btjd'][0]; dur=2.2/24
tgt=SkyCoord(285.90782692874626*u.deg,40.94198844296448*u.deg)
g=pd.read_csv('/root/ph/planethunt/evidence/codex/database_expansion/kbonus/2103792461826460288_gaia_contaminants.csv')
nb=SkyCoord(g.ra.values[0]*u.deg,g.dec.values[0]*u.deg)
res=[]; chi={'zero':0.,'target':0.,'neighbour':0.}; dof=0
for f in sorted(glob.glob('/root/ph/rel/kx/planet-search/database_expansion/kbonus/pixels/kplr005689116-*_lpd-targ.fits.gz')):
    h=fits.open(f); q=h[0].header['QUARTER']; d=h[1].data; w=WCS(h[2].header)
    t=d['TIME']-2167.; F=d['FLUX'].astype(float); qual=d['QUALITY']
    good=(qual==0)&np.isfinite(t)
    pixok=np.all(np.isfinite(F[good]),axis=0)&(np.nanmedian(F[good],axis=0)>0)
    F=F[good][:,pixok]; t=t[good]
    ny,nx=d['FLUX'].shape[1:]; Y,X=np.mgrid[0:ny,0:nx]; X=X[pixok]; Y=Y[pixok]
    S=F.sum(1); cx=(F*X).sum(1)/S; cy=(F*Y).sum(1)/S; fl=S/np.median(S)
    n=np.round((t-T0)/P); dt=t-(T0+n*P); D=[];DX=[];DY=[]
    for k in np.unique(n[np.abs(dt)<0.4]):
        s=(n==k)&(np.abs(dt)<0.4); i=s&(np.abs(dt)<dur*0.4); o=s&(np.abs(dt)>dur/2+0.03)
        if i.sum()<2 or o.sum()<8: continue
        for arr,lst,sign in ((fl,D,-1),(cx,DX,1),(cy,DY,1)):
            c=np.polyfit(dt[o],arr[o],1); v=np.mean(arr[i]-np.polyval(c,dt[i])); lst.append(v if sign>0 else -v/np.polyval(c,0))
    D,DX,DY=map(np.array,(D,DX,DY))
    if len(D)<3: continue
    c=np.array([np.median(cx),np.median(cy)]); xt=np.array(w.world_to_pixel(tgt),float); xn=np.array(w.world_to_pixel(nb),float)
    dap=D.mean(); meas=np.array([DX.mean(),DY.mean()]); err=np.array([DX.std(ddof=1),DY.std(ddof=1)])/np.sqrt(len(DX))
    pred={'zero':np.zeros(2),'target':-dap*(xt-c),'neighbour':-dap*(xn-c)}
    for kk in chi: chi[kk]+=float(np.sum(((meas-pred[kk])/err)**2))
    dof+=2
    r=dict(q=int(q),n=int(len(D)),npix=int(pixok.sum()),depth_ap_ppm=float(dap*1e6),depth_ap_err=float(D.std(ddof=1)/np.sqrt(len(D))*1e6),
           meas_mpix=(meas*1e3).tolist(),err_mpix=(err*1e3).tolist(),pred_target=(pred['target']*1e3).tolist(),pred_neighbour=(pred['neighbour']*1e3).tolist())
    res.append(r)
    print('Q%-2d npix %2d  ap depth %5.0f±%4.0f ppm  shift [%6.2f %6.2f]±[%5.2f %5.2f]  pred tgt [%6.2f %6.2f]  pred nb [%6.2f %6.2f] mpix'%(q,r['npix'],r['depth_ap_ppm'],r['depth_ap_err'],*r['meas_mpix'],*r['err_mpix'],*r['pred_target'],*r['pred_neighbour']))
from scipy.stats import chi2 as C
for k,v in chi.items(): print('%-9s chi2 %.1f / %d  p=%.3g'%(k,v,dof,C.sf(v,dof)))
json.dump(dict(per_quarter=res,chi2=chi,dof=dof),open('/root/ph/work/kcentroid_tpf.json','w'),indent=1)
