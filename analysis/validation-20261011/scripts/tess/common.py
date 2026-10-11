import numpy as np, pandas as pd
F='/root/ph/planethunt/evidence/tess/lightcurves/309780779.npz'
P0=8.723607282476642; T00=1329.1455684886305
def load():
    d=np.load(F); t,f,e,s,x=d['time'],d['flux'],d['flux_err'],d['sector'],d['exptime']
    ok=np.isfinite(t)&np.isfinite(f)&np.isfinite(e)&(e>0); o=np.argsort(t[ok])
    return t[ok][o],f[ok][o],e[ok][o],s[ok][o],x[ok][o]
def flatten(t,f,s,window=0.75,mask=None):
    """time-windowed running median per sector; optional mask excludes points from the trend"""
    out=np.empty_like(f)
    for sec in np.unique(s):
        m=s==sec; ts=pd.to_datetime(t[m],unit='D'); y=pd.Series(np.where(mask[m],np.nan,f[m]) if mask is not None else f[m],index=ts)
        tr=y.rolling('%dmin'%int(window*1440),center=True,min_periods=5).median().interpolate(limit_direction='both').values
        out[m]=f[m]/tr
    return out
def intransit(t,P,T0,dur):
    return np.abs(((t-T0+P/2)%P)-P/2)<dur/2
