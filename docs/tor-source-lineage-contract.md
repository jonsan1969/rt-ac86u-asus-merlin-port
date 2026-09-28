# Tor source-lineage and secure integration contract

Date: 2026-09-28  
Feature inventory ID: M28  
Dependencies: M29 local NTP server; M01/M04 custom-script/config framework for donor-compatible torrc customization  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Clean ASUS source anchor: 386.45956 @ `a9179fc9329565dea0f7c5c7648fe8ad49ceaaf6`  
Late source reference: Merlin 386.12_x @ `5b47ec64ce58d23c591e809d4cbad09d1121c4ea`  
Pinned feature donor: Merlin 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Decision

M28 is **not** a binary-only overlay and it is **not** a Merlin-only backend.

Clean ASUS 386.45956 already contains the complete Tor feature lineage behind disabled `RTCONFIG_TOR`:

- Tor source package and build target;
- `start_Tor_proxy()` / `stop_Tor_proxy()`;
- Tor NVRAM defaults;
- Tor account generation;
- transparent-proxy NAT rules;
- fail-closed IPv4 FORWARD DROP rules;
- `Advanced_TOR_Content.asp`.

The later port should therefore reconcile/re-enable this ASUS-lineage feature in a sufficiently late ASUS-compatible source tree while preserving all newer 52334 surrounding control flow.

The Tor executable itself must be the pinned 386.14_2 feature version or an explicitly reviewed newer security-equivalent source build. Never fall back to the much older ASUS 45956 Tor executable merely because its build source is available.

## Source lineage

### Clean ASUS 386.45956

`release/src/router/config_base`:

`# RTCONFIG_TOR is not set`

When `RTCONFIG_TOR=y`, the top-level router build includes `tor` and installs:

`tor/src/app/tor -> /usr/sbin/Tor`.

The clean ASUS Tor source declares:

`Tor 0.4.5.8`.

The clean ASUS backend already includes the same core NVRAM contract and transparent-proxy structure later retained by Merlin.

### Merlin 386.12 / ASUS GPL 386_51997 lineage

Merlin 386.12 retains the same feature surface after its documented merge with ASUS GPL 386_51997.

Its bundled Tor version is:

`0.4.7.13`.

This is structural evidence that the Tor backend survived the later ASUS GPL merge, not proof that unmodified ASUS 51997 shipped it enabled.

### Pinned Merlin 386.14_2 donor

Pinned donor Tor version:

`0.4.7.16`.

This is the project feature version baseline for M28.

Do not substitute the ASUS 0.4.5.8 Tor binary/source result as the runtime daemon.

## NVRAM contract

The ASUS lineage and pinned donor both define:

- `Tor_enable=0`;
- `Tor_socksport=9050`;
- `Tor_transport=9040`;
- `Tor_dnsport=9053`;
- `Tor_redir_list=""`.

The normal WebUI client picker stores MAC addresses in `Tor_redir_list`.

The backend parser also has legacy support for IP and IPv4 range values; do not broaden the new UI beyond the pinned donor UX merely because those parser branches exist.

## Tor account

When the feature is built, the source-side account generator adds a non-login service account:

`tor:x:65533:65533:tor:/dev/null:/dev/null`

and group:

`tor:*:65533:`.

The shadow/gshadow path must be reviewed in the final later ASUS account generator so the service account remains locked and non-login.

Do not create the Tor user dynamically with an addon script on every boot when the source build can preserve the existing ASUS-lineage account contract.

## Runtime configuration

Pinned donor `start_Tor_proxy()`:

1. stops any existing Tor process;
2. exits if `Tor_enable=0`;
3. creates `/tmp/torrc`;
4. restores a non-stale cached microdescriptor DB from `/jffs/.tordb` when available;
5. writes:
   - `SocksPort <Tor_socksport>`;
   - log to `/tmp/torlog`;
   - `VirtualAddrNetwork 10.192.0.0/10`;
   - `AutomapHostsOnResolve 1`;
   - `TransPort <lan_ipaddr>:<Tor_transport>`;
   - `DNSPort <lan_ipaddr>:<Tor_dnsport>`;
   - `RunAsDaemon 1`;
   - `DataDirectory /tmp/.tordb`;
   - `AvoidDiskWrites 1`;
   - `User tor`;
6. applies M04 custom-config semantics:
   - append `torrc.add`;
   - optional full `torrc` replacement;
   - blocking `torrc.postconf`;
7. launches `Tor -f /tmp/torrc --quiet`.

Stop behavior removes the log and may back up the Tor DB to `/jffs/.tordb`.

Preserve this sequencing where it remains valid against the final Tor version and later ASUS source.

## Binary/source build rule

Preferred M28 daemon path:

1. build pinned Tor 0.4.7.16 source with the target ASUS-compatible cross toolchain;
2. link against the **later ASUS 52334-compatible** OpenSSL/libevent/zlib runtime selected by the target build;
3. install only the Tor executable/additive assets required by the feature;
4. keep ASUS OpenSSL, libevent, zlib and all core libraries authoritative.

A prebuilt donor `Tor` binary may only remain as an intermediate compatibility artifact if its ELF ABI and every dependency have already been proven compatible. It is not the preferred final build when source rebuilding is available.

Never transplant donor OpenSSL or other supporting core libraries to make Tor run.

## IPv4 transparent-proxy contract

Pinned 386.14_2 generates Tor rules in the IPv4 iptables rule files.

When `Tor_enable=1` and the redirect list is empty, all LAN clients receive:

- UDP/53 REDIRECT to `Tor_dnsport`;
- UDP/123 REDIRECT to local UDP/123;
- TCP SYN outside the LAN class REDIRECT to `Tor_transport`.

When MAC clients are selected, those redirects are scoped to each selected MAC.

Legacy backend paths also support IPv4 source/IP-range selectors.

### Why local NTP is mandatory

The donor itself comments that UDP/123 redirection **requires an NTP server**.

Therefore M28 must not become activatable until M29 has a working local UDP/123 server.

M30 global NTP interception is not required for Tor because M28 installs its own selected-client UDP/123 redirects.

## Fail-closed IPv4 filtering

Pinned donor also inserts an IPv4 FORWARD DROP for Tor-selected clients after the redirect rules have captured the supported traffic.

Purpose, as documented in donor source:

- block traffic that cannot be routed through Tor;
- prevent UDP/ICMP or other non-proxied traffic from revealing the router/public IP.

This filtering is security-critical.

It must be generated **inside the source firewall build**, not added later by the asynchronous generic `firewall-start` hook.

Reason: ASUS can flush/rebuild firewall state. Re-adding Tor protection asynchronously after the rebuild would create a transient clear-network leak window.

The Tor NAT redirects and fail-closed filter rules must be committed as part of the same later-ASUS firewall-generation cycle as the rest of the rules.

## IPv6 scope and project hardening

Pinned Merlin 386.14_2 Tor transparent-proxy logic is **IPv4-only**:

- Tor redirect rules are written to the IPv4 NAT rule stream;
- the Tor FORWARD DROP is written to the IPv4 filter stream;
- the nearby `ip6tables` code belongs to other features such as DNSFilter/OpenVPN/WireGuard handling;
- `Advanced_TOR_Content.asp` contains no IPv6 warning or gating.

Therefore unmodified donor semantics can allow a Tor-selected dual-stack client to use IPv6 outside the IPv4 Tor proxy path.

That is unacceptable for this project's security baseline.

### Required hardening

The final M28 source integration must add an IPv6 **FORWARD DROP** for Tor-selected clients whenever IPv6 forwarding is enabled.

It does **not** attempt to transparently proxy IPv6 through Tor.

For the donor UI's normal MAC-based selectors:

- each selected MAC gets an IPv6 FORWARD DROP on the LAN ingress path.

For empty `Tor_redir_list` ("all clients"):

- IPv6 FORWARD from the Tor-covered LAN scope is dropped while Tor transparent proxying is enabled.

Router-local IPv6 traffic/management is not blocked by a FORWARD-only rule.

This intentionally means Tor-covered clients lose routed IPv6 connectivity rather than bypass Tor.

If a future UI exposes legacy IPv4 IP/IP-range selectors, it must not claim IPv6 leak protection unless equivalent client identity can be proven. Prefer keeping the pinned MAC-based UI.

## Firewall merge rule

Do not copy the old ASUS 45956 `firewall.c`.

On the later ASUS-compatible source:

1. locate the corresponding NAT-generation paths;
2. insert/reconcile the existing Tor IPv4 redirect block at the current correct rule ordering;
3. preserve later ASUS DNS Director, VPN, dual-WAN, HND/NAT acceleration and security logic;
4. locate the current IPv4 filter path and preserve the donor fail-closed DROP before the final generic LAN allow;
5. add the project IPv6 fail-closed DROP in the corresponding IPv6 FORWARD path;
6. ensure enabling/disabling Tor causes a synchronous firewall rebuild through the current ASUS service mechanism.

## Lifecycle

The existing ASUS-lineage `start_Tor_proxy()` / `stop_Tor_proxy()` behavior may be source-integrated into the later ASUS `rc` if the current control path is available.

Unlike M21 wsdd2, Tor is not a good candidate for a pure post-firewall addon reconcile because firewall atomicity/fail-closed behavior is part of the feature.

Generic JFFS M01/M04 remains useful for:

- `torrc.add`;
- full custom `torrc`;
- `torrc.postconf`;
- addon interoperability.

Do not make Tor daemon startup depend solely on an asynchronous post-firewall script.

## UI contract

Use the existing donor concept/page only after all backend pieces are functional.

Expose:

- Tor enable;
- SOCKS port;
- transport port;
- DNS port;
- redirect scope;
- MAC client list.

Apply must synchronously coordinate:

1. Tor stop/reconfigure/start;
2. firewall regeneration;
3. M29 availability check.

### Safety presentation

Because project hardening disables routed IPv6 for Tor-covered clients rather than proxying it, the UI should state that clearly.

Do not claim full native IPv6-over-Tor support.

## Validation gate

Before M28 becomes **SUCCESS**, prove:

1. ASUS 52334 core networking/security components remain the runtime base;
2. Tor executable is 0.4.7.16-equivalent source build or explicitly reviewed newer security build;
3. no old ASUS 0.4.5.8 Tor binary is used;
4. no donor OpenSSL/libevent/zlib replaces ASUS libraries;
5. Tor runs as locked non-login UID/GID 65533;
6. default disabled state produces no Tor process/rules;
7. enabled state generates donor-compatible torrc and applies M04 config/postconf ordering;
8. M29 local NTP is running before Tor transparent proxy can activate;
9. selected IPv4 client TCP traffic is redirected to TransPort;
10. selected IPv4 DNS goes to DNSPort;
11. selected IPv4 NTP goes to local UDP/123;
12. unsupported/non-proxied IPv4 forwarding is dropped for Tor clients;
13. firewall rebuild never leaves a post-rebuild window where Tor clients have unrestricted IPv4 forwarding;
14. selected Tor clients cannot bypass via routed IPv6: project-owned IPv6 FORWARD DROP is present;
15. disabling Tor removes both IPv4 and IPv6 Tor rules;
16. selected MAC list semantics match the pinned donor UI;
17. stale Tor DB handling does not damage unrelated JFFS content;
18. Tor restart/failure is logged and failure does not silently expose selected clients through clear IPv4/IPv6 paths.

## Classification

**SOURCE-REQUIRED / ASUS-LINEAGE FEATURE RE-ENABLE + SECURITY HARDENING**

M28 is not a new Merlin backend transplant. The backend already exists in clean ASUS lineage but is disabled. The final port must reconcile that feature into later ASUS source, build the pinned Tor generation against the later runtime, require M29, and close the donor's IPv6 bypass gap.
