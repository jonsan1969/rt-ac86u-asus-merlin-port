# JFFS/custom-script implementation gate

Status: **GATE ESTABLISHED**

## Inputs

- Runtime/hardware/security baseline remains official ASUS RT-AC86U `3.0.0.4.386_52334`.
- Merlin donor/reference remains `386.14_2` at `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`.
- `JFFS custom-script source delta map` run `36123084408` completed successfully.
- We do **not** claim to possess ASUS `52334` source.

## Verified Merlin source surface

The source map shows custom-script/config support spanning:

- `release/src/router/shared/scripts.c`
- `release/src/router/shared/shared.h`
- `release/src/router/rc/firewall.c`
- `release/src/router/rc/init.c`
- `release/src/router/rc/qos.c`
- `release/src/router/rc/qos_multiwan.c`
- `release/src/router/rc/rc_ipsec.c`
- `release/src/router/rc/services.c`
- `release/src/router/rc/snmpd.c`
- `release/src/router/rc/udhcpc.c`
- `release/src/router/rc/usb.c`
- `release/src/router/rc/vpn.c`
- `release/src/router/rc/wan.c`
- `release/src/router/rc/watchdog.c`

The mapped helper API is `run_custom_script()`, `run_postconf()`, `use_custom_config()` and `append_custom_config()`.

## Newer ASUS GPL intersection

The later ASUS GPL imports in Merlin materially modify the same core files. The `386_52796` import intersects `firewall.c`, `init.c`, `services.c`, `udhcpc.c`, `usb.c`, `wan.c`, `watchdog.c`, `defaults.c` and `shared.h` (1513 insertions / 775 deletions across the mapped intersection). The `386_52805` import additionally touches `init.c` and `shared.h`.

Therefore old Merlin core objects or whole source files are not safe substitutes for the ASUS 52334 runtime.

## Implementation decision

### Allowed now

1. Preserve the verified ASUS 52334 rootfs/core binaries as the baseline.
2. Port image-level, additive support only where it does not require replacing or binary-patching `rc`, `httpd`, kernel/HND, BusyBox, dnsmasq, OpenVPN, Dropbear, OpenSSL or proprietary components.
3. Continue extracting exact Merlin helper/hook contracts and prepare source-level patch sets against a sufficiently close/newer ASUS GPL source tree.
4. Keep every future overlay fail-closed with preimage hashes and exact change-set validation.

### Blocked until a suitable ASUS source base is available

Full lifecycle JFFS/custom-script compatibility (`init-start`, `services-start`, `services-stop`, `service-event`, `service-event-end`, `nat-start`, `firewall-start`, `wan-event`, `wan-start`, `dhcpc-event`, `pre-mount`, `post-mount`, `unmount`, `qos-start`, etc.) must **not** be implemented by replacing the ASUS 52334 `rc` binary with Merlin's older `rc` or by blind binary patching.

The implementation target is source-level integration into the closest usable ASUS GPL baseline, followed by rebuild/ABI validation against the ASUS 52334 firmware baseline. Until then, these lifecycle hooks remain explicitly gated rather than silently emulated.

## Next executable work

The next port work is to split the JFFS plan into two manifests:

- **image-safe/additive candidates**: files/settings/UI/init assets that can be proven independent of core-binary replacement;
- **source-required candidates**: helper API and lifecycle call-sites that require compilation into ASUS-side core components.

No broad GPL search is required for this split; use the already verified source-delta map and existing three-way inventory.
