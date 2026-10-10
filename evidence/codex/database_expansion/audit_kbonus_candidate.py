"""Independent protected-baseline, exposure-integrated audit of KIC5689121.
Period fixed to discovery search. Local baselines use out-of-transit points only;
transit shape fitted to discovery quarters only. Holdout is never used to tune.
Shape fits are conditional descriptive fits, not false-positive probabilities.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,sys,hashlib
from pathlib import Path
import numpy as np
from astropy.io import fits
from scipy.optimize import least_squares
import batman
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent;KB=ROOT/'kbonus';OUT=ROOT/'kbonus_independent_audit';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT.parent/'improvements'))
from independent_vet import vet,mad
SID='2103792461826460288'
r=json.loads((KB/'results'/f'{SID}.json').read_text());s=r['signals'][0];P=s['period'];E=s['t0_btjd'];D=s['duration_hr']/24;H=r['holdout_quarters']

def load_column(column,errcolumn):
 parts=[]
 with fits.open(KB/'fits'/f'{SID}.fits') as hdus:
  ex=hdus[0].header['XPOSURE']
  for h in hdus:
   if not h.name.startswith('LIGHTCURVE_Q') or h.header['PSFFRAC']<.5:continue
   d=h.data;t=np.asarray(d['TIME'],float)-2167;f=np.asarray(d[column],float);e=np.asarray(d[errcolumn],float)
   m=(d['SAP_QUALITY']==0)&np.isfinite(t)&np.isfinite(f)&np.isfinite(e)&(e>0)
   if m.sum()<300:continue
   med=np.median(f[m]);n=m.sum()
   parts.append(dict(time=t[m],flux=f[m]/med,flux_err=e[m]/med,sector=np.full(n,int(h.header['QUARTER'])),exptime=np.full(n,ex)))
 result={k:np.concatenate([a[k] for a in parts]) for k in parts[0]};ix=np.argsort(result['time']);return {k:v[ix] for k,v in result.items()}

def prepare(raw,window=.4,degree=1):
 arr=[];t=raw['time'];cyc=np.rint((t-E)/P).astype(int)
 for n in np.unique(cyc):
  for q in np.unique(raw['sector'][cyc==n]):
   m=(cyc==n)&(raw['sector']==q)&(np.abs(t-(E+n*P))<window)
   x=t[m]-(E+n*P);y=raw['flux'][m];er=raw['flux_err'][m]
   oot=np.abs(x)>D # masks twice total BLS duration around center
   if (x[oot]<0).sum()<5 or (x[oot]>0).sum()<5:continue
   empirical=max(mad(np.diff(y[oot]))/np.sqrt(2),1e-8);er=np.maximum(er,empirical)
   X=np.column_stack([(x/window)**k for k in range(degree+1)])
   beta=np.linalg.lstsq(X[oot]/er[oot,None],y[oot]/er[oot],rcond=None)[0];trend=X@beta
   arr.append(dict(time=x,flux=y/trend,flux_err=er/trend,sector=raw['sector'][m],exptime=raw['exptime'][m],cycle=np.full(len(x),n)))
 return {k:np.concatenate([a[k] for a in arr]) for k in arr[0]}

def profile(d,nb=48,window=.4):
 ix=np.clip(((d['time']/window+1)/2*nb).astype(int),0,nb-1);w=1/d['flux_err']**2;y=(d['flux']-1)*1e6
 sw=np.bincount(ix,w,minlength=nb);mu=np.bincount(ix,w*y,minlength=nb)/sw;err=1e6/np.sqrt(sw)
 for b in range(nb):
  m=ix==b;u,inv=np.unique(d['cycle'][m],return_inverse=True)
  if len(u)<2:continue
  ew=np.bincount(inv,w[m]);ey=np.bincount(inv,w[m]*y[m])/ew;a=ew/ew.sum()
  err[b]=max(err[b],np.sqrt(np.sum((a*(ey-a@ey))**2)*len(a)/(len(a)-1)))
 return dict(centers=(np.arange(nb)+.5)*2*window/nb-window,flux=mu,error=err,bin=ix,weight=w,sumw=sw)

def sub(d,m):return {k:v[m] for k,v in d.items()}

def fit(d,ld):
 pr=profile(d);pars=batman.TransitParams();pars.t0=0;pars.per=P;pars.rp=.05;pars.a=40;pars.inc=89;pars.ecc=0;pars.w=90;pars.u=ld;pars.limb_dark='quadratic'
 model=batman.TransitModel(pars,d['time'],supersample_factor=15,exp_time=float(np.median(d['exptime'])/86400))
 def flux(theta,times=None):
  k,b,a,shift,offset=theta;pars.rp=k;pars.a=a;pars.inc=np.degrees(np.arccos(b/a));pars.t0=shift
  m=model if times is None else batman.TransitModel(pars,times,supersample_factor=15,exp_time=float(np.median(d['exptime'])/86400))
  return (m.light_curve(pars)-1)*1e6+offset
 def binned(theta):return np.bincount(pr['bin'],pr['weight']*flux(theta),minlength=len(pr['centers']))/pr['sumw']
 valid=np.isfinite(pr['flux'])&np.isfinite(pr['error'])&(pr['error']>0)
 sols=[]
 for b0 in (0.05,.4,.8,.98):
  sol=least_squares(lambda th:(binned(th)[valid]-pr['flux'][valid])/pr['error'][valid],[.047,b0,40,0,0],bounds=([.002,0,3,-D,-500],[.3,1.2,150,D,500]),max_nfev=500,diff_step=1e-4)
  sols.append(sol)
 sol=min(sols,key=lambda v:np.sum(v.fun**2));k,b,a,shift,offset=sol.x
 # Exact circular first-to-fourth contact duration; no eccentricity constraint.
 dur=P/np.pi*np.arcsin(np.sqrt(max(0,(1+k)**2-b*b))/np.sqrt(a*a-b*b))*24
 rho=3*np.pi/(6.67430e-11*(P*86400)**2)*a**3/1408
 return {'parameters':dict(zip(['radius_ratio','impact_parameter','a_over_rstar','epoch_shift_days','offset_ppm'],map(float,sol.x))),'duration_contact_hours':float(dur),'circular_stellar_density_solar':float(rho),'fixed_limb_darkening':ld,'chi2_diagonal_bins':float(np.sum(sol.fun**2)),'n_bins':int(valid.sum()),'optimizer_success':bool(sol.success)},pr,flux,binned(sol.x)

def main():
 report={'source_id':SID,'kic':5689121,'period_fixed_days':P,'epoch_btjd':E,'discovery_quarters':r['discovery_quarters'],'holdout_quarters':H,'original_fits_sha256':hashlib.sha256((KB/'fits'/f'{SID}.fits').read_bytes()).hexdigest(),'limitations':['Conditional descriptive shape fit, no astrophysical false-positive probability.','No source localization or dilution correction.','Circular density is model-conditional, eccentricity unconstrained.','Event-baseline errors induce correlated phase bins; diagonal chi-square not independent likelihood.']}
 raw=load_column('FLUX','FLUX_ERR');sap=load_column('SAP_FLUX','SAP_FLUX_ERR');report['sap_matching_error_vet']=vet(sap,P,E,D,holdout=H,controls=24,holdout_was_unseen=True)
 fig,axes=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
 fitsout=[]
 for degree in (1,2):
  d=prepare(raw,degree=degree);train=sub(d,~np.isin(d['sector'],H));test=sub(d,np.isin(d['sector'],H))
  for ld in ([.5,.2],[.3,.2]):
   result,pr,model,pred=fit(train,ld);result['baseline_degree']=degree;fitsout.append(result)
   if degree==1 and ld==[.5,.2]:
    theta=list(result['parameters'].values());pt=profile(test);ym=model(theta,test['time']);templ=ym-theta[-1]
    # Fixed discovery shape/epoch, fit holdout depth scale and constant only.
    A=np.column_stack([templ,np.ones(len(templ))]);err=test['flux_err']*1e6
    beta=np.linalg.lstsq(A/err[:,None],(test['flux']-1)*1e6/err,rcond=None)[0]
    report['fixed_shape_holdout_scale']=float(beta[0]);report['fixed_shape_holdout_offset_ppm']=float(beta[1]);report['training_events']=len(np.unique(train['cycle']));report['holdout_events']=len(np.unique(test['cycle']))
    axes[0,0].errorbar(pr['centers']*24,pr['flux'],yerr=pr['error'],fmt='.',color='#305fa2',label='Discovery quarters');axes[0,0].plot(pr['centers']*24,pred,color='#cf563a',label='Integrated circular transit fit')
    axes[0,1].errorbar(pt['centers']*24,pt['flux'],yerr=pt['error'],fmt='.',color='#217b64',label='Reserved quarters')
    mt=np.bincount(pt['bin'],pt['weight']*(templ*beta[0]+beta[1]),minlength=len(pt['centers']))/pt['sumw'];axes[0,1].plot(pt['centers']*24,mt,color='#cf563a',label='Fixed discovery shape, depth rescaled')
    for ax in axes[0]:ax.set(xlim=(-4,4),xlabel='Hours from discovery search epoch',ylabel='Relative flux (ppm)');ax.legend(fontsize=8)
    axes[0,0].set_title('KIC 5689121: discovery-only physical shape fit');axes[0,1].set_title('Holdout shape at frozen period and epoch')
 # Per-quarter depth comparison, independent extraction errors.
 for column,rawdata,col in [('PSF',raw,'#305fa2'),('SAP',sap,'#b66027')]:
  v=vet(rawdata,P,E,D,holdout=H,controls=0,holdout_was_unseen=True)
  qq=[];dd=[];ee=[]
  for q,val in v['per_sector'].items():qq.append(int(q));dd.append(val['depth_ppm']);ee.append(val['error_ppm'])
  axes[1,0].errorbar(np.array(qq)+(-.12 if column=='PSF' else .12),dd,yerr=ee,fmt='o',label=column,color=col,markersize=4)
  seasons={}
  from independent_vet import combine
  for season in range(4):seasons[str(season)]=combine([e for e in v['events'] if e['sector']%4==season])
  report[column.lower()+'_season_depths']=seasons
  dp=prepare(rawdata);pr=profile(dp);axes[1,1].errorbar(pr['centers']*24,pr['flux'],yerr=pr['error'],fmt='.-',label=column,color=col,alpha=.75)
 axes[1,0].set(xlabel='Kepler quarter',ylabel='Local event depth (ppm)',title='Depth stability and extraction dependence');axes[1,0].axvline(11.5,color='grey',linestyle='--');axes[1,0].legend()
 axes[1,1].set(xlim=(-4,4),xlabel='Hours from fixed epoch',ylabel='Relative flux (ppm)',title='Both extractions: protected linear local baselines');axes[1,1].legend()
 report['discovery_shape_sensitivity_fits']=fitsout
 (OUT/'2103792461826460288.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');fig.savefig(OUT/'2103792461826460288_shape.png',dpi=180)
 print(json.dumps({'fits':fitsout,'holdout_scale':report['fixed_shape_holdout_scale'],'sap_vet':report['sap_matching_error_vet']['primary'],'sap_hold':report['sap_matching_error_vet']['holdout']},indent=2),flush=True)
if __name__=='__main__':main()
