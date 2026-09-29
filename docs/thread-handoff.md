# New-thread handoff

Updated: 2026-09-29

## Project
**Take official ASUS RT-AC86U 3.0.0.4.386_52334 and restore pinned Merlin 386.14_2 functionality without replacing newer ASUS core/runtime components.**

Repository: `jonsan1969/rt-ac86u-asus-merlin-port`  
Branch: `asus-52334-merlin-port`

## Working-memory rule
Git is the project working memory.

After **every GitHub Action**:
1. inspect the result;
2. update Git docs to the current truth before continuing;
3. when a blocker is solved, remove obsolete troubleshooting history and retain only the final cause/fix if it remains technically relevant;
4. do not preserve a chronological list of failed runs merely for history;
5. fetch an Action log only once and reuse the extracted finding.

Repository state overrides chat recollection. Do not reopen settled probes.

## Non-negotiable architecture
- Final runtime/hardware/security baseline: ASUS RT-AC86U `386_52334`.
- Merlin donor/reference: `386.14_2`, source commit `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`.
- ASUS-first: never replace newer ASUS `rc`, `httpd`, `dnsmasq`, BusyBox, OpenVPN, Dropbear, OpenSSL, kernel/HND or proprietary components with older Merlin binaries.
- Shared-core features require source-delta ports onto ASUS-compatible lineage.
- Image-first changes remain additive or exact/preimage-guarded.
- No flashability claim before repack and real-router/runtime gates pass.
- Never replace the ASUS 52334 kernel image.

## Settled decisions
Do not investigate these again:
- M48 per-IP traffic/cstats: **NO PORT** on pinned 386.14_2 RT-AC86U/HND.
- M35 WiFi Insight: **CANCELLED**.
- M67 speedtest VPN selector: **CANCELLED**.
- M24 OpenVPN umbrella: preserve ASUS; only separately proven deltas proceed.
- M37 IPv6 OpenVPN server: **NO PORT**.
- M39 OpenVPN custom-option storage: **NO PORT**.
- M51 Wireless ACL client names: **NO PORT / ASUS equivalent**.
- M56 editable-entry umbrella: **NO PORT / ASUS equivalent**.
- M12 cru and M14 generic CLI umbrella: **NO generic port**.

Detailed feature state lives in `STATUS.md` and feature-specific contracts.

## Active kernel/module track
Optional features: M22 NFS, M23 CIFS, M27 ipset, M32 Cake, M33 WireGuard.

Exact source/SDK pin:
`RMerl/asuswrt-merlin.ng@c553d8e4b0bf3289683368b0d57172649b030039`

RT-AC86U profile:
`release/src-rt-5.02hnd/targets/94908HND/94908HND.RT-AC86U`

Pinned toolchain:
`SWRT-dev/bcmhnd-toolchains@7710a1e09d994598ac6c2db8ab16dc54ca5aed3d`

Toolchain directory:
`crosstools-aarch64-gcc-5.3-linux-4.1-glibc-2.22-binutils-2.25`

### K1 — SUCCESS
Run: `36531249746`  
Commit: `fc60abc315d0bf1e7b6f50beaad879533a67db7a`  
Generated config SHA-256:
`9b9c2f93e915ae2b81893839b66080a7d6a4efe5470ab8bed9e6084fea77aed2`

K1 reproduced the exact RT-AC86U 51997 source/config/toolchain lineage and passed all NFS/CIFS/ipset/Cake/WireGuard assertions.

Relevant final materialization detail: the three `src-rt-5.02hnd` Makefile entries are Git symlinks to `../src-rt`; they must remain real symlinks rather than flattened pointer files.

Old failed K1 runs and their superseded troubleshooting are intentionally omitted.

### Immediate continuation — K2
Build **one coherent ipset module family** from the exact K1 lineage.

Current Action: `36556708965` — **FAILURE before job start (0 jobs)** after adding the `bcmdrivers` autogen step; this is a workflow syntax/parse blocker, not a kernel result. The underlying kernel blocker remains generation of `bcmdrivers/Kconfig.autogen` before `oldnoconfig`. Fix workflow syntax first, then rerun. The previous `fltr` workspace-link blocker is resolved; do not revisit older K2 failures.

K2 must:
- prepare the real HND Linux 4.1 build tree/config using the same source/profile/toolchain;
- build the ipset kernel module family as one coherent unit;
- publish SHA-256, ELF architecture, vermagic, imported symbols and dependency/module metadata;
- publish artifacts only;
- perform **no activation** and make **no overlay/ports/active.json change**.

K2 success authorizes K3. K2 compilation does **not** prove ASUS 52334 runtime compatibility.

### After K2
- K3: build remaining optional M22/M23/M27/M32/M33 module families from the exact same prepared tree/config/toolchain.
- K4: controlled real-router load/function validation against ASUS 52334.
- Runtime lineage `51967 -> 52294 -> 52334` remains the parallel risk gate.

## Read only as needed
Primary current state:
1. `docs/thread-handoff.md`
2. `STATUS.md`
3. `docs/kernel-build-lineage-51997.md`

Use other feature/source-contract docs only when their feature becomes active.
