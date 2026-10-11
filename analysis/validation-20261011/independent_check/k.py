import numpy as np, sys
d=np.load(sys.argv[1]); t=d['time']; f=d['flux']; e=d['flux_err']; q=d['sector']
m=np.isfinite(t)&np.isfinite(f)&np.isfinite(e); t,f,e,q=t[m],f[m],e[m],q[m]
def boxdepth(P,T0,dur_h,win_h=None,verbose=False):
    dur=dur_h/24; half=dur/2
    win = 3*dur if win_h is None else win_h/24   # local baseline: within +-win of center, outside +-dur
    n0=int(np.floor((t.min()-T0)/P))-1; n1=int(np.ceil((t.max()-T0)/P))+1
    deps=[];errs=[];allres=[];allin=[]
    for n in range(n0,n1+1):
        tc=T0+n*P; dt=t-tc
        sel=np.abs(dt)<win
        if not sel.any(): continue
        intr=np.abs(dt)<half; oot=sel&(np.abs(dt)>dur)
        if intr.sum()<1 or oot.sum()<4: continue
        # local linear baseline fit on OOT
        A=np.vstack([np.ones(oot.sum()),dt[oot]]).T
        c,*_=np.linalg.lstsq(A,f[oot],rcond=None)
        base=c[0]+c[1]*dt[intr]
        r=1-f[intr]/base
        allres.append(r); allin.append(e[intr])
        # also oot scatter
    r=np.concatenate(allres); ee=np.concatenate(allin)
    w=1/ee**2; dep=np.sum(w*r)/np.sum(w); err=1/np.sqrt(np.sum(w))
    return dep*1e6, err*1e6, len(allres), len(r)
# empirical scatter check: random epochs
def emp(P,dur_h,ntr=500,seed=1):
    rng=np.random.default_rng(seed); out=[]
    for i in range(ntr):
        out.append(boxdepth(P,rng.uniform(0,P)+t.min(),dur_h)[0])
    return np.array(out)
P=13.769448; T0=-1369.7546
for dur in [2.0,2.2,2.4]:
    dp,er,ne,npnt=boxdepth(P,T0,dur); print('cand dur',dur,'depth %.0f +- %.0f ppm  snr %.1f events %d pts %d'%(dp,er,dp/er,ne,npnt))
r=emp(P,2.2); r=r[np.abs(r)<5000]
print('random-phase depths: mean %.0f std %.0f -> emp snr %.1f'%(r.mean(),r.std(),boxdepth(P,T0,2.2)[0]/r.std()))
# per-quarter
# claim 2
Pe=13.76710058; T0e=174.81089-2167
print('K169e T0 BTJD',T0e)
dp,er,ne,npnt=boxdepth(Pe,T0e,2.9105); print('K169e fold depth %.0f +- %.0f ppm snr %.1f events %d'%(dp,er,dp/er,ne))
dp,er,ne,npnt=boxdepth(Pe,T0e,2.2); print('K169e fold (2.2h) depth %.0f +- %.0f'%(dp,er))
# separations over candidate events with data
seps=[]
n0=int(np.floor((t.min()-T0)/P))-1; n1=int(np.ceil((t.max()-T0)/P))+1
for n in range(n0,n1+1):
    tc=T0+n*P
    if not np.any(np.abs(t-tc)<1.1/24): continue
    k=np.round((tc-T0e)/Pe); s=abs(tc-(T0e+k*Pe))*24; seps.append((s,n,tc))
seps.sort(); print('n cand events with data',len(seps),'min sep h %.2f at n=%d tc=%.3f'%seps[0], 'threshold',(2.2+2.91)/2)
print('all events (no data req) min sep:',min(abs(T0+n*P-(T0e+np.round((T0+n*P-T0e)/Pe)*Pe))*24 for n in range(n0,n1+1)))
