# K4 family staging bundles

Date: 2026-10-02

## Purpose

The physical K4 rule is **one coherent family at a time**.

The main hardware-validation bundle intentionally preserves all exact K2/K3 outputs, but those 27 modules must not be copied wholesale into a live router staging directory. Family staging bundles reduce the chance of loading or testing an unrelated module by mistake.

The staging workflow does not build, load, install or activate anything. It only selects already verified files from the preserved hardware-validation bundle and repackages them into small Unix tar archives with hash manifests.

## Family contents

### ipset / xt_set

Minimum smoke family:

1. `ip_set.ko`
2. `ip_set_hash_ip.ko`
3. `xt_set.ko`

The package also carries the previously verified `k4-ipset-userspace-51997.tar.gz`.

This subset is sufficient for an isolated `hash:ip` userspace/kernel smoke and an `xt_set` parse/use check. Other ipset set-type modules remain preserved in the main hardware bundle but are not staged for the first K4 smoke.

### Cake

- `sch_cake.ko`
- verified temporary CAKE-aware `tc` companion tarball.

### CIFS

- `cifs.ko` only.

No unrelated Samba/Merlin userspace is bundled. A real filesystem smoke remains physical/environment-dependent.

### NFS / SUNRPC / LOCKD

Exact full K3 family:

1. `sunrpc.ko`
2. `lockd.ko`
3. `nfs.ko`
4. `nfsd.ko`
5. `nfsv2.ko`
6. `nfsv3.ko`

Unload order is the reverse.

The order is frozen by ELF-symbol closure run `36976006891`; it is not taken from the incomplete `modinfo depends` metadata.

The exact 51997 router userspace build disables `mount.nfs`, so this staging package deliberately does not invent a new NFS client userspace ABI.

### WireGuard

- `wireguard.ko`
- verified temporary `wg` companion tarball.

## Safety boundary

Every family package is:

- temporary K4 staging material only;
- bound to the exact project candidate and K2/K3 lineage through its manifest;
- composed only from files already present in the preserved hardware-validation bundle;
- hash-verified after re-extraction in CI;
- never installed into a firmware rootfs, JFFS autoload path or stock module directory.

A staging package is **not** module compatibility evidence and is not flash approval.

Before any load, the real ASUS-52334 K4a/runtime evidence gates and `K4_SYMBOL_PREFLIGHT_PASS` remain mandatory.

## Physical use

Copy and extract only the family being tested below a temporary path such as `/tmp/k4-<family>`.

Do not extract multiple family packages into one directory.

Follow `docs/k4-controlled-module-validation.md` for the actual operator-controlled load/function/unload sequence and STOP conditions.


## CI evidence

Run `36978077020` — **SUCCESS**.

Published artifact:

- name: `k4-family-staging-bundles`;
- artifact id: `11213839004`;
- ZIP digest: `sha256:728f00b384a851dbca4c7c04419009a4b8253be30baa6736a8abd90d34b6db93`;
- expires: `2026-12-31T07:20:53Z`.

CI validates source inventory, exact family isolation, per-family manifests, re-extraction, executable userspace transport where applicable, and the outer package checksum file. The preceding run `36977943467` is a superseded checksum-path harness failure only; its log is already consumed and must not be fetched again.

The five family tarballs remain temporary K4 staging material only. They do not authorize module loading and do not change the candidate's UNVALIDATED status.


## Preserved with the complete hardware bundle

Preservation run `36995684511` — **SUCCESS** — downloads artifact `11213839004`, verifies `package-sha256.txt`, re-extracts all five family tarballs, rechecks each internal manifest, and then embeds them in the 90-day `hardware-validation-bundle-eac8a777`.

Preserved artifact id: `11221372631`.  
Preserved artifact ZIP digest: `sha256:7bf47721147dbd49c52ec0af2e065499b3b35efada44057771588b163b2a37a1`.  
Expiry: `2026-12-31T10:28:43Z`.

This preservation step changes transport/readiness only. It does not add runtime evidence or authorize loading any module.


## Host-side family staging verifier

`scripts/verify-k4-family-staging.py` is the fail-closed host-side selector/preparer for physical K4. It pins the five exact outer family archive SHA-256 values from run `36978077020`, requires the exact outer package inventory, validates the selected tar path/type set, requires exact manifest provenance/load order/file hashes, and may extract only the selected family to a clean host directory.

Example:

```sh
python3 scripts/verify-k4-family-staging.py \
  --packages-root <hardware-bundle>/k4-family-staging \
  --family ipset \
  --output /tmp/k4-ipset-host-stage \
  --report k4-ipset-staging.json
```

Require `K4_FAMILY_STAGING_PASS family=<family>` before copying the resulting single family directory to router `/tmp`. This verifier does not run K4 symbol-preflight and does not load a module.


## Verifier CI evidence

Run `36994228096` — **SUCCESS**.

The validation workflow uses the exact family packages preserved by run `36995684511` and proves:

- all five families pass the pinned outer archive hashes and selected-family manifest/file inventory;
- each selected family extracts to a clean host staging directory;
- an altered family archive is rejected;
- a changed outer checksum pin is rejected;
- an unexpected package-root file is rejected;
- a non-empty output directory is rejected.

Superseded run `36993934701` failed only because the verifier's raw outer filename regex over-escaped the literal dots in `.tar.gz`; its job log was fetched exactly once. No family-content or runtime conclusion was taken from that failed run.
