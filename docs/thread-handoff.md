K4 exact module dependency closure is now SUCCESS: run `36976006891`, artifact `k4-module-dependency-closure` id `11212893202`, ZIP digest `sha256:55df58d1682d82e8de79030f0c1e425beced4d17632013ba405271e1b65553b7`, expires 2026-12-31. The gate analyzes the exact preserved 18 K2 + 9 K3 modules by matching undefined ELF symbols to `__ksymtab_*` exports. It finds no cross-family optional-module dependency and no declared external module dependency. NFS order is `sunrpc -> lockd -> nfs -> nfsd -> nfsv2 -> nfsv3`, unload reverse; CIFS is standalone. This does not prove 52334 kernel-symbol availability; K4a + physical load remain mandatory. Log for `36976006891` was fetched exactly once.

K4 dependency closure run `36975779541` is SUCCESS as a modinfo/inventory diagnostic, but its modinfo-only load order must NOT be used for physical K4. All 27 exact K2/K3 modules were found and verified, and no declared external `depends=` entries were present for CIFS/NFS. However NFS sorted with `sunrpc` after dependants, proving the separate K3 builds do not encode the true relation in modinfo. Active next gate: derive inter-module dependencies from undefined ELF symbols matched to other modules' `__ksymtab_*` exports; reject cycles/cross-family coupling and use only that result for K4 order. Log for `36975779541` was fetched exactly once.

K4 exact-module dependency closure run `36975679917` is a superseded tooling failure only. It successfully downloaded preservation run `36972221014`, found 18 K2 + 9 K3 modules and verified the pinned K3 hashes. The Python analyzer then saw zero files because it used non-recursive `glob("*.ko")` below nested artifact directories. Fix is `rglob("*.ko")`. No dependency/ABI conclusion was reached from the failed run. Its log was fetched exactly once and must never be fetched again.

Latest hardware-preservation checkpoint: run `36972221014` is SUCCESS on head `5c79c38395ed32d497d590c9b730a94e4bd0bb6d`. It verifies and carries the official ASUS 386_52334 stock image, exact UNVALIDATED candidate, K2/K3 modules, and the ipset/WireGuard/Cake temporary K4 userspace companions. Artifact `11211903638`, ZIP digest `sha256:02b59148fd8b37c48fc847afa73b2501667aaebc956f8eb9259764ca352b8670`, expires 2026-12-31. Firmware identity remains the internal .w SHA-256.

K4 Cake userspace companion is now SUCCESS: run `36972043724` builds c553's CAKE-aware `tc` from iproute2 5.11.0 with the pinned ARM32 HND toolchain. CI proves ARM32/EABI5, `cake_qdisc_util` is linked, `tc -V` reports 5.11.0, the local `cake help` parser exposes CAKE options without qdisc mutation, and the Unix-preserving tarball re-verifies after extraction. Artifact `k4-cake-userspace-51997` id `11212107182`, ZIP digest `sha256:4bc49da98adc4a32a0945a96a335aaf7b285471ba514dd330ac1fb5af898687b`, expires 2026-12-31. Failed run `36971869155` was only a subdirectory-build include-path mistake; its log was fetched once and must never be fetched again.

K4 WireGuard userspace companion is now SUCCESS: run `36971511361` builds exact c553 `wireguard-tools` / `wg` 1.0.20200827 with the pinned ARM32 HND GCC 5.3/glibc 2.22 toolchain. QEMU `wg --version` passes and the Unix-preserving tarball re-extraction verifies executable/manifest integrity. Artifact `k4-wireguard-userspace-51997` id `11211229289`, ZIP digest `sha256:2a5d5ab85615a7cd069f58812986322f9b875b08b8a6410b268498c6773038f4`, expires 2026-12-31. It remains temporary /tmp smoke-test userspace only.

K4 ipset userspace transport is now closed correctly: run `36971390631` is SUCCESS and publishes a Unix-preserving tarball. CI re-extracts it and verifies executable bits, libipset/libmnl symlinks and manifest hashes. Artifact `k4-ipset-userspace-51997` id `11212280337`, ZIP digest `sha256:d935dfde9f58b1e072d6780d83613abfef825121598924012f39aa4b88a2b7e5`, expires 2026-12-31. Preservation run `36971216870` failed only because it tested executable/symlink metadata on loose GitHub artifact files; that log was fetched once and must never be fetched again. The preservation workflow is being switched to verify/extract the tarball instead.

K4 ipset userspace companion is SUCCESS: run `36970920179` builds exact 51997 `ipset-7.6` + `libmnl-1.0.4` with the pinned ARM32 HND GCC 5.3/glibc 2.22 toolchain. The bundled real ELF is ARM32/EABI5 with closure `ipset.real -> libipset.so.13 -> libmnl.so.0`; QEMU reaches `ipset v7.6, protocol version: 7`. Artifact `k4-ipset-userspace-51997` id `11211646518`, ZIP digest `sha256:9f286d86e20e9d97a2782b29a65b9e36313f3ff5d8103860048f406131240890`, expires 2026-12-31. It is temporary /tmp K4 userspace only and does not load modules. Superseded ipset-userspace failure logs are consumed; never fetch those run logs again.

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

Run `36972221014` is SUCCESS.

Artifact: `hardware-validation-bundle-eac8a777`  
Artifact id: `11211903638`  
ZIP digest: `sha256:02b59148fd8b37c48fc847afa73b2501667aaebc956f8eb9259764ca352b8670`  
Expiry: 2026-12-31.

The workflow verifies the official ASUS 386_52334 stock image, exact candidate hash/size, K2/K3 module identities, the Unix-preserving ipset, WireGuard and Cake K4 companions, and carries the current collectors, hardware-evidence verifier, M49 response verifier, physical sequence and recovery/handoff documents.

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

Candidate evidence skeleton revalidation: run `36968749755` — SUCCESS after adding the host-side evidence-verifier prerequisite. No mutation capability was introduced.

## Hardware evidence intake gate

Host-side verifier:

`scripts/verify-hardware-evidence.py`

Latest CI: runtime collector `36968903987` — SUCCESS; evidence verifier `36968903989` — SUCCESS.

It fail-closed cross-checks the K4a and general runtime archives for the current candidate binding, RT-AC86U identity, ASUS 386_52334 identity, AArch64/kernel consistency, required read-only safety markers and required evidence files. Candidate mode additionally requires exact hashes for `/usr/sbin/helper.sh`, `Tools_OtherSettings.asp`, `Advanced_Wireless_Survey.asp`, `qrcode.min.js`, `logFilter.json`, plus the `user1/user20` aliases. CI proves rejection of a changed canary, wrong candidate SHA, Merlin runtime identity, unavailable kallsyms and unsafe tar traversal.

A PASS is only a baseline evidence-intake PASS. It does not authorize module loading, prove M49 EJ dispatch or make the candidate flashable.

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

Host-side response verification is READY: `scripts/verify-m49-ej-response.py`, CI run `36969317440` — SUCCESS. It distinguishes real multiline rstats handler output from the page's single-line fallbacks and rejects login/wrong-page/raw-token responses.

The remaining gate is physical/runtime proof that ASUS 386_52334 stock `httpd` EJ-expands:

`<% bandwidth("monthly"); %>`

through the active custom user-slot path.

Capture the authenticated candidate `userN.asp` response body and require `M49_EJ_RESPONSE_PASS`. Do not replace that runtime proof with more static CI.

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

## Physical validation sequence

The future physical work is now explicitly separated in `docs/physical-validation-sequence.md`.

Key rule:

- official stock ASUS 386_52334 is the first kernel/K4 baseline;
- candidate runtime must subsequently pass the candidate-canary evidence mode;
- stock K4 evidence does not prove candidate WebUI/JFFS behavior;
- candidate WebUI canaries do not authorize optional kernel modules;
- M49 EJ dispatch remains its own active HTTP/runtime test.

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
