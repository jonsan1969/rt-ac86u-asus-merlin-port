# New-thread handoff

Updated: 2026-09-29

## Project sentence

**Take the latest official ASUS RT-AC86U 386_52334 firmware and make it Merlin again.**

The final architecture is ASUS-first, not Merlin-first.

## Working rule from the user

**Do not stop unless input from the user is genuinely required.**

When an Action finishes:

- green: inspect result/artifacts and continue immediately;
- red: inspect logs, fix the real cause or classify the feature correctly, push the minimal change and continue;
- do not stop merely to narrate the next intended step.

The previous thread became too long and repeatedly timed out. Do not restart already-settled work. Read the current repo state first and continue from the Immediate continuation section below.

## Non-negotiable technical rules

- Final runtime/hardware/security baseline: ASUS RT-AC86U `3.0.0.4.386_52334`.
- Merlin donor/reference: Asuswrt-Merlin `386.14_2`.
- Pinned Merlin source commit: `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`.
- Never replace newer ASUS `rc`, `httpd`, `dnsmasq`, BusyBox, OpenVPN, Dropbear, OpenSSL, kernel/HND or proprietary components with older Merlin binaries.
- Shared-core features are source-delta ports onto an ASUS-compatible source/build lineage.
- Image-first work must remain additive or exact/preimage-guarded.
- No flashability claim before repack + real-router/runtime gates pass.

## Repository

Repository: `jonsan1969/rt-ac86u-asus-merlin-port`

Branch: `asus-52334-merlin-port`

Snapshot base HEAD immediately before this handoff update:

`2fbd983a7a71c88faa6414b5df968beba4e1e079`

That commit fixes the K1 toolchain host-library path.

Read these first in the next thread:

1. `docs/thread-handoff.md`
2. `STATUS.md`
3. `docs/merlin-feature-inventory.md`
4. `docs/source-base-strategy.md`
5. `docs/source-anchor-51997-import-boundary.md`
6. `docs/kernel-build-lineage-51997.md`
7. `docs/jffs-core-source-patch-series.md`
8. `ports/active.json`

## Major completed image-safe/runtime work

Do not redo these.

- DNS Director phase 1 — SUCCESS.
- JFFS image-safe shell/profile/helper foundation — SUCCESS.
- Nano + isolated ncurses bundle — SUCCESS.
- Conntrack tuning — SUCCESS.
- Traffic-history persistence — SUCCESS.
- Global monthly traffic — SUCCESS.
- Wireless Site Survey — SUCCESS.
- Temperature/performance page — SUCCESS.
- WiFi QR codes — SUCCESS.
- Local OUI database — SUCCESS.
- System/Wireless Log no-auto-logout — SUCCESS.
- safe System Log enhancements — SUCCESS.
- dual-radio WiFi icon — SUCCESS.
- WINS UI adaptation M20 — SUCCESS.
- SCP M16 — SUCCESS as add-only static AArch64 `/usr/bin/scp`, ASUS dbclient retained.
- M12 `cru` — SUCCESS / NO PORT; ASUS script retained.
- M14 generic enhanced CLI set — SUCCESS / NO generic port.
- M48 per-IP traffic/cstats — **NO PORT** for pinned 386.14_2 on RT-AC86U/HND; do not start this investigation again.
- M51 Wireless ACL client names — NO PORT, ASUS newer equivalent.
- M56 editable-entry umbrella — NO PORT, ASUS already supplies equivalent edit flows.
- M35 WiFi Insight — CANCELLED, donor itself lacks full runtime.
- M67 speedtest VPN selector — CANCELLED, outside pinned donor.

Latest guarded active-overlay validation/status is recorded in `STATUS.md`; protected ASUS core binaries remain non-replaced.

## Dormant foundations already staged

These are not full feature SUCCESS yet, but the safe binary foundations are already done.

### M21 wsdd2

- add-only `/usr/sbin/wsdd2`;
- SHA-256 starts `89a4309c...`;
- ARM32 EABI5 donor ELF;
- exact stock loader/libc dependencies;
- QEMU load passed;
- no startup/config reference in overlay.
- Full feature waits on generic M01-M03 JFFS lifecycle hooks.
- Design: add-only binary + reconcile wrapper driven by `services-start`, `service-event(-end)`, `post-mount`, `services-stop`; **no M21-specific ASUS rc patch**.
- See `docs/wsdd2-jffs-lifecycle-plan.md`.

### M29 local NTP daemon

- add-only `/usr/libexec/rtac86u-ntpd`;
- static AArch64/no PT_INTERP;
- SHA-256 starts `6885069b...`;
- QEMU option-surface passed;
- no startup/config reference.
- Full M29 waits on JFFS lifecycle + dnsmasq/postconf integration.
- See `docs/local-ntp-jffs-adaptation.md`.

## Source contracts now defined

Do not reprobe donor behavior unless implementing/fixing these contracts.

### JFFS/addon core

- M01-M03/M41/M42 lifecycle patch series:
  - `docs/jffs-core-source-patch-series.md`
- M04 custom config/postconf:
  - `docs/custom-config-postconf-source-contract.md`
- M10/M60 hardened JFFS backup/restore:
  - `docs/jffs-backup-restore-source-contract.md`
- M08/M09 AMTM/Entware after JFFS:
  - `docs/amtm-entware-after-jffs.md`

Important: the four helper implementations in `shared/scripts.c` are inherited from clean ASUS lineage and stable. The risky work is exposure/defaults/call sites, not replacing `scripts.c`.

### Network/services

- M11 custom DDNS:
  - `docs/custom-ddns-source-contract.md`
- M18/M19 Samba simpler naming + Master Browser:
  - `docs/samba-merlin-controls-source-contract.md`
- M29/M30 local NTP + redirect:
  - `docs/local-ntp-jffs-adaptation.md`
- M36 IPv6 DNS Director Custom 1-3:
  - `docs/dns-director-ipv6-custom-source-contract.md`
- M66 Prevent Auto DoH/DDR/Private Relay:
  - `docs/prevent-auto-doh-source-contract.md`
- M68 outbound LAN allowed logging:
  - `docs/outbound-lan-logging-source-contract.md`

### VPN

- M38 OpenVPN DNS Exclusive:
  - `docs/openvpn-dns-exclusive-source-contract.md`
- M25/M40 VPN Director/routing:
  - `docs/vpn-director-routing-source-contract.md`
- M57 Advanced VPN Status:
  - `docs/advanced-vpn-status-source-contract.md`

M38 policy-mode DNS must share the final M25/M40 policy owner; do not build a second policy parser.

### HTTPD/read-only UI backends

- M43 System Info:
  - `docs/system-info-source-contract.md`
  - classification: small C backend + add-only UI after backend.
- M46 QoS Stats:
  - `docs/qos-stats-source-contract.md`
  - classification: read-only tc/BWDPI backend + add-only UI.
- M64 Traditional QoS overhead/download stats:
  - `docs/qos-overhead-stats-source-contract.md`
  - download stats are folded into M46, not a second handler.
- M52 wireless-client auto-refresh:
  - `docs/wireless-client-refresh-source-contract.md`

## Source strategy advanced materially in the previous thread

The source problem is no longer only "45956 is old".

### Layer A — clean ASUS ancestry

Clean ASUS 386.45956 mirror:

`blackfuel/asuswrt-rt-ac86u@a9179fc9329565dea0f7c5c7648fe8ad49ceaaf6`

Use only to establish clean-ASUS ancestry.

### Layer B — exact general GPL 386_51997 import boundary

Merlin history pin:

`28daa82377c5a9a68bf2c79aea429323a891ac08`

Parent:

`bf59d7ec4339d3c1eb71fe03209243947084e754`

Commit message:

`Merged with GPL 386_51997 + RT-AC88U SDK and binary blobs`

This gives the exact late shared-source shape, but it is still a Merlin tree, not clean ASUS.

### Layer C — exact RT-AC86U 386_51997 SDK/blob import

Pin:

`c553d8e4b0bf3289683368b0d57172649b030039`

Parent:

`2b13c8cc8cf821fa774371c18e3a68a8b6965ad8`

Commit message:

`Merge RT-AC86U binary blobs + SDK from 386_51997`

Use this for RT-AC86U HND model/build/kernel archaeology.

See:

`docs/source-anchor-51997-import-boundary.md`

### Layer D — official ASUS runtime authority

Compare official runtime lineage after the last GPL generation:

`51967 -> 52294 -> 52334`

Workflow:

`.github/workflows/asus-runtime-lineage-51967-52294-52334.yml`

This is the risk gate for rebuilding protected components from 51997-era source.

## 51997 import-boundary Action status

The old `source-anchor-51997-import-boundary.yml` had a workflow-parse/startup failure: failed runs showed zero jobs and the UI/API used the workflow path as its name.

That was repaired in commit:

`e871d6ec1ba449aead095e87f97e50c26da403db`

Verification run:

`36522206460` — **SUCCESS**

So the exact general-GPL and RT-AC86U SDK/blob import provenance is now CI-locked.

## Optional kernel/module source-build track

Features:

- M22 NFS
- M23 CIFS
- M27 ipset
- M32 Cake
- M33 WireGuard

Prior image ABI CRC probing proved donor `.ko` transplant cannot be justified.

The better source-build anchor is now documented in:

`docs/kernel-build-lineage-51997.md`

### Exact K1 inputs

Source/SDK:

`RMerl/asuswrt-merlin.ng@c553d8e4b0bf3289683368b0d57172649b030039`

RT-AC86U profile:

`release/src-rt-5.02hnd/targets/94908HND/94908HND.RT-AC86U`

Kernel generation:

Linux 4.1 / BCM4908 / 94908HND

Pinned toolchain repo:

`SWRT-dev/bcmhnd-toolchains@7710a1e09d994598ac6c2db8ab16dc54ca5aed3d`

Toolchain directory:

`crosstools-aarch64-gcc-5.3-linux-4.1-glibc-2.22-binutils-2.25`

Compiler:

GCC 5.3.0 / AArch64 / glibc 2.22 / binutils 2.25

The exact target/config lineage already contains:

- NFS/NFSD/SUNRPC/LOCKD modules;
- CIFS + SMB2;
- ipset core/families + xt_set;
- `CONFIG_NET_SCH_CAKE=m`;
- WireGuard source and target-driven `CONFIG_WIREGUARD=m`.

`act_ctinfo` is **not** part of this verified 51997 anchor.

### K1 first run failure and fix

First K1 run:

`36516591962` — **FAILURE**

Actual failure:

the pinned GCC executable started and reported 5.3.0, but its `cc1` host process could not load:

`libmpc.so.3`

This library is present inside the pinned toolchain at:

`.../usr/lib/libmpc.so.3`

So this was a host-library search-path problem on Ubuntu 24.04, not a source/kernel incompatibility.

Minimal fix commit:

`2fbd983a7a71c88faa6414b5df968beba4e1e079`

The smoke step now exports:

`LD_LIBRARY_PATH="$DIR/usr/lib:$LD_LIBRARY_PATH"`

Second K1 run:

`36522285065` — **FAILURE**

The host-library fix worked: the exact GCC 5.3 compiler smoke step now passes and produces an AArch64 object.

The failure moved to the next step, **Extract original Asuswrt kernel-config macros**.

Actual traceback:

`FileNotFoundError: work/source/release/src-rt-5.02hnd/Makefile`

So the remaining K1 problem is the workflow's source materialization/sparse-checkout pattern, not the compiler, kernel source lineage, or toolchain.

Preferred next fix: stop relying on the fragile no-cone sparse checkout for K1's few files. Fetch `c553d8e4...` with `--filter=blob:none`, then materialize the exact required build/config/source files with `git show <sha>:<path>` into `work/source/<path>`, followed immediately by explicit `test -f` assertions before macro extraction.

Do not start K2 until K1 is green.

## Immediate continuation

### 1. Fix K1 source materialization, then rerun

Run `36522285065` is already diagnosed.

What is proven:

- pinned toolchain download is correct;
- GCC 5.3 starts;
- pinned `usr/lib` host libraries fix `cc1`;
- compiler smoke now passes;
- failure is only that the sparse checkout did not materialize `release/src-rt-5.02hnd/Makefile`.

Next concrete change:

1. keep the exact source pin `c553d8e4...`;
2. replace K1's fragile source sparse-checkout step with deterministic exact-path materialization, preferably `git show <sha>:<path> > work/source/<path>` for the small K1 file set;
3. add explicit `test -f` checks for:
   - `release/src-rt-5.02hnd/Makefile`;
   - `platform.mak`;
   - `target.mak`;
   - RT-AC86U profile;
   - `config_base.6a`;
   - the individual NFS/CIFS/ipset/WireGuard/Cake source files used by assertions;
4. push the minimal workflow fix;
5. inspect the new Action automatically.

When K1 becomes green:

- inspect artifact `kernel-build-anchor-51997`;
- verify compiler smoke object is AArch64;
- verify generated RT-AC86U config;
- record config SHA-256 and feature settings;
- update `STATUS.md` / `docs/kernel-build-lineage-51997.md` to K1 verified;
- continue immediately to K2.

### 2. K2 — real one-module build smoke

Preferred initial family: **ipset**, because it has a clear 51997 kernel lineage and can exercise real module build machinery without touching the running firmware.

K2 should:

1. fetch the exact `c553d8e4...` HND source/build tree;
2. use the exact pinned GCC 5.3 toolchain and host-library path;
3. execute the real RT-AC86U config preparation/oldnoconfig/required Broadcom build preparation;
4. build one coherent ipset module family, not an arbitrary donor `.ko`;
5. publish:
   - SHA-256;
   - ELF architecture;
   - vermagic;
   - module dependencies;
   - undefined/imported symbols;
   - section metadata;
6. do **not** add it to `ports/active.json`;
7. compare the built module's expectations with official ASUS 52334 runtime/kernel evidence;
8. keep activation deferred until K4 real-router validation.

### 3. Then K3/K4

K3: build the remaining required optional module families from the same config/toolchain.

K4: controlled real-router load/function tests against ASUS 52334. A successful 51997 build is not proof of 52334 runtime compatibility.

### 4. Parallel source/runtime risk work

After K1/K2 is moving cleanly, continue the official ASUS runtime-lineage comparison `51967 -> 52294 -> 52334` and use that evidence to decide whether any protected core rebuild from 51997 is acceptable.

## Important anti-loop reminders

Do not restart these investigations:

- M12 cru — settled NO PORT.
- M20 WINS — already SUCCESS.
- M21 wsdd2 binary compatibility — already proven/staged; waits on generic JFFS lifecycle.
- M48 cstats — settled NO PORT for HND donor.
- generic Merlin BusyBox command transplant — forbidden and already classified.
- stock Dropbear SCP applet — absent; M16 standalone SCP is already SUCCESS.
- WiFi Insight — cancelled.
- speedtest VPN selector — outside donor baseline.

## Flashable firmware

Still **IN PROGRESS**.

The project has not yet crossed:

- protected-core source rebuild gates;
- optional-module real-router ABI/load gates;
- final firmware repack;
- boot/runtime validation;
- rollback/recovery validation.

Do not describe the current branch as flash-ready.
