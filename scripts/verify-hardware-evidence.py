#!/usr/bin/env python3
"""Fail-closed host-side verifier for RT-AC86U physical evidence archives."""

from __future__ import annotations

import argparse
import json
import posixpath
import sys
import tarfile
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Dict, Iterable

DEFAULT_SHA = "eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3"

CANDIDATE_CANARIES = {
    "/usr/sbin/helper.sh": "f4f19dd4e0437869d476e37d9b74b0bf75690886941bd00c0079eb1425dd0bba",
    "/www/Tools_OtherSettings.asp": "16b6d409b90fe2319adbf62f42b54f0027dddf94913402eba5cd36d955e99d56",
    "/www/Advanced_Wireless_Survey.asp": "a4d4391781bd9a1cb8c0d93cb6f0abca1b1d7f96809231ecdd233394a931fe9a",
    "/www/js/qrcode.min.js": "7f5a45e2791b3ef6cde1a34a253711b7510ad7c6136d20fc91404b48f744647b",
    "/www/ajax/logFilter.json": "a6e28e7be5b00799f4492ab99baba31e9a9255ffd3e62bbb276270f5645c04f3",
}


class EvidenceError(RuntimeError):
    pass


@dataclass
class ArchiveView:
    kind: str
    root: str
    members: Dict[str, tarfile.TarInfo]
    tar: tarfile.TarFile

    def member(self, rel: str) -> tarfile.TarInfo:
        name = f"{self.root}/{rel}"
        try:
            return self.members[name]
        except KeyError as exc:
            raise EvidenceError(f"{self.kind}: missing required file {rel}") from exc

    def read_text(self, rel: str, limit: int = 1024 * 1024) -> str:
        info = self.member(rel)
        if not info.isfile():
            raise EvidenceError(f"{self.kind}: {rel} is not a regular file")
        if info.size > limit:
            raise EvidenceError(f"{self.kind}: {rel} unexpectedly large ({info.size} bytes)")
        fh = self.tar.extractfile(info)
        if fh is None:
            raise EvidenceError(f"{self.kind}: cannot read {rel}")
        data = fh.read(limit + 1)
        if len(data) > limit:
            raise EvidenceError(f"{self.kind}: {rel} exceeds read limit")
        return data.decode("utf-8", errors="replace")

    def require_regular(self, rel: str, *, nonempty: bool = True) -> tarfile.TarInfo:
        info = self.member(rel)
        if not info.isfile():
            raise EvidenceError(f"{self.kind}: {rel} is not a regular file")
        if nonempty and info.size == 0:
            raise EvidenceError(f"{self.kind}: {rel} is empty")
        return info


def safe_member_name(name: str) -> bool:
    if not name or name.startswith("/"):
        return False
    p = PurePosixPath(name)
    if ".." in p.parts:
        return False
    return posixpath.normpath(name) == name.rstrip("/")


def open_archive(path: str, kind: str, expected_root: str) -> ArchiveView:
    try:
        tf = tarfile.open(path, mode="r:*")
    except (tarfile.TarError, OSError) as exc:
        raise EvidenceError(f"{kind}: cannot open archive {path}: {exc}") from exc

    members: Dict[str, tarfile.TarInfo] = {}
    for info in tf.getmembers():
        name = info.name.rstrip("/")
        if not safe_member_name(name):
            tf.close()
            raise EvidenceError(f"{kind}: unsafe archive path {info.name!r}")
        if info.issym() or info.islnk() or info.isdev() or info.isfifo():
            tf.close()
            raise EvidenceError(f"{kind}: unsupported archive member type: {info.name}")
        if name != expected_root and not name.startswith(expected_root + "/"):
            tf.close()
            raise EvidenceError(
                f"{kind}: member outside expected root {expected_root!r}: {info.name}"
            )
        members[name] = info

    if expected_root not in members or not members[expected_root].isdir():
        tf.close()
        raise EvidenceError(f"{kind}: missing top-level directory {expected_root}")

    return ArchiveView(kind, expected_root, members, tf)


def parse_key_values(text: str, magic: str, kind: str) -> Dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != magic:
        raise EvidenceError(f"{kind}: summary magic mismatch")
    values: Dict[str, str] = {}
    for line in lines[1:]:
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def require_equal(values: Dict[str, str], key: str, want: str, kind: str) -> None:
    got = values.get(key, "")
    if got != want:
        raise EvidenceError(f"{kind}: {key}={got!r}, expected {want!r}")


def validate_identity(values: Dict[str, str], kind: str, expected_sha: str) -> None:
    require_equal(values, "expected_candidate_sha256", expected_sha, kind)
    require_equal(values, "productid", "RT-AC86U", kind)

    firmver = values.get("firmver", "")
    buildno = values.get("buildno", "")
    extendno = values.get("extendno", "")
    if not firmver.startswith("3.0.0.4"):
        raise EvidenceError(f"{kind}: unexpected firmver {firmver!r}")
    if buildno != "386":
        raise EvidenceError(f"{kind}: unexpected buildno {buildno!r}")
    if "52334" not in extendno:
        raise EvidenceError(
            f"{kind}: extendno does not identify ASUS 386_52334: {extendno!r}"
        )
    if "merlin" in extendno.lower() or "386.14" in extendno.lower():
        raise EvidenceError(f"{kind}: Merlin-like extendno rejected: {extendno!r}")


def validate_safety(view: ArchiveView, required: Iterable[str]) -> None:
    text = view.read_text("safety.txt", limit=64 * 1024)
    got = {}
    for line in text.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            got[k.strip()] = v.strip()
    for key in required:
        if got.get(key) != "1":
            raise EvidenceError(f"{view.kind}: missing safety marker {key}=1")


def validate_k4(view: ArchiveView, expected_sha: str) -> Dict[str, str]:
    for rel in (
        "summary.txt",
        "safety.txt",
        "proc-modules.txt",
        "proc-kallsyms.txt",
        "dmesg-before.txt",
        "module-tree.txt",
        "stock-module-vermagic.txt",
    ):
        view.require_regular(rel, nonempty=rel not in {"proc-modules.txt", "module-tree.txt", "stock-module-vermagic.txt"})

    summary = parse_key_values(
        view.read_text("summary.txt", limit=256 * 1024),
        "K4A_RTAC86U_52334_READ_ONLY_PREFLIGHT",
        view.kind,
    )
    validate_identity(summary, view.kind, expected_sha)

    if summary.get("uname_m") != "aarch64":
        raise EvidenceError(f"{view.kind}: uname_m must be aarch64")
    if not summary.get("uname_r"):
        raise EvidenceError(f"{view.kind}: missing uname_r")

    kallsyms = view.read_text("proc-kallsyms.txt", limit=32 * 1024 * 1024)
    if kallsyms.startswith("UNAVAILABLE"):
        raise EvidenceError(f"{view.kind}: /proc/kallsyms unavailable")
    dmesg = view.read_text("dmesg-before.txt", limit=32 * 1024 * 1024)
    if dmesg.startswith("UNAVAILABLE"):
        raise EvidenceError(f"{view.kind}: dmesg unavailable")

    validate_safety(
        view,
        (
            "NO_MODULES_LOADED",
            "NO_NVRAM_WRITES",
            "NO_JFFS_WRITES",
            "NO_SERVICE_RESTARTS",
            "NO_REBOOT",
            "NO_FLASH_WRITES",
        ),
    )
    return summary


def validate_candidate_canaries(view: ArchiveView) -> None:
    view.require_regular("candidate-canaries.txt", nonempty=True)
    text = view.read_text("candidate-canaries.txt", limit=256 * 1024)
    observed: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("==="):
            continue
        if line.startswith("MISSING ") or line.startswith("NO_SHA256SUM "):
            continue
        parts = line.split(None, 1)
        if len(parts) == 2 and len(parts[0]) == 64:
            observed[parts[1].strip()] = parts[0].lower()

    for path, want in CANDIDATE_CANARIES.items():
        got = observed.get(path)
        if got != want:
            raise EvidenceError(
                f"{view.kind}: candidate canary mismatch for {path}: {got!r} != {want!r}"
            )

    webui = view.read_text("webui.txt", limit=512 * 1024)
    for required in (
        "/www/user -> /var/wwwext",
        "/www/user1.asp -> user/user1.asp",
        "/www/user20.asp -> user/user20.asp",
    ):
        if required not in webui:
            raise EvidenceError(f"{view.kind}: missing candidate WebUI canary {required!r}")


def validate_runtime(
    view: ArchiveView, expected_sha: str, require_candidate_canaries: bool = False
) -> Dict[str, str]:
    for rel in ("summary.txt", "safety.txt", "webui.txt", "jffs.txt", "services.txt"):
        view.require_regular(rel, nonempty=True)

    summary = parse_key_values(
        view.read_text("summary.txt", limit=256 * 1024),
        "RTAC86U_MERLIN_RUNTIME_READ_ONLY_PROBE",
        view.kind,
    )
    validate_identity(summary, view.kind, expected_sha)
    uname = summary.get("uname", "")
    if "aarch64" not in uname:
        raise EvidenceError(f"{view.kind}: uname does not contain aarch64: {uname!r}")

    validate_safety(
        view,
        (
            "NO_MODULES_LOADED",
            "NO_NVRAM_WRITES",
            "NO_JFFS_WRITES",
            "NO_SERVICE_RESTARTS",
            "NO_HTTP_REQUESTS",
            "NO_REBOOT",
            "NO_FLASH_WRITES",
        ),
    )
    if require_candidate_canaries:
        validate_candidate_canaries(view)
    return summary


def cross_check(k4: Dict[str, str], runtime: Dict[str, str]) -> None:
    for key in ("expected_candidate_sha256", "productid", "firmver", "buildno", "extendno"):
        if k4.get(key) != runtime.get(key):
            raise EvidenceError(
                f"identity mismatch between K4a and runtime archives for {key}: "
                f"{k4.get(key)!r} != {runtime.get(key)!r}"
            )

    release = k4.get("uname_r", "")
    if release and release not in runtime.get("uname", ""):
        raise EvidenceError(
            f"kernel release mismatch: K4a {release!r} not found in runtime uname"
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k4", required=True, help="K4a preflight tar/tar.gz")
    ap.add_argument("--runtime", required=True, help="general runtime preflight tar/tar.gz")
    ap.add_argument("--expected-sha", default=DEFAULT_SHA)
    ap.add_argument("--report", help="optional JSON report output path")
    ap.add_argument(
        "--require-candidate-canaries",
        action="store_true",
        help="require immutable candidate overlay hashes and user-slot symlinks",
    )
    ns = ap.parse_args()

    if len(ns.expected_sha) != 64 or any(c not in "0123456789abcdef" for c in ns.expected_sha):
        print("FAIL invalid expected SHA-256", file=sys.stderr)
        return 2

    k4_view = runtime_view = None
    try:
        k4_view = open_archive(ns.k4, "K4a", "rtac86u-k4-preflight")
        runtime_view = open_archive(
            ns.runtime, "runtime", "rtac86u-merlin-runtime-probe"
        )
        k4 = validate_k4(k4_view, ns.expected_sha)
        runtime = validate_runtime(
            runtime_view, ns.expected_sha, ns.require_candidate_canaries
        )
        cross_check(k4, runtime)

        classification = (
            "READ_ONLY_52334_CANDIDATE_RUNTIME_EVIDENCE"
            if ns.require_candidate_canaries
            else "READ_ONLY_52334_BASELINE_EVIDENCE"
        )
        report = {
            "status": "PASS",
            "classification": classification,
            "candidate_sha256": ns.expected_sha,
            "productid": k4["productid"],
            "firmver": k4["firmver"],
            "buildno": k4["buildno"],
            "extendno": k4["extendno"],
            "kernel_release": k4["uname_r"],
            "architecture": k4["uname_m"],
            "candidate_canaries_required": ns.require_candidate_canaries,
            "limitations": [
                "This verifies collector identity, archive integrity constraints, safety markers, and ASUS 386_52334 runtime identity.",
                "It does not prove optional module compatibility.",
                "It does not prove M49 EJ dispatch.",
                "Candidate-canary mode fingerprints immutable overlay files and WebUI aliases but still cannot reconstruct the full .w SHA-256 from runtime files.",
            ],
        }
        payload = json.dumps(report, indent=2, sort_keys=True)
        if ns.report:
            with open(ns.report, "w", encoding="utf-8") as fh:
                fh.write(payload + "\n")
        print(payload)
        print(
            "HARDWARE_EVIDENCE_CANDIDATE_PASS"
            if ns.require_candidate_canaries
            else "HARDWARE_EVIDENCE_BASELINE_PASS"
        )
        return 0
    except EvidenceError as exc:
        print(f"HARDWARE_EVIDENCE_BASELINE_FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        if k4_view is not None:
            k4_view.tar.close()
        if runtime_view is not None:
            runtime_view.tar.close()


if __name__ == "__main__":
    raise SystemExit(main())
