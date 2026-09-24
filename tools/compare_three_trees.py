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
    if not (p.exists() or p.is_symlink()):
        return None
    if p.is_symlink():
        return ('symlink', os.readlink(p))
    if p.is_file():
        return ('file', digest(p), str(p.stat().st_size))
    if p.is_dir():
        return ('dir',)
    return ('other', str(p.lstat().st_size))

def collect(*roots):
    paths = set()
    for root in roots:
        for p in root.rglob('*'):
            paths.add(p.relative_to(root))
    return paths

def classify(a, m, n):
    # a = ASUS 51955, m = Merlin 386.14_2, n = ASUS 52334
    if a == m == n:
        return 'ALL_IDENTICAL'

    if a is None and m is not None and n is None:
        return 'MERLIN_ONLY_PURE_ADDITION'
    if a is None and m is not None and n == m:
        return 'MERLIN_ADDITION_NOW_IN_ASUS_52334'
    if a is None and m is None and n is not None:
        return 'ASUS_52334_ONLY_ADDITION'

    if a is not None and m == a and n != a:
        return 'ASUS_LATER_CHANGE_ONLY'
    if a is not None and n == a and m != a:
        return 'MERLIN_DELTA_ASUS_UNCHANGED'
    if a is not None and m == n and m != a:
        return 'MERLIN_MATCHES_LATER_ASUS'

    if a is not None and m is None and n == a:
        return 'MERLIN_REMOVAL_ASUS_UNCHANGED'
    if a is not None and m is None and n is None:
        return 'REMOVED_BY_BOTH'
    if a is not None and m == a and n is None:
        return 'REMOVED_LATER_BY_ASUS'

    if a is None and m is not None and n is not None and m != n:
        return 'BOTH_ADDED_DIFFERENTLY'

    if a is not None and m != a and n != a and m != n:
        return 'BOTH_CHANGED_DIVERGENT'

    return 'OTHER_MIXED'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('asus_51955')
    ap.add_argument('merlin')
    ap.add_argument('asus_52334')
    ap.add_argument('-o', '--output', required=True)
    args = ap.parse_args()

    aroot = Path(args.asus_51955).resolve()
    mroot = Path(args.merlin).resolve()
    nroot = Path(args.asus_52334).resolve()

    counts = {}
    rows = []
    for rel in sorted(collect(aroot, mroot, nroot), key=lambda x: x.as_posix()):
        a = entry(aroot, rel)
        m = entry(mroot, rel)
        n = entry(nroot, rel)
        cls = classify(a, m, n)
        counts[cls] = counts.get(cls, 0) + 1
        rows.append((cls, '/' + rel.as_posix(), a, m, n))

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['class', 'path', 'asus_51955', 'merlin_386_14_2', 'asus_52334'])
        for cls, path, a, m, n in rows:
            w.writerow([cls, path, repr(a), repr(m), repr(n)])

    print('SUCCESS:', args.output)
    for k in sorted(counts):
        print(f'{k}\t{counts[k]}')

if __name__ == '__main__':
    main()
