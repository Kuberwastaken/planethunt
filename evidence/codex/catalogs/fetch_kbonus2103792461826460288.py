import urllib.request,urllib.parse,json,hashlib,datetime,concurrent.futures
from pathlib import Path
p=Path(__file__).parent;ra=285.907836;dec=40.941985;tic='kbonus2103792461826460288';gid='2103792461826460288'
def save(name,u,data=None):
 try:
  b=urllib.request.urlopen(urllib.request.Request(u,data=data),timeout=120).read();(p/name).write_bytes(b);(p/(name+'.provenance.json')).write_text(json.dumps({'url':u,'body':data.decode()if data else None,'sha256':hashlib.sha256(b).hexdigest(),'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2));print(name,len(b),flush=True)
 except Exception as e:print(name,repr(e),flush=True)
def gaia(name,q):save(name,'https://gea.esac.esa.int/tap-server/tap/sync?'+urllib.parse.urlencode({'REQUEST':'doQuery','LANG':'ADQL','FORMAT':'csv','QUERY':q}))
q=f"SELECT source_id,ra,dec,parallax,pmra,pmdec,phot_g_mean_mag,phot_bp_mean_mag,phot_rp_mean_mag,ruwe,non_single_star,teff_gspphot,logg_gspphot FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{ra},{dec},{120/3600}))"
req={'service':'Mast.Catalogs.Tic.Cone','params':{'ra':ra,'dec':dec,'radius':120/3600},'format':'json','pagesize':5000,'page':1}
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as e:
 fs=[e.submit(save,f'tic{tic}_tic_cone.json','https://mast.stsci.edu/api/v0/invoke',urllib.parse.urlencode({'request':json.dumps(req)}).encode()),e.submit(gaia,f'tic{tic}_gaia_cone.csv',q),e.submit(gaia,f'tic{tic}_gaia_ap.csv',f'SELECT * FROM gaiadr3.astrophysical_parameters WHERE source_id={gid}')]
 for f in fs:f.result()
