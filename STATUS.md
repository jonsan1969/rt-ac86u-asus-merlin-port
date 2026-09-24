# Status

| Item | Status | Evidence |
|---|---|---|
| ASUS RT-AC86U 3.0.0.4.386_52334 baseline reference | **SUCCESS** | official ASUS support page + published SHA-256 |
| Merlin RT-AC86U 386.14_2 firmware reference | **SUCCESS** | official SourceForge file + published SHA-256 |
| Merlin 386.14_2 source revision | **SUCCESS** | exact tag/ref pinned to Git commit |
| ASUS 386_52334 GPL/source acquisition | **IN PROGRESS** | no matching public archive located; legacy `gpl@asus.com` request bounced with SMTP 550 #5.1.0; current support route deferred |
| Firmware archives materialized and locally verified | **SUCCESS** | GitHub Actions run 35982703376; both locked SHA-256 values matched |
| Firmware filesystem extraction | **SUCCESS** | GitHub Actions run 35982848587; both UBI/UBIFS root filesystems extracted |
| ASUS vs Merlin tree/hash diff | **SUCCESS** | 1992 identical, 60 ASUS-only, 267 Merlin-only, 1939 different |
| Merlin A/B/C/D delta classification | **IN PROGRESS** | initial high-risk/core/hardware/addition classification documented |
| Merlin feature port | **IN PROGRESS** | branch reserved; no unsafe binary replacement work started |

## Status vocabulary

Only these project states are used:

- **SUCCESS**
- **FAILURE**
- **IN PROGRESS**
- **CANCELLED**
