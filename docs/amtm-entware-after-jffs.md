# AMTM and Entware integration after JFFS core hooks

Date: 2026-09-28  
Feature inventory IDs: M08, M09  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Merlin donor: 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Decision

AMTM and Entware do not need their own ASUS core-binary transplant.

They are layered on top of the generic JFFS/addon foundation:

- M01/M04 provide `jffs2_scripts`, `/jffs/scripts`, `/jffs/configs`, addon helper conventions and config integration;
- M02/M03 provide the lifecycle events addons depend on;
- stock ASUS already exposes `/opt -> /tmp/opt`.

Once those prerequisites are implemented in the source build, AMTM can be restored as an add-only shell script and Entware can use the normal addon lifecycle.

## M08 — AMTM

Pinned donor installs:

`release/src/router/others/amtm -> /usr/sbin/amtm`

mode 0700.

The pinned script is a small bootstrap/controller. It uses:

- `/jffs/addons/amtm`;
- `/jffs/configs/profile.add`;
- `jffs2_scripts`;
- `/usr/sbin/curl`;
- standard shell utilities;
- online AMTM module downloads.

It does not require a Merlin `rc` or HTTPD binary merely to start.

### First-run behavior relevant to this port

Pinned AMTM:

1. creates `/jffs/addons/amtm/a_fw`;
2. requires router time/NTP to be ready;
3. migrates old AMTM files;
4. cleans an obsolete `alias amtm=` from `profile.add`;
5. removes old `/jffs/scripts/amtm` or `/opt/bin/amtm` copies;
6. checks `jffs2_scripts`;
7. enables it and commits NVRAM if disabled;
8. downloads `amtm.mod`;
9. executes the integrated AMTM menu/module framework.

In this project, step 7 must not be relied on to create functionality before M01 exists. Setting the NVRAM key alone is not equivalent to having the source-side hook engine.

### M08 activation rule

Do not put AMTM in the active image overlay until:

- `jffs2_scripts` is a real later-ASUS default/backend key;
- `/jffs/addons` is bootstrapped;
- helper/profile integration is working;
- the stock ASUS 52334 curl/TLS/CA path is verified for AMTM downloads.

Then M08 can be **add-only**.

## M09 — Entware/addon integration

The firmware already has:

`/opt -> /tmp/opt`

which is the expected volatile mountpoint model.

The missing piece in stock ASUS is not the symlink. It is the generic lifecycle framework used to bind/mount/start addon services reliably.

Entware/addon installers commonly need at least:

- `post-mount`;
- `services-start`;
- `services-stop`;
- sometimes `service-event`;
- shell profile additions;
- persistent files under `/jffs`.

Therefore M09 is not considered functional until M01-M03 are active.

## Do not bake package-manager state into rootfs

Do not transplant an old Merlin Entware tree into firmware.

The firmware contribution is only:

- generic JFFS lifecycle compatibility;
- the existing `/opt` convention;
- AMTM/helper bootstrap pieces.

Entware packages remain user-installed external software on persistent storage.

## Online update boundary

Pinned AMTM intentionally downloads modules at runtime from the AMTM infrastructure.

That means the integrated bootstrap is pinned to the donor firmware, but module contents can evolve independently after installation.

This is consistent with Merlin's own design. The project should not silently vendor current AMTM online modules into the firmware image and call them 386.14_2 donor content.

## Security/runtime rules

Before enabling AMTM:

1. use ASUS 52334 curl/OpenSSL/CA stack only;
2. do not bundle Merlin curl/OpenSSL;
3. HTTPS certificate verification must remain enabled;
4. keep downloaded modules on JFFS, not immutable rootfs;
5. do not auto-run newly downloaded third-party code merely because firmware booted unless the user installed/enabled it;
6. preserve executable/file ownership expected by JFFS addons;
7. provide a clear log path for addon lifecycle failures.

## Validation gate

### M08

1. `amtm` launches using ASUS shell/userspace;
2. first-run addon directory creation works;
3. NTP-ready check works;
4. module download succeeds through ASUS 52334 TLS stack;
5. failure to download leaves no corrupted partial module;
6. profile integration does not duplicate aliases;
7. no Merlin core libraries/binaries are introduced.

### M09

8. Entware installation can bind/mount `/opt` correctly;
9. post-mount restores it after storage remount/reboot;
10. services-start starts installed addon services once;
11. services-stop shuts them down coherently;
12. unplug/remount does not leave stale `/opt` state;
13. stock Samba/USB mount behavior is unchanged;
14. addon failure never prevents normal ASUS boot/service startup.

## Classification

**M08: B AFTER M01/M04**  
**M09: B AFTER M01-M03**

Neither feature needs a dedicated ASUS core patch beyond the generic JFFS engine already required by the project.
