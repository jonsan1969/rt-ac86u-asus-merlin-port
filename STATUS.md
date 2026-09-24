# Status

| Item | Status | Evidence |
|---|---|---|
| ASUS RT-AC86U 3.0.0.4.386_52334 baseline reference | **SUCCESS** | official ASUS support page + published SHA-256 |
| ASUS RT-AC86U 3.0.0.4.386_51955 comparison reference | **SUCCESS** | official ASUS support page + firmware-image SHA-256 verified in run 35987265109 |
| Merlin RT-AC86U 386.14_2 firmware reference | **SUCCESS** | official SourceForge file + published SHA-256 |
| Merlin 386.14_2 source revision | **SUCCESS** | exact tag/ref pinned to Git commit |
| ASUS 386_52334 GPL/source acquisition | **IN PROGRESS** | no matching public archive located; legacy `gpl@asus.com` request bounced with SMTP 550 #5.1.0; current support route deferred |
| Firmware artifact verification | **SUCCESS** | all three comparison images verified in run 35987265109 |
| Firmware filesystem extraction | **SUCCESS** | ASUS 51955, Merlin 386.14_2 and ASUS 52334 UBI/UBIFS rootfs extracted in run 35987265109 |
| Direct ASUS 52334 vs Merlin diff | **SUCCESS** | 1992 identical, 60 ASUS-only, 267 Merlin-only, 1939 different |
| ASUS 51955 vs Merlin diff | **SUCCESS** | 2017 identical, 59 ASUS-only, 267 Merlin-only, 1914 different |
| ASUS 51955 vs ASUS 52334 diff | **SUCCESS** | 3505 identical, 1 51955-only, 2 52334-only, 484 different |
| Three-way delta classification | **SUCCESS** | 1513 Merlin-delta/ASUS-unchanged, 266 pure Merlin additions, 460 divergent shared changes |
| Merlin feature compatibility probe | **SUCCESS** | run 35989225935 separates missing features from ASUS-backend overlap |
| Merlin feature-level inventory | **SUCCESS** | README + 386 changelog + runtime/source/three-way/probe evidence consolidated in master inventory |
| JFFS/custom-script port specification | **IN PROGRESS** | behavioral/helper/hook patch series defined; source-history Action 35990042520 still validating GPL intersections |
| Merlin A/B/C/D implementation classification | **IN PROGRESS** | exact source patch boundaries being reduced per required feature |
| Merlin feature port | **IN PROGRESS** | branch reserved; no unsafe core binary replacement started |

## Status vocabulary

Only these project states are used:

- **SUCCESS**
- **FAILURE**
- **IN PROGRESS**
- **CANCELLED**
