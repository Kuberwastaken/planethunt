"""usage: python3 shard_ext.py K N [WORKERS]   (K = lane index 0..N-1; N=6 for the 1500-star extended list, ~250 stars/lane)
Searches shard K of results/targets_extended.csv with Paras's BLS pipeline (MIT). Light curves deleted after search.
Output: results/phase2/stars/<TIC>.json ; at the end hits_ext_K.txt = signals with SDE>=9, SNR>=7, >=3 transits, period>1 d, not TESS-orbit alias."""
import sys; sys.path.insert(0,'pipeline')
import env, importlib, json, glob, pandas as pd
from multiprocessing import Pool
d02=importlib.import_module('02_download'); s03=importlib.import_module('03_search')
from env import RESULTS, LIGHTCURVES
K,N=int(sys.argv[1]),int(sys.argv[2]); W=int(sys.argv[3]) if len(sys.argv)>3 else 2
for d in (s03.STARS,s03.PERIODOGRAMS,LIGHTCURVES): d.mkdir(parents=True,exist_ok=True)
tg=pd.read_csv(RESULTS/'targets_extended.csv').sort_values('snr_ref',ascending=False).reset_index(drop=True)
tg=tg.iloc[K::N].head(60); rho=(tg.Mass/tg.Rad**3).fillna(1).clip(.2,50)
mine=set(tg.TIC.astype(int))

def trim4(tic):
    import numpy as np
    f=LIGHTCURVES/f'{tic}.npz'; d=dict(np.load(f)); sec=np.unique(d['sector'])[-4:]; k=np.isin(d['sector'],sec)
    n=len(d['time']); out={a:(v[k] if getattr(v,'shape',None)==(n,) else v) for a,v in d.items()}; np.savez_compressed(f,**out)
def job(a):
    tic,r=a; d02.download_star(tic)
    if not (LIGHTCURVES/f'{tic}.npz').exists(): return {'tic':tic,'status':'nodata'}
    trim4(tic)
    rec=s03.search_star((tic,r)); (LIGHTCURVES/f'{tic}.npz').unlink(missing_ok=True); return rec
if __name__=='__main__':
    with Pool(W) as p:
        for r in p.imap_unordered(job,list(zip(tg.TIC.astype(int),rho.astype(float)))): print(r['tic'],r['status'],flush=True)
    out=[]
    for t in mine:
        f=s03.STARS/f'{t}.json'
        if not f.exists(): continue
        r=json.load(open(f))
        for s in r.get('signals',[]):
            if s['sde']>=9 and s['snr']>=7 and s['n_transits']>=3 and s['period']>1 and not s.get('flags'):
                if not any(abs(s['period']/13.7-h)<0.01*h for h in (.25,1/3,.5,1,2)): out.append((t,s))
    open(f'hits_ext_{K}.txt','w').write(json.dumps(out,indent=1)); print('hits',len(out))
