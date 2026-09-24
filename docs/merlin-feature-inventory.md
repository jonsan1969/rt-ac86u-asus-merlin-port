# RT-AC86U Merlin 386.14_2 feature inventory

Date: 2026-09-24

## Scope

This is the feature-level master inventory for restoring Asuswrt-Merlin functionality to the ASUS RT-AC86U `3.0.0.4.386_52334` baseline.

Donor:

- Asuswrt-Merlin `386.14_2`
- source commit `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

Comparison references:

- ASUS `386_51955` — near-Merlin temporal reference
- ASUS `386_52334` — final hardware/security baseline

The inventory combines:

1. the feature list in Merlin's own `README-merlin.txt`;
2. feature-bearing NEW/CHANGED entries in `Changelog-386.txt`;
3. verified three-way firmware-tree analysis;
4. the pinned Merlin source map;
5. targeted runtime compatibility probes.

Broad bugfixes, component version bumps and security backports are tracked separately from user-facing functionality.

## Decision labels

- **PORT** — genuine Merlin functionality is absent from ASUS 52334.
- **ADAPT** — ASUS 52334 already has a backend/equivalent primitive; graft only missing Merlin UI/behavior.
- **REVIEW** — both sides implement related functionality and the exact behavioral delta must be isolated before deciding.
- **NO PORT** — the functionality is already present or later ASUS implementation should remain authoritative.
- **N/A** — feature is not applicable to the RT-AC86U Merlin 386.14_2 runtime.

## Port classes

- **A** — pure addition.
- **B** — Merlin-patched/open-source component.
- **C** — shared ASUS/Merlin core integration; source-level patch only.
- **D** — proprietary/model/hardware-sensitive; keep ASUS unless explicitly proven otherwise.

---

## 1. Extensibility, JFFS and addons

| ID | Function | ASUS 52334 state | Decision | Class | Port notes |
|---|---|---|---|---|---|
| M01 | JFFS user scripts under `/jffs/scripts/` | direct Merlin signature absent | **PORT** | C | restore shared script helper and individual event call sites |
| M02 | `service-event` / `service-event-end` hooks | absent | **PORT** | C | source-level `rc/services.c` integration |
| M03 | Event hooks: init/firewall/services/NAT/WAN/QoS/DDNS/USB/DHCP/update | most Merlin hook signatures absent | **PORT** | C | add only hook calls, never Merlin `rc` binary |
| M04 | postconf/custom config framework | postconf signature absent | **PORT** | B/C | `run_postconf()`, `.add`, custom configs; preserve ASUS generators |
| M05 | Addon helper API | `helper.sh` absent | **PORT** | A | includes postconf helpers |
| M06 | Addon custom-settings API | absent | **PORT** | A | `/jffs/addons/custom_settings.txt`, `am_settings_get/set` |
| M07 | 20 custom WebUI slots | absent | **PORT** | A/C | `user1.asp` … `user20.asp`, mount/allocation plumbing |
| M08 | AMTM management interface | absent | **PORT** | A/C | depends on working JFFS/addon framework |
| M09 | Entware/addon friendliness | no integrated Merlin setup path | **PORT** | A/C | `/opt` exists but Merlin integration/setup behavior must be restored |
| M10 | JFFS backup/restore/upload WebUI | `UploadingJFFS.asp` absent | **PORT** | A/C | verify backend handlers before adding page |
| M11 | Custom DDNS user-script callback | `ddns_custom_updated` absent | **PORT** | A/C | restore custom provider/script integration |
| M12 | Scheduled jobs / `cru` | ASUS already has `/usr/sbin/cru`; implementation differs | **REVIEW** | B/C | preserve stock primitive; evaluate Merlin collision/race fixes; `crontab` utility is Merlin-only |

## 2. Shell, SSH and administration

| ID | Function | ASUS 52334 state | Decision | Class | Port notes |
|---|---|---|---|---|---|
| M13 | Nano editor | absent | **PORT** | A/B | Merlin image includes `nano` and `rnano` |
| M14 | Enhanced CLI utility set | many tools absent | **PORT** | A/B | includes `scp`, `crontab`, `diff`, `dos2unix`, `unix2dos`, `hexdump`, `xargs`, `getopt`, `hostname`, `tee`, `uniq` and others |
| M15 | SSH public-key authentication | already present | **NO PORT** | C | ASUS `rc` already contains `authorized_keys` support |
| M16 | Merlin SSH behavior/key persistence | partially overlaps | **ADAPT** | B/C | compare `rc/ssh.c`, JFFS host-key persistence/fallback, Dropbear options and SCP |
| M17 | SNMP | not present in verified AC86U Merlin image | **N/A** | — | Merlin README says only some models; do not invent support |

## 3. SMB, disk sharing and filesystem services

| ID | Function | ASUS 52334 state | Decision | Class | Port notes |
|---|---|---|---|---|---|
| M18 | Simpler SMB share naming | UI and backend signatures absent | **PORT** | C | `smbd_simpler_naming` in Samba UI + config generator |
| M19 | Force SMB Master Browser | UI and backend signatures absent | **PORT** | C | `smbd_master` |
| M20 | WINS server | UI and backend signatures absent | **PORT** | C | `smbd_wins` |
| M21 | Windows discovery via `wsdd2` | runtime binary absent | **PORT** | A/B | integrate only if compatible with ASUS Samba stack |
| M22 | NFS exports for USB storage | NFS page/daemon/modules absent | **PORT** | A/B/C | `nfsd`, `mountd`, `exportfs`, sunrpc/NFS modules + WebUI/config |
| M23 | CIFS client support | mount points exist but CIFS kernel module absent | **PORT** | B/C | add source-compatible CIFS client support; no blind module transplant |

## 4. VPN, DNS and routing

| ID | Function | ASUS 52334 state | Decision | Class | Port notes |
|---|---|---|---|---|---|
| M24 | Advanced OpenVPN client/server integration | stock OpenVPN exists; Merlin advanced page absent | **ADAPT** | A/B/C | reconcile against later ASUS OpenVPN/security implementation |
| M25 | VPN Director | page and `vpndirector_rulelist` backend absent | **PORT** | A/B/C | JFFS-backed rules, RPDB routing, kill-switch/DNS interaction |
| M26 | DNS Director | ASUS has DNSFilter backend; Merlin page absent | **ADAPT** | A/C | retain ASUS backend, adapt Merlin UI/schema; verify IPv4/IPv6/custom providers |
| M27 | ipset kernel/userspace support | absent | **PORT** | A/B | modules + `libipset` + userspace `ipset` |
| M28 | TOR with per-client access control | daemon/page absent | **PORT** | A/B/C | restore only current safe integration |
| M29 | Local NTP daemon | `ntpd_enable` and Merlin daemon absent | **PORT** | A/B/C | local LAN NTP server |
| M30 | Redirect client NTP queries to router | `ntpd_server_redir` absent | **PORT** | C | firewall UDP/123 redirect tied to NTP daemon |
| M31 | TCP/UDP conntrack timeout tuning | backend keys already present; Merlin UI absent | **ADAPT** | A/C | reuse ASUS backend and add compatible controls |
| M32 | Cake SQM QoS | cake module absent | **PORT** | B/C | requires kernel/source compatibility; hardware acceleration implications |
| M33 | WireGuard kernel module/userspace tool | Merlin has `wireguard.ko` + `wg`; ASUS image lacks same runtime components but contains generic WG pages/libvpn | **REVIEW** | B/C/D | determine ASUS 52334 WireGuard capability path before any kernel/tool port |
| M34 | Wireless Site Survey | page absent | **PORT** | A/C | AC86U-specific supported feature since Merlin 386.10 |
| M35 | Detailed WiFi troubleshooting / WiFi Insight | AC86U-specific page absent | **PORT** | A/C | `WiFi_Insight.asp` has RT-AC86U-specific source |
| M36 | IPv6-aware DNS Director | ASUS backend overlap exists | **ADAPT** | C | preserve Merlin IPv6/custom resolver behavior only where missing |
| M37 | IPv6 OpenVPN server + optional IPv6 NAT | stock support must be verified | **REVIEW** | B/C | part of advanced OpenVPN block |
| M38 | OpenVPN DNS Exclusive behavior | shared OpenVPN/dnsmasq stack differs | **REVIEW** | B/C | preserve later ASUS security; port behavior only if missing |
| M39 | OpenVPN custom options stored in JFFS / expanded storage | Merlin behavior; stock equivalence unverified | **PORT/REVIEW** | B/C | source-level comparison required |
| M40 | Multiple OpenVPN client routes and Merlin routing semantics | stock equivalence unverified | **REVIEW** | B/C | part of VPN Director/OpenVPN route-control pass |
| M41 | `dhcpc-event` IPv4/IPv6 protocol argument | Merlin hook API extension | **PORT** | C | restore with user-script framework if absent |
| M42 | QoS `qos-start init` blocking hook semantics | stock user-hook absent | **PORT** | C | preserve ordering guarantee for addon QoS changes |

## 5. WebUI, monitoring and diagnostics

| ID | Function | ASUS 52334 state | Decision | Class | Port notes |
|---|---|---|---|---|---|
| M43 | System Info summary page | absent | **PORT** | A/C | `Tools_Sysinfo.asp` + httpd/sysinfo handlers |
| M44 | Other Settings page | absent | **PORT/ADAPT** | A/C | umbrella page for traffic storage, conntrack and other controls |
| M45 | Temperature/performance page | absent | **PORT** | A/C | AC86U temperature display from `Advanced_PerformanceTuning_Content.asp` |
| M46 | QoS Stats page | absent | **PORT** | A/C | preserve compatible ASUS QoS backend |
| M47 | Save traffic history to USB/JFFS/NVRAM | `rstats_path` backend signature exists; Merlin UI absent | **ADAPT** | A/B/C | compare rstats semantics, then restore location/schedule controls |
| M48 | Enhanced/per-IP traffic monitoring | only partial stock overlap | **PORT/ADAPT** | A/B/C | monthly page is Merlin-only; existing traffic pages are divergent |
| M49 | Monthly traffic history page | absent | **PORT** | A/C | `Main_TrafficMonitor_monthly.asp` |
| M50 | DHCP reservation hostname field | already present in ASUS page | **NO PORT** | — | stock page contains `dhcp_hostname_x_0`; compare only semantics |
| M51 | Wireless ACL/client-name display enhancement | shared page is divergent | **REVIEW** | C | manual page-level comparison |
| M52 | Auto-refreshing advanced wireless client list | Merlin signatures absent from ASUS | **PORT** | A/C | `ajax_wificlients.asp`, refresh preference |
| M53 | System Log / Wireless Log no-auto-logout behavior | shared pages differ | **PORT/REVIEW** | C | Merlin explicitly disables auto logout on these log pages |
| M54 | System Log layout/filter/log-level enhancements | shared pages differ | **REVIEW** | C | port only demonstrably missing useful UI behavior |
| M55 | WiFi icon reports both radios | shared UI; exact stock behavior unverified | **REVIEW** | C | small visual/behavioral delta |
| M56 | Editable-entry WebUI enhancements | cross-cutting page differences | **REVIEW** | C | not a single transplantable file |
| M57 | Advanced VPN status page | absent | **PORT** | A/C | `Advanced_VPNStatus.asp` + backend status handlers |
| M58 | QR codes for network/Guest Network | Merlin `qrcode.min.js` present; no same runtime asset in ASUS | **PORT/REVIEW** | A/C | verify ASUS has no alternative implementation before adding |
| M59 | Local OUI database for WebUI/networkmap | Merlin `ajax/ouiDB.json` is runtime-only | **PORT/REVIEW** | A/C | enables local vendor lookup without remote query |
| M60 | JFFS upload/restore page | absent | **PORT** | A/C | also listed under addon/JFFS block for dependency ordering |

## 6. QoS and networking refinements from the 386 changelog

These are feature-bearing behavior changes rather than standalone pages.

| ID | Function | Decision | Notes |
|---|---|---|---|
| M61 | QoS Classification resolves local IPv6 addresses | **REVIEW** | compare divergent QoS pages/backend |
| M62 | Show tracked connections even without Adaptive QoS | **REVIEW** | user-visible diagnostics enhancement |
| M63 | Basic IPv6 support for Traditional QoS | **REVIEW** | preserve only if ASUS 52334 lacks equivalent |
| M64 | Traditional QoS overhead accuracy/download statistics improvements | **REVIEW** | do not replace later ASUS QoS code wholesale |
| M65 | IPv6 DDNS support | **REVIEW** | compare current ASUS DDNS behavior first |
| M66 | Prevent Auto DoH also handles DDR / Private Relay interactions | **REVIEW** | security-sensitive behavior; ASUS 52334 wins unless missing and safely portable |
| M67 | OpenVPN client selection for Ookla Speedtest | **REVIEW** | minor integration; verify AC86U page/backend in final donor |
| M68 | Outbound LAN connection logging when allowed-connection logging is enabled | **REVIEW** | firewall/logging behavior |
| M69 | Local QR/OUI and WebUI diagnostics additions | **PORT/REVIEW** | grouped supporting WebUI assets |

## 7. Items deliberately not treated as Merlin feature ports

The following may differ between Merlin and ASUS but are **not** copied merely because Merlin has a different version:

- OpenSSL version/build and security backports
- OpenVPN binary version
- dnsmasq binary/version
- Dropbear binary/version
- BusyBox binary/version
- curl/wget/miniupnpd/strongSwan/Tor package revisions
- CA bundle version
- ASUS AiCloud/WebDAV fixes
- kernel/HND/Broadcom SDK modules and proprietary binaries
- Trend Micro components
- entropy-daemon choice (`haveged` in Merlin vs later ASUS `jitterentropy-rngd`)
- generic ASUS GPL files that happen to appear Merlin-only because the two firmware generations package different common assets

For all of these, ASUS 52334 remains authoritative unless an exact missing behavior is proven and ported at source level.

## 8. Removed/deprecated functionality

Merlin 386.14 removed WiFi Radar due to support/security concerns. It is **not** a feature to restore merely because older Merlin versions had it.

Any other feature removed for security reasons follows the same rule.

## 9. Feature-discovery conclusion

At feature level, the RT-AC86U Merlin 386.14_2 donor is now inventoried from:

- Merlin's official feature list;
- the 386-series feature changelog;
- verified runtime additions;
- source mapping;
- ASUS 51955/Merlin/ASUS 52334 three-way provenance;
- targeted ASUS-52334 compatibility probes.

This allows **feature discovery** to be marked **SUCCESS**.

What remains **IN PROGRESS** is implementation classification: reducing every required PORT/ADAPT/REVIEW item to exact source patches against the best buildable ASUS-side source generation.

The next implementation-analysis order is:

1. M01–M07: JFFS/custom-script/addon framework.
2. M04/M18–M21: custom config + SMB extensions.
3. M29–M31/M47–M49: NTP, conntrack and traffic-monitor adaptations.
4. M26: DNS Director on ASUS backend.
5. M24–M25/M37–M40: Advanced OpenVPN + VPN Director.
6. M22–M23/M27–M35: optional kernel/userland feature blocks.
7. WebUI/diagnostic refinements.
