# M48 per-IP traffic / cstats classification

Date: 2026-09-28  
Feature inventory ID: M48  
Target: RT-AC86U / HND  
Pinned donor: Merlin 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Result

**NO PORT — the pinned RT-AC86U/HND donor build deliberately excludes classic cstats/IP Traffic.**

Earlier runtime probing correctly found that ASUS 52334 lacks:

- `cstats`;
- `/proc/net/ipt_account/lan` based Merlin accounting;
- classic `ipt_bandwidth`/IPTraffic HTTPD handlers;
- device traffic pages.

Source inspection now shows that this is not an ASUS-only gap. Merlin 386.14_2 itself excludes the classic per-IP traffic implementation on HND, which includes RT-AC86U.

## Donor source evidence

### cstats daemon

The donor contains a standalone source component:

`release/src/router/cstats/`

including `cstats.c`, `cstats.h` and a Makefile.

However the top-level router Makefile builds it only under:

```make
ifneq ($(HND_ROUTER),y)
obj-y += cstats
endif
```

Therefore the presence of cstats source in the repository does not mean it is part of the RT-AC86U donor firmware.

### rc lifecycle

The donor's `stop_cstats()`, `start_cstats()` and `restart_cstats()` implementation is enclosed in:

```c
#if !defined(HND_ROUTER)
...
#endif
```

The `rc_service` handler for `cstats` is likewise excluded on HND.

### firewall accounting

The classic per-IP accounting setup in `rc/firewall.c` is also guarded by:

```c
#if !defined(HND_ROUTER)
if (nvram_match("cstats_enable", "1")) {
    ...
    ipt_account(fp, NULL);
}
#endif
```

So HND does not get the donor's `ipt_account` rule chain that cstats expects.

### HTTPD handlers

The donor declares classic IP traffic handlers only under:

```c
#if !defined(HND_ROUTER)
extern int ej_iptmon(...);
extern int ej_ipt_bandwidth(...);
extern int ej_iptraffic(...);
...
#endif
```

These handlers therefore are not part of the HND WebUI backend contract.

### WebUI pages

The donor WebUI Makefile explicitly deletes on HND:

- `Main_TrafficMonitor_devdaily.asp`;
- `Main_TrafficMonitor_devmonthly.asp`;
- `Main_TrafficMonitor_devrealtime.asp`.

This closes the loop: the daemon, firewall accounting, HTTPD API and UI are all deliberately absent from the pinned RT-AC86U/HND build.

## Why we do not port the non-HND feature anyway

The project goal is to restore **Merlin 386.14_2 functionality applicable to RT-AC86U** on top of ASUS 52334.

Importing cstats from Merlin's non-HND model path would instead create a new cross-platform backport that the pinned RT-AC86U donor itself does not ship.

It would also require reintroducing an old `ipt_account` architecture into the HND networking/acceleration stack, which violates the ASUS-first runtime rule without a donor requirement to justify it.

## Relationship to existing traffic features

This decision does not affect:

- M47 traffic-history persistence — already SUCCESS using ASUS rstats;
- M49 global monthly traffic — already SUCCESS using ASUS rstats history;
- ASUS/TrendMicro Traffic Analyzer — remains ASUS-owned;
- M46 QoS Stats — separate read-only tc/BWDPI feature.

Do not confuse global rstats history with classic per-IP cstats.

## Classification

**M48: NO PORT / DONOR-DISABLED ON HND**

If a future project intentionally wants to design a new per-device traffic engine for HND, that is a separate feature request and must use an HND-native accounting architecture rather than reviving Merlin's non-HND cstats path.
