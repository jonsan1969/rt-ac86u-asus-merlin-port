# JFFS/custom-script source integration contract

Date: 2026-09-26

## Purpose

This document is the source-level contract for restoring Merlin's JFFS custom-script/config framework without replacing ASUS 52334 core binaries.

The final runtime baseline remains official ASUS RT-AC86U 3.0.0.4.386_52334. Asuswrt-Merlin 386.14_2 at commit `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b` is only the behavioral/source donor.

This is deliberately **not** described as a patch against ASUS 52334 source because the project does not have that source.

## Image-first pieces already isolated

The verified ASUS 52334 image allows these pieces without replacing a core binary:

- exact patch of `/rom/etc/profile` to source `/jffs/configs/profile.add` only when `jffs2_scripts=1`;
- add-only `/usr/sbin/helper.sh` from the pinned Merlin donor;
- add-only custom WebUI aliases `/www/user1.asp` through `/www/user20.asp`, targeting the stock `/www/user -> /var/wwwext` runtime namespace;
- stock `/opt -> /tmp/opt` and the stock HND profile already provide the Entware-style PATH and `/opt/etc/profile` sourcing.

The guarded overlay engine rejects writes through rootfs symlinks, so persistent files must be addressed by their canonical image path.

## Stock ASUS 52334 runtime facts

Targeted image probes established:

- JFFS mount/format support is present: `jffs2_on`, `jffs2_format`, `jffs2_clean_fs`, and JFFS mount strings are present in stock `rc`.
- The stock image has no `jffs2_exec` signature and no `/jffs/.asusrouter` signature.
- Stock `rc` does contain generic `.asusrouter` strings in the ASUS Apps/USB autorun namespace (for example `%s/%s/.asusrouter`), so those strings are not evidence of a JFFS autorun path.
- The principal Merlin lifecycle signatures are absent from stock `rc`; the generic string `firewall-start` exists but is not proof of Merlin's custom-script engine.
- `/www/user` already points to `/var/wwwext` at runtime.
- `/usr/sbin/helper.sh` and `/jffs/addons` are absent in stock.
- BusyBox already supplies the commands used by Merlin's helper API: `sed`, `grep`, `cut`, `md5sum`, and `touch`.

Therefore there is no hidden stock primitive that can substitute for the missing Merlin hook engine.

## Core helper API that must be source-integrated

From pinned Merlin `release/src/router/shared/scripts.c`:

- `run_custom_script(name, timeout, arg1, arg2)`
  - resolves `/jffs/scripts/<name>`;
  - does nothing if the script is absent;
  - blocks execution when `jffs2_scripts=0`;
  - rejects scripts without an executable bit;
  - logs invocation and optional arguments;
  - uses blocking or asynchronous execution according to `timeout`.
- `run_postconf(name, config)`
  - maps a generated config to `<name>.postconf` and invokes it with the generated config path.
- `use_custom_config(config, target)`
  - replaces a generated target with `/jffs/configs/<config>` when enabled.
- `append_custom_config(config, fp)`
  - appends `/jffs/configs/<config>.add` to the generated config when enabled.
The corresponding declarations for the four helper functions belong in the shared header used by rebuilt core components.

## Mount-time integration

Pinned Merlin `386.14_2` does **not** use the later `setup_jffs_dirs()` helper.  In this donor generation the mount implementations create the directories inline after the persistent filesystem is loaded:

- `rc/ubifs.c`: create `/jffs/scripts`, `/jffs/configs`, and `/jffs/addons` with mode 0755 after `userfs_prepare()` and the Loaded/Formatted notice;
- `rc/jffs2.c`: the same three directory creations after successful JFFS setup.

Both pinned donor files still contain the older ASUS `.asusrouter` / `jffs2_exec` or `ubifs_exec` autoexec block, but it is wrapped in `#if 0 /* disable legacy & asus autoexec */` and therefore is deliberately **not** part of Merlin's active custom-script mechanism.

For RT-AC86U/HND, directory creation must be inserted only after the ASUS-side persistent filesystem is successfully available.

The ASUS 52334 mount implementation and error handling remain authoritative; only the three-directory creation behavior is to be grafted. Do not revive legacy `.asusrouter` or `jffs2_exec` merely as a shortcut.

## Lifecycle hook contract

The pinned Merlin donor contains these custom-script call sites:

| Hook | Source area | Required ordering/arguments |
|---|---|---|
| `init-start` | `rc/init.c` | after JFFS is available; before custom fstab handling |
| `services-start` | `rc/services.c` | after normal services startup |
| `services-stop` | `rc/services.c` | before normal services shutdown sequence |
| `service-event` | `rc/services.c` | before dispatch; blocking, action + service arguments |
| `service-event-end` | `rc/services.c` | after dispatch; asynchronous, same arguments |
| `nat-start` | `rc/services.c` | after NAT rules/timeouts reach normal state |
| `firewall-start` | `rc/firewall.c` | after firewall generation/reload; WAN interface argument |
| `wan-event` | `rc/wan.c` | state transition arguments |
| `wan-start` | `rc/wan.c` | compatibility hook on connected WAN |
| `dhcpc-event` | `rc/udhcpc.c` | DHCP event plus protocol argument where applicable |
| `zcip-event` | `rc/udhcpc.c` | IPv4 link-local event |
| `pre-mount` | `rc/usb.c` | blocking before mount, device/type arguments |
| `post-mount` | `rc/usb.c` | blocking after mount, mountpoint argument |
| `unmount` | `rc/usb.c` | blocking before unmount, mountpoint argument |
| `qos-start` | `rc/qos*.c` | preserve Merlin's blocking `init` semantics and rule-stage hook |
| `ddns-start` | `rc/services.c` | preserve WAN-IP argument and blocking semantics where used |
| `update-notification` | `rc/watchdog.c` | after update notification state is established |

These call sites must be merged into a source generation that preserves later ASUS behavior around them. Copying the Merlin `rc` binary or replacing whole source files is explicitly forbidden.

## Custom config/postconf integration

The helper functions are inert until each ASUS config generator has a reviewed call site. Merlin uses them across, among others:

- passwd/group/shadow and hosts;
- dnsmasq;
- inadyn/DDNS;
- multicast/UPnP/Avahi;
- VPN/IPsec;
- FTP/media/NFS services;
- WAN IGMP proxy;
- QoS/Cake.

Each generator must be reviewed independently against the later ASUS implementation. A generic global patch is not acceptable because generated file paths and service ordering can differ.

## NVRAM and WebUI contract

Pinned Merlin defaults:

- `jffs2_on=1`;
- `jffs2_scripts=0`;
- `jffs2_format=0`.

The System page exposes `jffs2_scripts` as an explicit enable/disable control.

For this project, the UI toggle must not be exposed as fully functional until the core hook engine is source-integrated. The image-first profile hook may already honor a manually set `jffs2_scripts`, but that alone is not equivalent to Merlin custom-script support.

## Addon custom-settings API

The shell half is provided by `/usr/sbin/helper.sh`:

- `am_settings_get`;
- `am_settings_set`;
- backing file `/jffs/addons/custom_settings.txt`.

The full WebUI API also requires Merlin HTTPD-side support:

- reading the settings file as JSON for EJ output;
- accepting/writing custom settings submitted by addon pages.

Because ASUS 52334 `httpd` is protected and its matching source is unavailable, the HTTPD half remains source-blocked. Do not replace `httpd` with the Merlin binary.

## AMTM prerequisite probe

The pinned Merlin 386.14_2 AMTM launcher is additive, but it is intentionally not included yet.

ASUS 52334 provides `/usr/sbin/curl` and the normal shell/core commands used by the launcher. It does not provide `dos2unix` or `unix2dos`, and these applets were not identified in the stock BusyBox string surface.

The base AMTM launcher defines its line-ending conversion helper even though that helper is not called by the bootstrap body itself; downloaded AMTM modules/addons may rely on it. More importantly, AMTM can enable `jffs2_scripts` and install addons that expect the lifecycle hook engine. Shipping AMTM before those prerequisites would therefore misrepresent support.

## Source gate

A core JFFS feature can move from SOURCE-BLOCKED to implementation only when one of these is true:

1. matching ASUS 52334 source becomes available; or
2. a sufficiently late, clean, independently verified ASUS AC86U source baseline is available and its delta to the 52334 runtime can be bounded well enough to rebuild the affected component without regressing later ASUS behavior.

Merlin GPL-merge commits 386_52796/386_52805 remain useful archaeology only; they retain pre-existing Merlin code and are not clean ASUS snapshots.
