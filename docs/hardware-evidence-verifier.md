# Hardware evidence verifier

Date: 2026-10-02

## Purpose

`scripts/verify-hardware-evidence.py` is the host-side fail-closed intake gate for the future physical validation phase.

It consumes the two read-only router archives:

- K4a: `rtac86u-k4-preflight.tar[.gz]`;
- general runtime: `rtac86u-merlin-runtime-probe.tar[.gz]`.

The verifier does **not** contact or mutate the router.

## Required identity

For the current candidate it requires:

- embedded expected candidate SHA-256:
  `eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3`;
- `productid=RT-AC86U`;
- ASUS firmware base beginning `3.0.0.4`;
- `buildno=386`;
- `extendno` containing `52334`;
- no Merlin-like `386.14` identity;
- AArch64 kernel identity;
- matching firmware identity across both archives.

It also requires the declared read-only safety markers, readable K4 `/proc/kallsyms`, pre-test dmesg, and the expected evidence files.

Archives with absolute/traversal paths, symlinks, hardlinks, devices or other unexpected member types are rejected before content inspection.

## Usage

```sh
python3 scripts/verify-hardware-evidence.py \
  --k4 rtac86u-k4-preflight.tar.gz \
  --runtime rtac86u-merlin-runtime-probe.tar.gz \
  --report hardware-baseline-report.json
```

A successful verification prints:

`HARDWARE_EVIDENCE_BASELINE_PASS`

and exits zero.

## What PASS means

PASS means the two collector archives are structurally safe to inspect, carry the expected current candidate binding, identify the same RT-AC86U ASUS 386_52334 runtime, retain the read-only safety contract, and include the baseline K4/runtime evidence required for further review.

PASS does **not** mean:

- the UNVALIDATED firmware is flash-approved;
- K2/K3 modules are compatible;
- a K4 family may be activated;
- M49 EJ dispatch works;
- the runtime can independently reconstruct and cryptographically prove the full `.w` SHA-256.

The exact candidate binding remains procedural: the operator uses the preserved candidate whose `.w` hash is recorded by `prepare-candidate-evidence.sh`, while these collectors confirm the intended 52334 runtime and evidence set.

## CI

`.github/workflows/validate-hardware-evidence-verifier.yml` covers:

- valid matching ASUS 52334 fixtures;
- wrong candidate SHA rejection;
- Merlin-runtime rejection;
- missing `/proc/kallsyms` rejection;
- unsafe tar path rejection.

This gate is deliberately before any mutating K4 step.
