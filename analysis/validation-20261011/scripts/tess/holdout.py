import sys, json, numpy as np
sys.path.insert(0,'/root/ph/work/tess'); from common import *
d=json.load(open('/root/ph/work/tess/tfit_free_disc.json')); l=json.load(open('/root/ph/work/tess/tfit_free_late.json')); a=json.load(open('/root/ph/work/tess/tfit_rho_all.json'))
P,eP=d['P'][0],max(d['P'][1:]); T0,eT=d['T0'][0],max(d['T0'][1:])
Tl,eTl=l['T0'][0],max(l['T0'][1:])
N=np.round((Tl-T0)/P); pred=T0+N*P; spred=np.hypot(eT,N*eP)
out=dict(disc_P=P,disc_P_err=eP,disc_T0=T0,cycles=float(N),predicted_late_T0=pred,predicted_err_d=spred,measured_late_T0=Tl,measured_err_d=eTl,
         offset_min=(Tl-pred)*1440,offset_sigma=(Tl-pred)/np.hypot(spred,eTl),
         period_diff_sigma=(l['P'][0]-P)/np.hypot(eP,max(l['P'][1:])))
# depth in late sectors at the frozen discovery ephemeris
t,f,e,s,x=load(); m=s>=61; t,f,e=t[m],f[m],e[m]
dur=a['T14_h'][0]/24*0.8
n=np.round((t-T0)/P); dt=t-(T0+n*P); D=[];V=[]
for k in np.unique(n[np.abs(dt)<0.3]):
    s_=(n==k)&(np.abs(dt)<0.3); i=s_&(np.abs(dt)<dur/2); o=s_&(np.abs(dt)>0.05)
    if i.sum()<1 or o.sum()<10: continue
    c=np.polyfit(dt[o],f[o],1); r=f[o]-np.polyval(c,dt[o]); D.append(1-np.mean(f[i]/np.polyval(c,dt[i]))); V.append(np.var(r)/i.sum())
D=np.array(D); w=1/np.array(V); dep=np.sum(w*D)/np.sum(w); err=np.sqrt(1/np.sum(w))*np.sqrt(max(1,np.sum(w*(D-dep)**2)/(len(D)-1)))
out.update(late_depth_at_frozen_ephem_ppm=dep*1e6,late_depth_err_ppm=err*1e6,late_events=len(D),late_snr=dep/err,positive_event_fraction=float(np.mean(D>0)))
for k,v in out.items(): print(k,v)
json.dump(out,open('/root/ph/work/tess/holdout.json','w'),indent=1,default=float)
