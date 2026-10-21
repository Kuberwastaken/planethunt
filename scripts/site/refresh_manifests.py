"""Regenerate inventory.json and SHA256SUMS for every git-tracked file (inventory.json and SHA256SUMS themselves excluded,
inventory.json is listed in SHA256SUMS). Run from repo root after `git add -A`."""
import json, hashlib, subprocess

# Output bytes must not depend on the platform: `.gitattributes` pins `* -text`,
# so whatever this script writes is committed verbatim. Without newline='\n' a
# Windows run emits CRLF and a Linux run LF, and the two disagree on every line.
files = [f for f in subprocess.run(['git', 'ls-files', '-co', '--exclude-standard'], capture_output=True, text=True).stdout.split('\n') if f and f not in ('inventory.json', 'SHA256SUMS')]
files = sorted(set(files))
def h(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
old = json.load(open('inventory.json', encoding='utf-8'))
old['files'] = [{'path': f, 'bytes': len(open(f, 'rb').read()), 'sha256': h(f)} for f in files]
old['updated'] = '2026-10-13 publication snapshot; archival follow-up 2026-10-12; validation baseline remains 2026-10-11'
with open('inventory.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(old, f, indent=2); f.write('\n')
lines = [f'{e["sha256"]}  {e["path"]}' for e in old['files']] + [f'{h("inventory.json")}  inventory.json']
lines.sort(key=lambda l: l.split('  ', 1)[1])
with open('SHA256SUMS', 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')
print(len(old['files']), 'files')
