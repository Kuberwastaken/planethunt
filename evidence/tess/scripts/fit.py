import sys; sys.path.insert(0,'/tmp/fast/pipeline')
import env, numpy as np, lcsearch as L, batman, json
from scipy.optimize import least_squares
tic=309780779; P0=8.723607282476642; T00=1329.1455684886305
d=np.load(f'/tmp/r/data/lightcurves/{tic}.npz'); lc={k:d[k] for k in d.files}
lc,_,_=L.reject_bad_sectors(lc); c=L.clean(lc)   # no binning
t,f,e,ex=c['time'],c['flux'],c['flux_err'],c['exptime']
ph=((t-T00+P0/2)%P0)-P0/2; m=np.abs(ph)<0.3; t,f,e,ex=t[m],f[m],e[m],ex[m]; print('pts',len(t),'exptimes',sorted(set(ex.astype(int))))
rho=0.83/0.69**3; G=6.674e-8; rho_cgs=rho*1.41
def model(p,tt,exp):
    t0,k,b,P=p
    a=(G*rho_cgs*(P*86400)**2/(3*np.pi))**(1/3)
    pm=batman.TransitParams(); pm.t0=t0; pm.per=P; pm.rp=k; pm.a=a; pm.inc=np.degrees(np.arccos(min(b/a,1))); pm.ecc=0; pm.w=90; pm.u=[0.5,0.2]; pm.limb_dark='quadratic'
    out=np.ones_like(tt)
    for ee in np.unique(exp):
        s=exp==ee; mm=batman.TransitModel(pm,tt[s],supersample_factor=5 if ee>300 else 1,exp_time=ee/86400); out[s]=mm.light_curve(pm)
    return out
def res(p): return (f-model(p,t,ex))/e
best=None
for b0 in (0.1,0.5,0.8,0.95):
  for k0 in (0.021,0.03,0.05):
    r=least_squares(res,[T00,k0,b0,P0],bounds=([T00-0.1,0.005,0,P0-0.001],[T00+0.1,0.3,1.3,P0+0.001]),x_scale=[0.01,0.01,0.1,1e-5])
    chi=np.sum(r.fun**2)
    if best is None or chi<best[0]: best=(chi,r.x,b0,k0)
    print('start',b0,k0,'chi2',round(chi,1),'k',round(r.x[1],4),'b',round(r.x[2],3))
chi,p,_,_=best; print('BEST chi2',round(chi,1),'dof',len(t)-4,'k',round(p[1],4),'b',round(p[2],3),'T0',p[0],'P',p[3])
null=np.sum(((f-1)/e)**2); print('null chi2',round(null,1),'dchi2',round(null-chi,1))
# central-transit-only (b<0.3) best
r=least_squares(lambda q:res([q[0],q[1],0.2,q[2]]),[p[0],0.03,p[3]],bounds=([p[0]-0.1,0.005,p[3]-0.001],[p[0]+0.1,0.3,p[3]+0.001]),x_scale=[0.01,0.01,1e-5]); print('b=0.2 forced chi2',round(np.sum(r.fun**2),1),'k',round(r.x[1],4))
a=(G*rho_cgs*(p[3]*86400)**2/(3*np.pi))**(1/3); print('a/Rs',round(a,1)); print('Rp(Re) best',round(p[1]*0.69*109.1,2))
