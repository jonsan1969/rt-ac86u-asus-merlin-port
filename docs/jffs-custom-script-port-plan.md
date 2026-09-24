# JFFS custom-script framework — port specification

Date: 2026-09-24  
Feature inventory IDs: M01–M07, M41–M42  
Donor: Asuswrt-Merlin `386.14_2` @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Purpose

Restore Merlin's extensibility framework without replacing the later ASUS `rc` or other core binaries wholesale.

This specification is deliberately source-base independent. Exact ASUS `386_52334` source has not been obtained, so this document defines the **behavioral/source delta to port** rather than pretending that a build-ready 52334 patch already exists.

## Runtime evidence

The verified ASUS 52334 runtime does not expose the principal Merlin signatures:

- `/jffs/scripts`
- `service-event`
- `service-event-end`
- `services-start`
- `services-stop`
- `nat-start`
- `wan-start`
- postconf framework

The verified Merlin 386.14_2 runtime does.

Therefore this is a genuine Merlin feature block rather than a UI-only difference.

## Core helper layer

Merlin implements the reusable framework in:

- `release/src/router/shared/scripts.c`
- declarations in `release/src/router/shared/shared.h`
- NVRAM default in `release/src/router/shared/defaults.c`

Required helpers:

### `run_custom_script(name, timeout, arg1, arg2)`

Behavior to preserve:

1. resolve the target as `/jffs/scripts/<name>`;
2. do nothing if the file does not exist;
3. reject execution when `jffs2_scripts=0`;
4. reject non-executable scripts;
5. pass up to two optional arguments;
6. support asynchronous execution when timeout is zero;
7. support blocking execution with a bounded wait when timeout is nonzero;
8. log clear reasons when a script is present but cannot be executed.

The current Merlin helper is the product of a mature sequence of Merlin changes:

- `10bc8c9e...` — legacy 380.68 helper imported into the NG tree;
- `61832839...` — second optional argument;
- `fbaeda81...` — bounded blocking wait;
- `c2389213...` — unified blocking/non-blocking helper.

### `run_postconf(name, config)`

Resolve `<name>.postconf` through the same custom-script executor and pass the generated config path as argument.

### `use_custom_config(config, target)`

When enabled, replace a generated config with `/jffs/configs/<config>`.

### `append_custom_config(config, fp)`

When enabled, append `/jffs/configs/<config>.add` to a generated config stream.

## Enable/disable contract

Add/preserve NVRAM:

`jffs2_scripts=0` by default.

Add Administration/System control:

**Enable JFFS custom scripts and configs**

Values:

- `1` = enabled
- `0` = disabled

The switch gates both custom scripts and custom configs.

## UBI/JFFS directory initialization

RT-AC86U is an HND/UBI target. Merlin's UBI path creates:

- `/jffs/scripts/`
- `/jffs/configs/`
- `/jffs/addons/`

all with directory mode `0755`.

This UBI-specific support was repaired in Merlin commit `275c13af...` ("fix JFFS custom scripts/config support on UBI models"). That behavior is directly relevant to RT-AC86U.

## Shell/addon environment

The login profile must preserve:

- `/opt/sbin`
- `/opt/bin`
- `/opt/usr/sbin`
- `/opt/usr/bin`

in `PATH`.

When present:

- source `/opt/etc/profile`;
- source `/jffs/configs/profile.add` only when `jffs2_scripts=1`.

This is part of Entware/addon friendliness and must be tested together with the JFFS framework.

## Event hook matrix

These are the Merlin 386.14_2 hook semantics to preserve.

| Hook | Source integration | Blocking | Arguments |
|---|---|---:|---|
| `init-start` | `rc/init.c` | no | none |
| `firewall-start` | `rc/firewall.c` | no | WAN interface |
| `services-start` | `rc/services.c` | no | none |
| `services-stop` | `rc/services.c` | no | none |
| `service-event` | `rc/services.c` | **yes, max 120s** | action, service |
| `service-event-end` | `rc/services.c` | no | action, service |
| `nat-start` | `rc/services.c` | no | none |
| `ddns-start` | `rc/services.c` | normally no | WAN IP |
| `wan-event` | `rc/wan.c` | no | WAN unit/state context |
| `wan-start` | `rc/wan.c` | no | WAN unit |
| `qos-start rules` | `rc/qos.c` | no | `rules` |
| `qos-start init` | `rc/qos.c` | **yes, max 120s** | `init` |
| `dhcpc-event` IPv4 | `rc/udhcpc.c` | no | event, `4` |
| `dhcpc-event` IPv6 | `rc/udhcpc.c` | no | event, `6` |
| `zcip-event` | `rc/udhcpc.c` | no | event |
| `pre-mount` | `rc/usb.c` | **yes, max 120s** | device, filesystem type |
| `post-mount` | `rc/usb.c` | **yes, max 120s** | mount point |
| `unmount` | `rc/usb.c` | **yes, max 120s** | mount point |
| `update-notification` | `rc/watchdog.c` | no | none |

### Important historical semantics

- `service-event` was introduced by Merlin commit `1de044ac...` as a blocking pre-service hook.
- `service-event-end` was added by `6e131ba3...` as a non-blocking post-event hook.
- `wan-event` was introduced by `24462245...`; later commits fixed its arguments while retaining legacy `wan-start`.
- `qos-start init` became blocking in `90fb2373...` so addon changes finish before QoS configs are applied.
- `pre-mount` gained filesystem type as its second argument in `16d6e24c...`.
- `dhcpc-event` gained explicit IPv4/IPv6 context in `8297baf1...`.

These details are API compatibility, not implementation trivia. Existing Merlin addons may depend on them.

## Custom config/postconf matrix

The helper layer is only useful if integrated after ASUS generates each service configuration. Merlin 386.14_2 wires it into, among others:

- `fstab`
- `passwd`
- `group`
- `shadow`
- `gshadow`
- `hosts`
- `dnsmasq.conf`
- `stubby.yml`
- `inadyn.conf`
- `mcpd.conf`
- UPnP config
- Avahi configs/services
- `vsftpd.conf`
- media-server config
- NFS `exports`
- `igmpproxy.conf`
- strongSwan/IPsec configs
- selected routing/QoS configs

### Porting rule

Do **not** copy Merlin's generator body.

For every service:

1. start with the newest ASUS generator available in the chosen build source;
2. find the final point after ASUS has written the configuration;
3. add only the matching `.add`, full replacement (where still safe), and/or postconf calls;
4. preserve ASUS permissions/chown/security handling;
5. do not re-enable a full-replacement path that Merlin itself disabled for correctness/security (for example Stubby replacement was intentionally removed; use `.add`/postconf instead).

## ASUS GPL merge interaction

Merlin's ASUS GPL history is important here.

The `386_52796` import changed several files that also contain hook call sites:

- `rc/firewall.c`
- `rc/init.c`
- `rc/services.c`
- `rc/udhcpc.c`
- `rc/usb.c`
- `rc/wan.c`
- `rc/watchdog.c`
- `shared/defaults.c`
- `shared/shared.h`

The `386_52805` incremental merge touched only:

- `rc/init.c`
- `shared/shared.h`

within this selected JFFS surface.

Consequence: **hook call sites are conflict-sensitive even though the hook API is conceptually small**. The final implementation must insert the calls into the later ASUS control flow, never replace these core files wholesale.

GitHub's compare endpoint caps large file lists, so absence from the returned `52796` file list is not by itself proof that a file was untouched. The source-history Action is used as an additional check.

## Proposed patch series

When a buildable ASUS-side source tree is selected, implement this block as a small ordered series:

1. **shared: add Merlin custom-script/config helper API**
   - helpers + declarations;
   - no service hooks yet.
2. **jffs: initialize scripts/configs/addons directories on UBI**
   - RT-AC86U path first;
   - verify permissions and persistence.
3. **webui/defaults: add jffs2_scripts control**
   - default disabled.
4. **rc: add lifecycle custom-script hooks**
   - init/services/service-event/NAT/WAN/firewall.
5. **rc: add DHCP/QoS/USB/update hooks**
   - preserve blocking semantics and arguments.
6. **rc: add custom config/postconf integration**
   - service by service, after comparison to ASUS generator.
7. **shell: restore profile.add and /opt environment**
   - prerequisite for addon/Entware compatibility.

Do not combine all seven into one giant patch.

## Validation gate

Before calling this feature block **SUCCESS**, a built image must pass at least:

1. `jffs2_scripts=0`: scripts and custom configs are ignored.
2. `jffs2_scripts=1`: executable hook scripts run.
3. non-executable scripts are rejected and logged.
4. blocking hooks wait but have a bounded timeout.
5. `service-event` gets correct action/service arguments.
6. `service-event-end` runs after the event.
7. IPv4/IPv6 `dhcpc-event` gets `4`/`6`.
8. USB hooks receive the expected mount/device arguments.
9. `.add` config fragments append correctly.
10. `.postconf` receives the generated config path.
11. full custom config replacement works only for explicitly supported configs.
12. `profile.add` is ignored when custom scripts are disabled.
13. `/opt/etc/profile` works for Entware.
14. ASUS 52334 networking, DNS/DHCP, firewall and USB behavior remains intact when no custom script is installed.

## Current status

**IN PROGRESS**

The behavioral patch specification is complete. The remaining prerequisite for an actual code patch is selecting and labeling the buildable ASUS-side source generation against which these small deltas will be applied.
