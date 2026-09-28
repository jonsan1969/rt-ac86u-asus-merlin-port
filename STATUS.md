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
| M16 Merlin SSH behavior / SCP | **IN PROGRESS** | run 36382880359: basic ASUS SSH/key NVRAM + host-key signatures overlap Merlin, but Merlin `scp` is only a symlink to Merlin's older `dropbearmulti`; ASUS has no `scp`. Do not transplant Dropbear; SCP requires an ASUS-compatible source/build path if pursued |
| M14 Enhanced CLI utility set | **SUCCESS** | NO generic port: run 36382597888 found no Merlin-only BusyBox symlink command missing from ASUS. Standalone donor ELFs map to separately tracked features (Nano, NFS, ipset, Tor, WireGuard, wsdd2); Merlin BusyBox remains forbidden |
| M11 Custom DDNS callback | **IN PROGRESS** | pinned source delta is now specified in `docs/custom-ddns-source-contract.md`: preserve ASUS DDNS/Inadyn, add separate `CUSTOM` provider, blocking custom `ddns-start`, async normal-provider hook, and `ddns_custom_updated` rc callback; dependency remains JFFS core engine |
| M10 JFFS backup/restore | **IN PROGRESS** | ASUS 52334 stock settings backup page exists, but the build lacks JFFS backup/upload routes/tokens in `httpd/uploader`; source backend required before exposing Merlin UI |
| JFFS core hook/config engine | **IN PROGRESS** | pinned source delta contract complete; requires later ASUS-compatible source build path for `rc`/shared/httpd integration |
| M08/M09 AMTM + Entware/addon integration | **IN PROGRESS** | run 36382931979: Merlin `amtm` is a standalone shell script and both images expose `/opt -> tmp/opt`, but AMTM/addons depend on `/jffs` conventions while ASUS `rc` lacks Merlin `services-start`/`post-mount` hooks; defer until JFFS source hooks are integrated rather than expose a partial ecosystem |
| M36 IPv6 DNS Director parity | **IN PROGRESS** | ASUS 52334 already has IPv6 DNSFilter rule machinery (`DNSFILTERI/F`, DHCPv6 option 23) for supported modes, but lacks Merlin `dnsfilter_custom61/62/63` across rc/httpd/defaults; full custom-IPv6 parity requires source integration |
| M18/M19 Samba naming/Master Browser | **IN PROGRESS** | exact donor behavior and later-ASUS merge constraints are specified in `docs/samba-merlin-controls-source-contract.md`: M18 changes only unique share-section naming; M19 adds forced-master config/lifecycle semantics; current M20 WINS backend must remain authoritative |
| M20 WINS server | **SUCCESS** | UI-only ASUS-backed adaptation: `smbd_wins` exists in stock rc + libshared, generic `/start_apply.htm` form handling was proven, exact page patch result is SHA-locked, and guarded validation 36382734032 passes without M18/M19 or core-binary changes |
| M21 Windows discovery (`wsdd2`) | **IN PROGRESS** | run 36382208517: Merlin `wsdd2` donor ELF is dependency-compatible with ASUS 52334, but ASUS `rc` has no `wsdd2` lifecycle while Merlin `rc` does; source-side start/stop integration is required, so no binary-only overlay |
| M29/M30 Local NTP server + client-NTP redirect | **IN PROGRESS** | run 36374675271: no ntpd/chronyd and no `ntpd_enable`, `ntpd_server_redir`, or `ntpd_server_trust`; source/runtime integration required |
| M31 Conntrack timeout tuning | **SUCCESS** | ASUS-backed UI adapter uses stock NVRAM keys and stock reboot apply path; no `rc` replacement |
| M34 Wireless Site Survey | **SUCCESS** | adapted page reuses stock `/apscan.asp` + `restart_wlcscan`; guarded validation run 36338372948 |
| M35 WiFi Insight / legacy WiFi Radar | **CANCELLED** | pinned Merlin 386.14_2 image contains only the launcher; visualization pages/assets and both Broadcom runtime daemons are absent, so there is no complete donor runtime to restore |
| M47 Traffic history persistence controls | **SUCCESS** | ASUS `rstats`/libshared backend verified and safe controls exposed in Other Settings |
| M48 Per-IP traffic monitoring | **IN PROGRESS** | ASUS 52334 lacks `cstats`, `ipt_bandwidth`, cstats NVRAM/backend keys and all three device traffic pages; source-side daemon/HTTPD integration required |
| M49 Global monthly traffic history | **SUCCESS** | ASUS history spool contains monthly data; adapted Merlin page + add-only Chart.js validated in run 36334016748 |
| M59 Local OUI database | **SUCCESS** | verified Merlin OUI DB add-only; exactly three ASUS remote OUI lookups redirected locally; guarded validation run 36336834393 |\n| M69 WebUI diagnostics umbrella | **SUCCESS** | no separate port: constituent QR/OUI/log diagnostics work is already tracked under M53/M54/M58/M59 |
| M58 QR codes for WiFi/Guest Network | **SUCCESS** | add-only pinned QR library + exact multi-patches of ASUS Guest Network/router pages; validation run 36337583899 |
| M43 System Info page | **IN PROGRESS** | stock `httpd` has generic `sysinfo` dispatcher but lacks Merlin `cpu.model`, `cpu.freq`, `conn.max`, `nvram.total`; source-side HTTPD work required |
| M46 QoS Stats / Classification page | **IN PROGRESS** | ASUS 52334 lacks `ajax_gettcdata.asp`, `get_ipv6clients_array`, `get_tcfilter_array`, `get_tcdata`/conntrack data handlers; source-side HTTPD/QoS integration required |
| M44 Other Settings page | **SUCCESS** | add-only page exposes only ASUS-backed conntrack, traffic-history persistence, and shell-timeout controls; unsupported Merlin-only settings are omitted |\n| M45 Temperature/performance page | **SUCCESS** | ASUS-native `/ajax_coretmp.asp` backend reused; guarded validation run 36338181498 |
| M51 Wireless ACL/client-name display | **SUCCESS** | NO PORT: ASUS 52334 already resolves/stores client names through its newer `clientList` model and ACL page logic; compatibility run 36373415595 |
| M52 Auto-refreshing wireless client list | **IN PROGRESS** | stock page + `wl_log.asp` exist, but Merlin's `ajax_wificlients.asp` endpoint depends on `get_wl_status`, absent from ASUS 52334 `httpd`; source-side HTTPD work required for full feature |
| M53 System/Wireless Log no-auto-logout | **SUCCESS** | two SHA-locked page-only patches validated by guarded overlay run 36369816037; no backend/core changes |
| M54 System Log enhancements | **SUCCESS** | safe UI-only subset implemented: local logFilter database + auto-refresh/filter controls; unsupported Merlin log-level backend controls deliberately excluded; guarded validation run 36370670710 |
| M55 Dual-radio WiFi icon | **SUCCESS** | ASUS hardware-switch logic preserved; no-switch on/partial/off fallback plus minimal partial-state CSS validated in run 36370439356 |\n| M56 Editable-entry WebUI enhancements | **SUCCESS** | NO PORT: run 36397818442 shows ASUS 52334 already provides edit flows on shared DHCP/port-forward and other pages; Merlin-only residual edit surfaces belong to separately gated NFS/OpenVPN/VPN Director work |
| M57 Advanced VPN Status | **IN PROGRESS** | ASUS 52334 retains `ajax_ipsec.asp` but lacks `ajax_vpn_status.asp`, Merlin OpenVPN status globals and the expected vpn_client1/2 status-NVRAM contract; source-side HTTPD/OpenVPN status integration required |\n| M24 Advanced OpenVPN integration | **IN PROGRESS** | runs 36398033834/36398402429: ASUS has a later native OpenVPN UI/lifecycle; Merlin-only client controls are not safe UI-only additions because their keys are not proven consumed by ASUS rc/libvpn. Keep stock UI and implement only separately proven source deltas (M38/M40) |
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
