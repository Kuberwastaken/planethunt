import json,subprocess,datetime,concurrent.futures
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'archive'/'additional-probes';p.mkdir(exist_ok=True)
ua='OpenAI File Downloader, XaiImageApiFetch/1.0'
qs={
'gaia_source':('https://gea.esac.esa.int/tap-server/tap/sync',{'REQUEST':'doQuery','LANG':'ADQL','FORMAT':'csv','QUERY':'select * from gaiadr3.gaia_source where source_id=2103792461826460288'}),
'gaia_nss':('https://gea.esac.esa.int/tap-server/tap/sync',{'REQUEST':'doQuery','LANG':'ADQL','FORMAT':'csv','QUERY':'select * from gaiadr3.nss_two_body_orbit where source_id=2103792461826460288'}),
'gemini_300arcsec':('https://archive.gemini.edu/jsonsummary/canonical/ra=285.907827/dec=40.941988/sr=300',{}),
'koa_tables':('https://koa.ipac.caltech.edu/TAP/sync',{'query':'select table_name from TAP_SCHEMA.tables','format':'json'}),
'koa_nirc2_300arcsec':('https://koa.ipac.caltech.edu/cgi-bin/VOServ/nph-searchImage',{'POS':'CIRCLE 285.907827 40.941988 0.0833333333','INSTRUMENT':'NIRC2','RESULTFORMAT':'csv'}),
'mast_cone':('https://mast.stsci.edu/api/v0/invoke',{'request':json.dumps({'service':'Mast.Caom.Cone','params':{'ra':285.907827,'dec':40.941988,'radius':.0083333333},'format':'json','pagesize':10000,'page':1})})}
def run(it):
 n,(u,params)=it;cmd=['curl','-L','--silent','--show-error','--max-time','45','-A',ua,'--get',u]
 for k,v in params.items():cmd+=['--data-urlencode',k+'='+v]
 r=subprocess.run(cmd,capture_output=True);(p/(n+'.txt')).write_bytes(r.stdout)
 return dict(name=n,url=u,params=params,returncode=r.returncode,stderr=r.stderr.decode(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),bytes=len(r.stdout),preview=r.stdout.decode(errors='replace')[:150])
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:logs=list(pool.map(run,qs.items()))
(p/'query-log.json').write_text(json.dumps(logs,indent=2)); print(json.dumps(logs,indent=2))
