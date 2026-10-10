"""Additional, explicitly exploratory broad-transit diagnostics.

Does NOT replace default-vetter outputs. Compares local windows +/-0.35P and
+/-0.40P with linear/quadratic baselines at a FROZEN search ephemeris. It uses
event-cluster uncertainty and separately reports fixed-ephemeris holdout.
Control boxes do not overlap the real transit and exclude its cadences from
their baselines. They can overlap each other and are not a global FAP sample.
"""
import argparse,json,hashlib,csv
from pathlib import Path
import numpy as np
from independent_vet import load,phase,mad,combine


def contact_geometry(row,sig):
    """Conditional geometry only; BLS width is not a physical transit fit."""
    from scipy.optimize import brentq
    P=sig['period'];D=sig['duration_hr']/24;R=float(row['Rad']);M=float(row['Mass'])
    k=np.sqrt(max(sig['depth_ppm'],0)/1e6);rho=M/R**3
    a=(2.959122e-4*M*P**2/(4*np.pi**2))**(1/3)/(R*.00465047)
    dc=P/np.pi*np.arcsin((1+k)/a);ac=(1+k)/np.sin(np.pi*D/P)
    def at_apastron(e):
        ang=np.arcsin((1+k)/(a*np.sqrt(1-e*e)))
        return P/np.pi*(ang+e*np.sin(ang))
    emax=1-(1+k)/a
    e=brentq(lambda x:at_apastron(x)-D,0,emax-1e-8) if dc<D and emax>0 and at_apastron(emax-1e-8)>D else None
    return {'catalog_radius_solar':R,'catalog_mass_solar':M,'catalog_density_solar':rho,
            'circular_a_over_rstar':a,'assumed_radius_ratio_from_depth':k,
            'circular_central_contact_duration_hours':dc*24,
            'observed_box_duration_over_circular_contact_max':D/dc,
            'circular_central_density_for_box_duration_solar':rho*(ac/a)**3,
            'apastron_central_eccentricity_matching_box_duration':e,
            'matching_eccentric_orbit_periastron_in_rstar':a*(1-e) if e else None,
            'caveat':'Idealized central single-star geometry using catalog parameters and box width as approximate contact duration. Not a fitted eccentric solution. Dilution, shape bias, stellar parameter errors, other source stars, and other periods remain possible.'}


def events(lc,P,t0,D,half_fraction,degree,exclude=None):
    t,f,er,sec,ex=[lc[k] for k in ('time','flux','flux_err','sector','exptime')]
    cy=np.rint((t-t0)/P).astype(np.int64)
    window=half_fraction*P;out=[]
    for n in np.unique(cy):
        center=t0+n*P;a,b=np.searchsorted(t,[center-window,center+window])
        if b-a<16:continue
        for ss in np.unique(sec[a:b]):
            idx=np.arange(a,b)[sec[a:b]==ss]
            if exclude is not None:
                pp,ee,dd=exclude
                # Exposure-aware exclusion: no leakage from the known primary.
                idx=idx[np.abs(phase(t[idx],pp,ee))>(dd+ex[idx]/86400)/2]
            x=t[idx]-center;y=f[idx];exp=ex[idx]/86400;err=er[idx]
            box=np.maximum(0,np.minimum(x+exp/2,D/2)-np.maximum(x-exp/2,-D/2))/exp
            intr=box>0;oot=box==0
            if intr.sum()<2 or (x < -D).sum()<4 or (x>D).sum()<4:continue
            X=np.column_stack([np.ones(len(x)),*[ (x/window)**k for k in range(1,degree+1)],-box])
            noise=mad(np.diff(y[oot]))/np.sqrt(2)
            if not np.isfinite(noise) or noise<=0:continue
            err=np.where(np.isfinite(err)&(err>0),err,noise)
            if np.all(err==1):err=np.full_like(err,noise)
            err=np.maximum(err,noise);w=1/err**2
            try:cov=np.linalg.inv(X.T@(w[:,None]*X))
            except np.linalg.LinAlgError:continue
            beta=cov@(X.T@(w*y));res=y-X@beta
            inflation=max(1.,np.sum(w*res**2)/max(1,len(y)-X.shape[1]))
            sigma=float(np.sqrt(cov[-1,-1]*inflation))
            out.append({'cycle':int(n),'sector':int(ss),'center':float(center),
                        'depth':float(beta[-1]),'error':sigma,'snr':float(beta[-1]/sigma),
                        'n_in':int(intr.sum()),'n_out':int(oot.sum())})
    return out


def one(lc,P,t0,D,holdout,hf,deg,ncontrol=64):
    ev=events(lc,P,t0,D,hf,deg)
    primary=combine(ev);train=combine([r for r in ev if r['sector'] not in holdout]);test=combine([r for r in ev if r['sector'] in holdout])
    odd,even=[combine([r for r in ev if r['cycle']%2==p]) for p in (1,0)]
    oe=abs(odd['depth_ppm']-even['depth_ppm'])/np.hypot(odd['error_ppm'],even['error_ppm']) if odd['n_events'] and even['n_events'] else None
    sec=combine(events(lc,P,t0+P/2,D,hf,deg,exclude=(P,t0,D)))
    offs=(np.arange(ncontrol)+.5)/ncontrol
    offs=offs[np.minimum(offs,1-offs)>D/P+np.max(lc['exptime'])/86400/P]
    controls=[]
    for off in offs:
        c=combine(events(lc,P,t0+off*P,D,hf,deg,exclude=(P,t0,D)))
        if c['n_events']>=3:controls.append({'offset_phase':float(off),**c})
    dep=np.array([r['depth_ppm'] for r in controls]);ns=mad(dep) if len(dep)>5 else None
    return {'half_window_period_fraction':hf,'baseline_polynomial_degree':deg,
            'primary':primary,'discovery':train,'holdout':test,'odd_even_sigma':oe,
            'secondary':sec,'per_sector':{str(s):combine([r for r in ev if r['sector']==s]) for s in sorted(set(lc['sector']))},
            'n_controls':len(controls),'control_depth_scatter_ppm':ns,
            'depth_over_control_scatter':primary.get('depth_ppm',0)/ns if ns else None,
            'phase_controls':controls,'events':ev,
            'control_limitations':'Control boxes do not overlap primary, but overlap each other and can include phase-0.5 dimming. Primary cadences excluded from control baselines. Conditional diagnostic only.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('search_json',type=Path);p.add_argument('--rank',type=int,default=1);p.add_argument('--output',required=True,type=Path);p.add_argument('--controls',type=int,default=64);p.add_argument('--npz',type=Path,help='Explicit filtered NPZ for a separate reanalysis branch')
    a=p.parse_args();r=json.loads(a.search_json.read_text());sig=next(s for s in r['signals'] if s['rank']==a.rank)
    root=Path(__file__).resolve().parents[1];raw=a.npz or root/'lightcurves'/f"{r['tic']}.npz"
    digest=hashlib.sha256(raw.read_bytes()).hexdigest()
    if digest!=r.get('input_sha256'):raise RuntimeError('Search/input hashes differ; cannot vet stale search')
    lc=load(raw);excluded=r.get('rejected_discovery_sectors',[])
    if excluded:
        mask=~np.isin(lc['sector'],excluded);lc={k:v[mask] for k,v in lc.items()}
    P,t0,D=sig['period'],sig['t0'],sig['duration_hr']/24;hold=r['holdout_sectors']
    result={'tic':r['tic'],'mode':r['mode'],'rank':a.rank,'pipeline_version':r['pipeline_version'],
            'ephemeris':{'period_days':P,'epoch_btjd':t0,'duration_hours':D*24,'duty_fraction':D/P},
            'source_search':str(a.search_json.resolve()),'source_search_sha256':hashlib.sha256(a.search_json.read_bytes()).hexdigest(),
            'input_sha256':digest,'holdout_sectors':hold,
            'scope':'Exploratory broad-event diagnostic using newly chosen baseline windows; fixed discovery ephemeris; no planet confirmation/novelty claim.',
            'holdout_status':'Retrospective pipeline-development check; no independent blind-validation claim.',
            'configurations':[]}
    for hf in (.35,.40):
        for deg in (1,2):
            m=one(lc,P,t0,D,hold,hf,deg,a.controls);result['configurations'].append(m)
            print(json.dumps({k:m[k] for k in ('half_window_period_fraction','baseline_polynomial_degree','primary','discovery','holdout','secondary','n_controls','depth_over_control_scatter')}),flush=True)
    with (root/'targets.csv').open() as f:
        row=next((r for r in csv.DictReader(f) if int(r['TIC'])==result['tic']),None)
    if row:result['conditional_geometry']=contact_geometry(row,sig)
    result['control_coverage_warning']='Wide boxes and required side baseline severely restrict control phases, which overlap strongly and cannot establish tail significance.'
    result['control_phase_ranges']=[{'half_window_period_fraction':c['half_window_period_fraction'],
                                    'baseline_polynomial_degree':c['baseline_polynomial_degree'],
                                    'n':c['n_controls'],
                                    'min_phase':min((r['offset_phase'] for r in c['phase_controls']),default=None),
                                    'max_phase':max((r['offset_phase'] for r in c['phase_controls']),default=None)}
                                   for c in result['configurations']]
    a.output.parent.mkdir(exist_ok=True,parents=True);a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')


if __name__=='__main__':main()
