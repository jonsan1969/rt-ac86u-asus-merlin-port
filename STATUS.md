# Status

| Item | Status | Evidence |
|---|---|---|
| ASUS RT-AC86U 3.0.0.4.386_52334 baseline reference | **SUCCESS** | official ASUS support page + published SHA-256 |
| ASUS RT-AC86U 3.0.0.4.386_51955 comparison reference | **SUCCESS** | official ASUS support page + firmware-image SHA-256 verified in run 35987265109 |
| Merlin RT-AC86U 386.14_2 firmware reference | **SUCCESS** | official SourceForge file + published SHA-256 |
| Merlin 386.14_2 source revision | **SUCCESS** | exact tag/ref pinned to Git commit |
| ASUS 386_52334 GPL/source acquisition | **IN PROGRESS** | no matching public archive located; legacy `gpl@asus.com` request bounced with SMTP 550 #5.1.0; current support route deferred |
| Firmware artifact verification | **SUCCESS** | all three comparison images verified in run 35987265109 |
| Firmware filesystem extraction | **SUCCESS** | ASUS 51955, Merlin 386.14_2 and ASUS 52334 UBI/UBIFS rootfs extracted |
| Direct ASUS 52334 vs Merlin diff | **SUCCESS** | 1992 identical, 60 ASUS-only, 267 Merlin-only, 1939 different |
| ASUS 51955 vs Merlin diff | **SUCCESS** | 2017 identical, 59 ASUS-only, 267 Merlin-only, 1914 different |
| ASUS 51955 vs ASUS 52334 diff | **SUCCESS** | 3505 identical, 1 51955-only, 2 52334-only, 484 different |
| Three-way delta classification | **SUCCESS** | 1513 Merlin-delta/ASUS-unchanged, 266 pure Merlin additions, 460 divergent shared changes |
| Merlin feature compatibility probe | **SUCCESS** | run 35989225935 separates missing features from ASUS-backend overlap |
| Merlin feature-level inventory | **SUCCESS** | README + 386 changelog + runtime/source/three-way/probe evidence consolidated in master inventory |
| JFFS/custom-script source delta map | **SUCCESS** | Action 35990042520 completed successfully |
| JFFS/custom-script port specification | **SUCCESS** | behavioral/helper/hook patch series documented in docs/jffs-custom-script-port-plan.md |
| ASUS 52334 DNSFilter runtime map | **SUCCESS** | Action 35993309478 verified retained stock backend/UI-support pieces |
| DNS Director phase-1 overlay implementation | **IN PROGRESS** | guarded overlay exists on port branch; latest validation stopped fail-closed at exact state.js text match |
| DNS Director overlay validation run 36000073528 | **FAILURE** | Apply guarded overlay: entry 2 expected one exact match, found zero |
| Merlin A/B/C/D implementation classification | **IN PROGRESS** | exact source patch boundaries continue per feature |
| Merlin feature port | **IN PROGRESS** | first guarded DNS Director overlay staged; no unsafe core binary replacement |
| Flashable firmware | **IN PROGRESS** | no flashability claim until repack + hardware/runtime gates pass |

## Status vocabulary

Only these project states are used:

- **SUCCESS**
- **FAILURE**
- **IN PROGRESS**
- **CANCELLED**
