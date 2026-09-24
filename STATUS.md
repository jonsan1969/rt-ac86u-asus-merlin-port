# Status

| Item | Status | Evidence |
|---|---|---|
| ASUS RT-AC86U 3.0.0.4.386_52334 baseline reference | **SUCCESS** | official ASUS support page + published SHA-256 |
| Merlin RT-AC86U 386.14_2 firmware reference | **SUCCESS** | official SourceForge file + published SHA-256 |
| Merlin 386.14_2 source revision | **SUCCESS** | exact tag/ref pinned to Git commit |
| Public official ASUS 386_52334 GPL tarball | **FAILURE** | not found in bounded initial search; do not repeat without new evidence |
| Firmware archives materialized and locally verified | **IN PROGRESS** | fetch/verify tooling committed |
| Firmware filesystem extraction | **IN PROGRESS** | reproducible extraction scaffold committed |
| ASUS vs Merlin tree/hash diff | **IN PROGRESS** | deterministic comparison tooling committed |
| Merlin A/B/C/D delta classification | **IN PROGRESS** | begins after first complete filesystem diff |
| Merlin feature port | **IN PROGRESS** | branch reserved; no unsafe binary replacement work started |

## Status vocabulary

Only these project states are used:

- **SUCCESS**
- **FAILURE**
- **IN PROGRESS**
- **CANCELLED**
