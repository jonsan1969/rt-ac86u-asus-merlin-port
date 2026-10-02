# Pre-flash backup and rollback preparation

Date: 2026-10-02

This document prepares the **future** physical validation phase. It does not authorize flashing the current candidate.

Current candidate identity:

`eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3`

Current router state before the physical phase:

- RT-AC86U;
- running Asuswrt-Merlin 386.14_2;
- not yet providing ASUS 386_52334 K4/runtime evidence.

## Safety boundary

Backup material is for rollback and recovery only. It is **not** valid ASUS-52334 or candidate runtime evidence.

Do not restore Merlin NVRAM/configuration or JFFS content into stock ASUS 386_52334 or an UNVALIDATED candidate merely to make validation convenient. A runtime gate must be evaluated on the intended runtime state, not on state imported from another firmware lineage.

Backup archives may contain passwords, keys, VPN material, DDNS credentials and addon configuration. Keep them off the public repository and out of GitHub Actions artifacts.

## Before any future firmware change

Prepare all of the following while the known-good Merlin 386.14_2 installation is still available:

1. Export the current firmware configuration using the running firmware's normal configuration-backup UI. Store the export off-router.
2. Make a separate JFFS archive and copy it off-router. A conservative SSH-side example that writes only below `/tmp` is:

   ```sh
   umask 077
   mkdir -p /tmp/rtac86u-preflash-backup
   tar -cpf /tmp/rtac86u-preflash-backup/jffs.tar -C /jffs .
   sha256sum /tmp/rtac86u-preflash-backup/jffs.tar > /tmp/rtac86u-preflash-backup/jffs.tar.sha256
   ```

   Copy both files to secure off-router storage and remove the temporary router copy after confirming the transfer.

3. Retain a known-good copy of the currently running Merlin 386.14_2 firmware image and its verified project hash.
4. Retain the official ASUS 386_52334 image used by this project and its verified image SHA-256:

   `1b4fe984e13afdf0a69c11bda759f3222822e12f5b8c929da33f334f2cc7483f`

5. Keep a wired management path available. Wireless-only recovery is not an acceptable rollback plan.
6. Record a small private manifest containing:
   - backup date;
   - router model;
   - current firmware/version;
   - configuration-backup filename + SHA-256;
   - JFFS archive filename + SHA-256;
   - known-good rollback firmware filename + SHA-256.

## Rollback principle

If a future test loses normal management access or exhibits instability, stop validation and return to a known-good firmware using the device's established ASUS recovery/rescue path.

Only after the matching known-good firmware is restored should its matching configuration backup be considered for restore. JFFS content should likewise be restored only to the firmware environment for which that backup was taken, and only after basic router operation is confirmed.

Do not use rollback restoration as a way to continue a failed K4 family. A K4 STOP/FAIL remains a failure until separately understood.

## Candidate evidence directory

The candidate evidence directory prepared by `scripts/prepare-candidate-evidence.sh` should record that backup/recovery preparation is complete, but the backup files themselves should remain outside the repository and outside public CI artifacts.

The current hardware-validation bundle from run `37011499307` (artifact `11228371174`, ZIP SHA-256 `3b2959753b5464cc4e05f0cbd13cfdac6aaeba0ddcb0e1cade6bc08cf473c50a`) preserves the verified official ASUS 386_52334 stock image, exact UNVALIDATED candidate, K2/K3 inputs, temporary K4 companions, isolated family staging packages and current validation runbooks. Its internal manifest SHA-256 is `fc6825056f8270db4f8d876c208b0447a419744f526d0bece0f3f24f9b9f9e33`; external bundle verification is CI-green in run `37017852039`, and normalized pre-K4 orchestration is CI-green in run `37020619484`. It does not replace the private rollback backups described here.

## Promotion implication

Promotion prerequisite 8 is considered **prepared/documented** when this procedure is available. It is not considered **physically satisfied** until the operator has actually created and secured the backups before the first firmware change.
