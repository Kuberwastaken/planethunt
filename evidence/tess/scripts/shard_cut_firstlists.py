"""usage: python shard.py K N [WORKERS]  -> searches shard K of N over FFI-only stars with snr_ref<10 (sorted desc), top 600.
Output: results/phase2/stars/<TIC>.json; at end prints passing signals (sde>=9, snr>=7) to hits_K.txt"""
import sys; sys.path.insert(0,'pipeline')
import env, importlib, json, glob, pandas as pd
from multiprocessing import Pool
d02=importlib.import_module('02_download'); s03=importlib.import_module('03_search')
from env import RESULTS, LIGHTCURVES
K,N=int(sys.argv[1]),int(sys.argv[2]); W=int(sys.argv[3]) if len(sys.argv)>3 else 2
for d in (s03.STARS,s03.PERIODOGRAMS,LIGHTCURVES): d.mkdir(parents=True,exist_ok=True)
tg=pd.read_csv(RESULTS/'targets_ranked.csv'); tg=tg[(~tg.has_2min)&(tg.snr_ref<10)].sort_values('snr_ref',ascending=False).head(600)
tg=tg.iloc[K::N].head(60); rho=(tg.Mass/tg.Rad**3).fillna(1).clip(.2,50)

def trim4(tic):
    import numpy as np
    f=LIGHTCURVES/f'{tic}.npz'; d=dict(np.load(f)); sec=np.unique(d['sector'])[-4:]; k=np.isin(d['sector'],sec)
    n=len(d['time']); out={a:(v[k] if getattr(v,'shape',None)==(n,) else v) for a,v in d.items()}; np.savez_compressed(f,**out)
def job(a):
    tic,r=a; d02.download_star(tic)
    if not (LIGHTCURVES/f'{tic}.npz').exists(): return {'tic':tic,'status':'nodata'}
    trim4(tic)
    rec=s03.search_star((tic,r))
    (LIGHTCURVES/f'{tic}.npz').unlink(missing_ok=True)  # save disk
    return rec
if __name__=='__main__':
    with Pool(W) as p:
        for r in p.imap_unordered(job,list(zip(tg.TIC.astype(int),rho.astype(float)))): print(r['tic'],r['status'],flush=True)
    out=[]
    for f in glob.glob(str(s03.STARS/'*.json')):
        r=json.load(open(f))
        for s in r.get('signals',[]):
            if s['sde']>=9 and s['snr']>=7: out.append((r['tic'],s))
    open(f'hits_{K}.txt','w').write(json.dumps(out,indent=1))
    print('hits',len(out))
