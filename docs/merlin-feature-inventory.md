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
| M05 | Addon helper API | stock helper absent; pinned Merlin `helper.sh` is now add-only in guarded overlay | **PORT** | A | image-safe foundation implemented; includes postconf helpers |
| M06 | Addon custom-settings API | stock API absent; active pinned `helper.sh` already provides `am_settings_get/set` and `/jffs/addons/custom_settings.txt` | **PORT** | A | image-safe implementation already delivered as part of JFFS helper foundation |
| M07 | 20 custom WebUI slots | stock aliases absent; 20 add-only `/www/userN.asp -> user/userN.asp` aliases are active | **PORT** | A/C | image-safe alias layer implemented; deeper addon/event behavior still follows JFFS source-hook dependency |
| M08 | AMTM management interface | absent; donor `usr/sbin/amtm` is a standalone shell script (run 36382931979) | **PORT** | A/C | do not expose yet: AMTM-managed addons depend on JFFS lifecycle hooks ASUS `rc` lacks; revisit after M01–M03 source integration |
| M09 | Entware/addon friendliness | both images have `/opt -> tmp/opt`, but ASUS lacks Merlin `services-start`/`post-mount` rc hooks | **PORT** | A/C | dependency-blocked by JFFS event-hook integration; avoid a partial addon environment |
| M10 | JFFS backup/restore/upload WebUI | stock settings-backup page exists, but JFFS-specific upload/backup handlers are absent from ASUS 52334 | **PORT** | C | source-side HTTPD/uploader integration required; do not expose dead UI |
| M11 | Custom DDNS user-script callback | ASUS 52334 lacks `WWW.CUSTOM`, `ddns-start` and `ddns_custom_updated` | **PORT** | C | source-side DDNS + JFFS hook integration required; stock DDNS path remains authoritative |
| M12 | Scheduled jobs / `cru` | ASUS has a functional native `cru`; Merlin's material delta is fd-based `flock` locking | **NO PORT** | B | keep ASUS `cru`/crond/BusyBox. QEMU cannot execute this ASUS BusyBox reliably enough to prove the fd-278 delta (run 36383042773), so no unproven lock patch is justified |

## 2. Shell, SSH and administration

| ID | Function | ASUS 52334 state | Decision | Class | Port notes |
|---|---|---|---|---|---|
| M13 | Nano editor | absent | **PORT** | A/B | Merlin image includes `nano` and `rnano` |
| M14 | Enhanced CLI utility set | run 36382597888 found no Merlin-only BusyBox symlink command absent from ASUS; remaining standalone donor ELFs belong to separately tracked feature blocks | **NO PORT** | A/B | no generic CLI transplant. M13 Nano is the isolated proven exception; BusyBox remains ASUS-authoritative |
| M15 | SSH public-key authentication | already present | **NO PORT** | C | ASUS `rc` already contains `authorized_keys` support |
| M16 | Merlin SSH behavior/key persistence | basic key/NVRAM/host-key signatures overlap; ASUS lacks `scp`, while Merlin `scp` resolves to Merlin `dropbearmulti` | **ADAPT** | B/C | run 36382880359: never add the symlink against ASUS Dropbear or transplant donor Dropbear; remaining SCP/behavior delta needs ASUS-compatible source/build work |
| M17 | SNMP | not present in verified AC86U Merlin image | **N/A** | — | Merlin README says only some models; do not invent support |

## 3. SMB, disk sharing and filesystem services

| ID | Function | ASUS 52334 state | Decision | Class | Port notes |
|---|---|---|---|---|---|
| M18 | Simpler SMB share naming | `smbd_simpler_naming` absent from ASUS rc/httpd/libshared | **PORT** | C | source-side Samba config/default/UI integration required |
| M19 | Force SMB Master Browser | `smbd_master` absent from ASUS rc/httpd/libshared | **PORT** | C | source-side Samba config/default/UI integration required |
| M20 | WINS server | ASUS rc + libshared retain `smbd_wins`; generic Samba form/NVRAM apply handling was proven | **ADAPT** | A/C | implemented as one exact UI row in stock Samba page; guarded run 36382734032 validates WINS on/off controls, stock `restart_ftpsamba`, and absence of M18/M19 leakage |
| M21 | Windows discovery via `wsdd2` | ASUS smbd/nmbd present; donor `wsdd2` ELF has all NEEDED libs in ASUS, but ASUS `rc` has no wsdd2 lifecycle | **PORT** | A/B/C | binary compatibility proven in 36382208517; source-side start/stop integration is still required, so no binary-only overlay |
| M22 | NFS exports for USB storage | NFS page/daemon/modules absent | **PORT** | A/B/C | `nfsd`, `mountd`, `exportfs`, sunrpc/NFS modules + WebUI/config |
| M23 | CIFS client support | mount points exist but CIFS kernel module absent | **PORT** | B/C | add source-compatible CIFS client support; no blind module transplant |

## 4. VPN, DNS and routing

| ID | Function | ASUS 52334 state | Decision | Class | Port notes |
|---|---|---|---|---|---|
| M24 | Advanced OpenVPN client/server integration | stock OpenVPN exists; Merlin advanced page absent | **ADAPT** | A/B/C | reconcile against later ASUS OpenVPN/security implementation |
| M25 | VPN Director | page and `vpndirector_rulelist` backend absent | **PORT** | A/B/C | JFFS-backed rules, RPDB routing, kill-switch/DNS interaction |
| M26 | DNS Director | ASUS has DNSFilter backend; Merlin page absent | **ADAPT** | A/C | retain ASUS backend, adapt Merlin UI/schema; verify IPv4/IPv6/custom providers |
| M27 | ipset kernel/userspace support | absent | **PORT** | A/B | modules + `libipset` + userspace `ipset` |
| M28 | TOR with per-client access control | ASUS lacks daemon/page and all `Tor_*`/`start_tor` lifecycle contract; donor ELF itself has all NEEDED libs in ASUS | **PORT** | A/B/C | run 36383112487 proves binary compatibility but also Merlin-only rc/libshared lifecycle; source integration required, no standalone-binary overlay |
| M29 | Local NTP daemon | ASUS 52334 has no ntpd/chronyd and no `ntpd_enable` backend/default/UI contract | **PORT** | A/B/C | source/runtime integration required; not an image-only UI port |
| M30 | Redirect client NTP queries to router | `ntpd_server_redir`/`ntpd_server_trust` and firewall redirect contract absent | **PORT** | C | source-side rc/firewall/default/UI integration tied to M29 |
| M31 | TCP/UDP conntrack timeout tuning | backend keys already present; Merlin UI absent | **ADAPT** | A/C | reuse ASUS backend and add compatible controls |
| M32 | Cake SQM QoS | cake module absent | **PORT** | B/C | requires kernel/source compatibility; hardware acceleration implications |
| M33 | WireGuard kernel module/userspace tool | Merlin has `wireguard.ko` + `wg`; ASUS image lacks same runtime components but contains generic WG pages/libvpn | **REVIEW** | B/C/D | determine ASUS 52334 WireGuard capability path before any kernel/tool port |
| M34 | Wireless Site Survey | page absent | **PORT** | A/C | AC86U-specific supported feature since Merlin 386.10 |
| M35 | Detailed WiFi troubleshooting / WiFi Insight | launcher absent in ASUS; pinned Merlin image contains only a stale launcher and no visualization pages/backends | **NO PORT** | — | do not resurrect incomplete legacy WiFi Radar runtime; donor firmware lacks `visindex.asp`/capacity/metrics/config pages and `vis-datacollector`/`vis-dcon` |
| M36 | IPv6-aware DNS Director | ASUS 52334 has IPv6 DNSFilter rule machinery but lacks Merlin `dnsfilter_custom61/62/63` backend/default/UI contract | **ADAPT** | C | built-in-mode IPv6 can reuse ASUS; full Custom 1–3 IPv6 parity needs source-side rc/httpd/defaults integration |
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
| M46 | QoS Stats page | page absent and ASUS 52334 lacks Merlin tc/IPv6/conntrack EJ data handlers plus `ajax_gettcdata.asp` | **PORT** | C | source-side HTTPD/QoS data integration required before UI port |
| M47 | Save traffic history to USB/JFFS/NVRAM | `rstats_path` backend signature exists; Merlin UI absent | **ADAPT** | A/B/C | compare rstats semantics, then restore location/schedule controls |
| M48 | Enhanced/per-IP traffic monitoring | ASUS 52334 lacks `cstats`, `ipt_bandwidth`, cstats backend keys and device traffic pages | **PORT** | B/C | source-side cstats + HTTPD integration required; keep M49 global history separate |
| M49 | Monthly traffic history page | absent | **PORT** | A/C | `Main_TrafficMonitor_monthly.asp` |
| M50 | DHCP reservation hostname field | already present in ASUS page | **NO PORT** | — | stock page contains `dhcp_hostname_x_0`; compare only semantics |
| M51 | Wireless ACL/client-name display enhancement | ASUS 52334 already has client-name resolution and a newer shared `clientList` model | **NO PORT** | — | verified runtime page equivalence; preserve later ASUS implementation |
| M52 | Auto-refreshing advanced wireless client list | stock wireless log page exists, but Merlin AJAX endpoint and `get_wl_status` HTTPD handler are absent | **PORT** | C | page refresh UI is simple, but full Merlin client-list data path requires source-side HTTPD handler before adding `ajax_wificlients.asp` |
| M53 | System Log / Wireless Log no-auto-logout behavior | shared pages differ | **PORT/REVIEW** | C | Merlin explicitly disables auto logout on these log pages |
| M54 | System Log layout/filter/log-level enhancements | shared pages differ | **REVIEW** | C | port only demonstrably missing useful UI behavior |
| M55 | WiFi icon reports both radios | shared UI; exact stock behavior unverified | **REVIEW** | C | small visual/behavioral delta |
| M56 | Editable-entry WebUI enhancements | cross-cutting page differences | **REVIEW** | C | not a single transplantable file |
| M57 | Advanced VPN status page | page absent; stock IPsec AJAX exists but Merlin OpenVPN status endpoint/globals are absent | **PORT** | C | do not add page alone; source-side HTTPD/OpenVPN status endpoint integration required before UI port |
| M58 | QR codes for network/Guest Network | Merlin `qrcode.min.js` present; no same runtime asset in ASUS | **PORT/REVIEW** | A/C | verify ASUS has no alternative implementation before adding |
| M59 | Local OUI database for WebUI/networkmap | Merlin `ajax/ouiDB.json` is runtime-only | **PORT/REVIEW** | A/C | enables local vendor lookup without remote query |
| M60 | JFFS upload/restore page | absent and backend handler absent | **PORT** | C | same source-side dependency as M10; keep as dependency-order alias, not a separate image port |

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
| M67 | OpenVPN client selection for Ookla Speedtest | not present in pinned 386.14_2 donor; appears in later 3006 changelog | **N/A** | — | outside this project's pinned Merlin donor baseline |
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
