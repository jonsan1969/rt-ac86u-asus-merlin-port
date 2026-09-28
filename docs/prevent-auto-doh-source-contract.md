# Prevent Auto DoH / DDR / Private Relay source contract

Date: 2026-09-28  
Feature inventory ID: M66  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Clean source-lineage anchor: ASUS 386.45956 @ `a9179fc9329565dea0f7c5c7648fe8ad49ceaaf6`  
Merlin donor: 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Purpose

Restore Merlin's **Prevent client auto DoH** behavior, including the donor-generation handling for:

- Mozilla/Firefox automatic DoH discovery;
- DDR (Discovery of Designated Resolvers);
- Apple iCloud Private Relay canaries;

without replacing ASUS 52334 `dnsmasq`, `rc`, or DNS Privacy components.

This is dnsmasq **configuration-generation behavior**, not a dnsmasq binary feature.

## Source-lineage findings

Clean ASUS 386.45956 `rc/services.c` contains none of:

- `dns_priv_override`;
- `use-application-dns.net`;
- `_dns.resolver.arpa`;
- `mask.icloud.com`;
- `mask-h2.icloud.com`.

Pinned Merlin 386.14_2 adds the control/default/UI and emits the canary entries from the dnsmasq configuration generator.

ASUS 52334 runtime has later DNS Privacy functionality of its own, so the final merge must use the later ASUS dnsmasq generator and DNS Privacy state as authoritative. The 45956 tree is only a clean lineage anchor.

## NVRAM control

Pinned Merlin defines:

`dns_priv_override=0`

with three values:

| Value | UI | Meaning |
|---:|---|---|
| `0` | Auto | enable the prevention canaries only when relevant router DNS enforcement/privacy is active |
| `1` | Yes | always emit the prevention canaries |
| `2` | No | do not emit them |

The donor WAN page exposes the selector as **Prevent client auto DoH** and restarts dnsmasq when the value changes.

## Activation semantics

Pinned Merlin evaluates:

`n = nvram_get_int("dns_priv_override")`

and emits the canaries when either:

1. `n == 1`; or
2. `n == 0` and at least one relevant automatic condition is active:
   - DNS Privacy is enabled, when compiled with `RTCONFIG_DNSPRIVACY`; or
   - DNSFilter/DNS Director is enabled in a nonzero global mode, when compiled with `RTCONFIG_DNSFILTER`.

When `n == 2`, the donor does not emit these prevention records.

The final ASUS-based implementation must map the **Auto** condition onto the later ASUS DNS Privacy/DNS Director state without regressing newer ASUS logic.

## Exact dnsmasq output

When active, the pinned donor emits:

```text
address=/use-application-dns.net/
address=/_dns.resolver.arpa/
address=/mask.icloud.com/mask-h2.icloud.com/
```

These three lines are the M66 behavior contract.

### Mozilla / application DoH

`use-application-dns.net` is the application canary used by clients such as Firefox when deciding whether automatic DoH should be enabled.

### DDR

`_dns.resolver.arpa` is the donor's DDR-related canary name.

Preserve the exact leading `_dns.` label from the pinned donor. Do not simplify the implementation to a generic `resolver.arpa` match without proving equivalent behavior.

### Apple Private Relay

The donor places both:

- `mask.icloud.com`;
- `mask-h2.icloud.com`;

on the same dnsmasq `address=` line.

Preserve both names.

## Required source patch surface

A later ASUS-compatible implementation is expected to touch only:

1. the relevant defaults table, **if** `dns_priv_override` is not already present in that later source;
2. the current ASUS dnsmasq config generator;
3. the current WAN/DNS settings UI, **if** the control is not already exposed.

Do not replace:

- `dnsmasq`;
- Stubby/DNS Privacy binaries;
- ASUS `rc`;
- current DNSFilter/DNS Director backend.

## Relationship to DNS Director

The project already ports DNS Director UI on top of ASUS's newer DNSFilter backend.

M66's Auto state should treat the **actual later ASUS global DNS-enforcement state** as authoritative. It must not import an older Merlin DNSFilter implementation just to evaluate the condition.

Full IPv6 DNS Director Custom 1–3 parity (M36) remains a separate source-required item.

## WebUI gate

Before adding a UI selector, verify whether ASUS 52334 already exposes or consumes `dns_priv_override`.

If the later ASUS source/runtime already owns the key, reuse its semantics rather than creating a duplicate setting.

If it does not, add the donor-compatible:

- Auto = `0`;
- Yes = `1`;
- No = `2`;

and ensure a change causes dnsmasq configuration to be regenerated/restarted through the normal later ASUS apply path.

## Validation gate

Before M66 becomes **SUCCESS**, prove:

1. `dns_priv_override=2` emits none of the three prevention entries;
2. `dns_priv_override=1` emits all three entries;
3. Auto with no DNS Privacy/global DNS enforcement emits none;
4. Auto with DNS Privacy enabled emits all three entries;
5. Auto with global DNS Director/DNSFilter enforcement enabled emits all three entries;
6. the emitted names are exactly:
   - `use-application-dns.net`;
   - `_dns.resolver.arpa`;
   - `mask.icloud.com`;
   - `mask-h2.icloud.com`;
7. dnsmasq accepts the generated configuration;
8. disabling the feature removes the entries after the normal apply/restart path;
9. ASUS DNS Privacy, DNS Director, DHCP and resolver behavior remains unchanged outside these canaries;
10. no older Merlin dnsmasq or `rc` binary is introduced.

## Current classification

**SOURCE-REQUIRED — CONFIG-GENERATION DELTA VERIFIED**

The donor semantics are bounded. Final implementation waits for a later ASUS-compatible dnsmasq generator source path and a definitive check of whether ASUS 52334 already owns the `dns_priv_override` key/UI.
