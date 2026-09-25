# New-thread handoff

Updated: 2026-09-25

## Project sentence

**Take the latest official ASUS RT-AC86U 386_52334 firmware and make it Merlin again.**

The final architecture is ASUS-first, not Merlin-first.

## Non-negotiable rules

- Final runtime/hardware/security baseline: ASUS RT-AC86U `3.0.0.4.386_52334`.
- Merlin donor/reference: Asuswrt-Merlin `386.14_2`.
- Pinned Merlin source commit: `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`.
- Preserve later ASUS code, hardware support, proprietary/model-specific components and security changes.
- Never replace newer ASUS `rc`, `httpd`, `dnsmasq`, OpenVPN, Dropbear, BusyBox, OpenSSL or kernel/HND components with older Merlin binaries just to regain a feature.
- For shared core components, identify and port the Merlin source/behavior delta onto the latest ASUS-side implementation that can be established.
- Do not claim a build is “built from 52334 source” unless corresponding 52334 source is actually obtained and verified.

## Repository

Repository: `jonsan1969/rt-ac86u-asus-merlin-port`

Branches:

- `main` — documented stable baseline
- `asus-52334-analysis` — firmware/source comparison and feature classification
- `asus-52334-merlin-port` — implementation/overlay work

At handoff:

- analysis branch before this handoff commit: `8fc456fd153706b894d95fcde4f850b53fbd5d8b`
- port branch before this handoff commit: `d3bba607d0aca6150c1dad2b14e805c8764fd6e8`

## Verified firmware artifacts

### ASUS 52334 — final baseline

- version: `3.0.0.4.386_52334`
- release date: 2026-05-07
- ZIP SHA-256:
  `e8fd0f3a26db4fe9cf6acb64272d2b78247eb9ccf3890fbdb8daace0bac10d61`
- image:
  `RT-AC86U_3.0.0.4_386_52334-gd500e53_ubi.w`
- image SHA-256:
  `1b4fe984e13afdf0a69c11bda759f3222822e12f5b8c929da33f334f2cc7483f`

### ASUS 51955 — temporal comparison reference

- version: `3.0.0.4.386_51955`
- release date: 2024-11-08
- ASUS-published SHA-256 applies to the **unzipped .w image**:
  `af63aeb4ef335e2ebac521358103de451333b021ec82e59736854ae95a3424e0`
- role: isolate Merlin delta from later ASUS changes; it is not the final firmware baseline.

### Merlin 386.14_2 — donor

- release date: 2024-11-17
- ZIP SHA-256:
  `1dedab53b08b93c529920c791291d04e36089a9c85d672a5a0fff9dea45bb49a`
- image:
  `RT-AC86U_386.14_2_ubi.w`
- image SHA-256:
  `ebe1491f8edb3f81ca4077d482ffca33d34ae7dfe245bbff7843684dbe9b7728`

## Three-way analysis

The useful model is:

```text
ASUS 386_51955 ──────┬──────> Merlin 386.14_2
                     │          isolate candidate Merlin delta
                     │
                     └──────> ASUS 386_52334
                                identify later ASUS changes
```

Then implementation remains:

```text
ASUS 386_52334
+ selected source-reviewed Merlin functionality
= project firmware
```

Verified three-way results:

- `ALL_IDENTICAL`: 1,992
- `MERLIN_ONLY_PURE_ADDITION`: 266
- `MERLIN_DELTA_ASUS_UNCHANGED`: 1,513
- `BOTH_CHANGED_DIVERGENT`: 460
- `ASUS_LATER_CHANGE_ONLY`: 25
- `ASUS_52334_ONLY_ADDITION`: 1
- `BOTH_ADDED_DIFFERENTLY`: 1

The original direct 52334-vs-Merlin comparison had 1,939 same-path/different-content entries. The three-way model reduces the genuinely ambiguous shared-change set to 460 paths.

See `docs/three-way-firmware-analysis.md`.

## Merlin feature inventory

Feature-level inventory is **SUCCESS**.

The master inventory is:

`docs/merlin-feature-inventory.md`

Major identified Merlin functionality includes:

- JFFS custom scripts under `/jffs/scripts/`
- `init-start`, `services-start/stop`, `service-event`, `service-event-end`, `wan-start`, `wan-event`, `nat-start`, `firewall-start`, USB/QoS/update hooks
- postconf/custom-config framework
- VPN Director
- DNS Director/DNSFilter UI and enhanced behavior
- advanced OpenVPN integration
- custom WebUI pages/user slots
- AMTM/addon integration
- Entware/`/opt` friendliness
- SSH/Dropbear enhancements
- SMB simpler naming, Master Browser and WINS options
- NTP daemon/redirection
- conntrack tuning
- traffic-history/storage options
- NFS/CIFS additions
- ipset/Cake/WireGuard and other rebuildable open-source additions
- various Merlin tools/pages such as System Info, Other Settings, Site Survey and QoS-related UI

The compatibility probe also showed that several backends already exist in ASUS 52334. Do not port duplicate backends blindly.

See `docs/merlin-feature-compatibility-probe.md`.

## ASUS GPL/source situation

Exact public ASUS `386_52334` corresponding source has not been located.

A direct request to legacy `gpl@asus.com` bounced with SMTP:

`550 #5.1.0 Address rejected`

Current ASUS support-account route was deferred.

Important late-Merlin provenance:

- `e9e6035c85c673701646f2cf15de09b01a997ab9` — “Merge with GPL 386_52796”
- `75c9d789179e169de5b2da2c02031358d5d03566` — “Merge with GPL 386_52805”
- `47bbd79560ec3f03f12537cce8fea81766e9f47d` — AC86U SDK/binary refresh from 386_52796

These are **not clean ASUS source snapshots**. Merlin code already exists across those merge points, so they are provenance references only.

See `docs/asus-gpl-provenance.md` and `docs/source-base-strategy.md`.

## JFFS/custom-script work

The JFFS source-delta map Action `35990042520` completed **SUCCESS**.

The port specification is in:

`docs/jffs-custom-script-port-plan.md`

Key implementation areas:

- `shared/scripts.c`
- declarations/defaults
- `rc/services.c`
- `rc/init.c`
- `rc/firewall.c`
- `rc/wan.c`
- `rc/usb.c`
- JFFS/UBIFS setup
- other individual hook call sites

No old Merlin `rc` binary is to be transplanted.

## Current implementation: DNS Director phase 1

A guarded image-first overlay framework exists on `asus-52334-merlin-port`.

Key files:

- `ports/active.json`
- `ports/files/DNSFilter.asp`
- `tools/apply_port_overlay.py`
- `tools/check_port_overlay.py`
- `.github/workflows/validate-dns-director-overlay.yml`
- `docs/dns-director-phase1-port.md`

ASUS 52334 runtime mapping established:

- stock backend has `dnsfilter_enable_x`
- stock backend has `dnsfilter_mode`
- stock backend has `dnsfilter_custom1..3`
- stock backend has `dnsfilter_rulelist`
- stock `rc` contains DNSFilter firewall/dnsmasq integration
- stock `httpd` contains `dnsfilter_modes_list`
- stock menu has a `DNSFilter.asp` reference
- stock firmware does **not** ship `/www/DNSFilter.asp`
- stock `state.js` computes `isSupport("dnsfilter")` and then explicitly forces `dnsfilter_support = false`

Phase 1 intentionally does not add Merlin-only:

- `dnsfilter_rulelist1..5`
- `dnsfilter_custom61..63`
- `restart_dnsfilter`
- expanded HND rule storage/full IPv6 behavior

Instead it aims to:

- add an adapted `DNSFilter.asp`
- keep ASUS 52334 `rc`, `httpd`, `dnsmasq`
- use stock `restart_dnsmasq;restart_firewall`
- retain stock one-field rule storage
- patch only the forced-false UI line using an exact, preimage-hash-guarded text patch

## Exact current failure to fix next

Latest port branch:

`d3bba607d0aca6150c1dad2b14e805c8764fd6e8`

Validation Action:

- run: `36000073528`
- workflow: `Validate DNS Director overlay`
- result: **FAILURE**

All prior steps succeeded:

- manifest validation
- extraction-tool install
- verified ASUS 52334 download
- pinned Merlin-source fetch
- ASUS rootfs extraction
- pre-overlay inventory

Failure occurred only at **Apply guarded overlay**:

```text
entry 2: expected 1 exact match(es), found 0
```

The manifest entry for the `state.js` text replacement currently encodes the search separator as a literal escaped `\\n` sequence rather than matching the actual newline in the stock file.

The next change should be **only** to correct that exact preimage match representation, then rerun the same validation workflow once.

Do not weaken the preimage SHA-256 guard or replacement-count guard just to make the run pass.

Current stock `state.js` preimage SHA-256 pinned in the manifest:

`bce58d27bcfdaeff9fdb216a5eb0f8fd944b5618058c1d38ef7b3cb8452e5d61`

Current adapted `DNSFilter.asp` manifest SHA-256:

`bb032b3cbe8a7e197a710213e8bf440564b03b82c79358a7fd253b79bb05b545`

## Immediate next steps

1. On `asus-52334-merlin-port`, fix only the exact `state.js` search string/newline representation in `ports/active.json`.
2. Trigger/observe a single `Validate DNS Director overlay` run.
3. If it reaches the exact-change verification step, inspect that report before any further change.
4. Require unchanged hashes for protected core binaries and unchanged `menuTree.js`.
5. If automated overlay/integrity validation becomes **SUCCESS**, keep DNS Director phase 1 marked implementation-success but hardware-validation-pending.
6. Then return to the JFFS/custom-script source-level port. JFFS is foundational for AMTM, addons, postconf and service hooks.
7. Do not start VPN Director until the `libovpn/httpd/rc` source reconciliation is sufficiently defined.

## Important Actions

- `35982703376` — firmware artifact verification — **SUCCESS**
- `35982848587` — ASUS 52334 vs Merlin extraction/diff — **SUCCESS**
- `35987265109` — three-way firmware analysis — **SUCCESS**
- `35989225935` — Merlin feature compatibility probe — **SUCCESS**
- `35990042520` — JFFS custom-script source delta map — **SUCCESS**
- `35993309478` — ASUS 52334 DNSFilter runtime map — **SUCCESS**
- `36000073528` — DNS Director overlay validation — **FAILURE** at exact text patch match

## Flashability status

**IN PROGRESS.**

No firmware should be described as flashable yet.

Successful compile/repack alone is not enough. Final validation must cover model/header, size/layout, retained ASUS 52334 hardware components, WebUI, SSH, JFFS/custom scripts, DNS/DHCP, NAT/firewall, OpenVPN/VPN Director, addons and regression checks.
