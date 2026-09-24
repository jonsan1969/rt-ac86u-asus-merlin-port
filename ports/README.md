# Port overlays

This directory describes **selected Merlin functionality layered onto an extracted ASUS 52334 rootfs**.

The overlay mechanism is deliberately conservative:

- ASUS 52334 is the runtime baseline.
- Every port operation is explicit and hash-pinned.
- New files are **add-only**.
- Existing ASUS text files may only be modified by an **exact, base-hash-pinned text patch**.
- Shared/core binaries are protected from replacement or patching.
- Kernel modules and hardware-sensitive files are protected.
- Every applied entry produces a provenance report.

The overlay layer is appropriate for pure/static additions and for adapted WebUI files that can use an existing ASUS backend.

It is **not** permission to replace later ASUS implementations with Merlin binaries.

## Manifest

The active manifest is `ports/active.json`.

### Copy entries

- `type: "copy"`
- `source_kind: "merlin"` for an unchanged file from the pinned donor, or `"repo"` for a project-maintained ASUS-52334 adapter
- `source`: path relative to the selected source tree
- `target`: absolute path inside the extracted ASUS rootfs
- `sha256`: expected source-file SHA-256
- `mode`: optional octal mode such as `0644`
- `policy: "add_only"`

### Exact text patches

For a small reviewed modification to an existing ASUS text file:

- `type: "patch_text"`
- `target`: existing ASUS path
- `base_sha256`: exact SHA-256 of the unmodified ASUS 52334 file
- `find`: exact text to replace
- `replace`: reviewed replacement text
- `expected_count`: normally `1`
- optional `result_sha256`: expected hash after patching
- `policy: "exact_patch"`

The operation fails if the ASUS base hash or patch context does not match exactly. This prevents a patch written for one firmware generation from silently changing a different file.

## Adapted files

Files under `ports/files/` are project-maintained adaptations. They are used when a Merlin file cannot safely be copied unchanged onto ASUS 52334.

Every adapted file must document its donor and compatibility assumptions in the relevant port-plan document. The manifest pins its exact SHA-256.

## Protected runtime paths

The tool rejects both replacement and patching of sensitive paths. Examples include:

- `/sbin/rc`
- `/usr/sbin/httpd`
- `/usr/sbin/dnsmasq`
- `/usr/sbin/openvpn`
- `/usr/bin/dropbearmulti`
- `/bin/busybox`
- OpenSSL runtime libraries
- all `/lib/modules/`

Core changes require a separate source-level build path. This keeps the project aligned with the ASUS-first architecture.

## Exact text patches

Existing non-core text files may be modified only with `type: "text_replace"` and `policy: "patch_exact"`. The complete ASUS 52334 preimage SHA-256 and exact replacement count are mandatory. Any unexpected stock-file drift fails closed.
