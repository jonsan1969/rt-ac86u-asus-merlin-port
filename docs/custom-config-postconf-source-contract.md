# JFFS custom-config and postconf source integration contract

Date: 2026-09-28  
Feature inventory ID: M04  
Dependencies: M01 helper exposure + `jffs2_scripts` enable contract  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Clean ASUS source anchor: 386.45956 @ `a9179fc9329565dea0f7c5c7648fe8ad49ceaaf6`  
Late structural reference: Merlin 386.12_x @ `5b47ec64ce58d23c591e809d4cbad09d1121c4ea`  
Behavior donor: Merlin 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Purpose

Restore Merlin's custom configuration framework without replacing ASUS configuration generators or core binaries.

The framework has three operations:

- append `/jffs/configs/<config>.add` to an ASUS-generated file;
- replace the generated file with `/jffs/configs/<config>`;
- run `/jffs/scripts/<name>.postconf <target>` after generation.

The helper implementation itself already exists unchanged in the clean ASUS source lineage. The source port is primarily about exposing it and adding reviewed generator call sites.

## Helper semantics

### `append_custom_config(config, fp)`

Target addon file:

`/jffs/configs/<config>.add`

Behavior:

1. do nothing when the addon file does not exist;
2. when `jffs2_scripts=0`, log that custom configs are disabled and do not append;
3. otherwise append the file contents to the already-open generated config stream.

The append therefore occurs **before the generator closes the file**.

### `use_custom_config(config, target)`

Replacement file:

`/jffs/configs/<config>`

Behavior:

1. do nothing when the replacement does not exist;
2. when `jffs2_scripts=0`, log and leave the ASUS-generated target untouched;
3. otherwise copy the replacement over the target.

This is a full replacement, not a merge.

### `run_postconf(name, config)`

Script:

`/jffs/scripts/<name>.postconf`

Invocation:

`<name>.postconf <config-path>`

The donor delegates to:

`run_custom_script(..., 120, config, NULL)`

so postconf is **blocking and bounded to 120 seconds**.

It inherits the normal custom-script checks:

- `jffs2_scripts` must be enabled;
- script file must exist;
- script must have an executable bit.

## Required ordering

For generated service configs, the normal donor order is:

1. ASUS generator writes its normal configuration;
2. `append_custom_config()` while the output stream is still open;
3. close the generated file;
4. `use_custom_config()` to optionally replace the whole file;
5. `run_postconf()` to allow a final scripted edit;
6. apply final permissions;
7. launch/reload the service.

This ordering is part of the API contract.

Do not run postconf before a full custom-config replacement.  
Do not apply `.add` after the full replacement.

## Priority integration targets for RT-AC86U

The full donor has many generator integrations. The source port should be staged so high-value/current ASUS services are handled first.

### Tier 1 — addon/core-service value

| Config key | Target | Donor area | Required sequence |
|---|---|---|---|
| `hosts` | `/etc/hosts` | `rc/services.c` | append → replace → `hosts.postconf` → chmod |
| `dnsmasq.conf` | `/etc/dnsmasq.conf` | `rc/services.c` | append → replace → `dnsmasq.postconf` → chmod |
| `inadyn.conf` | `/etc/inadyn.conf` | `rc/services.c` | append → replace → `inadyn.postconf` |
| `smb.conf` | current Samba config path | `libdisk/write_smb_conf.c` | append → replace → `smb.postconf` → chmod |
| `vsftpd.conf` | `/etc/vsftpd.conf` | `rc/usb.c` | append → replace → `vsftpd.postconf` |
| media-server config | current `/etc/<media-server>.conf` | `rc/usb.c` | append → replace → service-named postconf |
| `igmpproxy.conf` | current igmpproxy path | `rc/wan.c` | append → replace → `igmpproxy.postconf` |

These provide most of the practical addon/config extensibility without requiring optional Merlin-only daemons.

### Tier 2 — ASUS-supported optional services

Port only when the corresponding later ASUS service still exists and the final target path is verified:

- `stubby.yml` + `stubby.postconf`;
- UPnP config + `upnp.postconf`;
- multicast/MCPD config;
- Avahi service/config files;
- password/group/shadow postconf hooks;
- OpenVPN client/server postconf;
- PPTP config where still relevant.

### Tier 3 — feature-gated ports

Do not add generator hooks solely for a feature that is not otherwise being ported:

- Tor;
- NFS exports;
- Zebra/RIP;
- SNMP;
- WireGuard;
- other donor-only services.

Those hooks belong to their owning feature block.

## Identity/account files

Pinned donor also allows post-generation edits of files such as:

- `/etc/shadow`;
- `/etc/gshadow`;
- `/etc/passwd`;
- `/etc/group`.

These are security-sensitive.

They must be reviewed separately against later ASUS account-generation logic and permissions before enabling. The existence of the donor hook does not justify copying the old generator wholesale.

## OpenVPN postconf

Pinned donor runs:

- `openvpnclientN.postconf /etc/openvpn/clientN/config.ovpn`;
- `openvpnserverN.postconf /etc/openvpn/serverN/config.ovpn`.

This is postconf-only in the pinned donor code path.

Because ASUS 52334 has a newer OpenVPN implementation, integrate only if the current ASUS config generation point and file ownership are confirmed. Never replace the later ASUS OpenVPN control stack to gain this hook.

## Relationship to image-safe `helper.sh`

The image-safe addon helper already delivered in this project provides shell-side postconf helpers for addons.

That does **not** make M04 complete.

The firmware generators still need to call the source-side framework so an addon can actually intercept a regenerated stock config at the correct lifecycle point.

## Relationship to M01-M03

M04 shares the helper implementation and `jffs2_scripts` gate with M01, but its generator hooks are independently reviewable.

A source build may stage M04 progressively:

1. expose helper + default;
2. integrate Tier-1 config generators;
3. validate;
4. then add lifecycle event hooks M02/M03 and lower-priority generator targets.

This reduces the amount of core control flow changed in one step.

## Validation gate

For every integrated config target prove:

1. with `jffs2_scripts=0`, generated output is stock ASUS;
2. with no files in `/jffs/configs`, generated output is stock ASUS;
3. `<config>.add` appends after ASUS-generated content;
4. `<config>` fully replaces the generated file;
5. when both replacement and `.add` exist, the full replacement wins because it happens after append;
6. `<name>.postconf` runs after replacement and sees the final target path as argv[1];
7. postconf execution is bounded to 120 seconds;
8. non-executable postconf is rejected;
9. final file mode/ownership remains appropriate for the service;
10. service startup/reload still occurs in later ASUS order;
11. no stale temporary/generated file survives a failed regeneration;
12. protected ASUS behavior is unchanged when the framework is unused.

## Current classification

**SOURCE-REQUIRED — PER-GENERATOR PORT**

The helper primitive is already inherited from ASUS source lineage. M04 should be integrated as small call-site deltas in current ASUS generators, not as a donor-file transplant.
