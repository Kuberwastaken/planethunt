"""Separate retrospective rerun omitting whole QLP S99--104 products.

Original v3 results and NPZ files are never changed. Last retained observing
season is assigned as holdout before the new period search, but because earlier
analyses inspected these stars this is NOT an independent blind validation.
"""
import csv,json,hashlib,sys
from pathlib import Path
import numpy as np

PROJECT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT));import run_search as S
sys.path.insert(0,str(PROJECT/'improvements'))
from independent_vet import load,vet


def main():
    branch=Path(__file__).resolve().parent/'timing_safe_repeat'
    for name in ('lightcurves','results','manifests','vetting'):(branch/name).mkdir(parents=True,exist_ok=True)
    with (PROJECT/'targets.csv').open() as f:targets={int(r['TIC']):r for r in csv.DictReader(f)}
    S.ROOT=branch;reports=[]
    for tic,mode in ((358559650,'usp'),(241606913,'regular')):
        old=PROJECT/'lightcurves'/f'{tic}.npz';manifest=json.loads((PROJECT/'manifests'/f'{tic}.json').read_text())
        remove=sorted({int(m['sector']) for m in manifest if m.get('provenance')=='QLP' and 99<=int(m['sector'])<=104 and not m.get('error') and not m.get('parse_error')})
        with np.load(old,allow_pickle=False) as z:
            lc={k:z[k] for k in z.files}
        keep=~np.isin(lc['sector'],remove)
        clean={k:(v[keep] if isinstance(v,np.ndarray) and v.shape==lc['time'].shape else v) for k,v in lc.items()}
        if 'authors' in clean:clean['authors']=np.array([a for a in clean['authors'] if int(str(a).split(':')[0]) not in remove])
        new=branch/'lightcurves'/f'{tic}.npz';np.savez_compressed(new,**clean)
        provenance={'tic':tic,'removed_qlp_sectors':remove,'original_npz':str(old),
                    'original_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),
                    'filtered_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),
                    'retained_sectors':sorted(map(int,np.unique(clean['sector']))),
                    'reason':'MAST QLP warning: barycentric timing errors for second half S99 through S104; whole sector products omitted conservatively.',
                    'source':'https://archive.stsci.edu/hlsp/qlp','interpretation':'Retrospective rerun; new holdout assigned before this period refit, but its data were seen in previous pipeline development.'}
        (branch/'manifests'/f'{tic}_filter.json').write_text(json.dumps(provenance,indent=2)+'\n')
        row=targets[tic];row['TIC']=tic;row['Mass']=float(row['Mass']);row['Rad']=float(row['Rad'])
        r=S.one((row,mode,False));r['analysis_branch']='timing_safe_reanalysis';r['timing_filter_provenance']=provenance
        out=branch/'results'/f'{tic}_{mode}.json';out.write_text(json.dumps(r,indent=2)+'\n')
        for sig in r.get('signals',[]):
            if not sig.get('screen_pass'):continue
            v=vet(load(new),sig['period'],sig['t0'],sig['duration_hr']/24,holdout=tuple(r.get('holdout_sectors',[])),controls=64)
            v.update(tic=tic,rank=sig['rank'],mode=mode,analysis_branch='timing_safe_reanalysis',
                     source_search=str(out),source_search_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
                     source_npz=str(new),source_npz_sha256=hashlib.sha256(new.read_bytes()).hexdigest())
            (branch/'vetting'/f'{tic}_{mode}_rank{sig["rank"]}.json').write_text(json.dumps(v,indent=2)+'\n')
        summary={'tic':tic,'mode':mode,'status':r['status'],'removed_qlp_sectors':remove,
                 'discovery_sectors':r.get('discovery_sectors'),'holdout_sectors':r.get('holdout_sectors'),
                 'signals':[{k:s[k] for k in ('rank','period','duration_hr','depth_ppm','bls_snr','screen_pass')}|
                            {'holdout_snr':s['holdout']['snr']} for s in r.get('signals',[])]}
        reports.append(summary);print(json.dumps(summary),flush=True)
    (branch/'summary.json').write_text(json.dumps(reports,indent=2)+'\n')


if __name__=='__main__':main()
