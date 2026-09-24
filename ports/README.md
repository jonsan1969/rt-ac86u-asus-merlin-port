# Port overlays

This directory describes **selected Merlin functionality layered onto an extracted ASUS 52334 rootfs**.

The overlay mechanism is deliberately conservative:

- ASUS 52334 is the runtime baseline.
- A port entry is explicit and hash-pinned.
- New files default to **add-only**.
- Shared/core binaries are protected from accidental replacement.
- Kernel modules and hardware-sensitive files are protected.
- Every applied entry produces a provenance report.

The overlay layer is appropriate for pure/static additions and for UI files that can use an existing ASUS backend.

It is **not** permission to replace later ASUS implementations with Merlin binaries.

## Manifest

The active manifest is `ports/active.json`.

Each entry has:

- `type`: `copy` or `symlink`
- `source`: path inside the pinned Merlin source tree for a copy entry
- `target`: absolute target path inside the extracted ASUS rootfs
- `sha256`: expected source-file SHA-256 for copy entries
- `mode`: optional octal mode such as `0644`
- `policy`: normally `add_only`

For `add_only`, application fails if ASUS already has a file/symlink at the target path.

## Protected runtime paths

The port tool blocks replacement of sensitive paths unless a future, explicitly reviewed mechanism is added. Examples include:

- `/sbin/rc`
- `/usr/sbin/httpd`
- `/usr/sbin/dnsmasq`
- `/usr/sbin/openvpn`
- `/usr/bin/dropbearmulti`
- `/bin/busybox`
- `/lib/modules/`

This keeps the project aligned with the ASUS-first architecture.
