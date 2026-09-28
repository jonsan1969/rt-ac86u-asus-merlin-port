# Samba Merlin controls source integration contract

Date: 2026-09-28  
Feature inventory IDs: M18, M19  
Related completed feature: M20 WINS server  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Clean source-lineage anchor: ASUS 386.45956 mirror @ `a9179fc9329565dea0f7c5c7648fe8ad49ceaaf6`  
Merlin donor: 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Purpose

Define the smallest source-side delta required for:

- M18 — simpler SMB share naming;
- M19 — force Samba Master Browser;

without replacing ASUS 52334 Samba binaries, `rc`, `libshared`, or the later ASUS Samba configuration generator.

M20 WINS is already implemented image-safely because ASUS 52334 runtime retains the `smbd_wins` backend. M18/M19 are different: their backend keys are absent from the verified 52334 runtime and therefore need source integration.

## Source-lineage warning

The clean ASUS 386.45956 source anchor is structurally useful but is **not** a drop-in Samba source base.

At that anchor:

- `release/src/router/libdisk/write_smb_conf.c` contains none of:
  - `smbd_simpler_naming`;
  - `smbd_master`;
  - `smbd_wins`.
- ASUS `shared/defaults.c` contains an old commented `smbd_master` entry and an active `smbd_wins` default.
- verified ASUS 52334 runtime, by contrast, contains active `smbd_wins` behavior in `rc` + `libshared`.

Therefore the later ASUS Samba path clearly evolved after 45956. The final implementation must locate the **52334-compatible/later ASUS generator** and insert only the reviewed M18/M19 semantics there.

Do not copy the 45956 or Merlin Samba generator wholesale.

## M18 — simpler share naming

### Donor behavior

Merlin adds NVRAM key:

`smbd_simpler_naming=0`

When generating per-folder Samba shares, the donor counts duplicate folder names.

If:

- `smbd_simpler_naming=1`; and
- the folder name is unique across the generated share list;

the share is emitted as:

```text
[folder]
```

Otherwise the existing disambiguated form is retained:

```text
[folder (at disk-or-mount-name)]
```

The pinned donor applies this decision at each relevant share-generation branch in `libdisk/write_smb_conf.c`. It does not globally rename arbitrary Samba sections.

### Required source integration

On the later ASUS generator:

1. add default `smbd_simpler_naming=0`;
2. identify every branch that emits the existing `[folder (at ...)]` section name;
3. reuse the donor's uniqueness check semantics;
4. emit simple `[folder]` only when the name is unique;
5. keep ASUS paths, permissions, comments, ACL behavior, protocol settings and share enumeration unchanged.

### Collision rule

The uniqueness condition is mandatory. Enabling simpler naming must never create duplicate Samba section names.

## M19 — force Master Browser

### Donor behavior

Merlin adds active default:

`smbd_master=0`

When enabled, the generated Samba global configuration receives:

```text
os level = 255
domain master = yes
local master = yes
preferred master = yes
```

The donor also changes Samba lifecycle behavior so Samba can remain/start for Master Browser or WINS duties even when there is no normal USB share to serve.

Relevant donor conditions include:

- do not early-return merely because no storage partition is mounted when `smbd_master=1` or `smbd_wins=1`;
- start Samba in the no-disk path when either `smbd_master` or `smbd_wins` is enabled.

### Required source integration

On the later ASUS Samba/runtime path:

1. add default `smbd_master=0`;
2. append the four Master Browser directives only when enabled;
3. review all no-disk/early-return logic in the current ASUS Samba lifecycle;
4. extend only the conditions necessary for Master Browser service;
5. preserve the already working ASUS 52334 `smbd_wins` behavior and the M20 UI contract.

Do not assume the 45956 `rc/usb.c` control flow matches 52334.

## M20 interaction

M20 is already image-safe and green:

- ASUS 52334 `rc` + `libshared` retain `smbd_wins`;
- generic form/NVRAM apply was proven;
- the UI-only WINS row is active;
- guarded overlay validation preserves protected core binaries.

The future M18/M19 source build must pass a regression gate proving that M20 still works exactly as before.

In particular:

- do not reset `smbd_wins` default semantics merely to match the donor;
- do not replace current ASUS WINS config generation with the older donor generator;
- do not require M18 or M19 for WINS to remain functional.

## WebUI contract

After backend support is present, add two controls to the stock Samba page:

### Simpler share naming

- key: `smbd_simpler_naming`;
- values: `1` / `0`;
- default: `0`.

### Force as Master Browser

- key: `smbd_master`;
- values: `1` / `0`;
- default: `0`.

Use the same proven generic ASUS form/NVRAM apply path already used for M20. Do not expose either row before backend consumption is built and verified.

## Validation gate

### M18

1. default/off preserves stock ASUS share names byte-for-byte where feasible;
2. on uses simple names only for unique folder names;
3. duplicate folder names remain disambiguated;
4. paths, permissions and access controls are unchanged;
5. multi-disk and multi-partition cases do not create duplicate Samba sections.

### M19

1. default/off preserves stock ASUS master-browser behavior;
2. on emits exactly the intended four Samba directives;
3. Samba can provide Master Browser service without a mounted share if current architecture permits that donor semantic;
4. disabling the option removes the forced-master directives;
5. WINS remains functional both with and without Master Browser enabled.

### Combined regression

- M20 `smbd_wins` continues to work;
- current ASUS SMB protocol/security defaults remain authoritative;
- no Merlin Samba binary or older `rc` binary is transplanted;
- guarded core hashes remain unchanged for image-only pieces, and rebuilt source components are provenance-labelled when source integration begins.

## Current classification

**M18 SOURCE-REQUIRED**  
**M19 SOURCE-REQUIRED**  
**M20 SUCCESS / MUST REGRESSION-PASS**

The pinned donor delta is small and well-defined, but implementation waits for a sufficiently late ASUS-compatible source generator.
