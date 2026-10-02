# KoolCenter 386.14_2 security review checkpoint

## Scope
Security review of KoolCenter RT-AC86U 386.14_2 versus official Asuswrt-Merlin 386.14_2 and later ASUS RT-AC86U stock firmware. This is not a continuation of the ASUS 52334 + Merlin port.

Candidate SHA-256: `0e640a4ac8f7b30a29485c26f14c3e564c9f391a4800333ffa21e67af021615e`.

## Verified findings
- KoolCenter follows the Merlin 386.14_2 generation, not later ASUS 51967/52294/52334 runtime lineage.
- `dnsmasq`, Dropbear and OpenVPN are byte-identical to official Merlin 386.14_2.
- KoolCenter `httpd`, `rc`, BusyBox, libcrypto, libcurl, lighttpd and miniupnpd differ from official Merlin.
- KoolCenter carries OpenSSL 1.1.1w versus 1.1.1k in the compared Merlin image. ELF dependency inspection confirms relevant binaries including `httpd` use the KoolCenter SSL/crypto libraries.
- Later ASUS firmware repeatedly changes core security-sensitive components. KoolCenter does not match that later lineage.
- KoolCenter removes components including `asd` and `awsiot`.
- KoolCenter adds privileged Koolshare/SoftCenter code plus persistent JFFS/bootstrap integration.
- Static inspection found no obvious separate SoftCenter-specific listener in 1.9.36 and no clear public/no-auth SoftCenter route. This is static evidence, not a dynamic penetration test.
- SoftCenter online package installation disables TLS certificate verification, checks MD5 supplied via metadata, then executes package `install.sh` with router privileges. No cryptographic publisher/package signature verification was found.
- ASUS firmware update handling subsequently performs firmware and RSA signature checks.
- Software Center 1.9.36 contains a KoolCenter-documented remote-file-manipulation fix; exact attack preconditions were not established.
- The KoolCenter httpd change includes a documented crash-related fix, but there is no evidence of a broad backport of later ASUS web/input-validation security changes.

## Minimal hardened-Merlin feasibility
Decision: **NO GO as a project** under the current time/cost constraint.

1. Replacing `httpd` or `rc` re-enters the tightly integrated ASUS/HND porting problem.
2. OpenSSL has broad dependency fan-out; a safe upgrade requires regression testing of multiple consumers.
3. `dnsmasq`, Dropbear and OpenVPN are more isolated, but updating them ourselves still requires new builds and compatibility/regression testing.
4. Updating those isolated daemons would not import later ASUS web/httpd/rc hardening and therefore does not solve the main age gap.

Reopen isolated component replacement only for a specific relevant high-severity vulnerability with a clear payoff.

## Practical interpretation
KoolCenter 386.14_2 is a security tradeoff, not ASUS 52334 security with Merlin features. It has genuine selective improvements, notably active OpenSSL 1.1.1w, removal of some cloud components and SoftCenter-specific fixes, while retaining old Merlin-generation network daemons and adding a privileged third-party package subsystem.

For a hardened deployment, treat the SoftCenter online plugin path as avoidable supply-chain surface. Keeping WAN administration disabled and not using SoftCenter packages materially reduces the practical exposure indicated by the static analysis, but does not remove KoolCenter code from the trusted computing base.

## Evidence workflows
- `.github/workflows/koolcenter-38614-security-delta.yml`
- `.github/workflows/asus-runtime-lineage-51967-52294-52334.yml`

Key successful runs: 36858101371, 36864579998, 37022744705, 37024597365, 37028589465, 37029776411, 37031418519, 37034570428.
