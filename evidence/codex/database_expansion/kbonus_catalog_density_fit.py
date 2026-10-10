"""Supplemental fixed catalog-density shape check; discovery quarters only."""
import json
import numpy as np
from scipy.optimize import least_squares
import batman
import audit_kbonus_candidate as A
M=.5446;R=.5553;ars=(6.67430e-11*M*1.98847e30*(A.P*86400)**2/(4*np.pi**2))**(1/3)/(R*6.957e8)
raw=A.load_column('FLUX','FLUX_ERR');reports=[]
for degree in (1,2):
 d=A.prepare(raw,degree=degree);d=A.sub(d,~np.isin(d['sector'],A.H));pr=A.profile(d)
 for ld in ([.5,.2],[.3,.2]):
  pars=batman.TransitParams();pars.t0=0;pars.per=A.P;pars.rp=.047;pars.a=ars;pars.inc=89;pars.ecc=0;pars.w=90;pars.u=ld;pars.limb_dark='quadratic'
  model=batman.TransitModel(pars,d['time'],supersample_factor=15,exp_time=np.median(d['exptime'])/86400)
  def compute(th):
   k,b,shift,offset=th;pars.rp=k;pars.inc=np.degrees(np.arccos(b/ars));pars.t0=shift
   f=(model.light_curve(pars)-1)*1e6+offset
   return np.bincount(pr['bin'],pr['weight']*f,minlength=len(pr['centers']))/pr['sumw']
  sols=[]
  for b in (.1,.5,.85):
   sol=least_squares(lambda th:(compute(th)-pr['flux'])/pr['error'],[.047,b,0,0],bounds=([.002,0,-A.D,-500],[.3,1.2,A.D,500]),max_nfev=500,diff_step=1e-4);sols.append(sol)
  sol=min(sols,key=lambda s:np.sum(s.fun**2));k,b,shift,off=sol.x
  duration=A.P/np.pi*np.arcsin(np.sqrt(max(0,(1+k)**2-b*b))/np.sqrt(ars*ars-b*b))*24
  reports.append({'baseline_degree':degree,'fixed_limb_darkening':ld,'chi2_diagonal_bins':float(np.sum(sol.fun**2)),'n_bins':len(pr['centers']),'radius_ratio':float(k),'impact_parameter':float(b),'epoch_shift_days':float(shift),'offset_ppm':float(off),'duration_contact_hours':float(duration),'illustrative_undiluted_planet_radius_Earth':float(k*R*109.076)})
out={'mass_solar':M,'radius_solar':R,'stellar_parameter_source':'GaiaDR3 values independently retrieved by catalog agent; parent holds source response. Values have uncertainty not propagated here.','a_over_rstar':float(ars),'density_solar':M/R**3,'fit_scope':'Discovery quarters only; approximate fixed limb darkening; no dilution. Diagonal phase-bin residuals descriptive, not validation odds.','fits':reports}
(A.OUT/'catalog_density_shape.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
