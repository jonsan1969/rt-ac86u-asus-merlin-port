# Candidate promotion gate

A CI-produced `UNVALIDATED` firmware is a development artifact, not a flash recommendation.

## Promotion prerequisites

All of the following must be recorded against the exact candidate SHA-256:

1. software repack gate PASS: exact 570-PEB UBI, valid WFI/trailer/CRC and zero unauthorized semantic drift;
2. protected ASUS 52334 core byte-identity PASS;
3. no K2/K3 optional kernel module leakage into the immutable image;
4. K4a read-only preflight collected from an actual RT-AC86U on official ASUS 386_52334 before module testing, and again on the candidate runtime before final candidate-side activation; evidence pairs must be accepted by `scripts/verify-hardware-evidence.py` in the appropriate mode;
5. candidate module families that are intended for use pass `docs/k4-controlled-module-validation.md` before activation; K4 is deliberately operator-controlled because it mutates live kernel state;
6. general runtime feature preflight collected on candidate runtime and accepted with `--require-candidate-canaries`; a stock-only runtime archive is baseline evidence but does not satisfy candidate feature validation;
7. runtime-sensitive WebUI/JFFS features pass their own contracts before they are advertised as available; M49 specifically requires a saved authenticated candidate user-slot response that passes `scripts/verify-m49-ej-response.py` (`36969317440` validates the verifier itself);
8. configuration/JFFS backup and recovery path are prepared before first candidate flash, following `docs/preflash-backup-recovery.md`; the procedure is documented now, but physical backup completion must be recorded before any firmware change;
9. project status explicitly promotes the exact candidate hash from UNVALIDATED to hardware-tested.

## Fail closed

A candidate must remain UNVALIDATED if any prerequisite is missing, ambiguous, collected from Merlin 386.14_2 instead of ASUS 386_52334, or belongs to a different candidate hash.

Passing CI alone is never sufficient for flashability.

## Evidence preparation

Run `scripts/prepare-candidate-evidence.sh <candidate-UNVALIDATED.w> <evidence-dir>` before collecting hardware evidence. Latest CI run `36977544208` validates both host-verifier prerequisites (hardware evidence + K4 symbol-name preflight), non-mutating behavior and rejection of candidates not explicitly marked UNVALIDATED.

## Current quarantined candidate

Run `36924014278` produced the first end-to-end software-gated candidate. Exact `.w` identity: `eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3` (78,250,004 bytes). This remains **UNVALIDATED** and may not be promoted using evidence from any other image hash.


## Preserved hardware-validation bundle

Run `36977559328` re-downloaded and re-verified the exact current validation inputs and republished them as one 90-day artifact:

- artifact: `hardware-validation-bundle-eac8a777`;
- artifact id: `11214106455`;
- artifact ZIP digest: `sha256:399ad74f1456f63109301e16201fec32371753fc7500896515b9031b3b92fa66`;
- expires: `2026-12-31T07:14:50Z`;
- candidate inside: exact `.w` SHA-256 `eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3`, size `78,250,004` bytes;
- K2 source run: `36556899650`;
- K3 source run: `36561957525`.

The workflow first downloads and verifies the official ASUS 386_52334 stock image (`1b4fe984...7483f`, 78,250,004 bytes), then verifies the candidate hash/size, K2 module count and representative hashes, and the full expected K3 family plus representative hashes before publishing the bundle. It also verifies and carries the Unix-preserving ipset, WireGuard and Cake K4 userspace companions plus exact ELF dependency-closure report run `36976006891` and the K4 symbol-preflight verifier/docs validated by run `36977341893`; that report freezes artifact-internal load/unload ordering but does not replace real ASUS-52334 symbol/runtime validation. The bundle also carries the current K4/runtime collectors, host-side evidence verifier, M49 EJ response verifier, physical-validation sequence, recovery material instructions and current handoff/status documents.

The artifact ZIP digest is only the GitHub archive digest. It must never be substituted for the firmware `.w` hash when binding hardware evidence.

The bundle manifest records docs snapshot commit `40f5a4ece1b05b5b39f45e0504cde60226165a4c`. Later documentation-only updates that merely point back to the newly created artifact are expected self-reference deltas and do not change the candidate/module inputs.


## Evidence intake gate

Before any mutating K4 family test, run the host-side verifier described in `docs/hardware-evidence-verifier.md`.

Then run the read-only symbol-name gate in `docs/k4-symbol-preflight.md` against the same K4a archive plus the exact preserved K2/K3 modules and dependency-closure report. Require `K4_SYMBOL_PREFLIGHT_PASS` before any module load. CI run `36977341893` validates both fail-closed fixtures and the default project profile against the exact preserved 27-module set.

Latest evidence-verifier CI run `36968903989` validates both stock/baseline and candidate-canary modes. The gate intentionally rejects:

- a different embedded candidate SHA-256;
- Merlin 386.14_2 presented as ASUS 386_52334 evidence;
- missing `/proc/kallsyms`;
- unsafe/traversal archive content.

A verifier PASS is prerequisite evidence hygiene only. It does not replace the controlled K4 protocol or runtime-sensitive feature gates.


## Stock baseline versus candidate runtime

Follow `docs/physical-validation-sequence.md`.

The official ASUS 386_52334 phase establishes the clean kernel/module baseline and is the first place controlled K4 may be attempted after read-only evidence passes.

The UNVALIDATED candidate phase must collect fresh read-only K4a/runtime evidence and pass:

```sh
python3 scripts/verify-hardware-evidence.py \
  --k4 <candidate-k4a.tar.gz> \
  --runtime <candidate-runtime.tar.gz> \
  --require-candidate-canaries
```

The five immutable file hashes and custom-WebUI aliases in candidate mode strengthen runtime provenance without pretending the runtime can reconstruct the full WFI `.w` hash.
