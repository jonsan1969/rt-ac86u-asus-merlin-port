# IPv6 DNS Director Custom 1–3 source integration contract

Date: 2026-09-28  
Feature inventory ID: M36  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Merlin donor: 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Purpose

Complete IPv6 parity for DNS Director Custom 1–3 without replacing ASUS 52334 DNSFilter/DNS Director, firewall, dnsmasq, HTTPD or `rc` wholesale.

DNS Director phase 1 is already **SUCCESS** in this project.

ASUS 52334 runtime already contains the IPv6 DNSFilter rule machinery needed for built-in modes. The missing donor contract is specifically the HND custom-IPv6 server mapping/default/UI surface.

## Target facts already established

Runtime probe `36374478421` and `.github/workflows/dns-director-ipv6-52334.yml` establish that ASUS 52334 has IPv6 DNSFilter machinery such as:

- IPv6 DNSFilter rule-generation signatures;
- `DNSFILTERI`;
- `DNSFILTERF`;
- split HND `dnsfilter_rulelist` handling;
- IPv6 firewall userspace.

But ASUS 52334 lacks the complete donor contract for:

- `dnsfilter_custom61`;
- `dnsfilter_custom62`;
- `dnsfilter_custom63`;

across backend/default/UI ownership.

Therefore do not port the full Merlin `dnsfilter.c`. Add only the missing custom IPv6 mapping and storage/UI pieces to later ASUS code.

## Donor defaults

Pinned Merlin defines three empty IPv6 strings:

```c
{ "dnsfilter_custom61", "", CKN_STR39, ... },
{ "dnsfilter_custom62", "", CKN_STR39, ... },
{ "dnsfilter_custom63", "", CKN_STR39, ... },
```

These correspond one-to-one with IPv4:

- `dnsfilter_custom1`;
- `dnsfilter_custom2`;
- `dnsfilter_custom3`.

The values are individual IPv6 DNS server addresses, not lists.

## Core HND resolver delta

Pinned Merlin `rc/dnsfilter.c` resolves a DNSFilter mode through:

`get_dns_filter(proto, mode, dnsfsrv)`.

For `AF_INET6` on HND, donor behavior is:

### Custom 1

```c
case DNSF_SRV_CUSTOM1:
    strlcpy(dnsfsrv->server1, nvram_safe_get("dnsfilter_custom61"), 46);
    dnsfsrv->server2[0] = '\0';
    break;
```

### Custom 2

Same mapping to:

`dnsfilter_custom62`.

### Custom 3

Same mapping to:

`dnsfilter_custom63`.

Each custom mode supplies at most one IPv6 server in the pinned donor.

If the string is invalid/empty, the existing generic `get_dns_filter()` validation causes the mode to resolve as unavailable rather than emitting a bad firewall target.

## Preserve existing ASUS IPv6 machinery

The later ASUS DNSFilter backend remains authoritative for:

- HND rule-list splitting;
- MAC rule parsing;
- IPv6 INPUT/FORWARD enforcement;
- built-in DNS provider IPv6 table;
- firewall chain creation;
- dnsmasq DHCPv6 behavior;
- DoT bypass prevention where already present;
- rule restart/apply sequencing.

M36 does **not** require a second IPv6 firewall implementation.

## HND enforcement model in donor

Pinned Merlin's HND IPv6 path can DNAT DNS directly through the existing DNSFilter chain.

For each per-client rule:

- Unfiltered returns/accepts;
- filtered modes resolve server(s) via `get_dns_filter(AF_INET6,...)`;
- allowed configured server destinations are accepted;
- other DNS destinations are dropped/rejected according to the existing chain design.

Global mode follows the same `get_dns_filter(AF_INET6,...)` resolver.

By making Custom 1–3 resolve to the new `dnsfilter_custom6N` values, the existing HND rule generator gains custom-server parity without a new rule architecture.

## DoT interaction

Pinned donor `dnsfilter_support_dot()` considers:

- Custom 1;
- Custom 2;
- Custom 3

potentially DoT-capable.

The IPv6 DoT rule generator therefore permits TCP/853 only toward the resolved custom IPv6 server for those modes and rejects other destinations.

The final ASUS merge must preserve whatever later ASUS DoT/DNS Director bypass-prevention design already exists.

Do not downgrade newer ASUS handling merely to match donor rule text.

## WebUI contract

The existing project DNS Director page already owns Custom 1–3 IPv4 UI.

Once backend/default support is built, add one IPv6 input adjacent to each custom IPv4 input:

- Custom 1 → `dnsfilter_custom61`;
- Custom 2 → `dnsfilter_custom62`;
- Custom 3 → `dnsfilter_custom63`.

Pinned donor behavior:

- only show the IPv6 inputs on HND-capable targets;
- max length 39;
- validate each nonempty value with IPv6 validation;
- use normal `restart_dnsfilter` apply flow.

The current project page should be patched minimally rather than replaced wholesale by donor `DNSDirector.asp`.

## Apply/storage boundary

Before exposing fields, source/default handling must guarantee that the three keys survive:

- form submission;
- NVRAM/default validation;
- reboot;
- DNSFilter restart.

Do not rely on arbitrary generic NVRAM writes if later ASUS HTTPD uses an allowlist/schema for these fields.

If the later ASUS source requires explicit HTTPD variable registration, add exactly these three keys.

## Required source patch surface

Expected minimum patch:

1. later ASUS defaults/schema:
   - add empty `dnsfilter_custom61/62/63` with IPv6-sized storage;
2. later ASUS DNSFilter resolver:
   - in the existing HND/AF_INET6 mode resolver, map Custom 1–3 to those keys;
3. HTTPD apply/schema:
   - only if required by current ASUS form handling;
4. current project DNS Director page:
   - add three IPv6 inputs + validation after backend support exists.

No changes are required to the ASUS 52334 DNSFilter mode numbering.

## Do not alter Router-mode behavior blindly

Pinned donor contains platform-specific handling around IPv6 Router mode, including comments about HND kernel checksum behavior on some later chipsets.

RT-AC86U is not those later chipsets.

M36 must not copy unrelated conditional Router-mode changes from donor source.

The source patch is only Custom 1–3.

## Validation gate

Before M36 becomes **SUCCESS**, prove:

1. existing DNS Director IPv4 behavior remains unchanged;
2. built-in IPv6 DNS Director modes remain unchanged;
3. Custom 1 with valid IPv6 server enforces that server globally;
4. Custom 2 does the same;
5. Custom 3 does the same;
6. per-client Custom 1–3 rules enforce the selected IPv6 server;
7. empty custom IPv6 value fails safely without generating invalid rules;
8. invalid IPv6 input is rejected in UI/backend;
9. settings survive reboot;
10. `restart_dnsfilter` applies changes without reboot;
11. TCP and UDP DNS behavior both remain correct;
12. existing DoT-bypass policy remains coherent for custom modes;
13. IPv4 custom address and IPv6 custom address are independently stored;
14. no ASUS `rc`, HTTPD, dnsmasq or firewall binary is transplanted;
15. existing DNS Director phase-1 guarded overlay tests remain green.

## Current classification

**NARROW SOURCE ADAPTATION + UI FOLLOW-UP**

The IPv6 rule engine is already present in ASUS 52334. M36 is not a full backend port; it is a three-key custom-server resolver/default/UI gap.
