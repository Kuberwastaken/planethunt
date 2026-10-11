import json, glob, numpy as np
from astropy.io import fits
rows=json.load(open('/root/ph/work/kcentroid_raw.json')); crowd={r['q']:r for r in json.load(open('/root/ph/work/kcrowd.json'))}
orig={}
for f in glob.glob('/root/ph/rel/kx/planet-search/database_expansion/kbonus/pixels/kplr005689116-*_lpd-targ.fits.gz'):
    h=fits.open(f); orig[h[0].header['QUARTER']]=(h[2].header['CRVAL1P'],h[2].header['CRVAL2P'])
chi={'zero':0.,'target':0.,'neighbour':0.}; dof=0; out=[]
for r in rows:
    q=r['q']; c0,r0=orig[q]
    xt=np.array([c0+r['tgt_pix'][0],r0+r['tgt_pix'][1]]); xn=np.array([c0+r['nb_pix'][0],r0+r['nb_pix'][1]])
    c=np.array([r['cen_col'],r['cen_row']]); d=crowd[q]['sap'][1]*1e-6
    meas=np.array([r['dcol'],r['drow']]); err=np.array([r['dcol_e'],r['drow_e']])
    err=np.maximum(err,1e-5)
    pred={'zero':np.zeros(2),'target':-d*(xt-c),'neighbour':-d*(xn-c)}
    for k in chi: chi[k]+=np.sum(((meas-pred[k])/err)**2)
    dof+=2
    out.append(dict(q=q,meas_mpix=(meas*1e3).round(3).tolist(),err_mpix=(err*1e3).round(3).tolist(),pred_target_mpix=(pred['target']*1e3).round(3).tolist(),pred_neighbour_mpix=(pred['neighbour']*1e3).round(3).tolist(),sep_t=float(np.hypot(*(xt-c))),sep_n=float(np.hypot(*(xn-c)))))
    print('Q%-2d meas %s ±%s  pred(target) %s  pred(neighbour) %s  [mpix]'%(q,out[-1]['meas_mpix'],out[-1]['err_mpix'],out[-1]['pred_target_mpix'],out[-1]['pred_neighbour_mpix']))
from scipy.stats import chi2 as C
for k,v in chi.items(): print('%-9s chi2 %.1f / %d  p=%.3g'%(k,v,dof,C.sf(v,dof)))
print('Delta chi2 neighbour - target = %.1f'%(chi['neighbour']-chi['target']))
json.dump(dict(per_quarter=out,chi2=chi,dof=dof),open('/root/ph/work/kcentroid.json','w'),indent=1)
