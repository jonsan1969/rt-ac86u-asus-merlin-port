#!/usr/bin/env python3
"""Host-only orchestration of the pre-K4 evidence gates.

This script never contacts the router and never loads a module. It chains the
existing fail-closed host verifiers against one exact preserved bundle plus one
pair of read-only router evidence archives, then prepares one verified family in
a clean host staging directory.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

CANDIDATE_SHA = "eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3"
FAMILIES = ("ipset", "cake", "cifs", "nfs", "wireguard")


class GateError(RuntimeError):
    pass


def run_gate(cmd: list[str], marker: str, log_path: Path) -> None:
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log_path.write_text(cp.stdout, encoding="utf-8")
    if cp.returncode != 0:
        raise GateError(f"{Path(cmd[1]).name} failed; see {log_path}")
    if marker not in cp.stdout:
        raise GateError(f"{Path(cmd[1]).name} returned rc=0 without {marker!r}")


def require_empty_or_create(path: Path) -> None:
    if path.exists():
        if not path.is_dir():
            raise GateError(f"output path exists and is not a directory: {path}")
        if any(path.iterdir()):
            raise GateError(f"output directory is not empty: {path}")
    else:
        path.mkdir(parents=True, mode=0o700)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle-root", required=True)
    ap.add_argument("--k4", required=True, help="read-only K4a archive from the router")
    ap.add_argument("--runtime", required=True, help="read-only runtime archive from the router")
    ap.add_argument("--family", required=True, choices=FAMILIES)
    ap.add_argument("--output", required=True, help="clean host workspace")
    ap.add_argument("--candidate-mode", action="store_true")
    ns = ap.parse_args()

    root = Path(ns.bundle_root)
    out = Path(ns.output)
    try:
        require_empty_or_create(out)
        scripts = Path(__file__).resolve().parent
        required_scripts = {
            "bundle": scripts / "verify-hardware-validation-bundle.py",
            "evidence": scripts / "verify-hardware-evidence.py",
            "symbols": scripts / "verify-k4-symbol-preflight.py",
            "family": scripts / "verify-k4-family-staging.py",
        }
        for name, path in required_scripts.items():
            if not path.is_file():
                raise GateError(f"missing host verifier {name}: {path}")

        modules = root / "modules"
        closure = root / "reports" / "k4-module-dependency-closure.json"
        packages = root / "k4-family-staging"
        for path in (root, modules, closure, packages):
            if not path.exists():
                raise GateError(f"required bundle path missing: {path}")

        run_gate(
            [sys.executable, str(required_scripts["bundle"]), "--bundle-root", str(root),
             "--report", str(out / "bundle-report.json")],
            "HARDWARE_VALIDATION_BUNDLE_PASS",
            out / "bundle-verifier.log",
        )

        evidence_cmd = [
            sys.executable, str(required_scripts["evidence"]),
            "--k4", ns.k4, "--runtime", ns.runtime,
            "--expected-sha", CANDIDATE_SHA,
            "--report", str(out / "hardware-evidence-report.json"),
        ]
        evidence_marker = "HARDWARE_EVIDENCE_BASELINE_PASS"
        if ns.candidate_mode:
            evidence_cmd.append("--require-candidate-canaries")
            evidence_marker = "HARDWARE_EVIDENCE_CANDIDATE_PASS"
        run_gate(evidence_cmd, evidence_marker, out / "hardware-evidence.log")

        run_gate(
            [
                sys.executable, str(required_scripts["symbols"]),
                "--k4", ns.k4,
                "--modules-root", str(modules),
                "--closure", str(closure),
                "--expected-sha", CANDIDATE_SHA,
                "--report", str(out / "symbol-preflight-report.json"),
            ],
            "K4_SYMBOL_PREFLIGHT_PASS",
            out / "symbol-preflight.log",
        )

        staged_parent = out / "selected-family"
        run_gate(
            [
                sys.executable, str(required_scripts["family"]),
                "--packages-root", str(packages),
                "--family", ns.family,
                "--output", str(staged_parent),
                "--report", str(out / "family-staging-report.json"),
            ],
            f"K4_FAMILY_STAGING_PASS family={ns.family}",
            out / "family-staging.log",
        )

        staged = staged_parent / ns.family
        if not staged.is_dir():
            raise GateError(f"family verifier passed but staged directory is missing: {staged}")

        report = {
            "status": "PASS",
            "classification": "RTAC86U_52334_PRE_K4_HOST_GATES",
            "candidate_sha256": CANDIDATE_SHA,
            "candidate_mode": ns.candidate_mode,
            "family": ns.family,
            "bundle_root": str(root),
            "staged_family_path": str(staged),
            "required_markers": [
                "HARDWARE_VALIDATION_BUNDLE_PASS",
                evidence_marker,
                "K4_SYMBOL_PREFLIGHT_PASS",
                f"K4_FAMILY_STAGING_PASS family={ns.family}",
            ],
            "next_step": (
                "Operator-controlled physical K4 only. Copy only staged_family_path to a fresh "
                f"/tmp/k4-{ns.family} path and follow docs/k4-controlled-module-validation.md."
            ),
            "limitations": [
                "This script is host-only and does not contact the router.",
                "It does not load modules, alter NVRAM/JFFS/services, reboot, or flash firmware.",
                "PASS does not prove module loadability, HND stability, functional smoke success, M49 EJ dispatch, or flashability.",
                "The physical K4 load/function/unload protocol remains mandatory.",
            ],
        }
        (out / "pre-k4-host-gates.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        print(f"PRE_K4_HOST_GATES_PASS family={ns.family}")
        return 0
    except (GateError, OSError) as exc:
        print(f"PRE_K4_HOST_GATES_FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
