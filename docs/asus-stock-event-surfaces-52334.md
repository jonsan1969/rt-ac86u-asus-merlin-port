# ASUS 52334 stock event surfaces

Date: 2026-09-28  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Probe run: `36415137373`

## Purpose

Record stock ASUS callback surfaces that can safely inform later image/source adaptations without overstating them as Merlin JFFS hook parity.

The probe is observational only. It does not authorize a core-binary patch.

## Confirmed stock callbacks

### PPP ip-up.local

Stock ASUS 52334 `/rom/etc/ppp/ip-up` contains:

```sh
[ -x /etc/ppp/ip-up.local ] && /etc/ppp/ip-up.local "$@"
```

This is a real executable callback after the stock PPP ip-up script reaches that point.

### PPP ip-down.local

Stock ASUS 52334 `/rom/etc/ppp/ip-down` similarly contains:

```sh
[ -x /etc/ppp/ip-down.local ] && /etc/ppp/ip-down.local "$@"
```

This is a real executable callback for the PPP teardown path.

### Shell profile extension

Stock ASUS 52334 `/rom/etc/profile` already sources:

```sh
[ -f /jffs/etc/profile ] && . /jffs/etc/profile
```

The project additionally has an image-safe exact patch for Merlin-style `/jffs/configs/profile.add` gating.

### Hotplug dispatcher

Stock `/rom/etc/hotplug2.rules` dispatches selected kernel/USB events to ASUS `/sbin/hotplug` and dedicated ASUS USB handlers.

This is an ASUS internal event surface, not a generic user-script extension point.

## What these callbacks do not replace

The PPP-local callbacks are **protocol/path specific**.

They do not provide full equivalents for:

- `wan-start`;
- `wan-event`;
- DHCPv4 `dhcpc-event`;
- DHCPv6 `dhcpc-event`;
- `services-start`;
- `service-event`;
- `firewall-start`;
- `post-mount`.

A router using DHCP WAN can never rely on PPP `ip-up.local`, and even on PPP WAN the callback timing/arguments are not the same API contract as Merlin `wan-event`.

Therefore M01-M03 remain source-required.

## Allowed future use

The stock PPP callbacks may be used only for a feature whose required lifecycle is specifically tied to the PPP path and whose argument/order contract has been proven compatible.

Any wrapper added there must be:

- add-only;
- idempotent;
- fail-open with respect to ASUS WAN connectivity;
- bounded in runtime;
- independent of Merlin core binaries.

Do not make a generic addon framework depend on them.

## ASUS app/init observations

The stock image also contains ASUS application scripts and internal event tokens such as:

- `notify_rc*`;
- `rc_service`;
- `/sbin/hotplug`;
- `app_init_run.sh`.

These remain ASUS-private lifecycle mechanisms unless a concrete add-only extension contract is proven.

In particular, the mere presence of strings such as `firewall-start` inside an ASUS app script does not establish a globally supported user hook.

## Classification

**SUPPLEMENTAL STOCK CALLBACKS VERIFIED**

**NO GENERAL M03 SUBSTITUTE FOUND**

Probe run `36415137373` explicitly remains report-only and authorizes no protected-core modification.
