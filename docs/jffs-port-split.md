# JFFS/custom-script port split

This split is derived from the verified JFFS source-delta map and the existing port specification. It does not assume ASUS 52334 source availability.

## A. Image-safe/additive candidates

These may be investigated/implemented against the extracted ASUS 52334 image provided every change is guarded by exact preimage/change-set validation and does not replace a core binary.

| Candidate | Intended behavior | Gate before implementation |
|---|---|---|
| shell profile `/opt` PATH additions | expose `/opt/sbin`, `/opt/bin`, `/opt/usr/sbin`, `/opt/usr/bin` | identify exact ASUS 52334 profile asset and prove it is a non-core text asset |
| `/opt/etc/profile` sourcing | Entware environment integration | same profile-asset gate |
| `/jffs/configs/profile.add` sourcing | Merlin addon shell extension | must remain gated by `jffs2_scripts=1`; requires a trustworthy way to read the NVRAM flag from the profile asset |
| WebUI control for `jffs2_scripts` | Administration/System toggle | only if stock ASUS httpd/apply path already accepts/persists the variable without replacing `httpd` |
| static/additive UI text/assets | expose already-supported settings | exact stock preimage and no core replacement |

Directory creation under `/jffs` is **not** classified image-safe merely because directories are simple: persistent UBI/JFFS initialization is performed by core runtime code and must be integrated at the source-required layer unless stock ASUS already creates the required directories.

## B. Source-required candidates

These require compilation/integration into an ASUS-side source base and are blocked from image-first binary substitution:

- `run_custom_script()`
- `run_postconf()`
- `use_custom_config()`
- `append_custom_config()`
- `jffs2_scripts` default in `shared/defaults.c`
- UBI/JFFS creation of `/jffs/scripts`, `/jffs/configs`, `/jffs/addons`
- `init-start`
- `firewall-start`
- `services-start`
- `services-stop`
- `service-event`
- `service-event-end`
- `nat-start`
- `ddns-start`
- `wan-event`
- `wan-start`
- `qos-start`
- `dhcpc-event`
- `zcip-event`
- `pre-mount`
- `post-mount`
- `unmount`
- `update-notification`
- service-specific `.add`, replacement and `.postconf` integrations where the call must be inserted into an ASUS config generator.

## C. Immediate image-first probe

Before changing the active overlay, inspect the verified ASUS 52334 rootfs for:

1. the shell profile asset(s) and current `/opt` behavior;
2. existing `jffs2_scripts` strings in `httpd`, `rc`, defaults/runtime assets;
3. whether `/jffs/scripts`, `/jffs/configs`, or `/jffs/addons` are referenced/created anywhere in the stock image;
4. whether the Administration/System page already contains a hidden/disabled JFFS scripts control.

The probe must report evidence only. It must not infer source availability and must not modify ASUS core binaries.

## Decision rule

A candidate moves from probe to active overlay only when its complete runtime path is already supported by ASUS 52334 or can be added through a non-core text/image asset. Anything requiring a new call inside `rc`, `httpd`, kernel/HND or another protected core component remains source-required.
