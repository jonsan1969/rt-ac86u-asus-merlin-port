# Core feature signature probe

Date: 2026-09-24

Compared selected strings in the verified runtime binaries from:

- ASUS RT-AC86U `3.0.0.4.386_52334`
- Asuswrt-Merlin RT-AC86U `386.14_2`

Action run: `35984546389` — **SUCCESS**

String presence is useful evidence of implementation overlap. String absence is **not** proof that code or behavior is absent.

## Result matrix

| Binary | Signature | ASUS 52334 | Merlin 386.14_2 |
|---|---|---:|---:|
| `/sbin/rc` | `/jffs/scripts` | 0 | 1 |
| `/sbin/rc` | `service-event` | 0 | 2 |
| `/sbin/rc` | `service-event-end` | 0 | 1 |
| `/sbin/rc` | `firewall-start` | 1 | 1 |
| `/sbin/rc` | `services-start` | 0 | 1 |
| `/sbin/rc` | `services-stop` | 0 | 1 |
| `/sbin/rc` | `nat-start` | 0 | 1 |
| `/sbin/rc` | `wan-start` | 0 | 1 |
| `/sbin/rc` | `dnsfilter_enable_x` | 1 | 1 |
| `/sbin/rc` | `dnsfilter_rulelist` | 1 | 1 |
| `/sbin/rc` | `DNSFILTER` | 36 | 34 |
| `/sbin/rc` | `authorized_keys` | 1 | 1 |
| `/usr/sbin/httpd` | `vpndirector_rulelist` | 0 | 1 |
| `/usr/sbin/httpd` | `DNSFILTER` | 0 | 1 |
| `/usr/sbin/httpd` | `dnsfilter_modes_list` | 1 | 1 |
| `/usr/bin/dropbearmulti` | `authorized_keys` | 2 | 4 |

## DNS Director finding

ASUS 52334 clearly contains a DNSFilter backend family:

- `dnsfilter_enable_x`
- `dnsfilter_rulelist`
- `dnsfilter_modes_list`
- `DNSFILTER`
- `DNSFILTERI`
- `DNSFILTERF`
- `DNSFILTER_DOT`

Examples in ASUS `/sbin/rc` include:

- `:DNSFILTER - [0:0]`
- `:DNSFILTERI - [0:0]`
- `:DNSFILTERF - [0:0]`
- `:DNSFILTER_DOT - [0:0]`

The ASUS root filesystem does **not** contain Merlin's `/www/DNSDirector.asp`.

### Revised port rule

Do **not** begin by transplanting Merlin's `rc/dnsfilter.c` or Merlin's `rc` binary.

Instead:

1. preserve the ASUS 52334 DNSFilter implementation;
2. verify its NVRAM schema, modes and rule encoding against Merlin 386.14_2;
3. verify firewall/dnsmasq behavior compatibility;
4. add/adapt the Merlin DNS Director WebUI only where the ASUS implementation does not already expose equivalent functionality;
5. port only any missing Merlin-specific backend delta that is demonstrated by comparison.

This changes DNS Director from an assumed B/C backend port into an **ASUS-backend-first compatibility/adaptation task**.

## VPN Director finding

`vpndirector_rulelist` is present in Merlin `httpd` but not in ASUS 52334 `httpd`.

Combined with the Merlin source map, this remains strong evidence that VPN Director is a genuine Merlin feature delta involving:

- `libovpn/openvpn_config.c`
- `libovpn/openvpn_control.c`
- `httpd/web.c`
- WebUI and defaults/NVRAM integration

VPN Director therefore remains a source-level B/C port target.

## JFFS/custom-script finding

The selected ASUS `rc` binary lacks these direct Merlin signatures:

- `/jffs/scripts`
- `service-event`
- `service-event-end`
- `services-start`
- `services-stop`
- `nat-start`
- `wan-start`

Merlin has them.

ASUS `rc` does contain `firewall-start`, so that single signature must be investigated before assuming whether it is a compatible custom-script hook or an unrelated internal event string.

Overall, JFFS/custom scripts remain a genuine Merlin port target.

## SSH finding

ASUS 52334 `rc` already contains `/root/.ssh/authorized_keys`, and its Dropbear binary supports authorized_keys.

Therefore Merlin SSH work should start with a behavioral/configuration comparison, not by assuming stock ASUS lacks public-key support.

## Consequence for port ordering

The refined order is now:

1. JFFS/custom-script framework and service hooks.
2. postconf/custom-config support.
3. addon/user-page/AMTM plumbing.
4. **DNS Director compatibility analysis against the existing ASUS 52334 backend.**
5. VPN Director source-level port.
6. SSH behavior comparison and only missing Merlin deltas.
7. remaining UI/features.

No runtime string result authorizes replacing ASUS core binaries with Merlin binaries.
