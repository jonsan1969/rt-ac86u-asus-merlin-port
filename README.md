# RT-AC86U ASUS → Merlin port

A clean-room project to restore Merlin functionality on top of the latest official ASUS firmware for **ASUS RT-AC86U**.

## Baseline

- **Primary hardware/security/runtime baseline:** ASUS RT-AC86U `3.0.0.4.386_52334`
- **Near-Merlin comparison reference:** ASUS RT-AC86U `3.0.0.4.386_51955`
- **Merlin donor/reference:** Asuswrt-Merlin `386.14_2`
- **Merlin source pin:** `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

The project is intentionally **ASUS-first**:

> Keep the later ASUS implementation and port the required Merlin delta on top.

Do not replace newer ASUS core components with older Merlin binaries merely to regain a feature.

## Branches

- `main` — documented stable baseline
- `asus-52334-analysis` — firmware/source comparison and classification
- `asus-52334-merlin-port` — actual Merlin feature port

## Current phase

**IN PROGRESS:** feature-level porting.

Completed analysis milestones include verified firmware artifacts, UBI/UBIFS extraction, three-way ASUS-51955/Merlin/ASUS-52334 classification, complete Merlin feature inventory, compatibility probes and the JFFS/custom-script source-delta specification.

The active image-safe overlay now contains the proven source-independent Merlin deltas and passes an exact-size 570-PEB ASUS 52334 repack gate without replacing protected ASUS core binaries. Capacity-heavy features are optionalized rather than forcing partition growth. Shared-core features remain source-contract work until matching ASUS 52334 source is available; kernel/runtime features remain behind explicit physical-router gates.

For continuation in a fresh ChatGPT thread, start with:

- `docs/thread-handoff.md`
- `STATUS.md`
- `docs/merlin-feature-inventory.md`
- `docs/source-base-strategy.md`

No firmware is considered flashable yet. CI may publish artifacts explicitly named `UNVALIDATED`; these are quarantined development candidates only and must not be flashed until the documented ASUS-52334 hardware/runtime gates pass.
