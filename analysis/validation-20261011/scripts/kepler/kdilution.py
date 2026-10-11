import json, numpy as np
rows=json.load(open('/root/ph/work/kcrowd.json'))
gd=json.load(open('/root/ph/work/kdepth.json'))['target_psf_at_candidate'][1]
q=np.array([r['q'] for r in rows]); sap=np.array([r['sap'][1] for r in rows]); se=np.array([r['sap'][2] for r in rows])
fl=np.array([r['flfrcsap'] for r in rows]); ratio_flux=np.array([r['med_sap']/r['med_psf'] for r in rows]); crowd=np.array([r['crowdsap'] for r in rows])
pred_frac=fl/ratio_flux          # fraction of SAP-aperture flux that is the target's (from PSF-fit flux)
def fitalpha(x):                 # sap = alpha * gd * x
    w=1/se**2; a=np.sum(w*sap*gd*x)/np.sum(w*(gd*x)**2); chi=np.sum(((sap-a*gd*x)/se)**2); return a,chi
a1,c1=fitalpha(pred_frac); a2,c2=fitalpha(np.ones_like(sap)); a3,c3=fitalpha(crowd)
print('dilution from flux ratio: alpha=%.3f chi2=%.1f (dof %d)'%(a1,c1,len(sap)-1))
print('CROWDSAP model          : alpha=%.3f chi2=%.1f'%(a3,c3))
print('constant (no dilution)  : alpha=%.3f chi2=%.1f'%(a2,c2))
# contaminant-hosted hypothesis: signal is on extra flux in aperture; SAP depth ∝ (1 - target frac)
a4,c4=fitalpha(1-pred_frac); print('signal on contaminating flux: alpha=%.3f chi2=%.1f'%(a4,c4))
r=np.corrcoef(pred_frac,sap)[0,1]; print('corr(pred target frac, SAP depth)=%.2f'%r)
for i in np.argsort(pred_frac): print('Q%-2d target frac in SAP ap %.2f  SAP depth %5.0f+/-%4.0f  pred %5.0f'%(q[i],pred_frac[i],sap[i],se[i],a1*gd*pred_frac[i]))
json.dump(dict(alpha_dilution=a1,chi2_dilution=c1,chi2_crowdsap=c3,chi2_constant=c2,chi2_contaminant=c4,dof=len(sap)-1,corr=r,global_psf_depth=gd),open('/root/ph/work/kdilution.json','w'),indent=1)
