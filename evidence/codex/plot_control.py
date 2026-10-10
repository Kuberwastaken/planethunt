from run_search import ROOT,L
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=json.loads((ROOT/'positive_control.json').read_text());s=p['signals'][0]
z=dict(np.load(ROOT/'lightcurves/410153553.npz'));d=L.clean(z)
fig,axs=plt.subplots(1,2,figsize=(10,4))
for ax,hold,title in zip(axs,[False,True],['Discovery observations','Withheld observations']):
 m=np.isin(d['sector'],p['holdout_sectors']);m=m if hold else ~m
 t=d['time'][m];y=(d['flux'][m]-1)*1e6
 ph=((t-s['t0']+.5*s['period'])%s['period'])-.5*s['period']
 edges=np.linspace(-.09,.09,81);ix=np.digitize(ph,edges)-1;xx=[];yy=[];ee=[]
 for k in range(len(edges)-1):
  a=y[ix==k]
  if len(a)>2:xx.append((edges[k]+edges[k+1])*12);yy.append(a.mean());ee.append(a.std()/np.sqrt(len(a)))
 ax.errorbar(xx,yy,yerr=ee,fmt='.',color='#245980',ms=5)
 ax.set(title=title,xlabel='Hours from transit center',ylabel='Relative flux (ppm)',ylim=(-6000,1500));ax.axhline(0,color='#999',lw=.6);ax.grid(alpha=.15)
fig.suptitle(f"Known-planet control: LHS 3844 b\nRecovered period {s['period']:.7f} days — NOT a new discovery",fontsize=13)
fig.tight_layout();(ROOT/'figures').mkdir(exist_ok=True);fig.savefig(ROOT/'figures/known_planet_control.png',dpi=170)
