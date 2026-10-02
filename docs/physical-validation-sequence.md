# Physical validation execution sequence

Date: 2026-10-02

This is a **future operator-controlled test plan**. It does not recommend or authorize flashing the current UNVALIDATED candidate.

Current candidate SHA-256:

`eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3`

## Why the phases are separate

Three different questions must not be conflated:

1. Does the rebuilt optional kernel family load and function on the clean ASUS 386_52334 kernel/HND runtime?
2. Is the intended guarded candidate overlay actually the runtime being inspected?
3. Do runtime-sensitive candidate features, especially M49, work through ASUS `httpd` and the custom WebUI path?

A PASS for one question is not a PASS for the others.

## Phase 0 — recovery preparation

Before any firmware change:

- complete `docs/preflash-backup-recovery.md`;
- copy configuration/JFFS rollback material off-router and keep it private;
- verify the known-good Merlin rollback image;
- verify the official ASUS 386_52334 image;
- verify the UNVALIDATED candidate `.w` hash;
- keep wired management/recovery access available.

No K4 module is loaded in this phase.

## Phase A — official ASUS 386_52334 baseline

Target image:

official ASUS `RT-AC86U_3.0.0.4_386_52334-gd500e53_ubi.w`

Verified image SHA-256:

`1b4fe984e13afdf0a69c11bda759f3222822e12f5b8c929da33f334f2cc7483f`

After the router is confirmed stable:

1. run `scripts/k4-router-preflight.sh`;
2. run `scripts/runtime-feature-preflight.sh`;
3. copy both archives off-router;
4. run the host evidence verifier **without** candidate-canary mode;
5. run the host-side K4 symbol-name preflight against this K4a archive, the exact preserved modules and dependency-closure report; require `K4_SYMBOL_PREFLIGHT_PASS`;
6. inspect baseline dmesg, loaded modules, symbol-preflight report and stock module metadata;
7. run `scripts/verify-k4-family-staging.py` against `bundle/k4-family-staging` from the preserved hardware bundle, select exactly one family, require `K4_FAMILY_STAGING_PASS family=<family>`, and copy only the resulting verified family directory to `/tmp` on the router;
8. only then begin controlled K4, one family at a time:
   - ipset / xt_set;
   - Cake;
   - CIFS;
   - NFS/SUNRPC/LOCKD;
   - WireGuard.

Every STOP/FAIL condition in `docs/k4-controlled-module-validation.md` remains mandatory.

This phase proves stock-52334 kernel/module compatibility only. It does not prove candidate WebUI/JFFS features.

## Phase B — UNVALIDATED candidate runtime

This phase begins only after the operator deliberately proceeds to candidate testing with Phase 0 recovery material ready.

Before optional module activation:

1. confirm the candidate file SHA-256 again off-router;
2. after boot, perform basic wired-management and network stability checks;
3. do **not** restore Merlin configuration/JFFS merely to recreate previous state;
4. run fresh `scripts/k4-router-preflight.sh`;
5. run fresh `scripts/runtime-feature-preflight.sh`;
6. copy both archives off-router;
7. verify them with:

   ```sh
   python3 scripts/verify-hardware-evidence.py \
     --k4 <candidate-k4a.tar.gz> \
     --runtime <candidate-runtime.tar.gz> \
     --require-candidate-canaries \
     --report candidate-runtime-evidence.json
   ```

Candidate mode requires the five immutable overlay hashes and the custom-WebUI aliases.

8. before any candidate-side optional-module repeat, run `scripts/verify-k4-symbol-preflight.py` again against the **fresh candidate K4a archive** and the same exact preserved module/closure inputs; require a fresh `K4_SYMBOL_PREFLIGHT_PASS`.

A PASS establishes the intended guarded overlay/runtime fingerprint and the 52334 read-only evidence baseline. It is still not a flashability verdict.

## Phase C — candidate-side optional module confirmation

For any optional kernel family intended to become active:

- require the corresponding Phase A stock K4 PASS first;
- re-run `scripts/verify-k4-family-staging.py` for that family and stage only its verified output outside autoload/boot paths; never copy the full 27-module host analysis set to the router;
- repeat the minimum load/function/unload test under the candidate runtime;
- record module hashes, command statuses and new dmesg lines;
- STOP on any discrepancy, WARN/Oops, symbol/format error, HND/network instability or unexpected dependency.

A family not tested in Phase C remains disabled even if it passed on stock.

## Phase D — candidate runtime features

Only after candidate read-only evidence passes:

- validate normal guarded WebUI pages;
- validate JFFS/custom-user-slot filesystem behavior;
- test M49 optional delivery separately.

M49 requires a real authenticated HTTP request through the installed custom user slot and proof that the response executes, rather than returns literally:

`<% bandwidth("monthly"); %>`

Static file hashes or presence of the `bandwidth` handler are not substitutes.

Save the authenticated response body off-router and verify it with:

```sh
python3 scripts/verify-m49-ej-response.py userN-response.html \
  --report m49-ej-report.json
```

Require `M49_EJ_RESPONSE_PASS`. CI run `36969317440` proves the response verifier's positive and fail-closed cases.

## Phase E — promotion review

Promotion remains fail-closed until all applicable evidence is assembled against the current candidate:

- software repack gate;
- protected-core identity/no module leakage;
- Phase A stock K4 evidence;
- Phase B candidate canary/read-only evidence;
- Phase C candidate-side K4 evidence for every module family intended for activation;
- Phase D runtime-sensitive feature evidence;
- completed private recovery preparation.

Only then may `STATUS.md` be changed from UNVALIDATED to hardware-tested.

## Explicit non-equivalences

- Merlin 386.14_2 K4 test != ASUS 386_52334 evidence.
- Official stock WebUI result != candidate WebUI result.
- Candidate canary PASS != K4 module PASS.
- Stock K4 PASS != candidate module activation approval.
- CI PASS != flashability.
- GitHub artifact ZIP digest != firmware `.w` SHA-256.
