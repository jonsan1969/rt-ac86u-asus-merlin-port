# Preserved hardware-validation bundle verifier

Date: 2026-10-02

`scripts/verify-hardware-validation-bundle.py` is a fail-closed host-side integrity/provenance gate for the exact preserved hardware-validation artifact.

It pins the current `BUNDLE-MANIFEST.txt` SHA-256, exact manifest metadata, full regular-file inventory, every file hash, stock/candidate identities and sizes, the candidate SHA256SUMS binding, and the five-family outer staging checksums. Symlinks, extra files, missing files, changed manifest content and changed payload files are rejected.

Current preserved input:

- run `36998454435`;
- artifact `hardware-validation-bundle-eac8a777`;
- artifact id `11222508393`;
- ZIP digest `sha256:25309515170b32d2c85829977e24f27c44ec4934b89c641fc00d90dbe4dfed50`;
- expiry `2026-12-31T10:58:45Z`;
- internal manifest SHA-256 `2f2e16e182ba111e660fda5269546c798460918808fe7a8c641fd3f21ed700ec`.

A PASS is transport/inventory evidence only. It does not prove flashability, router runtime identity, kernel-module loadability, K4 behavior or M49 EJ dispatch.


## CI evidence

Run `37003596484` — **SUCCESS**.

Run `37003596484` validates current preservation run `36998454435` with `104` manifest-bound files and provenance fields for pre-K4 orchestrator CI `36997859437` plus candidate-evidence CI `36998249913`. CI also proves fail-closed rejection of:

- a changed manifest-bound payload file;
- changed manifest metadata/content;
- an unexpected extra file;
- a symlink injection.

The verifier is deliberately not embedded in the same preserved bundle whose manifest hash it pins. Its expected manifest SHA-256 is the external trust anchor; embedding that verifier in the manifest would make the verifier content depend on the manifest hash while the manifest hash simultaneously depends on the verifier content.


The current pin is CI-validated for exact manifest SHA-256 `2f2e16e182ba111e660fda5269546c798460918808fe7a8c641fd3f21ed700ec`. Historical verifier run `36996895881` applies only to the preceding 103-file preservation bundle.
