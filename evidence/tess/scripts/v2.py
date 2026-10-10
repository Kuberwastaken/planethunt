import sys,json; sys.path.insert(0,'/tmp/fast/pipeline')
import env, numpy as np, pandas as pd, importlib, lcsearch as L
d02=importlib.import_module('02_download')
tic=int(sys.argv[1]); P=float(sys.argv[2]); T0=float(sys.argv[3]); dur=float(sys.argv[4])/24
print(d02.download_star(tic))
lc,bad,_=L.reject_bad_sectors(L.load_star(tic)); c=L.bin_lc(L.clean(lc)); t,f,s=c['time'],c['flux'],c['sector']
def dep(m):
    return (round((1-f[m].mean())*1e6),round(f[m].std()/np.sqrt(max(m.sum(),1))*1e6)) if m.sum()>5 else None
ph=((t-T0+P/2)%P)-P/2; it=np.abs(ph)<dur/2*0.9; n=np.round((t-T0)/P).astype(int)
print('sectors',sorted(set(s.astype(int))),'rej',bad)
print('all',dep(it),'odd',dep(it&(n%2==1)),'even',dep(it&(n%2==0)))
ph2=((t-T0)%P)-P/2; print('secondary',dep(np.abs(ph2)<dur/2*0.9))
# per-sector depth
print('per-sector',[(int(x),dep(it&(s==x))) for x in np.unique(s)])
# per-transit depths
tr=[(int(k),dep(it&(n==k))) for k in np.unique(n[it])]; print('n_transits',len(tr),tr[:12])
for w in (0.5,1.5):
    c2=L.bin_lc(L.clean(lc,window=w)); tt,ff=c2['time'],c2['flux']; p=((tt-T0+P/2)%P)-P/2; m=np.abs(p)<dur/2*0.9; print('win',w,round((1-ff[m].mean())*1e6))
