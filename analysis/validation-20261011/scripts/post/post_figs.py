import json, numpy as np, pandas as pd, batman, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, Polygon
from astropy.wcs import WCS
OUT='/root/ph/post/out/'; import os; os.makedirs(OUT,exist_ok=True); os.makedirs(OUT+'data',exist_ok=True)
SURF,SURF2,INK,INK2,INK3,GRID='#1a1a19','#232322','#f0efec','#c3c2b7','#8f8e86','#33332f'
BLUE,ORANGE='#3987e5','#d95926'
plt.rcParams.update({'figure.facecolor':SURF,'axes.facecolor':SURF,'savefig.facecolor':SURF,'axes.edgecolor':INK3,'axes.labelcolor':INK2,
 'xtick.color':INK3,'ytick.color':INK3,'text.color':INK,'font.size':11,'axes.spines.top':False,'axes.spines.right':False,
 'axes.grid':True,'grid.color':GRID,'grid.linewidth':0.6,'legend.frameon':False,'font.family':'DejaVu Sans'})
fit=json.load(open('/root/ph/work/kfit_psf.json')); P=fit['P'][0]; T0=fit['T0_btjd'][0]
k,b,lar=fit['k'][0],fit['b'][0],fit['ln_aR'][0]; aR=np.exp(lar)
def title(fig,t,sub):
    fig.text(0.035,0.955,t,fontsize=20,weight='bold',color=INK,va='top')
    fig.text(0.035,0.905,sub,fontsize=12,color=INK2,va='top')
def foot(fig,s='KIC 5689121 · Kepler Bonus PSF photometry (Martínez-Palomera et al.) · planet CANDIDATE, not confirmed'):
    fig.text(0.035,0.012,s,fontsize=9,color=INK3)
# ------------------------------------------------------------------ data
D=np.load('/root/ph/rel/kx/planet-search/database_expansion/kbonus_independent_audit/2103792461826460288_correct_errors.npz')
t,f,e,q=D['time'],D['flux'],D['flux_err'],D['sector']; ok=np.isfinite(t)&np.isfinite(f); t,f,e,q=t[ok],f[ok],e[ok],q[ok]
n=np.round((t-T0)/P); dt=t-(T0+n*P); intr=np.abs(dt)<0.08
# detrend for display: running median 1.0 d per quarter, transits masked
fd=np.empty_like(f)
for qq in np.unique(q):
    m=q==qq; s=pd.Series(np.where(intr[m],np.nan,f[m]),index=pd.to_datetime(t[m],unit='D'))
    tr=s.rolling('1D',center=True,min_periods=10).median().interpolate(limit_direction='both').values; fd[m]=f[m]/tr
BJD=t+2457000.
pd.DataFrame(dict(time_btjd=t,time_bjd_tdb=BJD,flux_psf_norm=f,flux_err=e,flux_detrended=fd,quarter=q,in_transit=intr)).to_csv(OUT+'data/kic5689121_lightcurve_psf.csv',index=False,float_format='%.7f')
epochs=np.unique(n[(np.abs(dt)<0.3)]); tt=T0+epochs*P
# ------------------------------------------------------------------ FIG 2: light curve
fig=plt.figure(figsize=(14,8.2)); title(fig,'Four years of starlight from one faint red dwarf','Kepler, 2009–2013. Every 13.77 days the star dims by about 0.2% for two hours.')
ax=fig.add_axes([0.06,0.52,0.92,0.32])
bw=6/24; bi=np.floor((t-t.min())/bw); u,inv=np.unique(bi,return_inverse=True); c=np.bincount(inv)
tb=np.bincount(inv,t)/c; fb=np.bincount(inv,fd)/c; keep=c>=6
ax.plot(tb[keep]+2457000-2450000,(fb[keep]-1)*1e3,'.',ms=2.2,color=INK3,alpha=0.8,label='6-hour averages')
ax.plot(t[intr]+2457000-2450000,(fd[intr]-1)*1e3,'.',ms=3,color=ORANGE,alpha=0.9,label='Points inside a predicted transit')
ax.set_ylim(-6,3); ax.set_xlim(4950,6430); ax.set_ylabel('Brightness change (parts per thousand)'); ax.set_xlabel('Date (BJD − 2,450,000)')
ax.plot(tt+2457000-2450000,np.full(len(tt),2.6),'v',ms=5,color=ORANGE,label='Predicted transit times')
ax.legend(loc='lower right',fontsize=9,markerscale=2,ncol=3)
# six individual transits
ev=[e_ for e_ in epochs if ((n==e_)&(np.abs(dt)<0.3)).sum()>15]
pick=[ev[int(i)] for i in np.linspace(3,len(ev)-4,6)]
for j,e_ in enumerate(pick):
    a=fig.add_axes([0.06+j*0.155,0.11,0.135,0.27]); m=(n==e_)&(np.abs(dt)<0.3)
    a.plot(dt[m]*24,(fd[m]-1)*1e3,'o',ms=3.2,color=BLUE)
    a.axvspan(-1.1,1.1,color=SURF2,zorder=0); a.set_ylim(-5.5,3); a.set_xlim(-7,7)
    a.set_title('Transit %d · %s'%(int(e_)+int(-epochs.min())+1,'Q%d'%q[m][0]),fontsize=9,color=INK2)
    a.set_xlabel('hours',fontsize=9)
    if j==0: a.set_ylabel('ppt',fontsize=9)
    else: a.set_yticklabels([])
fig.text(0.06,0.43,'Single transits are barely above the noise — the signal only becomes clear when all 70 are stacked.',fontsize=10.5,color=INK2)
foot(fig); fig.savefig(OUT+'post_02_lightcurve.png',dpi=150); plt.close(fig)
# ------------------------------------------------------------------ FIG 3: folded dip
ph=dt[np.abs(dt)<0.35]; fl=fd[np.abs(dt)<0.35]
edges=np.arange(-0.35,0.3501,15/1440); idx=np.digitize(ph,edges); rows=[]
for i in range(1,len(edges)):
    v=fl[idx==i]
    if len(v)>10: rows.append(((edges[i-1]+edges[i])/2*24,(v.mean()-1)*1e6,v.std(ddof=1)/np.sqrt(len(v))*1e6,len(v)))
B=pd.DataFrame(rows,columns=['hours_from_mid','flux_ppm','err_ppm','n_points']); B.to_csv(OUT+'data/kic5689121_folded_15min_bins.csv',index=False,float_format='%.3f')
pm=batman.TransitParams(); pm.t0=0; pm.per=P; pm.rp=k; pm.a=aR; pm.inc=np.degrees(np.arccos(b/aR)); pm.ecc=0; pm.w=90; pm.u=[0.45,0.25]; pm.limb_dark='quadratic'
xm=np.linspace(-0.35,0.35,1500); mm=batman.TransitModel(pm,xm,supersample_factor=15,exp_time=1765.464/86400).light_curve(pm)
pd.DataFrame(dict(hours_from_mid=xm*24,model_ppm=(mm-1)*1e6)).to_csv(OUT+'data/kic5689121_transit_model.csv',index=False,float_format='%.3f')
depth_model=(1-mm.min())*1e6
fig=plt.figure(figsize=(14,8.2)); title(fig,'Stack all 70 transits and the dip is unmistakable','Kepler light folded on the 13.769-day period. Grey: every measurement. Blue: 15-minute averages. Orange: transit model.')
ax=fig.add_axes([0.06,0.12,0.60,0.70])
ax.plot(ph*24,(fl-1)*1e6,'.',ms=2,color=INK3,alpha=0.35,zorder=1)
ax.errorbar(B.hours_from_mid,B.flux_ppm,B.err_ppm,fmt='o',ms=6,color=BLUE,ecolor=BLUE,elinewidth=1.2,zorder=3,label='15-min averages')
ax.plot(xm*24,(mm-1)*1e6,color=ORANGE,lw=2.2,zorder=4,label='Transit model (MCMC median)')
ax.set_ylim(-4200,2600); ax.set_xlim(-8.4,8.4); ax.set_xlabel('Hours from mid-transit'); ax.set_ylabel('Brightness change (ppm)')
ax.legend(loc='upper left',fontsize=10)
ax.annotate('',xy=(3.4,0),xytext=(3.4,-depth_model),arrowprops=dict(arrowstyle='<->',color=INK2,lw=1.2))
ax.text(3.7,-depth_model/2,'model: %.1f ppt deep\n(%.2f%% of the light)'%(depth_model/1e3,depth_model/1e4),fontsize=11,color=INK,va='center')
cards=[('Period','13.76945 ± 0.00007 d'),('Duration','≈ 2.1–2.4 h'),('Depth','≈ 2,000–2,400 ppm (method-dependent)'),('Transits','70 over 3.9 years'),
       ('Significance','13.7σ (aperture) · 26.7 BLS SNR'),('Held-out quarters','still there: 5.8σ in the last 4'),
       ('Host star','M dwarf, 0.51 R☉, ~300 pc, Kp 16.3'),('Size if real','≈ 2.5–3 Earth radii')]
y0=0.80
for i,(kk,vv) in enumerate(cards):
    fig.text(0.70,y0-i*0.083,kk.upper(),fontsize=9,color=INK3,weight='bold'); fig.text(0.70,y0-i*0.083-0.032,vv,fontsize=13,color=INK)
foot(fig); fig.savefig(OUT+'post_03_folded_dip.png',dpi=150); plt.close(fig)
print('depth_model',depth_model,'k',k,'b',b,'aR',aR)
