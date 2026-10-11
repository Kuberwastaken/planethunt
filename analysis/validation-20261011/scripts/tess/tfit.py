"""Transit fit for TIC 309780779 on native-cadence SPOC/QLP FFI flux.
Per-event linear baselines profiled out; errors scaled by white rms and beta.
mode: free (free a/R) | rho (Gaussian prior on rho* from TIC: M=0.83, R=0.685)
subset: all | disc (sectors<=38) | late (>=61)"""
import sys, json, numpy as np, batman, emcee
sys.path.insert(0,'/root/ph/work/tess'); from common import *
mode=sys.argv[1]; subset=sys.argv[2]; nstep=int(sys.argv[3]); seed=int(sys.argv[4]) if len(sys.argv)>4 else 0
np.random.seed(seed)
t,f,e,s,x=load()
sel={'all':np.ones_like(t,bool),'disc':s<=38,'late':s>=61}[subset]
t,f,e,s,x=t[sel],f[sel],e[sel],s[sel],x[sel]
P0_,T0_=P0,T00
Tref=T0_+P0_*np.round((np.median(t)-T0_)/P0_)
n=np.round((t-Tref)/P0_); dt=t-(Tref+n*P0_); W=0.3; m=np.abs(dt)<W
t,f,e,x,n,dt=t[m],f[m],e[m],x[m],n[m].astype(int),dt[m]
keep=[k for k in np.unique(n) if ((n==k)&(np.abs(dt)>0.06)).sum()>=10 and ((n==k)&(np.abs(dt)<0.015)).sum()>=1]
s_=np.isin(n,keep); t,f,e,x,n,dt=t[s_],f[s_],e[s_],x[s_],n[s_],dt[s_]
idx=[np.where(n==k)[0] for k in keep]
# noise: per-cadence-group white scale and beta from out-of-transit residuals
oot=np.abs(dt)>0.06; E=e.copy(); info={}
for ex in np.unique(x):
    g=(x==ex); r=[];ee=[]
    for ii in idx:
        j=ii[g[ii]&oot[ii]]
        if len(j)<6: continue
        c=np.polyfit(dt[j],f[j],1); r.append(f[j]-np.polyval(c,dt[j])); ee.append(e[j])
    rr=np.concatenate(r); sc=np.std(rr)/np.median(np.concatenate(ee))
    nb=max(1,int(round(3600/ex)))  # 1 h bins
    bm=[];
    for q in r:
        for a in range(0,len(q)-nb+1,nb): bm.append(q[a:a+nb].mean())
    beta=max(1.,np.std(bm)/(np.std(rr)/np.sqrt(nb)))
    E[g]=e[g]*sc*beta; info[int(ex)]=dict(white_scale=float(sc),beta=float(beta))
print(subset,mode,'events',len(keep),'points',len(t),info)
pm=batman.TransitParams(); pm.t0=0; pm.per=P0_; pm.rp=0.02; pm.a=24.; pm.inc=88.; pm.ecc=0; pm.w=90; pm.u=[0.45,0.2]; pm.limb_dark='quadratic'
groups=[(ex,np.where(x==ex)[0]) for ex in np.unique(x)]
models=None
def lc(th):
    T0,P,k,b,lar=th; ar=np.exp(lar)
    pm.per=P; pm.rp=k; pm.a=ar; pm.inc=np.degrees(np.arccos(min(b/ar,1)))
    out=np.empty_like(t); tt=t-(T0+n*P)
    for ex,g in groups:
        mm=batman.TransitModel(pm,tt[g],supersample_factor=max(1,int(ex/120)),exp_time=ex/86400); out[g]=mm.light_curve(pm)
    return out
rho_tic=0.83/0.685**3
def lnp(th):
    T0,P,k,b,lar=th; ar=np.exp(lar)
    if not(0.003<k<0.5 and 0<=b<1+k and 3<ar<150): return -np.inf
    lp=0.
    if mode=='rho':
        rho=3*np.pi*ar**3/(6.674e-8*(P*86400)**2)/1.408
        lp+=-0.5*((rho-rho_tic)/(0.15*rho_tic))**2
    mm=lc(th); chi=0.
    for ii in idx:
        A=np.vstack([mm[ii],mm[ii]*dt[ii]]).T/E[ii,None]; y=f[ii]/E[ii]
        c,*_=np.linalg.lstsq(A,y,rcond=None); chi+=np.sum((y-A@c)**2)
    return lp-0.5*chi
from scipy.optimize import minimize
best=None
for b0 in (0.2,0.6,0.9,0.98):
    th0=np.array([Tref,P0_,0.021,b0,np.log(24.)])
    r=minimize(lambda q:-lnp(q),th0,method='Nelder-Mead',options=dict(maxiter=4000,xatol=1e-7,fatol=1e-3))
    if best is None or r.fun<best.fun: best=r
print('ML',best.x,-best.fun)
nw=20; p0=best.x+np.array([3e-4,3e-6,1e-3,0.02,0.02])*np.random.randn(nw,5); p0[:,3]=np.clip(np.abs(p0[:,3]),0,1.0)
S=emcee.EnsembleSampler(nw,5,lnp); S.run_mcmc(p0,nstep,progress=False)
ch=S.get_chain(discard=nstep//3,flat=True); lpch=S.get_log_prob(discard=nstep//3,flat=True); ch=ch[np.isfinite(lpch)]
out=dict(mode=mode,subset=subset,n_events=len(keep),n_points=int(len(t)),noise=info,acceptance=float(np.mean(S.acceptance_fraction)),Tref=float(Tref),ML=best.x.tolist())
def q(v): a=np.percentile(v,[16,50,84]); return [float(a[1]),float(a[1]-a[0]),float(a[2]-a[1])]
for i,nm in enumerate(['T0','P','k','b','ln_aR']): out[nm]=q(ch[:,i])
ar=np.exp(ch[:,4]); out['aR']=q(ar)
out['rho_solar']=q(3*np.pi*ar**3/(6.674e-8*(ch[:,1]*86400)**2)/1.408)
inc=np.arccos(ch[:,3]/ar); 
arg=np.sqrt(np.clip((1+ch[:,2])**2-ch[:,3]**2,0,None))/ar/np.sin(inc)
out['T14_h']=q(ch[:,1]/np.pi*np.arcsin(np.clip(arg,0,1))*24)
out['Rp_earth_R0.685']=q(ch[:,2]*0.685*109.08)
out['frac_grazing(b>1-k)']=float(np.mean(ch[:,3]>1-ch[:,2]))
for k,v in out.items(): print(k,v)
np.save('/root/ph/work/tess/chain_%s_%s.npy'%(mode,subset),ch[::5])
json.dump(out,open('/root/ph/work/tess/tfit_%s_%s.json'%(mode,subset),'w'),indent=1)
