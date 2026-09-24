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

def verify_hash(path: Path, expected: str, label: str):
    actual = sha256(path)
    if actual.lower() != str(expected).lower():
        raise SystemExit(
            f"{label} checksum mismatch\n expected {expected}\n actual   {actual}"
        )
    return actual

def main():
    ap = argparse.ArgumentParser(description="Apply hash-pinned additions/patches to an extracted ASUS 52334 rootfs")
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
        policy = entry.get("policy", "add_only" if etype in {"copy", "symlink"} else "exact_patch")
        if not target:
            raise SystemExit(f"entry {idx}: missing target")
        if is_protected(target):
            raise SystemExit(f"entry {idx}: protected target rejected: {target}")
        dst = safe_target(root, target)
        exists = dst.exists() or dst.is_symlink()

        if etype == "copy":
            if policy != "add_only":
                raise SystemExit(f"entry {idx}: copy only supports add_only")
            if exists:
                raise SystemExit(f"entry {idx}: add_only target already exists in ASUS rootfs: {target}")
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
            actual = verify_hash(src, expected, f"entry {idx}: source {source}")
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            mode = parse_mode(entry.get("mode"))
            if mode is not None:
                os.chmod(dst, mode)
            rows.append((target, etype, source_kind, source, "-", actual, policy))

        elif etype == "symlink":
            if policy != "add_only":
                raise SystemExit(f"entry {idx}: symlink only supports add_only")
            if exists:
                raise SystemExit(f"entry {idx}: add_only target already exists in ASUS rootfs: {target}")
            link_target = entry.get("link_target")
            if not link_target:
                raise SystemExit(f"entry {idx}: symlink requires link_target")
            dst.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(link_target, dst)
            rows.append((target, etype, "symlink", link_target, "-", "-", policy))

        elif etype == "patch_text":
            if policy != "exact_patch":
                raise SystemExit(f"entry {idx}: patch_text requires exact_patch policy")
            if not dst.is_file() or dst.is_symlink():
                raise SystemExit(f"entry {idx}: patch target must be an existing regular file: {target}")
            expected_base = entry.get("base_sha256")
            find = entry.get("find")
            replace = entry.get("replace")
            expected_count = entry.get("expected_count", 1)
            if not expected_base or find is None or replace is None:
                raise SystemExit(f"entry {idx}: patch_text requires base_sha256, find and replace")
            before = verify_hash(dst, expected_base, f"entry {idx}: ASUS base {target}")
            text = dst.read_text(encoding=entry.get("encoding", "utf-8"))
            count = text.count(find)
            if count != expected_count:
                raise SystemExit(
                    f"entry {idx}: patch context count mismatch for {target}: "
                    f"expected {expected_count}, found {count}"
                )
            patched = text.replace(find, replace, expected_count)
            dst.write_text(patched, encoding=entry.get("encoding", "utf-8"))
            after = sha256(dst)
            expected_result = entry.get("result_sha256")
            if expected_result and after.lower() != expected_result.lower():
                raise SystemExit(
                    f"entry {idx}: patched checksum mismatch for {target}\n"
                    f" expected {expected_result}\n actual   {after}"
                )
            rows.append((target, etype, "asus52334", "inline exact text patch", before, after, policy))

        else:
            raise SystemExit(f"entry {idx}: unsupported type {etype!r}")

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w", encoding="utf-8") as f:
        f.write("target\ttype\tsource_kind\tsource_or_patch\tbase_sha256\tresult_sha256\tpolicy\n")
        for row in rows:
            f.write("\t".join(row) + "\n")

    print(f"SUCCESS: applied {len(rows)} overlay entries")
    print(f"provenance report: {report}")

if __name__ == "__main__":
    main()
