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

Run `scripts/prepare-candidate-evidence.sh <candidate-UNVALIDATED.w> <evidence-dir>` before collecting hardware evidence. Its checklist now names the complete host trust chain: preserved-bundle verification, hardware-evidence verification, K4 symbol-name preflight, pre-K4 host orchestration and exact one-family staging before any mutating K4 test. The script remains non-mutating and rejects candidates not explicitly marked UNVALIDATED; updated CI run `36998249913` passes syntax, mutation, positive and fail-closed tests.

## Current quarantined candidate

Run `36924014278` produced the first end-to-end software-gated candidate. Exact `.w` identity: `eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3` (78,250,004 bytes). This remains **UNVALIDATED** and may not be promoted using evidence from any other image hash.


## Preserved hardware-validation bundle

Run `37011499307` re-downloaded and re-verified the exact current validation inputs and republished them as one 90-day artifact:

- artifact: `hardware-validation-bundle-eac8a777`;
- artifact id: `11228371174`;
- artifact ZIP digest: `sha256:3b2959753b5464cc4e05f0cbd13cfdac6aaeba0ddcb0e1cade6bc08cf473c50a`;
- expires: `2026-12-31T13:12:49Z`;
- candidate inside: exact `.w` SHA-256 `eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3`, size `78,250,004` bytes;
- K2 source run: `36556899650`;
- K3 source run: `36561957525`.

The workflow first downloads and verifies the official ASUS 386_52334 stock image (`1b4fe984...7483f`, 78,250,004 bytes), then verifies the candidate hash/size, K2 module count and representative hashes, and the full expected K3 family plus representative hashes before publishing the bundle. It also verifies and carries the Unix-preserving ipset, WireGuard and Cake K4 userspace companions plus exact ELF dependency-closure report run `36976006891` and the K4 symbol-preflight verifier/docs validated by run `36977341893`; that report freezes artifact-internal load/unload ordering but does not replace real ASUS-52334 symbol/runtime validation. The bundle also carries the current K4/runtime collectors, the five isolated K4 family staging bundles from run `36978077020`, host-side evidence verifier, M49 EJ response verifier, physical-validation sequence, recovery material instructions and current handoff/status documents.

The artifact ZIP digest is only the GitHub archive digest. It must never be substituted for the firmware `.w` hash when binding hardware evidence.

The bundle manifest records `preservation_run=37011499307`, docs/source snapshot commit `0b42a3b59e96b5c8601a41316a717eae8eabe71b`, and internal manifest SHA-256 `fc6825056f8270db4f8d876c208b0447a419744f526d0bece0f3f24f9b9f9e33`. `BUNDLE-README.txt` repeats the preservation run, snapshot commit, candidate hash and classification so the extracted kit identifies itself without relying on copied snapshot docs. Later documentation-only updates that merely point back to the newly created artifact are expected self-reference deltas and do not change the candidate/module inputs.


## Evidence intake gate

Before using files from the preserved hardware-validation artifact, run `scripts/verify-hardware-validation-bundle.py --bundle-root <extracted-bundle>` and require `HARDWARE_VALIDATION_BUNDLE_PASS`. Normalized-pin CI run `37017852039` validates preservation run `37011499307` / exact 105-file manifest `fc682505...9f9e33`, including bundle-local README identity and fail-closed tamper/injection cases. Historical runs `37003596484` and `36996895881` apply only to superseded bundles. This proves bundle integrity/provenance only.

Before any mutating K4 family test, run the host-side verifier described in `docs/hardware-evidence-verifier.md`.

Then run the read-only symbol-name gate in `docs/k4-symbol-preflight.md` against the same K4a archive plus the exact preserved K2/K3 modules and dependency-closure report. Require `K4_SYMBOL_PREFLIGHT_PASS` before any module load. CI run `36977341893` validates both fail-closed fixtures and the default project profile against the exact preserved 27-module set.

Before copying a family to the router, run `scripts/verify-k4-family-staging.py` against the preserved `k4-family-staging` directory and require `K4_FAMILY_STAGING_PASS family=<family>`. CI run `36994228096` validates all five exact families and fail-closed corruption/output cases. This staging PASS is transport/inventory evidence only and does not replace K4 symbol or load/runtime gates.

For operator convenience, `scripts/prepare-k4-host-gates.py` may run the preserved-bundle verifier, hardware-evidence verifier, symbol-name preflight and selected-family staging gate in sequence. Require `PRE_K4_HOST_GATES_PASS family=<family>`. Run `37006423674` validates both stock-baseline and candidate-canary orchestration logic against the preceding preservation kit; the workflow is now re-pinned to normalized preservation run `37011499307` and must pass before physical use of that exact kit. The underlying normalized bundle pin is independently green in run `37017852039`. This does not collapse the underlying evidence classes or authorize module loading.

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
