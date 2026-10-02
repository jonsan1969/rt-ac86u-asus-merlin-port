# Candidate promotion gate

A CI-produced `UNVALIDATED` firmware is a development artifact, not a flash recommendation.

## Promotion prerequisites

All of the following must be recorded against the exact candidate SHA-256:

1. software repack gate PASS: exact 570-PEB UBI, valid WFI/trailer/CRC and zero unauthorized semantic drift;
2. protected ASUS 52334 core byte-identity PASS;
3. no K2/K3 optional kernel module leakage into the immutable image;
4. K4a read-only preflight collected from an actual ASUS RT-AC86U running the 386_52334 runtime;
5. candidate module families that are intended for use pass `docs/k4-controlled-module-validation.md` before activation; K4 is deliberately operator-controlled because it mutates live kernel state;
6. general runtime feature preflight collected from the same 52334 runtime;
7. runtime-sensitive WebUI/JFFS features pass their own contracts before they are advertised as available; M49 specifically requires HTTPD EJ-dispatch proof;
8. configuration/JFFS backup and recovery path are prepared before first candidate flash, following `docs/preflash-backup-recovery.md`; the procedure is documented now, but physical backup completion must be recorded before any firmware change;
9. project status explicitly promotes the exact candidate hash from UNVALIDATED to hardware-tested.

## Fail closed

A candidate must remain UNVALIDATED if any prerequisite is missing, ambiguous, collected from Merlin 386.14_2 instead of ASUS 386_52334, or belongs to a different candidate hash.

Passing CI alone is never sufficient for flashability.

## Evidence preparation

Run `scripts/prepare-candidate-evidence.sh <candidate-UNVALIDATED.w> <evidence-dir>` before collecting hardware evidence. CI run `36924149359` validates that this helper is non-mutating and rejects candidates that are not explicitly marked UNVALIDATED.

## Current quarantined candidate

Run `36924014278` produced the first end-to-end software-gated candidate. Exact `.w` identity: `eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3` (78,250,004 bytes). This remains **UNVALIDATED** and may not be promoted using evidence from any other image hash.


## Preserved hardware-validation bundle

Run `36967617052` re-downloaded and re-verified the exact current validation inputs and republished them as one 90-day artifact:

- artifact: `hardware-validation-bundle-eac8a777`;
- artifact id: `11209744574`;
- artifact ZIP digest: `sha256:48ea093a26a854955aa61726cdaec26b4feaac7b78fdbfe4ce991991c600db7a`;
- expires: `2026-12-31T05:08:36Z`;
- candidate inside: exact `.w` SHA-256 `eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3`, size `78,250,004` bytes;
- K2 source run: `36556899650`;
- K3 source run: `36561957525`.

The workflow first downloads and verifies the official ASUS 386_52334 stock image (`1b4fe984...7483f`, 78,250,004 bytes), then verifies the candidate hash/size, K2 module count and representative hashes, and the full expected K3 family plus representative hashes before publishing the bundle. The bundle also carries the current collectors and recovery/handoff documents.

The artifact ZIP digest is only the GitHub archive digest. It must never be substituted for the firmware `.w` hash when binding hardware evidence.
