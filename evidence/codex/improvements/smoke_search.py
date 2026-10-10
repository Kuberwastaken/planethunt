"""Actual root search injection and holdout-leakage smoke test.

Runs run_search.one against a temporary directory, never real result paths.
This is an implementation check, not an injection-completeness measurement.
"""
import json
import sys
import tempfile
from pathlib import Path
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import run_search as S


def synthetic(period,duration,seed=92):
    rng=np.random.default_rng(seed)
    t=np.concatenate([np.arange(b,b+12,5/1440) for b in (1400.,1440.,1480.)])
    sectors=np.repeat([1,2,3],len(t)//3)
    epoch=1400.8137
    phase=(t-epoch+period/2)%period-period/2
    ex=5/1440
    overlap=np.maximum(0,np.minimum(phase+ex/2,duration/2)-np.maximum(phase-ex/2,-duration/2))/ex
    f=1+.0003*np.sin(2*np.pi*t/5)+rng.normal(0,.0005,len(t))-.002*overlap
    return {'time':t,'flux':f,'flux_err':np.full(len(t),.0005),
            'exptime':np.full(len(t),300.),'sector':sectors}


def main():
    reports=[]
    with tempfile.TemporaryDirectory(prefix='tess_search_smoke_') as td:
        S.ROOT=Path(td)
        for name in ('lightcurves','results','manifests'):(S.ROOT/name).mkdir()
        for mode,period,duration,rho in [('regular',2.371,.065,8.),('usp',.3173,.017,80.)]:
            tic=999999999;lc=synthetic(period,duration)
            row={'TIC':tic,'Mass':rho*.2**3,'Rad':.2}
            np.savez_compressed(S.ROOT/'lightcurves'/f'{tic}.npz',**lc)
            r=S.one((row,mode,False))
            if r['status']!='ok':raise AssertionError(r)
            first=r['signals'][0]
            relative_error=abs(first['period']/period-1)
            assert relative_error<.001,(mode,'did not recover period',first)
            assert r['holdout_sectors']==[3],r
            assert first['holdout']['snr']>5,first
            # Change only unseen flux dramatically. Discovery ephemeris must be identical.
            lc['flux'][lc['sector']==3]=1+np.random.default_rng(17).normal(0,.001,(lc['sector']==3).sum())
            np.savez_compressed(S.ROOT/'lightcurves'/f'{tic}.npz',**lc)
            (S.ROOT/'results'/f'{tic}_{mode}.json').unlink()
            changed=S.one((row,mode,False))
            cf=changed['signals'][0]
            for field in ('period','t0','duration_hr','depth_ppm','bls_snr'):
                assert first[field]==cf[field],('holdout leakage',field,first[field],cf[field])
            rec={'mode':mode,'true_period':period,'recovered_period':first['period'],
                 'true_duration_hr':duration*24,'recovered_duration_hr':first['duration_hr'],
                 'discovery_snr':first['bls_snr'],'holdout_snr':first['holdout']['snr'],
                 'screen_pass':first['screen_pass'],'holdout_flux_changed_ephemeris':False,
                 'noise_holdout_snr':cf['holdout']['snr']}
            reports.append(rec);print(json.dumps(rec),flush=True)
    return reports


if __name__=='__main__':main()
