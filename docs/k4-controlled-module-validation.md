# K4 controlled module validation protocol

Candidate identity: `eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3`.

This protocol is intentionally **not** an auto-run script. K4 changes live kernel state and therefore requires an operator at the router. Never execute K4 on the currently installed Merlin 386.14_2 runtime as evidence for ASUS 386_52334.

## Preconditions

- router is an RT-AC86U and is actually running ASUS 386_52334;
- K4a archive and general runtime archive were collected first and both embed the candidate hash above;
- configuration/JFFS backup and recovery access are prepared;
- no candidate module is installed into a boot/autoload path;
- K2/K3 artifacts are copied only to a temporary staging directory;
- stock module tree, `/proc/modules`, `/proc/kallsyms` and pre-test `dmesg` are preserved.

## Family order

Test one family at a time; do not mix failures.

1. ipset / xt_set;
2. Cake;
3. CIFS;
4. NFS/SUNRPC/LOCKD;
5. WireGuard.

Dependencies must be loaded before dependants. Record SHA-256 and vermagic for every staged `.ko` before any load attempt.

## Per-family gate

For each family:

1. capture `/proc/modules` and a fresh dmesg boundary;
2. verify all expected symbols/dependencies from K4a evidence;
3. load only the minimum family needed for the test;
4. immediately capture command status and new dmesg lines;
5. if there is an unknown symbol, version/format error, Oops/WARN, HND/network instability, or unexpected dependency: **STOP**, unload what was added if safe, and mark the family FAIL;
6. if load succeeds, perform only the feature-specific smoke test;
7. unload in reverse dependency order where supported;
8. verify networking, routing and HND acceleration behavior remain normal;
9. capture post-test `/proc/modules` and dmesg.

A PASS applies only to the exact candidate hash, exact K2/K3 module hashes, and exact ASUS 386_52334 runtime evidence.

## Promotion rule

No optional kernel feature becomes active merely because its module loads. Functional smoke, clean post-test state, and the project status update are separate required gates. Any ambiguity remains FAIL/DEFERRED.


## Stock-first and candidate-repeat rule

Use the execution order in `docs/physical-validation-sequence.md`.

The first controlled family tests are performed only after a clean official ASUS 386_52334 read-only baseline passes host verification.

A stock ASUS K4 PASS materially de-risks the candidate because the software repack gate proves the candidate retains the stock kernel/HND/protected runtime and contains no K2/K3 module leakage. It still does not activate the feature in the candidate.

Before final candidate-side activation, collect fresh candidate K4a/runtime evidence, require candidate canaries, and repeat the minimum controlled family load/function check needed for that family. A discrepancy between stock and candidate phases is STOP/FAIL.
