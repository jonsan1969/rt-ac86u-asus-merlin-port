# Traditional QoS overhead and download-statistics source contract

Date: 2026-09-28  
Feature inventory ID: M64  
Related feature: M46 QoS Stats  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Clean source-lineage anchor: ASUS 386.45956 @ `a9179fc9329565dea0f7c5c7648fe8ad49ceaaf6`  
Merlin donor: 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Purpose

Bound the Merlin 386.14_2 deltas that improve Traditional QoS shaping accuracy and expose useful download-side class statistics, while preserving the newer ASUS 52334 QoS implementation.

M64 is source-only. No donor `rc`, `tc`, kernel qdisc/module, or HTTPD binary may be transplanted.

## Part A — shaping overhead / framing accuracy

### Source-lineage result

Clean ASUS 386.45956 `release/src/router/rc/qos.c` lacks:

- `qos_overhead`;
- `qos_atm`;
- the donor `overhead %d %s` tc syntax.

Pinned Merlin adds these inputs to the existing QoS script-generation path.

Pinned Merlin defaults on BCM ARM include:

- `qos_overhead=0` — overhead in bytes;
- `qos_atm=0` — 0 Ethernet, 1 ATM, 2 PTM where supported;
- `qos_mpu=0` — minimum packet unit input used by Cake-related paths.

M32 Cake itself remains source/kernel-required and is not implied by M64.

### Traditional HTB behavior

For relevant BCM ARM Traditional QoS paths, Merlin reads `qos_overhead`.

Where the generated tc syntax supports an overhead argument, the donor builds:

```text
overhead <bytes> linklayer atm
```

when ATM framing is selected, otherwise:

```text
overhead <bytes> linklayer ethernet
```

When overhead is zero, the donor omits that overhead string.

The final port must inject this behavior into the later ASUS 52334-compatible QoS generator rather than copy the donor function wholesale.

### Interface/header adjustment

The donor also adjusts user-visible IP overhead before applying it to HTB paths that already account for an Ethernet header:

- subtract 14 bytes where the shaped interface already includes the Ethernet header;
- clamp negative results to zero;
- keep the PPP path unadjusted where the donor determines no adjustment is required.

Download-side adjustment differs depending on the donor IMQ/CLS_ACT path. The final merge must review the later ASUS HND datapath rather than assume the donor's interface arrangement.

### ATM/PTM mode

Pinned donor behavior includes mode-dependent handling, including a PTM mode in newer QoS paths.

Do not expose PTM/MPU choices unless the later ASUS target path actually consumes them. The minimum M64 contract is accurate donor-equivalent overhead/framing behavior for the QoS path available on RT-AC86U.

## Part B — download class statistics

Pinned Merlin's QoS Stats backend uses `ej_tcclass_dump_array()` in `httpd/data_arrays.c`.

For Traditional/Adaptive/Geforce-style classful modes it gathers LAN/download-side class data with:

```sh
tc -s class show dev br0
tc -s class show dev imq0
```

then parses the result into `tcdata_lan_array`.

It separately gathers WAN/upload-side class data from the active WAN interface into `tcdata_wan_array`.

This HTTPD/data-array surface is absent from the clean ASUS 45956 source anchor and the ASUS 52334 runtime probe found no Merlin QoS Stats page/backend contract.

Therefore the M64 statistics portion must be implemented **inside the M46 QoS Stats source integration**, not as a second page/backend port.

## Source patch boundary

Expected later-ASUS patch areas are:

1. current QoS defaults, only for keys actually consumed by the final implementation;
2. current ASUS QoS script generator for overhead/framing;
3. M46's future HTTPD tc-class data handler for download statistics;
4. current QoS UI for the relevant controls only after backend support exists.

Do not replace ASUS QoS wholesale and do not enable unsupported qdisc/kernel functionality.

## WebUI rules

The donor UI exposes overhead/framing controls conditionally based on supported QoS/qdisc mode.

For this project:

- never expose a control whose NVRAM value is not consumed by the final source path;
- keep ASUS 52334's newer QoS layout and mode selection authoritative;
- add only controls that correspond to verified backend semantics;
- keep M32 Cake controls gated behind an actual Cake-compatible source/kernel build.

## Validation gate

### Shaping accuracy

1. default `qos_overhead=0` preserves stock ASUS-generated QoS behavior;
2. positive overhead produces the expected tc overhead parameter;
3. ATM mode produces donor-equivalent ATM framing semantics;
4. Ethernet mode produces donor-equivalent Ethernet framing semantics;
5. any Ethernet-header subtraction is applied only on the interface paths where it is correct;
6. negative adjusted overhead is clamped to zero;
7. PPP and HND interface handling is validated against the later ASUS source, not assumed from donor layout.

### Statistics

8. M46 reports upload and download class counters from the correct target interfaces;
9. disabled QoS returns empty/valid arrays instead of stale data;
10. temporary tc dump files are removed;
11. statistics polling does not alter shaping state;
12. no duplicate M46/M64 HTTPD handler implementations are created.

## Current classification

**SOURCE-REQUIRED**

The donor overhead/framing semantics are independently bounded. Download statistics remain a sub-requirement of M46's source-side QoS Stats backend.
