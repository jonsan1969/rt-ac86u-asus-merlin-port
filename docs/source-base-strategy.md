# Source-base strategy

Date: 2026-09-24

## Decision

The project remains **ASUS 52334 image-first**.

We do **not** redefine the final source base as Asuswrt-Merlin merely because later ASUS GPL archives were imported into the Merlin repository.

## Verified facts

### Final runtime baseline

Official ASUS RT-AC86U firmware:

- version: `3.0.0.4.386_52334`
- verified archive SHA-256: `e8fd0f3a26db4fe9cf6acb64272d2b78247eb9ccf3890fbdb8daace0bac10d61`
- verified image SHA-256: `1b4fe984e13afdf0a69c11bda759f3222822e12f5b8c929da33f334f2cc7483f`

This image remains authoritative for hardware, proprietary/model-specific components and later ASUS security/runtime changes.

### Near-Merlin comparison reference

ASUS `386_51955` is retained only as a temporal/runtime comparison reference.

It is useful because 3,505 runtime paths are byte-identical between ASUS 51955 and ASUS 52334, allowing later-ASUS changes to be separated from Merlin changes.

It is **not** currently available to this project as a verified clean GPL/source archive.

### Clean public ASUS GPL reference

A public Git mirror exists for older RT-AC86U ASUS GPL source. Its history identifies the latest clean imported ASUS generation there as:

- `386.45956`
- commit `a9179fc9329565dea0f7c5c7648fe8ad49ceaaf6`

This is a **community mirror of ASUS GPL material**, not an ASUS-hosted canonical archive. It may be used for structural/source archaeology only and must not be described as our modern build base.

A later ASUS RT-AC86U GPL generation `386_46092` is historically corroborated by downstream firmware projects, but this project has not independently verified an original ASUS archive or a clean unmodified mirror for that release.

## Late ASUS GPL history inside Merlin

The Merlin donor history contains:

- `e9e6035c85c673701646f2cf15de09b01a997ab9` — “Merge with GPL 386_52796”
- `75c9d789179e169de5b2da2c02031358d5d03566` — “Merge with GPL 386_52805”
- `47bbd79560ec3f03f12537cce8fea81766e9f47d` — RT-AC86U SDK/binary refresh from `386_52796`

These commits are valuable provenance, but they are not clean ASUS snapshots.

### Direct proof

The JFFS/custom-script helper file:

`release/src/router/shared/scripts.c`

contains Merlin's `run_custom_script()`, `run_postconf()`, `use_custom_config()` and `append_custom_config()` both:

- immediately before the `386_52796` merge, and
- at the `386_52796` merge commit itself.

Therefore the merge commit demonstrably preserves pre-existing Merlin code and cannot be called “clean ASUS 52796 source”.

The same rule applies to descendants such as the `386_52805` merge.

## Practical build architecture

Until a clean late ASUS AC86U source archive is obtained, development is split into four layers.

### Layer 1 — ASUS 52334 firmware image

Always the final runtime/container baseline.

Keep unchanged by default:

- kernel
- HND/Broadcom SDK runtime
- Wi-Fi drivers/firmware
- Trend Micro/ASUS proprietary binaries
- model-specific prebuilts
- later ASUS-only services and security/runtime changes

### Layer 2 — additive/static Merlin functionality

Port first when ASUS already provides the required backend or when no core binary replacement is required.

Examples:

- DNS Director WebUI on top of ASUS DNSFilter backend
- custom WebUI assets/pages where handlers already exist
- addon helper scripts
- AMTM/userland additions after JFFS prerequisites exist

These are the safest first functional ports.

### Layer 3 — rebuildable open-source additions

Examples:

- ipset
- Cake
- NFS/CIFS modules/userspace
- WireGuard components
- selected CLI utilities

These must be built against a source/kernel environment demonstrably compatible with the ASUS 52334 runtime. Old Merlin kernel modules are not copied blindly.

### Layer 4 — shared core programs

Examples:

- `rc`
- `httpd`
- `dnsmasq`
- OpenVPN integration
- Dropbear integration

These remain blocked from binary replacement until their source-side ASUS baseline is sufficiently reconstructed or obtained.

A Merlin binary is never used merely because it contains the desired feature.

## Porting rule for core features

For every core-dependent Merlin feature:

1. identify the exact behavioral/source delta in Merlin;
2. determine whether ASUS 52334 already implements all or part of it;
3. preserve the ASUS 52334 runtime implementation;
4. patch/rebuild only when later ASUS behavior can be retained with confidence;
5. otherwise defer that feature instead of downgrading the core binary.

## Immediate consequence

The first actual port candidate should be a feature in which:

- ASUS 52334 already has the backend;
- Merlin contributes mostly UI/static integration;
- no newer ASUS core binary needs replacement.

DNS Director currently fits this profile and is being compatibility-tested first.

## What would change this strategy

If ASUS later provides the complete corresponding source for `386_52334`, that source immediately becomes the preferred build source.

If a clean official later AC86U GPL archive is independently verified before then, it may become the build-source baseline after provenance and buildability checks.

Until that happens, every build/source claim must explicitly distinguish:

- ASUS 52334 runtime baseline,
- actual source generation used for a rebuilt component,
- Merlin source delta applied,
- any retained 52334 prebuilt/proprietary component.

