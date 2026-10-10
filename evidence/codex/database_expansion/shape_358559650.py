"""Exploratory fixed-period shape comparison for timing-clean TIC358559650.

Phase-bin errors use per-event cluster scatter; models are exposure integrated
on the actual native timestamps before binning. Chi-square/BIC are descriptive
under a diagonal-bin approximation, not classification or discovery odds.
"""
import json,sys
from pathlib import Path
import numpy as np,pandas as pd
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from wotan import flatten
import batman

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
sys.path.insert(0,str(PROJECT/'improvements'))
from independent_vet import load,combine
from broad_signal_vet import events


def prepare(lc,window=1.):
    out=[]
    for s in np.unique(lc['sector']):
        m=lc['sector']==s;t,f=lc['time'][m],lc['flux'][m]
        flat=flatten(t,f,method='biweight',window_length=window,break_tolerance=.5)
        ok=np.isfinite(flat);sd=1.4826*np.median(np.abs(flat[ok]-np.median(flat[ok])))
        ok &= np.abs(flat-np.median(flat[ok]))<8*sd
        err=np.maximum(lc['flux_err'][m],sd)
        out.append({'time':t[ok],'flux':flat[ok],'flux_err':err[ok],
                    'sector':lc['sector'][m][ok],'exptime':lc['exptime'][m][ok]})
    result={k:np.concatenate([d[k] for d in out]) for k in out[0]}
    o=np.argsort(result['time']);return {k:v[o] for k,v in result.items()}


def profile(lc,P,t0,nb=80):
    ph=(lc['time']-t0+P/2)%P-P/2
    key=np.minimum(nb-1,np.floor((ph/P+.5)*nb).astype(int))
    w=1/lc['flux_err']**2;y=(lc['flux']-1)*1e6
    sw=np.bincount(key,w,minlength=nb);val=np.bincount(key,w*y,minlength=nb)/sw
    err=1e6/np.sqrt(sw)
    cycles=np.rint((lc['time']-t0)/P).astype(int)
    for b in range(nb):
        idx=np.where(key==b)[0]
        if len(idx)<2:continue
        uniq,inv=np.unique(cycles[idx],return_inverse=True)
        cw=np.bincount(inv,w[idx]);cy=np.bincount(inv,w[idx]*y[idx])/cw
        a=cw/cw.sum();mu=a@cy
        cluster=np.sqrt(np.sum((a*(cy-mu))**2)*len(a)/(len(a)-1)) if len(a)>1 else 0
        err[b]=max(err[b],cluster)
    return {'phase_days':ph,'key':key,'weights':w,'sum_weights':sw,'centers':((np.arange(nb)+.5)/nb-.5)*P,'flux_ppm':val,'error_ppm':err}


def fit_models(lc,P,t0,ars):
    pr=profile(lc,P,t0);ph=pr['phase_days'];ex=lc['exptime']/86400;nb=len(pr['centers'])
    valid=np.isfinite(pr['flux_ppm'])&np.isfinite(pr['error_ppm'])&(pr['error_ppm']>0)
    def fold(values):return np.bincount(pr['key'],pr['weights']*values,minlength=nb)/pr['sum_weights']
    # Exposure-average Fourier terms analytically using sinc attenuation.
    fits={}
    for nh in (1,2):
        cols=[np.ones(len(ph))]
        for k in range(1,nh+1):
            attenuation=np.sinc(k*ex/P);angle=2*np.pi*k*ph/P
            cols.extend([np.cos(angle)*attenuation,np.sin(angle)*attenuation])
        X=np.column_stack([fold(c) for c in cols]);A=X[valid]/pr['error_ppm'][valid,None]
        b=pr['flux_ppm'][valid]/pr['error_ppm'][valid];coef=np.linalg.lstsq(A,b,rcond=None)[0]
        model=X@coef;chi=float(np.sum(((model[valid]-pr['flux_ppm'][valid])/pr['error_ppm'][valid])**2))
        fits[f'fourier_{nh}']={'n_parameters':len(coef),'chi2_diagonal_bins':chi,'bic_diagonal_bins':chi+len(coef)*np.log(valid.sum()),'coefficients_ppm':coef.tolist(),'model_ppm':model.tolist()}
    pars=batman.TransitParams();pars.t0=0;pars.per=P;pars.rp=.02;pars.a=ars;pars.inc=89.;pars.ecc=0.;pars.w=90.;pars.u=[.5,.2];pars.limb_dark='quadratic'
    groups=[]
    for exp in np.unique(ex):
        m=ex==exp
        groups.append((m,batman.TransitModel(pars,ph[m],supersample_factor=11,exp_time=float(exp))))
    def transit(theta,free_density=False):
        k,bfrac,center,offset=theta[:4];a=theta[4] if free_density else ars
        pars.rp=k;pars.a=a;pars.inc=np.degrees(np.arccos(np.clip(bfrac*(1+k)/a,-1,1)));pars.t0=center
        values=np.empty(len(ph))
        for mask,model in groups:values[mask]=(model.light_curve(pars)-1)*1e6+offset
        return fold(values)
    for free in (False,True):
        x0=[.018,.2,0.,0.]+([ars*.75] if free else [])
        lo=[.0003,0.,-.12*P,-1000.]+([1.3] if free else [])
        hi=[.2,.99,.12*P,1000.]+([10.] if free else [])
        sol=least_squares(lambda x:(transit(x,free)[valid]-pr['flux_ppm'][valid])/pr['error_ppm'][valid],x0,bounds=(lo,hi),max_nfev=180,diff_step=1e-4)
        model=transit(sol.x,free);chi=float(np.sum(sol.fun**2));k=len(sol.x)
        fits['transit_free_density' if free else 'transit_catalog_density']={'n_parameters':k,'chi2_diagonal_bins':chi,'bic_diagonal_bins':chi+k*np.log(valid.sum()),'parameters':dict(zip(['radius_ratio','impact_fraction','epoch_shift_days','offset_ppm']+(['a_over_rstar'] if free else []),map(float,sol.x))),'fixed_a_over_rstar':None if free else ars,'fixed_limb_darkening':[.5,.2],'optimizer_success':bool(sol.success),'model_ppm':model.tolist()}
    return pr,fits


def main():
    branch=ROOT/'timing_safe_repeat';r=json.loads((branch/'results/358559650_usp.json').read_text());s=r['signals'][0]
    P,t0,D=s['period'],s['t0'],s['duration_hr']/24;raw=load(branch/'lightcurves/358559650.npz');lc=prepare(raw)
    star=pd.read_csv(PROJECT/'targets.csv').query('TIC==358559650').iloc[0]
    ars=(2.959122e-4*star.Mass*P**2/(4*np.pi**2))**(1/3)/(star.Rad*.00465047)
    pr,fits=fit_models(lc,P,t0,ars)
    doubles={}
    for parity in (0,1):
        ev=events(raw,2*P,t0+parity*P,D,.2,2)
        doubles[str(parity)]={'all':combine(ev),'holdout':combine([v for v in ev if v['sector'] in r['holdout_sectors']])}
    a,b=doubles['0']['all'],doubles['1']['all'];z=(a['depth_ppm']-b['depth_ppm'])/np.hypot(a['error_ppm'],b['error_ppm'])
    report={'tic':358559650,'period_days':P,'epoch_btjd':t0,'exposure_integration':'Native exposure durations, batman supersampling11; Fourier terms analytically exposure averaged; models binned with exact data weights.',
            'preparation':'Each sector biweight-flattened with fixed 1.0d window; symmetric8MAD clipping. Exploratory diagnostic, not new independent confirmation.',
            'profile_errors':'Maximum of white weighted error and per-event cluster scatter; correlations between phase bins not modeled.',
            'statistical_caution':'Chi-square/BIC use diagonal-bin approximation and are descriptive only; not validated model probabilities or a discovery FAP.',
            'models':fits,'double_period_event_comparison':doubles,'double_period_odd_even_sigma':float(abs(z)),
            'phase_bins':{'phase_hours':(pr['centers']*24).tolist(),'flux_ppm':pr['flux_ppm'].tolist(),'error_ppm':pr['error_ppm'].tolist()}}
    (branch/'shape_comparison.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(3,1,figsize=(11,11),constrained_layout=True)
    ax=axes[0];ax.errorbar(pr['centers']*24,pr['flux_ppm'],yerr=pr['error_ppm'],fmt='.',color='black',label='Phase bins; event-cluster errors',alpha=.8)
    colors={'fourier_1':'#648c32','fourier_2':'#cb6e24','transit_catalog_density':'#ce4052','transit_free_density':'#365fbc'}
    for name in fits:ax.plot(pr['centers']*24,fits[name]['model_ppm'],label=name.replace('_',' '),color=colors[name])
    ax.set(title='TIC 358559650 — timing-clean broad periodic dimming; unresolved source/nature',ylabel='Relative flux (ppm)',xlabel='Hours from fixed search epoch');ax.legend(ncol=2,fontsize=8)
    ax=axes[1]
    groups={'Discovery: S9/36/62/63':[9,36,62,63],'Reassigned holdout: S89/90':[89,90]}
    for name,secs in groups.items():
        m=np.isin(lc['sector'],secs);sub={k:v[m] for k,v in lc.items()};p=profile(sub,P,t0,50)
        ax.errorbar(p['centers']*24,p['flux_ppm'],yerr=p['error_ppm'],fmt='.-',label=name,alpha=.8)
    ax.set(xlabel='Hours from fixed search epoch',ylabel='Relative flux (ppm)',title='Separate retained-season profiles; holdout is retrospective');ax.legend()
    ax=axes[2];p=profile(lc,2*P,t0,100);ax.errorbar(p['centers']*24,p['flux_ppm'],yerr=p['error_ppm'],fmt='.',color='#604595')
    ax.set(xlabel='Hours folded on 2P',ylabel='Relative flux (ppm)',title=f'Doubled-period check: alternating event-depth difference {abs(z):.2f}σ (conditional)')
    fig.savefig(branch/'358559650_timing_safe_shape.png',dpi=180);plt.close(fig)
    print(json.dumps({'models':{n:{k:v[k] for k in ('chi2_diagonal_bins','bic_diagonal_bins')}|{'parameters':v.get('parameters')} for n,v in fits.items()},'double_period_odd_even_sigma':abs(z)},indent=2),flush=True)


if __name__=='__main__':main()
