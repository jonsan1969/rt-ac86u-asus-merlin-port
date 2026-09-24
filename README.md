# RT-AC86U ASUS → Merlin port

A clean-room project to rebuild Merlin functionality on top of the latest official ASUS firmware for **ASUS RT-AC86U**.

## Baseline

- **Primary hardware/security baseline:** ASUS RT-AC86U `3.0.0.4.386_52334`
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

**IN PROGRESS:** artifact acquisition, checksum verification, firmware extraction and deterministic tree diff.

See `STATUS.md`, `artifacts.lock.json` and `docs/project-goals.md`.
