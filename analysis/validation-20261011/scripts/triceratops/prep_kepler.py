"""Prepare TRICERATOPS inputs for KIC 5689121 / TIC 120686465 without network access.
- light curve: KBonus PSF flux, per-event linear out-of-transit baselines, folded on the
  full-baseline MCMC ephemeris (kfit_psf.json).
- background population: the 120-arcsec Gaia DR3 cone already retrieved by the Codex catalog
  agent, characterised with TRICERATOPS' own query_gaia_background recipe, resampled to the
  0.1 deg^2 field area its priors assume."""
import json, numpy as np, pandas as pd
from math import pi
import triceratops.funcs as F
W='/root/ph/work/tri/'
D=np.load('/root/ph/rel/kx/planet-search/database_expansion/kbonus_independent_audit/2103792461826460288_correct_errors.npz')
fit=json.load(open('/root/ph/work/kfit_psf.json')); P=fit['P'][0]; T0=fit['T0_btjd'][0]
t,f=D['time'],D['flux']; ok=np.isfinite(t)&np.isfinite(f); t,f=t[ok],f[ok]
n=np.round((t-T0)/P); dt=t-(T0+n*P); ph=[];fl=[]
for k in np.unique(n[np.abs(dt)<0.3]):
    s=(n==k)&(np.abs(dt)<0.3); o=s&(np.abs(dt)>0.075)
    if o.sum()<8 or (s&(np.abs(dt)<0.03)).sum()<2: continue
    c=np.polyfit(dt[o],f[o],1); ph.append(dt[s]); fl.append(f[s]/np.polyval(c,dt[s]))
ph=np.concatenate(ph); fl=np.concatenate(fl); o=np.argsort(ph); ph,fl=ph[o],fl[o]
err=np.std(fl[np.abs(ph)>0.075])
np.savez(W+'kepler_fold.npz',time=ph,flux=fl,err=err,P=P)
print('folded points',len(ph),'oot rms %.0f ppm'%(err*1e6))
# background population from the Gaia cone
g=pd.read_csv('/root/ph/planethunt/evidence/codex/catalogs/tickbonus2103792461826460288_gaia_cone.csv')
tic=pd.read_csv('/root/ph/planethunt/evidence/codex/catalogs/tickbonus2103792461826460288_tic_cone.csv')
# parallax errors from TIC (Gaia-based) for the parallax_over_error test
# match by position (TIC GAIA column is float and cannot be used as an exact identifier)
from astropy.coordinates import SkyCoord; import astropy.units as u
cg=SkyCoord(g.ra.values*u.deg,g.dec.values*u.deg); ct=SkyCoord(tic.ra.values*u.deg,tic.dec.values*u.deg)
idx,sep,_=cg.match_to_catalog_sky(ct)
g['e_plx']=np.where(sep.arcsec<1.0,tic.e_plx.values[idx],np.nan)
print('position matches <1":',int((sep.arcsec<1).sum()),'of',len(g))
radius_deg=120/3600; area=pi*radius_deg**2
print('cone stars',len(g),'area %.5f deg2'%area, 'G range %.2f-%.2f'%(g.phot_g_mean_mag.min(),g.phot_g_mean_mag.max()))
G,BP,RP,plx=[g[c].values.astype(float) for c in ('phot_g_mean_mag','phot_bp_mean_mag','phot_rp_mean_mag','parallax')]
plx_snr=plx/g['e_plx'].values.astype(float)
def characterise(G,BP,RP,plx,plx_snr):
    Tmag=F.gaia_to_Tmag(G,BP,RP)
    def seq(xc,yc):
        x,y=F.mamajek_column(xc),F.mamajek_column(yc); k=np.isfinite(x)&np.isfinite(y); x,y=x[k],y[k]; o=np.argsort(x); x,y=x[o],y[o]
        k=np.concatenate(([True],np.diff(x)>1e-9)); return x[k],y[k]
    cx,cy=seq('BpRp','Teff'); Teff=np.interp(BP-RP,cx,cy,left=cy[0],right=cy[-1])
    out={}
    for nm,col in (('mass','Msun'),('rad','R_Rsun'),('MG','M_G'),('MJ','M_J'),('MKs','M_Ks'),('JH','JH')):
        x,y=seq('Teff',col); out[nm]=np.interp(Teff,x,y)
    logg=np.log10(F.G*(out['mass']*F.Msun)/(out['rad']*F.Rsun)**2)
    use=np.isfinite(plx)&(plx>0)&(plx_snr>5)
    dmod=np.where(use,5*np.log10(1000/np.where(plx>0,plx,np.nan))-5,G-out['MG'])
    good=np.isfinite(Teff)&np.isfinite(out['mass'])&np.isfinite(dmod)&np.isfinite(Tmag)
    return pd.DataFrame(dict(Mact=out['mass'],logg=logg,logTe=np.log10(Teff),**{'[M/H]':np.zeros_like(G)},TESS=Tmag,
        J=out['MJ']+dmod,H=out['MJ']-out['JH']+dmod,Ks=out['MKs']+dmod))[good]
pop=characterise(G,BP,RP,plx,plx_snr)
print('characterised',len(pop))
rng=np.random.default_rng(1)
Nfield=int(round(len(pop)*0.1/area))
pop01=pop.iloc[rng.integers(0,len(pop),Nfield)].reset_index(drop=True)
pop01.to_csv(W+'bg_gaia_G21.csv',index=False)
print('resampled to 0.1 deg2:',len(pop01))
# faint-end extension G 21-22.5: extrapolate dlogN/dG fitted over G 18-21, colours drawn from G 20-21 stars
Gm=G[np.isfinite(G)]; bins=np.arange(17,21.01,0.5); h,_=np.histogram(Gm,bins); cen=(bins[1:]+bins[:-1])/2
ok=h>0; sl,ic=np.polyfit(cen[ok],np.log10(h[ok]),1)
extra_bins=np.arange(21,22.51,0.5); nextra=[10**(sl*c+ic) for c in (extra_bins[1:]+extra_bins[:-1])/2]
faint=np.where((G>20)&(G<21.1)&np.isfinite(BP)&np.isfinite(RP))[0]
rows=[]
for (lo,hi),ne in zip(zip(extra_bins[:-1],extra_bins[1:]),nextra):
    k=rng.poisson(ne*0.1/area)
    j=rng.choice(faint,k); Gn=rng.uniform(lo,hi,k); dG=Gn-G[j]
    rows.append(characterise(Gn,BP[j]+dG,RP[j]+dG,np.full(k,np.nan),np.zeros(k)))
ext=pd.concat([pop01]+rows,ignore_index=True); ext.to_csv(W+'bg_gaia_G22p5.csv',index=False)
print('slope dlogN/dG %.3f; faint extension adds %d stars (0.1 deg2 equiv)'%(sl,len(ext)-len(pop01)))
json.dump(dict(cone_radius_arcsec=120,cone_area_deg2=area,n_cone=int(len(g)),n_char=int(len(pop)),n_field01=Nfield,slope=sl,n_ext=int(len(ext)),fold_err=float(err),n_fold=int(len(ph))),open(W+'prep_kepler.json','w'),indent=1)
