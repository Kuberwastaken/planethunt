import json, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,'/root/ph/work/tess'); from common import load
B,O,SURF,INK,INK2,GRID='#2a78d6','#eb6834','#fcfcfb','#0b0b0b','#52514e','#e4e3df'
plt.rcParams.update({'figure.facecolor':SURF,'axes.facecolor':SURF,'axes.edgecolor':INK2,'axes.labelcolor':INK,'xtick.color':INK2,'ytick.color':INK2,
 'text.color':INK,'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.color':GRID,'grid.linewidth':0.6,'legend.frameon':False})
OUT='/root/ph/out/figures/'
# ---- Figure 1: KIC 5689121 dilution + centroid
rows=json.load(open('/root/ph/work/kcrowd.json')); D=json.load(open('/root/ph/work/kdepth.json')); dil=json.load(open('/root/ph/work/kdilution_pooled.json'))
gd=D['target_psf_at_candidate'][1]; sig=dil['per_event_sigma_ppm']
x=np.array([r['flfrcsap']/(r['med_sap']/r['med_psf']) for r in rows]); y=np.array([r['sap'][1] for r in rows]); ye=sig/np.sqrt([r['sap'][0] for r in rows]); q=[r['q'] for r in rows]
fig,ax=plt.subplots(1,2,figsize=(10,4.2))
a=ax[0]; xx=np.linspace(0.5,1.05,10)
a.plot(xx,dil['dilution_fluxratio']['alpha']*gd*xx,color=B,lw=2,label='Signal on target, diluted (p = 0.22)')
a.plot(xx,dil['on_contaminant']['alpha']*gd*(1-xx),color=O,lw=2,ls='--',label='Signal on extra aperture flux (p ≈ 1e-36)')
a.errorbar(x,y,ye,fmt='o',ms=6,color=INK,ecolor=INK2,elinewidth=1,capsize=0,label='Aperture (SAP) depth per quarter')
for xi,yi,qi in zip(x,y,q):
    if qi in (2,6,14,16,1): a.annotate('Q%d'%qi,(xi,yi),xytext=(5,4),textcoords='offset points',fontsize=8,color=INK2)
a.set_xlabel('Target share of aperture flux'); a.set_ylabel('Transit depth in aperture (ppm)'); a.set_title('KIC 5689121: aperture depth tracks dilution',loc='left',fontsize=11)
a.legend(fontsize=8,loc='upper left'); a.set_ylim(-200,4200)
C=json.load(open('/root/ph/work/kcentroid_tpf.json'))['per_quarter']
a=ax[1]
for i,r in enumerate(C):
    m=np.array(r['meas_mpix']); pt=np.array(r['pred_target']); pn=np.array(r['pred_neighbour'])
    a.plot(*pt,'o',color=B,ms=7,mfc='none',mew=1.6,label='Predicted: signal on target' if i==0 else None)
    a.plot(*pn,'s',color=O,ms=7,mfc='none',mew=1.6,label='Predicted: signal on KIC 5689116' if i==0 else None)
    a.errorbar(*m,xerr=r['err_mpix'][0],yerr=r['err_mpix'][1],fmt='o',color=INK,ms=4,ecolor=INK2,elinewidth=0.8,label='Measured (raw TPF centroid)' if i==0 else None)
a.axhline(0,color=INK2,lw=0.8); a.axvline(0,color=INK2,lw=0.8)
a.set_xlabel('In-transit column shift (millipixel)'); a.set_ylabel('In-transit row shift (millipixel)')
a.set_title('Centroid shifts point to the target',loc='left',fontsize=11); a.legend(fontsize=8,loc='lower right'); a.set_xlim(-1.2,3.0); a.set_ylim(-1.5,1.6)
fig.tight_layout(); fig.savefig(OUT+'kic5689121_dilution_centroid.png',dpi=150); plt.close(fig)
# ---- Figure 2: TIC 309780779 halves + phase scan
t,f,e,s,x_=load(); dsc=json.load(open('/root/ph/work/tess/tfit_free_disc.json')); P,T0=dsc['P'][0],dsc['T0'][0]
fig,ax=plt.subplots(1,2,figsize=(10,4.2))
a=ax[0]
for lab,sel,col,off in (('Years 1–4 (S1–38): fit + discovery',s<=38,B,0.0),('Years 5–7 (S61–90): frozen ephemeris',s>=61,O,-1000)):
    tt,ff=t[sel],f[sel]; n=np.round((tt-T0)/P); dt=tt-(T0+n*P); ph=[];fl=[]
    for k in np.unique(n[np.abs(dt)<0.25]):
        m=(n==k)&(np.abs(dt)<0.25); o=m&(np.abs(dt)>0.05)
        if o.sum()<10: continue
        c=np.polyfit(dt[o],ff[o],1); ph.append(dt[m]); fl.append(ff[m]/np.polyval(c,dt[m]))
    ph=np.concatenate(ph)*24; fl=(np.concatenate(fl)-1)*1e6
    bins=np.arange(-6,6.01,0.25); idx=np.digitize(ph,bins); cb=[];mb=[];eb=[]
    for i in range(1,len(bins)):
        v=fl[idx==i]
        if len(v)>5: cb.append((bins[i-1]+bins[i])/2); mb.append(v.mean()); eb.append(v.std()/np.sqrt(len(v)))
    a.errorbar(cb,np.array(mb)+off,eb,fmt='o',ms=4,color=col,ecolor=col,elinewidth=1,label=lab)
a.axvspan(-0.54,0.54,color=GRID,alpha=0.6,lw=0)
a.set_xlabel('Hours from predicted mid-transit'); a.set_ylabel('Relative flux (ppm, offset)'); a.legend(fontsize=8,loc='upper center',bbox_to_anchor=(0.5,-0.16),ncol=1); a.set_ylim(-1900,450)
a.set_title('TIC 309780779: the later half repeats on schedule',loc='left',fontsize=11)
S=np.load('/root/ph/work/tess/scan.npy'); sc=json.load(open('/root/ph/work/tess/scan.json'))
a=ax[1]; r=S[0]; a.plot(r[:,0],r[:,1]/r[:,2],color=B,lw=1.4,label='Box SNR at each phase (duration = T14)')
a.axhline(3,color=INK2,lw=0.8,ls=':'); a.axhline(-3,color=INK2,lw=0.8,ls=':')
a.plot([0.0],[sc['primary'][0]/sc['primary'][1]],'o',color=O,ms=8,label='Primary transit (SNR %.1f)'%(sc['primary'][0]/sc['primary'][1]))
a.axvline(0.5,color=INK2,lw=0.8); a.text(0.52,8.5,'phase 0.5:\n%.0f ± %.0f ppm'%(sc['scan_dur1']['depth_05'],sc['scan_dur1']['err_05']),fontsize=8,color=INK2)
a.set_xlim(-0.02,1.0); a.set_xlabel('Orbital phase'); a.set_ylabel('Dip significance (σ)'); a.legend(fontsize=8,loc='upper right')
a.set_title('No secondary eclipse at any phase',loc='left',fontsize=11)
fig.tight_layout(); fig.subplots_adjust(bottom=0.27); fig.savefig(OUT+'tic309780779_holdout_phase_scan.png',dpi=150); plt.close(fig)
print('ok')
