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
| M01 | JFFS user scripts under `/jffs/scripts/` | helper implementation exists in clean ASUS lineage but is TOR-gated and normal lifecycle call sites are absent | **PORT** | C | ordered source patch series in `docs/jffs-core-source-patch-series.md`; preserve inherited helper implementation and add only exposure/default/bootstrap + reviewed call sites |
| M02 | `service-event` / `service-event-end` hooks | absent | **PORT** | C | stable across Merlin 386.12/51997 and 386.14_2: blocking 120s pre-dispatch + async post-dispatch with action/service args; exact contract in `docs/jffs-core-source-patch-series.md` |
| M03 | Event hooks: init/firewall/services/NAT/WAN/QoS/DDNS/USB/DHCP/update | most Merlin hook signatures absent | **PORT** | C | core non-DDNS lifecycle signatures are stable across 386.12/51997 and 386.14_2 and frozen in `docs/jffs-core-source-patch-series.md`; DDNS-specific M11 remains separate |
| M04 | postconf/custom config framework | helper primitive exists in clean ASUS lineage but generator call sites are absent | **PORT** | B/C | exact append → replace → blocking postconf sequencing and Tier-1 generator targets are defined in `docs/custom-config-postconf-source-contract.md`; port per generator, never transplant donor rc/httpd files |
| M05 | Addon helper API | stock helper absent; pinned Merlin `helper.sh` is add-only in guarded overlay | **SUCCESS** | A | active overlay ships pinned `/usr/sbin/helper.sh`; image-safe foundation validated, with core generator/event hooks tracked separately under M01-M04 |
| M06 | Addon custom-settings API | stock API absent; active pinned `helper.sh` provides `am_settings_get/set` and `/jffs/addons/custom_settings.txt` | **SUCCESS** | A | delivered as part of the image-safe JFFS helper foundation; runtime lifecycle dependency remains owned by M01-M04, not M06 |
| M07 | 20 custom WebUI slots | stock aliases absent; 20 add-only `/www/userN.asp -> user/userN.asp` aliases are active | **SUCCESS** | A | all 20 aliases target stock `/www/user -> /var/wwwext`; deeper addon lifecycle is tracked separately under M01-M04 |
| M08 | AMTM management interface | donor `/usr/sbin/amtm` is standalone shell bootstrap | **PORT** | B after M01/M04 | `docs/amtm-entware-after-jffs.md`: add-only AMTM after real `jffs2_scripts`/addon/config foundation exists; preserve ASUS curl/TLS stack and do not vendor live online modules |
| M09 | Entware/addon friendliness | `/opt -> tmp/opt` already exists; missing piece is generic lifecycle | **PORT** | B after M01-M03 | `docs/amtm-entware-after-jffs.md`: no dedicated core patch or baked package tree; rely on services/post-mount hooks for user-installed Entware/addons |
| M10 | JFFS backup/restore/upload WebUI | stock settings-backup page exists; full addon-JFFS handlers are absent, while clean ASUS 45956 exposes only disabled partial `RTCONFIG_SAVEJFFS` machinery | **PORT** | C | hardened authenticated full-JFFS design in `docs/jffs-backup-restore-source-contract.md`; reuse later ASUS auth/upload architecture but reject donor's destructive unrestricted tar restore |
| M11 | Custom DDNS user-script callback | ASUS 52334 lacks Merlin `CUSTOM` script provider, `ddns-start` hook and `ddns_custom_updated` callback | **PORT** | C | exact source contract in `docs/custom-ddns-source-contract.md`; preserve stock DDNS/Inadyn and ASUS `WWW.DYNDNS.ORG(CUSTOM)` while adding the separate script-driven provider after JFFS core hooks exist |
| M12 | Scheduled jobs / `cru` | ASUS has a functional native `cru`; Merlin's material delta is fd-based `flock` locking | **NO PORT** | B | keep ASUS `cru`/crond/BusyBox. QEMU cannot execute this ASUS BusyBox reliably enough to prove the fd-278 delta (run 36383042773), so no unproven lock patch is justified |

## 2. Shell, SSH and administration

| ID | Function | ASUS 52334 state | Decision | Class | Port notes |
|---|---|---|---|---|---|
| M13 | Nano editor | absent in ASUS; donor nano requires ncurses | **SUCCESS** | A/B | pinned nano 5.7 + isolated add-only `libncurses.so.6.0`, `libncurses.so.6` symlink and `rnano` symlink validated under qemu and guarded overlay run 36373879103 |
| M14 | Enhanced CLI utility set | run 36382597888 found no Merlin-only BusyBox symlink command absent from ASUS; remaining standalone donor ELFs belong to separately tracked feature blocks | **NO PORT** | A/B | no generic CLI transplant. M13 Nano is the isolated proven exception; BusyBox remains ASUS-authoritative |
| M15 | SSH public-key authentication | already present | **NO PORT** | C | ASUS `rc` already contains `authorized_keys` support |
| M16 | Merlin SSH behavior / SCP | ASUS key/host-key behavior already overlaps sufficiently; missing parity was SCP | **SUCCESS** | B | build run `36466679828` + guarded overlay run `36467262213`: add-only standalone `/usr/bin/scp` (`d47ec3eb...`), delegates transport to ASUS `/usr/bin/dbclient`; no Dropbear core replacement |
| M17 | SNMP | not present in verified AC86U Merlin image | **N/A** | — | Merlin README says only some models; do not invent support |

## 3. SMB, disk sharing and filesystem services

| ID | Function | ASUS 52334 state | Decision | Class | Port notes |
|---|---|---|---|---|---|
| M18 | Simpler SMB share naming | `smbd_simpler_naming` absent from ASUS rc/httpd/libshared | **PORT** | C | exact donor uniqueness/section-name semantics documented in `docs/samba-merlin-controls-source-contract.md`; graft into later ASUS generator only |
| M19 | Force SMB Master Browser | `smbd_master` absent from ASUS rc/httpd/libshared | **PORT** | C | exact global-config + no-disk lifecycle semantics documented in `docs/samba-merlin-controls-source-contract.md`; preserve current ASUS/M20 WINS path |
| M20 | WINS server | ASUS rc + libshared retain `smbd_wins`; generic Samba form/NVRAM apply handling was proven | **SUCCESS** | A | one exact UI row is active in the stock Samba page; guarded run 36382734032 validates WINS on/off, stock `restart_ftpsamba`, and no M18/M19 leakage |
| M21 | Windows discovery via `wsdd2` | ASUS smbd/nmbd present; donor `wsdd2` ELF has all NEEDED libs in ASUS | **PORT** | B after M01-M03 | binary compatibility proven in 36382208517; `docs/wsdd2-jffs-lifecycle-plan.md` replaces the wsdd2-specific `rc` patch with an add-only binary + idempotent reconcile wrapper driven by generic JFFS lifecycle hooks |
| M22 | NFS exports for USB storage | ASUS image has no NFS userland or NFS/sunrpc kernel modules; Merlin has both | **PORT** | B/C | run 36383330681: donor modules report `4.1.27 SMP preempt mod_unload aarch64`, but matching vermagic is not kernel symbol/config ABI proof; rebuild/integrate against ASUS kernel source, then add userland/WebUI; ABI diagnostics: `docs/optional-kernel-module-abi-strategy.md`. |
| M23 | CIFS client support | ASUS lacks `cifs.ko`; Merlin donor has it | **PORT** | B/C | run 36383330681 confirms kernel component gap; source-build for ASUS kernel required, no donor `.ko` transplant; ABI diagnostics: `docs/optional-kernel-module-abi-strategy.md`. |

## 4. VPN, DNS and routing

| ID | Function | ASUS 52334 state | Decision | Class | Port notes |
|---|---|---|---|---|---|
| M24 | Advanced OpenVPN client/server integration | ASUS 52334 has its own later client/server UI/lifecycle; focused probing found no safe monolithic donor page/backend to port | **NO PORT (umbrella)** | — | preserve newer ASUS OpenVPN. Independently proven missing behavior is tracked under M38 DNS Exclusive, M40/VPN Director routing and M57 Advanced VPN Status; do not expose unproven legacy NVRAM controls |
| M25 | VPN Director | page and `vpndirector_rulelist` backend absent | **PORT** | C | shared routing contract with M40 in `docs/vpn-director-routing-source-contract.md`: validated JFFS-backed rule store, deterministic RPDB/table ownership, per-client killswitch, and shared parser for M38 DNS policy |
| M26 | DNS Director phase 1 | ASUS DNSFilter backend already provides the usable IPv4 enforcement engine; Merlin page absent | **SUCCESS** | A | guarded overlay ships adapted `DNSFilter.asp` + exact `state.js` enablement; validation run 36121711046. Remaining IPv6 Custom 1–3 parity is tracked separately as M36 |
| M27 | ipset kernel/userspace support | ASUS lacks `ipset` userland and `ip_set*`/`xt_set` modules; Merlin contains them | **PORT** | B/C | run 36383330681: kernel/source build required first; do not overlay donor modules or userland alone; ABI diagnostics: `docs/optional-kernel-module-abi-strategy.md`. |
| M28 | TOR with per-client access control | clean ASUS 45956 already contains disabled `RTCONFIG_TOR` backend/page/accounts/firewall/source package; donor ELF compatibility was proven but old ASUS Tor is 0.4.5.8 vs pinned donor 0.4.7.16 | **PORT** | C + M29 | `docs/tor-source-lineage-contract.md`: re-enable/reconcile ASUS-lineage backend in later source, build pinned Tor generation against ASUS runtime, keep fail-closed firewall synchronous, and add IPv6 FORWARD-drop hardening to prevent bypass |
| M29 | Local NTP daemon | reproducible ASUS-lineage static AArch64 daemon is now staged dormant and guarded | **PORT** | B after M01-M04 | build run `36466577777` + overlay run `36468186414`; add-only `/usr/libexec/rtac86u-ntpd` SHA-256 `6885069b...`, no startup reference yet; preserve ASUS `ntp_ready`/ntpclient, lifecycle via generic JFFS hooks, DHCP advertisement via M04 |
| M30 | Redirect client NTP queries to router | `ntpd_server_redir` backend absent; pinned 386.14_2 has no `ntpd_server_trust` NVRAM feature | **PORT** | B after M03 + M29 | `docs/local-ntp-jffs-adaptation.md`: donor UDP/123 REDIRECT semantics can be owned by a dedicated NAT chain restored through `firewall-start`; no ASUS firewall binary/source patch required for M30 |
| M31 | TCP/UDP conntrack timeout tuning | ASUS backend keys already present; only UI adaptation was needed | **SUCCESS** | A | ASUS-backed UI adapter uses stock NVRAM keys and stock reboot apply path; no `rc` replacement |
| M32 | Cake SQM QoS | ASUS lacks `sch_cake.ko`/`act_ctinfo.ko`; Merlin contains both | **PORT** | B/C | run 36383330681: ASUS-kernel-compatible build/integration required; preserve ASUS acceleration/runtime policy; ABI diagnostics: `docs/optional-kernel-module-abi-strategy.md`. |
| M33 | WireGuard kernel module/userspace tool | ASUS has no `wireguard.ko` or `wg`; Merlin has both, while ASUS still contains some generic WG UI/libvpn tokens | **PORT** | B/C/D | run 36383330681 closes binary-overlay path: kernel module must be built/integrated for ASUS 4.1.27 tree before userspace/UI capability is enabled; never transplant donor `.ko`; ABI diagnostics: `docs/optional-kernel-module-abi-strategy.md`. |
| M34 | Wireless Site Survey | page absent in stock image but stock scan backend already existed | **SUCCESS** | A | adapted page reuses ASUS `/apscan.asp` + `restart_wlcscan`; guarded validation run 36338372948 |
| M35 | Detailed WiFi troubleshooting / WiFi Insight | launcher absent in ASUS; pinned Merlin image contains only a stale launcher and no visualization pages/backends | **NO PORT** | — | do not resurrect incomplete legacy WiFi Radar runtime; donor firmware lacks `visindex.asp`/capacity/metrics/config pages and `vis-datacollector`/`vis-dcon` |
| M36 | IPv6-aware DNS Director | ASUS 52334 already has IPv6 DNSFilter rule machinery; missing parity is the three HND custom IPv6 server keys/mapping/default/UI contract | **ADAPT** | narrow C + A | exact scope in `docs/dns-director-ipv6-custom-source-contract.md`: add `dnsfilter_custom61/62/63` defaults + AF_INET6 Custom 1–3 resolver mapping, then minimally extend the existing project DNS Director page |
| M37 | IPv6 OpenVPN server + optional IPv6 NAT | ASUS stock page already exposes IPv6 server mode, NAT6, IPv6 subnet/local/remote fields; matching `vpn_server_ip6/nat6/sn6/local6/remote6` defaults exist in ASUS libshared | **NO PORT** | — | run 36383666065: preserve newer ASUS implementation; no Merlin OpenVPN transplant |
| M38 | OpenVPN DNS Exclusive behavior | ASUS retains `vpn_client_adns` default but lacks Merlin `ovpn_set_exclusive_dns`, `ovpn_clear_exclusive_dns` and ordered per-client DNS-chain behavior | **PORT** | C | exact donor contract in `docs/openvpn-dns-exclusive-source-contract.md`; preserve later ASUS OpenVPN/dnsmasq and reconcile policy-mode DNS interception with M40/VPN Director routing ownership |
| M39 | OpenVPN custom options stored in JFFS / expanded storage | ASUS 52334 already uses `/jffs/openvpn` and exposes a 15000-character `vpn_server_custom` field; Merlin adds the older `custom3` split-storage contract | **NO PORT** | — | run 36384020800: preserve newer ASUS OpenVPN storage; do not graft Merlin `custom3`/`cust2` layout onto ASUS 52334 |
| M40 | Multiple OpenVPN client routes and Merlin routing semantics | ASUS has generic route-nopull/route primitives but lacks Merlin `ovpnc` policy tables, `vpn_client*_rgw/enforce` and VPN Director rule integration | **PORT** | C | exact table-build/RPDB priority/killswitch/client cleanup semantics are frozen with M25 in `docs/vpn-director-routing-source-contract.md`; preserve ASUS OpenVPN binary and later routing/security baseline |
| M41 | `dhcpc-event` IPv4/IPv6 protocol argument | Merlin hook API extension | **PORT** | C | exact three-context contract is frozen in `docs/jffs-core-source-patch-series.md`: WAN v4 = event+`4`, LAN/AP DHCP client = event only, WAN v6 = event+`6`; stable across 386.12/386.14 |
| M42 | QoS `qos-start init` blocking hook semantics | stock user-hook absent | **PORT** | C | stable across 386.12/386.14: async `qos-start rules` plus 120-second blocking `qos-start init` at both donor init paths; exact contract in `docs/jffs-core-source-patch-series.md` |

## 5. WebUI, monitoring and diagnostics

| ID | Function | ASUS 52334 state | Decision | Class | Port notes |
|---|---|---|---|---|---|
| M43 | System Info summary page | stock ASUS has generic sysinfo plumbing but lacks key Merlin read-only fields | **PORT** | C backend + A UI | minimal HTTPD handler set and add-only page/AJAX contract in `docs/system-info-source-contract.md`; do not replace ASUS httpd or import irrelevant platform handlers |
| M44 | Other Settings page | stock page absent; verified ASUS-backed controls are exposed through an add-only Tools page | **SUCCESS** | A | active overlay ships `Tools_OtherSettings.asp` with only proven conntrack, traffic-history and shell-timeout controls; unsupported Merlin-only settings remain omitted |
| M45 | Temperature/performance page | stock ASUS temperature AJAX backend already existed; page was absent | **SUCCESS** | A | active overlay adds `Advanced_PerformanceTuning_Content.asp` using stock `/ajax_coretmp.asp`; guarded validation run 36338181498 |
| M46 | QoS Stats page | page absent and ASUS 52334 lacks Merlin tc/BWDPI data handlers plus `ajax_gettcdata.asp` | **PORT** | C backend + A UI | exact read-only tc-class + BWDPI conntrack contract in `docs/qos-stats-source-contract.md`; M64 download statistics are folded into this backend |
| M47 | Save traffic history to USB/JFFS/NVRAM | ASUS `rstats`/libshared backend already supports the required persistence settings; Merlin page absent | **SUCCESS** | A | safe persistence controls are exposed through the active Other Settings page; ASUS `rstats` remains authoritative |
| M48 | Per-IP traffic monitoring / cstats | pinned Merlin 386.14_2 explicitly excludes legacy iptraffic/cstats HTTPD handlers and removes device traffic pages on `HND_ROUTER` | **CANCELLED / NO PORT** | - | RT-AC86U is HND; adding legacy `ipt_account`/cstats would exceed donor parity. Evidence: `docs/per-ip-traffic-hnd-donor-classification.md` |
| M49 | Monthly traffic history page | ASUS history spool already contains monthly data; only page/chart adaptation was missing | **SUCCESS** | A | adapted Merlin page + pinned local Chart.js validated in run 36334016748; active overlay ships `/www/Main_TrafficMonitor_monthly.asp` |
| M50 | DHCP reservation hostname field | already present in ASUS page | **NO PORT** | — | stock page contains `dhcp_hostname_x_0`; compare only semantics |
| M51 | Wireless ACL/client-name display enhancement | ASUS 52334 already has client-name resolution and a newer shared `clientList` model | **NO PORT** | — | verified runtime page equivalence; preserve later ASUS implementation |
| M52 | Wireless client auto-refresh | stock Wireless Log exists but ASUS 52334 lacks Merlin structured `get_wl_status` AJAX contract | **PORT** | C backend + A UI | small read-only Broadcom/HND HTTPD handler + add-only AJAX/exact page adaptation; contract in `docs/wireless-client-refresh-source-contract.md`; preserve M53 patch |
| M53 | System Log / Wireless Log no-auto-logout behavior | ASUS pages lacked Merlin session override | **SUCCESS** | A | two SHA-locked page-only patches validated by guarded overlay run 36369816037; no backend/core changes |
| M54 | System Log layout/filter/log-level enhancements | ASUS lacked only the safe UI subset selected for this project | **SUCCESS** | A | local logFilter database + auto-refresh/filter controls validated by run 36370670710; unsupported Merlin backend log-level controls deliberately excluded |
| M55 | WiFi icon reports both radios | stock single-state presentation adapted without replacing hardware-switch logic | **SUCCESS** | A | no-switch on/partial/off fallback + minimal partial-state CSS validated by run 36370439356 |
| M56 | Editable-entry WebUI enhancements | ASUS 52334 already has editable-entry behavior on the main shared targets, including DHCP reservations and port forwarding; remaining Merlin-only edit surfaces map to separately gated NFS/OpenVPN/VPN Director features | **NO PORT** | — | run 36397818442: preserve newer ASUS table/edit implementations; do not apply a generic cross-page Merlin patch |
| M57 | Advanced VPN status page | stock IPsec AJAX exists; Merlin consolidated OpenVPN status API/page absent | **PORT** | C backend + A UI | stable 386.12/386.14 donor API is frozen in `docs/advanced-vpn-status-source-contract.md`; implement read-only `pid/vpnip/vpnstatus` equivalents without donor NVRAM writes or blocking sleep |
| M58 | QR codes for network/Guest Network | ASUS lacked equivalent runtime asset on target pages | **SUCCESS** | A | add-only pinned QR library + exact page patches validated by run 36337583899 |
| M59 | Local OUI database for WebUI/networkmap | ASUS used remote OUI lookups on three target surfaces | **SUCCESS** | A | pinned local OUI DB added and exactly three ASUS remote lookups redirected locally; guarded validation run 36336834393 |
| M60 | JFFS upload/restore page | same backend dependency as M10 | **PORT** | C | folded into M10; one hardened backend contract in `docs/jffs-backup-restore-source-contract.md`, no duplicate implementation |

## 6. QoS and networking refinements from the 386 changelog

These are feature-bearing behavior changes rather than standalone pages.

| ID | Function | Decision | Notes |
|---|---|---|---|
| M61 | QoS Classification resolves local IPv6 addresses | **FOLDED INTO M46** | — | not a standalone port: IPv6 client/name handling is part of the M46 QoS Stats backend/UI contract |
| M62 | Show tracked connections even without Adaptive QoS | **FOLDED INTO M46** | — | not a standalone port: BWDPI connection visibility/degradation semantics are part of `docs/qos-stats-source-contract.md` |
| M63 | Basic IPv6 support for Traditional QoS | **NO PORT** | run 36383630066: ASUS `rc` already contains the core IPv6 TQoS runtime signatures `mangle_rules_ipv6`, `ip6tables-restore` and `QOSO`, matching donor surface; preserve newer ASUS implementation |
| M64 | Traditional QoS overhead accuracy/download statistics improvements | **PORT** | clean ASUS 45956 source confirms no `qos_overhead`/`qos_atm`; donor shaping/framing rules and the M46-owned download tc-class datapath are bounded in `docs/qos-overhead-stats-source-contract.md`; narrow source integration only |
| M65 | IPv6 DDNS support | ASUS already contains `ddns_ipv6_update`, `ddns_ipv6_ipaddr`, `ddns_ipv6_updated` runtime/default contract and stock IPv6 DDNS UI | **NO PORT** | — | run 36383666065: later ASUS already provides the donor feature; preserve stock implementation |
| M66 | Prevent Auto DoH also handles DDR / Private Relay interactions | run 36409047088 proves ASUS 52334 lacks `dns_priv_override` in rc/httpd/libshared, lacks its UI, and lacks all donor canaries | **PORT** | C | exact Auto/Yes/No + canary contract in `docs/prevent-auto-doh-source-contract.md`; source patch definitively needs default + UI + later-ASUS dnsmasq-generator integration |
| M67 | OpenVPN client selection for Ookla Speedtest | not present in pinned 386.14_2 donor; appears in later 3006 changelog | **N/A** | — | outside this project's pinned Merlin donor baseline |
| M68 | Outbound LAN connection logging when allowed-connection logging is enabled | **PORT** | clean ASUS 45956 has two equivalent LAN default-allow call sites (single-/multi-WAN) targeting literal `ACCEPT`; pinned Merlin changes only each target to existing `logaccept`. Contract: `docs/outbound-lan-logging-source-contract.md`; source-port only |
| M69 | Local QR/OUI and WebUI diagnostics additions | **NO PORT (umbrella)** | constituent work is tracked and completed under M53/M54/M58/M59; keep this row only as a grouping alias, not an additional port |

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
