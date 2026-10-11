"""Regenerate inventory.json and SHA256SUMS for every git-tracked file (inventory.json and SHA256SUMS themselves excluded,
inventory.json is listed in SHA256SUMS). Run from repo root after `git add -A`."""
import json, hashlib, subprocess
files = [f for f in subprocess.run(['git', 'ls-files', '-co', '--exclude-standard'], capture_output=True, text=True).stdout.split('\n') if f and f not in ('inventory.json', 'SHA256SUMS')]
files = sorted(set(files))
def h(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
old = json.load(open('inventory.json'))
old['files'] = [{'path': f, 'bytes': len(open(f, 'rb').read()), 'sha256': h(f)} for f in files]
old['updated'] = '2026-10-12 public field-report rebuild; science snapshot remains 2026-10-11'
json.dump(old, open('inventory.json', 'w'), indent=2); open('inventory.json', 'a').write('\n')
lines = [f'{e["sha256"]}  {e["path"]}' for e in old['files']] + [f'{h("inventory.json")}  inventory.json']
lines.sort(key=lambda l: l.split('  ', 1)[1])
open('SHA256SUMS', 'w').write('\n'.join(lines) + '\n')
print(len(old['files']), 'files')
