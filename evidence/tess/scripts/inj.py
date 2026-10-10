import sys,os,time,json; sys.path.insert(0,'/tmp/fast/pipeline')
import env, numpy as np, lcsearch as L
rng=np.random.default_rng(int(sys.argv[1])); budget=float(sys.argv[2]); t00=time.time()
tics=[370612437,344099041,366306106,72604026,241606913]
tics=[t for t in tics if os.path.exists(f'/tmp/r/data/lightcurves/{t}.npz')]
base={}
for t in tics:
    d=np.load(f'/tmp/r/data/lightcurves/{t}.npz'); l={k:d[k] for k in d.files}; l,_,_=L.reject_bad_sectors(l)
    sg,_=L.bls_search(L.bin_lc(L.clean(l)),1.0); base[t]=sg[0]['sde']; print('baseline',t,round(sg[0]['sde'],1),flush=True)
tics=[t for t in tics if base[t]<8.5]; print('quiet hosts',tics,flush=True)
while tics and time.time()-t00<budget:
    tic=int(rng.choice(tics)); lc=L.load_star(tic) if False else None
    import numpy as np2
    d=np.load(f'/tmp/r/data/lightcurves/{tic}.npz'); lc={k:d[k] for k in d.files}
    lc,_,_=L.reject_bad_sectors(lc)
    P=float(np.exp(rng.uniform(np.log(1.5),np.log(15)))); dep=float(rng.choice([150,250,400]))*1e-6; dur=0.06*(P/4)**(1/3)*1.0
    t0=lc['time'].min()+rng.uniform(0,P)
    ph=((lc['time']-t0+P/2)%P)-P/2; f=lc['flux'].copy(); f[np.abs(ph)<dur/2]*=1-dep; lc2=dict(lc); lc2['flux']=f
    c=L.bin_lc(L.clean(lc2)); sg,_=L.bls_search(c,1.0); s=sg[0]
    ok=abs(s['period']/P-1)<0.01 or abs(s['period']/P-2)<0.02 or abs(s['period']/P-0.5)<0.01
    print(json.dumps({'tic':tic,'P':round(P,3),'dep':dep*1e6,'found_P':round(s['period'],3),'sde':round(s['sde'],1),'snr':round(s['snr'],1),'ok_exact':abs(s['period']/P-1)<0.01}),flush=True)
