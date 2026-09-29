# ASUS RT-AC86U late-386 runtime lineage: 51967 -> 52294 -> 52334

Date: 2026-09-29  
Workflow: `.github/workflows/asus-runtime-lineage-51967-52294-52334.yml`  
Successful run: `36570687943`  
Commit: `f3119ef1a4e195d5261d2fa1072cb194387ebf3e`  
Artifact: `asus-runtime-lineage-51967-52294-52334`  
Artifact digest: `sha256:6cd8d98896cbb6221051c505fc073764e4d5e5cc9eb4fa3e1773b7f5ea180cbe`

## Pinned official firmware archives

- ASUS 386_51967: `297c02cce8bb227497cfaab46df3c34fefc241649e2cbcbf2509e1396cdb5bdb`
- ASUS 386_52294: `6107d58ad49c767b64a69b125e20349c21a28a4729e67422ef5ac179688d7c32`
- ASUS 386_52334: `e8fd0f3a26db4fe9cf6acb64272d2b78247eb9ccf3890fbdb8daace0bac10d61`

The workflow downloads the official ASUS archives, verifies those SHA-256 values, extracts the root filesystems, builds whole-rootfs manifests and compares protected/security-sensitive components.

## Whole-rootfs results

### 51967 -> 52294

- same: 2650
- changed: 476
- added: 0
- removed: 1 (`/www/ajax_oauth.asp`)

This is a broad runtime refresh, not a small security-only delta.

### 52294 -> 52334

- same: 3065
- changed: 61
- added: 2
- removed: 0

Added:
- `/usr/lib/libipaddr.so`
- `/www/Main_Security_Change_Notification.asp`

### 51967 -> 52334

- same: 2644
- changed: 482
- added: 2
- removed: 1

## Protected/security-sensitive lineage

The protected comparison tracked 142 selected core/kernel-sensitive paths.

### 51967 -> 52294

- changed: 137
- same: 5

This includes a broad rebuild of the shipped Linux 4.1.27 module set and HND/Broadcom modules.

### 52294 -> 52334

Only 9 protected paths changed:

- `/bin/busybox`
- `/lib/modules/4.1.27/extra/dhd.ko`
- `/lib/modules/4.1.27/modules.dep`
- `/sbin/rc`
- `/usr/lib/libcrypto.so.1.1`
- `/usr/lib/libshared.so`
- `/usr/sbin/dnsmasq`
- `/usr/sbin/httpd`
- `/usr/sbin/openvpn`

Notable stable protected component:
- `/usr/lib/libssl.so.1.1` is byte-identical across 51967, 52294 and 52334.

Selected core lineage:

| Path | 51967->52294 | 52294->52334 |
|---|---|---|
| `/bin/busybox` | changed | changed |
| `/sbin/rc` | changed | changed |
| `/usr/sbin/httpd` | changed | changed |
| `/usr/sbin/openvpn` | changed | changed |
| `/usr/sbin/dnsmasq` | same | changed |
| `/usr/lib/libshared.so` | changed | changed |
| `/usr/lib/libcrypto.so.1.1` | changed | changed |
| `/usr/lib/libssl.so.1.1` | same | same |
| `/lib/modules/4.1.27/extra/dhd.ko` | changed | changed |

## Consequences for this project

1. **ASUS 52334 remains authoritative** for `rc`, `httpd`, `dnsmasq`, BusyBox, OpenVPN, `libshared`, crypto libraries and HND/Wi-Fi runtime components. The lineage proves that these continued changing after the final public 386 GPL generation.

2. The 51967 -> 52294 transition rebuilt almost the entire protected module set. Therefore successful compilation of optional K2/K3 modules from the 51997 source lineage is **not** sufficient evidence of compatibility with the final 52334 kernel/runtime.

3. Most shipped kernel modules are byte-identical between 52294 and 52334, but `dhd.ko` is not. This narrows the final runtime drift but does not establish optional-module ABI compatibility.

4. K4 real-router validation remains mandatory before M22/M23/M27/M32/M33 can be activated. The user's current router runs Merlin 386.14_2, so K4 is deferred until ASUS 52334 is actually available on hardware during a controlled validation phase.

5. Source-level Merlin functionality must continue to be grafted as narrow deltas while preserving later ASUS behavior; older Merlin core binaries remain prohibited.

## Download robustness

ASUS uses inconsistent historical CDN filenames. The final workflow first tries the direct CDN pattern and falls back to ASUS's support API to resolve the actual download URL by firmware version, while still enforcing the pinned official SHA-256.
