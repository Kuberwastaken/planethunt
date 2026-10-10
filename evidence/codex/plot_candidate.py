import os
os.environ['MPLBACKEND']='Agg'
from run_search import L,ROOT,subset
import matplotlib.pyplot as plt
import numpy as np,json,sys
if __name__=='__main__':
 tic=int(sys.argv[1]);mode=sys.argv[2];d=json.loads((ROOT/'results'/f'{tic}_{mode}.json').read_text());raw=dict(np.load(ROOT/'lightcurves'/f'{tic}.npz'))
 flat=L.clean(raw)
 fig,axs=plt.subplots(len(d['signals']),3,figsize=(14,4*len(d['signals'])),squeeze=False)
 for i,s in enumerate(d['signals']):
  p,t0,dur=s['period'],s['t0'],s['duration_hr']/24
  for j,(arr,title) in enumerate([(flat,'Detrended all seasons'),(flat,'Withheld season'),(raw,'Normalized flux (raw product)')]):
   mask=np.ones(len(arr['time']),bool)
   if j==1:mask=np.isin(arr['sector'],d['holdout_sectors'])
   t=arr['time'][mask];y=(arr['flux'][mask]-1)*1e6
   phase=((t-t0+.5*p)%p)-.5*p
   ax=axs[i,j];ax.scatter(phase*24,y,s=1,alpha=.1,c='#597b9e',rasterized=True)
   edges=np.linspace(-p/2,p/2,81);ix=np.digitize(phase,edges)-1
   xx=[];yy=[];ee=[]
   for k in range(80):
    a=y[ix==k]
    if len(a)>4:xx.append((edges[k]+edges[k+1])*12);yy.append(np.mean(a));ee.append(np.std(a)/np.sqrt(len(a)))
   ax.errorbar(xx,yy,yerr=ee,fmt='.',c='#c04435',ms=4)
   ax.axvline(-dur*12,c='k',lw=.7,ls='--');ax.axvline(dur*12,c='k',lw=.7,ls='--')
   ax.set(title=title,xlabel='Hours from predicted transit',ylabel='Flux deviation (ppm)')
   ax.set_ylim(np.nanpercentile(y,[1,99]));ax.grid(alpha=.2)
  axs[i,0].text(.03,.97,f"TIC {tic}, rank {i+1}\nP={p:.8f} d; box={s['duration_hr']:.2f} h",transform=axs[i,0].transAxes,va='top')
 fig.suptitle('Exploratory transit vetting — not a planet claim',fontsize=15);fig.tight_layout()
 out=ROOT/'figures';out.mkdir(exist_ok=True);fig.savefig(out/f'{tic}_{mode}.png',dpi=160)
