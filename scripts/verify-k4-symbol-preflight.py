#!/usr/bin/env python3
"""Read-only host-side K4 symbol-name preflight for exact RT-AC86U modules.

This verifier never loads a module and never contacts the router.  It consumes:
  * a K4a read-only preflight archive containing /proc/kallsyms,
  * the exact preserved K2/K3 .ko files,
  * the exact schema-2 dependency-closure report.

A PASS proves that every strong undefined symbol not supplied by another
preserved optional module is at least present by name in the observed ASUS
386_52334 /proc/kallsyms snapshot.  It does not prove EXPORT_SYMBOL visibility,
CRC/modversions compatibility, or successful module loading.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath
from typing import Dict, Iterable, List, Set, Tuple

DEFAULT_SHA = "eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3"
EXPECTED_CLOSURE_RUN = 36972221014
EXPECTED_VERMAGIC = "4.1.27 SMP preempt mod_unload aarch64"

EXPECTED_MODULES = {
    "ip_set",
    "ip_set_bitmap_ip",
    "ip_set_bitmap_ipmac",
    "ip_set_bitmap_port",
    "ip_set_hash_ip",
    "ip_set_hash_ipmac",
    "ip_set_hash_ipmark",
    "ip_set_hash_ipport",
    "ip_set_hash_ipportip",
    "ip_set_hash_ipportnet",
    "ip_set_hash_mac",
    "ip_set_hash_net",
    "ip_set_hash_netiface",
    "ip_set_hash_netnet",
    "ip_set_hash_netport",
    "ip_set_hash_netportnet",
    "ip_set_list_set",
    "xt_set",
    "sunrpc",
    "lockd",
    "nfs",
    "nfsv2",
    "nfsv3",
    "nfsd",
    "cifs",
    "sch_cake",
    "wireguard",
}

# Independent pins already enforced by the preservation workflow.  The closure
# report supplies hashes for all 27 files; these pins ensure the report itself
# also identifies the intended project artifacts rather than an arbitrary set.
REPRESENTATIVE_HASHES = {
    "ip_set": "19c47ab22f38c50e3ddfea153e54c10e4c4ecb244fe1fa77e225c0bca94162b6",
    "ip_set_hash_ip": "e1179e36ebad16843537338fae3134f75c672161a1702f518a64cebeab1cb93d",
    "ip_set_list_set": "060bce188e4f4ac42064e4c9774f637dcee84b0cea5bb0d3e858a0ae28464cf5",
    "xt_set": "6ed89a951afdabf5b93158d7ef8edc0c7804b51df0c98f3f8c64500a47fb0b3a",
    "sunrpc": "b547166600f2e2c0b6ff7356010b7eeec509139b928cc01236e8cba2820b1241",
    "nfs": "82f8a84767334ab49a032f5b96f59960cd4e207336b9b8995c9442947631bf5d",
    "nfsd": "953d838733e9ab740980ecd5f0a5c76ddbcfafef8c0af1621171551406a8a293",
    "cifs": "eb545f7ce5429477f081ef0c4d1c5d1b8eca519d9025afdc2a225417417567b8",
    "sch_cake": "159256eb407a76d0ac38b53c3eea36ef74d054b1afe60329a61aad0e5024f24c",
    "wireguard": "418f6e212f4d8f3f83142352f462fd870b591602f45b8af0564ecd72c7e5161c",
}


class GateError(RuntimeError):
    pass


def normalize_module(name: str) -> str:
    return name.replace("-", "_")


def safe_member_name(name: str) -> bool:
    if not name or name.startswith("/"):
        return False
    p = PurePosixPath(name)
    if ".." in p.parts:
        return False
    return posixpath.normpath(name) == name.rstrip("/")


def read_k4_archive(path: Path, expected_sha: str) -> Tuple[Dict[str, str], Set[str]]:
    try:
        tf = tarfile.open(path, mode="r:*")
    except (OSError, tarfile.TarError) as exc:
        raise GateError(f"K4a: cannot open {path}: {exc}") from exc

    root = "rtac86u-k4-preflight"
    try:
        members: Dict[str, tarfile.TarInfo] = {}
        for info in tf.getmembers():
            name = info.name.rstrip("/")
            if not safe_member_name(name):
                raise GateError(f"K4a: unsafe archive path {info.name!r}")
            if info.issym() or info.islnk() or info.isdev() or info.isfifo():
                raise GateError(f"K4a: unsupported archive member type {info.name!r}")
            if name != root and not name.startswith(root + "/"):
                raise GateError(f"K4a: member outside expected root: {info.name!r}")
            members[name] = info

        if root not in members or not members[root].isdir():
            raise GateError("K4a: missing top-level rtac86u-k4-preflight directory")

        def text(rel: str, limit: int) -> str:
            key = f"{root}/{rel}"
            info = members.get(key)
            if info is None or not info.isfile():
                raise GateError(f"K4a: missing regular file {rel}")
            if info.size > limit:
                raise GateError(f"K4a: {rel} unexpectedly large ({info.size} bytes)")
            fh = tf.extractfile(info)
            if fh is None:
                raise GateError(f"K4a: cannot read {rel}")
            data = fh.read(limit + 1)
            if len(data) > limit:
                raise GateError(f"K4a: {rel} exceeds read limit")
            return data.decode("utf-8", errors="replace")

        summary_text = text("summary.txt", 256 * 1024)
        lines = summary_text.splitlines()
        if not lines or lines[0].strip() != "K4A_RTAC86U_52334_READ_ONLY_PREFLIGHT":
            raise GateError("K4a: summary magic mismatch")
        summary: Dict[str, str] = {}
        for line in lines[1:]:
            if "=" in line:
                k, v = line.split("=", 1)
                summary[k.strip()] = v.strip()

        required_identity = {
            "expected_candidate_sha256": expected_sha,
            "productid": "RT-AC86U",
            "buildno": "386",
            "uname_m": "aarch64",
        }
        for key, want in required_identity.items():
            if summary.get(key) != want:
                raise GateError(f"K4a: {key}={summary.get(key)!r}, expected {want!r}")
        if not summary.get("firmver", "").startswith("3.0.0.4"):
            raise GateError(f"K4a: unexpected firmver {summary.get('firmver')!r}")
        extendno = summary.get("extendno", "")
        if "52334" not in extendno or "merlin" in extendno.lower() or "386.14" in extendno.lower():
            raise GateError(f"K4a: invalid ASUS-52334 runtime identity {extendno!r}")
        if not summary.get("uname_r"):
            raise GateError("K4a: missing kernel release")

        safety_text = text("safety.txt", 64 * 1024)
        safety = {}
        for line in safety_text.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                safety[k.strip()] = v.strip()
        for key in (
            "NO_MODULES_LOADED",
            "NO_NVRAM_WRITES",
            "NO_JFFS_WRITES",
            "NO_SERVICE_RESTARTS",
            "NO_REBOOT",
            "NO_FLASH_WRITES",
        ):
            if safety.get(key) != "1":
                raise GateError(f"K4a: missing safety marker {key}=1")

        kallsyms_text = text("proc-kallsyms.txt", 64 * 1024 * 1024)
        if kallsyms_text.startswith("UNAVAILABLE"):
            raise GateError("K4a: /proc/kallsyms unavailable")
        symbols: Set[str] = set()
        for line in kallsyms_text.splitlines():
            parts = line.split()
            if len(parts) >= 3:
                symbols.add(parts[2])
        if not symbols:
            raise GateError("K4a: no symbol names parsed from /proc/kallsyms")
        return summary, symbols
    finally:
        tf.close()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def readelf_symbols(path: Path) -> Tuple[Set[str], Set[str], Set[str]]:
    try:
        cp = subprocess.run(
            ["readelf", "-Ws", str(path)],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise GateError("host readelf is required (install binutils)") from exc
    if cp.returncode:
        raise GateError(f"readelf failed for {path}: {cp.stderr.strip()}")

    strong_undefined: Set[str] = set()
    weak_undefined: Set[str] = set()
    exports: Set[str] = set()
    for line in cp.stdout.splitlines():
        parts = line.split()
        if len(parts) < 8 or not parts[0].rstrip(":").isdigit():
            continue
        bind = parts[4]
        ndx = parts[6]
        name = parts[7].split("@", 1)[0]
        if ndx == "UND" and name:
            if bind == "WEAK":
                weak_undefined.add(name)
            else:
                strong_undefined.add(name)
        if name.startswith("__ksymtab_"):
            exports.add(name[len("__ksymtab_") :])
    return strong_undefined, weak_undefined, exports


def require_aarch64(path: Path) -> None:
    cp = subprocess.run(
        ["readelf", "-h", str(path)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if cp.returncode or "Machine:" not in cp.stdout or "AArch64" not in cp.stdout:
        raise GateError(f"{path}: expected AArch64 ELF module")


def load_closure(path: Path, profile: str) -> dict:
    if not path.is_file():
        raise GateError(f"closure report not found: {path}")
    if path.stat().st_size > 16 * 1024 * 1024:
        raise GateError("closure report unexpectedly large")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GateError(f"cannot parse closure report: {exc}") from exc
    if data.get("schema") != 2:
        raise GateError(f"closure schema={data.get('schema')!r}, expected 2")
    if profile == "project" and data.get("source_preservation_run") != EXPECTED_CLOSURE_RUN:
        raise GateError(
            f"closure source run={data.get('source_preservation_run')!r}, "
            f"expected {EXPECTED_CLOSURE_RUN}"
        )
    if not isinstance(data.get("modules"), dict):
        raise GateError("closure report missing modules object")
    return data


def discover_modules(root: Path) -> Dict[str, Path]:
    if not root.is_dir():
        raise GateError(f"module root not found: {root}")
    result: Dict[str, Path] = {}
    for p in sorted(root.rglob("*.ko")):
        name = normalize_module(p.stem)
        if name in result:
            raise GateError(f"duplicate module name {name}: {result[name]} and {p}")
        result[name] = p
    if not result:
        raise GateError(f"no .ko files found below {root}")
    return result


def validate_modules(module_paths: Dict[str, Path], closure: dict, profile: str) -> dict:
    rows: dict = closure["modules"]
    closure_names = set(rows)
    actual_names = set(module_paths)
    if actual_names != closure_names:
        raise GateError(
            "module set differs from closure report: "
            f"missing={sorted(closure_names-actual_names)} "
            f"extra={sorted(actual_names-closure_names)}"
        )
    if profile == "project" and actual_names != EXPECTED_MODULES:
        raise GateError(
            "project module set mismatch: "
            f"missing={sorted(EXPECTED_MODULES-actual_names)} "
            f"extra={sorted(actual_names-EXPECTED_MODULES)}"
        )

    actual: dict = {}
    for name, p in module_paths.items():
        row = rows.get(name)
        if not isinstance(row, dict):
            raise GateError(f"closure row missing for {name}")
        got_hash = sha256_file(p)
        want_hash = str(row.get("sha256", "")).lower()
        if got_hash != want_hash:
            raise GateError(f"{name}: SHA-256 mismatch {got_hash} != {want_hash}")
        if profile == "project":
            if row.get("vermagic") != EXPECTED_VERMAGIC:
                raise GateError(
                    f"{name}: closure vermagic={row.get('vermagic')!r}, "
                    f"expected {EXPECTED_VERMAGIC!r}"
                )
            require_aarch64(p)

        strong, weak, exports = readelf_symbols(p)
        recorded_undef = set(row.get("undefined_symbols") or [])
        recorded_exports = set(row.get("exported_symbols") or [])
        if strong | weak != recorded_undef:
            raise GateError(f"{name}: undefined-symbol set differs from closure report")
        if exports != recorded_exports:
            raise GateError(f"{name}: exported-symbol set differs from closure report")

        actual[name] = {
            "sha256": got_hash,
            "strong_undefined": strong,
            "weak_undefined": weak,
            "exports": exports,
        }

    if profile == "project":
        for name, want in REPRESENTATIVE_HASHES.items():
            if actual[name]["sha256"] != want:
                raise GateError(
                    f"{name}: representative project pin mismatch "
                    f"{actual[name]['sha256']} != {want}"
                )
    return actual


def evaluate_symbols(actual: dict, closure: dict, kallsyms: Set[str]) -> dict:
    exporters: Dict[str, List[str]] = {}
    for mod, row in actual.items():
        for sym in row["exports"]:
            exporters.setdefault(sym, []).append(mod)

    missing: Dict[str, List[str]] = {}
    weak_missing: Dict[str, List[str]] = {}
    internal: Dict[str, Dict[str, List[str]]] = {}
    required_kernel: Dict[str, List[str]] = {}

    for mod, row in actual.items():
        provided_by_optional: Dict[str, List[str]] = {}
        kernel_required: List[str] = []
        for sym in sorted(row["strong_undefined"]):
            owners = [x for x in exporters.get(sym, []) if x != mod]
            if len(owners) > 1:
                raise GateError(f"{mod}: ambiguous optional providers for {sym}: {owners}")
            if owners:
                provided_by_optional.setdefault(owners[0], []).append(sym)
            else:
                kernel_required.append(sym)

        # Ensure the freshly derived optional-module graph agrees with the
        # preserved closure report generated from these exact hashes.
        derived_deps = sorted(provided_by_optional)
        recorded_deps = sorted((closure["modules"][mod].get("symbol_internal_depends") or []))
        if derived_deps != recorded_deps:
            raise GateError(
                f"{mod}: fresh internal deps {derived_deps} != closure {recorded_deps}"
            )

        internal[mod] = provided_by_optional
        required_kernel[mod] = kernel_required
        absent = [sym for sym in kernel_required if sym not in kallsyms]
        if absent:
            missing[mod] = absent

        weak_absent = []
        for sym in sorted(row["weak_undefined"]):
            owners = [x for x in exporters.get(sym, []) if x != mod]
            if not owners and sym not in kallsyms:
                weak_absent.append(sym)
        if weak_absent:
            weak_missing[mod] = weak_absent

    return {
        "internal_symbol_dependencies": internal,
        "kernel_required_symbols": required_kernel,
        "missing_strong_symbols": missing,
        "missing_weak_symbols": weak_missing,
    }


def jsonable(value):
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [jsonable(v) for v in value]
    return value


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k4", required=True, help="K4a preflight tar/tar.gz")
    ap.add_argument("--modules-root", required=True, help="directory containing exact K2/K3 .ko files")
    ap.add_argument("--closure", required=True, help="schema-2 K4 dependency closure JSON")
    ap.add_argument("--expected-sha", default=DEFAULT_SHA)
    ap.add_argument("--report", help="optional JSON report output path")
    ap.add_argument(
        "--profile",
        choices=("project", "fixture"),
        default="project",
        help="project enforces RT-AC86U exact module set, pins and AArch64; fixture is CI-only",
    )
    ns = ap.parse_args()

    if len(ns.expected_sha) != 64 or any(c not in "0123456789abcdef" for c in ns.expected_sha):
        print("K4_SYMBOL_PREFLIGHT_FAIL: invalid expected SHA-256", file=sys.stderr)
        return 2

    try:
        summary, kallsyms = read_k4_archive(Path(ns.k4), ns.expected_sha)
        closure = load_closure(Path(ns.closure), ns.profile)
        paths = discover_modules(Path(ns.modules_root))
        actual = validate_modules(paths, closure, ns.profile)
        result = evaluate_symbols(actual, closure, kallsyms)

        if result["missing_strong_symbols"]:
            details = "; ".join(
                f"{mod}: {','.join(symbols)}"
                for mod, symbols in sorted(result["missing_strong_symbols"].items())
            )
            raise GateError(f"required strong symbols absent from K4a kallsyms: {details}")

        report = {
            "status": "PASS",
            "classification": (
                "RTAC86U_52334_K4_SYMBOL_NAME_PREFLIGHT"
                if ns.profile == "project"
                else "TEST_FIXTURE_K4_SYMBOL_NAME_PREFLIGHT"
            ),
            "candidate_sha256": ns.expected_sha,
            "productid": summary["productid"],
            "firmver": summary["firmver"],
            "buildno": summary["buildno"],
            "extendno": summary["extendno"],
            "kernel_release": summary["uname_r"],
            "architecture": summary["uname_m"],
            "closure_source_preservation_run": closure.get("source_preservation_run"),
            "module_count": len(actual),
            "kallsyms_name_count": len(kallsyms),
            "modules": {
                name: {
                    "sha256": row["sha256"],
                    "strong_undefined_count": len(row["strong_undefined"]),
                    "weak_undefined_count": len(row["weak_undefined"]),
                    "exported_symbol_count": len(row["exports"]),
                }
                for name, row in sorted(actual.items())
            },
            "symbol_evaluation": jsonable(result),
            "limitations": [
                "PASS proves required strong symbol names are present in the observed ASUS 386_52334 /proc/kallsyms snapshot or supplied by another exact optional module.",
                "PASS does not prove that a name visible in /proc/kallsyms is exported to loadable modules.",
                "PASS does not prove MODVERSIONS/CRC, relocation, vermagic acceptance, HND stability, or successful module loading.",
                "Weak undefined symbols are reported but do not fail this name-presence gate.",
                "Physical K4 load/function/unload testing remains mandatory and mutating.",
            ],
        }
        payload = json.dumps(report, indent=2, sort_keys=True)
        if ns.report:
            Path(ns.report).write_text(payload + "\n", encoding="utf-8")
        print(payload)
        print(
            "K4_SYMBOL_PREFLIGHT_PASS"
            if ns.profile == "project"
            else "K4_SYMBOL_PREFLIGHT_FIXTURE_PASS"
        )
        return 0
    except (GateError, OSError) as exc:
        print(f"K4_SYMBOL_PREFLIGHT_FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
