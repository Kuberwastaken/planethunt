"""Exploratory per-event pixel difference image; not a calibrated centroid/FPP test."""
import json,hashlib
from pathlib import Path
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
 tic=94753488;rec=json.load(open(ROOT/'results'/f'{tic}_usp.json'));sig=rec['signals'][0]
 p,t0,dur=sig['period'],sig['t0'],sig['duration_hr']/24
 src=next((ROOT/'pixels').glob('*.fits'))
 with fits.open(src) as h:
  d=h[1].data;t=np.array(d['TIME'],float);flux=np.array(d['FLUX'],float);q=np.array(d['QUALITY']);wcs=WCS(h[2].header)
  good=np.isfinite(t)&((q&(17087|8192))==0)&np.all(np.isfinite(flux),axis=(1,2));t=t[good];flux=flux[good]
  targetxy=wcs.world_to_pixel_values(250.328903503527,-35.0087692592645)
 order=np.argsort(t);t=t[order];flux=flux[order];med=np.median(flux,axis=0)
 depths=[];errs=[]
 for n in np.unique(np.rint((t-t0)/p).astype(int)):
  x=t-(t0+n*p);m=np.abs(x)<.4*p
  if m.sum()<12:continue
  xx=x[m];yy=flux[m].reshape(m.sum(),-1)
  intr=np.abs(xx)<dur/2
  if intr.sum()<3 or (xx < -dur).sum()<3 or (xx>dur).sum()<3:continue
  X=np.column_stack([np.ones(len(xx)),xx,-intr.astype(float)])
  cov=np.linalg.inv(X.T@X);beta=cov@X.T@yy;res=yy-X@beta
  se=np.sqrt(np.sum(res**2,axis=0)/(len(xx)-3)*cov[-1,-1]);depths.append(beta[-1]);errs.append(se)
 dep=np.array(depths);err=np.array(errs);wt=1/np.maximum(err,1e-6)**2;a=wt/wt.sum(axis=0)
 mean=(a*dep).sum(axis=0);formal=1/np.sqrt(wt.sum(axis=0));cluster=np.sqrt(np.sum((a*(dep-mean))**2,axis=0)*len(dep)/(len(dep)-1));se=np.maximum(formal,cluster)
 diff=mean.reshape(11,11);snr=(mean/se).reshape(11,11);yy,xx=np.indices(diff.shape)
 aperture=(xx-targetxy[0])**2+(yy-targetxy[1])**2<2**2
 apos=np.maximum(diff,0)*aperture
 centroid=[float((xx*apos).sum()/apos.sum()),float((yy*apos).sum()/apos.sum())] if apos.sum()>0 else None
 result={'tic':tic,'sector':39,'fits_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'events':len(dep),'target_xy':list(map(float,targetxy)),'positive_difference_centroid_within_2px':centroid,'max_pixel_snr':float(snr.max()),'caveat':'Exploratory difference imaging. Clipped positive centroid is biased, conditional, aperture-limited and has no calibrated uncertainty. Cannot rule out nearby or unresolved blends.','period':p,'duration_hours':dur*24}
 (ROOT/'pixels/94753488_difference.json').write_text(json.dumps(result,indent=2))
 np.savez_compressed(ROOT/'pixels/94753488_difference.npz',mean_image=med,difference=diff,error=se.reshape(11,11),snr=snr)
 fig,axs=plt.subplots(1,3,figsize=(12,4))
 for ax,im,title in zip(axs,[np.log10(np.maximum(med,1)),diff,snr],['Mean image (log flux)','Fitted dimming per pixel','Conditional pixel signal / noise']):
  v=ax.imshow(im,origin='lower',cmap='viridis');ax.plot(*targetxy,'rx',ms=10);ax.set_title(title);fig.colorbar(v,ax=ax,shrink=.8)
 fig.suptitle('TIC 94753488, Sector 39 — exploratory; unresolved blends remain');fig.tight_layout();fig.savefig(ROOT/'figures/94753488_pixel_diagnostic.png',dpi=160)
 print(json.dumps(result,indent=2))
