# RT-AC86U kernel-module build lineage at ASUS GPL 386_51997

Date: 2026-09-29  
Features: M22 NFS, M23 CIFS, M27 ipset, M32 Cake, M33 WireGuard

## Purpose

Establish a reproducible **source/config/toolchain build anchor** for optional kernel modules without weakening the project rule that ASUS 386_52334 remains the final kernel/runtime authority.

The prior image-level ABI probe proved that donor module vermagic alone is insufficient and that neither firmware image exposes useful MODVERSIONS CRC data.

The missing piece was a sufficiently precise RT-AC86U HND build lineage.

That lineage is now pinned.

## Exact source/build anchor

RT-AC86U 386_51997 SDK/blob import:

`RMerl/asuswrt-merlin.ng@c553d8e4b0bf3289683368b0d57172649b030039`

Commit message:

`Merge RT-AC86U binary blobs + SDK from 386_51997`

This follows the general GPL 386_51997 source import documented in:

`docs/source-anchor-51997-import-boundary.md`.

This tree is modified Merlin source, not clean ASUS source. It is used here because it contains the exact RT-AC86U 51997 HND SDK/model profile and the kernel/module source wiring that Merlin built for this hardware generation.

## Exact RT-AC86U HND profile

Pinned model profile:

`release/src-rt-5.02hnd/targets/94908HND/94908HND.RT-AC86U`

Key properties:

- SoC: Broadcom BCM4908;
- profile: `94908HND`;
- userspace architecture: ARM;
- kernel architecture: AArch64;
- libc: glibc;
- kernel generation: Linux 4.1;
- SMP enabled;
- kernel preemption enabled;
- HND router build enabled.

The Asuswrt model target also sets, among other features:

- `NFS=y`;
- `WIREGUARD=y`.

## Exact kernel toolchain

The 51997 HND build rules select:

- directory: `crosstools-aarch64-gcc-5.3-linux-4.1-glibc-2.22-binutils-2.25`;
- prefix: `aarch64-buildroot-linux-gnu`;
- GCC: 5.3.0;
- glibc: 2.22;
- binutils: 2.25.

A public reproducible copy is pinned from:

`SWRT-dev/bcmhnd-toolchains@7710a1e09d994598ac6c2db8ab16dc54ca5aed3d`

Exact toolchain directory tree SHA:

`4239c9b4e94a91ecfafa55005404a829025302d1`

Selected binary/blob fingerprints include:

- GCC real binary: `ccd88f3016081109e8110fbf00537149590028d0`;
- assembler: `c95f02fae9f924f9aa4be58237e6dcb3890af26a`;
- linker: `7d299a7c27a273a88b233960730d2db051ed0538`;
- nm: `02b9fb87128e98d46044ef375c5156cd0cc496c6`;
- objcopy: `cb0504598460af0432ada5a0bad960c3bb856a53`;
- readelf: `295640e983c6abf8ccc31e8ba9002fd1657849ea`;
- strip: `afdadcd3d4eb3bcc1e43db6fa6eb45994ff8cb30`.

This toolchain copy is a build dependency only. It does not become firmware payload.

## Kernel config generation

The RT-AC86U build does not use a hand-written final `.config`.

The Asuswrt build flow starts from:

`release/src-rt-5.02hnd/kernel/linux-4.1/config_base.6a`

and applies the real make macros:

- `KernelConfig`;
- `platformKernelConfig`;
- `extraKernelConfig`;

under the expanded RT-AC86U model variables.

The resulting model config is then passed through Broadcom HND `prek` / kernel `oldnoconfig`.

The CI build anchor must therefore execute those original make macros rather than maintain a copied/manual list of kernel options.

## M22 — NFS

The exact 51997 HND base config already contains the module stack:

- `CONFIG_NFSD=m`;
- `CONFIG_NFSD_V3=y`;
- `CONFIG_LOCKD=m`;
- `CONFIG_LOCKD_V4=y`;
- `CONFIG_NFS_COMMON=y`;
- `CONFIG_SUNRPC=m`;
- `CONFIG_NFS_FS=m`;
- `CONFIG_NFS_V2=m`;
- `CONFIG_NFS_V3=m`.

NFS source is present directly in the HND kernel tree.

Example pinned source:

`fs/nfs/client.c`

blob SHA:

`fdd234206dff990888f7156d3188355a4796b37e`.

### Classification

**51997 SOURCE/CONFIG LINEAGE VERIFIED.**

Remaining gates:

- reproduce the modules with the pinned HND build environment;
- compare dependencies/vermagic/undefined symbols against 52334;
- real-router load and NFS functional test;
- add matching userland/export lifecycle only after kernel gate.

## M23 — CIFS

The exact HND config already contains:

- `CONFIG_CIFS=m`;
- `CONFIG_CIFS_SMB2=y`.

Source is present directly.

Example pinned source:

`fs/cifs/cifsfs.c`

blob SHA:

`fe24e22fc154d43805f6d19a4c0d6532c0c88982`.

### Classification

**51997 SOURCE/CONFIG LINEAGE VERIFIED.**

Remaining gates are build, 52334 ABI/load validation, then userspace/mount integration.

## M27 — ipset

The exact HND config already contains:

- `CONFIG_NETFILTER_XT_SET=m`;
- `CONFIG_IP_SET=m`;
- `CONFIG_IP_SET_MAX=256`;
- bitmap/hash/list ipset families as modules.

Source is present directly.

Example pinned source:

`net/netfilter/ipset/ip_set_core.c`

blob SHA:

`bee479f79ebe055a3d8e4bf65342278777e450d0`.

### Classification

**51997 SOURCE/CONFIG LINEAGE VERIFIED.**

The full kernel family and matching userspace `ipset` must be treated as one API unit.

## M32 — Cake

The exact HND config already contains:

`CONFIG_NET_SCH_CAKE=m`.

The HND kernel path:

`net/sched/sch_cake`

is intentionally wired as a symlink to:

`../../../../router/sch_cake`.

Pinned external Cake source tree:

`release/src/router/sch_cake`

tree SHA:

`c1dd48627755a5488aaf4cf7123ec6baa9b3697c`.

Pinned implementation:

`sch_cake.c`

blob SHA:

`0861c9b1e66c39f9697468cb747762ef239fe265`.

### act_ctinfo boundary

The exact RT-AC86U 51997 source generation does **not** expose a matching `act_ctinfo` implementation in this HND tree.

Therefore:

- Cake itself has a genuine 51997 RT-AC86U build lineage;
- do not silently import `act_ctinfo` from a later kernel/tree;
- if full donor QoS behavior genuinely requires ctinfo, treat ctinfo as a separate later-source/backport project with its own compatibility proof.

### Classification

**CAKE 51997 SOURCE/CONFIG LINEAGE VERIFIED.**  
**ACT_CTINFO NOT PART OF THIS VERIFIED ANCHOR.**

The 52334 HND acceleration interaction remains a mandatory runtime gate.

## M33 — WireGuard

The base config initially has WireGuard disabled, but the RT-AC86U Asuswrt target sets:

`WIREGUARD=y`.

The real `KernelConfig` macro translates this into:

`CONFIG_WIREGUARD=m`

and applies the related IPv6 NAT compatibility options when IPv6 support is enabled.

The complete WireGuard compatibility source is present directly in the exact HND Linux 4.1 tree:

`release/src-rt-5.02hnd/kernel/linux-4.1/net/wireguard/`

tree SHA:

`ccf2aa2b822fc3d8507461f16bd72ba15fc6a2f6`.

Pinned `main.c` blob:

`5435011588913715fe28dc6104640267f9c03550`.

The tree includes Kbuild/Kconfig, compat, crypto and the full module implementation.

### Classification

**51997 SOURCE/CONFIG LINEAGE VERIFIED.**

This does not authorize donor `wireguard.ko`. The module must be rebuilt and then validated against ASUS 52334.

## What this changes

Previous state:

`SOURCE_BUILD_REQUIRED, but exact target build provenance unresolved`.

New state:

`EXACT 51997 RT-AC86U SOURCE + CONFIG + TOOLCHAIN LINEAGE AVAILABLE`.

The remaining uncertainty is concentrated in the post-GPL runtime gap:

- ASUS security/runtime changes after 51997;
- final 52334 kernel configuration details;
- HND/proprietary object expectations;
- module symbol/structure ABI;
- real-router load behavior.

## Build progression

The kernel work now proceeds in four gates.

### Gate K1 — config/toolchain reproduction

CI must:

1. pin `c553d8e4...`;
2. pin toolchain `7710a1e...`;
3. verify exact compiler/blob fingerprints;
4. compile a trivial AArch64 object;
5. execute the original Asuswrt kernel-config make macros under the RT-AC86U model variables;
6. assert the expected NFS/CIFS/ipset/Cake/WireGuard module settings;
7. publish final generated config SHA-256.

### Gate K2 — one-module build smoke

Build one low-risk module family from the exact HND build system, initially ipset or another self-contained module.

Capture:

- module SHA-256;
- ELF architecture;
- vermagic;
- DT/section metadata where applicable;
- imported symbols;
- dependency list.

No firmware overlay is created.

### Gate K3 — all required optional module families

Rebuild only the feature families needed by M22/M23/M27/M32/M33 from the same prepared kernel tree.

No mixing of modules from different configs/toolchains.

### Gate K4 — ASUS 52334 real-router validation

Before activation:

1. confirm stock kernel release/vermagic;
2. validate every required dependency exists or is part of the same built family;
3. stage modules outside boot-critical paths;
4. perform controlled `insmod/modprobe` on the router;
5. record kernel log;
6. unload where supported;
7. run feature-specific functional tests;
8. confirm stock networking/HND acceleration remains stable.

A failure at K4 keeps the feature disabled.

## Runtime-lineage interaction

The separate workflow:

`.github/workflows/asus-runtime-lineage-51967-52294-52334.yml`

is a parallel gate.

If kernel modules or kernel-adjacent components materially changed between the later stock firmware generations, that evidence raises the validation bar and may rule out a 51997-built module despite successful compilation.

## Non-negotiable rule

**Never replace the ASUS 52334 kernel image.**

The objective is optional source-built modules only.

A successful 51997 build is evidence of reproducibility, not evidence of 52334 load compatibility.

## Current classification

**K1 SUCCESS.** Run `36531249746` on `fc60abc315d0bf1e7b6f50beaad879533a67db7a` reproduced the pinned RT-AC86U 51997 source/config/toolchain lineage end-to-end.

Generated config SHA-256:

`9b9c2f93e915ae2b81893839b66080a7d6a4efe5470ab8bed9e6084fea77aed2`

All expected NFS/CIFS/ipset/Cake/WireGuard config assertions passed. The final K1 source-materialization fix preserves the three `src-rt-5.02hnd` symlinks to `../src-rt`; flattening those Git symlink blobs had previously produced 18-byte pointer files instead of the referenced Makefiles.

**K2 SUCCESS.** Run `36556899650` on `2f423c2daa61924001675c04358bac156210c635` rebuilt the coherent ipset family: 17 `ip_set*.ko` modules plus `xt_set.ko`. All are ELF64/AArch64 with vermagic `4.1.27 SMP preempt mod_unload aarch64`. Artifact archive digest: `66b79e481390880a8c1e9c3e57aeca1d498fca8940638be53e9ce1e714afb9f2`. Representative hashes: `ip_set.ko=19c47ab2...`, `ip_set_hash_ip.ko=e1179e36...`, `ip_set_list_set.ko=060bce18...`, `xt_set.ko=6ed89a95...`. No activation or overlay was performed.

**K3 SUCCESS.** Run `36561957525` on `fb0dc42e34a17ddbe50c43672d0e8bf59cdafdb2` rebuilt the remaining optional families from the exact K1 lineage. Artifact `kernel-k3-optional-modules-51997` has archive digest `231f190223dc220008b6aab211cee9a017f9619e40327d3bd19d9ffa424021f3`.

Built modules:
- NFS family: `sunrpc.ko`, `lockd.ko`, `nfs.ko`, `nfsv2.ko`, `nfsv3.ko`, `nfsd.ko`;
- CIFS: `cifs.ko`;
- Cake: `sch_cake.ko`;
- WireGuard: `wireguard.ko`.

Every module is ELF64/AArch64 and reports vermagic `4.1.27 SMP preempt mod_unload aarch64`.

Representative SHA-256:
- `sunrpc.ko`: `b547166600f2e2c0b6ff7356010b7eeec509139b928cc01236e8cba2820b1241`;
- `nfs.ko`: `82f8a84767334ab49a032f5b96f59960cd4e207336b9b8995c9442947631bf5d`;
- `nfsd.ko`: `953d838733e9ab740980ecd5f0a5c76ddbcfafef8c0af1621171551406a8a293`;
- `cifs.ko`: `eb545f7ce5429477f081ef0c4d1c5d1b8eca519d9025afdc2a225417417567b8`;
- `sch_cake.ko`: `159256eb407a76d0ac38b53c3eea36ef74d054b1afe60329a61aad0e5024f24c`;
- `wireguard.ko`: `418f6e212f4d8f3f83142352f462fd870b591602f45b8af0564ecd72c7e5161c`.

The only K3 workflow fix was artifact collection through the Cake symlink (`find -L`); the module itself had already compiled successfully. No activation or overlay change was made.

**K4 is now the active gate.** Controlled real-router validation against ASUS 52334 remains mandatory before any optional kernel feature can become active.
