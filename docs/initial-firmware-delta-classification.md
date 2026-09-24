# Initial firmware delta classification

Date: 2026-09-24

This document records the first image-level comparison between:

- ASUS RT-AC86U `3.0.0.4.386_52334`
- Asuswrt-Merlin RT-AC86U `386.14_2`

The comparison is evidence for classification only. It is **not** a copy list.

## Verified inputs

### ASUS

- Archive: `FW_RT-AC86U_300438652334.zip`
- Archive SHA-256: `e8fd0f3a26db4fe9cf6acb64272d2b78247eb9ccf3890fbdb8daace0bac10d61`
- Image: `RT-AC86U_3.0.0.4_386_52334-gd500e53_ubi.w`
- Image size: 78,250,004 bytes
- Image SHA-256: `1b4fe984e13afdf0a69c11bda759f3222822e12f5b8c929da33f334f2cc7483f`

### Merlin

- Archive: `RT-AC86U_386.14_2.zip`
- Archive SHA-256: `1dedab53b08b93c529920c791291d04e36089a9c85d672a5a0fff9dea45bb49a`
- Image: `RT-AC86U_386.14_2_ubi.w`
- Image size: 82,706,452 bytes
- Image SHA-256: `ebe1491f8edb3f81ca4077d482ffca33d34ae7dfe245bbff7843684dbe9b7728`

Both images expose the UBI container at offset `0x360000`. Binwalk extracted the corresponding `rootfs_ubifs` trees successfully.

## Root filesystem comparison

Path classification:

| Class | Count |
|---|---:|
| IDENTICAL | 1,992 |
| ASUS_ONLY | 60 |
| MERLIN_ONLY | 267 |
| DIFFERENT | 1,939 |

Regular files:

- ASUS: 3,128
- Merlin: 3,473

Extracted rootfs byte totals:

- ASUS: 126,856,016
- Merlin: 135,876,137

The large `DIFFERENT` count means the port cannot be implemented by copying a small set of Merlin binaries over ASUS 52334.

## C — shared core programs: source-level port required

These paths exist in both images but differ materially and must **not** be replaced with the older Merlin binary:

| Path | ASUS size | Merlin size | Rule |
|---|---:|---:|---|
| `/sbin/rc` | 1,956,912 | 1,919,752 | preserve ASUS core; port hooks/features at source level |
| `/usr/sbin/httpd` | 618,412 | 659,476 | preserve ASUS security fixes; port Merlin handlers/UI integration |
| `/usr/sbin/dnsmasq` | 257,376 | 507,772 | compare source/options; port required behavior |
| `/usr/sbin/openvpn` | 496,380 | 724,348 | keep later ASUS security baseline; reconcile Merlin feature patches |
| `/usr/sbin/lighttpd` | 217,124 | 209,048 | security-sensitive; source/config comparison required |
| `/usr/bin/dropbearmulti` | 219,604 | 276,808 | SSH behavior/features must be traced to source/config |
| `/usr/lib/libssl.so.1.1` | 447,036 | 447,024 | never downgrade blindly |
| `/usr/lib/libcrypto.so.1.1` | 2,261,724 | 2,263,436 | never downgrade blindly |
| `/bin/busybox` | 463,628 | 526,308 | Merlin utilities/applets need feature-level analysis |

## D — proprietary/model/hardware-sensitive: keep ASUS 52334

Several HND/Broadcom hardware modules differ. These are strong evidence that ASUS 52334 contains a later model-specific hardware stack.

Examples:

| Path | ASUS size | Merlin size |
|---|---:|---:|
| `/lib/modules/4.1.27/extra/dhd.ko` | 1,747,208 | 1,658,168 |
| `/lib/modules/4.1.27/extra/hnd.ko` | 514,816 | 445,256 |
| `/lib/modules/4.1.27/extra/bcm_enet.ko` | 1,170,744 | 1,127,384 |

The same pattern exists across multiple `bdmf`, `rdpa`, packet-runner, multicast, Wi-Fi and Broadcom modules.

**Rule:** the final firmware must retain the ASUS 52334 versions unless a later source-level analysis proves a specific replacement is required and safe. Merlin kernel modules are not automatically Category A additions merely because they are Merlin-only.

## A — candidate pure Merlin additions

These are visible only in the Merlin rootfs and are candidates for restoration, subject to dependency tracing:

- `/usr/sbin/amtm`
- `/www/Advanced_VPNDirector.asp`
- `/www/DNSDirector.asp`
- `/www/Advanced_VPNStatus.asp`
- `/www/Advanced_OpenVPNClient_Content.asp`
- `/www/Tools_Sysinfo.asp`
- `/www/Tools_OtherSettings.asp`
- `/www/Advanced_AiDisk_NFS.asp`
- `/www/Advanced_Wireless_Survey.asp`
- `/www/UploadingJFFS.asp`
- `/www/user1.asp` through `/www/user20.asp`
- `/sbin/ddns_custom_updated`
- `/www/ajax_vpn_status.asp`
- Merlin logo/UI assets and supporting JS/JSON files

These files are not sufficient by themselves. For example VPN Director and DNS Director depend on `rc`, firewall/NVRAM logic and service integration.

## B — candidate patched open-source components

Image-level evidence shows major differences in components expected to have Merlin patch sets or different build options:

- dnsmasq
- OpenVPN
- BusyBox
- Dropbear
- OpenSSL
- iptables/ipset-related components
- WireGuard support
- NFS/userland utilities

The next task is to map these image differences to the pinned Merlin `386.14_2` source tree and isolate the actual Merlin commits/patches instead of transplanting binaries.

## ASUS-only content that must not be lost

Examples found only in 52334 include:

- `/sbin/firmware_check_update`
- `/usr/sbin/jitterentropy-rngd`
- `/usr/sbin/webs_upgrade.sh`
- `/www/Main_Security_Change_Notification.asp`
- `/www/css/asus_eula.css`
- `/www/js/asus_eula.js`
- `/usr/lib/libvpn.so`
- newer ASUS AiMesh location assets
- several diagnostic/support binaries

These are not presumed removable merely because Merlin lacks them.

## Immediate source-analysis targets

The next source pass should trace, in this order:

1. JFFS custom-script and service-event hooks in `rc`.
2. VPN Director and DNS Director integration points.
3. custom config/postconf implementation.
4. Merlin WebUI handler changes in `httpd`.
5. OpenVPN/dnsmasq build and patch deltas.
6. SSH/Dropbear additions.
7. addon/AMTM/Entware integration.

Only after those deltas are mapped should the `asus-52334-merlin-port` branch start receiving functional port patches.

## Reproducibility

- Artifact verification Action: run `35982703376` — **SUCCESS**
- Filesystem extraction/diff Action: run `35982848587` — **SUCCESS**
- No ASUS or Merlin firmware binary is committed to this repository.
