#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

PROTECTED_EXACT = {
    "/bin/busybox",
    "/sbin/rc",
    "/usr/sbin/httpd",
    "/usr/sbin/dnsmasq",
    "/usr/sbin/openvpn",
    "/usr/bin/dropbearmulti",
    "/usr/lib/libssl.so.1.1",
    "/usr/lib/libcrypto.so.1.1",
}
PROTECTED_PREFIXES = ("/lib/modules/",)

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def safe_child(base: Path, rel: str, label: str) -> Path:
    if Path(rel).is_absolute():
        raise ValueError(f"{label} must be relative: {rel}")
    out = (base / rel).resolve()
    try:
        out.relative_to(base.resolve())
    except ValueError:
        raise ValueError(f"{label} escapes its source tree: {rel}")
    return out

def safe_target(root: Path, target: str) -> Path:
    if not target.startswith("/"):
        raise ValueError(f"target must be absolute inside rootfs: {target}")
    out = (root / target.lstrip("/")).resolve(strict=False)
    try:
        out.relative_to(root.resolve())
    except ValueError:
        raise ValueError(f"target escapes rootfs: {target}")
    return out

def is_protected(target: str) -> bool:
    return target in PROTECTED_EXACT or any(target.startswith(p) for p in PROTECTED_PREFIXES)

def parse_mode(value):
    if value is None:
        return None
    if isinstance(value, int):
        return value
    return int(str(value), 8)

def main():
    ap = argparse.ArgumentParser(description="Apply hash-pinned additions to an extracted ASUS 52334 rootfs")
    ap.add_argument("--rootfs", required=True)
    ap.add_argument("--merlin-src", required=True)
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--manifest", default="ports/active.json")
    ap.add_argument("--report", default="reports/port-overlay-provenance.tsv")
    args = ap.parse_args()

    root = Path(args.rootfs).resolve()
    merlin = Path(args.merlin_src).resolve()
    repo = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest)

    if not root.is_dir():
        raise SystemExit(f"rootfs not found: {root}")
    if not merlin.is_dir():
        raise SystemExit(f"Merlin source tree not found: {merlin}")
    if not repo.is_dir():
        raise SystemExit(f"repo root not found: {repo}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != 1:
        raise SystemExit("unsupported manifest schema")
    if manifest.get("asus_baseline") != "3.0.0.4.386_52334":
        raise SystemExit("manifest ASUS baseline is not 3.0.0.4.386_52334")
    if manifest.get("merlin_commit") != "6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b":
        raise SystemExit("manifest Merlin commit is not the project donor pin")

    rows = []
    for idx, entry in enumerate(manifest.get("entries", []), 1):
        etype = entry.get("type", "copy")
        target = entry.get("target")
        policy = entry.get("policy", "add_only")
        if not target:
            raise SystemExit(f"entry {idx}: missing target")
        if is_protected(target):
            raise SystemExit(f"entry {idx}: protected target rejected: {target}")
        dst = safe_target(root, target)

        exists = dst.exists() or dst.is_symlink()
        if policy == "add_only" and exists:
            raise SystemExit(f"entry {idx}: add_only target already exists in ASUS rootfs: {target}")
        if policy != "add_only":
            raise SystemExit(f"entry {idx}: unsupported policy {policy!r}; only add_only is permitted")

        dst.parent.mkdir(parents=True, exist_ok=True)

        if etype == "copy":
            source = entry.get("source")
            expected = entry.get("sha256")
            source_kind = entry.get("source_kind", "merlin")
            if not source or not expected:
                raise SystemExit(f"entry {idx}: copy requires source and sha256")
            if source_kind == "merlin":
                src = safe_child(merlin, source, "Merlin source")
            elif source_kind == "repo":
                src = safe_child(repo, source, "repository source")
            else:
                raise SystemExit(f"entry {idx}: unsupported source_kind {source_kind!r}")
            if not src.is_file():
                raise SystemExit(f"entry {idx}: source not found: {source}")
            actual = sha256(src)
            if actual.lower() != str(expected).lower():
                raise SystemExit(
                    f"entry {idx}: source checksum mismatch for {source}\n"
                    f" expected {expected}\n actual   {actual}"
                )
            shutil.copyfile(src, dst)
            mode = parse_mode(entry.get("mode"))
            if mode is not None:
                os.chmod(dst, mode)
            rows.append((target, etype, source_kind, source, actual, policy))
        elif etype == "symlink":
            link_target = entry.get("link_target")
            if not link_target:
                raise SystemExit(f"entry {idx}: symlink requires link_target")
            os.symlink(link_target, dst)
            rows.append((target, etype, "symlink", link_target, "-", policy))
        else:
            raise SystemExit(f"entry {idx}: unsupported type {etype!r}")

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w", encoding="utf-8") as f:
        f.write("target\ttype\tsource_kind\tsource_or_link\tsha256\tpolicy\n")
        for row in rows:
            f.write("\t".join(row) + "\n")

    print(f"SUCCESS: applied {len(rows)} overlay entries")
    print(f"provenance report: {report}")

if __name__ == "__main__":
    main()
