import urllib.request,urllib.parse,json,hashlib,datetime,concurrent.futures
from pathlib import Path
p=Path(__file__).parent
queries={
'kepler_primary_targets.csv':'select distinct kepid,ra,dec from keplerstellar',
'kepler_koi.csv':'select kepid,kepoi_name,kepler_name,ra,dec,koi_disposition,koi_pdisposition,koi_period,koi_time0bk,koi_duration,koi_depth,koi_tce_plnt_num from cumulative',
'kepler_tce.csv':'select kepid,tce_plnt_num,ra,dec,tce_period,tce_time0bk,tce_duration,tce_depth,tce_model_snr,tce_max_mult_ev,tce_nkoi from q1_q17_dr25_tce',
'kepler_confirmed.csv':"select pl_name,hostname,gaia_dr2_id,gaia_dr3_id,tic_id,ra,dec,pl_orbper,pl_tranmid from pscomppars where discoverymethod='Transit' and ra between 275 and 305 and dec between 35 and 55"
}
def fetch(k,q):
 u='https://exoplanetarchive.ipac.caltech.edu/TAP/sync?'+urllib.parse.urlencode({'query':q,'format':'csv'})
 try:
  b=urllib.request.urlopen(u,timeout=180).read(); (p/k).write_bytes(b)
  (p/(k+'.provenance.json')).write_text(json.dumps({'url':u,'query':q,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)},indent=2)); print(k,len(b),flush=True)
 except Exception as e:print(k,repr(e),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as x:list(x.map(lambda item:fetch(*item),queries.items()))
