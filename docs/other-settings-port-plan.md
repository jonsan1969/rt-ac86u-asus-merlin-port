# Tools / Other Settings adaptation plan

Date: 2026-09-26  
Feature inventory IDs: M31, M44, M47 and adjacent controls  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Merlin donor: 386.14_2 @ 6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b

## Runtime-first decision

Do not transplant Merlin's full `Tools_OtherSettings.asp`.

The donor page is an umbrella over several independent Merlin features. ASUS 52334 only exposes a subset of the donor backend contract, so the port must be split by verified backend capability.

## Verified ASUS 52334 overlap

Targeted runtime probe:

- `ct_tcp_timeout`: exact NVRAM/backend string present in stock `/sbin/rc`;
- `ct_udp_timeout`: exact NVRAM/backend string present in stock `/sbin/rc`;
- `rstats_path`: exact stock `/sbin/rc` string present;
- `rstats_new`: exact stock `/sbin/rc` string present;
- stock `/bin/rstats` exists;
- stock `/usr/sbin/cru` exists;
- `shell_timeout`: stock HTTPD string present;
- reboot scheduling keys are present in stock RC/HTTPD.

The same probe did **not** establish a safe UI/apply contract for:

- `ct_max`;
- cstats controls;
- `dns_local_cache`;
- `ntpd_enable`;
- `ntpd_server_redir`.

A later targeted `rstats` probe refined the traffic-history result: the stock 52334 daemon itself contains `rstats_path`, `rstats_offset`, `rstats_stime`, `rstats_bak` and the Tomato-compatible history file logic. Those daemon strings prove consumption, but not yet safe arbitrary-path persistence through ASUS's restart/boot wrapper.

Those controls must not be exposed merely because Merlin's page contains them.

## Conntrack phase 1

The active adapter at `ports/files/Tools_OtherSettings.asp` exposes the verified timeout vectors:

- the eight TCP state timeout values encoded in `ct_tcp_timeout`;
- UDP unreplied/assured values encoded in `ct_udp_timeout`.

It preserves Merlin's value ranges and vector encoding but does not expose `ct_max`.

ASUS source provenance changes the apply strategy. The timeout backend itself is ASUS-origin: `ct_tcp_timeout`, `ct_udp_timeout` and `setup_conntrack()` are already present in the clean RT-AC86U ASUS GPL 382_15098 initial import, where `init.c` invokes `setup_conntrack()` during boot. By contrast, the `strcmp(script, "conntrack")` service-dispatch block is not present in that clean ASUS-origin point and enters the available history through the older Merlin merge lineage.

Therefore phase 1 must **not** rely on `action_script=restart_conntrack`. The staged adapter saves only the verified ASUS NVRAM vectors and requests a normal stock reboot, allowing the ASUS boot path to apply them through `setup_conntrack()`. Immediate conntrack reload remains deferred unless the 52334 runtime dispatcher is independently proven.

The earlier plain `strings -Fx conntrack` negative was also shown to be unsuitable as a discriminator: the verified Merlin 386.14_2 runtime itself lacks an exact standalone `conntrack` string even though its WebUI uses `restart_conntrack`.

Phase 1 was promoted into the guarded active overlay together with a hash-guarded ASUS `menuTree.js` patch that adds only a `Tools -> Other Settings` entry. Validation run `36331580369` passed. The exact menu preimage is `73163bdf1b9f20c056a3c2b90629521b0a0f2007ea4967b73c1b3d6d8d9583e2` and the validated postimage is `fd1982791f0ccb02039e56f883670c8a0dc42f6eae01afe8e135cda35b62c1ac`.

## Shell timeout adaptation

ASUS 52334 already consumes `shell_timeout` in its persistent HND profile:

`TMOUT="$(nvram get shell_timeout 2>/dev/null)"`

and stock `httpd` exposes the exact `shell_timeout` NVRAM/form string. Merlin's UI semantics store seconds while presenting minutes, accepting `0` as disabled or 10–999 minutes. The active Tools adapter therefore exposes only that same conversion/range and uses the already-required stock reboot path. No SSH/Dropbear binary is changed.

## Traffic-history follow-up

M47 is split into a safe stock-compatible subset and a deferred Merlin extension.

Verified safe subset:
- `rstats_bak` selects ASUS's stock NVRAM-backed history mode;
- `rstats_stime` is consumed directly by the stock 52334 `/bin/rstats` daemon; the adapter offers the donor's conservative 1/6/12/24/72-hour choices;
- `rstats_offset` is consumed directly by the stock daemon and is constrained to 1–31.

Runtime apply-path proof is also present: 52334 `httpd` dynamically links `/usr/lib/libshared.so`, and that exact library contains the full default-key set used by this page, including `rstats_bak`, `rstats_stime`, `rstats_offset`, `shell_timeout`, `ct_tcp_timeout` and `ct_udp_timeout`.

Clean ASUS-origin 382_15098 code shows that ASUS's `restart_rstats()` rewrites `rstats_path` from `rstats_bak` (NVRAM backup vs empty path), while Merlin later removed that restriction to preserve arbitrary paths. Therefore arbitrary USB/JFFS `rstats_path` and `rstats_new` remain deliberately absent. The active adapter uses the stock reboot path so ASUS's own boot-time `restart_rstats()` semantics remain authoritative.

## Safety rule

ASUS 52334 `rc`, `httpd`, kernel, dnsmasq and other core binaries remain unchanged. This block is UI/static adaptation only unless a later source-compatible implementation is explicitly proven.
