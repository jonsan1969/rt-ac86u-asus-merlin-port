# Custom DDNS source integration contract

Date: 2026-09-28  
Feature inventory ID: M11  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Clean source-lineage anchor: ASUS 386.45956 mirror @ `a9179fc9329565dea0f7c5c7648fe8ad49ceaaf6`  
Merlin donor: 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Purpose

Restore Merlin's script-driven **Custom DDNS** behavior without replacing ASUS 52334 `rc`, DDNS/Inadyn code, `httpd`, or any later ASUS networking/security logic.

This feature is dependent on the JFFS custom-script engine. The UI must not be exposed as functional until `run_custom_script()`, `jffs2_scripts`, and the lifecycle framework are source-integrated.

## Important distinction

ASUS already has a provider string named:

`WWW.DYNDNS.ORG(CUSTOM)`

That is an Inadyn/DynDNS provider mode and is **not** Merlin's script-driven Custom DDNS provider.

Merlin adds a separate provider value:

`CUSTOM`

which delegates the update to `/jffs/scripts/ddns-start`.

Do not confuse or replace the ASUS provider entry.

## Pinned source delta

### 1. rc multicall callback

Merlin adds the `ddns_custom_updated` command to the `rc` multicall table in:

- `release/src/router/rc/rc.c`

and its prototype in:

- `release/src/router/rc/rc.h`

The rc install step adds:

`/sbin/ddns_custom_updated -> rc`

in:

- `release/src/router/rc/Makefile`

The clean ASUS 45956 anchor has `ddns_updated` but does not have `ddns_custom_updated`.

### 2. Custom provider selection

In Merlin `start_ddns()`, provider value `CUSTOM` is mapped to an empty Inadyn service string rather than a normal provider backend.

The custom branch then blocks on:

```c
run_custom_script("ddns-start", 120, wan_ip, NULL);
return 0;
```

The blocking call is intentional: the script is expected to finish its update and call `ddns_custom_updated` so DDNS result NVRAM is coherent before the custom path returns.

The later ASUS DDNS implementation must remain authoritative around this insertion. Do not replace `start_ddns()` wholesale and do not regress ASUS dual-WAN, IPv6, provider, certificate, or retry behavior.

### 3. General ddns-start hook

Pinned Merlin also invokes:

```c
run_custom_script("ddns-start", 0, wan_ip, NULL);
```

after launching a normal DDNS provider update.

This is the generic Merlin lifecycle hook and is distinct from the blocking Custom-DDNS path.

When porting, preserve both semantics:

- normal provider: async `ddns-start`;
- `CUSTOM` provider: blocking max 120 seconds and no Inadyn provider launch.

### 4. Completion callback semantics

Pinned Merlin `ddns_custom_updated_main()` accepts an optional result argument.

Success is:

- no argument; or
- argument `1`.

On success it sets:

- `ddns_status=1`;
- `ddns_updated=1`;
- `ddns_return_code=200`;
- `ddns_return_code_chk=200`;
- `ddns_server_x_old` to the current provider;
- `ddns_hostname_old` to the current hostname;
- `ddns_last_wan_unit` to the primary WAN unit;
- `ddns_check_retry=10`;

and logs completion.

On failure it sets:

- `ddns_return_code=unknown_error`;
- `ddns_return_code_chk=unknown_error`;

and logs failure.

This callback is source-level behavior. Do not emulate it with a shell script that writes arbitrary NVRAM unless the rebuilt ASUS-side `rc` integration is unavailable and such a fallback is separately designed and validated.

## WebUI contract

Merlin's DDNS page adds provider option:

```html
<option value="CUSTOM" ...>Custom</option>
```

When `CUSTOM` is selected, the page:

- keeps hostname input available;
- disables username/password and wildcard controls that are irrelevant to the user script;
- shows a note explaining that `ddns-start` must perform the update;
- shows a warning if JFFS or custom scripts are disabled.

The donor explicitly checks both:

- `jffs2_on=1`;
- `jffs2_scripts=1`.

For this project, the UI row must not be added before the JFFS custom-script engine is functional. A dead or partially functional Custom DDNS selector is worse than leaving the ASUS page unchanged.

## Required source patch surface

The narrow expected source patch is:

1. `rc/rc.c`
   - register `ddns_custom_updated` multicall command.
2. `rc/rc.h`
   - declare `ddns_custom_updated_main()`.
3. `rc/Makefile`
   - install `ddns_custom_updated -> rc` symlink.
4. `rc/services.c`
   - recognize provider `CUSTOM`;
   - execute blocking custom `ddns-start` path;
   - preserve generic async `ddns-start` hook;
   - add `ddns_custom_updated_main()` using reviewed later-ASUS NVRAM/status semantics.
5. DDNS WebUI page
   - add the `CUSTOM` provider and conditional UI behavior only after the backend is present.

No donor `rc`, `httpd`, Inadyn binary, OpenSSL component, or other core binary is to be transplanted.

## Dependency on M01-M04

M11 cannot be considered complete until the source-side JFFS/custom-script engine provides:

- an enabled `run_custom_script()` helper;
- `jffs2_scripts` gating;
- executable `/jffs/scripts/ddns-start`;
- correct blocking timeout behavior.

The image-safe `/rom/etc/profile` and `helper.sh` pieces alone do not satisfy this dependency.

## Validation gate

Before M11 becomes **SUCCESS**, prove all of the following on the final ASUS-based build:

1. stock ASUS DDNS providers still update normally;
2. ASUS `WWW.DYNDNS.ORG(CUSTOM)` remains unchanged;
3. selecting `CUSTOM` never launches Inadyn for that update;
4. `ddns-start` receives the current WAN IPv4 address as its first argument;
5. the custom path blocks but is bounded to the donor-compatible timeout;
6. `ddns_custom_updated` with no arg or `1` reports success;
7. `ddns_custom_updated 0` reports failure;
8. result NVRAM and WebUI status update coherently;
9. disabled custom scripts prevent Custom DDNS from being presented as usable;
10. normal DDNS path still fires the async `ddns-start` lifecycle hook;
11. dual-WAN and IPv6 behavior remain later-ASUS-authoritative.

## Current classification

**SOURCE-REQUIRED / DEPENDENCY-GATED BY JFFS CORE ENGINE**

The pinned 45956 source anchor proves a small and reviewable source delta, but it does not make a binary-only or UI-only port safe.
