# VPN Director / OpenVPN policy routing source integration contract

Date: 2026-09-28  
Feature inventory IDs: M25, M40  
Related feature: M38 OpenVPN DNS Exclusive  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Merlin donor: 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Purpose

Restore Merlin 386.14_2 policy-based OpenVPN routing semantics while preserving ASUS 52334's newer OpenVPN binary, UI/lifecycle foundation, dual-WAN behavior, firewall baseline and HND runtime.

M25 and M40 are one routing backend:

- M25 = policy rule storage/UI ("VPN Director");
- M40 = routing-table/RPDB integration, tunnel lifecycle and killswitch semantics.

M38 DNS Exclusive must consume this same policy owner. Do not build a second independent policy parser for DNS.

## Donor routing modes

Pinned donor client routing values are:

- `0` = no Internet redirection;
- `1` = all traffic through VPN;
- `2` = VPN Director policy routing.

The enum also contains a legacy strict-policy value, but the 386.14_2 WebUI exposes only 0/1/2 and the active routing switch handles those three modes.

For this project, do not expose an unproven strict-policy mode merely because the enum value exists.

## Policy rule storage

Pinned Merlin stores VPN Director rules in:

`/jffs/openvpn/vpndirector_rulelist`

through the OpenVPN filesystem path, while the WebUI/default layer mirrors the rule list as:

`vpndirector_rulelist`

Rule encoding is:

`<enabled>description>source>destination>target`

Repeated rules are concatenated with `<`.

Fields:

1. enabled: numeric 0/1;
2. description;
3. source IPv4/CIDR or empty;
4. destination IPv4/CIDR or empty;
5. target:
   - `WAN`; or
   - `OVPN1` ... `OVPN5`.

Pinned UI limit: 199 rules.

The source backend filters this single list by target when building WAN or per-client rule sets.

## Persistence design for this project

Do not depend on the old donor's split NVRAM/JFFS implementation blindly.

Required behavior is:

- one authoritative policy-rule store;
- durable across reboot;
- readable by WebUI and routing backend;
- atomic enough that a partially written rule list cannot corrupt routing state;
- bounded size and rule count;
- validated before use.

Preferred final implementation is a JFFS-backed file under the existing ASUS 52334 OpenVPN persistent namespace, with the WebUI/API writing through a source-side validated handler.

If an NVRAM mirror is retained for compatibility, the JFFS file remains the canonical large-rule store.

## Routing tables

Pinned donor reserves named tables:

- `ovpnc1`;
- `ovpnc2`;
- `ovpnc3`;
- `ovpnc4`;
- `ovpnc5`.

The donor's pinned `rt_tables` maps these names to IDs 111-115.

The final ASUS-based build may use different unused numeric IDs if required by later ASUS tables, but the chosen mapping must be fixed, collision-free and documented.

Do not overwrite a later ASUS routing table assignment.

## Client table construction

On OpenVPN TUN client up, the donor:

1. flushes the client's `ovpncN` table;
2. copies the current main routing table into `ovpncN`;
3. applies OpenVPN-pushed routes into that table;
4. adds an explicit route for the remote VPN endpoint via the local WAN gateway;
5. when redirection is enabled, replaces the table default route with the VPN gateway;
6. installs RPDB rules;
7. flushes the route cache.

The later ASUS source path may already have richer route setup. Preserve it and add only the policy table/RPDB behavior that is missing.

## Policy rule priorities

Pinned 386.14_2 allocates:

- 10000-10009: clients using redirect-all;
- 10010-10209: WAN policy rules;
- 10210-10409: OpenVPN client 1 policy rules;
- 10510-10609: OpenVPN client 2;
- 10710-10809: OpenVPN client 3;
- 10910-11009: OpenVPN client 4;
- 11100-11209: OpenVPN client 5.

The exact donor comment contains these bands and `_write_routing_rules()` starts WAN at 10010 and each VPN client at:

`10010 + 200 * unit`.

Final implementation requirements:

- use a reserved deterministic range;
- never delete arbitrary ASUS or user RPDB rules;
- remove only rules owned by this feature;
- preserve rule ordering between WAN and VPN targets;
- document any changed priority range if later ASUS already occupies the donor range.

## Rule generation

For every enabled rule with at least source or destination:

- target `WAN` => table `main`;
- target `OVPNN` => table `ovpncN`.

Source and destination are translated into `ip rule from ... to ...` selectors.

Empty or `0.0.0.0` source/destination behaves as wildcard.

Rules with unsupported targets are ignored/rejected.

The final implementation must validate addresses/CIDRs before invoking `ip`; do not pass untrusted rule text through shell command construction.

Prefer direct argv execution or netlink over `system()` strings.

## Redirect-all mode

When a client is running or initializing and routing mode is redirect-all, donor routing installs:

`ip rule ... table ovpncN priority 10000+N`.

The later ASUS implementation must preserve its own client-up state machine while providing equivalent table selection.

## VPN Director mode

When routing mode is policy:

1. remove prior rules owned by that client;
2. refresh WAN-target rules;
3. load only rules targeting that OpenVPN client;
4. write source/destination RPDB selectors to `ovpncN`;
5. flush routing cache.

VPN Director applies only to TUN-style routed clients in the pinned UI. TAP clients are not offered policy mode.

Preserve that boundary unless later ASUS source proves a safe equivalent for TAP.

## Killswitch

Pinned donor uses:

`vpn_clientN_enforce`.

When enabled and the tunnel goes down, it changes the client's routing table default to:

`prohibit default`

instead of allowing that policy-routed traffic to fall back through WAN.

The donor calls the killswitch on client-down and during WAN/autostart transitions.

Requirements:

- only traffic already directed to that client table is blocked;
- WAN-target policy rules continue to use WAN;
- manual client stop must clear the client table/rules so the killswitch does not become an unintended permanent blackhole;
- autostart/reconnect must restore the correct state deterministically.

Do not implement the killswitch as a global LAN firewall drop if per-table behavior is available.

## Client stop/cleanup

Pinned manual stop:

1. stops the OpenVPN process;
2. clears owned RPDB rules;
3. flushes the `ovpncN` table, removing any prohibit default;
4. removes interface/firewall state;
5. updates client state.

Equivalent cleanup is mandatory.

Stale policy rules must not survive profile deletion, route-mode changes, client disable or reboot transitions.

## rp_filter

Pinned donor disables IPv4 reverse-path filtering in policy-routing mode because strict rp_filter can break asymmetric policy routing.

The final ASUS/HND implementation must review the actual 52334 kernel/network defaults.

Do not globally disable rp_filter without proving it is required. If disabling is necessary, scope it as narrowly as the target kernel permits and restore normal ASUS state when policy routing is no longer active.

## Interaction with M38 DNS Exclusive

M38 policy-mode DNS must consume the **same validated VPN Director rule set**.

Pinned donor behavior:

- rules targeted to `OVPNN` can receive DNAT to that VPN's pushed DNS;
- rules targeted to `WAN` get DNS bypass/RETURN behavior;
- only source-based rules without destination selectors participate in the donor DNS interception path.

The final backend should expose a shared parsed-rule representation to routing and DNS code rather than reparsing raw strings independently.

This avoids route/DNS divergence.

## Interaction with DNS Director

VPN Director and DNS Director are separate policy systems.

Validation must prove:

- VPN Director WAN/VPN routing choice does not silently bypass a user-selected DNS Director policy except where explicitly required by VPN DNS mode;
- M38 Exclusive mode has clearly defined precedence;
- DNS Privacy and ASUS dnsmasq behavior remain later-ASUS authoritative.

## UI integration

Preserve ASUS 52334's newer OpenVPN client UI.

Add only:

- routing mode option equivalent to "VPN Director (policy rules)" when the backend is present;
- per-client killswitch control;
- a dedicated VPN Director rule editor or equivalent modern ASUS-style page;
- rule status/client mapping.

Do not replace the entire ASUS OpenVPN page with Merlin's older page.

## Source patch boundary

Expected affected source ownership:

1. later ASUS OpenVPN client up/down integration;
2. routing policy helper module;
3. persistent rule-store API;
4. current WebUI/httpd API needed to read/write validated rules;
5. route-table naming/build assets;
6. M38 DNS integration against the same parser.

Do not replace:

- OpenVPN executable;
- ASUS `rc` wholesale;
- ASUS `libvpn` wholesale;
- dnsmasq;
- firewall binary;
- kernel/HND networking components.

## Safer implementation requirements

Where donor 386.14_2 uses `system()` with formatted strings, the new port should improve safety:

- validate every rule component;
- build commands as argv, or preferably use netlink APIs;
- use a dedicated feature lock around rule/table updates;
- write rule files atomically;
- enforce rule count/length bounds;
- fail closed on malformed rule entries;
- log rejected entries without applying partial unvalidated state.

## Validation gate

Before M25/M40 become **SUCCESS**, prove at minimum:

1. no-policy mode preserves stock ASUS routing;
2. redirect-all sends intended traffic to the selected VPN;
3. source-only VPN Director rule works;
4. destination-only rule works;
5. source+destination rule works;
6. WAN-target rule overrides VPN-target behavior according to documented priority/order;
7. disabled rules do nothing;
8. malformed addresses/CIDRs are rejected;
9. rules for disconnected clients behave according to killswitch setting;
10. killswitch enabled prevents policy-routed leak to WAN;
11. killswitch disabled permits documented fallback behavior;
12. manual client stop removes owned RPDB/table state;
13. client reconnect restores table and rules once, with no duplicates;
14. multiple clients have deterministic independent tables/priorities;
15. WAN reconnect/dual-WAN transition does not leave stale copied main-table routes;
16. M38 Exclusive DNS follows the same policy-rule owner;
17. DNS Director/DNS Privacy behavior remains coherent;
18. router management/LAN-local traffic is not accidentally blackholed;
19. ASUS 52334 OpenVPN binary and later UI/security behavior remain authoritative.

## Current classification

**M25 SOURCE-REQUIRED**  
**M40 SOURCE-REQUIRED**  
**M38 DEPENDS ON THIS POLICY OWNER FOR POLICY MODE**

The donor routing model is now bounded. Implementation remains blocked on a sufficiently late ASUS-compatible OpenVPN/routing source path.
