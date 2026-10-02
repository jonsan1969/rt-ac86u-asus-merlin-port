# New-thread handoff

Updated: 2026-10-02

## Project

**Modern RT-AC86U firmware med Merlin-funktionalitet**

Repository: `jonsan1969/rt-ac86u-asus-merlin-port`  
Branch: `asus-52334-merlin-port`

Main track: ASUS `386_52334` + pinned Merlin `386.14_2`.

KoolCenter is a separate track in the same repo/branch. Never mix its commits, Actions, evidence or conclusions into this main track unless a specific transfer is explicitly approved.

## Working rule

Git/repo is the project working memory.

Continue autonomously while work can be done. Stop only for genuinely required user input, physical router access or external information that cannot be worked around.

After every GitHub Action:

1. inspect the result;
2. update governing docs to current truth;
3. continue immediately if another source-independent/router-independent step exists.

Fetch any given Action **log** at most once. Reuse the extracted finding; do not re-fetch the same log.

Repository state overrides old chat context. Do not reopen settled probes.

## Non-negotiable architecture

- Final hardware/runtime/security authority: ASUS RT-AC86U `3.0.0.4.386_52334`.
- Merlin donor/reference: `386.14_2`, source commit `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`.
- Never replace newer ASUS `rc`, `httpd`, `dnsmasq`, BusyBox, OpenVPN, Dropbear, OpenSSL, kernel/HND or proprietary components with older Merlin binaries.
- Shared-core features require source-delta integration onto an ASUS-compatible lineage.
- Never replace the ASUS 52334 kernel image.
- No flashability claim before promotion and physical/runtime gates pass.

## Current software-gated candidate

Run: `36924014278`

Firmware: `RT-AC86U_386_52334_merlin-port-UNVALIDATED.w`

Exact `.w` SHA-256:

`eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3`

Size: `78,250,004` bytes.

Classification: **UNVALIDATED — NOT FLASH-APPROVED**.

The software gate proves:

- guarded manifest/overlay authorization;
- verified ASUS 386_52334 base;
- exact 570-PEB UBI;
- valid WFI/trailer/CRC;
- metadata-faithful re-extraction;
- zero unauthorized semantic drift;
- protected ASUS core files byte-identical;
- zero K2/K3 optional-kernel-module leakage.

Original candidate artifact: `11193520953`.

## Preserved hardware-validation inputs

Run `36967176099` is SUCCESS.

Artifact: `hardware-validation-bundle-eac8a777`  
Artifact id: `11210471933`  
ZIP digest: `sha256:05ee4f971846b84a83378e7673832550c8646bbedb8f77d846d49e942d4cc252`  
Expiry: 2026-12-31.

The workflow re-verifies the exact candidate hash/size and the K2/K3 module identities before republishing.

**Never use the artifact ZIP digest as the firmware identity.** Hardware evidence is bound to the exact `.w` SHA-256 above.

## Candidate evidence / physical collectors

Candidate evidence helper:

`scripts/prepare-candidate-evidence.sh`

CI: `36924149359` — SUCCESS.

K4a read-only collector:

`scripts/k4-router-preflight.sh`

Hash-bound CI: `36924628372` — SUCCESS.

General runtime collector:

`scripts/runtime-feature-preflight.sh`

Hash-bound CI: `36924632712` — SUCCESS.

Both collectors remain read-only and are bound to the current candidate hash.

## Kernel/module track

K1 config/toolchain lineage: **SUCCESS**, run `36531249746`.

K2 ipset/xt_set family: **SUCCESS**, run `36556899650`.

K3 optional families: **SUCCESS**, run `36561957525`.

Built families:

- ipset / xt_set;
- Cake;
- CIFS;
- NFS/SUNRPC/LOCKD;
- WireGuard.

These are build proofs only.

K4 physical ASUS-52334 validation remains mandatory. Test one family at a time in this order:

1. ipset / xt_set;
2. Cake;
3. CIFS;
4. NFS/SUNRPC/LOCKD;
5. WireGuard.

Unknown symbols, format/vermagic errors, WARN/Oops or HND/network instability are STOP/FAIL conditions.

Never run K4 on Merlin 386.14_2 and count it as ASUS 52334 evidence.

## M07 custom WebUI

M07 is SUCCESS.

Metadata-faithful `ubi-reader -k -x` extraction proves:

`/www/user -> /var/wwwext`

The old Binwalk-only `/dev/null` result was an extraction artifact.

Do not patch `/www/user`.

## M49 Monthly Traffic

Backend/implementation remains SUCCESS but built-in page/Chart.js were optionalized for the immutable 570-PEB budget.

Optional user-slot/JFFS package preparation is now **SUCCESS / STATIC-SANDBOX VALIDATED**:

run `36966933767`.

Package:

`optional/monthly-traffic/`

It provides explicit `userN.asp` rendering, private Chart.js in `/var/wwwext`, collision guards, no rootfs/NVRAM/service/startup mutation, and fail-closed uninstall.

The remaining gate is physical/runtime proof that ASUS 386_52334 stock `httpd` EJ-expands:

`<% bandwidth("monthly"); %>`

through the active custom user-slot path.

Do not replace that runtime proof with more static CI.

## Optional/JFFS payloads

Nano + SCP optional delivery: run `36863705618` — SUCCESS.

Dormant AMTM materialization: run `36864039573` — SUCCESS.

Local NTPD and wsdd2 foundations remain dormant until generic JFFS lifecycle hooks exist.

Capacity-heavy payloads must remain optional/JFFS-delivered unless a new design is separately proven.

## Pre-flash recovery readiness

`docs/preflash-backup-recovery.md` is READY.

It keeps Merlin configuration/JFFS backups private and rollback-only, forbids importing Merlin state as ASUS/candidate evidence, and requires verified rollback media plus wired recovery readiness.

Actual backup creation remains a physical operator step before any future firmware change.

## ASUS 52334 source

Matching ASUS `386_52334` GPL/source is still not available.

This is an **EXTERNAL BLOCKER**.

Do not repeat source hunting each work cycle without new evidence.

Source-backed core features requiring `rc/httpd/dnsmasq/shared` must not be solved by transplanting older Merlin binaries.

## Source-blocked feature work

The exact behavioral/source contracts are already documented. Remaining implementation is blocked on a suitable later ASUS source/build base for, among others:

- M01-M04 JFFS lifecycle/custom config;
- M10/M60 JFFS backup/restore backend;
- M11 custom DDNS;
- M18/M19 Samba deltas;
- M25/M40 VPN Director/routing;
- M36 IPv6 DNS Director Custom 1-3;
- M38 OpenVPN DNS Exclusive;
- M43 System Info HTTPD backend;
- M46/M64 QoS stats;
- M52 wireless-client auto-refresh backend;
- M57 Advanced VPN Status;
- M66 Prevent Auto DoH;
- M68 outbound LAN logging.

Do not reopen their donor/source archaeology unless new source evidence appears.

## Settled — do not investigate again

- M48 per-IP traffic/cstats: **NO PORT**.
- M35 WiFi Insight: **CANCELLED**.
- M67 speedtest VPN selector: **CANCELLED**.
- M37 IPv6 OpenVPN server: **NO PORT**.
- M39 OpenVPN custom-option storage: **NO PORT**.
- M51 Wireless ACL client names: **NO PORT / ASUS equivalent**.
- M56 editable-entry umbrella: **NO PORT / ASUS equivalent**.
- M12 cru: **NO generic port**.
- M14 generic CLI umbrella: **NO generic port**.
- LZO/rootfs-capacity investigation: closed.
- 570-PEB capacity problem: solved.
- stock repack: solved.
- K1/K2/K3 build loops: solved.

## What remains now

All currently identifiable source-independent and router-independent main-track work has been completed:

- full software-gated candidate exists;
- exact candidate/K2/K3 hardware inputs are preserved;
- K4/runtime collectors are hash-bound and CI-green;
- M49 optional delivery package is prepared and CI-green;
- rollback/backup procedure is documented;
- stale repack/build instructions have been removed from governing docs.

The remaining main-track gates require one of two external inputs:

1. **physical RT-AC86U access running the intended ASUS 386_52334 validation runtime**, for K4, general runtime and M49 EJ evidence; or
2. **new matching/later ASUS source evidence**, for the source-backed core feature contracts.

Until one of those exists, keep the candidate **UNVALIDATED** and do not make flashability claims.
