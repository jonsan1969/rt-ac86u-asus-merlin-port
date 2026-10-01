Current checkpoint while M07 revalidation runs: stock ASUS 52334 probe `36864164972` proved `/www/user -> /dev/null`, correcting the prior mistaken assumption that stock supplied `/var/wwwext`. Merlin 386.14_2 `rootprep_arm.sh` proves the intended image-build delta is `/www/user -> /tmp/var/wwwext`. The overlay engine now has a fail-closed `symlink_replace` operation that only replaces an exact expected final symlink; `ports/active.json` uses it to replace `/dev/null` with `/tmp/var/wwwext`, and the separate manifest validator recognizes only `replace_exact` with explicit old/new targets. M07 is temporarily IN PROGRESS until guarded-overlay run `36864603084` and full repack run `36864603300` finish. Earlier runs `36864562856`, `36864544562`, `36864544463` are superseded schema-gate failures from before `symlink_replace` was added to `check_port_overlay.py`; do not troubleshoot them. All prior stock/repack gates and optional Nano/SCP (`36863705618`) plus dormant AMTM (`36864039573`) remain established.

Run `36664684285` establishes the exact capacity boundary. Excluding `ouiDB.json`, `rtac86u-ntpd`, `scp`, `nano`/`ncurses`, and `chart.min.js` produces `72,122,368`-byte UBIFS and exact `74,711,040`-byte UBI / `570` PEB. All other tested small fifth removals remained `571` PEB. Its log has been fetched exactly once; never fetch it again. These five payload groups must leave the built-in rootfs overlay and become optional/JFFS-delivered; remove or redesign any built-in UI references that would otherwise become broken before running the real repack gate.

Run `36663568334` minimal-fourth-group matrix: atop `ouiDB+ntpd+scp`, removing `wsdd2` stays `573` PEB, `chart` gives `572`, `nano/ncurses` gives `571`, and `qrcode` stays `573`. Its log has been fetched exactly once; never fetch it again. Best measured candidate is exactly 1 PEB over the immutable 570-PEB span. Measure only the smallest extra payloads atop the 571-PEB candidate next.

Run `36663266938` targeted three-group matrix: `no_oui_ntpd_scp=573` PEB, `no_oui_ntpd_nano=574`, `no_oui_ntpd_wsdd2=575`, `no_oui_ntpd_chart=575`. Its log has been fetched exactly once; never fetch it again. Best candidate is only 3 PEB over the immutable span. Measure the smallest fourth group atop `ouiDB+ntpd+scp`; do not broaden removals blindly.

Run `36662877291` capacity matrix proves no tested one- or two-group footprint reduction fits: full `585` PEB; `no_oui=580`, `no_ntpd=580`, `no_scp=581`, `no_nano=582`, `no_oui_ntpd=576`, `no_oui_scp=577`, `no_ntpd_scp=577`. Its log has been fetched exactly once; never fetch it again. At least a third payload reduction is required; measure targeted three-group candidates next.

Run `36660637095` reconfirms the full active overlay under pinned zlib at `74,027,008`-byte UBIFS and `76,677,120`-byte UBI / `585` PEB: exactly 15 PEB over the immutable span. Its log has been fetched exactly once; never fetch it again. The next Action must be a capacity matrix, not another identical full-overlay retry.

Run `36659212017` closes the LZO experiment: LZO is materially worse (`81,264,640`-byte UBIFS; `84,148,224`-byte UBI / `642` PEB) than zlib (`585` PEB). Its log has been fetched exactly once; never fetch it again. Keep zlib and the immutable 570-PEB span. Largest repo add-only payloads are `ouiDB.json` 1,285,908 B, `rtac86u-ntpd` 925,720 B, `scp` 663,424 B, `nano` 223,780 B and `libncurses.so.6.0` 222,880 B. Continue by reducing/optionalizing feature payload footprint; do not enlarge the partition or replace the ASUS kernel.

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

### K2 — SUCCESS
Run: `36556899650`  
Commit: `2f423c2daa61924001675c04358bac156210c635`  
Artifact: `kernel-k2-ipset-51997`, archive digest `sha256:66b79e481390880a8c1e9c3e57aeca1d498fca8940638be53e9ce1e714afb9f2`.

K2 rebuilt the coherent ipset family from the exact K1 lineage: 17 `ip_set*.ko` modules plus `xt_set.ko`. Every module is ELF64/AArch64 and reports vermagic `4.1.27 SMP preempt mod_unload aarch64`. Generated config SHA-256 remains `9b9c2f93e915ae2b81893839b66080a7d6a4efe5470ab8bed9e6084fea77aed2`.

Representative SHA-256:
- `ip_set.ko`: `19c47ab22f38c50e3ddfea153e54c10e4c4ecb244fe1fa77e225c0bca94162b6`
- `ip_set_hash_ip.ko`: `e1179e36ebad16843537338fae3134f75c672161a1702f518a64cebeab1cb93d`
- `ip_set_list_set.ko`: `060bce188e4f4ac42064e4c9774f637dcee84b0cea5bb0d3e858a0ae28464cf5`
- `xt_set.ko`: `6ed89a951afdabf5b93158d7ef8edc0c7804b51df0c98f3f8c64500a47fb0b3a`

No activation or overlay change was made. All intermediate K2 troubleshooting is intentionally omitted now that K2 is solved.

### K3 — SUCCESS
Run: `36561957525`  
Commit: `fb0dc42e34a17ddbe50c43672d0e8bf59cdafdb2`  
Artifact: `kernel-k3-optional-modules-51997`, archive digest `sha256:231f190223dc220008b6aab211cee9a017f9619e40327d3bd19d9ffa424021f3`.

K3 rebuilt the remaining optional families from the exact K1 lineage:
- NFS: `sunrpc.ko`, `lockd.ko`, `nfs.ko`, `nfsv2.ko`, `nfsv3.ko`, `nfsd.ko`;
- CIFS: `cifs.ko`;
- Cake: `sch_cake.ko`;
- WireGuard: `wireguard.ko`.

All are ELF64/AArch64 with vermagic `4.1.27 SMP preempt mod_unload aarch64`. No activation or overlay change was made.

### K4a — READY / CI-VALIDATED
Workflow run: `36562651589` — SUCCESS.

The repo now contains `scripts/k4-router-preflight.sh`, a read-only physical-router collector. CI verifies POSIX syntax and rejects module loading, NVRAM mutation, JFFS writes, service mutation, reboot and flash/mtd operations.

K4a writes only below `/tmp` and collects firmware/kernel/module/symbol evidence before any candidate module is allowed to load.

### K4 hardware gate — DEFERRED UNTIL 52334 RUNTIME IS AVAILABLE
The user's physical RT-AC86U currently runs the final Asuswrt-Merlin 386.14_2, **not** ASUS 386_52334.

Therefore the current router cannot provide the required ASUS 52334 runtime evidence for K4. Do not ask the user to flash stock 52334 merely to advance development.

The K4a read-only collector remains ready and CI-validated, but final K4a/K4b compatibility testing is deferred until ASUS 52334 is actually running on hardware (for example during a controlled candidate/validation phase).

Do **not** load K2/K3 modules on the current Merlin runtime and do not treat a Merlin-side load test as proof of ASUS 52334 compatibility.

## Active firmware/repack track

### ASUS late-runtime lineage — SUCCESS
Run: `36570687943`.

The official `51967 -> 52294 -> 52334` comparison is complete. ASUS 52334 remains authoritative for protected/core runtime. See `docs/asus-runtime-lineage-51967-52294-52334.md`.

### 52334 repack geometry + final WFI contract — SUCCESS
- Geometry probe run: `36571407058`.
- Final WFI-token proof run: `36572950163`.
- Contract: `docs/firmware-repack-52334.md`.

Pinned stock geometry:
- immutable prefix: `0x360000` / 3,538,944 bytes;
- UBI: 570 PEBs × 131,072 bytes;
- UBIFS LEB: 126,976 bytes;
- volume: dynamic/autoresize `rootfs_ubifs`;
- final Broadcom WFI token: 20 bytes, BCM4908/NAND128.

### Stock ASUS 52334 semantic repack round-trip — SUCCESS
Run: `36593572826`  
Commit under test: `4b6ce8f675d7cdfa54b7ba71257bc645369a1a63`  
Artifact: `firmware-stock-repack-roundtrip-52334`  
Artifact digest: `sha256:8fddaed20326f10435d383a59006d33075c90ee3938939e642d1e5638b6107fe`.

Result:
- 3,992 original semantic rootfs entries;
- 3,992 rebuilt entries;
- 0 semantic mismatches;
- rebuilt UBIFS = 568 LEBs / 72,122,368 bytes;
- rebuilt UBI = exactly 570 PEBs / 74,711,040 bytes;
- no external UBI padding;
- final WFI validates.

This proves the **stock repack baseline only**, not flashability.

### Immediate continuation — ACTIVE OVERLAY REPACK GATE
Do **not** revisit the solved stock repack work.

Active-overlay authorization root cause is now fully resolved in workflow code. Run `36609601459` proved all 49 guarded overlay entries apply, then exposed the leading-slash path-domain mismatch. Run `36619600961` subsequently hung in step 7 because the corrected absolute parent walk reached `Path('/')`, whose parent is itself; the loop had no root termination. Commit `62dd48f45000ff8eb7b03ef360b3ffa8311cbeaf` terminates at filesystem root (`q == q.parent`). Neither case reached firmware repack semantics. Do not fetch logs for `36607825944` or `36609601459` again; `36619600961` required no log fetch for the hang diagnosis.

Run `36630738831` establishes the current capacity blocker: the 49-entry overlay and manifest authorization pass, but the pinned zlib rebuild produces UBIFS `74,027,008` bytes and UBI `76,677,120` bytes / `585` PEB, which cannot fit the immutable 570-PEB firmware span. Its log has been fetched exactly once; never fetch it again. The proven stock workflow permits a shorter UBI to be padded to 570 PEB, so the next software gate is to try UBIFS-native LZO compression and accept it only if the image fits <=568 data PEB and the final padded UBI remains exactly 570 PEB with identical re-extracted semantics and protected-file hashes.

Next task is exactly:

**Pass the current guarded active overlay through the proven 52334 extract → guarded apply → UBIFS/UBI repack → WFI → re-extract pipeline.**

The gate must prove:
1. post-repack semantic changes are exactly manifest-authorized overlay targets plus unavoidable parent directories;
2. protected ASUS `rc`, `httpd`, `dnsmasq`, BusyBox, OpenVPN, Dropbear, OpenSSL, kernel/HND and proprietary components remain stock-authoritative and byte-identical unless a separately approved source-delta gate exists;
3. existing guarded feature contracts still pass on the re-extracted image;
4. final UBI remains exactly 570 PEBs and final WFI validation passes;
5. K2/K3 optional modules are **not** added or activated;
6. no image is called flashable until this gate and the deferred real-router/runtime gates pass.

The user's physical RT-AC86U still runs Merlin 386.14_2. Do not ask for a stock 52334 reflash merely to advance development.

M27/ipset uses the successful K2 family; M22/M23/M32/M33 use the successful K3 family, but all remain build-only until deferred K4 validation.

## Read only as needed
Primary current state:
1. `docs/thread-handoff.md`
2. `STATUS.md`
3. `docs/kernel-build-lineage-51997.md`

Use other feature/source-contract docs only when their feature becomes active.
