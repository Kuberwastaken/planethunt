import numpy as np, sys
exec(open('k.py').read().split('P=13.769448')[0])
P=13.769448; T0=-1369.7546
r=emp(P,2.2,ntr=1000); 
mad=1.4826*np.median(np.abs(r-np.median(r)))
print('random-phase robust std %.0f, median %.0f -> snr %.1f'%(mad,np.median(r),1958/mad))
best=None
for dT in np.arange(-0.04,0.0401,0.005):
  for dur in [1.5,1.8,2.0,2.2,2.5]:
    dp,er,_,_=boxdepth(P,T0+dT,dur)
    if best is None or dp/er>best[0]: best=(dp/er,dT*24*60,dur,dp,er)
print('best snr %.1f at dT=%.1f min dur=%.1f depth %.0f +- %.0f'%best)
# oot scatter based error: per-point residual std
dur=2.2/24
ph=((t-T0+P/2)%P)-P/2
oot=(np.abs(ph)>3*dur)
print('median flux_err ppm',np.median(e)*1e6)
# per-quarter
for qq in np.unique(q):
    pass
# fold & bin by 0.5h to see shape
for lo in np.arange(-4,4,0.5):
    s=(ph*24>=lo)&(ph*24<lo+0.5); print('%5.1f h  %7.0f ppm n=%d'%(lo,(1-np.median(f[s]))*1e6, s.sum()))
