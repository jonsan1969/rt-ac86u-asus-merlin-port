# Advanced VPN Status source integration contract

Date: 2026-09-28  
Feature inventory ID: M57  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Late donor reference: Merlin 386.12_x @ `5b47ec64ce58d23c591e809d4cbad09d1121c4ea`  
Pinned behavior donor: Merlin 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Purpose

Restore Merlin's consolidated VPN Status page without replacing ASUS 52334 HTTPD, OpenVPN, IPsec, PPTP/L2TP or VPN lifecycle code.

The feature is primarily:

- a small read-only HTTPD/sysinfo extension;
- one add-only AJAX endpoint;
- one add-only status page/menu entry;
- reuse of existing ASUS IPsec status surfaces.

## Donor stability

The following files are byte-identical between Merlin 386.12_x (late 386_51997-based tree) and Merlin 386.14_2:

- `httpd/sysinfo.c`;
- `www/ajax_vpn_status.asp`;
- `www/Advanced_VPNStatus.asp`.

Therefore the donor API is stable across the late ASUS GPL merge.

## AJAX contract

Pinned donor `ajax_vpn_status.asp` returns JavaScript globals for:

### OpenVPN status blobs

- `vpnstatus.server.1`;
- `vpnstatus.server.2`;
- `vpnstatus.client.1` through `.5`.

### Process status

- `pid.vpnserver1`;
- `pid.vpnserver2`;
- `pid.pptpd`.

### Client tunnel IPv4

- `vpnip.1` through `.5`.

### Remote/public address display

Pinned donor also reads:

- `vpn_client1_rip` through `vpn_client5_rip`.

The final port must not require status polling to mutate those NVRAM values.

## Donor sysinfo handlers

Pinned `sysinfo.c` provides three generic VPN surfaces.

### `pid.<service>`

Returns `pidof(service)`.

For the final port, do not expose an arbitrary process-name oracle beyond what the WebUI needs.

Preferred implementation:

- explicit allowlist for VPN status process names; or
- dedicated VPN pid handlers.

### `vpnstatus.<service>.<unit>`

Pinned behavior:

1. parse `service` and unit;
2. construct process name `vpn<service><unit>`;
3. if running, read:
   `/etc/openvpn/<service><unit>/status`;
4. replace newlines with `>`;
5. return the status file verbatim.

The status file is OpenVPN status-version 2 output.

Pinned donor OpenVPN config writes:

`status-version 2`

and:

`status status 5`

for both servers and clients.

The final ASUS-based implementation must first verify the current 52334-generated OpenVPN status-file path and format.

Do not change OpenVPN binary or downgrade its config generation merely to match the old path.

### `vpnip.<unit>`

Pinned behavior reads interface IPv4 through `SIOCGIFADDR` on donor `tun1N`.

However the donor handler also:

- writes `vpn_clientN_rip`;
- invokes `/usr/sbin/gettunnelip.sh` when that value is empty.

That side effect is rejected for this port.

A periodically polled status endpoint must remain read-only.

## Read-only redesign

The new M57 handler must not:

- write NVRAM;
- commit NVRAM;
- execute helper scripts;
- sleep waiting for status files;
- restart services.

### Local tunnel IP

Resolve from the later ASUS OpenVPN interface owner.

Use the actual interface name reported by current OpenVPN state/config rather than assuming `tun1N` if 52334 differs.

### Remote/public IP

Preferred sources, in order:

1. current ASUS/OpenVPN status/state API if already available;
2. parsed OpenVPN status/config runtime data;
3. existing ASUS read-only runtime key if one is authoritative.

If no safe authoritative value exists, display "N/A" rather than write NVRAM from the status request.

## No blocking wait in HTTPD

Pinned donor sleeps up to five seconds when the OpenVPN status file is missing.

Do not copy this.

The AJAX path runs every roughly two seconds and must be nonblocking.

If the process is starting and the status file is not yet present:

- return an empty status blob;
- let the next poll refresh it.

## OpenVPN status parser

Pinned page parses OpenVPN status-version 2 records including:

- `CLIENT_LIST`;
- `ROUTING_TABLE`;
- `OpenVPN STATISTICS`;
- `END`.

It displays:

- connected clients;
- real/virtual addresses;
- bytes received/sent;
- connected-since;
- routes;
- static statistics.

Keep the parser compatible with the actual 52334 OpenVPN status output.

If the later ASUS/OpenVPN version emits a changed status schema, adapt the page instead of forcing old daemon output.

## Client state/error display

Pinned page also uses OpenVPN client state/error NVRAM values to show:

- stopped;
- connecting;
- connected;
- connection error.

Earlier 52334 probing showed the expected Merlin status contract is not fully present.

The source integration should expose equivalent **read-only** client state to the page through a dedicated endpoint/sysinfo value if later ASUS uses different keys.

Do not add legacy NVRAM state solely to satisfy old page JavaScript if a cleaner read-only API can expose the current ASUS state.

## PPTP/L2TP

Pinned page displays:

- PPTP server process state;
- connected PPTP clients from existing status text;
- PPTP/L2TP client list when supported.

Only enable those blocks if the corresponding ASUS 52334 backend still exists.

No obsolete VPN daemon should be added just to fill a status table.

## IPsec

ASUS 52334 already retains an IPsec AJAX/status backend.

Reuse that stock endpoint and current state.

Do not port Merlin IPsec backend code.

M57 only consolidates presentation.

## Maximum OpenVPN client units

Pinned page shows:

- two clients on AC68U/DSL-AC68U;
- up to five on other supported models.

For RT-AC86U, use the number of client instances actually supported by ASUS 52334 source/runtime.

Do not hardcode five if the final target exposes fewer.

## Security

All M57 endpoints are authenticated read-only status surfaces.

Requirements:

- validate service type against an allowlist;
- validate unit bounds;
- fixed/constructed paths only;
- no arbitrary file read;
- no arbitrary `pidof` target from request data;
- bound status-file size;
- escape/encode content appropriately for JavaScript output;
- never return credentials, keys or OpenVPN config secrets.

## UI integration

After backend support is present:

- add/adapt `Advanced_VPNStatus.asp`;
- add `ajax_vpn_status.asp`;
- preserve current ASUS VPN menu architecture;
- reuse stock ASUS IPsec status endpoint;
- hide unsupported protocol sections.

Do not replace ASUS 52334 OpenVPN client/server configuration pages.

## Relationship to M24/M25/M38/M40

M57 is read-only.

It may display state from:

- stock ASUS OpenVPN;
- M25/M40 VPN Director routing;
- M38 DNS Exclusive.

It must not become the owner of those features.

## Validation gate

Before M57 becomes **SUCCESS**, prove:

1. page loads under normal ASUS authentication;
2. polling endpoint performs no writes;
3. missing status file returns immediately;
4. stopped OpenVPN client/server renders stopped cleanly;
5. connecting state renders without HTTPD blocking;
6. connected client displays correct tunnel IP;
7. connected server displays OpenVPN client rows/routes/stats;
8. status parser matches actual 52334 OpenVPN status format;
9. unsupported client units are hidden;
10. IPsec section uses stock ASUS backend unchanged;
11. PPTP/L2TP sections appear only when supported;
12. repeated polling has negligible CPU/memory impact;
13. no secrets from OpenVPN config/key files are exposed;
14. no ASUS OpenVPN/HTTPD binary is transplanted.

## Current classification

**C small read-only backend + A UI after backend**

The donor status API is stable across 386.12 and 386.14_2, but the final implementation deliberately removes donor polling side effects and blocking waits.
