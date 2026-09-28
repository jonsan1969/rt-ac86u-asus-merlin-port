# New-thread handoff

Updated: 2026-09-28

## Project sentence

**Take the latest official ASUS RT-AC86U 386_52334 firmware and make it Merlin again.**

The final architecture is ASUS-first, not Merlin-first.

## Working rule from the user

**Do not stop unless input from the user is genuinely required.**

When an Action finishes:
- green: inspect the result/artifact and immediately continue to the next concrete step;
- red: inspect logs, fix the real issue or classify the feature correctly, push the minimal change and continue;
- do not end a turn merely by saying what will be done next.

Ask the user only for information/decisions/access that cannot be resolved from the repo, firmware images, Actions, or established project rules.

## Non-negotiable technical rules

- Final runtime/hardware/security baseline: ASUS RT-AC86U `3.0.0.4.386_52334`.
- Merlin donor/reference: Asuswrt-Merlin `386.14_2`.
- Pinned Merlin source commit: `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`.
- Preserve later ASUS code, hardware support, proprietary/model-specific components and security changes.
- Never replace newer ASUS `rc`, `httpd`, `dnsmasq`, OpenVPN, Dropbear, BusyBox, OpenSSL, kernel/HND or proprietary components with older Merlin binaries just to regain a feature.
- For shared core components, identify the Merlin behavior/source delta and port it onto an ASUS-compatible source base later.
- Do not claim a build is “built from 52334 source” unless matching 52334 source is actually obtained and verified.
- Image-first work must be additive or exact/preimage-guarded. Fail closed on unexpected stock content.
- Do not write overlays through rootfs symlinks; target persistent canonical paths.
- Do not describe the project as flashable until repack + hardware/runtime gates pass.

## Repository

Repository: `jonsan1969/rt-ac86u-asus-merlin-port`

Implementation branch: `asus-52334-merlin-port`

Snapshot base HEAD before this handoff commit:

`154c77f00b6ff51db20baa107edaffc8b1806aed`

The branch contains all current implementation/probe work. Read these first in a new thread:

1. `docs/thread-handoff.md`
2. `STATUS.md`
3. `docs/merlin-feature-inventory.md`
4. `docs/source-base-strategy.md`
5. `docs/jffs-custom-script-port-plan.md`
6. `ports/active.json`

## Verified firmware artifacts

### ASUS 52334 — final baseline

- version: `3.0.0.4.386_52334`
- ZIP SHA-256: `e8fd0f3a26db4fe9cf6acb64272d2b78247eb9ccf3890fbdb8daace0bac10d61`
- image: `RT-AC86U_3.0.0.4_386_52334-gd500e53_ubi.w`
- image SHA-256: `1b4fe984e13afdf0a69c11bda759f3222822e12f5b8c929da33f334f2cc7483f`

### ASUS 51955 — temporal comparison reference

- version: `3.0.0.4.386_51955`
- image SHA-256: `af63aeb4ef335e2ebac521358103de451333b021ec82e59736854ae95a3424e0`
- role: isolate candidate Merlin changes from later ASUS changes; never use as final baseline.

### Merlin 386.14_2 — donor

- ZIP SHA-256: `1dedab53b08b93c529920c791291d04e36089a9c85d672a5a0fff9dea45bb49a`
- image: `RT-AC86U_386.14_2_ubi.w`
- image SHA-256: `ebe1491f8edb3f81ca4077d482ffca33d34ae7dfe245bbff7843684dbe9b7728`
- source pin: `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Three-way analysis

Verified classification:

- 1,992 all-identical paths
- 266 pure Merlin additions
- 1,513 strong Merlin-delta / ASUS-unchanged candidates
- 460 divergent shared changes
- 25 ASUS-later-change-only paths
- 1 ASUS-52334-only addition
- 1 both-added-differently path

Feature inventory is maintained in `docs/merlin-feature-inventory.md`.

## Source-base situation

Exact public ASUS `386_52334` source has still not been obtained.

Legacy `gpl@asus.com` bounced with SMTP 550. Late Merlin GPL merge commits are provenance references only, not clean ASUS source snapshots.

Therefore:
- image-safe/additive features can proceed now;
- features that require `rc/httpd/shared/defaults` changes are documented as source-required and must not be faked by transplanting old Merlin core binaries.

## Guarded overlay framework

Key files:

- `ports/active.json`
- `ports/files/`
- `tools/apply_port_overlay.py`
- `tools/check_port_overlay.py`
- `.github/workflows/validate-dns-director-overlay.yml`

Important safety behavior:
- exact stock preimage hashes where needed;
- exact replacement counts;
- add-only policy for new files;
- rootfs symlink traversal rejected;
- protected core hashes checked unchanged.

Latest active-overlay validation:

- run `36373879103` — **SUCCESS**
- ASUS `rc`, `httpd`, `dnsmasq`, BusyBox, OpenVPN and Dropbear remained unchanged.

## Implemented and green

The following are already implemented/validated. Do not redo them.

### DNS/JFFS/addon foundation
- DNS Director phase 1: adapted `DNSFilter.asp` + exact state.js enablement; ASUS backend retained.
- JFFS image-safe shell profile: exact `/rom/etc/profile` patch, including guarded `/jffs/configs/profile.add`.
- Merlin addon helper API: `/usr/sbin/helper.sh` add-only.
- 20 custom WebUI aliases add-only.
- overlay engine hardened against writes through rootfs symlinks.

### WebUI / diagnostics / traffic
- M31 Conntrack timeout tuning — ASUS-backed.
- M34 Wireless Site Survey — stock `/apscan.asp` + `restart_wlcscan`.
- M45 Temperature/performance page — stock `/ajax_coretmp.asp`.
- M47 Traffic history persistence controls.
- M49 Global monthly traffic history — ASUS rstats history spool + adapted page/Chart.js.
- M51 Wireless ACL client-name display — **NO PORT needed**; ASUS 52334 already has a newer equivalent.
- M53 System/Wireless Log no-auto-logout.
- M54 safe System Log enhancements — local filtering/auto-refresh only; unsupported Merlin log-level backend controls deliberately omitted.
- M55 dual-radio WiFi icon state — ASUS hardware-switch logic preserved; Merlin-style no-switch on/partial/off fallback added.
- M58 WiFi/Guest QR codes — add-only QR library + exact page patches.
- M59 local OUI database — local database + exactly three stock URL redirects.

### CLI
- M13 Nano — **SUCCESS**.
  - Merlin nano 5.7 staged as an isolated add-only bundle.
  - required `libncurses.so.6.0` included without replacing ASUS libraries.
  - qemu execution against ASUS rootfs passed.
  - active overlay validation run `36373879103` passed.

## Explicit NO PORT / CANCELLED decisions

- M35 WiFi Insight / legacy WiFi Radar — **CANCELLED**. Pinned Merlin 386.14_2 firmware contains only a stale launcher; visualization pages/assets and `vis-datacollector`/`vis-dcon` are absent even from the donor image.
- M51 Wireless ACL client-name enhancement — **NO PORT**. ASUS 52334 already has equivalent/newer behavior.
- M67 Speedtest VPN interface selector — **CANCELLED / outside donor baseline**. It appears in later 3006 Merlin, not pinned 386.14_2.

## Source-required / gated features already proven

Do not keep reproving these unless implementing their source contract.

- JFFS core custom-script/postconf engine — source-required in shared/rc/httpd.
- M10 JFFS backup/restore — stock settings-backup page exists, but ASUS 52334 has no JFFS backup/upload routes in httpd/uploader.
- M11 custom DDNS callback — normal DDNS exists, but `WWW.CUSTOM`, `ddns-start`, `ddns-started`, `ddns_custom_updated` are absent; run `36374538623`.
- M18 simpler SMB naming — `smbd_simpler_naming` absent in rc/httpd/libshared.
- M19 force SMB Master Browser — `smbd_master` absent in rc/httpd/libshared.
- M29/M30 local NTP server + NTP redirect — no ntpd/chronyd and no `ntpd_enable` / redirect/trust keys; run `36374675271`.
- M36 full IPv6 DNS Director custom resolver parity — ASUS has IPv6 DNSFilter machinery (`DNSFILTERI/F`, DHCPv6 option 23) but lacks Merlin `dnsfilter_custom61/62/63`; run `36374478421`.
- M43 full System Info — stock generic sysinfo exists but Merlin-specific cpu/conntrack/nvram fields require HTTPD work.
- M46 QoS Stats — missing Merlin AJAX/EJ tc/IPv6/conntrack data handlers.
- M48 per-IP traffic — missing `cstats`, `ipt_bandwidth`, cstats keys and device traffic pages.
- M52 wireless-client auto-refresh — stock log page exists but `get_wl_status`/Merlin AJAX endpoint is absent.
- M57 Advanced VPN Status — stock `ajax_ipsec.asp` exists, but `ajax_vpn_status.asp`, Merlin OpenVPN status globals and expected client status contract are absent.
- VPN Director remains deferred until the source-side routing/OpenVPN/JFFS integration path is defined.

## Partially reusable / next-image-safe candidates

These are better places to continue than repeatedly probing already-gated core features.

### M12 scheduled jobs / cru
- ASUS and Merlin both have `/usr/sbin/cru` shell scripts.
- ASUS uses a hand-rolled lock-file loop.
- Merlin's main delta uses fd-based `flock`.
- ASUS already ships `/usr/bin/flock -> ../../bin/busybox`.
- Do **not** transplant Merlin BusyBox/crond.
- Candidate: exact script-level adaptation of ASUS `cru`, but first make the flock runtime test unambiguous.

### M20 WINS
- ASUS `rc` and `libshared.so` contain `smbd_wins`.
- `httpd`/WebUI token was not found.
- This is worth a focused probe to determine whether generic ASUS form/NVRAM apply can expose the retained backend as an image-safe UI adaptation.
- Do not group it with M18/M19, which definitely need source backend work.

### M21 wsdd2
- ASUS Samba `smbd` and `nmbd` exist.
- `wsdd2` is absent.
- Only proceed if an isolated donor binary and all dependencies can be shown compatible with ASUS 52334.

### M14 enhanced CLI set
- Many Merlin command names are symlinks to Merlin BusyBox.
- Never add those symlinks unless the same applet is proven present in ASUS BusyBox.
- Stock Dropbear multicall does **not** expose SCP; run `36373784882`.
- Nano is already handled separately and is green.

## Samba probe details

Run `36374607127` — **SUCCESS classification probe**:

- `smbd_simpler_naming`: absent in rc/httpd/libshared.
- `smbd_master`: absent in rc/httpd/libshared.
- `smbd_wins`: present in rc + libshared, absent as explicit httpd token.
- ASUS has `/usr/sbin/smbd -> samba_multicall`.
- ASUS has `/usr/sbin/nmbd -> samba_multicall`.
- ASUS lacks `wsdd2`.

Overall probe classification was source-backend-required because only 1/3 Merlin control keys is retained, but M20 should be considered separately.

## NTP probe details

Run `36374675271` — **SUCCESS classification probe**:

- no `ntpd`;
- no `chronyd`;
- no `ntpd_enable`;
- no `ntpd_server_redir`;
- no `ntpd_server_trust`;
- no identified UDP/123 redirect contract.

Classification: `SOURCE_BACKEND_REQUIRED`.

## Recent important Actions

- `36373879103` — guarded active overlay incl. Nano — **SUCCESS**
- `36374021624` — QoS Stats backend probe — **SUCCESS classification**
- `36374147948` — per-IP traffic backend probe — **SUCCESS classification**
- `36374208783` — cru scheduler + stock flock comparison — **SUCCESS**
- `36374478421` — IPv6 DNS Director probe — **SUCCESS classification**
- `36374538623` — custom DDNS callback probe — **SUCCESS classification**
- `36374607127` — Samba controls probe — **SUCCESS classification**
- `36374675271` — local NTP server probe — **SUCCESS classification**

At this snapshot there are no known Actions that require user intervention.

## Immediate continuation in the next thread

1. Read this file + `STATUS.md` + `docs/merlin-feature-inventory.md`.
2. Check current branch HEAD and any Actions newer than this snapshot.
3. Continue automatically; do not ask permission.
4. Prefer unresolved image-safe/adapt candidates before source-required features.
5. Best immediate candidates:
   - make M12 `cru` flock semantics test definitive, then exact-patch only if justified;
   - isolate M20 WINS as a possible ASUS-backed UI adaptation;
   - probe M21 `wsdd2` as a standalone dependency-safe binary only if M20 does not produce a safe port;
   - continue remaining inventory rows for more A/B image-safe candidates.
6. For every implementation, rerun guarded overlay validation and require protected ASUS core hashes unchanged.
7. Source-required features should accumulate precise source contracts, not binary transplants.
8. Flashable firmware remains **IN PROGRESS**; repack/hardware validation is a later gate.
