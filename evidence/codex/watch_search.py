"""Continuously consume acquired stars; terminates after all logged download jobs.
A foreground task, not a persistent hosted/background service.
"""
from run_search import ROOT,one
import pandas as pd,json,time,zipfile
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
if __name__=='__main__':
 tg=pd.read_csv(ROOT/'targets.csv').to_dict('records');submitted=set();pending={}
 with ProcessPoolExecutor(4) as ex:
  while True:
   for row in tg:
    tic=int(row['TIC'])
    lcpath=ROOT/'lightcurves'/f'{tic}.npz'
    if not lcpath.exists() or not zipfile.is_zipfile(lcpath):continue
    for mode in ['usp','regular']:
     key=(tic,mode)
     if key in submitted or (ROOT/'results'/f'{tic}_{mode}.json').exists():continue
     if len(pending)>=12:break
     submitted.add(key);f=ex.submit(one,(row,mode,False));pending[f]=key
   if pending:
    done,_=wait(pending,timeout=5,return_when=FIRST_COMPLETED)
    for f in done:
     key=pending.pop(f)
     try:
      r=f.result();print(json.dumps({k:r.get(k) for k in ['tic','mode','inverted','status','seconds','error']}|{'signals':[{'period':s['period'],'snr':s['bls_snr'],'holdout_snr':s['holdout']['snr'],'screen_pass':s['screen_pass']} for s in r['signals']]}),flush=True)
     except Exception as e:print('worker error',key,str(e),flush=True)
   else:
    log=ROOT/'download_log.jsonl';n=len({json.loads(l)['tic'] for l in log.read_text().splitlines()}) if log.exists() else 0
    if n>=len(tg):break
    time.sleep(5)
 print('Consumer finished',flush=True)
