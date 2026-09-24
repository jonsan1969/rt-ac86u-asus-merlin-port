# ASUS GPL provenance inside the Merlin 386.14_2 donor tree

This project must distinguish **ASUS-origin code integrated into Merlin** from a **clean official ASUS source tree**.

## Relevant Merlin history

The pinned Merlin `386.14_2` history contains this sequence:

| Commit | Date | Meaning |
|---|---|---|
| `e9e6035c85c673701646f2cf15de09b01a997ab9` | 2024-06-27 | `Merge with GPL 386_52796` |
| `75c9d789179e169de5b2da2c02031358d5d03566` | 2024-06-27 | `Merge with GPL 386_52805` |
| `47bbd79560ec3f03f12537cce8fea81766e9f47d` | 2024-06-27 | `Merge binary RT-AC86U SDK + binary blobs from 386_52796` |
| `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b` | 2024-11-17 | final `386.14_2` donor pin |

The `52796` GPL integration changes hundreds of tracked files. The later `52805` integration is an incremental update on top of that integration history. The RT-AC86U-specific SDK/prebuilt refresh is explicitly labeled `386_52796`, not `52805`.

## What this does mean

We can use the history to determine:

- which changes entered from later ASUS GPL snapshots,
- which RT-AC86U prebuilt/SDK generation Merlin used,
- where Merlin had to re-apply or adapt its own changes after an ASUS merge,
- candidate ASUS-vs-Merlin patch boundaries for source archaeology.

This is valuable donor provenance.

## What this does **not** mean

None of these Merlin commits is treated as a clean, independently verified ASUS GPL source archive.

They are commits in an already modified Asuswrt-Merlin repository. Therefore this project must not describe a checkout of `75c9d789...`, `47bbd795...`, or any descendant as:

- “stock ASUS source”,
- “clean ASUS 52805 source”, or
- “ASUS 52334 source”.

## Important version nuance

Merlin 386.14 combined:

- generic/common ASUS GPL changes reaching `386_52805`,
- RT-AC86U model-specific SDK/binary material explicitly refreshed from `386_52796`,
- Merlin's own pre-existing and subsequently re-applied changes.

The final stock ASUS RT-AC86U image used by this project is instead `3.0.0.4.386_52334`, released in 2026 and independently verified at image level.

ASUS build numbers alone must therefore not be used as a chronological ordering between these different provenance streams.

## External context

RMerlin has stated that ASUS GPL archives supplied to him can be snapshots generated specifically for Merlin and do not imply a matching public stock release.

Reference discussion:
https://www.snbforums.com/threads/asus-rt-ac68u-firmware-version-3-0-0-4-386_51685-2024-04-15.89692/page-4

He also stated that he works with whatever snapshot ASUS considers suitable when he requests an updated GPL rather than targeting a specific stock release.

Reference discussion:
https://www.snbforums.com/threads/asuswrt-merlin-386-14-is-now-available-for-ac-models.91060/page-2

## Build-strategy consequence

Until a clean later official ASUS AC86U source archive is verified, the source problem remains explicit:

1. ASUS `52334` firmware image is authoritative for runtime hardware/security components.
2. Merlin `386.14_2` is authoritative only as the Merlin feature donor.
3. Merlin's ASUS-GPL merge history is useful for source archaeology, not a license to redefine the technical baseline as Merlin.
4. Any eventual build-source base must be labeled by its actual provenance and version.
