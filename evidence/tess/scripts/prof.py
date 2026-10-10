import sys,time; sys.path.insert(0,'/tmp/fast/pipeline')
import env, numpy as np, lcsearch as L
from astropy.timeseries import BoxLeastSquares
lc,_,_=L.reject_bad_sectors(L.load_star(370612437)); t0=time.time(); c=L.clean(lc); print('clean',round(time.time()-t0,1)); c=L.bin_lc(c)
t,y,dy=c['time'],c['flux'],c['flux_err']; base=t.max()-t.min(); print('n',len(t),'base',base)
for pmin,os_ in ((1.0,3),(1.0,1.5),(1.0,1.0)):
    P=L.period_grid(base,1.0,pmin=pmin,oversample=os_); D=L.duration_grid(1.0,pmax=P.max(),n=5)
    t0=time.time(); r=BoxLeastSquares(t,y,dy).power(P,D,objective='snr'); print(pmin,os_,len(P),round(time.time()-t0,1),flush=True)
