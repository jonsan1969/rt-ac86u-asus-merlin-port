# Preserved hardware-validation bundle verifier

Date: 2026-10-02

`scripts/verify-hardware-validation-bundle.py` is a fail-closed host-side integrity/provenance gate for the exact preserved hardware-validation artifact.

It pins the current `BUNDLE-MANIFEST.txt` SHA-256, exact manifest metadata, full regular-file inventory, every file hash, stock/candidate identities and sizes, the candidate SHA256SUMS binding, and the five-family outer staging checksums. Symlinks, extra files, missing files, changed manifest content and changed payload files are rejected.

Current preserved input:

- run `36995684511`;
- artifact `hardware-validation-bundle-eac8a777`;
- artifact id `11221372631`;
- ZIP digest `sha256:7bf47721147dbd49c52ec0af2e065499b3b35efada44057771588b163b2a37a1`;
- expiry `2026-12-31T10:28:43Z`;
- internal manifest SHA-256 `1f1198fdc23bc656bdbf01b3beaafb9154c742ef22c9274ac5acf296042a3a8f`.

A PASS is transport/inventory evidence only. It does not prove flashability, router runtime identity, kernel-module loadability, K4 behavior or M49 EJ dispatch.
