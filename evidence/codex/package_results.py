"""Package reproducible outputs; excludes environments and upstream git checkouts."""
from pathlib import Path
import zipfile,json,hashlib
P=Path(__file__).resolve().parent;OUT=P.parent/'deliverables';OUT.mkdir(exist_ok=True)
source_ids={'2103792461826460288','2103792427466721792','2103789438169485056','2102053446751282944'}
groups={'planet-search-results.zip':[],'planet-search-tess-data.zip':[],'planet-search-kepler-data.zip':[]}
for f in sorted(P.rglob('*')):
 if not f.is_file():continue
 rel=f.relative_to(P);parts=rel.parts
 if any(x in parts for x in ('.venv','__pycache__','cache','lightcurves_v1')):continue
 if f.suffix in ('.pyc','.nbi','.nbc') or f.name.startswith('review-'):continue
 if f.name=='sample.fits':continue
 # Keep original FITS for candidate, neighbors and known Kepler control.
 if 'kbonus' in parts and 'fits' in parts:
  if f.stem not in source_ids:continue
  group='planet-search-data.zip'
 elif f.suffix=='.npz' or 'pixels' in parts and (f.suffix in ('.fits','.gz')):group='planet-search-data.zip'
 else:group='planet-search-results.zip'
 if group=='planet-search-data.zip':
  group='planet-search-kepler-data.zip' if any(x.startswith('kbonus') for x in parts) else 'planet-search-tess-data.zip'
 groups[group].append(f)
summary={}
for name,files in groups.items():
 target=OUT/name;manifest=[]
 with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
  for f in files:
   rel='planet-search/'+str(f.relative_to(P));digest=hashlib.sha256(f.read_bytes()).hexdigest()
   z.write(f,rel,compress_type=zipfile.ZIP_STORED if f.suffix in ('.npz','.gz') else zipfile.ZIP_DEFLATED)
   manifest.append({'path':rel,'bytes':f.stat().st_size,'sha256':digest})
  z.writestr('planet-search/'+name.replace('.zip','-manifest.json'),json.dumps(manifest,indent=2))
 with zipfile.ZipFile(target) as z:
  corrupt=z.testzip()
  if corrupt:raise ValueError(corrupt)
 summary[name]={'files':len(files),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
 print(name,summary[name],flush=True)
(OUT/'package_manifest.json').write_text(json.dumps(summary,indent=2))
