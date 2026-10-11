import sys, json, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
import triceratops.triceratops as tr
W='/root/ph/work/tri/'
bg=sys.argv[1]; N=int(float(sys.argv[2])); seed=int(sys.argv[3]) if len(sys.argv)>3 else 0
cc=sys.argv[4] if len(sys.argv)>4 and sys.argv[4]!='none' else None
np.random.seed(seed)
lc=np.load(W+'kepler_fold.npz'); t,f,err,P=lc['time'],lc['flux'],float(lc['err']),float(lc['P'])
m=np.abs(t)<0.25; t,f=t[m],f[m]
tic=pd.read_csv('/root/ph/planethunt/evidence/codex/catalogs/tickbonus2103792461826460288_tic_cone.csv')
r=tic[tic.ID==120686465].iloc[0]
oot=np.abs(t)>0.075; intr=np.abs(t)<0.03
depth=1-np.mean(f[intr])/np.mean(f[oot])
stars=pd.DataFrame([dict(ID=str(int(r.ID)),Tmag=r.Tmag,Jmag=r.Jmag,Hmag=r.Hmag,Kmag=r.Kmag,ra=r.ra,dec=r.dec,
     mass=r['mass'],rad=r['rad'],Teff=r.Teff,plx=r.plx,sep=0.0,PA=0.0,fluxratio=1.0,tdepth=depth)])
T=object.__new__(tr.target)
T.ID=int(r.ID); T.mission='Kepler'; T.search_radius=10; T.sectors=np.array([1]); T.stars=stars
T.trilegal_fname=W+bg; T.trilegal_url=None
T.calc_probs(time=t,flux_0=f,flux_err_0=err,P_orb=P,N=N,parallel=False,verbose=0,
             exptime=1765.464/86400,nsamples=20,contrast_curve_file=cc,filt=(sys.argv[5] if len(sys.argv)>5 else 'K') if cc else 'TESS')
pr=T.probs
print(pr[['ID','scenario','M_s','R_s','P_orb','b','R_p','prob']].to_string())
out=dict(bg=bg,N=N,seed=seed,contrast_curve=cc,depth_input=depth,flux_err=err,FPP=float(T.FPP),NFPP=float(T.NFPP),
         probs=pr[['scenario','prob']].assign(prob=lambda d:d.prob.astype(float)).to_dict('records'))
print('FPP %.4g NFPP %.4g'%(T.FPP,T.NFPP))
json.dump(out,open(W+'kepler_fpp_%s_N%d_s%d%s.json'%(bg.split('.')[0],N,seed,'_cc' if cc else ''),'w'),indent=1)
