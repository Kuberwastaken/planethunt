import sys, json, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
import triceratops.triceratops as tr
W='/root/ph/work/tri/'
lcf=sys.argv[1]; N=int(float(sys.argv[2])); seed=int(sys.argv[3]); cc=sys.argv[4] if len(sys.argv)>4 and sys.argv[4]!='none' else None
np.random.seed(seed)
lc=np.load(W+lcf); t,f,err,P,ex=lc['time'],lc['flux'],float(lc['err']),float(lc['P']),float(lc['exptime'])
oot=np.abs(t)>0.05; intr=np.abs(t)<0.015; depth=1-np.mean(f[intr])/np.mean(f[oot])
# TIC 309780779: Teff 5013 K, logg 4.685, R 0.685, M 0.83, d 74.94 pc, Tmag 10.0253 (targets_extended row)
import triceratops.funcs as F
def seq(xc,yc):
    x,y=F.mamajek_column(xc),F.mamajek_column(yc); k=np.isfinite(x)&np.isfinite(y); x,y=x[k],y[k]; o=np.argsort(x); return x[o],y[o]
dmod=5*np.log10(74.9398)-5
MJ=np.interp(5013,*seq('Teff','M_J')); JH=np.interp(5013,*seq('Teff','JH')); MK=np.interp(5013,*seq('Teff','M_Ks'))
stars=pd.DataFrame([dict(ID='309780779',Tmag=10.0253,Jmag=MJ+dmod,Hmag=MJ-JH+dmod,Kmag=MK+dmod,ra=126.209819412415,dec=-62.9034093638149,
     mass=0.83,rad=0.685377,Teff=5013.,plx=1000/74.9398,sep=0.,PA=0.,fluxratio=1-0.0162206013,tdepth=depth)])
T=object.__new__(tr.target); T.ID=309780779; T.mission='TESS'; T.search_radius=10; T.sectors=np.array([61]); T.stars=stars
T.trilegal_fname=W+'bg_tess_G20.csv'; T.trilegal_url=None
T.calc_probs(time=t,flux_0=f,flux_err_0=err,P_orb=P,N=N,parallel=False,verbose=0,exptime=ex/86400,nsamples=20,contrast_curve_file=cc,filt='Vis' if cc else 'TESS')
pr=T.probs; print(pr[['ID','scenario','M_s','R_s','P_orb','b','R_p','prob']].to_string()); print('FPP %.4g NFPP %.4g'%(T.FPP,T.NFPP))
json.dump(dict(lc=lcf,N=N,seed=seed,contrast_curve=cc,depth_input=depth,flux_err=err,FPP=float(T.FPP),NFPP=float(T.NFPP),
   probs=pr[['scenario','prob']].assign(prob=lambda d:d.prob.astype(float)).to_dict('records'),
   best=pr[['scenario','b','R_p','M_EB','R_EB']].astype({'b':float,'R_p':float}).to_dict('records') if 'M_EB' in pr else None),
   open(W+'tess_fpp_%s_N%d_s%d%s.json'%(lcf.split('.')[0],N,seed,'_cc' if cc else ''),'w'),indent=1,default=float)
