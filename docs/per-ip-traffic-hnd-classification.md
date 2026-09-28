# M48 per-IP traffic/cstats — HND donor classification

Date: 2026-09-28  
Feature inventory ID: M48  
Target: ASUS RT-AC86U 386_52334 (HND)  
Pinned donor: Merlin 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Result

**CANCELLED / NO PORT**

The pinned Merlin donor source explicitly excludes the legacy per-IP traffic/cstats WebUI/backend on HND routers.

RT-AC86U is an HND platform, so this is not a missing Merlin feature for the target model. Porting it would create functionality beyond the pinned RT-AC86U donor instead of restoring donor parity.

## Backend evidence

Pinned Merlin `release/src/router/httpd/data_arrays.h` places the legacy per-IP traffic handlers behind:

```c
#if !defined(HND_ROUTER)
extern int ej_iptmon(...);
extern int ej_ipt_bandwidth(...);
extern int ej_iptraffic(...);
extern void iptraffic_conntrack_init();
...
#endif
```

The corresponding implementation in `data_arrays.c` is likewise non-HND-only.

These handlers depend on the old iptables/accounting path, including `ipt_account`, rather than the HND traffic architecture.

## WebUI evidence

Pinned Merlin `release/src/router/www/Makefile` explicitly removes the per-device traffic pages when:

`HND_ROUTER=y`

The removed pages are:

- `Main_TrafficMonitor_devdaily.asp`;
- `Main_TrafficMonitor_devmonthly.asp`;
- `Main_TrafficMonitor_devrealtime.asp`.

Therefore the donor build system itself prevents these pages from being installed on HND targets such as RT-AC86U.

## Distinction from global traffic history

This does **not** affect the already completed global traffic-history features:

- M47 traffic-history persistence — SUCCESS;
- M49 global monthly traffic history — SUCCESS.

Those use the stock ASUS `rstats`/history path and are valid on RT-AC86U.

M48 was specifically the legacy **per-IP/device cstats** path.

## Distinction from ASUS Traffic Analyzer

ASUS 52334 has its own newer Traffic Analyzer / TrendMicro/BWDPI surfaces.

Those are not the same as Merlin's legacy cstats/device-history implementation and must not be relabeled as M48 parity.

M46 QoS Stats may read BWDPI classified connection data, but that is also a separate feature.

## Project rule applied

The project restores Merlin 386.14_2 functionality on top of ASUS 52334 while preserving the newer ASUS runtime.

When the pinned Merlin build intentionally excludes a feature for HND, adding that feature to RT-AC86U would be a new feature, not a port.

Therefore:

- do not add old `ipt_account` kernel/userland machinery;
- do not add a cstats daemon solely for M48;
- do not resurrect the removed device traffic pages;
- do not weaken HND acceleration/security paths to emulate a non-HND donor feature.

## Current classification

**M48 CANCELLED / NO PORT — PINNED DONOR EXCLUDES LEGACY PER-IP CSTATS ON HND**

This supersedes the earlier provisional SOURCE-REQUIRED classification.
