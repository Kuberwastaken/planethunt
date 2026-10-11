"""Fixed-ephemeris box depth with per-event local linear baselines (out-of-transit only).
Error = scatter of per-event depths / sqrt(N) (empirical, includes red noise)."""
import numpy as np, json, sys
def depth(t,f,P,T0,dur,W=0.4):
    n=np.round((t-T0)/P); dt=t-(T0+n*P); ds=[]
    for k in np.unique(n[np.abs(dt)<W]):
        s=(n==k)&(np.abs(dt)<W); i=s&(np.abs(dt)<dur/2*0.8); o=s&(np.abs(dt)>dur/2+0.03)
        if i.sum()<2 or o.sum()<8: continue
        c=np.polyfit(t[o]-t[o].mean(),f[o],1); base=np.polyval(c,t[i]-t[o].mean())
        ds.append(np.mean(1-f[i]/base))
    ds=np.array(ds); 
    return len(ds), ds.mean()*1e6, ds.std(ddof=1)/np.sqrt(len(ds))*1e6
def load(p,col='flux'):
    d=np.load(p); t=d['time']; f=d[col]; ok=np.isfinite(t)&np.isfinite(f); return t[ok],f[ok]
if __name__=='__main__':
    tgt='/root/ph/rel/kx/planet-search/database_expansion/kbonus_independent_audit/2103792461826460288_correct_errors.npz'
    nb='/root/ph/rel/kx/planet-search/database_expansion/kbonus/lightcurves/2103792427466721792.npz'
    fit=json.load(open('/root/ph/work/kfit_psf.json'))
    P=fit['P'][0]; T0=fit['T0_btjd'][0]; dur=2.2/24
    out={}
    t,f=load(tgt)
    out['target_psf_at_candidate']=depth(t,f,P,T0,dur)
    ts,fs=load(tgt,'sap_flux'); out['target_sap_at_candidate']=depth(ts,fs,P,T0,dur)
    for nm,(p,t0bk,dh) in {'K169e':(13.767101,174.81089,2.9105),'K169c':(6.19546,134.71507,2.952),'K169b':(3.250582,133.69472,2.2537),'K169d':(8.348192,136.84111,2.835),'K169f':(87.091259,187.31231,7.0)}.items():
        out['target_psf_at_'+nm]=depth(t,f,p,t0bk-2167,dh/24)
        out['target_sap_at_'+nm]=depth(ts,fs,p,t0bk-2167,dh/24)
    tn,fn=load(nb); out['neighbor5689116_psf_at_candidate']=depth(tn,fn,P,T0,dur)
    tn2,fn2=load(nb,'sap_flux'); out['neighbor5689116_sap_at_candidate']=depth(tn2,fn2,P,T0,dur)
    for k,v in out.items(): print('%-38s N=%3d depth %8.1f +/- %6.1f ppm (%.1f sigma)'%(k,v[0],v[1],v[2],v[1]/v[2]))
    json.dump(out,open('/root/ph/work/kdepth.json','w'),indent=1)
