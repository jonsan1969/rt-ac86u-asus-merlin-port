# Status

| Item | Status | Evidence |
|---|---|---|
| ASUS RT-AC86U 3.0.0.4.386_52334 baseline reference | **SUCCESS** | official ASUS support page + published SHA-256 |
| ASUS RT-AC86U 3.0.0.4.386_51955 comparison reference | **SUCCESS** | official ASUS support page + firmware-image SHA-256 verified in run 35987265109 |
| Merlin RT-AC86U 386.14_2 firmware reference | **SUCCESS** | official SourceForge file + published SHA-256 |
| Merlin 386.14_2 source revision | **SUCCESS** | exact tag/ref pinned to Git commit |
| ASUS 386_52334 GPL/source acquisition | **IN PROGRESS** | no matching public archive located; legacy `gpl@asus.com` request bounced with SMTP 550 #5.1.0; current support route deferred |
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
| Guarded Merlin overlay validation | **SUCCESS** | latest exact-change validation run 36373879103 passed; ASUS rc/httpd/dnsmasq/BusyBox/OpenVPN/Dropbear hashes unchanged |
| Merlin A/B/C/D implementation classification | **IN PROGRESS** | exact source patch boundaries continue per feature |
| JFFS image-safe subphase | **SUCCESS** | `/rom/etc/profile` exact patch, `/usr/sbin/helper.sh` add-only, 20 custom WebUI aliases add-only; no core binary replacement |
| M13 Nano editor | **SUCCESS** | verified Merlin nano 5.7 + isolated add-only `libncurses.so.6.0` runtime executes against ASUS 52334 under qemu; four add-only overlay targets validated in run 36373879103 |
| M11 Custom DDNS callback | **IN PROGRESS** | ASUS 52334 has normal DDNS but lacks `WWW.CUSTOM`, `ddns-start` and `ddns_custom_updated`; restore only with source-side DDNS/JFFS hook integration |
| M10 JFFS backup/restore | **IN PROGRESS** | ASUS 52334 stock settings backup page exists, but the build lacks JFFS backup/upload routes/tokens in `httpd/uploader`; source backend required before exposing Merlin UI |
| JFFS core hook/config engine | **IN PROGRESS** | pinned source delta contract complete; requires later ASUS-compatible source build path for `rc`/shared/httpd integration |
| AMTM integration | **IN PROGRESS** | stock has required curl/core shell tools but lacks `dos2unix`/`unix2dos`; defer until utility + core-hook prerequisites are satisfied |
| M36 IPv6 DNS Director parity | **IN PROGRESS** | ASUS 52334 already has IPv6 DNSFilter rule machinery (`DNSFILTERI/F`, DHCPv6 option 23) for supported modes, but lacks Merlin `dnsfilter_custom61/62/63` across rc/httpd/defaults; full custom-IPv6 parity requires source integration |
| M31 Conntrack timeout tuning | **SUCCESS** | ASUS-backed UI adapter uses stock NVRAM keys and stock reboot apply path; no `rc` replacement |
| M34 Wireless Site Survey | **SUCCESS** | adapted page reuses stock `/apscan.asp` + `restart_wlcscan`; guarded validation run 36338372948 |
| M35 WiFi Insight / legacy WiFi Radar | **CANCELLED** | pinned Merlin 386.14_2 image contains only the launcher; visualization pages/assets and both Broadcom runtime daemons are absent, so there is no complete donor runtime to restore |
| M47 Traffic history persistence controls | **SUCCESS** | ASUS `rstats`/libshared backend verified and safe controls exposed in Other Settings |
| M48 Per-IP traffic monitoring | **IN PROGRESS** | ASUS 52334 lacks `cstats`, `ipt_bandwidth`, cstats NVRAM/backend keys and all three device traffic pages; source-side daemon/HTTPD integration required |
| M49 Global monthly traffic history | **SUCCESS** | ASUS history spool contains monthly data; adapted Merlin page + add-only Chart.js validated in run 36334016748 |
| M59 Local OUI database | **SUCCESS** | verified Merlin OUI DB add-only; exactly three ASUS remote OUI lookups redirected locally; guarded validation run 36336834393 |
| M58 QR codes for WiFi/Guest Network | **SUCCESS** | add-only pinned QR library + exact multi-patches of ASUS Guest Network/router pages; validation run 36337583899 |
| M43 System Info page | **IN PROGRESS** | stock `httpd` has generic `sysinfo` dispatcher but lacks Merlin `cpu.model`, `cpu.freq`, `conn.max`, `nvram.total`; source-side HTTPD work required |
| M46 QoS Stats / Classification page | **IN PROGRESS** | ASUS 52334 lacks `ajax_gettcdata.asp`, `get_ipv6clients_array`, `get_tcfilter_array`, `get_tcdata`/conntrack data handlers; source-side HTTPD/QoS integration required |
| M45 Temperature/performance page | **SUCCESS** | ASUS-native `/ajax_coretmp.asp` backend reused; guarded validation run 36338181498 |
| M51 Wireless ACL/client-name display | **SUCCESS** | NO PORT: ASUS 52334 already resolves/stores client names through its newer `clientList` model and ACL page logic; compatibility run 36373415595 |
| M52 Auto-refreshing wireless client list | **IN PROGRESS** | stock page + `wl_log.asp` exist, but Merlin's `ajax_wificlients.asp` endpoint depends on `get_wl_status`, absent from ASUS 52334 `httpd`; source-side HTTPD work required for full feature |
| M53 System/Wireless Log no-auto-logout | **SUCCESS** | two SHA-locked page-only patches validated by guarded overlay run 36369816037; no backend/core changes |
| M54 System Log enhancements | **SUCCESS** | safe UI-only subset implemented: local logFilter database + auto-refresh/filter controls; unsupported Merlin log-level backend controls deliberately excluded; guarded validation run 36370670710 |
| M55 Dual-radio WiFi icon | **SUCCESS** | ASUS hardware-switch logic preserved; no-switch on/partial/off fallback plus minimal partial-state CSS validated in run 36370439356 |
| M57 Advanced VPN Status | **IN PROGRESS** | ASUS 52334 retains `ajax_ipsec.asp` but lacks `ajax_vpn_status.asp`, Merlin OpenVPN status globals and the expected vpn_client1/2 status-NVRAM contract; source-side HTTPD/OpenVPN status integration required |
| Merlin feature port | **IN PROGRESS** | DNS Director + image-safe JFFS/addon + ASUS-backed Other Settings + monthly traffic + local OUI + WiFi QR implemented; no unsafe core binary replacement |
| Flashable firmware | **IN PROGRESS** | no flashability claim until repack + hardware/runtime gates pass |

## Status vocabulary

Only these project states are used:

- **SUCCESS**
- **FAILURE**
- **IN PROGRESS**
- **CANCELLED**

| M67 Speedtest VPN interface selector | **CANCELLED** | feature appears in later 3006 Merlin changelog; pinned 386.14_2 `internet_speed.html` has no VPN/interface selector, so it is outside this donor baseline |
