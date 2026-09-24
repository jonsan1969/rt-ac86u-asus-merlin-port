#!/usr/bin/env python3
import argparse
import csv
import hashlib
import os
from pathlib import Path

def digest(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def entry(root, rel):
    p = root / rel
    if p.is_symlink():
        return ('symlink', os.readlink(p), '-')
    if p.is_file():
        return ('file', digest(p), str(p.stat().st_size))
    if p.is_dir():
        return ('dir', '-', '-')
    return ('other', '-', '-')

def collect(root):
    out = set()
    for p in root.rglob('*'):
        try:
            out.add(p.relative_to(root))
        except ValueError:
            pass
    return out

def main():
    ap = argparse.ArgumentParser(description='Deterministic file/hash diff between extracted firmware trees')
    ap.add_argument('asus_root')
    ap.add_argument('merlin_root')
    ap.add_argument('-o', '--output', default='reports/firmware-tree-diff.tsv')
    args = ap.parse_args()
    a, m = Path(args.asus_root).resolve(), Path(args.merlin_root).resolve()
    paths = sorted(collect(a) | collect(m), key=lambda x: x.as_posix())
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    counts = {'IDENTICAL': 0, 'ASUS_ONLY': 0, 'MERLIN_ONLY': 0, 'DIFFERENT': 0}
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['class', 'path', 'asus_type', 'asus_sha_or_target', 'asus_size',
                    'merlin_type', 'merlin_sha_or_target', 'merlin_size'])
        for rel in paths:
            ae = entry(a, rel) if (a / rel).exists() or (a / rel).is_symlink() else None
            me = entry(m, rel) if (m / rel).exists() or (m / rel).is_symlink() else None
            if ae is None:
                cls = 'MERLIN_ONLY'
            elif me is None:
                cls = 'ASUS_ONLY'
            elif ae == me:
                cls = 'IDENTICAL'
            else:
                cls = 'DIFFERENT'
            counts[cls] += 1
            w.writerow([cls, '/' + rel.as_posix(), *(ae or ('-', '-', '-')), *(me or ('-', '-', '-'))])
    print('SUCCESS:', args.output)
    for k in ('IDENTICAL', 'ASUS_ONLY', 'MERLIN_ONLY', 'DIFFERENT'):
        print(f'{k}\t{counts[k]}')

if __name__ == '__main__':
    main()
