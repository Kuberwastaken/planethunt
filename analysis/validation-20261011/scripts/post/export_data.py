import json, numpy as np, pandas as pd
O='/root/ph/post/out/data/'
fit=json.load(open('/root/ph/work/kfit_psf.json')); P=fit['P'][0]; T0=fit['T0_btjd'][0]
D=np.load('/root/ph/rel/kx/planet-search/database_expansion/kbonus_independent_audit/2103792461826460288_correct_errors.npz')
t,f,q=D['time'],D['flux'],D['sector']; ok=np.isfinite(t)&np.isfinite(f); t,f,q=t[ok],f[ok],q[ok]
n=np.round((t-T0)/P); dt=t-(T0+n*P); rows=[]
for k in np.unique(n[np.abs(dt)<0.4]):
    s=(n==k)&(np.abs(dt)<0.4); i=s&(np.abs(dt)<0.044); o=s&(np.abs(dt)>0.076)
    if i.sum()<2 or o.sum()<8: continue
    c=np.polyfit(dt[o],f[o],1); r=f[o]-np.polyval(c,dt[o]); d=1-np.mean(f[i]/np.polyval(c,dt[i]))
    rows.append(dict(epoch=int(k),predicted_mid_btjd=T0+k*P,predicted_mid_bjd_tdb=T0+k*P+2457000,quarter=int(q[s][0]),n_in=int(i.sum()),depth_ppm=d*1e6,err_ppm=np.std(r)/np.sqrt(i.sum())*1e6,
        held_out=bool(q[s][0] in (12,14,15,16))))
E=pd.DataFrame(rows); E.to_csv(O+'kic5689121_per_transit_depths.csv',index=False,float_format='%.6f')
d=json.load(open('/root/ph/post/diffimg.json'))
for s,v in d['seasons'].items():
    pd.DataFrame(v['diff']).to_csv(O+'kic5689121_diffimage_season%s_electrons_per_s.csv'%s,index=False,header=False)
    pd.DataFrame(np.array(v['diff'],dtype=float)/np.array(v['diff_err'],dtype=float)).to_csv(O+'kic5689121_diffimage_season%s_snr.csv'%s,index=False,header=False,float_format='%.3f')
pd.DataFrame(d['gaia']).to_csv(O+'kic5689121_gaia_neighbours_120arcsec.csv',index=False)
summ=dict(target=dict(kic=5689121,tic=120686465,gaia_dr3='2103792461826460288',ra_deg=285.90782692874626,dec_deg=40.94198844296448,constellation='Lyra',G=16.282,Kp=16.332,
  teff_tic=3633,radius_tic_rsun=0.50748,mass_tic_msun=0.5054,distance_pc=298,ruwe=0.984),
  ephemeris=dict(period_d=fit['P'],t0_btjd=fit['T0_btjd'],t0_bjd_tdb=fit['T0_btjd'][0]+2457000,note='median, -err, +err; full-baseline PSF MCMC'),
  transit=dict(radius_ratio=fit['k'],impact_parameter=fit['b'],aR=float(np.exp(fit['ln_aR'][0])),rho_star_solar=fit['rho_star_solar'],
     depth_ppm_range='~1830-2430 depending on method (PSF); SAP aperture 1438 +/- 105 (diluted)',duration_h='2.1-2.4',
     radius_earth_if_on_target='~2.5 (TIC R*) to ~2.8 (Gaia R*), Codex fixed-density fits 2.96-3.09'),
  n_transits_measured=int(len(E)),held_out_events=int(E.held_out.sum()),
  fpp=json.load(open('/root/ph/work/tri/fpp_summary.json')),status='planet candidate; not validated, not confirmed')
json.dump(summ,open(O+'kic5689121_key_numbers.json','w'),indent=1,default=float)
print(len(E),'events; held out',E.held_out.sum(),'; mean depth %.0f ppm'%E.depth_ppm.mean())
