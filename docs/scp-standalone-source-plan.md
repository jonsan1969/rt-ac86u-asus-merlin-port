# Standalone SCP adaptation plan

Date: 2026-09-28  
Feature inventory ID: M16  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Clean ASUS Dropbear lineage: 2020.81 in ASUS 386.45956 source  
Pinned Merlin donor Dropbear: 2022.83 in Merlin 386.14_2

## Result

M16 does **not** require replacing ASUS Dropbear or importing Merlin `dropbearmulti`.

Both the clean ASUS Dropbear source and the pinned Merlin Dropbear source support building `scp` as a **standalone executable**.

Their Makefiles explicitly define:

- `SCPOBJS=scp.o progressmeter.o atomicio.o scpmisc.o compat.o`;
- a standalone `scp` target;
- the comment: `scp doesn't use the libs so is special`.

This gives the project a safe narrow path for the missing SCP command.

## Why the current donor symlink is unusable

The Merlin image exposes `scp` through the Merlin Dropbear multicall binary.

ASUS 52334 does not expose the SCP applet in its protected Dropbear runtime.

Therefore:

- do not add a Merlin `scp -> dropbearmulti` symlink;
- do not replace ASUS `dropbearmulti`;
- do not replace ASUS `dropbear` or `dbclient`.

The missing command should be supplied as its own executable.

## SSH transport dependency

Both source generations define:

```c
#define DROPBEAR_PATH_SSH_PROGRAM "/usr/bin/dbclient"
```

and standalone `scp` executes that path for the encrypted transport.

This is ideal for the project: the new SCP binary can delegate SSH negotiation/authentication to ASUS's existing `/usr/bin/dbclient`.

The SCP binary therefore owns only SCP protocol/file-copy behavior, not the SSH transport implementation.

## Preferred build

Build a standalone SCP executable from the pinned Merlin Dropbear 2022.83 SCP source set against the ASUS-compatible aarch64 userspace/toolchain:

- `scp.c`;
- `progressmeter.c`;
- `atomicio.c`;
- `scpmisc.c`;
- `compat.c`;
- required headers/config generated for the target.

Do **not** enable `MULTI=1`.

Expected conceptual build target:

```sh
make PROGRAMS="scp" MULTI=0 SCPPROGRESS=1
```

The exact cross-build invocation must use the final ASUS-compatible toolchain/configure environment.

If the 2022.83 standalone source proves incompatible with the ASUS libc/toolchain, fall back to the ASUS-lineage standalone SCP source and carry only reviewed SCP-specific fixes from 2022.83. Do not solve a build issue by replacing the SSH runtime.

## Install target

Add-only:

`/usr/bin/scp`

Mode:

`0755`

No symlink to any multicall binary.

## Compatibility requirements

Before activation, prove:

1. target is AArch64 and uses an interpreter available in ASUS 52334;
2. every DT_NEEDED dependency exists in ASUS 52334;
3. no new libcrypto/libssl/dropbear shared library replacement is required;
4. `/usr/bin/dbclient` exists and is executable;
5. `scp -V`/usage path executes without loader errors;
6. local-to-remote transfer works against an external OpenSSH server;
7. remote-to-local transfer works;
8. recursive copy works;
9. preserve-times mode works;
10. filenames with spaces and shell metacharacters are handled according to SCP protocol behavior without introducing local shell injection;
11. failed SSH authentication exits nonzero;
12. ASUS SSH host keys, authorized_keys, password policy and server configuration remain untouched.

## Server-side SCP behavior

Classic SCP requires an `scp` executable on the remote side when the router is the destination/source for another SCP client.

Installing the standalone binary at `/usr/bin/scp` provides that server-side command as well.

The Dropbear SSH server should execute it as a requested remote command through its existing command-execution path.

Validation must test both directions:

- workstation -> router;
- router -> workstation.

## SFTP distinction

M16 is only SCP parity.

Do not add SFTP server/client functionality unless separately tracked and proven part of the pinned donor requirement.

## Security boundary

The SCP executable must not be setuid.

Preserve ASUS's SSH authentication and privilege model.

Do not weaken shell restrictions, root login policy or key permissions merely to make SCP work.

## Current classification

**B — ADD-ONLY SOURCE-BUILT STANDALONE SCP**

This supersedes the earlier vague B/C classification. No ASUS Dropbear core replacement is required.


## Reproducible build evidence

GitHub Actions run `36466679828` built the pinned Merlin Dropbear 2022.83 standalone SCP target with server password authentication disabled only in a local build override (SCP does not use Dropbear server authentication).

Verified artifact:

- ELF64 little-endian AArch64;
- statically linked;
- no PT_INTERP;
- size: 663424 bytes;
- SHA-256: `d47ec3eba8bde2e244b96feb47ed0fc26d4556de5aebfd3771822970c5754851`;
- embeds `/usr/bin/dbclient` as the SSH transport;
- QEMU usage path works;
- QEMU local-to-local copy with spaces in filenames works;
- remote path honors `-S` override and fails closed with a failing transport;
- a clean rebuild is byte-identical.

The build path is therefore no longer the M16 blocker. Remaining work is guarded add-only image integration and target-router SCP interoperability testing.
