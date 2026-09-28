# M48 per-IP traffic / cstats HND donor classification

Date: 2026-09-28  
Feature inventory ID: M48  
Target: RT-AC86U / HND  
Pinned Merlin donor: 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Result

**NO PORT for pinned RT-AC86U donor parity.**

The Merlin source tree contains the old Tomato-derived `cstats` implementation, but Merlin 386.14_2 deliberately excludes the complete feature on HND routers.

RT-AC86U is HND.

Therefore M48 is not a source-required missing Merlin feature for this target. Porting it would create a new feature that the pinned donor itself does not provide on RT-AC86U-class HND builds.

## Evidence

### 1. cstats daemon is not built on HND

Pinned donor `release/src/router/Makefile`:

```make
ifneq ($(HND_ROUTER),y)
obj-y += cstats
endif
```

The `release/src/router/cstats/` source directory exists, but the router build deliberately omits the daemon for HND.

### 2. cstats service lifecycle is not compiled on HND

Pinned donor `rc/services.c` wraps:

- `stop_cstats()`;
- `start_cstats()`;
- `restart_cstats()`;
- the `rc_service cstats` dispatcher;
- boot/restart calls;

inside `#if !defined(HND_ROUTER)`.

So HND builds do not start or manage the daemon.

### 3. ipt_account firewall accounting is not installed on HND

Pinned donor `rc/firewall.c` wraps the cstats accounting chains and `ipt_account()` setup inside:

```c
#if !defined(HND_ROUTER)
...
#endif
```

The shared helper `ipt_account()` is likewise declared/implemented only for non-HND.

The old `cstats` daemon reads:

`/proc/net/ipt_account/lan`.

Without that accounting path, its primary input is absent.

### 4. HTTPD per-IP handlers are excluded on HND

Pinned donor `httpd/data_arrays.h` places:

- `ej_iptmon`;
- `ej_ipt_bandwidth`;
- `ej_iptraffic`;
- `iptraffic_conntrack_init`;

under:

`#if !defined(HND_ROUTER)`.

The matching implementation area in `data_arrays.c` is also non-HND.

### 5. WebUI per-device pages are removed from HND images

Pinned donor `www/Makefile` explicitly removes:

- `Main_TrafficMonitor_devdaily.asp`;
- `Main_TrafficMonitor_devmonthly.asp`;
- `Main_TrafficMonitor_devrealtime.asp`;

when:

`HND_ROUTER=y`.

The source files remain in the tree because non-HND models use them, but they are not part of the HND installed WebUI.

## Why source presence was misleading

The donor tree contains:

- `release/src/router/cstats/cstats.c`;
- cstats defaults such as `cstats_enable`;
- per-device ASP pages.

Those files are shared across many router families.

For feature inventory purposes, source presence alone is insufficient. The target build guards are decisive.

On HND, Merlin intentionally disables the daemon, accounting backend, service lifecycle, HTTPD handlers and installed pages as one coherent feature boundary.

## Relationship to other traffic features

This reclassification does **not** affect:

- M47 traffic-history persistence — already SUCCESS;
- M49 global monthly traffic — already SUCCESS;
- M46 QoS Stats — separate tc/BWDPI read-only backend;
- ASUS/TrendMicro Traffic Analyzer — newer separate ASUS capability.

M48 specifically means the legacy Merlin/Tomato per-IP `cstats`/IPTraffic feature.

## Project rule applied

The project ports features actually present in Merlin 386.14_2 for the RT-AC86U target generation.

It does not use dormant source for other platforms as justification to invent a new HND subsystem.

A future project could deliberately design a modern HND per-IP accounting feature using nftables/netfilter/BWDPI/flow accounting, but that would be a new enhancement, not donor parity, and is outside M48.

## Classification

**M48: NO PORT — PINNED MERLIN HND BUILD DELIBERATELY EXCLUDES CSTATS/IPTRAFFIC**
