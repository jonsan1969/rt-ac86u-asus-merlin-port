# Optional kernel module ABI validation strategy

Date: 2026-09-28  
Features: M22 NFS, M23 CIFS, M27 ipset, M32 Cake/ctinfo, M33 WireGuard

## Purpose

Improve the evidence beyond matching kernel release/vermagic before any source-build work.

The project rule remains:

**Do not transplant Merlin kernel modules into ASUS 52334.**

This ABI analysis is diagnostic. It can prove incompatibility early and can identify how close the kernel symbol ABI is, but it cannot by itself authorize a donor module overlay.

## Why vermagic is insufficient

A module can report the same:

`4.1.27 SMP preempt mod_unload aarch64`

and still be incompatible because of:

- different CONFIG options;
- different exported symbol version CRCs;
- Broadcom/HND vendor patches;
- changed struct layouts not covered by a referenced symbol;
- missing dependent modules;
- proprietary subsystem expectations;
- different compiler/build flags.

## Stronger check: CONFIG_MODVERSIONS CRCs

Linux modules built with symbol versioning carry a `__versions` table.

`modprobe --dump-modversions <module.ko>` exposes pairs of:

- expected CRC;
- imported symbol name.

The new CI probe builds an observed ASUS 52334 CRC map from **all stock ASUS modules**.

For each optional Merlin module it then classifies every required symbol:

- **MATCH** — the same symbol is referenced by at least one ASUS stock module and the CRC agrees;
- **MISMATCH** — ASUS stock modules reference the same symbol with a different CRC;
- **UNOBSERVED** — no stock ASUS module happens to import that symbol, so the image cannot prove its CRC.

## Interpretation

### Any mismatch

A mismatch is a hard stop for binary-module compatibility.

Classification remains:

`SOURCE_BUILD_REQUIRED`

and the report identifies the exact symbols that differ.

### All observed symbols match

This is useful lineage evidence, but still insufficient for transplant.

Unobserved symbol CRCs and kernel configuration/proprietary subsystem state remain unknown.

Classification remains:

`SOURCE_BUILD_REQUIRED`

until a module is built against the actual ASUS-compatible kernel source/config/symbol environment.

## Common-module sanity check

The probe also compares modules with the same basename present in ASUS and Merlin.

For these stock-common modules it reports symbol-version overlap/mismatches.

This gives a broad indication of whether the two firmware images share the same effective module ABI generation.

It is still not a substitute for ASUS `Module.symvers`.

## Feature-specific requirements

### M22 NFS

Rebuild the NFS/sunrpc/lockd stack together against the ASUS-compatible kernel tree.

Do not mix donor `sunrpc.ko` with ASUS kernel internals.

### M23 CIFS

Rebuild `cifs.ko` against the ASUS-compatible tree/config.

Validate crypto/keyring dependencies and mount helper/userland separately.

### M27 ipset

Rebuild the full ipset kernel family and `xt_set` against the ASUS-compatible tree.

Userspace `ipset` must match the built kernel API revision.

### M32 Cake

Rebuild `sch_cake.ko` and `act_ctinfo.ko` against the ASUS-compatible networking/qdisc tree.

Then validate Broadcom HND acceleration interaction before enabling a UI/qdisc choice.

### M33 WireGuard

Rebuild WireGuard and its required crypto/compat layer against the target kernel source/config.

Do not assume generic WireGuard strings in ASUS UI/libvpn imply kernel support.

## Final build gate

A kernel feature may move beyond SOURCE_BUILD_REQUIRED only when all are true:

1. a sufficiently late ASUS-compatible kernel tree is identified;
2. target RT-AC86U kernel config is reconstructed/verified;
3. required Broadcom/HND patches and headers are present;
4. module is built with the target toolchain;
5. vermagic matches;
6. no symbol-version mismatch exists;
7. all dependencies resolve from the same build/runtime;
8. qemu/static inspection passes where meaningful;
9. real-router load/unload and functional validation succeeds;
10. ASUS kernel image and existing proprietary modules remain authoritative.

## Current classification

**ABI DIAGNOSTIC IMPROVED; ALL FIVE FEATURES REMAIN SOURCE-BUILD REQUIRED.**


## Firmware-image CRC probe result

Run `36447256650` completed successfully after the module-selection probe was corrected.

Observed result:

- ASUS 52334 stock modules: `0` readable imported symbol/CRC pairs;
- Merlin optional modules: present for NFS, CIFS, ipset, Cake and WireGuard, but `modprobe --show-modversions` likewise returns no usable per-symbol version table;
- 132 module basenames exist in both images, but zero could be compared through MODVERSIONS CRCs.

Therefore the firmware images do not expose enough symbol-version metadata to upgrade binary compatibility confidence. This is a diagnostic limitation, not evidence of ABI equality.

The source-build requirement and no-donor-`.ko` rule remain unchanged.
