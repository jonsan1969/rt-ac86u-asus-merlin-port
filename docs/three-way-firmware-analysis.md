# Three-way firmware delta analysis

Date: 2026-09-24  
Action run: `35987265109` — **SUCCESS**

## Purpose

Directly comparing ASUS `386_52334` with Merlin `386.14_2` mixes two effects:

1. genuine Merlin functionality and package changes;
2. later ASUS changes made after Merlin's final RT-AC86U release.

To separate them, this project now uses ASUS RT-AC86U `3.0.0.4.386_51955` as a temporal comparison reference.

ASUS released `51955` on 2024-11-08. Merlin `386.14_2` was released on 2024-11-17.

The final firmware baseline remains **ASUS 52334**.  
ASUS 51955 is only a delta-analysis reference.

## Verified 51955 artifact

- ZIP: `FW_RT_AC86U_300438651955.zip`
- observed ZIP SHA-256: `d364820f2b3182be90bfdad987e0d6a9ce7facc3bcdf676d74e6cc9da7234273`
- ZIP size: 69,878,988 bytes
- firmware image: `RT-AC86U_3.0.0.4_386_51955-g1f1ef30_ubi.w`
- firmware image size: 78,118,932 bytes
- ASUS-published/verified image SHA-256: `af63aeb4ef335e2ebac521358103de451333b021ec82e59736854ae95a3424e0`

Important checksum detail: ASUS explicitly instructs users to unzip this release before verifying the checksum. The published SHA-256 therefore applies to the `.w` image, not the ZIP archive.

## Pairwise results

### ASUS 51955 vs Merlin 386.14_2

| Class | Count |
|---|---:|
| IDENTICAL | 2,017 |
| ASUS_ONLY | 59 |
| MERLIN_ONLY | 267 |
| DIFFERENT | 1,914 |

### ASUS 51955 vs ASUS 52334

| Class | Count |
|---|---:|
| IDENTICAL | 3,505 |
| 51955_ONLY | 1 |
| 52334_ONLY | 2 |
| DIFFERENT | 484 |

This confirms that 51955 is a useful near-Merlin ASUS reference: most of the ASUS runtime tree remained identical through 52334.

## Three-way classification

The three trees were classified as:

| Class | Count | Meaning |
|---|---:|---|
| `ALL_IDENTICAL` | 1,992 | unchanged in all three images |
| `MERLIN_ONLY_PURE_ADDITION` | 266 | absent from both ASUS images, present in Merlin |
| `MERLIN_DELTA_ASUS_UNCHANGED` | 1,513 | ASUS 51955 == ASUS 52334, Merlin differs |
| `BOTH_CHANGED_DIVERGENT` | 460 | Merlin and later ASUS both differ from 51955 and from each other |
| `ASUS_LATER_CHANGE_ONLY` | 25 | Merlin stayed with 51955 while ASUS later changed |
| `ASUS_52334_ONLY_ADDITION` | 1 | new only in later ASUS |
| `BOTH_ADDED_DIFFERENTLY` | 1 | absent in 51955, later added differently by Merlin and ASUS |

## Why this materially improves the port

The original direct ASUS-52334-vs-Merlin comparison had **1,939 same-path/different-content entries** that all looked like conflicts.

The three-way analysis reduces the truly ambiguous shared-change set to **460 paths**, a reduction of about **76.3%**.

It also separates:

- **266 pure Merlin additions**, including clear features such as:
  - `/www/Advanced_VPNDirector.asp`
  - `/www/DNSDirector.asp`
  - `/usr/sbin/amtm`
  - `/www/Tools_Sysinfo.asp`
  - `/www/Tools_OtherSettings.asp`
  - `/sbin/ddns_custom_updated`
- **1,513 strong Merlin-delta candidates** where ASUS 51955 and 52334 are byte-identical but Merlin differs.
- **25 later-ASUS-only changes** that should normally be retained.
- **460 high-conflict paths** requiring source-level reconciliation.

## Core binary examples

The major shared programs remain in the divergent/high-risk set:

- `/sbin/rc`
- `/usr/sbin/httpd`
- `/usr/sbin/dnsmasq`
- `/usr/sbin/openvpn`
- `/usr/sbin/lighttpd`
- `/usr/bin/dropbearmulti`
- `/bin/busybox`

This is exactly where source-level porting remains mandatory.

By contrast, `/usr/lib/libssl.so.1.1` is a useful example of a `MERLIN_DELTA_ASUS_UNCHANGED` path: both ASUS 51955 and 52334 use the same file while Merlin differs. That identifies provenance, but **does not automatically authorize porting Merlin's version**. Security-sensitive components still follow the ASUS-first rule.

## Revised analysis model

The project now uses this model:

```text
ASUS 386_51955 ──────┬──────> Merlin 386.14_2
                     │          isolate candidate Merlin delta
                     │
                     └──────> ASUS 386_52334
                                identify later ASUS changes
```

Then the actual implementation remains:

```text
ASUS 386_52334
+ selected, source-reviewed Merlin functionality
= project firmware
```

## Next step

Use the two reduced candidate sets to build the complete Merlin feature inventory:

1. inspect all `MERLIN_ONLY_PURE_ADDITION` paths;
2. group `MERLIN_DELTA_ASUS_UNCHANGED` paths by component/feature;
3. manually review the 460 `BOTH_CHANGED_DIVERGENT` paths against Merlin source history and later ASUS behavior;
4. classify each actual feature as A/B/C/D and assign a port strategy.

The filesystem classifications are evidence of provenance/delta, not an instruction to copy binaries.
