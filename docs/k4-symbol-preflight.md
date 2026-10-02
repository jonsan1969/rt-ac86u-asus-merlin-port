# K4 host-side symbol preflight

Date: 2026-10-02

## Purpose

`scripts/verify-k4-symbol-preflight.py` is a **read-only host-side gate** between K4a evidence intake and the first mutating module-load attempt.

It consumes:

- the real-router K4a archive `rtac86u-k4-preflight.tar[.gz]`;
- the exact preserved K2/K3 `.ko` files;
- the schema-2 dependency-closure report from run `36976006891`.

It never contacts the router and never loads/unloads a module.

## What it verifies

In normal `project` profile the verifier requires:

- the current candidate binding:
  `eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3`;
- RT-AC86U identity;
- ASUS 386_52334 identity, not Merlin 386.14_2;
- AArch64 target identity;
- the K4a read-only safety markers;
- readable `/proc/kallsyms`;
- the exact expected 18 K2 + 9 K3 module-name set;
- every actual module SHA-256 matching its row in the preserved closure report;
- independent representative module hashes already pinned by the preservation workflow;
- `4.1.27 SMP preempt mod_unload aarch64` closure vermagic for every module;
- AArch64 ELF identity;
- freshly recalculated undefined symbols and `__ksymtab_*` exports matching the preserved closure report;
- freshly derived optional-module provider relationships matching that report.

For every **strong undefined symbol** not supplied by another exact K2/K3 module, the verifier then requires that symbol name to exist in the observed ASUS-52334 K4a `/proc/kallsyms`.

A missing strong symbol is a hard pre-load failure.

Weak undefined symbols are reported separately. Their absence does not fail this name-presence gate.

## Usage

After the normal hardware evidence intake has passed:

```sh
python3 scripts/verify-k4-symbol-preflight.py \
  --k4 rtac86u-k4-preflight.tar.gz \
  --modules-root hardware-validation-bundle/modules \
  --closure hardware-validation-bundle/reports/k4-module-dependency-closure.json \
  --report k4-symbol-preflight.json
```

Require:

`K4_SYMBOL_PREFLIGHT_PASS`

before any optional module load is considered.

## Important limitation

`/proc/kallsyms` is a symbol-name inventory, not a complete proof of module-linkability.

A PASS therefore means only:

> every strong symbol name that the exact optional modules require, after satisfying their own artifact-internal dependencies, is visible in the captured target runtime.

It does **not** prove:

- that a visible name is exported through `EXPORT_SYMBOL` / `EXPORT_SYMBOL_GPL`;
- symbol CRC / MODVERSIONS compatibility;
- relocation success;
- final vermagic acceptance by the running kernel;
- absence of duplicate/export conflicts;
- HND/network stability;
- functional behavior;
- safe unload.

The physical K4 load/function/unload test remains authoritative. An `Unknown symbol`, format/vermagic error, WARN/Oops, HND instability or network regression remains STOP/FAIL even after this preflight passes.

## Security / evidence boundary

The verifier:

- rejects unsafe/traversing K4 tar members;
- rejects symlinks, hardlinks, devices and FIFOs in the evidence archive;
- validates the K4a safety markers;
- hashes module files rather than trusting filenames;
- recomputes ELF symbol sets with host `readelf`;
- produces only an optional host-side JSON report.

It performs no NVRAM/JFFS writes, no service actions, no network requests and no router mutation.

## CI

`.github/workflows/validate-k4-symbol-preflight.yml` uses synthetic ELF modules and synthetic K4a archives to prove:

- PASS when a strong kernel-required symbol exists and an optional dependency is supplied by another exact module;
- FAIL when a strong required symbol is absent;
- FAIL when a module hash changes;
- FAIL when the recorded internal dependency graph is stale/wrong;
- FAIL on Merlin-like runtime identity;
- FAIL on unsafe tar traversal.

The CI fixture profile is explicitly non-production and does not relax the default `project` profile.
