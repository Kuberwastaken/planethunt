"""Download public catalogs, preserving hashes; build conservative TIC exclusions.

Usage: python refresh_catalogs.py [--tce]
Catalog exclusion is only a first pass. It does not establish novelty or planetary nature.
"""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode, urljoin
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import re
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[1]

def fetch(name, url):
    entry = dict(url=url, requested_utc=datetime.now(timezone.utc).isoformat())
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(url, timeout=55) as response:
            data = response.read()
            entry.update(status=response.status, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        path.write_bytes(data)
    except Exception as exc:
        entry['error'] = repr(exc)
    path.with_suffix(path.suffix + '.provenance.json').write_text(json.dumps(entry, indent=2))
    print(name, entry.get('status',entry.get('error')), flush=True)
    return entry

def exclusions():
    records = []
    def add(values, source):
        for value in pd.Series(values).dropna():
            try:
                records.append(dict(TIC=int(str(value).replace('TIC ', '')), source=source))
            except ValueError:
                pass
    for filename, column in [('nasa_toi.csv','tid'), ('exofop_toi.csv','TIC ID'),
                             ('exofop_ctoi.csv','TIC ID'), ('nasa_pscomppars.csv','tic_id'),
                             ('tce_hosts.csv','ticid'), ('villanova_eb.csv','tic')]:
        path = ROOT/filename
        if path.exists():
            frame = pd.read_csv(path)
            add(frame[column], filename)
    for path in (WORKSPACE/'upstream-eumemic/results_public').glob('candidates*.csv'):
        add(pd.read_csv(path).TIC, 'eumemic/'+path.name)
    for path in (ROOT/'raven').glob('*.csv'):
        add(pd.read_csv(path).ticid, 'RAVEN/'+path.name)
    add([370612437,252721481], 'Paras announced candidates')
    frame = pd.DataFrame(records).drop_duplicates()
    frame.to_csv(ROOT/'known_tic_sources.csv',index=False)
    hosts = frame.groupby('TIC').source.agg(lambda v:'; '.join(sorted(set(v)))).reset_index()
    hosts.to_csv(ROOT/'known_tics.csv',index=False)
    ranked = pd.read_csv(WORKSPACE/'upstream-tess/results/targets_ranked.csv')
    searched = pd.read_csv(WORKSPACE/'upstream-tess/results/phase2/signals.csv').tic
    ranked = ranked[~ranked.TIC.isin(hosts.TIC) & ~ranked.TIC.isin(searched)]
    ranked.to_csv(ROOT/'unsearched_ranked_excluding_known.csv',index=False)
    ranked[~ranked.has_2min].to_csv(ROOT/'unsearched_ffi_excluding_known.csv',index=False)
    print(f'{len(hosts)} excluded hosts; {len(ranked)} unsearched; {(~ranked.has_2min).sum()} FFI only')

if __name__ == '__main__':
    if '--tce' in sys.argv:
        index_url = 'https://archive.stsci.edu/tess/bulk_downloads/bulk_downloads_tce.html'
        fetch('tce_index.html', index_url)
        links = sorted(set(re.findall(r'href="([^"]*dvr-tcestats\.csv)"', (ROOT/'tce_index.html').read_text())))
        def get_tce(link):
            return fetch('tce/'+link.rsplit('/',1)[-1],urljoin(index_url,link))
        with ThreadPoolExecutor(max_workers=5) as executor:
            results=list(executor.map(get_tce,links))
        frames=[]
        for path in (ROOT/'tce').glob('*.csv'):
            f=pd.read_csv(path,comment='#',usecols=lambda c:c in ['ticid','tce_period','tce_time0bt','tce_duration','tce_depth','tce_model_snr','sectors'])
            f['source_file']=path.name
            frames.append(f)
        if frames:
            all_tce=pd.concat(frames,ignore_index=True)
            all_tce.to_csv(ROOT/'tce_all.csv',index=False)
            all_tce[['ticid']].drop_duplicates().to_csv(ROOT/'tce_hosts.csv',index=False)
        print(f'TCE tables: {len(links)} requested, {sum("error" not in x for x in results)} succeeded')
    else:
        urls={
            'nasa_toi.csv':'https://exoplanetarchive.ipac.caltech.edu/TAP/sync?'+urlencode({'query':'select * from toi','format':'csv'}),
            'nasa_pscomppars.csv':'https://exoplanetarchive.ipac.caltech.edu/TAP/sync?'+urlencode({'query':'select pl_name,hostname,tic_id,ra,dec,pl_orbper,pl_tranmid,discoverymethod,disc_year from pscomppars','format':'csv'}),
            'exofop_toi.csv':'https://exofop.ipac.caltech.edu/tess/download_toi.php?sort=toi&output=csv',
            'exofop_ctoi.csv':'https://exofop.ipac.caltech.edu/tess/download_ctoi.php?sort=ctoi&output=csv',
        }
        with ThreadPoolExecutor(max_workers=4) as executor:
            list(executor.map(lambda pair:fetch(*pair),urls.items()))
    exclusions()
