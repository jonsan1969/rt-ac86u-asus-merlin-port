# JFFS backup/restore source integration contract

Date: 2026-09-28  
Feature inventory IDs: M10, M60  
Runtime baseline: ASUS RT-AC86U 3.0.0.4.386_52334  
Clean ASUS source anchor: 386.45956 @ `a9179fc9329565dea0f7c5c7648fe8ad49ceaaf6`  
Merlin donor: 386.14_2 @ `6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b`

## Goal

Provide authenticated WebUI backup and restore of the persistent JFFS partition for addon/config portability without importing Merlin's old unsafe restore implementation.

M60 is the dependency-order alias for the same feature surface as M10 and does not receive a separate backend.

## Donor behavior

Pinned Merlin adds a **JFFS Partition** section to `Advanced_SettingBackup_Content.asp`.

The UI is hidden when:

`jffs2_on != 1`.

### Backup

The donor GETs:

`backup_jffs.tar`

The authenticated HTTP handler executes conceptually:

`tar cf /tmp/backup_jffs.tar -C /jffs .`

serves that file, then unlinks the temporary archive.

### Restore

The page accepts a `.tar` upload field named `file2` and posts to:

`jffsupload.cgi`.

The old donor backend:

1. writes the multipart body to `/tmp/backup_jffs.tar`;
2. checks only that the resulting file size is greater than 10 bytes;
3. runs `rm -rf /jffs/*`;
4. runs `tar -xf /tmp/backup_jffs.tar -C /jffs`;
5. removes the upload;
6. reports completion.

That behavior is functionally useful but is **not acceptable as the final restore implementation** because it destroys current state before validating the archive and relies on unrestricted tar extraction of uploaded content as root.

## Existing ASUS SAVEJFFS framework

Clean ASUS 386.45956 source already contains a separate, disabled framework:

`RTCONFIG_SAVEJFFS`

with:

- `JFFS_CFGS_HDR = "JCFG"`;
- `append_jffs_cfgs()`;
- `restore_jffs_cfgs()`;
- integration into normal settings backup/upload.

However, `config_base` has `RTCONFIG_SAVEJFFS is not set`.

The visible 45956 implementation only packages a **small whitelist** of router-owned JFFS data into the settings profile, such as feature-specific permission/customization/usericon directories when compiled.

It deliberately warns against large JFFS data because `/tmp` RAM is limited.

Therefore ASUS SAVEJFFS is a useful design/provenance reference but does **not** provide full addon-JFFS backup parity.

The `jffs_cfgs.c` implementation itself is not present as clean source in the inspected mirror, so it must not become an opaque dependency for the full addon backup feature unless a later source package supplies it.

## Project design decision

M10/M60 will use:

- ASUS's existing authenticated settings-page/upload architecture and later HTTPD conventions;
- Merlin's user-facing concept of a separate full-JFFS backup/restore action;
- a **new hardened archive validation/extraction path**.

Do not copy the donor's destructive restore routine unchanged.

## Backup contract

The backup endpoint must:

1. require normal authenticated WebUI access;
2. be available only when persistent JFFS is mounted/enabled;
3. generate an archive rooted at `/jffs` with **relative paths only**;
4. store the temporary archive outside `/jffs`, preferably `/tmp`;
5. set a deterministic attachment filename such as:
   `backup_jffs_RT-AC86U_<date>.tar`;
6. use no-cache response semantics;
7. remove the temporary archive after transfer;
8. fail cleanly when `/tmp` lacks sufficient space;
9. never shell-interpolate user-controlled path or filename data.

The archive should include the full persistent JFFS namespace needed by addons, including hidden entries, unless a path is explicitly documented as transient or unsafe to restore.

## Restore preflight contract

**No existing JFFS file may be deleted before all preflight checks pass.**

The upload path must enforce:

1. authenticated request;
2. persistent JFFS enabled/mounted;
3. explicit maximum upload size derived from safe `/tmp` capacity;
4. regular tar archive header validation;
5. every archive pathname is relative;
6. reject empty, absolute or root-prefixed paths;
7. reject `..` path components;
8. reject control characters and malformed names;
9. reject device nodes, FIFOs and other special files;
10. reject hardlinks unless a safe bounded implementation is deliberately added;
11. validate symlink targets and do not permit a link to escape the restore root;
12. reject entries that could overwrite the archive/upload or router filesystem outside JFFS;
13. validate aggregate extracted size against target free-space policy;
14. validate entry count/path-length bounds to avoid resource exhaustion.

The generated backup format should be the primary supported restore format. Arbitrary third-party tar variants do not need to be accepted.

## Safe extraction design

Preferred implementation is a small source-side extractor/helper that processes the validated archive using directory-relative operations.

Security requirements:

- hold a directory FD for the JFFS restore root;
- create directories and regular files with `openat()`/`mkdirat()`-style relative operations;
- use `O_NOFOLLOW` where available;
- never resolve an archive pathname from filesystem root;
- do not follow archive-created symlinks while writing later regular files;
- if symlinks are supported, create them only after regular files/directories have been safely materialized or otherwise guarantee no traversal through them;
- never execute restored content during extraction.

A direct `tar -xf <uploaded-root-controlled-file> -C /jffs` is not the preferred final design.

## Commit/rollback behavior

Because duplicate staging of a full JFFS tree may exceed RAM/flash capacity, full atomic replacement may not be practical.

Minimum safe sequence:

1. fully validate uploaded archive in `/tmp`;
2. verify space/resource bounds;
3. acquire a dedicated restore lock;
4. quiesce addon lifecycle execution as far as the current architecture permits;
5. create a small rescue/metadata marker for interrupted restore detection;
6. only then clear the existing restore scope;
7. extract through the safe path;
8. fsync/sync persistent storage;
9. remove restore marker;
10. reboot after successful full-JFFS restore.

If extraction fails after destructive replacement starts, the UI/log must clearly report restore failure and the next boot must not silently claim success.

## Scope of deletion

Unlike donor `rm -rf /jffs/*`, the implementation must handle hidden files/directories too.

A full restore must define whether it replaces:

- the complete contents of `/jffs`; or
- a documented addon/user-data subset.

For Merlin parity, the target is **complete user-visible persistent JFFS content** while preserving filesystem mount internals.

Never use a glob whose semantics accidentally omit dotfiles.

## Lifecycle interaction

After M01-M04 are present, restore must prevent user scripts from firing against a half-restored tree.

Recommended behavior:

- set/hold a restore-in-progress state/lock;
- do not invoke custom lifecycle hooks during destructive restore;
- reboot on successful completion;
- normal boot then re-enters addon lifecycle from a coherent restored JFFS tree.

## UI contract

Add the JFFS section to the existing ASUS settings backup page, preserving the later ASUS layout.

Controls:

- **Backup JFFS partition** — download action;
- **Restore JFFS partition** — file picker + upload;
- clear warning that restore replaces persistent JFFS content and reboots;
- hide/disable when JFFS is not enabled/mounted.

Client-side extension checks are convenience only; security validation belongs in the authenticated backend.

## Relationship to ASUS settings backup

Do not overload the normal ASUS configuration profile with the full addon JFFS tree.

Reasons:

- large addon data can exceed the intended settings-profile/`/tmp` assumptions;
- restoring router NVRAM and restoring arbitrary addon files are different risk domains;
- a dedicated full-JFFS archive gives clearer failure handling and user intent.

ASUS `RTCONFIG_SAVEJFFS` may remain useful for its original small router-owned whitelist if later ASUS enables it.

## Validation gate

Before M10/M60 become **SUCCESS**, prove:

1. backup requires authentication;
2. unauthenticated endpoint access fails;
3. backup contains hidden and normal JFFS user data as intended;
4. temporary backup is deleted after transfer;
5. oversized upload is rejected before destructive action;
6. absolute-path tar entries are rejected;
7. `../` traversal entries are rejected;
8. symlink-escape archives are rejected;
9. special device/FIFO entries are rejected;
10. invalid/truncated tar leaves existing JFFS unchanged;
11. valid restore replaces the documented scope including dotfiles;
12. restored executable bits required by `/jffs/scripts` are preserved;
13. restore is serialized against another restore/backup operation;
14. successful restore reboots and starts with coherent M01-M04 lifecycle state;
15. failed restore is visible in logs/UI and does not falsely report success;
16. normal ASUS settings backup/restore remains unchanged.

## Current classification

**SOURCE-REQUIRED / HARDENED ADAPTATION**

The UI concept and archive semantics come from Merlin, but the old donor restore code must not be transplanted as-is. Existing ASUS SAVEJFFS source proves ASUS already had JFFS-aware backup machinery, but it is partial and disabled at the clean source anchor.
