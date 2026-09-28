# M48 per-IP traffic / cstats donor applicability finding

Date: 2026-09-28  
Feature inventory ID: M48  
Target: ASUS RT-AC86U 3.0.0.4.386_52334  
Pinned donor: Merlin 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Finding

M48 is **not applicable to RT-AC86U from the pinned Merlin donor**.

The Merlin 386.14_2 source tree explicitly excludes the cstats/per-IP traffic backend on HND routers.

RT-AC86U is an HND router.

## Build exclusion

Pinned donor top-level router Makefile contains:

```make
ifneq ($(HND_ROUTER),y)
obj-y += cstats
endif
```

Therefore `cstats` is not built for HND targets.

This is not a missing ASUS feature that Merlin supplies on RT-AC86U. The donor itself excludes it for this architecture class.

## HTTPD exclusion

Pinned donor `release/src/router/httpd/data_arrays.h` declares the per-IP traffic handlers only under:

```c
#if !defined(HND_ROUTER)
extern int ej_iptmon(...);
extern int ej_ipt_bandwidth(...);
extern int ej_iptraffic(...);
extern void iptraffic_conntrack_init();
#endif
```

The corresponding implementations in `data_arrays.c` are also inside:

```c
#if !defined(HND_ROUTER)
```

Relevant donor functions include:

- `ej_iptmon()`;
- `ej_ipt_bandwidth()`;
- `ej_iptraffic()`;
- `iptraffic_conntrack_init()`.

They rely on the non-HND cstats/ipt_account style backend.

## Historical files do not change applicability

The donor source still contains references such as:

- `/var/lib/misc/cstats-history.gz`;
- `/var/spool/cstats-speed.js`;
- `/var/spool/cstats-history.js`;
- `cstats_exclude`;
- `cstats_include`;
- `cstats_all`.

Those references are part of the generic/non-HND source tree and do not prove the feature is built for RT-AC86U.

Likewise, the presence of UI source files for device/IP traffic on other models does not make the backend available on HND.

## Project decision

M48 is reclassified from **PORT** to:

**NO PORT / DONOR NOT APPLICABLE TO RT-AC86U HND**

We will not invent a new HND per-IP traffic accounting subsystem and call it a Merlin 386.14_2 port.

If a future project goal explicitly asks for a *new* per-device traffic feature, that would be a separate design effort and could potentially use:

- ASUS Traffic Analyzer/BWDPI data;
- nf_conntrack accounting;
- nftables/iptables counters;
- eBPF where kernel support allows;
- another HND-native accounting backend.

That would not be feature parity with the pinned Merlin donor and must not be conflated with M48.

## Relationship to other traffic features

This finding does **not** affect already completed/supported items:

- M47 traffic-history persistence;
- M49 global monthly traffic page;
- M50 monthly rollup rules.

Those use the stock global `rstats` path that does exist on RT-AC86U.

It also does not affect:

- M46 QoS Stats / BWDPI classification;
- ASUS Traffic Analyzer.

Those are separate data paths.

## Validation evidence required in CI

The project CI check for this classification should prove:

1. pinned donor Makefile contains `obj-y += cstats` only within a non-HND conditional;
2. HTTPD per-IP handlers are declared only under `!HND_ROUTER`;
3. handler implementations are in the same non-HND section;
4. no HND-specific cstats replacement is present in the pinned donor tree.

## Current classification

**NO PORT — PINNED DONOR DOES NOT PROVIDE M48 ON RT-AC86U/HND**

This closes M48 rather than leaving it as an indefinite source-required feature.
