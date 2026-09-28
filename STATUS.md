# Status

| Item | Status | Evidence |
|---|---|---|
| ASUS RT-AC86U 3.0.0.4.386_52334 baseline reference | **SUCCESS** | official ASUS support page + published SHA-256 |
| ASUS RT-AC86U 3.0.0.4.386_51955 comparison reference | **SUCCESS** | official ASUS support page + firmware-image SHA-256 verified in run 35987265109 |
| Merlin RT-AC86U 386.14_2 firmware reference | **SUCCESS** | official SourceForge file + published SHA-256 |
| Merlin 386.14_2 source revision | **SUCCESS** | exact tag/ref pinned to Git commit |
| ASUS 386_52334 GPL/source acquisition | **IN PROGRESS** | no matching public archive located; legacy `gpl@asus.com` request bounced with SMTP 550 #5.1.0; current support route deferred |
| Clean ASUS 386.45956 source-lineage anchor | **SUCCESS** | pinned community mirror `a9179fc...`; helper/build-gate/lifecycle/JFFS call-site matrix documented in `docs/source-anchor-45956-findings.md`; this is archaeology only, not the 52334 build base |
| Firmware artifact verification | **SUCCESS** | all three comparison images verified in run 35987265109 |
| Firmware filesystem extraction | **SUCCESS** | ASUS 51955, Merlin 386.14_2 and ASUS 52334 UBI/UBIFS rootfs extracted |
| Direct ASUS 52334 vs Merlin diff | **SUCCESS** | 1992 identical, 60 ASUS-only, 267 Merlin-only, 1939 different |
| ASUS 51955 vs Merlin diff | **SUCCESS** | 2017 identical, 59 ASUS-only, 267 Merlin-only, 1914 different |
| ASUS 51955 vs ASUS 52334 diff | **SUCCESS** | 3505 identical, 1 51955-only, 2 52334-only, 484 different |
| Three-way delta classification | **SUCCESS** | 1513 Merlin-delta/ASUS-unchanged, 266 pure Merlin additions, 460 divergent shared changes |
| Merlin feature compatibility probe | **SUCCESS** | run 35989225935 separates missing features from ASUS-backend overlap |
| Merlin feature-level inventory | **SUCCESS** | README + 386 changelog + runtime/source/three-way/probe evidence consolidated in master inventory |
| JFFS/custom-script source delta map | **SUCCESS** | Action 36123084408 completed successfully on `asus-52334-merlin-port` |
| JFFS/custom-script port specification | **SUCCESS** | behavioral/helper/hook patch series + pinned source contract documented in `docs/jffs-custom-script-port-plan.md` and `docs/jffs-custom-script-source-contract.md` |
| ASUS 52334 DNSFilter runtime map | **SUCCESS** | Action 35993309478 verified retained stock backend/UI-support pieces |
| DNS Director phase-1 overlay implementation | **SUCCESS** | guarded overlay changes only `DNSFilter.asp` + exact-patched `state.js`; validation run 36121711046 passed |
| Guarded Merlin overlay validation | **SUCCESS** | latest feature-aware active-overlay validation run 36382734032 passed; WINS UI contract is checked and ASUS rc/httpd/dnsmasq/BusyBox/OpenVPN/Dropbear remain protected |
| Merlin A/B/C/D implementation classification | **IN PROGRESS** | exact source patch boundaries continue per feature |
| JFFS image-safe subphase | **SUCCESS** | `/rom/etc/profile` exact patch, pinned `/usr/sbin/helper.sh` add-only, 20 custom WebUI aliases add-only; helper includes M05 postconf helpers plus M06 `am_settings_get/set` and `/jffs/addons/custom_settings.txt`; no core binary replacement |
| M12 Scheduled jobs / `cru` | **SUCCESS** | NO PORT: ASUS `cru` is retained. Runs through 36383042773 proved the direct QEMU harness cannot execute ASUS BusyBox reliably (`true`/`sh`/`flock` all rc=1), so Merlin's fd-278 lock delta cannot be safely validated; no unproven script patch and no BusyBox/crond transplant |
| M13 Nano editor | **SUCCESS** | verified Merlin nano 5.7 + isolated add-only `libncurses.so.6.0` runtime executes against ASUS 52334 under qemu; four add-only overlay targets validated in run 36373879103 |
| M16 SCP | **SUCCESS** | reproducible build run `36466679828`; active guarded-overlay validation run `36467262213`: add-only `/usr/bin/scp`, static AArch64/no PT_INTERP, exact SHA-256 `d47ec3eba8bde2e244b96feb47ed0fc26d4556de5aebfd3771822970c5754851`, QEMU usage/local-copy pass, transport remains ASUS `/usr/bin/dbclient`, protected ASUS Dropbear/core unchanged |
| M14 Enhanced CLI utility set | **SUCCESS** | NO generic port: run 36382597888 found no Merlin-only BusyBox symlink command missing from ASUS. Standalone donor ELFs map to separately tracked features (Nano, NFS, ipset, Tor, WireGuard, wsdd2); Merlin BusyBox remains forbidden |
| M11 Custom DDNS callback | **IN PROGRESS** | pinned source delta is now specified in `docs/custom-ddns-source-contract.md`: preserve ASUS DDNS/Inadyn, add separate `CUSTOM` provider, blocking custom `ddns-start`, async normal-provider hook, and `ddns_custom_updated` rc callback; dependency remains JFFS core engine |
| M10 JFFS backup/restore | **IN PROGRESS** | ASUS 52334 stock settings backup page exists, but the build lacks JFFS backup/upload routes/tokens in `httpd/uploader`; source backend required before exposing Merlin UI |
| JFFS core hook/config engine | **IN PROGRESS** | pinned source delta contract complete; requires later ASUS-compatible source build path for `rc`/shared/httpd integration |
| M08/M09 AMTM + Entware/addon integration | **IN PROGRESS** | now classified as add-on layers after generic JFFS source work: M08 = B after M01/M04, M09 = B after M01-M03. No dedicated core patch or baked Entware tree; see `docs/amtm-entware-after-jffs.md` |
| M36 IPv6 DNS Director parity | **IN PROGRESS** | ASUS 52334 already has IPv6 DNSFilter rule machinery (`DNSFILTERI/F`, DHCPv6 option 23) for supported modes, but lacks Merlin `dnsfilter_custom61/62/63` across rc/httpd/defaults; full custom-IPv6 parity requires source integration |
| M18/M19 Samba naming/Master Browser | **IN PROGRESS** | exact donor behavior and later-ASUS merge constraints are specified in `docs/samba-merlin-controls-source-contract.md`: M18 changes only unique share-section naming; M19 adds forced-master config/lifecycle semantics; current M20 WINS backend must remain authoritative |
| M20 WINS server | **SUCCESS** | UI-only ASUS-backed adaptation: `smbd_wins` exists in stock rc + libshared, generic `/start_apply.htm` form handling was proven, exact page patch result is SHA-locked, and guarded validation 36382734032 passes without M18/M19 or core-binary changes |
| M21 Windows discovery (`wsdd2`) | **IN PROGRESS** | donor ELF is dependency-compatible; lifecycle design is now **B after M01-M03**: add-only binary + reconcile wrapper using generic JFFS `services-start/service-event(-end)/post-mount/services-stop`, avoiding any M21-specific ASUS `rc` patch. See `docs/wsdd2-jffs-lifecycle-plan.md` |
| M31 Conntrack timeout tuning | **SUCCESS** | ASUS-backed UI adapter uses stock NVRAM keys and stock reboot apply path; no `rc` replacement |
| M34 Wireless Site Survey | **SUCCESS** | adapted page reuses stock `/apscan.asp` + `restart_wlcscan`; guarded validation run 36338372948 |
| M35 WiFi Insight / legacy WiFi Radar | **CANCELLED** | pinned Merlin 386.14_2 image contains only the launcher; visualization pages/assets and both Broadcom runtime daemons are absent, so there is no complete donor runtime to restore |
| M47 Traffic history persistence controls | **SUCCESS** | ASUS `rstats`/libshared backend verified and safe controls exposed in Other Settings |
| M48 per-IP traffic/cstats | **NO PORT** | pinned Merlin 386.14_2 deliberately excludes cstats on HND in build, rc lifecycle, firewall accounting, HTTPD handlers and installed device pages; RT-AC86U is HND. See `docs/per-ip-traffic-hnd-donor-classification.md` |
| M49 Global monthly traffic history | **SUCCESS** | ASUS history spool contains monthly data; adapted Merlin page + add-only Chart.js validated in run 36334016748 |
| M59 Local OUI database | **SUCCESS** | verified Merlin OUI DB add-only; exactly three ASUS remote OUI lookups redirected locally; guarded validation run 36336834393 |\n| M69 WebUI diagnostics umbrella | **SUCCESS** | no separate port: constituent QR/OUI/log diagnostics work is already tracked under M53/M54/M58/M59 |
| M58 QR codes for WiFi/Guest Network | **SUCCESS** | add-only pinned QR library + exact multi-patches of ASUS Guest Network/router pages; validation run 36337583899 |
| M43 System Info page | **IN PROGRESS** | narrowed to a small read-only HTTPD/sysinfo backend (`cpu.model`, `cpu.freq`, `conn.max`, `nvram.total` plus only missing AJAX fields) followed by add-only page/AJAX/menu integration; see `docs/system-info-source-contract.md` |
| M46 QoS Stats / Classification page | **IN PROGRESS** | ASUS 52334 lacks `ajax_gettcdata.asp`, `get_ipv6clients_array`, `get_tcfilter_array`, `get_tcdata`/conntrack data handlers; source-side HTTPD/QoS integration required |
| M44 Other Settings page | **SUCCESS** | add-only page exposes only ASUS-backed conntrack, traffic-history persistence, and shell-timeout controls; unsupported Merlin-only settings are omitted |\n| M45 Temperature/performance page | **SUCCESS** | ASUS-native `/ajax_coretmp.asp` backend reused; guarded validation run 36338181498 |
| M51 Wireless ACL/client-name display | **SUCCESS** | NO PORT: ASUS 52334 already resolves/stores client names through its newer `clientList` model and ACL page logic; compatibility run 36373415595 |
| M52 Auto-refreshing wireless client list | **IN PROGRESS** | stock page + `wl_log.asp` exist, but Merlin's `ajax_wificlients.asp` endpoint depends on `get_wl_status`, absent from ASUS 52334 `httpd`; source-side HTTPD work required for full feature |
| M53 System/Wireless Log no-auto-logout | **SUCCESS** | two SHA-locked page-only patches validated by guarded overlay run 36369816037; no backend/core changes |
| M54 System Log enhancements | **SUCCESS** | safe UI-only subset implemented: local logFilter database + auto-refresh/filter controls; unsupported Merlin log-level backend controls deliberately excluded; guarded validation run 36370670710 |
| M55 Dual-radio WiFi icon | **SUCCESS** | ASUS hardware-switch logic preserved; no-switch on/partial/off fallback plus minimal partial-state CSS validated in run 36370439356 |\n| M56 Editable-entry WebUI enhancements | **SUCCESS** | NO PORT: run 36397818442 shows ASUS 52334 already provides edit flows on shared DHCP/port-forward and other pages; Merlin-only residual edit surfaces belong to separately gated NFS/OpenVPN/VPN Director work |
| M57 Advanced VPN Status | **IN PROGRESS** | narrowed to a small read-only VPN status backend (`pid`, tunnel IP, OpenVPN status-file data) plus add-only AJAX/page/menu; donor poll-side NVRAM writes and 5s sleep are rejected. See `docs/advanced-vpn-status-source-contract.md` |\n| M24 Advanced OpenVPN integration | **IN PROGRESS** | runs 36398033834/36398402429: ASUS has a later native OpenVPN UI/lifecycle; Merlin-only client controls are not safe UI-only additions because their keys are not proven consumed by ASUS rc/libvpn. Keep stock UI and implement only separately proven source deltas (M38/M40) |
| M38 OpenVPN DNS Exclusive | **IN PROGRESS** | donor port-53 NAT-chain/up-down/dnsmasq semantics are bounded in `docs/openvpn-dns-exclusive-source-contract.md`; ASUS 52334 OpenVPN remains authoritative and policy-mode integration must align with M40/VPN Director |
| M39 OpenVPN custom-option storage | **SUCCESS** | NO PORT: run 36384020800 confirms ASUS 52334 already stores OpenVPN material under `/jffs/openvpn` and provides a larger 15000-character `vpn_server_custom` field; preserve the newer ASUS storage model rather than graft Merlin `custom3` split storage |\n| M40 Merlin OpenVPN routing semantics | **IN PROGRESS** | run 36384020800: ASUS retains generic route primitives but lacks Merlin `ovpnc` policy tables, `vpn_client*_rgw/enforce`, and VPN Director routing integration; source-side integration required without replacing ASUS OpenVPN |\n
| Merlin feature port | **IN PROGRESS** | DNS Director + image-safe JFFS/addon + ASUS-backed Other Settings + monthly traffic + local OUI + WiFi QR implemented; no unsafe core binary replacement |
| Flashable firmware | **IN PROGRESS** | no flashability claim until repack + hardware/runtime gates pass |

## Status vocabulary

Only these project states are used:

- **SUCCESS**
- **FAILURE**
- **IN PROGRESS**
- **CANCELLED**

| M67 Speedtest VPN interface selector | **CANCELLED** | feature appears in later 3006 Merlin changelog; pinned 386.14_2 `internet_speed.html` has no VPN/interface selector, so it is outside this donor baseline |

| M68 Outbound LAN allowed logging | **IN PROGRESS** | clean ASUS 45956 source vs pinned Merlin proves a one-line `ACCEPT` → `logaccept` target delta in the default LAN→WAN FORWARD rule; contract: `docs/outbound-lan-logging-source-contract.md`; later ASUS `rc` source still required |

| M66 Prevent Auto DoH / DDR / Private Relay | **IN PROGRESS** | donor Auto/Yes/No conditions and exact dnsmasq canaries are specified in `docs/prevent-auto-doh-source-contract.md`; source config-generation port only, with a targeted 52334 key/UI ownership check still required |

| M64 Traditional QoS overhead/download stats | **IN PROGRESS** | donor overhead/framing behavior is source-bounded in `docs/qos-overhead-stats-source-contract.md`; download class counters are explicitly folded into future M46 QoS Stats HTTPD integration |

| Late 386.51997 source triangulation | **SUCCESS** | Merlin `386.12_x` is pinned as a modified source/build tree merged with GPL 386_51997; SWRT independently documents Brcm AC merged with 386_51997. Both are structural references only; clean late ASUS source remains missing. See `docs/source-anchor-51997-triangulation.md` |

| M04 custom config/postconf framework | **IN PROGRESS** | helper implementation is inherited from ASUS lineage; exact append → full replace → 120s postconf sequencing and staged generator targets are specified in `docs/custom-config-postconf-source-contract.md` |

| M01-M03 JFFS core lifecycle patch series | **IN PROGRESS** | helper exposure, JFFS directory bootstrap, service/network/DHCP/USB/QoS/update hook signatures and blocking/argument semantics are frozen in `docs/jffs-core-source-patch-series.md`; signatures are stable across 386.12/51997 and 386.14_2 |

| M10/M60 JFFS backup/restore | **IN PROGRESS** | donor UI/archive semantics are bounded, but old `rm -rf /jffs/*` + unrestricted `tar -xf` restore is explicitly rejected; hardened authenticated full-JFFS design is in `docs/jffs-backup-restore-source-contract.md`; ASUS `RTCONFIG_SAVEJFFS` is partial-design reference only |

| M29/M30 local NTP server + redirect | **IN PROGRESS** | donor `/usr/sbin/ntp` proven to be Merlin BusyBox NTPD alias, so no binary transplant. Clean ASUS source already carries server-capable NTPD code but disables it. Plan: isolated ASUS-source NTPD in `-w` server-only mode after JFFS hooks, DHCP advertisement via M04 postconf, M30 via `firewall-start`; `ntpd_server_trust` is not a 386.14_2 donor key. See `docs/local-ntp-jffs-adaptation.md` |

| M28 Tor transparent proxy | **IN PROGRESS** | clean ASUS 45956 already contains disabled `RTCONFIG_TOR` backend/page/accounts/firewall/source; pinned donor advances Tor to 0.4.7.16. Final design re-enables/reconciles ASUS-lineage source, requires M29 local NTP, keeps fail-closed IPv4 rules synchronous in firewall generation, and adds IPv6 FORWARD-drop hardening. See `docs/tor-source-lineage-contract.md` |

| M25/M40 VPN Director routing | **IN PROGRESS** | rule schema, persistent store, `ovpncN` table construction, RPDB priority ownership, per-client killswitch, cleanup and M38 DNS coupling are specified in `docs/vpn-director-routing-source-contract.md`; later ASUS-compatible OpenVPN/routing source remains required |

| M46 QoS Stats | **IN PROGRESS** | narrowed to read-only tc-class + BWDPI HTTPD handlers, then add-only page/AJAX/menu integration; M64 download counters share this backend. See `docs/qos-stats-source-contract.md` |

| M52 Wireless client auto-refresh | **IN PROGRESS** | narrowed to read-only `get_wl_status` Broadcom/HND HTTPD handler + AJAX/exact Wireless Log page adaptation; no wireless daemon/driver replacement. Must compose with M53 no-auto-logout. See `docs/wireless-client-refresh-source-contract.md` |
| M36 IPv6 DNS Director Custom 1–3 | **IN PROGRESS** | existing ASUS IPv6 DNSFilter rule engine is retained; only `dnsfilter_custom61/62/63` defaults + HND AF_INET6 custom resolver mapping + follow-up UI fields remain. Contract: `docs/dns-director-ipv6-custom-source-contract.md` |

| Optional kernel module ABI CRC probe | **SUCCESS / DIAGNOSTIC LIMIT** | run `36447256650`: Merlin image contains NFS stack, CIFS, full ipset family, `sch_cake` and WireGuard modules, but stock ASUS and donor modules expose no readable MODVERSIONS CRC table (`required=0`, ASUS observed pairs=0); binary ABI cannot be proven from images, so M22/M23/M27/M32/M33 remain source-build-only and donor `.ko` transplant stays forbidden |

| M29 isolated local NTP daemon build | **SUCCESS / REPRODUCIBLE CANDIDATE** | run `36466577777`: clean ASUS-lineage BusyBox NTPD built twice byte-identically as static ELF64 AArch64 single-applet (925720 bytes), no PT_INTERP, correct `-w/-t/-l/-I/-p` surface, qemu root launch stayed alive to timeout; SHA-256 `6885069bb5ee26512b7f6903c08b3f28304f0b29e45bc7e810eeefe67276c6fb`. Remaining M29 work is add-only lifecycle/dnsmasq integration after M01-M04 |

