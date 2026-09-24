# Port overlays

This directory describes **selected Merlin functionality layered onto an extracted ASUS 52334 rootfs**.

The overlay mechanism is deliberately conservative:

- ASUS 52334 is the runtime baseline.
- A port entry is explicit and hash-pinned.
- New files are **add-only**.
- Shared/core binaries are protected from accidental replacement.
- Kernel modules and hardware-sensitive files are protected.
- Every applied entry produces a provenance report.

The overlay layer is appropriate for pure/static additions and for adapted UI files that can use an existing ASUS backend.

It is **not** permission to replace later ASUS implementations with Merlin binaries.

## Manifest

The active manifest is `ports/active.json`.

Each copy entry has:

- `type: "copy"`
- `source_kind: "merlin"` for an unchanged file from the pinned donor, or `"repo"` for a project-maintained ASUS-52334 adapter
- `source`: path relative to the selected source tree
- `target`: absolute path inside the extracted ASUS rootfs
- `sha256`: expected source-file SHA-256
- `mode`: optional octal mode such as `0644`
- `policy: "add_only"`

Symlink entries use `type: "symlink"`, `link_target`, `target` and `policy: "add_only"`.

For `add_only`, application fails if ASUS already has a file or symlink at the target path.

## Adapted files

Files under `ports/files/` are project-owned adaptations. They are used when a Merlin file cannot safely be copied unchanged onto ASUS 52334.

Every adapted file must document its donor and compatibility assumptions in the relevant port-plan document. The manifest pins its exact SHA-256.

## Protected runtime paths

The port tool blocks replacement of sensitive paths. Examples include:

- `/sbin/rc`
- `/usr/sbin/httpd`
- `/usr/sbin/dnsmasq`
- `/usr/sbin/openvpn`
- `/usr/bin/dropbearmulti`
- `/bin/busybox`
- OpenSSL runtime libraries
- all `/lib/modules/`

This keeps the project aligned with the ASUS-first architecture.
