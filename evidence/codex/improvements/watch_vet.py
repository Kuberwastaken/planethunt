"""Independently vet newly screened v3+ signals for a bounded observation period."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from independent_vet import load,vet

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).resolve().parent/'vetting'


def scan():
    count=0
    for path in sorted((ROOT/'results').glob('*.json')):
        try:r=json.loads(path.read_text())
        except (OSError,json.JSONDecodeError):continue
        if r.get('pipeline_version',0)<3 or r.get('inverted'):continue
        # This injected workload target is a known real-planet positive control.
        if r.get('tic')==410153553:continue
        for sig in r.get('signals',[]):
            if not sig.get('screen_pass'):continue
            dest=OUT/f"{r['tic']}_{r['mode']}_rank{sig['rank']}_v{r['pipeline_version']}.json"
            search_digest=hashlib.sha256(path.read_bytes()).hexdigest()
            if dest.exists():
                old=json.loads(dest.read_text())
                if old.get('source_search_sha256')==search_digest:continue
                # A fresh search/input supersedes the old measurement; preserve it.
                history=OUT/'history';history.mkdir(exist_ok=True)
                dest.rename(history/f'{dest.stem}_{int(time.time())}.json')
            rawpath=ROOT/'lightcurves'/f"{r['tic']}.npz"
            try:
                digest=hashlib.sha256(rawpath.read_bytes()).hexdigest()
                if r.get('input_sha256') and r['input_sha256']!=digest:
                    # Refreshed input needs a new search, not vetting an old ephemeris
                    # against an undisclosed change to the supposed holdout.
                    continue
                lc=load(rawpath)
                # Mirror quality-preserving selected sectors and discovery rejection;
                # never re-optimize the ephemeris using heldout observations.
                excluded=r.get('rejected_discovery_sectors',[])
                if excluded:
                    import numpy as np
                    keep=~np.isin(lc['sector'],excluded)
                    lc={k:v[keep] for k,v in lc.items()}
                v=vet(lc,sig['period'],sig['t0'],sig['duration_hr']/24,
                      holdout=tuple(r.get('holdout_sectors',[])),controls=64,
                      holdout_was_unseen=False)
                v.update(tic=r['tic'],mode=r['mode'],rank=sig['rank'],pipeline_version=r['pipeline_version'],
                         source_search=str(path),source_search_sha256=search_digest,
                         source_npz=str(rawpath),source_npz_sha256=digest,
                         source_holdout_caveat=r.get('holdout_caveat'))
            except Exception as e:
                v={'tic':r['tic'],'mode':r['mode'],'rank':sig['rank'],'status':'vet_error','error':repr(e),
                   'pipeline_version':r['pipeline_version'],'source_search':str(path),
                   'source_search_sha256':search_digest,
                   'interpretation':'This diagnostic could not be applied; this is not evidence that observed events are absent.'}
            OUT.mkdir(exist_ok=True)
            dest.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
            print(json.dumps({'file':str(dest),**{k:v[k] for k in ('tic','mode','rank','primary','odd_even_sigma','secondary','flags','error') if k in v}}),flush=True)
            count+=1
    return count


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=600);p.add_argument('--poll',type=float,default=15)
    a=p.parse_args();end=time.monotonic()+a.seconds;total=0
    while True:
        total+=scan()
        if time.monotonic()>=end:break
        time.sleep(min(a.poll,max(0,end-time.monotonic())))
    print(json.dumps({'watch_complete':True,'new_survivors_vetted':total}),flush=True)
