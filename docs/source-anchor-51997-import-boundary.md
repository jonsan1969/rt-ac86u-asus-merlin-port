# Exact 386.51997 import boundary for RT-AC86U

Date: 2026-09-29

## Purpose

Replace the vague statement "Merlin 386.12 was merged with ASUS GPL 386_51997" with exact Git provenance that separates:

1. the **general ASUS GPL 386_51997 import**; and
2. the later **RT-AC86U-specific SDK/binary-blob import**.

This gives the project a much stronger late-386 structural anchor while preserving the rule that a Merlin tree is not clean ASUS source.

## Exact commits

### General GPL 386_51997 import

Commit:

`28daa82377c5a9a68bf2c79aea429323a891ac08`

Commit message:

`Merged with GPL 386_51997 + RT-AC88U SDK and binary blobs`

Parent:

`bf59d7ec4339d3c1eb71fe03209243947084e754`

This is a single-parent import commit, not a merge commit with a recoverable clean-ASUS second parent.

It updates the shared router source tree to the 51997 generation while preserving/reconciling existing Merlin modifications.

### RT-AC86U 386_51997 SDK/blob import

Commit:

`c553d8e4b0bf3289683368b0d57172649b030039`

Commit message:

`Merge RT-AC86U binary blobs + SDK from 386_51997`

Parent:

`2b13c8cc8cf821fa774371c18e3a68a8b6965ad8`

This commit refreshes the model-specific HND SDK/prebuilt surface for RT-AC86U after the general GPL import.

For late-386 RT-AC86U build-shape archaeology, `c553d8e4...` is therefore the most precise pinned reference currently available.

It is **not** a clean ASUS source commit.

## What the general GPL import changed

Direct blob-SHA comparison before and after `28daa823...` shows that the 51997 GPL import changed the source shape of most large files in which our source-required hooks must ultimately be placed:

| File | pre-51997 SHA | post-general-51997 SHA | Result |
|---|---|---|---|
| `shared/shared.h` | `e118cf71...` | `4502576e...` | changed |
| `shared/defaults.c` | `4395df60...` | `5499734a...` | changed |
| `rc/services.c` | `aabaa70c...` | `08e2dcdd...` | changed |
| `rc/firewall.c` | `0d9855a4...` | `c11eab8f...` | changed |
| `rc/udhcpc.c` | `1b70b958...` | `a424e353...` | changed |
| `rc/qos.c` | `293861ec...` | `2fb7e64c...` | changed |
| `rc/usb.c` | `41614c40...` | `d8018a77...` | changed |
| `rc/wan.c` | `78b6629b...` | `b6c95518...` | changed |
| `rc/init.c` | `4313eb7e...` | `e38c7fa5...` | changed |
| `rc/watchdog.c` | `4baf7ac4...` | `1ada970a...` | changed |
| `httpd/web.c` | `99187a29...` | `27377f8f...` | changed |
| `httpd/httpd.c` | `9730cb5d...` | `dbbb9358...` | changed |

These are exactly the kinds of files for which the much older clean ASUS 45956 tree is insufficient as a patch-placement reference.

The 51997 post-import version should be used for **late source shape**, while clean 45956 remains the clean-ASUS lineage comparator.

## Important files unchanged by the general GPL import

The following inspected files did not change across the general 51997 import:

| File | Blob SHA | Interpretation |
|---|---|---|
| `shared/scripts.c` | `be75c75b...` | inherited helper implementation remained stable |
| `rc/ubifs.c` | `74b8981d...` | JFFS/UBIFS source shape remained stable across this import |
| `libdisk/write_smb_conf.c` | `227fb26d...` | this particular donor-side Samba generator was not refreshed by the GPL import |
| `libovpn/openvpn_control.c` | `17cb87b6...` | remained Merlin-owned/unchanged through import; **not evidence of ASUS source equivalence** |

The last point is critical.

A file being unchanged by the ASUS GPL import can mean either:

- stable inherited ASUS-lineage code; or
- Merlin-specific code that ASUS's import did not overwrite.

Authorship/provenance must be established independently before treating an unchanged file as ASUS-derived.

## RT-AC86U model-specific import boundary

Comparing parent `2b13c8cc...` to RT-AC86U import `c553d8e4...` shows that the commit primarily refreshes model-specific SDK/prebuilt/proprietary assets.

Examples include:

- HND wireless objects such as `dhd.o`, `wl.o`, `wlcsm.o`;
- RT-AC86U HTTPD prebuilt objects `pwenc.o` and `web_hook.o`;
- numerous RT-AC86U `rc/prebuild/*.o` objects;
- numerous RT-AC86U `shared/prebuild/*.o` objects;
- BWDPI/TrendMicro binaries and libraries;
- AiMesh/config/networkmap/protection components;
- model-specific `libnvram`, WLAN and helper binaries.

The notable open kernel-source change in this model import is:

`release/src-rt-5.02hnd/kernel/linux-4.1/net/ipv6/ip6_tunnel.c`

which receives a substantial update.

This reinforces two project rules:

1. the RT-AC86U HND SDK/proprietary object boundary is model-specific and must be preserved;
2. optional kernel feature work must be built against the correct HND source/config/object ecosystem, not merely against a generic Linux 4.1.27 tree.

## Core source files are unchanged by the RT-AC86U blob/SDK import

For the inspected source files relevant to JFFS lifecycle, HTTPD, QoS and networking, the blob SHA after the general GPL import is the same at `c553d8e4...`.

Examples:

- `shared/shared.h`;
- `shared/defaults.c`;
- `rc/services.c`;
- `rc/firewall.c`;
- `rc/udhcpc.c`;
- `rc/qos.c`;
- `rc/usb.c`;
- `rc/wan.c`;
- `rc/init.c`;
- `rc/watchdog.c`;
- `httpd/web.c`;
- `httpd/httpd.c`.

Therefore, for these files:

- `28daa823...` identifies the late shared GPL source-shape transition;
- `c553d8e4...` adds the correct RT-AC86U model SDK/blob context without changing that inspected router-source shape.

## How this changes the project source strategy

Use four evidence layers:

### A. Clean ASUS lineage

`blackfuel/asuswrt-rt-ac86u@a9179fc...` / ASUS 386.45956

Use for:

- proving whether a primitive existed in clean ASUS;
- identifying ASUS-vs-Merlin feature ancestry.

### B. Exact late general GPL shape

`RMerl/asuswrt-merlin.ng@28daa823...`

Use for:

- identifying the 51997-era source/function layout;
- reviewing merge placement of narrow patches.

Do not treat Merlin-retained code as clean ASUS merely because it exists here.

### C. Exact RT-AC86U 51997 SDK/blob context

`RMerl/asuswrt-merlin.ng@c553d8e4...`

Use for:

- HND 5.02 build environment archaeology;
- RT-AC86U model-specific prebuilt/object provenance;
- kernel/SDK integration experiments;
- determining which source areas were model-specific vs shared.

### D. Official ASUS runtime lineage

Official 51967 -> 52294 -> 52334 firmware images.

Use for:

- determining which runtime components changed after the last GPL source generation;
- retaining the final 52334 security/runtime implementation.

## Patch-placement rule

For a source-required feature in a shared router source file:

1. prove feature ancestry against clean 45956 where possible;
2. inspect the exact post-51997 source shape at `28daa823...`;
3. use `c553d8e4...` when RT-AC86U SDK/model context matters;
4. compare the relevant final runtime component across 51967/52294/52334;
5. rebuild/replace a protected component only if the later runtime delta can be preserved with evidence.

The default remains **no rebuild of a protected core component** from 51997-era source merely because the source now builds.

## Kernel-module implication

For M22/M23/M27/M32/M33, `c553d8e4...` is a materially better build-environment anchor than the generic 45956 mirror because it contains the RT-AC86U 51997 HND SDK/blob refresh.

It still does not provide:

- ASUS 52334 kernel source;
- final 52334 kernel config certainty;
- final proprietary object ABI certainty.

The optional-module rule remains source-build-only, followed by strict compatibility and real-router validation.

## Current classification

**EXACT 51997 IMPORT BOUNDARY: VERIFIED**

**CLEAN 51997 ASUS PARENT: NOT RECOVERABLE FROM MERLIN GIT HISTORY**

**RT-AC86U 51997 SDK/BLOB ANCHOR: `c553d8e4b0bf3289683368b0d57172649b030039`**

This significantly improves source placement/build provenance without weakening the ASUS 52334 runtime-baseline rule.
