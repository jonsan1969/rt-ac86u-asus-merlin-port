# Status

| Item | Status | Evidence |
|---|---|---|
| ASUS RT-AC86U 3.0.0.4.386_52334 baseline reference | **SUCCESS** | official ASUS support page + published SHA-256 |
| ASUS RT-AC86U 3.0.0.4.386_51955 comparison reference | **SUCCESS** | official ASUS support page + firmware-image SHA-256 verified in run 35987265109 |
| Merlin RT-AC86U 386.14_2 firmware reference | **SUCCESS** | official SourceForge file + published SHA-256 |
| Merlin 386.14_2 source revision | **SUCCESS** | exact tag/ref pinned to Git commit |
| ASUS 386_52334 GPL/source acquisition | **IN PROGRESS / EXTERNAL BLOCKER** | rechecked 2026-10-01: ASUS public RT-AC86U support still publishes binary 3.0.0.4.386_52334 (2026-05-07, SHA-256 `E8FD0F3A...`) and marks the model EOL, but no matching `300438652334` / `386_52334` GPL archive or public mirror was located via ASUS/public web/GitHub searches. Legacy `gpl@asus.com` request previously bounced SMTP 550 #5.1.0. Do not repeat source hunting every work cycle; source-backed core features remain externally blocked until new evidence appears. |
| Clean ASUS 386.45956 source-lineage anchor | **SUCCESS** | pinned community mirror `a9179fc...`; helper/build-gate/lifecycle/JFFS call-site matrix documented in `docs/source-anchor-45956-findings.md`; this is archaeology only, not the 52334 build base |
| Firmware artifact verification | **SUCCESS** | all three comparison images verified in run 35987265109 |
| ASUS 52334 stock semantic repack round-trip | **SUCCESS** | Run `36859123113` re-certifies stock extract/rebuild/WFI/re-extract with permission/xattr-preserving `ubi-reader -k -x`; semantic equality and geometry pass. Stock baseline only, not flashability. |
| Active guarded-overlay firmware repack | **SUCCESS / UNVALIDATED CANDIDATE PUBLISHED** | Run `36924014278` is the current full software-gate reference: exact 570-PEB UBI, valid WFI, zero semantic drift, protected ASUS core byte identity, zero K2/K3 leakage. It also publishes quarantined artifact `RT-AC86U-52334-merlin-port-UNVALIDATED` (artifact id `11193520953`, archive digest `sha256:bce18b898bf81f45c0b1ab616a42f511c25246b0b1e408e49d8e881d25e16f52`, expires 2026-10-08). This is NOT a flashability claim; exact image SHA-256 is inside its `SHA256SUMS` and must anchor future hardware evidence. |
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
| Guarded Merlin overlay validation | **SUCCESS** | Run `36858785201` passes after aligning validation with capacity-optionalized payloads. Monthly Traffic/Chart.js, Nano/ncurses and local OUI are no longer required built-ins; dead Monthly Traffic Tools-menu exposure was removed. Run `36858759242` was the superseded stale-validator failure and its log was fetched once. |
| Merlin A/B/C/D implementation classification | **IN PROGRESS** | exact source patch boundaries continue per feature |
| JFFS image-safe subphase | **SUCCESS** | profile/helper pieces remain proven; M07 aliases pass guarded overlay run `36864603084`. Metadata-faithful extraction shows stock `/www/user -> /var/wwwext`; Binwalk's `/dev/null` result was an extraction artifact exposed by fail-closed run `36864603300`. No core binary replacement. |
| M12 Scheduled jobs / `cru` | **SUCCESS** | NO PORT: ASUS `cru` is retained. Runs through 36383042773 proved the direct QEMU harness cannot execute ASUS BusyBox reliably (`true`/`sh`/`flock` all rc=1), so Merlin's fd-278 lock delta cannot be safely validated; no unproven script patch and no BusyBox/crond transplant |
| M13 Nano editor | **SUCCESS** | implementation/runtime contract proven in run 36373879103, but Nano/ncurses were removed from the built-in rootfs for the immutable 570-PEB capacity gate. Not present in the current active image. Optional JFFS delivery under `/jffs/addons/merlin-tools` is now proven by run `36863705618` with pinned checksum verification, isolated ncurses wrapper and fail-closed uninstall. |
| M16 SCP | **SUCCESS** | implementation/runtime contract proven (`36466679828`, `36467262213`), but `/usr/bin/scp` was removed from built-in rootfs for capacity. Current active image keeps ASUS Dropbear/core unchanged and does not contain SCP. Optional JFFS delivery under `/jffs/addons/merlin-tools` is proven by run `36863705618`; no startup hook or NVRAM change is installed. |
| M14 Enhanced CLI utility set | **SUCCESS** | NO generic port: run 36382597888 found no Merlin-only BusyBox symlink command missing from ASUS. Standalone donor ELFs map to separately tracked features (Nano, NFS, ipset, Tor, WireGuard, wsdd2); Merlin BusyBox remains forbidden |
| M11 Custom DDNS callback | **IN PROGRESS** | pinned source delta is now specified in `docs/custom-ddns-source-contract.md`: preserve ASUS DDNS/Inadyn, add separate `CUSTOM` provider, blocking custom `ddns-start`, async normal-provider hook, and `ddns_custom_updated` rc callback; dependency remains JFFS core engine |
| M10 JFFS backup/restore | **IN PROGRESS** | ASUS 52334 stock settings backup page exists, but the build lacks JFFS backup/upload routes/tokens in `httpd/uploader`; source backend required before exposing Merlin UI |
| JFFS core hook/config engine | **IN PROGRESS** | pinned source delta contract complete; requires later ASUS-compatible source build path for `rc`/shared/httpd integration |
| M08/M09 AMTM + Entware/addon integration | **IN PROGRESS** | run `36864039573` verifies/materializes the exact pinned AMTM donor blob (`283fa24c...`) without cloning or vendoring moving online modules. It remains DORMANT: activation still requires M01/M04 generic JFFS hooks; Entware remains M01-M03 dependent. |
| M36 IPv6 DNS Director parity | **IN PROGRESS** | ASUS 52334 already has IPv6 DNSFilter rule machinery (`DNSFILTERI/F`, DHCPv6 option 23) for supported modes, but lacks Merlin `dnsfilter_custom61/62/63` across rc/httpd/defaults; full custom-IPv6 parity requires source integration |
| M18/M19 Samba naming/Master Browser | **IN PROGRESS** | exact donor behavior and later-ASUS merge constraints are specified in `docs/samba-merlin-controls-source-contract.md`: M18 changes only unique share-section naming; M19 adds forced-master config/lifecycle semantics; current M20 WINS backend must remain authoritative |
| M20 WINS server | **SUCCESS** | UI-only ASUS-backed adaptation: `smbd_wins` exists in stock rc + libshared, generic `/start_apply.htm` form handling was proven, exact page patch result is SHA-locked, and guarded validation 36382734032 passes without M18/M19 or core-binary changes |
| M21 Windows discovery (`wsdd2`) | **IN PROGRESS / DORMANT FOUNDATION** | staging run `36467874419` + guarded overlay run `36468235793`: add-only `/usr/sbin/wsdd2` SHA-256 `89a4309c...`, ARM32 EABI5, exact stock loader/libc deps, QEMU load PASS, and no lifecycle/config reference. Full M21 still waits on M01-M03 generic JFFS reconcile hooks; no M21-specific ASUS `rc` patch |
| M31 Conntrack timeout tuning | **SUCCESS** | ASUS-backed UI adapter uses stock NVRAM keys and stock reboot apply path; no `rc` replacement |
| M34 Wireless Site Survey | **SUCCESS** | adapted page reuses stock `/apscan.asp` + `restart_wlcscan`; guarded validation run 36338372948 |
| M35 WiFi Insight / legacy WiFi Radar | **CANCELLED** | pinned Merlin 386.14_2 image contains only the launcher; visualization pages/assets and both Broadcom runtime daemons are absent, so there is no complete donor runtime to restore |
| M47 Traffic history persistence controls | **SUCCESS** | ASUS `rstats`/libshared backend verified and safe controls exposed in Other Settings |
| M48 per-IP traffic/cstats | **NO PORT** | pinned Merlin 386.14_2 deliberately excludes cstats on HND in build, rc lifecycle, firewall accounting, HTTPD handlers and installed device pages; RT-AC86U is HND. See `docs/per-ip-traffic-hnd-donor-classification.md` |
| M49 Global monthly traffic history | **SUCCESS** | implementation/backend contract proven in `36334016748`; built-in page/Chart.js optionalized for capacity. `docs/monthly-traffic-optional-delivery.md` defines JFFS/user-slot delivery; remaining delivery gate is real HTTPD EJ expansion of `bandwidth("monthly")` through a user slot. Current active image does not expose Monthly Traffic. |
| M59 Local OUI database | **SUCCESS** | local-OUI adaptation was proven in run 36336834393, but DB + three redirect patches were removed from built-in rootfs for capacity. Preserved as optional payload inventory; current active image retains ASUS remote OUI behavior. |\n| M69 WebUI diagnostics umbrella | **SUCCESS** | no separate port: constituent QR/OUI/log diagnostics work is already tracked under M53/M54/M58/M59 |
| M58 QR codes for WiFi/Guest Network | **SUCCESS** | add-only pinned QR library + exact multi-patches of ASUS Guest Network/router pages; validation run 36337583899 |
| M43 System Info page | **IN PROGRESS** | narrowed to a small read-only HTTPD/sysinfo backend (`cpu.model`, `cpu.freq`, `conn.max`, `nvram.total` plus only missing AJAX fields) followed by add-only page/AJAX/menu integration; see `docs/system-info-source-contract.md` |
| M46 QoS Stats / Classification page | **IN PROGRESS** | ASUS 52334 lacks `ajax_gettcdata.asp`, `get_ipv6clients_array`, `get_tcfilter_array`, `get_tcdata`/conntrack data handlers; source-side HTTPD/QoS integration required |
| M44 Other Settings page | **SUCCESS** | add-only page exposes only ASUS-backed conntrack, traffic-history persistence, and shell-timeout controls; unsupported Merlin-only settings are omitted |\n| M45 Temperature/performance page | **SUCCESS** | ASUS-native `/ajax_coretmp.asp` backend reused; guarded validation run 36338181498 |
| M51 Wireless ACL/client-name display | **SUCCESS** | NO PORT: ASUS 52334 already resolves/stores client names through its newer `clientList` model and ACL page logic; compatibility run 36373415595 |
| M52 Auto-refreshing wireless client list | **IN PROGRESS** | stock page + `wl_log.asp` exist, but Merlin's `ajax_wificlients.asp` endpoint depends on `get_wl_status`, absent from ASUS 52334 `httpd`; source-side HTTPD work required for full feature |
| M53 System/Wireless Log no-auto-logout | **SUCCESS** | two SHA-locked page-only patches validated by guarded overlay run 36369816037; no backend/core changes |
| M54 System Log enhancements | **SUCCESS** | safe UI-only subset implemented: local logFilter database + auto-refresh/filter controls; unsupported Merlin log-level backend controls deliberately excluded; guarded validation run 36370670710 |
| M55 Dual-radio WiFi icon | **SUCCESS** | ASUS hardware-switch logic preserved; no-switch on/partial/off fallback plus minimal partial-state CSS validated in run 36370439356 |\n| M56 Editable-entry WebUI enhancements | **SUCCESS** | NO PORT: run 36397818442 shows ASUS 52334 already provides edit flows on shared DHCP/port-forward and other pages; Merlin-only residual edit surfaces belong to separately gated NFS/OpenVPN/VPN Director work |
| M57 Advanced VPN Status | **IN PROGRESS** | narrowed to a small read-only VPN status backend (`pid`, tunnel IP, OpenVPN status-file data) plus add-only AJAX/page/menu; donor poll-side NVRAM writes and 5s sleep are rejected. See `docs/advanced-vpn-status-source-contract.md` |
| M24 Advanced OpenVPN integration | **IN PROGRESS** | runs 36398033834/36398402429: ASUS has a later native OpenVPN UI/lifecycle; Merlin-only client controls are not safe UI-only additions because their keys are not proven consumed by ASUS rc/libvpn. Keep stock UI and implement only separately proven source deltas (M38/M40) |
| M38 OpenVPN DNS Exclusive | **IN PROGRESS** | donor-contract verification run `36478506416` is green: port-53 NAT-chain setup/order/teardown plus dnsmasq coordination are pinned in `docs/openvpn-dns-exclusive-source-contract.md`; ASUS 52334 OpenVPN remains authoritative and policy mode must align with M40/VPN Director |
| M39 OpenVPN custom-option storage | **SUCCESS** | NO PORT: run 36384020800 confirms ASUS 52334 already stores OpenVPN material under `/jffs/openvpn` and provides a larger 15000-character `vpn_server_custom` field; preserve the newer ASUS storage model rather than graft Merlin `custom3` split storage |\n| M40 Merlin OpenVPN routing semantics | **IN PROGRESS** | run 36384020800: ASUS retains generic route primitives but lacks Merlin `ovpnc` policy tables, `vpn_client*_rgw/enforce`, and VPN Director routing integration; source-side integration required without replacing ASUS OpenVPN |\n
| Merlin feature port | **IN PROGRESS** | DNS Director + image-safe JFFS/addon + ASUS-backed Other Settings + monthly traffic + local OUI + WiFi QR implemented; no unsafe core binary replacement |
| Flashable firmware | **IN PROGRESS** | stock and active-overlay software repack gates are green (`36859123113`, `36858759179`) and feature-aware overlay validation is green (`36858785201`). Flashability remains blocked by deferred real ASUS-52334 hardware/runtime validation and any still-unimplemented source-backed feature contracts. |

## Status vocabulary

Only these project states are used:

- **SUCCESS**
- **FAILURE**
- **IN PROGRESS**
- **CANCELLED**

| M67 Speedtest VPN interface selector | **CANCELLED** | feature appears in later 3006 Merlin changelog; pinned 386.14_2 `internet_speed.html` has no VPN/interface selector, so it is outside this donor baseline |

| M68 Outbound LAN allowed logging | **IN PROGRESS** | source-delta verification run `36478040973` is green: clean ASUS 45956 vs pinned Merlin proves the same one-token `ACCEPT` → `logaccept` substitution at two equivalent single-/multi-WAN LAN default-allow call sites; later ASUS `rc` source still required |

| M66 Prevent Auto DoH / DDR / Private Relay | **IN PROGRESS** | run `36409047088` is green and proves ASUS 52334 has no `dns_priv_override` owner/UI/canaries; future source patch is definitively default + Auto/Yes/No UI + later-ASUS dnsmasq generator. Contract: `docs/prevent-auto-doh-source-contract.md` |

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

| M29 isolated local NTP daemon foundation | **SUCCESS / DORMANT FOUNDATION** | reproducible build run `36466577777`; guarded overlay run `36468186414`: add-only `/usr/libexec/rtac86u-ntpd`, static AArch64/no PT_INTERP, SHA-256 `6885069bb5ee26512b7f6903c08b3f28304f0b29e45bc7e810eeefe67276c6fb`, QEMU option-surface PASS, and no overlay startup/config reference. M29 feature remains IN PROGRESS until M01-M04 lifecycle/dnsmasq integration |


| ASUS 52334 stock event surfaces | **VERIFIED / LIMITED** | run `36415137373`: stock PPP scripts execute `/etc/ppp/ip-up.local` and `ip-down.local`, but no generic user lifecycle equivalent to M03 is proven; these are PPP-only supplemental callbacks. See `docs/asus-stock-event-surfaces-52334.md` |

| ASUS late-runtime lineage 51967→52294→52334 | **SUCCESS** | run `36570687943`, artifact digest `6cd8d988...`: 51967→52294 = 476 changed/2650 same/1 removed; 52294→52334 = 61 changed/3065 same/2 added. Of 142 protected paths, 137 changed in 51967→52294; only 9 changed in 52294→52334, including BusyBox, `rc`, `httpd`, `dnsmasq`, OpenVPN, `libshared`, `libcrypto` and `dhd.ko`. Confirms 52334 core/runtime authority and keeps K4 mandatory. See `docs/asus-runtime-lineage-51967-52294-52334.md` |

| Exact RT-AC86U GPL 386_51997 import boundary | **SUCCESS** | Git provenance pinned: general GPL import `28daa823...` (parent `bf59d7ec...`) and RT-AC86U SDK/blob import `c553d8e4...` (parent `2b13c8cc...`); critical source blob matrix and complete import diffs are CI-locked by `source-anchor-51997-import-boundary.yml`. See `docs/source-anchor-51997-import-boundary.md` |

| RT-AC86U 51997 optional-kernel build anchor | **SUCCESS / K1** | run `36531249746` on commit `fc60abc3...` passed exact source materialization, pinned GCC 5.3 smoke, original Asuswrt kernel-config macros, RT-AC86U target expansion and all M22/M23/M27/M32/M33 lineage assertions. Generated config SHA-256: `9b9c2f93e915ae2b81893839b66080a7d6a4efe5470ab8bed9e6084fea77aed2`. See `docs/kernel-build-lineage-51997.md` |
| RT-AC86U 51997 ipset module build | **SUCCESS / K2** | run `36556899650`, commit `2f423c2d...`: coherent 18-module ipset/xt_set family rebuilt from exact K1 lineage; ELF64 AArch64, vermagic `4.1.27 SMP preempt mod_unload aarch64`; artifact digest `66b79e48...`; no activation/overlay; K4 still required for ASUS 52334 runtime compatibility |

| RT-AC86U 51997 optional module family build | **SUCCESS / K3** | run `36561957525`, commit `fb0dc42e...`: NFS/SUNRPC/LOCKD, CIFS, Cake and WireGuard rebuilt from the exact K1 lineage; all ELF64/AArch64 with vermagic `4.1.27 SMP preempt mod_unload aarch64`; artifact digest `231f1902...`; no activation/overlay. K4 real-router validation is now the active gate. |

| RT-AC86U K4a read-only router preflight | **SUCCESS / DEFERRED HARDWARE GATE** | run `36562651589`: POSIX/safety/smoke CI passes for `scripts/k4-router-preflight.sh`; collector writes only to `/tmp` and contains no module load/unload, NVRAM/JFFS mutation, service restart, reboot or flash commands. User hardware currently runs Merlin 386.14_2, not ASUS 386_52334, so K4 runtime validation is deferred; do not treat Merlin-side loading as 52334 proof and do not require a stock reflash merely to advance development. |
| General runtime feature preflight | **READY / CI-VALIDATED** | `scripts/runtime-feature-preflight.sh` is read-only and writes only under `/tmp`; run `36876302545` validates POSIX syntax, forbids module/NVRAM/JFFS/service/network/reboot/flash mutation, and executes safely on CI. It will collect M07/JFFS/helper/httpd/rstats evidence when a 52334 runtime exists. |
| Candidate evidence skeleton | **READY / CI-VALIDATED** | `scripts/prepare-candidate-evidence.sh` accepts only `UNVALIDATED` candidate filenames, records the exact SHA-256 and creates the fail-closed K4/runtime/promotion checklist. Run `36924149359` validates syntax, mutation guard, positive path and rejection of an unmarked `.w`; it performs no flash/reboot/NVRAM/JFFS/module actions. |
