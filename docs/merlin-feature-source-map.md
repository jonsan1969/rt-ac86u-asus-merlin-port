# Merlin 386.14_2 feature source map

Pinned donor: `RMerl/asuswrt-merlin.ng` tag `386.14_2`  
Pinned commit: `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

This is the reduced source-level map used for port planning. It deliberately excludes broad third-party grep noise.

## 1. JFFS custom scripts

Core implementation:

- `release/src/router/shared/scripts.c`
  - `run_custom_script()` builds `/jffs/scripts/<name>`
  - checks `jffs2_scripts`
  - validates/execut es script hooks
  - `run_postconf()`
  - custom-config helpers such as `use_custom_config()` and `append_custom_config()`
- `release/src/router/shared/shared.h` — declarations
- `release/src/router/shared/defaults.c` — `jffs2_scripts` default
- `release/src/router/rc/jffs2.c`, `release/src/router/rc/ubifs.c` — create `/jffs/scripts/`

Important hook call sites:

- `rc/init.c` — `init-start`
- `rc/firewall.c` — `firewall-start`
- `rc/services.c` — `ddns-start`, `services-start`, `services-stop`, `service-event`, `service-event-end`, `nat-start`
- `rc/qos.c`, `rc/qos_multiwan.c` — `qos-start`
- `rc/udhcpc.c` — DHCP/ZCIP event hooks
- `rc/usb.c` — `pre-mount`, `post-mount`, `unmount`
- `rc/wan.c` — `wan-event`, `wan-start`
- `rc/watchdog.c` — `update-notification`

The service-event implementation is explicit in `rc/services.c`:

- `run_custom_script("service-event", ...)`
- `run_custom_script("service-event-end", ...)`

**Port category:** C for the `rc` call sites, plus a small shared helper delta. Do not transplant Merlin `rc`.

## 2. postconf and custom config

Core helper: `release/src/router/shared/scripts.c`.

Known service integrations include:

- `rc/init.c` — fstab
- `rc/services.c` — passwd/group/shadow/gshadow, hosts, dnsmasq, stubby, inadyn, mcpd, UPnP, Avahi, AFP, Tor and others
- `rc/rc_ipsec.c` — strongSwan/IPsec
- `rc/snmpd.c`
- `rc/usb.c` — vsftpd, media server, NFS exports
- `rc/vpn.c` — PPTP
- `rc/wan.c` — igmpproxy
- `rc/qos.c`, `rc/qos_multiwan.c` — cake-qos config

**Port category:** shared helper + selective source-level call-site patches. Later ASUS config generation must remain authoritative.

## 3. VPN Director

This is not just `Advanced_VPNDirector.asp`.

Persistent policy handling:

- `release/src/router/libovpn/openvpn_config.c`
  - `ovpn_get_policy_rules()`
  - `ovpn_set_policy_rules()`
  - stores policy rules under `OVPN_FS_PATH/vpndirector_rulelist`

Routing implementation:

- `release/src/router/libovpn/openvpn_control.c`
  - `ovpn_set_routing_rules()`
  - `_write_routing_rules()`
  - allocates policy-routing priorities
  - creates `ip rule` entries for WAN and `ovpncN` tables
  - integrates VPN Director rules with exclusive OpenVPN DNS routing
  - kill-switch handling remains tied to OpenVPN routing state

Web/NVRAM integration:

- `release/src/router/httpd/web.c`
  - special read handling for `vpndirector_rulelist` through `ovpn_get_policy_rules()`
  - special write handling through `ovpn_set_policy_rules()`
- `release/src/router/shared/defaults.c`
- `release/src/router/www/Advanced_VPNDirector.asp`
- `release/src/router/www/Advanced_OpenVPNClient_Content.asp`
- menu-tree/start-apply integration

**Port category:** B/C. The page is a pure addition, but the feature depends on libovpn and httpd integration. The ASUS 52334 OpenVPN implementation must be compared before applying these deltas.

## 4. DNS Director

The Merlin-generation feature is implemented internally as DNSFilter/DNS Director.

Core:

- `release/src/router/rc/dnsfilter.c`
- `release/src/router/rc/dnsfilter.h`
- `release/src/router/rc/Makefile` adds `dnsfilter.o`
- `release/src/router/rc/rc.h` declarations

Integration points:

- `release/src/router/rc/firewall.c`
  - IPv4/IPv6 DNS interception
  - DNS-over-TLS blocking/allow rules
- `release/src/router/rc/services.c`
  - dnsmasq integration
  - restart/service handling
- `release/src/router/rc/init.c`
  - exposes `dnsfilter` capability
- `release/src/router/httpd/web.c`
  - `dnsfilter_modes_list`
- `release/src/router/shared/defaults.c`
  - `dnsfilter_enable_x`
  - `dnsfilter_mode`
  - `dnsfilter_rulelist`
  - custom IPv4/IPv6 resolver NVRAM values
- `release/src/router/www/DNSDirector.asp`
- supporting menu/state/client JavaScript

**Port category:** C around firewall/services/httpd, with `rc/dnsfilter.c` itself a candidate B-style source addition. This must be adapted to ASUS 52334 firewall and dnsmasq code rather than copying Merlin binaries.

## 5. Custom WebUI user pages

Firmware image provides 20 public mount points:

- `/www/user1.asp` … `/www/user20.asp`

In the stock Merlin image these are symlinks to `/dev/null` until an addon claims a slot.

Build integration is in:

- `release/src/router/www/Makefile` — installs the twenty user-page mount points

Addon helper API:

- `release/src/router/others/helper.sh`
  - `am_get_webui_page()`
  - scans `/www/user/user1.asp` … `user20.asp`
  - returns the first free page or the existing page matching an addon

**Port category:** A plus WebUI/addon plumbing. The writable runtime `/www/user` behavior must be confirmed against the ASUS 52334 boot/runtime setup before implementation.

## 6. AMTM/addon integration

- `release/src/router/others/amtm` — integrated AMTM launcher
- `release/src/router/others/Makefile` — installs it as `/usr/sbin/amtm`
- AMTM enables `jffs2_scripts` when required
- AMTM migrates old `/jffs/scripts/amtm` and `/opt/bin/amtm` launchers
- `release/src/router/others/helper.sh` supplies postconf and addon helper functions

**Port category:** mostly A, but depends on the JFFS/custom-script framework being restored correctly first.

## 7. SSH/Dropbear

Main integration:

- `release/src/router/rc/ssh.c`
  - key generation/storage
  - `/root/.ssh/authorized_keys`
  - Dropbear command-line options
- `release/src/router/rc/format.c`
  - persists host keys in `/jffs/.ssh/`
- `release/src/router/rc/services.c`
  - service control
- `release/src/router/Makefile`
  - Dropbear build/install

**Port category:** B/C. Compare the ASUS 52334 Dropbear version/config first; restore only Merlin behavior that is still safe and needed.

## Port order implied by the source map

1. Establish the latest buildable ASUS AC86U 386 source baseline available to us.
2. Port the shared JFFS/custom-script primitives.
3. Port individual `rc` hook call sites.
4. Restore postconf/custom config call sites.
5. Port custom WebUI/addon plumbing and AMTM.
6. Port DNS Director against ASUS firewall/dnsmasq.
7. Port VPN Director against ASUS libovpn/httpd/OpenVPN.
8. Reconcile SSH behavior against ASUS 52334.
9. Only then add remaining Merlin WebUI pages/features.

No step above authorizes replacing a newer ASUS core binary with the Merlin binary.
