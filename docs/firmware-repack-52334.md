# ASUS RT-AC86U 386_52334 repack contract

Date: 2026-09-29

## Purpose

Define the verified container, UBI/UBIFS and final WFI-tag contract needed to repack ASUS RT-AC86U `3.0.0.4.386_52334` without replacing its kernel or protected runtime components.

This is a build/repack contract only. It is **not** a flashability claim.

## Official input

ASUS ZIP SHA-256:

`e8fd0f3a26db4fe9cf6acb64272d2b78247eb9ccf3890fbdb8daace0bac10d61`

Firmware image:

`RT-AC86U_3.0.0.4_386_52334-gd500e53_ubi.w`

Firmware image size:

`78250004`

Firmware image SHA-256:

`1b4fe984e13afdf0a69c11bda759f3222822e12f5b8c929da33f334f2cc7483f`

## Verified container geometry

Geometry probe run: `36571407058`.

Artifact digest:

`sha256:56fb39b4e0087832c7fd61f27101e178a920d8544741ddff2ec33dc41a5b5411`

- first UBI PEB offset: `3538944` / `0x360000`;
- immutable pre-UBI prefix length: `3538944` bytes;
- UBI PEB size: `131072`;
- UBI PEB count: `570`;
- raw UBI span: `74711040` bytes;
- final WFI token: `20` bytes;
- body length covered by WFI CRC: `78249984` bytes.

The 20-byte WFI token follows the complete body. It is not part of the UBI image.

## UBI/UBIFS geometry

- min I/O: `2048`;
- PEB: `131072`;
- LEB: `126976`;
- VID header offset: `2048`;
- data offset: `4096`;
- image sequence: `0`;
- volume id: `0`;
- volume name: `rootfs_ubifs`;
- volume type: dynamic;
- volume flags: autoresize;
- alignment: `1`;
- reserved PEBs: `568`;
- volume size: `72122368`.

UBIFS parameters recovered by ubi-reader:

- max LEB count: `2048`;
- compression: zlib;
- fanout: `8`;
- key hash: r5;
- log LEBs: `5`;
- journal size: `8388608`;
- orphan LEBs: `1`.

The pinned Broadcom HND build path uses:

`mkfs.ubifs --squash-uids -F -v -c 2048 -m 2048 -e 126976 -x zlib`

For the round-trip gate, modern `ubinize` is invoked explicitly with the stock-equivalent geometry:

`ubinize -p 131072 -m 2048 -s 2048 -O 2048 -Q 0`

The UBI config uses one dynamic volume, id 0, named `rootfs_ubifs`, with `vol_flags=autoresize`. The rebuilt UBIFS is exactly `72122368` bytes = 568 LEBs, and ubinize produces exactly 570 PEBs (2 layout + 568 data) with no external padding required.

## Final Broadcom WFI tag

Final-token proof run: `36572950163`.

Artifact digest:

`sha256:5974b02db63dcecac9a7fa1a7222f6ab1c4b5892d53275390ad04e29618ba6d4`

Stock body SHA-256:

`f5f3406a7ff5e828f7ac6ee3b5295f0c4151d424437eb036aa2451e81ffe0242`

Stock token bytes:

`d1 fd 62 51 32 57 00 00 08 49 00 00 03 00 00 00 02 00 00 00`

Little-endian WFI fields:

- CRC: `0x5162fdd1`;
- version: `0x00005732`;
- chip: `0x00004908` (BCM4908);
- flash type: `0x00000003` (NAND128);
- flags: `0x00000002`.

The final CRC algorithm matches Broadcom `createimg.pl`:

- width 32;
- polynomial `0x04c11db7`;
- initial value `0xffffffff`;
- xorout `0`;
- refin/refout enabled.

For a reflected implementation this is polynomial `0xEDB88320`.

Recomputing the CRC over the complete 78,249,984-byte stock body and packing the five 32-bit little-endian WFI fields reproduces the official 20-byte token and the official firmware image **byte for byte**.

## Packaging lineage

The pinned 51997 RT-AC86U HND build path uses Broadcom `bcmImageMaker`, `addvtoken` and then `createimg.pl --wholeflashfile`. The final `createimg.pl` pass recalculates WFI CRC after its NVRAM operation.

For project repacking, the final image contract is therefore validated directly at the WFI level; an already-final ASUS image is not expected to be idempotent through the earlier `addvtoken` intermediate step.

## Stock semantic round-trip — SUCCESS

Workflow run: `36593572826`  
Commit: `4b6ce8f675d7cdfa54b7ba71257bc645369a1a63`  
Artifact: `firmware-stock-repack-roundtrip-52334`  
Artifact digest: `sha256:8fddaed20326f10435d383a59006d33075c90ee3938939e642d1e5638b6107fe`

The gate performs the full stock-only path:

1. preserves the first `0x360000` bytes byte-for-byte;
2. extracts stock `rootfs_ubifs` as root;
3. inventories file type, content/symlink/device payload, mode, UID/GID, xattrs and hardlink relationships;
4. rebuilds UBIFS with the pinned Broadcom HND `--squash-uids -F -c 2048 -m 2048 -e 126976 -x zlib` contract;
5. rebuilds the single autoresize `rootfs_ubifs` volume with image sequence 0;
6. requires exactly 570 PEBs;
7. joins the immutable stock prefix and rebuilt UBI;
8. recalculates the final Broadcom WFI token;
9. re-extracts the rebuilt UBI and compares semantic inventories.

Observed result:

- original semantic entries: `3992`;
- rebuilt semantic entries: `3992`;
- non-root UID/GID entries in stock: `0`;
- semantic mismatches: `0`;
- rebuilt UBIFS: `72122368` bytes / 568 LEBs;
- rebuilt UBI: `74711040` bytes / 570 PEBs;
- external UBI padding: `0`;
- rebuilt WFI CRC: `0x10fff90e`;
- rebuilt full-image SHA-256: `5926ceb58c039bf44a76657ba571b7dcc82d34206ff474ad076e8b3f0beb4cac`.

The rebuilt image is not expected to be byte-identical to ASUS stock because UBIFS generation includes new filesystem metadata (for example a new UUID), but the extracted rootfs is semantically identical under the inventory contract and the final WFI container is structurally valid.

This establishes the **stock repack baseline**, not flashability.

## Active guarded-overlay repack — SUCCESS / UNVALIDATED CANDIDATE

The active-overlay software gate is complete.

Current reference run:

`36924014278`

Published firmware:

`RT-AC86U_386_52334_merlin-port-UNVALIDATED.w`

Exact firmware identity:

- SHA-256: `eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3`;
- size: `78,250,004` bytes.

The run proves:

- guarded manifest/overlay authorization;
- verified ASUS 386_52334 base;
- exact 570-PEB UBI;
- valid WFI/trailer/CRC;
- metadata-faithful re-extraction;
- zero unauthorized semantic drift;
- protected ASUS core files remain byte-identical;
- zero K2/K3 optional kernel-module leakage.

This closes the software repack gate. It does **not** establish flashability.

The original GitHub artifact is `11193520953`. Run `36969448115` additionally preserves the verified official ASUS 52334 stock image, the exact candidate, K2/K3 hardware-validation inputs and the current collectors/runbooks in 90-day artifact `11211056837` through 2026-12-31. The artifact ZIP digests are not firmware identities; all hardware evidence remains bound to the `.w` SHA-256 above.

## Remaining gate

The next gate is no longer another repack experiment.

Promotion now requires the physical/runtime prerequisites in `docs/candidate-promotion-gate.md`, including:

- actual ASUS 386_52334 K4a read-only evidence;
- general runtime preflight from the intended 52334 validation runtime;
- controlled K4 family validation for any optional kernel modules to be activated;
- feature-specific runtime proof such as M49 user-slot EJ expansion;
- physically completed backup/rollback preparation.

Until those gates pass, the candidate remains **UNVALIDATED** and must not be called flashable.
