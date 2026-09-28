# OpenVPN DNS Exclusive source integration contract

Date: 2026-09-28  
Feature inventory ID: M38  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Merlin donor: 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Purpose

Restore Merlin's **OpenVPN DNS Exclusive** behavior without replacing ASUS 52334 OpenVPN, `rc`, `dnsmasq`, firewall binaries, or the newer ASUS OpenVPN WebUI/lifecycle.

This is a narrow routing/DNS behavior port. It is not permission to import Merlin's complete OpenVPN control stack.

## Source-base limitation

The clean ASUS 386.45956 archaeology mirror does not expose a comparable open `libvpn/openvpn_control.c` implementation for this behavior; that part of the ASUS tree is effectively prebuilt/opaque at that anchor.

Therefore:

- ASUS 45956 is **not** used as proof of an M38 source-equivalent baseline;
- pinned Merlin 386.14_2 defines the exact donor behavior;
- verified ASUS 52334 runtime evidence defines what the target already exposes;
- implementation still waits for a sufficiently late ASUS-compatible source path for the affected OpenVPN/routing integration.

Do not infer source equivalence from the older mirror.

## Verified ASUS 52334 target facts

Prior runtime probe `36383666065` established that ASUS 52334 retains the `vpn_client_adns` configuration surface but does not expose the Merlin helper behavior/signatures:

- `ovpn_set_exclusive_dns`;
- `ovpn_clear_exclusive_dns`;
- `ovpn_update_exclusive_dns_rules`.

ASUS 52334 also has a newer OpenVPN UI/lifecycle than the pinned Merlin donor. That later ASUS implementation remains authoritative.

## Donor contract

Pinned Merlin implements the behavior in:

- `release/src/router/libovpn/openvpn_control.c`;
- declarations and lock name in `release/src/router/libovpn/openvpn_control.h`.

The lock is:

`VPNROUTING_LOCK = "vpnrouting-dns"`.

### Activation condition

After the OpenVPN client resolver data has been generated, exclusive DNS rules are installed only when:

- routing mode is `OVPN_RGW_POLICY` **or** `OVPN_RGW_ALL`; and
- `adns == OVPN_DNSMODE_EXCLUSIVE`.

The donor then:

1. locks `VPNROUTING_LOCK`;
2. calls `ovpn_set_exclusive_dns(unit)`;
3. calls `ovpn_update_exclusive_dns_rules()`;
4. unlocks.

The ordering is part of the behavior contract because multiple VPN clients can each own a DNS interception chain.

## Per-client DNS chain

For OpenVPN client unit `N`, the donor creates:

`DNSVPNN`

in the IPv4 `nat` table.

It reads:

`/etc/openvpn/clientN/client.resolv`

and writes an executable cleanup/recreation script:

`/etc/openvpn/clientN/dns.sh`.

The generated script owns the port-53 interception rules for that client.

### Redirect-all mode

When `rgw == OVPN_RGW_ALL`:

1. read the first valid IPv4 `server=` entry from `client.resolv`;
2. add one DNAT rule in `DNSVPNN` to that DNS server;
3. ignore later DNS servers because the first DNAT target consumes matching traffic.

This forces all intercepted DNS queries through the selected VPN DNS server.

### Policy-routing mode

When `rgw == OVPN_RGW_POLICY`:

1. merge the client's VPN policy rules with WAN policy rules;
2. process enabled entries with a source and no destination;
3. validate source address/netmask;
4. for entries assigned to `OVPNN`, DNAT that source to the first valid VPN DNS server;
5. for entries assigned to `WAN`, insert a source-specific `RETURN` rule so those clients are explicitly excluded from VPN DNS interception.

The policy association is therefore part of DNS leak prevention and must remain consistent with the routing engine chosen for the final ASUS-based implementation.

## PREROUTING interception

The donor inserts both:

- UDP destination port 53;
- TCP destination port 53;

from `PREROUTING` into `DNSVPNN`.

Both protocols are required.

After writing the per-client script, the donor:

- closes files;
- marks `dns.sh` mode 0755;
- executes it.

## Multiple-client ordering

`ovpn_update_exclusive_dns_rules()` walks OpenVPN client units from the highest unit down to 1.

For every unit with an existing `dns.sh`, it removes and reinserts the TCP/UDP PREROUTING jumps so their final ordering is deterministic.

The pinned donor comment describes the intended order as OpenVPN client 1 first through the highest client last.

A later ASUS implementation may use a different routing architecture, but it must preserve equivalent deterministic precedence and must not leave stale or ambiguous port-53 interception order.

## Teardown semantics

`ovpn_client_down_handler(unit)` calls `ovpn_clear_exclusive_dns(unit)` before deleting the client resolver/config state.

`ovpn_clear_exclusive_dns(unit)`:

1. deletes UDP port-53 PREROUTING jump to `DNSVPNN`;
2. deletes TCP port-53 PREROUTING jump to `DNSVPNN`;
3. flushes the `DNSVPNN` chain;
4. deletes the chain;
5. removes `/etc/openvpn/clientN/dns.sh` when present.

Teardown must be idempotent enough for stop/restart/error paths and must not leave stale DNS redirection after a client goes down.

## dnsmasq interaction

Pinned Merlin's `ovpn_skip_dnsmasq()` treats a running redirect-all client in exclusive mode specially.

It skips normal DNS setup when a client has:

- an existing `client.resolv`;
- `rgw == OVPN_RGW_ALL`;
- `adns == OVPN_DNSMODE_EXCLUSIVE`;
- client state above STOP.

This prevents the normal resolver path from undermining the exclusive DNS interception.

The final port must review the later ASUS DNS/dnsmasq lifecycle rather than blindly copying this helper. Equivalent exclusivity is required; the exact later-ASUS integration point may differ.

## Required source patch surface

The final source patch should be limited to the later ASUS OpenVPN/routing integration that owns:

- OpenVPN client up/down events;
- client resolver material;
- policy-routing state;
- firewall/NAT rule installation;
- dnsmasq coordination.

Expected behavior additions are:

1. exclusive-mode activation test;
2. per-client DNS chain setup;
3. deterministic multi-client ordering;
4. complete teardown;
5. equivalent dnsmasq exclusion where required.

No Merlin OpenVPN executable, `libovpn.so`, `rc`, `dnsmasq`, or full donor WebUI is to be transplanted.

## Interaction with M40 / VPN Director

Pinned Merlin's policy-mode exclusive DNS logic consumes Merlin policy-routing rules, so M38 and M40 are related.

For this project:

- M38 redirect-all behavior may be independently portable once the later ASUS routing owner is known;
- M38 policy-mode behavior must be reconciled with the final M40/VPN Director routing design;
- do not graft Merlin `ovpncN`/VPN Director assumptions into ASUS merely to make M38 compile.

DNS leak prevention must follow the final routing policy source of truth.

## Validation gate

Before M38 becomes **SUCCESS**, prove at least:

1. exclusive mode is inactive unless the selected client is in a compatible routing mode;
2. UDP and TCP port 53 are both intercepted;
3. redirect-all uses the first valid pushed VPN DNS server;
4. policy-routed VPN clients use VPN DNS;
5. policy-routed WAN clients are excluded from VPN DNS interception;
6. multiple OpenVPN clients get deterministic rule precedence;
7. stopping/restarting a client removes all of its DNS rules and temporary script;
8. no stale `DNSVPNN` chain remains after failure/down paths;
9. normal ASUS DNS behavior remains unchanged when exclusive mode is off;
10. later ASUS OpenVPN, dual-WAN, DNS Privacy and firewall behavior does not regress;
11. M40/VPN Director policy ownership is consistent with the DNS policy rules.

## Current classification

**SOURCE-REQUIRED**

The donor behavior is now bounded precisely. The source-equivalent target integration point is still unavailable, so no binary-only or UI-only implementation is justified.
