# JFFS core source patch series

Date: 2026-09-28  
Feature inventory IDs: M01, M02, M03, M41, M42  
Related contract: `docs/custom-config-postconf-source-contract.md`

## Goal

Define the smallest ordered source patch series that restores Merlin's JFFS user-script lifecycle API while preserving later ASUS control flow.

The lifecycle call signatures below are stable between:

- Merlin `386.12_x` pinned at `5b47ec64ce58d23c591e809d4cbad09d1121c4ea`, based on ASUS GPL 386_51997;
- Merlin `386.14_2` pinned at `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`.

That stability across the late ASUS GPL merge materially strengthens the source contract.

This is still not permission to replace ASUS 52334 `rc`. Each patch must be merged into a sufficiently late ASUS-compatible source tree.

## Patch 1 — expose the inherited helper

Clean ASUS 386.45956 already contains the exact four helper implementations in `shared/scripts.c`:

- `run_custom_script()`;
- `run_postconf()`;
- `use_custom_config()`;
- `append_custom_config()`.

Required source changes:

1. compile `shared/scripts.o` independently of `RTCONFIG_TOR`;
2. expose the helper declarations independently of `RTCONFIG_TOR`;
3. add `jffs2_scripts=0` under the correct later-ASUS persistent-JFFS/UBIFS build condition.

Do **not** replace `scripts.c`; preserve the ASUS-lineage implementation unless a later clean source proves it changed.

## Patch 2 — bootstrap addon directories after persistent mount

On RT-AC86U/HND the relevant storage implementation is `rc/ubifs.c`.

After successful persistent filesystem preparation, create if absent:

- `/jffs/scripts/`;
- `/jffs/configs/`;
- `/jffs/addons/`.

Modes: 0755.

Do not revive the disabled legacy `.asusrouter`/autoexec block.

## Patch 3 — init/services core hooks

These are the minimum high-value lifecycle hooks for addon frameworks and Entware-style services.

### init-start

`rc/init.c`

Stable donor call:

```c
run_custom_script("init-start", 0, NULL, NULL);
```

Semantics: asynchronous.

Placement requirement: after JFFS is available, at the reviewed late-ASUS initialization point used by the donor lineage.

### services-start

`rc/services.c`

```c
run_custom_script("services-start", 0, NULL, NULL);
```

Semantics: asynchronous after normal service startup reaches the donor-equivalent completion point.

### services-stop

`rc/services.c`

```c
run_custom_script("services-stop", 0, NULL, NULL);
```

Semantics: asynchronous at the donor-equivalent shutdown point before/around normal service teardown as verified against later ASUS flow.

### service-event

`rc/services.c`

```c
run_custom_script("service-event", 120, actionstr, script);
```

Semantics:

- blocking;
- max 120 seconds;
- argv[1] = action string;
- argv[2] = service/script target;
- runs before the service dispatch.

### service-event-end

`rc/services.c`

```c
run_custom_script("service-event-end", 0, actionstr, script);
```

Semantics:

- asynchronous;
- same two arguments;
- runs after the service dispatch.

## Patch 4 — network/firewall lifecycle hooks

### nat-start

`rc/services.c`

```c
run_custom_script("nat-start", 0, NULL, NULL);
```

Asynchronous after the reviewed normal NAT setup reaches its ready point.

### firewall-start

`rc/firewall.c`

```c
run_custom_script("firewall-start", 0, wan_if, NULL);
```

Asynchronous.

argv[1] = WAN interface used by that firewall generation path.

Do not move this call across later ASUS lock/reload/acceleration sequencing without review.

### wan-event

`rc/wan.c`

```c
run_custom_script("wan-event", 0, tmp, tmp1);
```

Asynchronous.

Preserve the donor mapping of the two transition/context arguments from the later source function rather than copying variable names mechanically.

### wan-start

`rc/wan.c`

```c
run_custom_script("wan-start", 0, tmp, NULL);
```

Legacy asynchronous WAN-connected hook.

## Patch 5 — DHCP/ZCIP event hooks

`rc/udhcpc.c`

The API has **three distinct contexts** and they must not be collapsed.

### WAN DHCPv4

```c
run_custom_script("dhcpc-event", 0, argv[1], "4");
```

Arguments:

- argv[1] = DHCP event;
- argv[2] = literal `4`.

### LAN/AP DHCP client path

```c
run_custom_script("dhcpc-event", 0, argv[1], NULL);
```

This is a separate LAN/AP client event path and intentionally has **no protocol argument**.

### WAN DHCPv6

```c
if (argv[2])
    run_custom_script("dhcpc-event", 0, argv[2], "6");
```

Arguments:

- argv[1] to script = DHCPv6 event carried in donor C `argv[2]`;
- argv[2] to script = literal `6`.

### ZCIP

```c
run_custom_script("zcip-event", 0, argv[1], NULL);
```

Asynchronous with the ZCIP event as the single argument.

## Patch 6 — USB mount lifecycle hooks

`rc/usb.c`

These are intentionally blocking because addons may need to prepare or release filesystem state.

### pre-mount

```c
run_custom_script("pre-mount", 120, dev_name, type);
```

Arguments:

- device name;
- filesystem type.

### post-mount

```c
run_custom_script("post-mount", 120, mountpoint, NULL);
```

Argument: mountpoint.

### unmount

```c
run_custom_script("unmount", 120, mnt->mnt_dir, NULL);
```

Argument: mountpoint being unmounted.

The unmount hook must run before the donor-equivalent sync/unmount loop and remain bounded.

## Patch 7 — QoS hook semantics

`rc/qos.c`

Pinned 386.12 and 386.14_2 both contain:

```c
run_custom_script("qos-start", 0, "rules", NULL);
```

for the rule-generation phase, and:

```c
run_custom_script("qos-start", 120, "init", NULL);
```

at both relevant QoS initialization paths.

Contract:

- `rules` = asynchronous;
- `init` = blocking, max 120 seconds;
- preserve both init call sites if the later ASUS code still has two equivalent initialization flows.

Do not reduce these to one generic QoS callback.

## Patch 8 — update notification hook

`rc/watchdog.c`

```c
run_custom_script("update-notification", 0, NULL, NULL);
```

Asynchronous after the reviewed new-firmware notification state/logging has been established.

This patch is lower priority than services/network/USB hooks and can be staged later.

## Patch 9 — M04 generator framework

Apply `docs/custom-config-postconf-source-contract.md` after helper exposure is working.

Tier-1 generators can be integrated independently of lower-priority lifecycle hooks.

## Build/merge rule

For every patch:

1. locate the equivalent function in the **latest ASUS-compatible source available**;
2. compare the late 386.12 source shape;
3. insert only the helper call and minimal required declarations/default;
4. preserve all later ASUS surrounding logic;
5. compile that component from source;
6. validate behavior with `jffs2_scripts=0` and with no script present before testing active hooks.

No patch should be implemented by copying an entire donor function when a call-site insertion is sufficient.

## Runtime validation matrix

At minimum, test:

| Hook | Disabled | Missing script | Executable script | Timeout/order |
|---|---|---|---|---|
| init-start | no run | no effect | async once | after JFFS ready |
| services-start/stop | no run | no effect | async | correct service boundary |
| service-event | no run | no effect | receives 2 args | blocks max 120s before dispatch |
| service-event-end | no run | no effect | receives 2 args | async after dispatch |
| nat-start | no run | no effect | async | NAT ready point |
| firewall-start | no run | no effect | WAN iface arg | after firewall apply |
| wan-event | no run | no effect | 2 donor-equivalent args | transition ordering |
| wan-start | no run | no effect | WAN context arg | connected point |
| dhcpc-event v4 | no run | no effect | event + `4` | before donor-equivalent handling |
| dhcpc-event LAN | no run | no effect | event only | separate LAN path |
| dhcpc-event v6 | no run | no effect | event + `6` | donor-equivalent ordering |
| zcip-event | no run | no effect | event only | donor-equivalent ordering |
| pre-mount | no run | no effect | device + fs type | blocks max 120s |
| post-mount | no run | no effect | mountpoint | blocks max 120s |
| unmount | no run | no effect | mountpoint | blocks max 120s before unmount |
| qos-start rules | no run | no effect | `rules` | async |
| qos-start init | no run | no effect | `init` | blocks max 120s |
| update-notification | no run | no effect | async | after update state |

## Current classification

**PATCH SERIES DEFINED / SOURCE TARGET STILL REQUIRED**

The core JFFS lifecycle API is stable across the late 51997-based Merlin branch and 386.14_2. The remaining blocker is not donor ambiguity; it is obtaining or constructing a sufficiently late ASUS-compatible source/build target without regressing 52334 runtime behavior.
