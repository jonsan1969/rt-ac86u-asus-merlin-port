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

Activation is gated on a runtime-level proof that the ASUS 52334 service dispatcher accepts the `conntrack` service token used by Merlin's `action_script=restart_conntrack`.

A plain `strings -Fx conntrack` test is insufficient because link-time suffix/string pooling can hide standalone service tokens. The project therefore compares the stock runtime against the verified Merlin runtime, where the same WebUI action contract is known to be used.

## Traffic-history follow-up

M47 remains a separate adaptation step. Presence of `rstats_path`, `rstats_new`, and `/bin/rstats` is promising, but the Merlin scheduling/location controls must not be enabled until their exact stock service and persistence semantics are mapped.

## Safety rule

ASUS 52334 `rc`, `httpd`, kernel, dnsmasq and other core binaries remain unchanged. This block is UI/static adaptation only unless a later source-compatible implementation is explicitly proven.
