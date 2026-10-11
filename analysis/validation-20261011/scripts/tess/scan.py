"""Fixed-ephemeris diagnostics for TIC 309780779: odd/even, per-era depth, all-phase secondary scan,
phase-shift null distribution (empirical FAP of the primary depth at this star)."""
import sys, json, numpy as np
sys.path.insert(0,'/root/ph/work/tess'); from common import *
fit=json.load(open('/root/ph/work/tess/tfit_free_all.json'))
P=fit['P'][0]; T0=fit['T0'][0]; T14=fit['T14_h'][0]/24
t,f,e,s,x=load()
def box(tc_phase,dur,sel=None,W=0.3):
    """mean depth at phase offset tc_phase (days) using per-event linear baselines; returns depth, err(empirical), n"""
    tt=t if sel is None else t[sel]; ff=f if sel is None else f[sel]; ee=e if sel is None else e[sel]
    T=T0+tc_phase; n=np.round((tt-T)/P); dt=tt-(T+n*P); m=np.abs(dt)<W
    tt,ff,ee,n,dt=tt[m],ff[m],ee[m],n[m],dt[m]
    D=[];V=[]
    for k in np.unique(n):
        s_=n==k; i=s_&(np.abs(dt)<dur/2); o=s_&(np.abs(dt)>dur/2+0.02)
        if i.sum()<1 or o.sum()<10: continue
        c=np.polyfit(dt[o],ff[o],1); r=ff[o]-np.polyval(c,dt[o]); base=np.polyval(c,dt[i])
        w=1/ee[i]**2; D.append(1-np.sum(w*ff[i]/base)/np.sum(w)); V.append(np.std(r)**2/i.sum())
    D=np.array(D); V=np.array(V); w=1/V
    d=np.sum(w*D)/np.sum(w); err=np.sqrt(1/np.sum(w))
    chi=np.sum(w*(D-d)**2)/(len(D)-1) if len(D)>1 else 1
    return d*1e6, err*1e6*np.sqrt(max(chi,1)), len(D)
out={}
d,er,nn=box(0,T14*0.8); out['primary']=(d,er,nn); print('primary depth %.0f±%.0f ppm (%d ev, %.1f sigma)'%(d,er,nn,d/er))
n_all=np.round((t-T0)/P)
for lab,sel in (('odd',n_all%2==1),('even',n_all%2==0)):
    out[lab]=box(0,T14*0.8,sel); print(lab,'%.0f±%.0f (%d)'%out[lab])
oe=abs(out['odd'][0]-out['even'][0])/np.hypot(out['odd'][1],out['even'][1]); out['odd_even_sigma']=oe; print('odd/even %.2f sigma'%oe)
for lab,sel in (('yr1-3 (1800s, S1-11)',s<=11),('yr3-4 (600s, S28-38)',(s>=28)&(s<=38)),('yr5-7 (200s, S61-90)',s>=61)):
    out[lab]=box(0,T14*0.8,sel); print(lab,'%.0f±%.0f (%d)'%out[lab])
# secondary / all-phase scan, durations T14 and 2*T14
ph=np.arange(0.03,0.971,0.0025); scan={}
for durf in (1.0,2.0):
    rows=[]
    for p in ph:
        d,er,nn=box(p*P,T14*durf); rows.append((p,d,er))
    rows=np.array(rows); snr=rows[:,1]/rows[:,2]; scan[durf]=rows
    j=np.argmax(snr); k=np.argmin(np.abs(rows[:,0]-0.5))
    print('dur x%.0f: max SNR %.2f at phase %.4f (depth %.0f±%.0f); phase 0.5 depth %.0f±%.0f; |SNR|>3 bins: %d of %d'%(durf,snr[j],rows[j,0],rows[j,1],rows[j,2],rows[k,1],rows[k,2],np.sum(np.abs(snr)>3),len(snr)))
    out['scan_dur%.0f'%durf]=dict(max_snr=float(snr[j]),phase_max=float(rows[j,0]),depth_at_max=float(rows[j,1]),depth_05=float(rows[k,1]),err_05=float(rows[k,2]),
        n_abs_snr_gt3=int(np.sum(np.abs(snr)>3)),n=int(len(snr)),snr_std=float(np.std(snr)),min_snr=float(snr.min()))
# phase-shift null for the primary: how often does a random phase give a dip as significant as the transit?
p_snr=out['primary'][0]/out['primary'][1]
s1=scan[1.0]; snr1=s1[:,1]/s1[:,2]
out['phase_null']=dict(primary_snr=p_snr,max_null_snr=float(snr1.max()),n_ge_primary=int(np.sum(snr1>=p_snr)),n=int(len(snr1)))
print('phase-shift null: primary SNR %.1f vs max off-phase SNR %.2f (std %.2f)'%(p_snr,snr1.max(),snr1.std()))
np.save('/root/ph/work/tess/scan.npy',np.array([scan[1.0],scan[2.0]]))
json.dump(out,open('/root/ph/work/tess/scan.json','w'),indent=1,default=float)
