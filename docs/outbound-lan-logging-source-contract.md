# Outbound LAN allowed-connection logging source contract

Date: 2026-09-28  
Feature inventory ID: M68  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Clean source-lineage anchor: ASUS 386.45956 @ `a9179fc9329565dea0f7c5c7648fe8ad49ceaaf6`  
Merlin donor: 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Purpose

Restore Merlin's logging of newly allowed outbound LAN-forwarded connections when the existing firewall allowed-connection logging option is enabled.

This is a deliberately tiny source delta. It must not be implemented by binary-patching or replacing ASUS `rc`.

## Existing ASUS logging contract

Both the clean ASUS source lineage and the pinned Merlin donor derive:

`logaccept`

from `fw_log_x`.

When:

- `fw_log_x=accept`; or
- `fw_log_x=both`;

`logaccept` resolves to the logging chain `logaccept`.

Otherwise it resolves to literal `ACCEPT`.

The logging chain records NEW connections with prefix `ACCEPT ` and then accepts them.

Therefore using `logaccept` as a rule target preserves normal acceptance while adding logging only when the existing firewall setting requests it.

## Exact source delta

In the LAN-to-WAN default allow rule, clean ASUS 386.45956 has:

```c
if (nvram_get_int("fw_enable_x"))
    fprintf(fp, "-A FORWARD -i %s -j %s\n", lan_if, "ACCEPT");
```

Pinned Merlin 386.14_2 changes only the target:

```c
if (nvram_get_int("fw_enable_x"))
    fprintf(fp, "-A FORWARD -i %s -j %s\n", lan_if, logaccept);
```

This is the M68 behavior.

## Why this is not an image-safe patch

ASUS 52334 `rc` is a protected core binary and remains authoritative for later firewall, HND, acceleration, dual-WAN and security behavior.

Even though runtime strings prove the relevant format string and logging chains exist, they do not prove the compiled argument at the specific LAN→WAN rule call site.

Therefore:

- do not binary-patch `rc`;
- do not transplant Merlin `rc`;
- apply the one-token source delta only to a sufficiently late ASUS-compatible `firewall.c` after reviewing the final call site.

## Scope boundary

M68 changes only the default LAN-originated FORWARD accept target from literal `ACCEPT` to the already-derived `logaccept`.

It does **not**:

- add a new NVRAM setting;
- add a new WebUI control;
- change drop logging;
- change INPUT logging;
- change DNAT/port-forward logging;
- change firewall enable semantics;
- alter packet acceptance when allowed logging is disabled.

## IPv6

The pinned donor change identified for this inventory item is the IPv4 LAN→WAN default rule shown above.

Do not automatically mirror it into IPv6 without separately proving the donor's corresponding IPv6 behavior and later ASUS rule ordering. M68's current contract is intentionally limited to the verified donor delta.

## Validation gate

Before M68 becomes **SUCCESS**, prove on the final ASUS-based source build:

1. with `fw_log_x` not logging allowed traffic, LAN→WAN behavior is unchanged;
2. with `fw_log_x=accept`, new allowed LAN→WAN connections produce the existing `ACCEPT ` log entry;
3. with `fw_log_x=both`, allowed logging and drop logging both continue to work;
4. existing LAN→WAN filtering and parental/network-service rules still execute before the default allow;
5. firewall-disabled behavior is unchanged;
6. NAT/port-forward and VPN rule ordering is unchanged;
7. no duplicate logging is introduced for rules already targeting `logaccept`.

## Current classification

**SOURCE-REQUIRED — ONE-LINE BEHAVIOR DELTA VERIFIED**

The behavior is precisely bounded; implementation waits for the later ASUS-compatible firewall source path.
