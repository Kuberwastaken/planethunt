import sys,json,glob; sys.path.insert(0,'/tmp/fast/pipeline')
import env, numpy as np, lcsearch as L
tic=int(sys.argv[1])
for f in glob.glob('/downloads/hits_ext_*.txt'):
    for t,s in json.load(open(f)):
        if t==tic: S=s
P,T0,dur=S['period'],S['t0'],S['duration_hr']/24
lc,bad,_=L.reject_bad_sectors(L.load_star(tic))
for w in (0.5,0.75,1.5,3.0):
    c=L.bin_lc(L.clean(lc,window=w)); t,f,s=c['time'],c['flux'],c['sector']
    ph=((t-T0+P/2)%P)-P/2; it=np.abs(ph)<dur/2*0.9; n=np.round((t-T0)/P).astype(int)
    d=(1-f[it].mean())*1e6; e=f[it].std()/np.sqrt(it.sum())*1e6
    # null: shift phase by random offsets
    rng=np.random.default_rng(0); nl=[]
    for _ in range(300):
        o=rng.uniform(0.15,0.85)*P; ph2=((t-T0-o+P/2)%P)-P/2; m=np.abs(ph2)<dur/2*0.9; nl.append((1-f[m].mean())*1e6)
    print('win',w,'depth',round(d),'+-',round(e),'null sd',round(np.std(nl)),'z',round(d/np.std(nl),1),'max null',round(max(nl)))
    if w==0.75:
        print('per-transit',[(int(k),round(float(t[it&(n==k)].mean())-0, 1),round((1-f[it&(n==k)].mean())*1e6),int((it&(n==k)).sum())) for k in np.unique(n[it]) if (it&(n==k)).sum()>3][:20])
