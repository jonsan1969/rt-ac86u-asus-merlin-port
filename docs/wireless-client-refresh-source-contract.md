# Wireless client auto-refresh source integration contract

Date: 2026-09-28  
Feature inventory ID: M52  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Merlin donor: 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Purpose

Restore Merlin's structured, automatically refreshing Wireless Log client list without replacing ASUS 52334 wireless drivers, `rc`, HTTPD, dnsmasq or Broadcom libraries.

The feature is a small read-only HTTPD data handler plus a WebUI/AJAX adaptation.

## Donor data path

Pinned Merlin registers the EJ function:

`get_wl_status -> ej_wl_status_array`

for BCMWL6 builds.

The implementation lives in:

`release/src/router/httpd/sysdeps/web-broadcom-am.c`.

The initial Wireless Log page invokes:

`<% get_wl_status(); %>`

and the refresh endpoint:

`/ajax_wificlients.asp`

invokes the same handler again.

No service restart or NVRAM write is required.

## HTTPD handler contract

`ej_wl_status_array()` iterates available wireless units and delegates each active unit to the unit-status collector.

The donor emits JavaScript arrays per unit:

- `dataarray0..3` for radio/BSS status;
- `wificlients0..3` for authenticated stations;
- DFS status arrays where supported.

RT-AC86U needs only its actual radios; do not retain four-radio special cases that are irrelevant to this model.

### Radio/BSS data

The donor reads Broadcom wireless state through the existing ASUS/Broadcom ioctl APIs.

Fields include donor-equivalent data such as:

- SSID;
- RSSI;
- SNR when available;
- noise;
- chanspec/channel;
- BSSID;
- operating mode.

If the radio is disabled, the handler emits no active radio array for that unit and the page shows the disabled state.

### Client data

For each authenticated station the donor combines:

- station MAC from Broadcom authenticated station list;
- current station info from the wireless driver;
- IPv4 from ARP and/or dnsmasq leases;
- hostname from dnsmasq leases;
- IPv6 client information when enabled;
- RX/TX rate and station timing/details from Broadcom station info.

The final ASUS 52334 port must use the later ASUS/Broadcom structs and APIs from the target source tree. Do not transplant old driver headers or ioctl ABI definitions from Merlin.

## Refresh endpoint

Pinned donor `ajax_wificlients.asp` contains:

```
<% get_wl_status(); %>;

var nvram_dump_String = function(){/*
<% nvram_dump("wlan11b_2g.log",""); %>
*/}.toString().slice(14,-3);
```

The structured `get_wl_status()` data is the essential M52 backend.

The legacy wireless log text dump may be retained only if the current ASUS page still needs it for the low-level detail view. Do not add a redundant dump if ASUS 52334 already provides an equivalent endpoint.

## Auto-refresh behavior

Pinned page supports refresh intervals:

- disabled;
- 1 second;
- 3 seconds;
- 5 seconds;
- 10 seconds.

Default donor behavior is 3 seconds.

The selected value is stored client-side in cookie:

`awrtm_wlrefresh`

and does not need NVRAM.

The page:

1. cancels the previous timer;
2. GETs `/ajax_wificlients.asp` as script;
3. redraws the existing DOM from returned arrays;
4. schedules the next refresh only when refresh is enabled.

## Error behavior improvement

Pinned donor immediately calls `get_wlclient_list()` again in the AJAX error callback, which can create a tight retry loop during HTTPD/wireless failure.

The new adaptation should improve this:

- retry with a bounded delay;
- never spin continuously on failed requests;
- stop scheduling when the page is unloaded/hidden if practical;
- keep only one in-flight request/timer.

This is a safe adaptation, not behavior we need to reproduce byte-for-byte.

## Source patch boundary

Expected source work:

1. add/reconcile `ej_wl_status_array()` and only the RT-AC86U-compatible helper path in current ASUS HTTPD;
2. register a read-only `get_wl_status` EJ name;
3. add `ajax_wificlients.asp`;
4. exact/adapt the stock `Main_WStatus_Content.asp` to use structured redraw + refresh selector.

Do not replace:

- Broadcom wireless driver;
- `wl` utility;
- ASUS wireless `rc` logic;
- dnsmasq;
- networkmap;
- full HTTPD binary with donor binary.

## Interaction with M53

M53 already patches the stock Wireless Log page to disable auto logout.

When M52 later patches the same page:

- use the current M53-patched page as the expected preimage or compose both changes into one exact multi-patch;
- preserve `AUTOLOGOUT_MAX_MINUTE = 0`;
- update `ports/active.json` result hash accordingly.

Do not create two conflicting independent replacements of the same page.

## Interaction with client names

M51 was correctly classified NO PORT because ASUS already has a newer wireless ACL/client-name equivalent.

M52 may still display hostnames from current ASUS DHCP/client sources for the log table, but it must not reintroduce the obsolete M51 UI/backend.

## Security/performance boundary

The handler is read-only.

Requirements:

- fixed wireless unit bounds;
- bounded station count;
- escaped SSID/hostname strings before emitting JavaScript;
- no user-supplied file path;
- no shell commands;
- free ARP/lease/client buffers on all paths;
- no wireless state changes;
- polling cadence must be viable on RT-AC86U.

## Validation gate

Before M52 becomes **SUCCESS**, prove:

1. page initial load reports both AC86U radios correctly;
2. disabled radio is represented correctly;
3. connecting client appears without full-page reload;
4. disconnecting client disappears;
5. MAC, IPv4 and hostname match ASUS client state;
6. IPv6 address handling is correct when IPv6 is enabled;
7. rates/status update across polls;
8. 0/1/3/5/10-second selector works;
9. refresh choice persists client-side as intended;
10. repeated AJAX errors do not create a tight retry loop;
11. no duplicate timer/request buildup occurs;
12. M53 no-auto-logout behavior remains present;
13. CPU impact at 1-second polling remains acceptable;
14. HTTPD memory remains stable under long polling sessions;
15. ASUS wireless driver and core runtime remain unchanged.

## Current classification

**C small read-only HTTPD backend + A page/AJAX adaptation**

The missing backend is narrow; the rest is image-safe once the handler is built.
