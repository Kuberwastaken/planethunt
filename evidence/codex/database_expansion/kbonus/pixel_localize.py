"""Original Kepler pixel difference images with official calibration PRFs.

Conditional source-localization diagnostic, not a calibrated false-positive
probability. Fits local linear backgrounds per transit, then compares PRFs at
the two bright catalog sources. PRF mismatch and inter-pixel correlations are
not captured by formal chi-squared values. No clipping of difference images.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,hashlib,warnings
from pathlib import Path
import numpy as np,requests
from astropy.io import fits
from astropy.wcs import WCS
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')
from lightkurve.prf import KeplerPRF
P=Path(__file__).resolve().parent
class LocalPRF(KeplerPRF):
 def _read_prf_calibration_file(self,path,ext):
  f=P/'pixels'/Path(path).name
  if not f.exists():
   u=path.replace('http://','https://');r=requests.get(u,timeout=60);r.raise_for_status();f.write_bytes(r.content)
   (f.with_suffix('.provenance.json')).write_text(json.dumps({'url':u,'sha256':hashlib.sha256(r.content).hexdigest()}))
  return super()._read_prf_calibration_file(str(f),ext)

def main():
 result=json.loads((P/'results/2103792461826460288.json').read_text());s=result['signals'][0]
 period,epoch,dur=s['period'],s['t0_btjd'],s['duration_hr']/24
 files=sorted((P/'pixels').glob('*_lpd-targ.fits.gz'));rows=[];fig,axes=plt.subplots(len(files),3,figsize=(10,2.5*len(files)),squeeze=False)
 for n,f in enumerate(files):
  with fits.open(f,memmap=False) as h:
   d=h[1].data;t=np.asarray(d['TIME'],float)-2167;good=np.isfinite(t)&(d['QUALITY']==0)
   t=t[good];flux=np.asarray(d['FLUX'][good],float);err=np.asarray(d['FLUX_ERR'][good],float);q=int(h[0].header['QUARTER'])
   shape=flux.shape[1:];wcs=WCS(h[2].header);xy=wcs.all_world2pix([[285.907836,40.941985],[285.905233,40.942079]],0)
   col=float(h[2].header['CRVAL1P']);row=float(h[2].header['CRVAL2P']);channel=int(h[0].header['CHANNEL'])
  fl=flux.reshape(len(t),-1);er=err.reshape(len(t),-1);usable=np.sum(np.isfinite(fl),axis=0)>.9*len(t)
  dep=[];de=[];cycles=[];exp=1765.464/86400
  for cycle in np.unique(np.rint((t-epoch)/period).astype(int)):
   x=t-(epoch+cycle*period);ix=np.abs(x)<.4
   if ix.sum()<15:continue
   x=x[ix];y=fl[ix];e=er[ix];box=np.maximum(0,np.minimum(x+exp/2,dur/2)-np.maximum(x-exp/2,-dur/2))/exp
   if (box>0).sum()<2 or (x < -dur).sum()<4 or (x>dur).sum()<4:continue
   X=np.column_stack([np.ones(len(x)),x/.4,-box]);dd=np.full(fl.shape[1],np.nan);ee=dd.copy()
   for k in np.flatnonzero(usable):
    valid=np.isfinite(y[:,k])&np.isfinite(e[:,k])&(e[:,k]>0)
    if valid.sum()<12:continue
    xx=X[valid];yy=y[valid,k];noise=1.4826*np.median(np.abs(np.diff(yy)-np.median(np.diff(yy))))/np.sqrt(2);ev=np.maximum(e[valid,k],noise);ww=1/ev**2
    try:cov=np.linalg.inv(xx.T@(ww[:,None]*xx))
    except np.linalg.LinAlgError:continue
    beta=cov@(xx.T@(ww*yy));res=yy-xx@beta;inflate=max(1,np.sum(ww*res**2)/max(1,len(yy)-3));dd[k]=beta[2];ee[k]=np.sqrt(cov[2,2]*inflate)
   dep.append(dd);de.append(ee);cycles.append(int(cycle))
  if len(dep)<2:continue
  dep=np.array(dep);de=np.array(de);weights=1/de**2;sw=np.nansum(weights,axis=0);mu=np.nansum(weights*dep,axis=0)/sw;se=np.sqrt(1/sw);robust=np.sqrt(np.nansum(((dep-mu)*weights/sw)**2,axis=0)*len(dep)/(len(dep)-1));se=np.maximum(se,robust);valid=usable&np.isfinite(mu)&np.isfinite(se)&(se>0)
  prf=LocalPRF(channel=channel,shape=shape,column=col,row=row)
  def template(x,y):return prf.evaluate(col+x+.5,row+y+.5).ravel()
  mean=np.nanmedian(fl,axis=0);point_noise=np.nanmedian(er,axis=0);point_noise=np.maximum(point_noise,1.)
  def meanfit(z,ret=False):
   a=template(*(xy[0]+z[:2]));b=template(*(xy[1]+z[:2]));X=np.column_stack([a,b,np.ones(len(a))]);w=1/point_noise[valid];beta=np.linalg.lstsq(X[valid]*w[:,None],mean[valid]*w,rcond=None)[0];r=(X@beta-mean)[valid]*w
   return (beta,X@beta) if ret else r
  offset=least_squares(meanfit,[0,0],bounds=(-.5,.5)).x
  def sourcefit(pos):
   a=template(*pos);X=np.column_stack([a,np.ones(len(a))]);w=1/se[valid];beta=np.linalg.lstsq(X[valid]*w[:,None],mu[valid]*w,rcond=None)[0];res=(X@beta-mu)[valid]*w;cov=np.linalg.inv((X[valid]*w[:,None]).T@(X[valid]*w[:,None]));return {'amplitude':float(beta[0]),'amplitude_error':float(np.sqrt(cov[0,0])),'chi2':float(res@res)},X@beta
  target,target_model=sourcefit(xy[0]+offset);primary,primary_model=sourcefit(xy[1]+offset)
  def centerres(pos):
   a=template(*pos);X=np.column_stack([a,np.ones(len(a))]);w=1/se[valid];beta=np.linalg.lstsq(X[valid]*w[:,None],mu[valid]*w,rcond=None)[0];return (X@beta-mu)[valid]*w
  fit=least_squares(centerres,xy[0]+offset,bounds=([-2,-2],[shape[1]+1,shape[0]+1]));free,_=sourcefit(fit.x)
  out={'quarter':q,'events':len(dep),'target_xy':xy[0].tolist(),'primary_xy':xy[1].tolist(),'mean_astrometric_offset':offset.tolist(),'target_prf':target,'primary_prf':primary,'delta_chi2_primary_minus_target':primary['chi2']-target['chi2'],'free_center_xy':fit.x.tolist(),'free_center_offset_from_target_pixels':(fit.x-xy[0]-offset).tolist(),'free_fit':free,'valid_pixels':int(valid.sum())};rows.append(out)
  np.savez_compressed(P/'pixels'/f'difference_q{q}.npz',difference=mu.reshape(shape),error=se.reshape(shape),mean=mean.reshape(shape),target_model=target_model.reshape(shape),primary_model=primary_model.reshape(shape))
  for ax,img,title in zip(axes[n],[mean.reshape(shape),(mu/se).reshape(shape),(mu-target_model).reshape(shape)/se.reshape(shape)],[f'Q{q}: mean flux',f'Difference / error; {len(dep)} events',f'Target-PRF residual / error']):
   ax.imshow(img,origin='lower',cmap='viridis' if 'mean' in title else 'RdBu_r');ax.scatter(*(xy[0]+offset),marker='x',s=65,c='lime',label='candidate');ax.scatter(*(xy[1]+offset),marker='+',s=80,c='orange',label='primary');ax.set_title(title,fontsize=9)
  axes[n,0].legend(fontsize=7);print(json.dumps(out),flush=True)
 fig.suptitle('KIC 5689121: original Kepler pixels at fixed 13.7694-day ephemeris',y=1.001);fig.tight_layout();fig.savefig(P/'pixels/candidate_difference_images.png',dpi=130,bbox_inches='tight')
 out={'source_id':'2103792461826460288','method':'local per-event pixel baseline fits; official Kepler PRF templates; quiescent two-source fit calibrates common WCS offset','caveat':'Conditional diagnostic only. Pixel covariances and PRF-model mismatch not calibrated; chi-square differences are not a planet false-positive probability. Gaia2016 coordinates not proper-motion propagated here.','quarters':rows,'sum_delta_chi2_primary_minus_target':sum(r['delta_chi2_primary_minus_target'] for r in rows)}
 (P/'pixels/localization.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__':main()
