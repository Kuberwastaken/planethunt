import urllib.request,urllib.parse,http.cookiejar,re,json,hashlib,datetime
from pathlib import Path
p=Path(__file__).parent
jar=http.cookiejar.CookieJar();o=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar));u='https://keplerebs.villanova.edu/search';b=o.open(u,timeout=90).read();s=b.decode();csrf=re.search("name='csrfmiddlewaretoken' value='([^']+)'",s).group(1)
params={'csrfmiddlewaretoken':csrf,'campaign_-2':'on','search_incat1':'on','search_incat0':'on','perpage':'all','format':'file_csv','sort':'kic'}
for c in ['kic','p','bjd0','ra','dec','pdepth','sdepth','morph','incat','flags']:params['col_'+c]='on'
r=o.open(urllib.request.Request('https://keplerebs.villanova.edu/process_search',data=urllib.parse.urlencode(params).encode(),headers={'Referer':u}),timeout=90);raw=r.read();(p/'kepler_eb.csv').write_bytes(raw);(p/'kepler_eb.csv.provenance.json').write_text(json.dumps({'url':r.url,'parameters':{k:v for k,v in params.items()if k!='csrfmiddlewaretoken'},'sha256':hashlib.sha256(raw).hexdigest(),'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2));print(len(raw),raw[:500])
