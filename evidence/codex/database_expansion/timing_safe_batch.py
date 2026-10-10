"""Retrospective timing-safe rerun of all44 affected targets, in separate branch."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import csv,json,hashlib,sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
PROJECT=Path(__file__).resolve().parents[1];ROOT=PROJECT/'database_expansion'/'timing_safe_all44'
sys.path.insert(0,str(PROJECT));import run_search as S

def prepare():
 for name in ('lightcurves','results','manifests'):(ROOT/name).mkdir(parents=True,exist_ok=True)
 audit=list(csv.DictReader((PROJECT/'database_expansion/qlp_timing_audit.csv').open()))
 tics=sorted({int(r['tic']) for r in audit if r['timing_status']=='potential_bad_barycentric_time' and r['used']=='True'})
 rows={int(r['TIC']):r for r in csv.DictReader((PROJECT/'targets.csv').open())}
 tasks=[]
 for tic in tics:
  old=PROJECT/'lightcurves'/f'{tic}.npz';new=ROOT/'lightcurves'/f'{tic}.npz';remove=sorted({int(r['sector']) for r in audit if int(r['tic'])==tic and r['timing_status']=='potential_bad_barycentric_time' and r['used']=='True'})
  with np.load(old,allow_pickle=False) as z:lc={k:z[k] for k in z.files}
  keep=~np.isin(lc['sector'],remove);clean={k:(v[keep] if v.shape==lc['time'].shape else v) for k,v in lc.items()}
  if 'authors' in clean:clean['authors']=np.array([a for a in clean['authors'] if int(str(a).split(':')[0]) not in remove])
  if not new.exists():np.savez_compressed(new,**clean)
  prov={'tic':tic,'removed_qlp_sectors':remove,'original_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'filtered_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'retained_sectors':sorted(map(int,np.unique(clean['sector']))),'interpretation':'Retrospective rerun: last retained season assigned before refitting but previously examined data. Omits entire QLP99-104 products conservatively.'}
  (ROOT/'manifests'/f'{tic}_filter.json').write_text(json.dumps(prov,indent=2)+'\n')
  row=rows[tic];row['TIC']=tic;row['Mass']=float(row['Mass']);row['Rad']=float(row['Rad']);tasks.extend([(row,m,False) for m in ('regular','usp')])
 return tasks

def run(task):
 S.ROOT=ROOT;r=S.one(task)
 return {'tic':r.get('tic',task[0]['TIC']),'mode':task[1],'status':r['status'],'error':r.get('error'),'discovery_sectors':r.get('discovery_sectors'),'holdout_sectors':r.get('holdout_sectors'),'signals':[{k:s[k] for k in ('rank','period','duration_hr','depth_ppm','bls_snr','screen_pass')}|{'holdout_snr':s['holdout']['snr']} for s in r.get('signals',[])]}

def main():
 tasks=prepare();results=[]
 with ProcessPoolExecutor(6) as pool:
  for f in as_completed([pool.submit(run,t) for t in tasks]):
   r=f.result();results.append(r);print(json.dumps(r),flush=True);(ROOT/'summary_inprogress.json').write_text(json.dumps(results,indent=2)+'\n')
 (ROOT/'summary.json').write_text(json.dumps({'retrospective':True,'target_count':44,'search_count':len(results),'results':results},indent=2)+'\n')
if __name__=='__main__':main()
