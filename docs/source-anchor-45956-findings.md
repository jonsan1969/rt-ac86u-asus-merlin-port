# Clean ASUS 386.45956 source anchor findings

Date: 2026-09-28

## Scope

This document records the clean-source archaeology anchor used while matching ASUS RT-AC86U `386_52334` source is unavailable.

It does **not** change the project runtime/build rule:

- final runtime baseline: official ASUS RT-AC86U `3.0.0.4.386_52334`;
- clean source archaeology anchor: community mirror `blackfuel/asuswrt-rt-ac86u` at `a9179fc9329565dea0f7c5c7648fe8ad49ceaaf6` (`386.45956`);
- Merlin donor/reference: `RMerl/asuswrt-merlin.ng` at `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b` (`386.14_2`).

The 45956 tree is only a lineage and merge-shape reference. It is not a substitute for 52334 source and must not be used to overwrite later ASUS runtime components.

## High-value result

The custom-script helper implementation is not a Merlin-only invention at this source generation.

`release/src/router/shared/scripts.c` exists in both pinned trees with the same four helper functions:

- `run_custom_script()`;
- `run_postconf()`;
- `use_custom_config()`;
- `append_custom_config()`.

The clean ASUS 45956 tree nevertheless does not expose the feature normally:

- `shared/Makefile` compiles `scripts.o` only when `RTCONFIG_TOR=y`;
- `shared/shared.h` declares the helper API only inside `#ifdef RTCONFIG_TOR`;
- `config_base` has `RTCONFIG_TOR is not set`;
- ASUS `defaults.c` has no `jffs2_scripts` default;
- normal Merlin lifecycle hook call sites are absent.

Merlin 386.14_2 removes the build dependency on TOR, adds ungated declarations, adds `jffs2_scripts=0`, creates the JFFS addon directories, and wires the helper into lifecycle/configuration call sites.

This materially narrows the future source port: preserve the ASUS implementation of the helper where a later ASUS source baseline still carries it, then expose and call it deliberately. Do not import a Merlin `rc`, `httpd`, or shared binary.

## Exact lifecycle call-site delta at the pinned anchor

| Feature/API | Clean ASUS 45956 | Merlin 386.14_2 | Source area / required semantics |
|---|---|---|---|
| `services-start` | absent | present | `rc/services.c`, async after normal service startup |
| `services-stop` | absent | present | `rc/services.c`, async before normal service shutdown |
| `service-event` | absent | present | `rc/services.c`, blocking max 120s before dispatch, args action + service |
| `service-event-end` | absent | present | `rc/services.c`, async after dispatch, same args |
| `nat-start` | absent | present | `rc/services.c`, async after conntrack/UDP timeout setup reaches normal state |
| `firewall-start` custom script call | absent | present | `rc/firewall.c`, async after firewall lock/reload, WAN interface arg |
| `dhcpc-event` IPv4 | absent | present | `rc/udhcpc.c`, event + literal `"4"` |
| `dhcpc-event` IPv6 | absent | present | `rc/udhcpc.c`, event + literal `"6"` |
| `zcip-event` | absent | present | `rc/udhcpc.c`, event arg |
| `qos-start rules` | absent | present | `rc/qos.c`, async after rule programming |
| `qos-start init` | absent | present | `rc/qos.c`, blocking max 120s before generated QoS start script executes |
| `pre-mount` | absent | present | `rc/usb.c`, blocking max 120s, device + filesystem type |
| `post-mount` | absent | present | `rc/usb.c`, blocking max 120s, mountpoint |
| `unmount` custom script call | absent | present | `rc/usb.c`, blocking max 120s before sync/unmount loop |
| `wan-event` | absent | present | `rc/wan.c`, async state transition context |
| legacy `wan-start` | absent | present | `rc/wan.c`, async on connected state |
| `init-start` | absent | present | `rc/init.c`, after JFFS is available and before custom fstab/passwd reapply |
| `update-notification` | absent | present | `rc/watchdog.c`, async after new-firmware state/logging |

A later ASUS source tree must be reviewed around each insertion point. These are behavioral anchors, not permission to replace the surrounding function with donor code.

## JFFS mount delta

At the pinned clean anchor, both ASUS and Merlin already have the legacy `.asusrouter` / `jffs2_exec` or `ubifs_exec` blocks disabled with `#if 0`.

Merlin then adds exactly the active directory bootstrap needed by the addon framework after the persistent filesystem has been prepared:

```c
if (!check_if_dir_exist("/jffs/scripts/")) mkdir("/jffs/scripts/", 0755);
if (!check_if_dir_exist("/jffs/configs/")) mkdir("/jffs/configs/", 0755);
if (!check_if_dir_exist("/jffs/addons/")) mkdir("/jffs/addons/", 0755);
```

For RT-AC86U/HND the relevant path is `rc/ubifs.c`; `rc/jffs2.c` carries the equivalent behavior for other storage layouts.

Do not revive the disabled legacy autoexec path.

## Build/default exposure delta

The pinned anchor establishes the minimal helper-exposure changes conceptually required in a later ASUS-compatible source tree:

1. compile `shared/scripts.o` independently of `RTCONFIG_TOR`;
2. expose the four helper declarations independently of `RTCONFIG_TOR`;
3. retain the helper implementation from the ASUS lineage when equivalent;
4. add `jffs2_scripts=0` under the appropriate JFFS/UBIFS build condition;
5. create `/jffs/scripts`, `/jffs/configs`, and `/jffs/addons` after successful persistent-filesystem setup;
6. add reviewed lifecycle hook call sites one file/function at a time.

The Administration/System UI switch remains gated until the core engine is actually present.

## Source-integration order

When a sufficiently late clean ASUS source baseline becomes buildable, use this order:

1. **shared helper exposure** — build/declarations/default only, no lifecycle calls;
2. **UBIFS/JFFS directory bootstrap** — three directories, no legacy autoexec;
3. **init/services/firewall/WAN hooks** — smallest core lifecycle block;
4. **DHCP/QoS/USB/watchdog hooks** — preserve arguments and blocking semantics;
5. **custom config/postconf generator hooks** — review each ASUS generator independently;
6. **HTTPD/UI enablement** — only after the underlying engine is functional;
7. **AMTM/addon exposure** — only after lifecycle hooks and required utilities are validated.

## Validation requirements

A source build implementing this contract must prove at least:

- helper symbols are linked without enabling TOR;
- `jffs2_scripts=0` suppresses scripts/config overrides;
- `jffs2_scripts=1` enables executable scripts only;
- blocking hooks are bounded;
- service-event ordering and arguments match the donor API;
- DHCPv4/v6 protocol arguments remain `4` / `6`;
- USB hook arguments and ordering match the donor API;
- JFFS directories are created only after successful persistent mount;
- disabled legacy `.asusrouter`/exec behavior stays disabled;
- later ASUS networking/firewall/USB behavior is unchanged when no custom script is installed.

## Current classification

**SOURCE-LINEAGE ANCHOR: VERIFIED**

**52334 SOURCE BUILD PATH: STILL BLOCKED**

This anchor reduces uncertainty about *how* to port the JFFS/custom-script engine, but it does not prove ABI/source equivalence to 52334 and does not authorize a 45956-based replacement of ASUS 52334 core binaries.
