# Tools / Other Settings adaptation plan

Date: 2026-09-26  
Feature inventory IDs: M31, M44, M47 and adjacent controls  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Merlin donor: 386.14_2 @ 6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b

## Runtime-first decision

Do not transplant Merlin's full `Tools_OtherSettings.asp`.

The donor page is an umbrella over several independent Merlin features. ASUS 52334 only exposes a subset of the donor backend contract, so the port must be split by verified backend capability.

## Verified ASUS 52334 overlap

Targeted runtime probe:

- `ct_tcp_timeout`: exact NVRAM/backend string present in stock `/sbin/rc`;
- `ct_udp_timeout`: exact NVRAM/backend string present in stock `/sbin/rc`;
- `rstats_path`: exact stock `/sbin/rc` string present;
- `rstats_new`: exact stock `/sbin/rc` string present;
- stock `/bin/rstats` exists;
- stock `/usr/sbin/cru` exists;
- `shell_timeout`: stock HTTPD string present;
- reboot scheduling keys are present in stock RC/HTTPD.

The same probe did **not** establish exact runtime support for:

- `ct_max`;
- `rstats_offset`;
- `rstats_stime`;
- cstats controls;
- `dns_local_cache`;
- `ntpd_enable`;
- `ntpd_server_redir`.

Those controls must not be exposed merely because Merlin's page contains them.

## Conntrack phase 1

The staged adapter at `ports/candidates/Tools_OtherSettings.asp` intentionally exposes only the verified timeout vectors:

- the eight TCP state timeout values encoded in `ct_tcp_timeout`;
- UDP unreplied/assured values encoded in `ct_udp_timeout`.

It preserves Merlin's value ranges and vector encoding but does not expose `ct_max`.

ASUS source provenance changes the apply strategy. The timeout backend itself is ASUS-origin: `ct_tcp_timeout`, `ct_udp_timeout` and `setup_conntrack()` are already present in the clean RT-AC86U ASUS GPL 382_15098 initial import, where `init.c` invokes `setup_conntrack()` during boot. By contrast, the `strcmp(script, "conntrack")` service-dispatch block is not present in that clean ASUS-origin point and enters the available history through the older Merlin merge lineage.

Therefore phase 1 must **not** rely on `action_script=restart_conntrack`. The staged adapter saves only the verified ASUS NVRAM vectors and requests a normal stock reboot, allowing the ASUS boot path to apply them through `setup_conntrack()`. Immediate conntrack reload remains deferred unless the 52334 runtime dispatcher is independently proven.

The earlier plain `strings -Fx conntrack` negative was also shown to be unsuitable as a discriminator: the verified Merlin 386.14_2 runtime itself lacks an exact standalone `conntrack` string even though its WebUI uses `restart_conntrack`.

## Traffic-history follow-up

M47 remains a separate adaptation step. Presence of `rstats_path`, `rstats_new`, and `/bin/rstats` is promising, but the Merlin scheduling/location controls must not be enabled until their exact stock service and persistence semantics are mapped.

## Safety rule

ASUS 52334 `rc`, `httpd`, kernel, dnsmasq and other core binaries remain unchanged. This block is UI/static adaptation only unless a later source-compatible implementation is explicitly proven.
