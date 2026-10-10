import sys,json,glob; sys.path.insert(0,'/tmp/fast/pipeline')
import env, numpy as np, importlib, lcsearch as L
d02=importlib.import_module('02_download')
tic=int(sys.argv[1]); S=None
for f in glob.glob('/downloads/hits_ext_*.txt'):
    for t,s in json.load(open(f)):
        if t==tic: S=s
P,T0,dur=S['period'],S['t0'],S['duration_hr']/24
d02.download_star(tic)
lc,bad,_=L.reject_bad_sectors(L.load_star(tic)); c=L.bin_lc(L.clean(lc)); t,f,s=c['time'],c['flux'],c['sector']
def dep(m): return (round((1-f[m].mean())*1e6),round(f[m].std()/np.sqrt(m.sum())*1e6)) if m.sum()>5 else None
ph=((t-T0+P/2)%P)-P/2; it=np.abs(ph)<dur/2*0.9; n=np.round((t-T0)/P).astype(int)
ps=[dep(it&(s==x)) for x in np.unique(s)]; ps=[p for p in ps if p]
ph2=((t-T0)%P)-P/2
z=[(a/b) for a,b in ps]
print(tic,'P',round(P,4),'dur',round(dur*24,2),'all',dep(it),'odd',dep(it&(n%2==1)),'even',dep(it&(n%2==0)),'sec',dep(np.abs(ph2)<dur/2*0.9),'| sectors',len(ps),'depth range',min(p[0] for p in ps),max(p[0] for p in ps),'n_neg_sectors',sum(p[0]<0 for p in ps),'chi2/dof',round(np.sum([((p[0]-dep(it)[0])/p[1])**2 for p in ps])/max(len(ps)-1,1),1))
