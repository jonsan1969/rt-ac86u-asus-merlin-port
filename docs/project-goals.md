# Project goals and technical policy

## Goal

Create a modern firmware for **ASUS RT-AC86U** using the latest official ASUS firmware for the model as the hardware/security baseline, then restore the relevant functionality from **Asuswrt-Merlin 386.14_2**.

The project is:

> **ASUS RT-AC86U 3.0.0.4.386_52334 → port the Merlin delta on top**

It is not:

- Merlin 386.14_2 with ASUS fixes backported one by one.
- A port of RT-AC86U to Merlin 3006.
- A community/homebrew fork used as the final codebase.

## Primary references

### ASUS baseline

**RT-AC86U 3.0.0.4.386_52334**

Use as primary reference for:

- RT-AC86U hardware support
- kernel
- Broadcom SDK
- Wi-Fi drivers
- proprietary ASUS/Broadcom components
- later ASUS security fixes
- model-specific changes

### Merlin donor

**Asuswrt-Merlin 386.14_2**

Use as donor/reference for Merlin functionality, not as the final technical baseline.

Pinned source commit:

`6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Conflict rule

When ASUS and Merlin differ:

1. Preserve the later ASUS implementation/fix.
2. Identify the exact Merlin behavior or patch that is required.
3. Port only that delta onto the latest usable ASUS implementation.

This rule is especially important for security-sensitive components such as:

- `httpd`
- `rc`
- `dnsmasq`
- OpenSSL
- VPN components
- AiCloud/WebDAV
- network and authentication code

## Merlin functionality to preserve where applicable

Examples include:

- JFFS scripts and `/jffs/scripts/`
- service-event hooks
- postconf/custom-config support
- Merlin SSH-related functionality
- VPN Director
- DNS Director where present in this Merlin generation
- advanced OpenVPN configuration
- Merlin WebUI pages
- custom user pages
- AMTM/addon friendliness
- Entware compatibility
- Merlin-specific settings and NVRAM integration
- other RT-AC86U functionality actually present in official 386.14_2

The objective is functional restoration, not merely a Merlin-looking UI.

## Security policy

Security takes precedence over reproducing historical behavior exactly.

- Preserve later ASUS security fixes.
- Do not blindly overwrite newer ASUS files with old Merlin files.
- Compare security-sensitive services before replacement or modification.
- Do not automatically reintroduce functionality that was removed for security reasons.

## Delta classification

### A. Pure additions

Merlin files/features ASUS does not have and that can be added without a core conflict.

### B. Merlin-patched open-source components

Port the relevant Merlin patch onto the ASUS-side component/version.

### C. Shared ASUS/Merlin core programs

Examples: `rc`, `httpd`.

Do **not** replace these with older Merlin binaries. Identify the Merlin changes at source level and port them to the latest usable ASUS base.

### D. Proprietary/model-specific components

Broadcom, Trend Micro, ASUS prebuilts and equivalent model-specific binaries.

Default rule: **retain the latest official ASUS 52334 version**.

## Source provenance

Ideal build chain:

1. latest buildable official ASUS AC86U 386 source
2. latest official ASUS 52334 model-specific components
3. Merlin delta from 386.14_2

If exact 52334 source is unavailable, documentation must clearly distinguish:

- the actual buildable source generation
- components taken directly from 52334
- Merlin patches layered on top

Never describe a build as “built from 52334 source” unless that source is genuinely available and used.

## Git strategy

- `main` — clean documented baseline
- `asus-52334-analysis` — firmware/source analysis and comparison
- `asus-52334-merlin-port` — actual feature port

Avoid experiment-branch sprawl.

## CI discipline

When debugging builds:

**change → Action → inspect result → analyze → next change**

Only one diagnostic run at a time where practical.

For failures:

1. identify the failed step
2. fetch the relevant log once
3. find the first real cause
4. fix that cause
5. rerun

## Flashability gate

A successful compile alone is not sufficient.

Before any image is considered flashable, verify at minimum:

- correct RT-AC86U model/header
- reasonable firmware size
- correct partition/UBI layout
- intended ASUS 52334 hardware components remain present
- intended ASUS Wi-Fi/drivers remain present
- WebUI starts
- SSH works
- JFFS works
- custom scripts work
- OpenVPN works
- VPN Director works
- DNS/DHCP works
- firewall/NAT works
- Merlin addon hooks remain present
- no obvious regression from ASUS 52334 has been introduced
