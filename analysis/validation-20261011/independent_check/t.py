import numpy as np, sys
d=np.load(sys.argv[1]); t=d['time']; f=d['flux']; e=d['flux_err']; s=d['sector']; ex=d['exptime']
m=np.isfinite(t)&np.isfinite(f)&np.isfinite(e); t,f,e,s,ex=t[m],f[m],e[m],s[m],ex[m]
print('sectors',{int(k):(int((s==k).sum()),float(np.median(ex[s==k]))) for k in np.unique(s)})
def depth(mask,P,T0,dur_h,win_h=None):
    tt,ff,ee=t[mask],f[mask],e[mask]; dur=dur_h; win=3*dur_h if win_h is None else win_h
    n0=int(np.floor((tt.min()-T0)/P))-1; n1=int(np.ceil((tt.max()-T0)/P))+1
    R=[];E=[];N=0;D=[]
    for n in range(n0,n1+1):
        dt=(tt-(T0+n*P))*24; sel=np.abs(dt)<win; intr=np.abs(dt)<dur/2; oot=sel&(np.abs(dt)>dur)
        if intr.sum()<2 or oot.sum()<6: continue
        c=np.polyfit(dt[oot],ff[oot],1); r=1-ff[intr]/np.polyval(c,dt[intr])
        R.append(r);E.append(ee[intr]);N+=1
    r=np.concatenate(R);ee=np.concatenate(E); w=1/ee**2
    return np.sum(w*r)/np.sum(w)*1e6, 1/np.sqrt(np.sum(w))*1e6, N
early=s<=38; late=s>=61
P0=8.7236; T00=1329.1456
# grid fit on early
best=None
for P in np.arange(8.7226,8.7246,0.00002):
  for T0 in np.arange(T00-0.03,T00+0.0301,0.0015):
    dp,er,N=depth(early,P,T0,1.0)
    if best is None or dp/er>best[0]: best=(dp/er,P,T0,dp,er,N)
print('early best snr %.1f P=%.5f T0=%.4f depth %.0f+-%.0f N=%d'%best)
_,P,T0,_,_,_=best
# refine finer
best2=None
for PP in np.arange(P-0.0001,P+0.0001,0.000005):
  for TT in np.arange(T0-0.003,T0+0.003,0.0003):
    dp,er,N=depth(early,PP,TT,1.0)
    if best2 is None or dp/er>best2[0]: best2=(dp/er,PP,TT,dp,er,N)
print('early refined snr %.1f P=%.6f T0=%.5f depth %.0f+-%.0f N=%d'%best2)
_,P,T0,_,_,_=best2
np.save('eph.npy',[P,T0])
print('late at frozen eph: depth %.0f +- %.0f N=%d'%depth(late,P,T0,1.0))
print('late phase 0.5: %.0f +- %.0f N=%d'%depth(late,P,T0+P/2,1.0))
print('all phase 0.5: %.0f +- %.0f N=%d'%depth(np.ones_like(early),P,T0+P/2,1.0))
print('early phase 0.5: %.0f +- %.0f N=%d'%depth(early,P,T0+P/2,1.0))
print('all at eph: %.0f +- %.0f N=%d'%depth(np.ones_like(early),P,T0,1.0))
# timing of late transits: fit local T for late data
for TT in [None]:
    pass
tl=t[late]; n0=int(np.ceil((tl.min()-T0)/P)); n1=int(np.floor((tl.max()-T0)/P))
for n in range(n0,n1+1):
    tc=T0+n*P
    if not np.any(np.abs(tl-tc)<0.5/24): continue
    print('late event n=%d pred %.4f'%(n,tc))
# fit late timing shift: scan dT jointly over all late events
res=[]
for dT in np.arange(-60,60.1,1)/1440:
    dp,er,N=depth(late,P,T0+dT,1.0); res.append((dT*1440,dp,er))
res=np.array(res); i=np.argmax(res[:,1]/res[:,2])
print('late timing offset best %.0f min, depth %.0f +- %.0f'%tuple(res[i]))
# parabola-ish uncertainty: where snr drops by 1
sn=res[:,1]/res[:,2]; ok=res[sn>sn[i]-1,0]; print('dT range (dsnr<1): %.0f..%.0f min'%(ok.min(),ok.max()))
