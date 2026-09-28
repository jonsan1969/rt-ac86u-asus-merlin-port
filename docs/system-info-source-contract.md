# System Info source integration contract

Date: 2026-09-28  
Feature inventory ID: M43  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Merlin donor: 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Purpose

Restore Merlin's read-only **Tools / System Information** page while preserving ASUS 52334 HTTPD, networking and hardware logic.

This feature does not require a daemon, kernel module or replacement binary. It is primarily:

- a small read-only HTTPD sysinfo extension;
- an add-only System Info page;
- an add-only AJAX refresh endpoint;
- a menu entry.

## Existing ASUS 52334 capability

Prior runtime probing established that stock ASUS 52334 already has a generic `sysinfo()` WebUI dispatcher and many reusable runtime surfaces, but does not expose the Merlin-specific keys required by the page, notably:

- `cpu.model`;
- `cpu.freq`;
- `conn.max`;
- `nvram.total`.

Do not replace ASUS HTTPD. Add the missing handlers to a later ASUS-compatible HTTPD source tree.

## Pinned Merlin HTTPD module

Pinned Merlin implements the read-only dispatcher in:

`release/src/router/httpd/sysinfo.c`

with a small header:

`release/src/router/httpd/sysinfo.h`.

The donor module exposes these core data classes:

### CPU
- `cpu.model`
- `cpu.freq`
- `cpu.load.1`
- `cpu.load.5`
- `cpu.load.15`

### Memory
- `memory.total`
- `memory.free`
- `memory.buffer`
- `memory.swap.total`
- `memory.swap.used`
- `memory.cache`

### NVRAM
- `nvram.total`
- `nvram.used`

### Persistent storage
- `jffs.usage`
- `jffs.free`

### Conntrack
- `conn.total`
- `conn.active`
- `conn.max`

### Hardware/platform
- `cfe_version`
- `qtn_version`
- `ethernet`
- `ethernet.rtk`

Not every donor handler is relevant to RT-AC86U. Port only handlers that produce meaningful data on the target.

## Fields actually consumed by Tools_Sysinfo.asp

The pinned page directly calls:

- `ethernet`;
- `ethernet.rtk`;
- `hwaccel.runner`;
- `hwaccel.fc`;
- `conn.max`;
- `nvram.total`;
- `driver_version.0` through `driver_version.3`;
- `cfe_version`;
- `qtn_version`;
- `cpu.model`;
- `cpu.freq`.

The page also consumes periodically refreshed values from `ajax_sysinfo.asp`, including memory, load, JFFS, connection and wireless-client counters.

For RT-AC86U, unsupported platform-specific fields must render as unavailable/hidden rather than fabricate data or fail the page.

## Minimal RT-AC86U backend set

The first source patch should add only the fields needed for a useful AC86U page and not already supplied by stock ASUS:

1. `cpu.model`;
2. `cpu.freq`;
3. `conn.max`;
4. `nvram.total`;
5. any missing memory/load/JFFS/conn counters required by the AJAX endpoint;
6. only hardware acceleration/driver fields that can be derived safely from existing ASUS runtime APIs or procfs.

Do not add Quantenna-only behavior to RT-AC86U.

## CPU model

Pinned donor reads CPU/platform information from Linux runtime data and applies HND-specific handling.

For the final port:

- prefer later ASUS/HND APIs or `/proc/cpuinfo` already present in 52334;
- return a bounded printable string;
- do not execute shell commands using untrusted input;
- do not hardcode a model string when the target can report it.

## CPU frequency

Use the later ASUS-compatible HND source/runtime owner.

Do not assume the donor's CPU-frequency retrieval path is correct for the final 52334 tree merely because both are HND.

Validation must compare the reported MHz against available kernel/platform state under idle/load conditions and ensure the value is sensible.

## Conntrack maximum

Use the active kernel sysctl path for the target, normally the current nf_conntrack maximum exposed by the running kernel.

This is read-only. M31 remains the separate feature that changes selected conntrack timeout values.

## NVRAM size

`nvram.total` must report the actual platform/build NVRAM capacity used by the later ASUS firmware.

Do not copy a compile-time constant from an older donor if the ASUS 52334 build defines a different capacity.

`nvram.used` should use the current ASUS NVRAM API or equivalent safe calculation.

## Memory/load/JFFS counters

Prefer direct C/library/procfs/statfs APIs:

- Linux `sysinfo()` for RAM/load where appropriate;
- filesystem stat APIs for JFFS;
- procfs/netfilter APIs for conntrack.

Avoid repeated shell pipelines on the AJAX refresh path.

## AJAX endpoint

Add/adapt `ajax_sysinfo.asp` only after all referenced sysinfo keys are backed.

The endpoint must be read-only and suitable for periodic polling.

Requirements:

- no writes to NVRAM;
- no service restart;
- no temporary files unless unavoidable;
- bounded runtime;
- graceful empty/unknown values;
- no sensitive secrets.

## WebUI

The page may be staged add-only after backend support exists:

- `/www/Tools_Sysinfo.asp`;
- `/www/ajax_sysinfo.asp` or donor-compatible endpoint;
- Tools/System Info menu link.

Preserve ASUS 52334's current CSS/JS/menu architecture where practical.

Do not import unrelated donor dashboard assets.

## Interaction with existing project features

- M45 temperature/performance page is already **SUCCESS** and remains separate.
- M31 conntrack timeout tuning is already **SUCCESS**; M43 only displays conntrack state.
- M49 traffic history and M47 persistence remain separate.
- M57 VPN Status must not be folded into M43.
- no-auto-logout behavior from M53/M54 need not be added automatically to this page unless the final UI design requires it.

## Security boundary

All M43 handlers are informational.

They must not accept arbitrary file paths, command strings, shell fragments or write operations.

Any procfs/sysfs path must be compile-time/fixed and target-specific.

## Validation gate

Before M43 becomes **SUCCESS**, prove:

1. page loads with stock ASUS authentication/session handling;
2. CPU model is nonempty and plausible;
3. CPU frequency is plausible for RT-AC86U;
4. memory totals match the running system within expected units;
5. load averages update correctly;
6. `nvram.total` matches the final ASUS build capacity;
7. `nvram.used` never exceeds total without an explicit error state;
8. JFFS usage/free values match filesystem statistics;
9. conntrack current/active/max values are valid;
10. unsupported platform-specific fields are hidden/empty, not bogus;
11. AJAX polling does not leak file descriptors or leave temp files;
12. polling has negligible CPU impact;
13. no ASUS core runtime binary is transplanted;
14. existing M45/M31 pages and handlers remain unchanged.

## Current classification

**C backend + A page after backend**

The feature is source-required only for a small read-only HTTPD/sysinfo extension. Once those handlers exist, the WebUI portion is image-safe/add-only.
