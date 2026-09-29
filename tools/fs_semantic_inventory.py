#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import stat
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def xattrs(path: Path):
    try:
        names = sorted(os.listxattr(path, follow_symlinks=False))
    except (AttributeError, OSError):
        return []
    out = []
    for name in names:
        try:
            value = os.getxattr(path, name, follow_symlinks=False)
        except OSError as e:
            value = f"<ERROR:{e.errno}>".encode()
        out.append([name, value.hex()])
    return out


def kind(st_mode: int) -> str:
    if stat.S_ISDIR(st_mode):
        return "dir"
    if stat.S_ISREG(st_mode):
        return "file"
    if stat.S_ISLNK(st_mode):
        return "symlink"
    if stat.S_ISCHR(st_mode):
        return "char"
    if stat.S_ISBLK(st_mode):
        return "block"
    if stat.S_ISFIFO(st_mode):
        return "fifo"
    if stat.S_ISSOCK(st_mode):
        return "socket"
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    rows = []
    inode_members = {}

    paths = [root] + sorted(root.rglob("*"))
    for p in paths:
        st = p.lstat()
        rel = "/" if p == root else "/" + p.relative_to(root).as_posix()
        k = kind(st.st_mode)
        if k == "file":
            payload = sha256_file(p)
            inode_members.setdefault((st.st_dev, st.st_ino), []).append(rel)
        elif k == "symlink":
            payload = os.readlink(p)
        elif k in ("char", "block"):
            payload = f"{os.major(st.st_rdev)}:{os.minor(st.st_rdev)}"
        else:
            payload = ""

        rows.append({
            "path": rel,
            "type": k,
            "mode": f"{stat.S_IMODE(st.st_mode):04o}",
            "uid": st.st_uid,
            "gid": st.st_gid,
            "payload": payload,
            "xattrs": xattrs(p),
            "_inode": (st.st_dev, st.st_ino) if k == "file" else None,
        })

    hardlink_group = {}
    for inode, members in inode_members.items():
        if len(members) > 1:
            group = "|".join(sorted(members))
            for rel in members:
                hardlink_group[rel] = group

    for row in rows:
        row["hardlinks"] = hardlink_group.get(row["path"], "")
        row.pop("_inode", None)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "\n".join(json.dumps(r, sort_keys=True, separators=(",", ":")) for r in rows) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
