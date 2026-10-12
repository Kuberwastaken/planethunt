"""Restore missing Spitzer inputs from recorded URLs, verifying every SHA-256."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1] / 'spitzer'
UA = 'OpenAI File Downloader, XaiImageApiFetch/1.0'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def fetch(url):
    return subprocess.check_output(['curl', '-fLSs', '--max-time', '120', '-A', UA, url])

manifest = json.loads((ROOT / 'provenance.json').read_text())
for entry in json.loads((ROOT / 'download-log.json').read_text()):
    path = ROOT / 'fits' / entry['file']
    if not path.exists():
        data = fetch(entry['url'])
        if digest(data) != entry['sha256']:
            raise ValueError(f'Archive content changed: {entry["url"]}')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
missing_prfs = [e for e in manifest['files'] if e['path'].startswith('prfs/') and not (ROOT/e['path']).exists()]
if missing_prfs:
    data = fetch(manifest['prf_url'])
    if digest(data) != manifest['prf_archive_sha256']:
        raise ValueError('PRF archive content changed')
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        members = {Path(m.name).name: m for m in archive.getmembers() if m.isfile()}
        for entry in missing_prfs:
            path = ROOT / entry['path']
            content = archive.extractfile(members[path.name]).read()
            if digest(content) != entry['sha256']:
                raise ValueError(f'PRF hash mismatch: {path.name}')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
for entry in manifest['files']:
    path = ROOT / entry['path']
    if digest(path.read_bytes()) != entry['sha256']:
        raise ValueError(f'Input hash mismatch: {path}')
print(f'Verified {len(manifest["files"])} input files.')
