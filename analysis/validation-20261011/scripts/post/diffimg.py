"""Transit difference images of KIC 5689121 from the KIC 5689116 Kepler target pixel files.
diff = mean(out-of-transit frames) - mean(in-transit frames), per event, averaged over events
(positive = light that goes missing during transit). Quarters of the same season share the
same stamp geometry and are stacked."""
import glob, json, numpy as np, pandas as pd
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.units as u
fit=json.load(open('/root/ph/work/kfit_psf.json')); P=fit['P'][0]; T0=fit['T0_btjd'][0]; dur=2.2/24
g=pd.read_csv('/root/ph/planethunt/evidence/codex/catalogs/tickbonus2103792461826460288_gaia_cone.csv')
tc=SkyCoord(285.90782692874626*u.deg,40.94198844296448*u.deg)
gc=SkyCoord(g.ra.values*u.deg,g.dec.values*u.deg); g['sep']=gc.separation(tc).arcsec
out={}
for f in sorted(glob.glob('/root/ph/rel/kx/planet-search/database_expansion/kbonus/pixels/kplr005689116-*_lpd-targ.fits.gz')):
    h=fits.open(f); q=h[0].header['QUARTER']; season=h[0].header['SEASON']; d=h[1].data
    t=d['TIME']-2167.; F=d['FLUX'].astype(float)
    pixok=np.mean(np.isfinite(F),axis=0)>0.9
    F[:,~pixok]=0.0
    good=(d['QUALITY']==0)&np.isfinite(t)&np.all(np.isfinite(F[:,pixok]),axis=1)
    t,F=t[good],F[good]
    n=np.round((t-T0)/P); dt=t-(T0+n*P); D=[]
    for k in np.unique(n[np.abs(dt)<0.4]):
        s=n==k; i=s&(np.abs(dt)<dur*0.4); o=s&(np.abs(dt)>dur/2+0.03)&(np.abs(dt)<0.4)
        if i.sum()<2 or o.sum()<8: continue
        # linear baseline per pixel from out-of-transit frames
        A=np.vstack([np.ones(o.sum()),dt[o]]).T; c,*_=np.linalg.lstsq(A,F[o].reshape(o.sum(),-1),rcond=None)
        base=(np.vstack([np.ones(i.sum()),dt[i]]).T@c).reshape(i.sum(),*F.shape[1:])
        dd=(base-F[i]).mean(0); dd[~pixok]=np.nan; D.append(dd)
    D=np.array(D)
    key=season
    e=out.setdefault(key,dict(quarters=[],diffs=[],med=[],wcs=h[2].header,crval=(h[2].header['CRVAL1P'],h[2].header['CRVAL2P'])))
    e['quarters'].append(int(q)); e['diffs'].append(D); mi=np.median(F,0); mi[~pixok]=np.nan; e['med'].append(mi)
res={}
for s,e in out.items():
    D=np.concatenate(e['diffs']); nn=np.sum(np.isfinite(D),0); m=np.nanmean(D,0); se=np.nanstd(D,0,ddof=1)/np.sqrt(np.maximum(nn,1)); m[nn<2]=np.nan; med=np.nanmean(e['med'],0)
    m=np.where(np.isfinite(m),m,np.nan)
    w=WCS(e['wcs']); xy=np.array(w.world_to_pixel(gc),float).T
    nan2none=lambda a:[[None if not np.isfinite(v) else float(v) for v in r] for r in a]
    res[int(s)]=dict(quarters=e['quarters'],n_events=int(len(D)),diff=nan2none(m),diff_err=nan2none(se),median_image=nan2none(med),
        target_xy=xy[g.sep.values.argmin()].tolist(),gaia_xy=xy.tolist())
    z=np.where(np.isfinite(m/se),m/se,-1e9); pk=np.unravel_index(np.argmax(z),m.shape)
    print('season',s,'Q',e['quarters'],'events',len(D),'shape',m.shape,'peak SNR pixel (row,col)',pk,'SNR %.1f'%(m/se)[pk],'target at (x,y)=(%.2f,%.2f)'%tuple(res[int(s)]['target_xy']))
json.dump(dict(seasons=res,gaia=g.assign(source_id=g.source_id.astype(str))[['source_id','ra','dec','phot_g_mean_mag','sep']].to_dict('records')),open('/root/ph/post/diffimg.json','w'))
