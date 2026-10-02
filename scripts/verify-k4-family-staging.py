#!/usr/bin/env python3
"""Fail-closed host-side verifier/preparer for RT-AC86U K4 family staging bundles.

This tool never contacts the router and never loads modules. It verifies the exact
five-family staging artifact produced by run 36978077020, validates the selected
family archive and manifest, and optionally extracts exactly one family into a
clean host staging directory for later operator-controlled transfer to /tmp.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import sys
import tarfile
from pathlib import Path, PurePosixPath
from typing import Dict

CANDIDATE_SHA = "eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3"
SOURCE_HARDWARE_BUNDLE_RUN = "36977559328"
DEPENDENCY_CLOSURE_RUN = "36976006891"
CLASSIFICATION = "K4_TEMPORARY_FAMILY_STAGING_ONLY"

OUTER_HASHES = {
    "cake": "bb913852f80d5efefcbc239ac7cde59d3e5513877b008e43d62dbbf46ed2d6e1",
    "cifs": "f96d734380bd496d60693b6d988306d08a923090c83a752da5961a825608f39d",
    "ipset": "a7278bc3f066d3a7a9a90ceaf522e93cda516686ad613d7054d2fa6419ef8231",
    "nfs": "55d7ba79c7af476f8e81f907cbfab5ec28904484f9973c25b467ee1ae9532520",
    "wireguard": "19676e3e6dfa508b54d1ab9a137b42a5feda2c9e97b1f59df7d310f5c6d0cdda",
}

SPECS = {
    "ipset": {
        "load_order": "ip_set,ip_set_hash_ip,xt_set",
        "unload_order": "xt_set,ip_set_hash_ip,ip_set",
        "files": {
            "modules/ip_set.ko": "19c47ab22f38c50e3ddfea153e54c10e4c4ecb244fe1fa77e225c0bca94162b6",
            "modules/ip_set_hash_ip.ko": "e1179e36ebad16843537338fae3134f75c672161a1702f518a64cebeab1cb93d",
            "modules/xt_set.ko": "6ed89a951afdabf5b93158d7ef8edc0c7804b51df0c98f3f8c64500a47fb0b3a",
            "userspace/k4-ipset-userspace-51997.tar.gz": "82bc1421ee8a680b13540484b468485f0395ffab5f337450030606387b08be11",
        },
    },
    "cake": {
        "load_order": "sch_cake",
        "unload_order": "sch_cake",
        "files": {
            "modules/sch_cake.ko": "159256eb407a76d0ac38b53c3eea36ef74d054b1afe60329a61aad0e5024f24c",
            "userspace/k4-cake-userspace-51997.tar.gz": "d21d124541eb0eac6fec4cc12418aaf6a364cb820201b8af3c8703cf7a6e2b51",
        },
    },
    "cifs": {
        "load_order": "cifs",
        "unload_order": "cifs",
        "files": {
            "modules/cifs.ko": "eb545f7ce5429477f081ef0c4d1c5d1b8eca519d9025afdc2a225417417567b8",
        },
    },
    "nfs": {
        "load_order": "sunrpc,lockd,nfs,nfsd,nfsv2,nfsv3",
        "unload_order": "nfsv3,nfsv2,nfsd,nfs,lockd,sunrpc",
        "files": {
            "modules/sunrpc.ko": "b547166600f2e2c0b6ff7356010b7eeec509139b928cc01236e8cba2820b1241",
            "modules/lockd.ko": "430a049f733730b18ed13b7fb0c1dafb8e01317ee0dc27d49805001974394b67",
            "modules/nfs.ko": "82f8a84767334ab49a032f5b96f59960cd4e207336b9b8995c9442947631bf5d",
            "modules/nfsd.ko": "953d838733e9ab740980ecd5f0a5c76ddbcfafef8c0af1621171551406a8a293",
            "modules/nfsv2.ko": "04522f79ed0051682df41b670d0fee4deb8bcec2ba36023f20964d5e17dd688c",
            "modules/nfsv3.ko": "7a7b1448126e265d40c7fe8bb7ecbe866b2b3238b8238a005097d264f0b891e3",
        },
    },
    "wireguard": {
        "load_order": "wireguard",
        "unload_order": "wireguard",
        "files": {
            "modules/wireguard.ko": "418f6e212f4d8f3f83142352f462fd870b591602f45b8af0564ecd72c7e5161c",
            "userspace/k4-wireguard-userspace-51997.tar.gz": "ad29adf9a84fa1752f6dfe7caa147c7eb158e10c8ce4902ac3bc4dd95106aa3a",
        },
    },
}


class GateError(RuntimeError):
    pass


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_member_name(name: str) -> bool:
    if not name or name.startswith("/"):
        return False
    p = PurePosixPath(name)
    if ".." in p.parts:
        return False
    return posixpath.normpath(name) == name.rstrip("/")


def parse_outer_manifest(root: Path) -> Dict[str, str]:
    manifest = root / "package-sha256.txt"
    if not manifest.is_file():
        raise GateError("missing package-sha256.txt")
    if manifest.stat().st_size > 32 * 1024:
        raise GateError("package-sha256.txt unexpectedly large")
    rows: Dict[str, str] = {}
    pat = re.compile(r"^([0-9a-f]{64})  (k4-family-([a-z0-9_-]+)\\.tar\\.gz)$")
    for raw in manifest.read_text(encoding="utf-8").splitlines():
        if not raw:
            continue
        m = pat.fullmatch(raw)
        if not m:
            raise GateError(f"invalid outer checksum line: {raw!r}")
        digest, filename, family = m.groups()
        if family in rows:
            raise GateError(f"duplicate outer checksum for {family}")
        if family not in OUTER_HASHES:
            raise GateError(f"unexpected family in outer checksum file: {family}")
        if digest != OUTER_HASHES[family]:
            raise GateError(f"{family}: outer checksum does not match pinned artifact")
        if filename != f"k4-family-{family}.tar.gz":
            raise GateError(f"{family}: unexpected archive name {filename}")
        rows[family] = digest
    if set(rows) != set(OUTER_HASHES):
        raise GateError(f"outer checksum family set mismatch: {sorted(rows)}")

    expected_names = {"package-sha256.txt"} | {f"k4-family-{f}.tar.gz" for f in OUTER_HASHES}
    actual_names = {p.name for p in root.iterdir() if p.is_file()}
    if actual_names != expected_names:
        raise GateError(
            f"package directory file set mismatch: missing={sorted(expected_names-actual_names)} "
            f"extra={sorted(actual_names-expected_names)}"
        )
    for family, want in rows.items():
        archive = root / f"k4-family-{family}.tar.gz"
        got = sha256_path(archive)
        if got != want:
            raise GateError(f"{family}: archive SHA-256 mismatch {got} != {want}")
    return rows


def read_selected_archive(path: Path, family: str) -> tuple[tarfile.TarFile, Dict[str, tarfile.TarInfo], str]:
    try:
        tf = tarfile.open(path, mode="r:gz")
    except (OSError, tarfile.TarError) as exc:
        raise GateError(f"cannot open {path}: {exc}") from exc

    root = family
    members: Dict[str, tarfile.TarInfo] = {}
    try:
        for info in tf.getmembers():
            name = info.name.rstrip("/")
            if not safe_member_name(name):
                raise GateError(f"unsafe archive path {info.name!r}")
            if info.issym() or info.islnk() or info.isdev() or info.isfifo():
                raise GateError(f"unsupported archive member type {info.name!r}")
            if not (info.isdir() or info.isfile()):
                raise GateError(f"unsupported archive member {info.name!r}")
            if name != root and not name.startswith(root + "/"):
                raise GateError(f"member outside expected family root: {info.name!r}")
            if name in members:
                raise GateError(f"duplicate archive member {name!r}")
            members[name] = info
        if root not in members or not members[root].isdir():
            raise GateError(f"missing top-level {root}/ directory")
        manifest_name = f"{root}/MANIFEST.txt"
        info = members.get(manifest_name)
        if info is None or not info.isfile():
            raise GateError("missing family MANIFEST.txt")
        if info.size > 64 * 1024:
            raise GateError("family MANIFEST.txt unexpectedly large")
        fh = tf.extractfile(info)
        if fh is None:
            raise GateError("cannot read family MANIFEST.txt")
        text = fh.read(64 * 1024 + 1).decode("utf-8")
        if len(text.encode("utf-8")) > 64 * 1024:
            raise GateError("family MANIFEST.txt exceeds read limit")
        return tf, members, text
    except Exception:
        tf.close()
        raise


def parse_family_manifest(text: str, family: str) -> Dict[str, str]:
    spec = SPECS[family]
    lines = text.splitlines()
    try:
        split = lines.index("===== FILE SHA256 =====")
    except ValueError as exc:
        raise GateError("family manifest missing checksum section") from exc
    meta: Dict[str, str] = {}
    for line in lines[:split]:
        if not line:
            continue
        if "=" not in line:
            raise GateError(f"invalid family metadata line: {line!r}")
        key, value = line.split("=", 1)
        if key in meta:
            raise GateError(f"duplicate family metadata key {key}")
        meta[key] = value
    expected_meta = {
        "classification": CLASSIFICATION,
        "candidate_sha256": CANDIDATE_SHA,
        "source_hardware_bundle_run": SOURCE_HARDWARE_BUNDLE_RUN,
        "dependency_closure_run": DEPENDENCY_CLOSURE_RUN,
        "family": family,
        "load_order": spec["load_order"],
        "unload_order": spec["unload_order"],
    }
    if meta != expected_meta:
        raise GateError(f"family metadata mismatch: got={meta!r}")

    hashes: Dict[str, str] = {}
    pat = re.compile(r"^([0-9a-f]{64})  (modules|userspace)/([^/]+)$")
    for line in lines[split + 1 :]:
        if not line:
            continue
        m = pat.fullmatch(line)
        if not m:
            raise GateError(f"invalid family checksum line: {line!r}")
        digest, directory, basename = m.groups()
        rel = f"{directory}/{basename}"
        if rel in hashes:
            raise GateError(f"duplicate family checksum for {rel}")
        hashes[rel] = digest
    expected_files: Dict[str, str] = spec["files"]  # type: ignore[assignment]
    if hashes != expected_files:
        raise GateError(f"family checksum inventory mismatch: got={hashes!r}")
    return hashes


def verify_archive_members(tf: tarfile.TarFile, members: Dict[str, tarfile.TarInfo], family: str, hashes: Dict[str, str]) -> None:
    expected_files = {f"{family}/MANIFEST.txt"} | {f"{family}/{rel}" for rel in hashes}
    actual_files = {name for name, info in members.items() if info.isfile()}
    if actual_files != expected_files:
        raise GateError(
            f"family archive file set mismatch: missing={sorted(expected_files-actual_files)} "
            f"extra={sorted(actual_files-expected_files)}"
        )
    expected_dirs = {family, f"{family}/modules", f"{family}/userspace"}
    actual_dirs = {name for name, info in members.items() if info.isdir()}
    if actual_dirs != expected_dirs:
        raise GateError(
            f"family archive directory set mismatch: missing={sorted(expected_dirs-actual_dirs)} "
            f"extra={sorted(actual_dirs-expected_dirs)}"
        )
    for rel, want in hashes.items():
        name = f"{family}/{rel}"
        info = members[name]
        fh = tf.extractfile(info)
        if fh is None:
            raise GateError(f"cannot read {name}")
        h = hashlib.sha256()
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
        got = h.hexdigest()
        if got != want:
            raise GateError(f"{rel}: SHA-256 mismatch {got} != {want}")


def extract_verified(tf: tarfile.TarFile, members: Dict[str, tarfile.TarInfo], family: str, output: Path) -> Path:
    if output.exists():
        if not output.is_dir():
            raise GateError(f"output exists and is not a directory: {output}")
        if any(output.iterdir()):
            raise GateError(f"output directory is not empty: {output}")
    else:
        output.mkdir(parents=True, mode=0o700)

    for name in sorted(members):
        info = members[name]
        target = output / Path(*PurePosixPath(name).parts)
        if info.isdir():
            target.mkdir(parents=True, exist_ok=True)
            os.chmod(target, info.mode & 0o777)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        fh = tf.extractfile(info)
        if fh is None:
            raise GateError(f"cannot extract {name}")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        fd = os.open(target, flags, info.mode & 0o777)
        try:
            with os.fdopen(fd, "wb", closefd=False) as out:
                for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                    out.write(chunk)
        finally:
            os.close(fd)
    return output / family


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packages-root", required=True, help="directory containing package-sha256.txt and all five family tarballs")
    ap.add_argument("--family", required=True, choices=sorted(SPECS))
    ap.add_argument("--output", help="clean host directory to receive the verified selected family")
    ap.add_argument("--report", help="optional JSON report path")
    ns = ap.parse_args()

    root = Path(ns.packages_root)
    family = ns.family
    try:
        if not root.is_dir():
            raise GateError(f"packages root not found: {root}")
        rows = parse_outer_manifest(root)
        archive = root / f"k4-family-{family}.tar.gz"
        tf, members, manifest_text = read_selected_archive(archive, family)
        try:
            hashes = parse_family_manifest(manifest_text, family)
            verify_archive_members(tf, members, family, hashes)
            staged = None
            if ns.output:
                staged = extract_verified(tf, members, family, Path(ns.output))
        finally:
            tf.close()

        report = {
            "status": "PASS",
            "classification": "RTAC86U_52334_K4_FAMILY_STAGING",
            "candidate_sha256": CANDIDATE_SHA,
            "family": family,
            "archive": archive.name,
            "archive_sha256": rows[family],
            "source_hardware_bundle_run": int(SOURCE_HARDWARE_BUNDLE_RUN),
            "dependency_closure_run": int(DEPENDENCY_CLOSURE_RUN),
            "load_order": SPECS[family]["load_order"].split(","),
            "unload_order": SPECS[family]["unload_order"].split(","),
            "files": hashes,
            "staged_path": str(staged) if staged else None,
            "limitations": [
                "PASS verifies only the exact preserved family package and host-side staging content.",
                "PASS does not verify target-kernel symbols, module loadability, runtime stability, or feature behavior.",
                "A fresh ASUS-52334 K4a archive and K4_SYMBOL_PREFLIGHT_PASS remain mandatory before any module load.",
                "Only this selected family may be copied to router /tmp; the full 27-module host analysis set must not be staged on the router.",
            ],
        }
        payload = json.dumps(report, indent=2, sort_keys=True)
        if ns.report:
            Path(ns.report).write_text(payload + "\n", encoding="utf-8")
        print(payload)
        print(f"K4_FAMILY_STAGING_PASS family={family}")
        return 0
    except (GateError, OSError, UnicodeError, tarfile.TarError) as exc:
        print(f"K4_FAMILY_STAGING_FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
