# Pre-K4 host gate orchestrator

Date: 2026-10-02

`scripts/prepare-k4-host-gates.py` is a host-only convenience wrapper for the already independent fail-closed gates. It does not replace any verifier and it never contacts the router.

For one selected family it requires, in order:

1. `HARDWARE_VALIDATION_BUNDLE_PASS` from the exact preserved bundle;
2. baseline or candidate `HARDWARE_EVIDENCE_*_PASS` from the fresh read-only router archives;
3. `K4_SYMBOL_PREFLIGHT_PASS` against the full preserved 27-module host analysis set;
4. `K4_FAMILY_STAGING_PASS family=<family>` and extraction of exactly one family into a clean host staging directory.

Example:

```sh
python3 scripts/prepare-k4-host-gates.py \
  --bundle-root <extracted-hardware-bundle> \
  --k4 <fresh-k4a.tar.gz> \
  --runtime <fresh-runtime.tar.gz> \
  --family ipset \
  --output <clean-host-workspace>
```

Add `--candidate-mode` only for candidate-runtime evidence requiring the immutable canaries.

A PASS ends at the host staging boundary. The resulting selected-family directory may then be copied manually to a fresh router `/tmp/k4-<family>` path under `docs/k4-controlled-module-validation.md`. The wrapper contains no module-load, NVRAM/JFFS, service restart, reboot or flash operations.


## CI evidence

Run `37020619484` — **SUCCESS against the current normalized preservation kit**.

Historical runs `37006423674` and `36997859437` remain logic evidence for superseded preservation kits.

CI proves the wrapper can chain the exact current preserved bundle through:

- bundle integrity/provenance verification;
- stock-baseline hardware-evidence verification;
- candidate-canary hardware-evidence verification;
- full-set K4 symbol-name preflight;
- exact one-family staging for both ipset and WireGuard test paths;
- fail-closed rejection of a non-empty workspace.

The wrapper is intentionally kept outside the preserved hardware bundle. It depends on `verify-hardware-validation-bundle.py`, whose pinned manifest hash is the external trust anchor for that bundle; embedding the orchestration stack back into the same bundle would reintroduce a self-reference update loop without adding runtime evidence.


## Current preservation compatibility

Normalized-bundle orchestration run `37020619484` is SUCCESS against preservation run `37011499307` / artifact `11228371174`; its external bundle verifier is independently CI-green in run `37017852039`. This closes the host-side orchestration/current-kit compatibility gate. Bundle-local `BUNDLE-README.txt` and `BUNDLE-MANIFEST.txt` remain the extracted-kit identity authority.
