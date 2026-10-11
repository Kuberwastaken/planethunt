import sys, json, numpy as np
sys.path.insert(0,'/root/ph/work/tess'); from common import *
from astropy.timeseries import BoxLeastSquares
t,f,e,s,x=load()
fl=flatten(t,f,s)
def run(tt,yy,ee,label,pmin=1.0,pmax=25.0):
    # 10-min bins to keep BLS tractable; durations bracket the reported 0.86 h
    b=BoxLeastSquares(tt,yy,ee)
    durs=np.array([0.5,0.75,0.864,1.0,1.5,2.0,3.0])/24
    base=np.ptp(tt); q=durs.min()
    freqs=np.arange(1/pmax,1/pmin,q/base/3)
    per=1/freqs[::-1]
    r=b.power(per,durs,objective='snr')
    pw=r.power; med=np.median(pw); mad=np.median(np.abs(pw-med))*1.4826
    sde=(pw-med)/mad
    i=np.argmax(pw)
    top=np.argsort(sde)[::-1]
    # top 5 distinct peaks
    peaks=[]
    for j in top:
        if all(abs(per[j]-p)/p>0.01 for p,_,_,_ in peaks): peaks.append((per[j],sde[j],r.depth[j]*1e6,r.duration[j]*24))
        if len(peaks)==5: break
    print(label,'N=%d'%len(tt))
    for p,sd,dp,du in peaks: print('   P=%.5f SDE=%.1f depth=%.0f ppm dur=%.2f h'%(p,sd,dp,du))
    return dict(label=label,peaks=[dict(P=float(p),SDE=float(sd),depth_ppm=float(dp),dur_h=float(du)) for p,sd,dp,du in peaks])
def binned(tt,yy,ee,w=10/1440):
    k=np.floor((tt-tt.min())/w).astype(int); u,inv,c=np.unique(k,return_inverse=True,return_counts=True)
    wt=1/ee**2; T=np.bincount(inv,tt*wt)/np.bincount(inv,wt); Y=np.bincount(inv,yy*wt)/np.bincount(inv,wt); E=1/np.sqrt(np.bincount(inv,wt))
    return T,Y,E
res=[]
what=sys.argv[1]
if what=='full':
    T,Y,E=binned(t,fl,e); res.append(run(T,Y,E,'full real'))
    T,Y,E=binned(t,2-fl,e); res.append(run(T,Y,E,'full inverted'))
elif what=='disc':
    m=s<=38
    T,Y,E=binned(t[m],fl[m],e[m]); res.append(run(T,Y,E,'discovery sectors <=38 real'))
    T,Y,E=binned(t[m],2-fl[m],e[m]); res.append(run(T,Y,E,'discovery sectors <=38 inverted'))
    m=s>=61
    T,Y,E=binned(t[m],fl[m],e[m]); res.append(run(T,Y,E,'late sectors >=61 real'))
json.dump(res,open('/root/ph/work/tess/bls_%s.json'%what,'w'),indent=1)
