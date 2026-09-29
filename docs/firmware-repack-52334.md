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

Equivalent tool parameters:

`mkfs.ubifs -m 2048 -e 126976 -c 2048 -x zlib -f 8 -k r5 -l 5 -j 8388608 -p 1`

`ubinize -p 131072 -m 2048 -s 2048 -O 2048 -Q 0`

The UBI config uses one dynamic volume, id 0, named `rootfs_ubifs`, `vol_size=72122368`, `vol_alignment=1`, `vol_flags=autoresize`.

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

## Next gate

Perform a stock semantic round-trip:

1. retain the 0x360000-byte prefix unchanged;
2. extract stock `rootfs_ubifs`;
3. build UBIFS with the recovered geometry;
4. ubinize the same single volume;
5. require exactly 570 PEBs;
6. join original prefix + rebuilt UBI;
7. generate a valid final WFI tag using the verified algorithm;
8. re-extract the rebuilt image;
9. compare file content, type, symlink target, mode, UID/GID, device metadata and hardlink relationships;
10. do not call the result flashable and do not activate optional K2/K3 modules.

Only after stock semantic round-trip succeeds may the active guarded overlay be passed through the same repack pipeline.
