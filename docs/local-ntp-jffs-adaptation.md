# Local NTP server and NTP interception integration contract

Date: 2026-09-28  
Feature inventory IDs: M29, M30  
Related dependency: M01-M04 JFFS lifecycle/config engine  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Clean ASUS source anchor: 386.45956 @ `a9179fc9329565dea0f7c5c7648fe8ad49ceaaf6`  
Late donor reference: Merlin 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Decision

Preserve the ASUS 52334 time-synchronization stack completely.

Do **not** replace ASUS BusyBox.  
Do **not** transplant Merlin BusyBox.  
Do **not** replace ASUS's `rc` NTP client or its `ntp_ready` lifecycle.

Instead:

- build a dedicated, isolated NTP server executable from compatible ASUS-lineage BusyBox `ntpd` source;
- run it in **query/server-only mode** so it never disciplines the system clock;
- manage it through the generic JFFS lifecycle engine;
- add DHCP advertisement through M04 `dnsmasq.postconf`;
- implement M30 interception through the generic `firewall-start` hook.

This makes M29/M30 adaptations layered on top of the JFFS core rather than new ASUS core-binary patches.

## Provenance of Merlin `/usr/sbin/ntp`

Pinned Merlin enables:

- `RTCONFIG_NTPD=y`;
- BusyBox `CONFIG_NTPD=y`;
- `CONFIG_FEATURE_NTPD_SERVER=y`;
- `CONFIG_FEATURE_NTPD_CONF=y`.

Its top-level build logic also forces:

`CONFIG_FEATURE_NTPD_NTP_ALIAS=y`

when `NTPD=y`.

BusyBox's applet table defines:

- `ntpd` in `/usr/sbin`;
- optional alias `ntp -> ntpd`.

Therefore Merlin's `/usr/sbin/ntp` is a BusyBox NTPD applet alias. It is **not** a standalone donor binary and must not be transplanted.

## Clean ASUS source result

Clean ASUS 386.45956 already contains:

`release/src/router/busybox/networking/ntpd.c`

with all behavior needed for a local server:

- `-l` — listen as NTP server on UDP/123;
- `-I IFACE` — bind the server to a specific interface;
- `-w` — query peers but do not set system time;
- `-p PEER` — upstream peer;
- `-t` — donor-compatible trust mode;
- `-S PROG` — optional callback;
- the UDP/123 server receive/reply loop.

Clean ASUS simply disables:

- `CONFIG_NTPD`;
- `CONFIG_FEATURE_NTPD_SERVER`;
- `CONFIG_FEATURE_NTPD_CONF`;

in its BusyBox base configuration.

This makes the NTP daemon code ASUS-lineage source, not a Merlin-only implementation.

## ASUS time ownership must remain intact

Clean ASUS `rc/ntp.c` demonstrates the stock architecture:

- `/sbin/ntp` is an `rc` multicall command;
- it launches `ntpclient`;
- it owns `ntp_ready`;
- it performs timezone/service initialization;
- later stock code uses `ntp_ready` to gate DNS Privacy, DDNS, scheduled services and other functionality;
- `refresh_ntpc()` and WAN events drive continued synchronization.

ASUS 52334 remains authoritative for all of this.

The local NTP server must **not**:

- be named/process-matched as `ntp`;
- own `/var/run/ntp.pid`;
- set `ntp_ready`;
- run Merlin's `/sbin/ntpd_synced` callback;
- kill or replace ASUS `ntpclient`;
- change ASUS time synchronization cadence.

## Isolated executable design

Build a separate BusyBox-derived executable containing only the NTPD applet and the libbb support it requires.

Preferred installed path:

`/usr/libexec/rtac86u-ntpd`

It must not replace or symlink over `/bin/busybox`.

The build should use the latest compatible ASUS-lineage source/toolchain available for the final source build. The clean 45956 source proves behavior availability but is not automatically the final binary build base.

The isolated build is a BusyBox **single-applet** executable, so invoke it directly rather than passing an extra `ntpd` applet name:

```sh
/usr/libexec/rtac86u-ntpd -w -t -l -I "$lan_if" -p "$server0" ...
```

This also avoids creating a multicall surface or symlink that could collide with ASUS `/sbin/ntp -> rc`.

The wrapper owns a distinct pidfile such as:

`/var/run/rtac86u-ntpd.pid`.

### Why `-w`

Both clean ASUS and pinned Merlin `ntpd.c` keep the NTP server listener in the poll loop when `-w` is active.

When a peer reply is processed, `-w` explicitly skips:

`update_local_clock()`.

Thus the local daemon can track peers and answer LAN clients while leaving system clock discipline entirely to stock ASUS.

Because `-w` implies foreground mode, the lifecycle wrapper backgrounds/supervises the isolated process and records its PID.

## M29 NVRAM contract

Pinned Merlin defines:

- `ntpd_enable=0`;
- `ntpd_server_redir=0`.

There is **no** pinned 386.14_2 `ntpd_server_trust` NVRAM setting.

Any prior inventory/reference to `ntpd_server_trust` is not part of this donor contract and must not be implemented as a Merlin 386.14_2 feature.

The BusyBox command-line `-t` option is separate from NVRAM and is used internally by the daemon launch.

## M29 lifecycle wrapper

Create an idempotent add-on wrapper, e.g.:

`/usr/sbin/local-ntp-reconcile`.

### When `ntpd_enable=0`

- stop only the isolated local NTP server process;
- remove its pidfile;
- leave ASUS time synchronization untouched.

### When `ntpd_enable=1`

Validate:

- router mode is appropriate;
- `lan_ifname` is non-empty and exists;
- UDP/123 can be bound;
- upstream server strings are bounded/valid enough to pass as individual argv entries.

Then run the isolated NTP server with:

- `-w`;
- `-t`;
- `-l`;
- `-I <lan_ifname>`;
- `-p <ntp_server0>` when configured;
- optional second `-p <ntp_server1>`.

Do not use shell interpolation to construct a command string; use argv-style execution in compiled helper code or a carefully quoted shell wrapper.

### Startup timing

The server must not knowingly advertise/serve unsynchronized time during early boot.

Preferred lifecycle:

1. `services-start` launches a bounded background waiter/reconcile path;
2. wait until ASUS `ntp_ready=1`;
3. then start the local server;
4. if the timeout expires, leave the local server stopped and log the reason;
5. later relevant `service-event-end` or periodic addon reconciliation may retry.

No hook may block ASUS boot waiting indefinitely for NTP.

### Shutdown

`services-stop` stops the isolated daemon only.

## dnsmasq advertisement

Pinned Merlin's dnsmasq generator advertises the router as NTP server when `ntpd_enable=1`:

IPv4 DHCP:

```text
dhcp-option=lan,42,0.0.0.0
```

IPv6 when enabled:

```text
dhcp-option=lan,option6:31,[::]
dhcp-option=lan,option6:56,[::]
```

Instead of patching ASUS `services.c`, implement these via M04:

`/jffs/scripts/dnsmasq.postconf`

The postconf script:

- appends the options only when `ntpd_enable=1`;
- removes/avoids duplicates;
- leaves stock ASUS dnsmasq generation intact.

This explains why pinned Merlin restarts dnsmasq when `ntpd_enable` changes.

## UI integration

Reuse the current ASUS System page layout and generic NVRAM submission path.

Pinned donor UI has:

### Enable local NTP server

- key: `ntpd_enable`;
- values: `1` / `0`;
- default: `0`.

### Intercept NTP client requests

- key: `ntpd_server_redir`;
- values: `1` / `0`;
- default: `0`;
- visible only when local NTP server is enabled.

The apply path must cause:

- local server reconcile;
- dnsmasq regeneration/restart when `ntpd_enable` changes;
- firewall reconciliation/restart when redirect state changes.

Do not use a stock-unknown `restart_ntpd` service name merely because Merlin has one. Generic M02/M03 hooks should drive the add-on reconcile layer.

## M30 interception

Pinned Merlin inserts, when both options are enabled:

```text
-A PREROUTING -i <lan_if> -p udp -m udp --dport 123 -j REDIRECT --to-port 123
```

It does so in both relevant NAT-generation branches.

For this project, avoid patching ASUS `firewall.c`.

Use the M03 `firewall-start` hook to manage a dedicated NAT chain/jump.

Requirements:

1. active only when `ntpd_enable=1` and `ntpd_server_redir=1`;
2. match only the stock LAN interface scope corresponding to donor behavior;
3. UDP only, destination port 123;
4. redirect to local UDP/123;
5. idempotent creation/removal;
6. remove stale jump/chain when disabled;
7. do not modify ASUS DNS Director or other NAT chains;
8. restore automatically after every ASUS firewall rebuild.

A dedicated chain is preferred to direct repeated insertion because ownership/cleanup can be proven.

## Interaction with M28 Tor

Pinned Tor transparent-proxy rules independently redirect selected clients' UDP/123 to local port 123 to prevent time traffic from leaking outside Tor.

Therefore:

- **M28 Tor requires M29 local NTP server** for donor-equivalent leak-safe operation;
- M28 does not require global M30 interception, because Tor installs its own selected-client NTP redirect;
- M30 remains the user-selectable global interception feature.

Do not activate transparent Tor until M29 has passed its server validation gate.

## Validation gate

### Source/provenance

1. no Merlin BusyBox binary is present in the image;
2. stock ASUS `/bin/busybox` hash is unchanged;
3. stock ASUS `/sbin/ntp -> rc` behavior is unchanged;
4. isolated NTP executable is source-built and provenance-labelled;
5. isolated process name/pidfile cannot collide with ASUS `ntp`/ntpclient lifecycle.

### M29

6. `ntpd_enable=0` leaves no local UDP/123 listener;
7. `ntpd_enable=1` starts one listener bound to the LAN interface;
8. server starts only after ASUS `ntp_ready=1` or fails closed;
9. local daemon does not call `settimeofday`, `adjtimex` or otherwise discipline system time while launched with `-w`;
10. ASUS stock time sync continues updating `ntp_ready` and related services;
11. LAN clients can obtain valid NTP replies;
12. DHCP option 42 is present only when enabled;
13. IPv6 options 31/56 are present only when enabled and IPv6 DHCP config is applicable;
14. disabling removes DHCP advertisements after normal dnsmasq restart.

### M30

15. redirect off => no project-owned UDP/123 PREROUTING jump;
16. redirect on => hardcoded client NTP targets are intercepted to router UDP/123;
17. redirect survives ASUS firewall restart through `firewall-start`;
18. disabling cleans up all project-owned rules;
19. guest/secondary networks are not broadened beyond donor scope without separate proof;
20. DNS Director/VPN/NAT ordering is unaffected.

## Classification

**M29: B AFTER M01-M04 — ISOLATED AARCH64 DAEMON BUILD PROVEN, NO BUSYBOX REPLACEMENT**  
**M30: B AFTER M03 + M29 — GENERIC FIREWALL-HOOK ADAPTATION**

The remaining build requirement is producing the isolated NTPD executable from the latest compatible ASUS-lineage source/toolchain. Neither feature requires transplanting Merlin BusyBox or modifying ASUS 52334 core binaries.


## Isolated daemon build result

GitHub Actions run `36466577777` successfully built and smoke-tested the isolated candidate from the pinned clean ASUS BusyBox lineage.

Evidence:

- source anchor: ASUS 386.45956 BusyBox/ntpd;
- target: ELF64 AArch64;
- linking: static, no `PT_INTERP`;
- size: 925720 bytes;
- SHA-256 for that run: `d6ba15cf241e09cda773d511af7e7c6e6aeae0464f78cb041af4fa5de57b0e47`;
- runtime usage: `Usage: ntpd [-dnqNwtl -I IFACE] [-S PROG] [-p PEER]...`;
- source getopt surface verifies `-w/-p/-S/-t/-l/-I`;
- qemu-aarch64 root launch with `-w -l -I lo -p 192.0.2.1` remained alive until the three-second timeout;
- stock ASUS BusyBox is not involved or replaced.

The build is therefore no longer the M29 blocker. Run `36466577777` additionally proves a clean rebuild is byte-identical after normalizing the old BusyBox build-time banner; both candidate binaries hash to `6885069bb5ee26512b7f6903c08b3f28304f0b29e45bc7e810eeefe67276c6fb`. Remaining work is image integration, lifecycle gating after ASUS `ntp_ready`, dnsmasq postconf, and real-router NTP reply validation.

The artifact hash is evidence for this CI build, not yet a permanent release pin. Before shipping, make the build reproducible/pinned and rerun guarded image-size/runtime validation.
