# Optional payload delivery contract

Date: 2026-10-01
Baseline: ASUS RT-AC86U 386_52334 + guarded Merlin overlay

This directory contains payloads deliberately excluded from the immutable rootfs capacity budget.

## Proven manual JFFS tools

Run 36863705618 validates a rootfs-independent installer for Nano/ncurses and SCP.

Default target:

`/jffs/addons/merlin-tools`

Properties:

- source payload SHA-256 values are checked before installation;
- Nano uses a wrapper that scopes `LD_LIBRARY_PATH` to its private ncurses directory;
- SCP remains the previously validated static AArch64 binary;
- no NVRAM values are changed;
- no startup/service hooks are installed;
- nothing auto-starts;
- uninstall is fail-closed to the exact production directory (or explicit `/tmp/*` test sandboxes).

These tools can therefore be delivered independently of the 570-PEB firmware rootfs. Automatic PATH integration remains dependent on the JFFS/profile framework; until then invocation is explicit from the add-on directory.

## WebUI payloads are NOT generic file installs

Monthly Traffic/Chart.js and local OUI cannot be restored by copying into stock `/www`: the firmware rootfs is immutable and local OUI also requires exact patches to stock pages.

The active image already provides `/www/user1.asp` ... `/www/user20.asp` aliases into the runtime `/var/wwwext` namespace. That is the correct future addon surface, but these optional features must be adapted to that namespace before delivery.

Do not re-add the removed Monthly Traffic Tools-menu entry until a working runtime page is actually installed.

## Local NTPD remains dormant

`/usr/libexec/rtac86u-ntpd` has a proven isolated binary/runtime contract, but server lifecycle, DHCP advertisement and redirect semantics depend on M01-M04/M30. Do not install or auto-start it as an optional package yet.

## AMTM remains dormant

The pinned AMTM launcher is add-only, but full behavior requires the generic JFFS engine and its dependencies. Verification/materialization may be performed in CI, but it must not be exposed as functional firmware until the M01/M04 gate is satisfied.

## Security boundary

Optional delivery must never:

1. replace ASUS 52334 core binaries;
2. modify the immutable firmware rootfs at runtime;
3. silently enable startup hooks or NVRAM features;
4. download unpinned binaries during firmware build;
5. claim a feature is active merely because its payload can be materialized.
