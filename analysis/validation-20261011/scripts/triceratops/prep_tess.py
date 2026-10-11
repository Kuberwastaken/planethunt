import sys, json, numpy as np, pandas as pd
from math import pi
import triceratops.funcs as F
sys.path.insert(0,'/root/ph/work/tess'); from common import load
W='/root/ph/work/tri/'
fit=json.load(open('/root/ph/work/tess/tfit_free_all.json')); P=fit['P'][0]; T0=fit['T0'][0]
t,f,e,s,x=load()
def fold(sel):
    tt,ff=t[sel],f[sel]; n=np.round((tt-T0)/P); dt=tt-(T0+n*P); ph=[];fl=[]
    for k in np.unique(n[np.abs(dt)<0.25]):
        m=(n==k)&(np.abs(dt)<0.25); o=m&(np.abs(dt)>0.05)
        if o.sum()<10 or (m&(np.abs(dt)<0.015)).sum()<1: continue
        c=np.polyfit(dt[o],ff[o],1); ph.append(dt[m]); fl.append(ff[m]/np.polyval(c,dt[m]))
    ph=np.concatenate(ph); fl=np.concatenate(fl); o=np.argsort(ph); ph,fl=ph[o],fl[o]
    return ph,fl,float(np.std(fl[np.abs(ph)>0.05]))
for lab,sel,ex in (('200s',x==200,200.),('600s',x==600,600.)):
    ph,fl,er=fold(sel); np.savez(W+'tess_fold_%s.npz'%lab,time=ph,flux=fl,err=er,P=P,exptime=ex); print(lab,len(ph),'rms %.0f ppm'%(er*1e6))
# all data averaged into 30-min bins on the folded grid (conservative single-exptime input)
ph,fl,er=fold(np.ones_like(t,bool)); b=np.round(ph/(1800/86400)); u,inv=np.unique(b,return_inverse=True)
pb=np.bincount(inv,ph)/np.bincount(inv); fb=np.bincount(inv,fl)/np.bincount(inv)
# per-point error of the binned series from its out-of-transit scatter
eb=float(np.std(fb[np.abs(pb)>0.05]))
np.savez(W+'tess_fold_all30.npz',time=pb,flux=fb,err=eb,P=P,exptime=1800.)
print('all->30min phase bins',len(pb),'rms %.0f ppm'%(eb*1e6))
# background population from the 90" neighbour list (G<~20.1); BP-RP from inverting the Stassun G-T relation
d=json.load(open('/root/ph/planethunt/evidence/tess/pixels/309780779_pixels.json'))
nb=pd.DataFrame(d['neighbours_tested'])
nb=nb.drop_duplicates(['sep_arcsec','G'])
grid=np.linspace(-0.5,4.5,5001)
GT=lambda c: 0.00522555*c**3-0.0891337*c**2+0.633923*c-0.0324473   # G-T(BP-RP) (Stassun+19)
gtg=GT(grid); o=np.argsort(gtg)
bprp=np.interp(nb.G-nb.Tmag,gtg[o],grid[o])
BP=nb.G+0.5*bprp; RP=nb.G-0.5*bprp  # only the difference matters downstream; recipe recomputes Tmag from these
area=pi*(90/3600)**2
def characterise(G,BP,RP):
    Tmag=F.gaia_to_Tmag(G,BP,RP)
    def seq(xc,yc):
        x,y=F.mamajek_column(xc),F.mamajek_column(yc); k=np.isfinite(x)&np.isfinite(y); x,y=x[k],y[k]; o=np.argsort(x); x,y=x[o],y[o]
        k=np.concatenate(([True],np.diff(x)>1e-9)); return x[k],y[k]
    cx,cy=seq('BpRp','Teff'); Teff=np.interp(BP-RP,cx,cy,left=cy[0],right=cy[-1]); o={}
    for nm,col in (('mass','Msun'),('rad','R_Rsun'),('MG','M_G'),('MJ','M_J'),('MKs','M_Ks'),('JH','JH')):
        xx,yy=seq('Teff',col); o[nm]=np.interp(Teff,xx,yy)
    logg=np.log10(F.G*(o['mass']*F.Msun)/(o['rad']*F.Rsun)**2); dmod=G-o['MG']
    return pd.DataFrame(dict(Mact=o['mass'],logg=logg,logTe=np.log10(Teff),**{'[M/H]':np.zeros(len(G))},TESS=Tmag,J=o['MJ']+dmod,H=o['MJ']-o['JH']+dmod,Ks=o['MKs']+dmod))
pop=characterise(nb.G.values,BP.values,RP.values)
rng=np.random.default_rng(1); Nf=int(round(len(pop)*0.1/area))
pop.iloc[rng.integers(0,len(pop),Nf)].to_csv(W+'bg_tess_G20.csv',index=False)
print('TESS background: %d stars in 90" cone (incl. target) -> %d in 0.1 deg2; Tmag recomputed vs given: max |dT| %.3f'%(len(pop),Nf,np.max(np.abs(pop.TESS.values-nb.Tmag.values))))
# combined 600-s-equivalent series: native 600-s cadences + 200-s cadences averaged in 600-s time bins
m2=x==200; tb=np.floor((t[m2]-t[m2].min())/(600/86400)); u,inv,cnt=np.unique(tb,return_inverse=True,return_counts=True)
t2=np.bincount(inv,t[m2])/cnt; f2=np.bincount(inv,f[m2])/cnt; ok=cnt==3
t6=np.concatenate([t[x==600],t2[ok]]); f6=np.concatenate([f[x==600],f2[ok]])
o=np.argsort(t6); t,f=t6[o],f6[o]
ph,fl,er=fold(np.ones_like(t,bool)); np.savez(W+'tess_fold_600eq.npz',time=ph,flux=fl,err=er,P=P,exptime=600.)
print('600-s-equivalent series: %d pts, rms %.0f ppm'%(len(ph),er*1e6))
