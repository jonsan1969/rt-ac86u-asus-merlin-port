#!/usr/bin/env python3
import argparse
import hashlib
import os
import stat
from pathlib import Path

def sha256(path: Path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('-o', '--output', required=True)
    args = ap.parse_args()
    root = Path(args.root).resolve()
    rows = []
    for p in sorted(root.rglob('*')):
        rel = '/' + p.relative_to(root).as_posix()
        try:
            st = p.lstat()
        except FileNotFoundError:
            continue
        mode = stat.S_IMODE(st.st_mode)
        if p.is_symlink():
            rows.append((rel, 'symlink', '-', mode, os.readlink(p)))
        elif p.is_file():
            rows.append((rel, 'file', sha256(p), mode, str(st.st_size)))
        elif p.is_dir():
            rows.append((rel, 'dir', '-', mode, '-'))
        else:
            rows.append((rel, 'other', '-', mode, str(st.st_size)))
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write('path\ttype\tsha256\tmode\tinfo\n')
        for r in rows:
            f.write('\t'.join([r[0], r[1], r[2], f'{r[3]:04o}', r[4]]) + '\n')

if __name__ == '__main__':
    main()
