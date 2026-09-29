# Late 386.51997 source-lineage triangulation

Date: 2026-09-28

## Purpose

Reduce the gap between the clean ASUS 386.45956 archaeology anchor and the final ASUS RT-AC86U runtime baseline 386_52334.

No public clean ASUS 386_52334 source archive has been located.

The project therefore uses three different reference classes and keeps them deliberately separate:

1. **clean ASUS source anchor** — 386.45956;
2. **late 386.51997 modified-source references** — Merlin 386.12_x and SWRT;
3. **final runtime authority** — official ASUS RT-AC86U 386_52334 firmware.

Only class 1 is treated as clean ASUS source.  
Class 2 is useful for later source shape and build-environment archaeology but is **not** treated as unmodified ASUS code.

## Merlin 386.12_x reference

Pinned branch head:

- repository: `RMerl/asuswrt-merlin.ng`;
- ref SHA: `5b47ec64ce58d23c591e809d4cbad09d1121c4ea`;
- branch: `386.12_x`.

Its `Changelog-386.txt` states for 386.12:

`UPDATED: Merged with GPL 386_51997.`

This is the closest known openly inspectable AC86U-capable source/build tree derived from a late ASUS 386 GPL merge, but it already contains Merlin modifications.

It must therefore be used only to answer questions such as:

- how did the later 386 ASUS source layout evolve relative to 45956?
- which files/components still exist and build for RT-AC86U?
- what merge conflicts are likely when applying a small source delta?
- which later upstream ASUS changes were present before Merlin re-applied its own behavior?

It must **not** be treated as the ASUS side of a direct feature diff.

## Independent SWRT lineage reference

SWRT's public supported-device changelog states:

`Brcm ac models merged with 386_51997.`

Current inspected source ref:

- repository: `SWRT-dev/asuswrt-bcm`;
- ref SHA: `2f655d718a110f9b1a45fb1166d701ff2bce850c`.

This tree is also modified firmware source and is not clean ASUS.

Its value is independent triangulation: when Merlin 386.12_x and SWRT show a similar late-386 structural change relative to clean ASUS 45956, that increases confidence that the later ASUS source shape had evolved in that direction. It still does not prove authorship or exact 51997 content.

## Important helper result

`release/src/router/shared/scripts.c` is exactly the same length/content across the inspected:

- clean ASUS 386.45956;
- Merlin 386.12_x;
- Merlin 386.14_2;
- current SWRT reference.

This reinforces the earlier conclusion that the four custom-script helper primitives themselves are inherited from the ASUS lineage and are not the risky part of the port.

The risky/source-required work is:

- exposing the helper outside the ASUS TOR build gate;
- adding the enable/default contract;
- wiring lifecycle call sites;
- preserving later ASUS control flow around those call sites.

## Why late modified trees still help

The clean 45956 tree and late modified trees differ substantially in large files such as:

- `shared/shared.h`;
- `shared/defaults.c`;
- `rc/services.c`;
- `rc/firewall.c`;
- `rc/udhcpc.c`;
- `rc/wan.c`;
- `rc/init.c`.

That means a patch prepared mechanically against 45956 is not safe to apply blindly to a later 386 tree.

For each source-required feature, the preferred merge method is now:

1. identify the exact behavior delta using pinned Merlin donor code;
2. identify the clean-ASUS lineage behavior using 45956 where possible;
3. inspect the same function/file shape in Merlin 386.12_x;
4. optionally inspect SWRT as an independent late-386 structural reference;
5. keep ASUS 52334 runtime strings/files/behavior as the final target authority;
6. write the patch against the latest genuinely ASUS-compatible source tree we can obtain, never by replacing a whole donor file.

## Example: JFFS helper exposure

The helper implementation remains stable across all references.

Clean ASUS 45956:

- has the helper implementation;
- TOR-gates build/declarations;
- lacks the normal Merlin lifecycle call sites.

Merlin 386.12_x:

- compiles/exposes the helper independently;
- retains the lifecycle hook framework;
- is based on the later 51997 GPL merge.

Therefore the source integration contract for M01-M04 is now stronger:

- do not import `scripts.c`;
- preserve the inherited helper implementation;
- reproduce only helper exposure, enable/default handling, JFFS directory bootstrap, and reviewed call sites in later ASUS control flow.

## Example: why SWRT is only secondary evidence

SWRT currently contains many custom-script lifecycle hooks, but its `rc/qos.c` does not carry the same `qos-start` hook surface as pinned Merlin.

That proves it is not simply a byte-for-byte copy of Merlin's source tree.

It does **not** prove that any individual SWRT hook came from ASUS.

Use SWRT to understand late source shape and divergence, not as a clean donor.

## Source strategy decision

From this point forward:

- **45956** = clean ASUS source truth for ancestry;
- **51997 Merlin/SWRT trees** = late modified structural references;
- **52334 official image** = runtime truth;
- **Merlin 386.14_2** = feature behavior donor.

A future clean 51997/52334 ASUS source archive would immediately supersede the modified-source references for direct diff work.

## Current classification

**LATE SOURCE TRIANGULATION: AVAILABLE**

**CLEAN LATE ASUS SOURCE: STILL MISSING**

This does not unlock wholesale source replacement, but it materially improves placement/review of narrow source patches and prevents us from overfitting patches to the much older 45956 source layout.


## Superseding precision note

The modified-source triangulation remains useful, but the Git history has now been pinned to the exact import stages. Use `docs/source-anchor-51997-import-boundary.md` for commit-level provenance:

- `28daa823...` = general GPL 386_51997 source-shape import;
- `c553d8e4...` = RT-AC86U 386_51997 SDK/blob import.

These exact anchors supersede the branch head when the question is source placement or RT-AC86U build provenance.
