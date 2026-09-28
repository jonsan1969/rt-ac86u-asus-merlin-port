# Future HND-native per-IP traffic enhancement (outside M48 donor parity)

Date: 2026-09-28  
Former inventory reference: M48 (NO PORT for donor parity)  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Merlin donor: 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Decision

**This document is not active M48 port work.** M48 is **NO PORT** because the pinned Merlin RT-AC86U/HND donor deliberately excludes classic cstats/IPTraffic.

The material below is retained only as a possible **future, separately-scoped enhancement** if the project later chooses to add a new HND-native per-device traffic engine beyond Merlin 386.14_2 donor parity.

M48 is **not a direct Merlin 386.14_2 source port on RT-AC86U/HND**.

Pinned Merlin explicitly excludes the historical cstats/IPTraffic backend from HND:

- top-level router Makefile builds `cstats` only when `HND_ROUTER != y`;
- `rc/services.c` starts/stops/restarts cstats only under `#if !defined(HND_ROUTER)`;
- HTTPD handlers `ej_iptmon`, `ej_ipt_bandwidth` and `ej_iptraffic` are compiled only under `#if !defined(HND_ROUTER)`.

The donor's cstats implementation reads:

`/proc/net/ipt_account/lan`

from the old ipt_ACCOUNT accounting backend.

Clean ASUS 386.45956 source search does not expose `ipt_ACCOUNT` / `xt_ACCOUNT` / `ipt_account` support for RT-AC86U/HND.

Therefore the original backend must not be enabled by simply deleting HND guards.

M48 requires an **HND-native per-IP accounting backend** that preserves the user-visible Merlin functionality without transplanting an unsupported legacy kernel accounting module.

## User-visible target

Restore the useful behavior represented by Merlin's device traffic pages:

- real-time per-device upload/download rate;
- cumulative per-device upload/download bytes;
- protocol counters where reasonably available;
- daily per-device history;
- monthly per-device history;
- include/exclude device filters;
- durable history persistence;
- no-auto-logout on long-running monitor pages.

The UI/API contract may remain Merlin-compatible where practical, but the backend accounting source will be different.

## Donor NVRAM contract

Pinned Merlin defines:

- `cstats_enable=0`;
- `cstats_exclude=""`;
- `cstats_include=""`;
- `cstats_all=1`;
- `cstats_sshut=1`;
- `cstats_new=0`.

These keys may be reused for compatibility if the new HND backend preserves their meaning.

Do not expose the controls until the replacement backend is functional.

## Donor history model

The old cstats daemon maintains a per-IP tree with:

- daily ring/history;
- monthly ring/history;
- current speed samples.

It emits temporary JS snapshots:

- `/var/spool/cstats-speed.js`;
- `/var/spool/cstats-history.js`.

Signals are used by HTTPD:

- SIGUSR1 => generate speed history;
- SIGUSR2 => generate daily/monthly history;
- SIGHUP => save/reload behavior.

The history file can be persisted to a configured path and uses a MAC-derived filename.

These are **behavior references**, not a mandatory implementation architecture.

The new HND backend should prefer a documented stable data format rather than serializing raw C structs from an old daemon.

## HND-native accounting requirements

The replacement collector must account traffic per LAN client without disabling or replacing ASUS HND acceleration globally.

Preferred source hierarchy:

1. use an existing ASUS/Broadcom HND accounting or flow-statistics API if later 52334-compatible source exposes one;
2. otherwise use a netfilter/nftables/iptables-compatible accounting mechanism already supported by the 52334 kernel;
3. otherwise add the smallest source/kernel accounting support that is compatible with HND fast-path statistics;
4. do **not** import the old `ipt_ACCOUNT` module merely to match donor code.

The final design must reconcile hardware/flow acceleration so counters include accelerated traffic.

A backend that only sees slow-path packets is not acceptable.

## Address ownership

Per-device traffic must be keyed by a stable LAN-client identity.

Minimum data association:

- IPv4 address;
- MAC address when known;
- client name from ASUS client database when available.

IPv6 support should be designed explicitly rather than inherited from the old IPv4-only `ipt_account/lan` backend.

If IPv6 accounting cannot be made reliable initially, the UI must state the limitation rather than silently omit it.

## Collector daemon

A new small daemon is acceptable if needed.

Responsibilities:

1. periodically snapshot per-client byte/packet counters;
2. calculate rate deltas;
3. maintain daily/monthly aggregates;
4. apply include/exclude policy;
5. persist history safely;
6. expose read-only snapshots to HTTPD through a bounded local file/socket/API.

Requirements:

- no shell command polling loop;
- monotonic counter handling;
- wrap/reset detection;
- atomic snapshot writes;
- bounded memory by maximum tracked clients/history;
- safe shutdown/save;
- no NVRAM writes on every sample.

The daemon must not own firewall policy; it only reads/accounting state.

## Persistence

M47/M49 already provide a proven persistent traffic-history pattern for global rstats.

M48 should reuse the same persistence philosophy:

- explicit user-selected durable path;
- atomic temp+rename writes;
- bounded save interval;
- backup rotation if useful;
- no excessive flash writes.

Do not reuse the donor's raw `Node` binary serialization as a public format.

Use a versioned format so future schema upgrades are possible.

## Read-only HTTPD/API

The old donor pages expect three styles of data:

### Live device list

Equivalent to `iptraffic()`:

- per-IP bytes;
- rate deltas;
- protocol/connection counts where supported.

### Speed history

Equivalent to `ipt_bandwidth("speed")`.

### Daily/monthly history

Equivalent to `ipt_bandwidth("daily"|"monthly")`.

The new backend can expose JSON/JS through modern read-only handlers instead of signaling a daemon to create predictable files in `/var/spool`.

Preferred API:

- authenticated GET endpoints;
- bounded JSON response;
- no temporary file race;
- no user-controlled filesystem path.

## WebUI

Merlin donor pages include:

- `Main_TrafficMonitor_devrealtime.asp`;
- `Main_TrafficMonitor_devdaily.asp` where applicable;
- `Main_TrafficMonitor_devmonthly.asp`.

The realtime page explicitly disables auto logout; preserve that project behavior.

For this project, pages may be adapted to the existing ASUS/Merlin-compatible traffic-monitor layout already used by M47/M49.

Reuse the local Chart.js already staged for traffic history.

Do not duplicate chart libraries.

## Protocol counters

The old `ej_iptraffic` parses per-protocol packet counters from `ipt_account/lan` and combines them with conntrack state.

On HND, protocol counters are optional until a trustworthy accelerated-path accounting source is identified.

Priority order:

1. correct byte totals and rates;
2. correct daily/monthly history;
3. correct connection counts;
4. protocol split if backed by reliable target data.

Do not fake TCP/UDP/ICMP columns from incomplete data.

## Interaction with ASUS Traffic Analyzer

ASUS 52334 has TrendMicro Traffic Analyzer functionality.

M48 must not:

- disable it;
- scrape private TrendMicro databases as the sole accounting backend;
- alter its retention;
- depend on cloud services.

If a stable local ASUS API can provide exact per-client byte counters, it may be reused after verification.

## Interaction with acceleration

Validation must test:

- NAT acceleration/CTF/FA/HND flow acceleration enabled;
- acceleration disabled where possible;
- LAN↔WAN large transfers;
- Wi-Fi and wired clients;
- upload and download separately.

Counter accuracy must remain within a documented small tolerance in both accelerated and non-accelerated cases.

If enabling per-IP accounting requires disabling a hardware acceleration mode, that tradeoff must be explicit and treated as a product decision, not silently applied.

## Validation gate

Before M48 becomes **SUCCESS**, prove:

1. donor legacy cstats/ipt_ACCOUNT path remains disabled on HND;
2. new backend sees accelerated WAN traffic;
3. wired client upload/download totals are accurate;
4. Wi-Fi client upload/download totals are accurate;
5. two simultaneous clients remain separated correctly;
6. DHCP IP reassignment does not merge unrelated device history incorrectly;
7. counter reset/reboot does not create huge negative/overflow deltas;
8. include/exclude rules behave deterministically;
9. daily rollover is correct;
10. monthly rollover is correct;
11. history persists across reboot when enabled;
12. disabling persistence does not write continuously to JFFS;
13. live polling does not materially increase CPU load;
14. IPv6 behavior is either correct or explicitly unavailable;
15. ASUS Traffic Analyzer and global rstats remain functional;
16. no unsupported old `ipt_ACCOUNT` kernel module is imported;
17. no ASUS core binary is replaced.

## Current classification

**OUT OF SCOPE FOR M48 / FUTURE ENHANCEMENT ONLY**

The pinned donor itself does not provide classic per-device cstats/IPTraffic on HND. Any HND-native replacement would be a new feature beyond donor parity and requires a separate project decision before implementation.
