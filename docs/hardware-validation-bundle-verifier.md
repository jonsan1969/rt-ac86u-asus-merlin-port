# Preserved hardware-validation bundle verifier

Date: 2026-10-02

`scripts/verify-hardware-validation-bundle.py` is a fail-closed host-side integrity/provenance gate for the exact preserved hardware-validation artifact.

It pins the current `BUNDLE-MANIFEST.txt` SHA-256, exact manifest metadata, full regular-file inventory, every file hash, stock/candidate identities and sizes, the candidate SHA256SUMS binding, and the five-family outer staging checksums. Symlinks, extra files, missing files, changed manifest content and changed payload files are rejected.

Current preserved input:

- run `37011499307`;
- artifact `hardware-validation-bundle-eac8a777`;
- artifact id `11228371174`;
- ZIP digest `sha256:3b2959753b5464cc4e05f0cbd13cfdac6aaeba0ddcb0e1cade6bc08cf473c50a`;
- expiry `2026-12-31T13:12:49Z`;
- internal manifest SHA-256 `fc6825056f8270db4f8d876c208b0447a419744f526d0bece0f3f24f9b9f9e33`.

A PASS is transport/inventory evidence only. It does not prove flashability, router runtime identity, kernel-module loadability, K4 behavior or M49 EJ dispatch.


## CI evidence

Run `37017852039` — **SUCCESS for the current normalized 105-file bundle**.

Run `37017852039` validates normalized preservation run `37011499307` with `105` manifest-bound files, including `BUNDLE-README.txt`, `preservation_run=37011499307`, snapshot commit `0b42a3b59e96b5c8601a41316a717eae8eabe71b`, pre-K4 orchestrator provenance `37006423674`, and candidate-evidence CI `36998249913`. The fail-closed suite covers:

- a changed manifest-bound payload file;
- changed manifest metadata/content;
- an unexpected extra file;
- a symlink injection.

The verifier is deliberately not embedded in the same preserved bundle whose manifest hash it pins. Its expected manifest SHA-256 is the external trust anchor; embedding that verifier in the manifest would make the verifier content depend on the manifest hash while the manifest hash simultaneously depends on the verifier content.


The current normalized pin is exact manifest SHA-256 `fc6825056f8270db4f8d876c208b0447a419744f526d0bece0f3f24f9b9f9e33` and is CI-validated by run `37017852039`. Historical runs `36996895881` and `37003596484` remain evidence only for their respective superseded 103- and 104-file bundles.

The verifier also cross-checks the bundle-local `BUNDLE-README.txt` preservation run, snapshot commit, candidate SHA-256 and classification against the authoritative manifest metadata.
