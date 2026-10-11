"""Full-baseline transit fit of KIC 5689121 (KBonus PSF flux), all 13 quarters.
Per-event local linear baselines are profiled out analytically. Errors inflated by beta
measured from out-of-transit binned scatter at the transit timescale."""
import json, numpy as np, batman, emcee, sys
D=np.load('/root/ph/rel/kx/planet-search/database_expansion/kbonus_independent_audit/2103792461826460288_correct_errors.npz')
which=sys.argv[1] if len(sys.argv)>1 else 'psf'
t=D['time']; f=D['flux'] if which=='psf' else D['sap_flux']; e=D['flux_err'] if which=='psf' else D['sap_flux_err']
ok=np.isfinite(t)&np.isfinite(f)&np.isfinite(e)&(e>0); t,f,e=t[ok],f[ok],e[ok]
P0=13.769413569662944; T00=-2030.687110167298
Tmid_ref=T00+P0*np.round((np.median(t)-T00)/P0)   # reference epoch near baseline middle -> decorrelates P,T0
W=0.35
n=np.round((t-Tmid_ref)/P0); dt=t-(Tmid_ref+n*P0); m=np.abs(dt)<W
t,f,e,n=t[m],f[m],e[m],n[m].astype(int)
# per-event normalisation of the flux (median out of transit)
ev=np.unique(n); keep=[]
for k in ev:
    s=n==k; o=s&(np.abs(dt[m])>0.1)
    if o.sum()<8 or (s&(np.abs(dt[m])<0.05)).sum()<2: continue
    keep.append(k)
sel=np.isin(n,keep); t,f,e,n=t[sel],f[sel],e[sel],n[sel]
idx=[np.where(n==k)[0] for k in keep]
print(which,'events used',len(keep),'points',len(t))
# beta (time-correlated noise) from out-of-transit residuals binned at ~2 h
dtt=t-(Tmid_ref+n*P0); oot=np.abs(dtt)>0.1
res=[]
for ii in idx:
    j=ii[oot[ii]]
    if len(j)<6: continue
    c=np.polyfit(t[j]-t[j].mean(),f[j],1); res.append((t[j],f[j]-np.polyval(c,t[j]-t[j].mean()),e[j]))
r=np.concatenate([x[1] for x in res]); ee=np.concatenate([x[2] for x in res])
sig1=np.std(r); Nb=4  # 4 x 29.4 min ~ 2 h
binned=[]
for tt,rr,_ in res:
    for s0 in range(0,len(rr)-Nb+1,Nb): binned.append(rr[s0:s0+Nb].mean())
beta=max(1.0,np.std(binned)/(sig1/np.sqrt(Nb)*np.sqrt(len(binned)/(len(binned)-1))))
scale=sig1/np.median(ee)
print('white rms/median err %.3f, beta %.3f'%(scale,beta))
E=np.median(ee)*scale*beta*np.ones_like(e)*(e/np.median(e))
params=batman.TransitParams(); params.t0=0; params.per=P0; params.rp=0.05; params.a=35.5; params.inc=89.
params.ecc=0; params.w=90; params.u=[0.45,0.25]; params.limb_dark='quadratic'
mdl=batman.TransitModel(params,t-(Tmid_ref+n*P0),supersample_factor=7,exp_time=1765.464/86400)
def model(th):
    T0,P,k,b,logar=th
    ar=np.exp(logar)
    if not(0<k<0.3 and 0<=b<1+k and 2<ar<200): return None
    params.t0=0; params.per=P; params.rp=k; params.a=ar
    params.inc=np.degrees(np.arccos(b/ar))
    x=t-(T0+n*P)
    mdl.t=x  # batman uses ds computed at init; recompute safely:
    m=batman.TransitModel(params,x,supersample_factor=7,exp_time=1765.464/86400)
    return m.light_curve(params)
def lnl(th,ret=False):
    mm=model(th)
    if mm is None: return -np.inf
    chi=0.
    for ii in idx:
        A=np.vstack([mm[ii],mm[ii]*(t[ii]-t[ii].mean())]).T/E[ii,None]
        y=f[ii]/E[ii]
        c,*_=np.linalg.lstsq(A,y,rcond=None)
        chi+=np.sum((y-A@c)**2)
    return -0.5*chi
# prior: stellar density from Gaia (rho=3.18 solar) only used for an optional comparison; fit free a/R
th0=np.array([Tmid_ref,P0,0.05,0.6,np.log(35.5)])
from scipy.optimize import minimize
best=minimize(lambda x:-lnl(x),th0,method='Nelder-Mead',options=dict(maxiter=6000,xatol=1e-7,fatol=1e-3))
print('ML',best.x,best.fun)
nw=24; p0=best.x+np.array([2e-4,2e-6,1e-3,0.02,0.01])*np.random.randn(nw,5)
p0[:,3]=np.abs(p0[:,3])
S=emcee.EnsembleSampler(nw,5,lnl); S.run_mcmc(p0,int(sys.argv[2]) if len(sys.argv)>2 else 3000,progress=False)
ch=S.get_chain(discard=S.iteration//3,flat=True)
names=['T0_btjd','P','k','b','ln_aR']
out={'flux':which,'n_events':len(keep),'beta':beta,'white_scale':scale,'T0_ref_btjd':float(Tmid_ref),'acceptance':float(np.mean(S.acceptance_fraction))}
for i,nm in enumerate(names):
    q=np.percentile(ch[:,i],[16,50,84]); out[nm]=[float(q[1]),float(q[1]-q[0]),float(q[2]-q[1])]
    print('%-8s %.7f -%.7f +%.7f'%(nm,q[1],q[1]-q[0],q[2]-q[1]))
ar=np.exp(ch[:,4]); rho=3*np.pi*ar**3/(6.674e-8*(ch[:,1]*86400)**2)/1.408
q=np.percentile(rho,[16,50,84]); out['rho_star_solar']=[float(q[1]),float(q[1]-q[0]),float(q[2]-q[1])]
print('rho* (solar) %.2f -%.2f +%.2f'%(q[1],q[1]-q[0],q[2]-q[1]))
dep=ch[:,2]**2*1e6; q=np.percentile(dep,[16,50,84]); out['k2_ppm']=[float(q[1]),float(q[1]-q[0]),float(q[2]-q[1])]
np.save('/root/ph/work/kchain_%s.npy'%which,ch[::10])
json.dump(out,open('/root/ph/work/kfit_%s.json'%which,'w'),indent=1)
