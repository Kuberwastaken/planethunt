import sys; sys.path.insert(0,'/tmp/r/pipeline')
import env, numpy as np, lcsearch as L
P,T0,dur=3.564921,None,1.44/24
lc,bad,_=L.reject_bad_sectors(L.load_star(370612437)); print('rejected',bad)
def prep(w): return L.bin_lc(L.clean(lc,window=w))
c=prep(L.DETREND_WINDOW_D); t,f,s=c['time'],c['flux'],c['sector']
# find T0 via fold scan
best=(0,0)
for t0 in np.linspace(0,P,400,endpoint=False):
    ph=((t-t0+P/2)%P)-P/2; m=np.abs(ph)<dur/2
    d=(1-f[m].mean())
    if m.sum()>20 and d>best[0]: best=(d,t0)
T0=best[1]; print('T0',T0,'depth ppm',best[0]*1e6)
def depth(mask):
    if mask.sum()<10: return np.nan,np.nan
    x=f[mask]; return (1-x.mean())*1e6, x.std()/np.sqrt(len(x))*1e6
ph=((t-T0+P/2)%P)-P/2; intr=np.abs(ph)<dur/2*0.9
n=np.round((t-T0)/P).astype(int)
print('all',depth(intr)); print('odd',depth(intr&(n%2==1))); print('even',depth(intr&(n%2==0)))
ph2=((t-T0)%P)-P/2; sec=np.abs(ph2)<dur/2*0.9; print('secondary@0.5',depth(sec))
for ss in np.unique(s): print('sector',int(ss),depth(intr&(s==ss)))
for w in (0.5,0.75,1.5,2.5):
    c=prep(w); t,f,s=c['time'],c['flux'],c['sector']; ph=((t-T0+P/2)%P)-P/2; intr=np.abs(ph)<dur/2*0.9; print('window',w,depth(intr))
