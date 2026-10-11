"""Build the public digest from preserved measurements. Stdlib only, no network.
Run: python3 scripts/site/charts.py && python3 scripts/site/build_site.py
"""
from pathlib import Path
import csv
import json
import re

ROOT = Path(__file__).resolve().parents[2]
V = 'analysis/validation-20261011/'
D = ROOT / V / 'post/data'

def csvrows(name):
    with (D / name).open() as f:
        return list(csv.DictReader(f))

def load(name):
    return json.loads((D / name).read_text())

# Keep the original photometry values, not a simulated display curve.
# Compact column arrays make the complete light curve inexpensive to inspect in-browser.
light = csvrows('kic5689121_lightcurve_psf.csv')
data = {
    'provenance': {'directory': V + 'post/data/', 'note': 'Saved measurements; presentation is not a new scientific analysis.'},
    'key': load('kic5689121_key_numbers.json'),
    'model': load('kic5689121_model_numbers.json'),
    'fold': [[float(r[k]) for k in ('hours_from_mid','flux_ppm','err_ppm')] for r in csvrows('kic5689121_folded_15min_bins.csv')],
    'transitModel': [[float(r[k]) for k in ('hours_from_mid','model_ppm')] for r in csvrows('kic5689121_transit_model.csv')][::2],
    'events': [[int(r['epoch']),float(r['depth_ppm']),float(r['err_ppm']),r['held_out']=='True',int(r['quarter'])] for r in csvrows('kic5689121_per_transit_depths.csv')],
    'light': [[round(float(r['time_btjd']),7),round((float(r['flux_detrended'])-1)*1e6,2),int(r['quarter']),r['in_transit']=='True'] for r in light],
}
(ROOT/'docs/site-data.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
html = (ROOT/'scripts/site/page.html').read_text()
for name in re.findall(r'\{\{chart:([\w-]+)\}\}',html):
    svg = (ROOT/f'docs/charts/{name}.svg').read_text()
    svg=svg.replace('aria-labelledby="t d"', f'aria-labelledby="{name}-t {name}-d"').replace('id="t"',f'id="{name}-t"').replace('id="d"',f'id="{name}-d"')
    html=html.replace('{{chart:'+name+'}}',svg)
# Retain the earlier methods/evidence, with dated caveats, in an accessible appendix.
legacy=(ROOT/'scripts/site/legacy_sections.html').read_text()
appendices=[]
for name,title in [('tess','Original TESS evidence'),('kepler','Original Kepler evidence'),('methods','Methods and early controls'),('extension','The extended Kepler search')]:
    match=re.search(rf'<section class="section" id="{name}">(.*?)</section>',legacy,re.S)
    if not match: raise ValueError(f'Missing legacy section {name}')
    body=match.group(1)
    appendices.append(f'<details><summary>{title} · 10–11 October record</summary><div class="legacy"><p class="dated">Historical evidence. The 11 October validation above supersedes earlier statements that formal FPP or holdout tests are missing.</p>{body}</div></details>')
html=html.replace('{{appendices}}','\n'.join(appendices))
if '{{' in html: raise ValueError('Unresolved template token')
(ROOT/'index.html').write_text(html)
print(f'Built index.html; {len(light):,} original light-curve samples and {len(data["events"])} event measurements.')
