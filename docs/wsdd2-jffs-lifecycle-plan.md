# wsdd2 via generic JFFS lifecycle integration

Date: 2026-09-28  
Feature inventory ID: M21  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Donor: Merlin 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Decision

Do **not** add a wsdd2-specific lifecycle patch to ASUS `rc`.

The donor `wsdd2` ELF has already been proven dependency-compatible with ASUS 52334 by run `36382208517`.

Once the generic JFFS lifecycle engine M01-M03 is source-integrated, M21 can be implemented as:

1. add-only `/usr/sbin/wsdd2` donor binary;
2. add-only small reconcile wrapper;
3. generic JFFS lifecycle scripts that invoke the wrapper.

This keeps ASUS Samba and `rc` authoritative.

## Pinned donor behavior

Merlin's Samba start path calls:

`start_wsdd();`

immediately after starting `smbd`.

The donor start function executes:

```text
/usr/sbin/wsdd2 -d -w -i <lan_ifname> -b sku:<productid>,serial:<LAN-MAC-no-colons>
```

Before launch it stops an existing wsdd2 process.

Serial construction is the lower-case hexadecimal LAN MAC bytes without separators. If LAN MAC parsing fails, donor C falls back to random bytes.

The donor stop function terminates wsdd2 when Samba stops.

There is no independent `wsdd_enable` NVRAM toggle in the pinned donor. wsdd2 follows Samba lifecycle.

## Generic reconcile model

Create an add-only wrapper, for example:

`/usr/sbin/wsdd2-reconcile`

The wrapper is idempotent.

### If Samba is running

When a valid Samba daemon process is present:

1. resolve `lan_ifname` from NVRAM;
2. resolve `productid`;
3. resolve LAN MAC from the normal ASUS NVRAM/source of truth;
4. construct donor-compatible `sku:...,serial:...` boot parameters;
5. if wsdd2 is already running with the expected configuration, do nothing;
6. otherwise stop stale wsdd2 and start the staged donor binary with donor-compatible arguments.

### If Samba is not running

Stop wsdd2 if present.

This process-state reconciliation is safer than trying to infer every internal ASUS Samba call site from UI events alone.

## Lifecycle entry points

After M01-M03 exist, invoke the reconcile wrapper from:

### `services-start`

Ensures WSD discovery is restored after normal boot services are up.

### `service-event` pre-hook

For actions that stop/restart Samba-owned services, stop wsdd2 before the stock service dispatch.

Relevant service names must be checked against the later ASUS source/runtime. Pinned Merlin includes at least:

- `ftpsamba`;
- `samba`;
- `samba_force`;
- permission/account paths that stop Samba.

The pre-hook should be conservative: only stop wsdd2 when the event is known to stop/restart Samba.

### `service-event-end`

Run reconcile after relevant start/restart events so wsdd2 follows the final actual `smbd` state.

Because the wrapper checks process state, false-positive reconciliation is harmless.

### `post-mount`

Run reconcile after USB mount handling, because ASUS may start/reconfigure Samba from storage lifecycle paths without a user-triggered `rc_service` event.

### `services-stop`

Stop wsdd2 during global service shutdown.

## Why this is preferable

A direct donor port would modify `rc/usb.c`:

- call `start_wsdd()` after `start_samba()`;
- call `stop_wsdd()` inside `stop_samba()`;
- add start/stop helper functions.

That is a small source delta, but it duplicates lifecycle ownership for one optional daemon.

The generic JFFS-hook design:

- reuses the already-required M01-M03 infrastructure;
- avoids touching later ASUS Samba control flow;
- keeps M21 add-only after the generic source engine lands;
- makes the daemon independently removable;
- remains compatible with M18/M19/M20 source/UI work.

## Binary safety requirements

Before activating M21, retain the existing compatibility evidence and revalidate:

1. ELF architecture matches ASUS RT-AC86U runtime;
2. interpreter exists;
3. every DT_NEEDED library exists in ASUS 52334 or is bundled add-only;
4. no library replacement;
5. qemu smoke test succeeds if the harness can exercise the binary;
6. binary hash is pinned;
7. no Merlin BusyBox or other core runtime is pulled in.

## Wrapper requirements

The wrapper must:

- use absolute paths;
- have a lock to avoid concurrent reconcile races;
- never use user-controlled shell interpolation;
- validate NVRAM-derived interface/product/MAC values;
- reject an invalid/empty LAN interface rather than launch on all interfaces accidentally;
- avoid duplicate wsdd2 instances;
- log start/stop failures;
- treat missing wsdd2 binary as a no-op/error rather than destabilize Samba;
- never restart Samba itself.

## Validation gate

Before M21 becomes **SUCCESS**, prove:

1. Samba disabled/stopped => wsdd2 is not running;
2. Samba starts at boot => wsdd2 starts after it;
3. `restart_ftpsamba` => wsdd2 is cleanly stopped/reconciled and ends running once;
4. `restart_samba` => same;
5. USB mount-triggered Samba startup/reconfigure => reconcile reaches correct final state;
6. service shutdown => wsdd2 stops;
7. repeated reconcile calls are idempotent;
8. invalid LAN MAC/interface input fails closed;
9. WSD discovery works from a Windows client on the LAN;
10. normal Samba access, WINS M20, M18/M19 controls and dnsmasq are unchanged;
11. ASUS `rc`, Samba binaries and libraries remain protected/unreplaced.

## Classification

**B AFTER M01-M03 / NO M21-SPECIFIC CORE PATCH**

M21 remains gated today because the generic JFFS lifecycle engine is not yet in the source build. Once that engine exists, wsdd2 can become an add-only binary + script adaptation instead of a dedicated `rc` source feature.
