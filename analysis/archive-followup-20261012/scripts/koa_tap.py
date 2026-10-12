import json,subprocess,concurrent.futures,datetime
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'archive'/'additional-probes'
# 5-arcmin enclosing rectangle: aim-point inventory, not image-footprint exclusion.
def query(t):
 q=f'select koaid,ra,dec,date_obs from {t} where ra between 285.7974 and 286.0183 and dec between 40.85865 and 41.02533'
 args=['curl','--silent','--show-error','--max-time','40','-A','OpenAI File Downloader, XaiImageApiFetch/1.0','--get','https://koa.ipac.caltech.edu/TAP/sync','--data-urlencode','query='+q,'--data-urlencode','format=json'];r=subprocess.run(args,capture_output=True);(p/(t+'.json')).write_bytes(r.stdout)
 return {'table':t,'query':q,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':r.returncode,'stderr':r.stderr.decode(),'preview':r.stdout.decode()[:200]}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:log=list(pool.map(query,['koa_nirc2','koa_nirc','koa_hires','koa_nirspec','koa_osiris']))
(p/'koa-tap-log.json').write_text(json.dumps(log,indent=2));print(json.dumps(log,indent=2))
