# RT-AC86U KoolCenter 386.14_2 hardened deployment profile

This profile assumes the reviewed KoolCenter RT-AC86U 386.14_2 image with SHA-256 `0e640a4ac8f7b30a29485c26f14c3e564c9f391a4800333ffa21e67af021615e`.

It is intended to retain Merlin functionality while minimizing practical exposure of this EOL firmware generation.

## Hard requirements

- WAN WebGUI / Web Access from WAN: **OFF**
- AiCloud: **OFF**
- SSH access from WAN: **OFF**
- WPS: **OFF**
- UPnP: **OFF unless a demonstrated application requires it**
- FTP server: **OFF unless explicitly required**
- Samba: LAN-only, no guest/anonymous access, and only if required
- Use a long unique router administrator password
- Do not expose router administration by port forwarding
- Remote router administration should traverse the VPN

## KoolCenter / SoftCenter

- Do not install online Software Center plugins.
- Do not treat the package MD5 check as publisher authentication.
- Do not manually remove /koolshare or modify kscore/rootfs merely to disable SoftCenter.
- No verified simple enable/disable switch was found that cleanly removes the bootstrap path.
- Keep JFFS custom-script functionality for trusted, locally controlled scripts only.
- Review every locally added JFFS script as privileged router code.

## OpenVPN server role

OpenVPN is the preferred intentional WAN-facing management entry point for this deployment.

Verified characteristics:
- KoolCenter and official Merlin 386.14_2 contain the same OpenVPN executable.
- The executable dynamically links against system libssl/libcrypto.
- On KoolCenter it therefore uses the reviewed KoolCenter OpenSSL 1.1.1w libraries at runtime.
- The binary contains support for TLS minimum-version controls, tls-auth/tls-crypt vocabulary, negotiated/data ciphers and AES-GCM-class options.
- The 386 GUI/config-generation path supports the established OpenVPN cipher/HMAC/TLS-key model. Do not depend on tls-crypt unless an exported client profile is explicitly verified to use it correctly.

### Conservative server settings

- Transport: **UDP**
- Authentication: certificates; do not rely on password-only remote access
- TLS minimum: **TLS 1.2**
- Data cipher: prefer **AES-256-GCM** or **AES-128-GCM** when offered by the GUI/client combination
- HMAC/control-channel digest: **SHA-256 or stronger** where selectable
- Static TLS key protection: use the GUI-generated **tls-auth** path when present in the exported client profile
- Compression: **disabled**
- Client-to-client access: **disabled unless specifically required**
- Push LAN routes only for networks the remote client actually needs
- Do not redirect all client Internet traffic through the router unless that is an intentional requirement
- Keep the number of VPN users/certificates minimal and revoke obsolete credentials
- Regenerate/export client profiles after material server-setting changes

### Custom Configuration

Use Custom Configuration only for directives confirmed absent from the generated configuration. Avoid duplicating cipher, auth or TLS-key directives already emitted by the ASUS/Merlin generator.

A candidate hardening directive is:
`tls-version-min 1.2`

Before deployment, inspect the generated server configuration or runtime log to confirm whether it is already emitted. Do not add duplicate/conflicting cipher policy merely for cosmetic hardening.

## Network/service exposure

- DDNS may remain enabled when needed to locate the VPN endpoint. DDNS is not permission to expose WebGUI.
- Do not forward management ports to the router.
- Disable unused VPN server types.
- Disable unused USB/network-sharing services.
- Prefer a guest/isolated network for untrusted IoT devices and prevent those clients from reaching router administration where the firmware configuration permits it.

## Operational rule

Treat the router as an EOL security boundary with minimized exposure:
1. Internet sees the normal routing/firewall surface plus the intentionally enabled VPN endpoint.
2. Router WebGUI and SSH are LAN/VPN management services, never direct WAN services.
3. SoftCenter online package execution is not part of the trusted operating workflow.
4. Configuration backups and known-good firmware are kept locally for recovery.

## Related review

See `docs/koolcenter-38614-security-review.md` for the firmware comparison and evidence behind this profile.
