# K4 controlled module validation protocol

Candidate identity: `eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3`.

This protocol is intentionally **not** an auto-run script. K4 changes live kernel state and therefore requires an operator at the router. Never execute K4 on the currently installed Merlin 386.14_2 runtime as evidence for ASUS 386_52334.

## Preconditions

- router is an RT-AC86U and is actually running ASUS 386_52334;
- K4a archive and general runtime archive were collected first and both embed the candidate hash above;
- configuration/JFFS backup and recovery access are prepared;
- no candidate module is installed into a boot/autoload path;
- the full preserved 27-module K2/K3 set is retained on the host for symbol-preflight only; the router receives only one verified `k4-family-<family>.tar.gz` at a time, extracted below `/tmp`;
- stock module tree, `/proc/modules`, `/proc/kallsyms` and pre-test `dmesg` are preserved.
- host-side `scripts/verify-k4-symbol-preflight.py` has been run against this K4a archive, the exact staged K2/K3 modules and preserved closure report, and returned `K4_SYMBOL_PREFLIGHT_PASS` before the first load attempt.

## Family order

Test one family at a time; do not mix failures.

1. ipset / xt_set;
2. Cake;
3. CIFS;
4. NFS/SUNRPC/LOCKD;
5. WireGuard.

Dependencies must be loaded before dependants. For physical staging, use only the isolated family tarballs produced by run `36978077020` from an extracted hardware-validation bundle that has first passed `HARDWARE_VALIDATION_BUNDLE_PASS`. Use the bundle-local `BUNDLE-README.txt` / `BUNDLE-MANIFEST.txt` as the identity and inventory authority for that extracted kit; do not depend on a preservation run number copied into a snapshot document. Before router transfer, require `PRE_K4_HOST_GATES_PASS family=<family>` and record SHA-256 and vermagic for every staged `.ko`.

### Exact artifact-internal dependency order

Run `36976006891` derives the dependency graph from the exact preserved K2/K3 ELF files by matching undefined symbols to other modules' `__ksymtab_*` exports. Artifact: `k4-module-dependency-closure`, id `11212893202`, ZIP digest `sha256:55df58d1682d82e8de79030f0c1e425beced4d17632013ba405271e1b65553b7`.

Use these artifact-internal orders during K4:

- ipset/xt_set: `ip_set` first, then only the subtype modules needed for the smoke test, with `xt_set` after `ip_set`; unload dependants before `ip_set`;
- Cake: `sch_cake` only;
- CIFS: `cifs` only;
- NFS/SUNRPC/LOCKD load: `sunrpc -> lockd -> nfs -> nfsd -> nfsv2 -> nfsv3`;
- NFS/SUNRPC/LOCKD unload: `nfsv3 -> nfsv2 -> nfsd -> nfs -> lockd -> sunrpc`;
- WireGuard: `wireguard` only.

The ELF gate found no dependency from one optional family into another and no declared external module dependency. This does **not** prove that all non-artifact kernel symbols exist on ASUS 386_52334. Before any load attempt, K4a evidence must still show that every required non-artifact symbol is present in the real target runtime. Any missing symbol is STOP/FAIL.

## Per-family gate

For each family:

1. on the host, run `scripts/prepare-k4-host-gates.py` for exactly one family against the verified extracted bundle and the fresh read-only K4a/runtime archives; require `PRE_K4_HOST_GATES_PASS family=<family>`, then copy only its `selected-family/<family>` directory to a fresh `/tmp/k4-<family>` path on the router;
2. capture `/proc/modules` and a fresh dmesg boundary;
3. require the saved K4 symbol-preflight PASS report for this exact K4a archive/full 27-module set, then re-check any family-specific dependency assumptions;
4. load only the minimum family needed for the test;
5. immediately capture command status and new dmesg lines;
6. if there is an unknown symbol, version/format error, Oops/WARN, HND/network instability, or unexpected dependency: **STOP**, unload what was added if safe, and mark the family FAIL;
7. if load succeeds, perform only the feature-specific smoke test;
8. unload in reverse dependency order where supported;
9. verify networking, routing and HND acceleration behavior remain normal;
10. capture post-test `/proc/modules` and dmesg.

A PASS applies only to the exact candidate hash, exact K2/K3 module hashes, and exact ASUS 386_52334 runtime evidence.

## Promotion rule

No optional kernel feature becomes active merely because its module loads. Functional smoke, clean post-test state, and the project status update are separate required gates. Any ambiguity remains FAIL/DEFERRED.


## Stock-first and candidate-repeat rule

Use the execution order in `docs/physical-validation-sequence.md`.

The first controlled family tests are performed only after a clean official ASUS 386_52334 read-only baseline passes host verification.

A stock ASUS K4 PASS materially de-risks the candidate because the software repack gate proves the candidate retains the stock kernel/HND/protected runtime and contains no K2/K3 module leakage. It still does not activate the feature in the candidate.

Before final candidate-side activation, collect fresh candidate K4a/runtime evidence, require candidate canaries, and repeat the minimum controlled family load/function check needed for that family. A discrepancy between stock and candidate phases is STOP/FAIL.


## Temporary K4 userspace companions

Kernel-module validation may require a matching userspace smoke tool that stock ASUS does not provide. Such tools are staged only below `/tmp`, are never added to the firmware image or an autoload path, and never authorize module loading by themselves.

### ipset / xt_set

Run `36971390631` produces artifact `k4-ipset-userspace-51997` (artifact id `11212280337`, ZIP digest `sha256:d935dfde9f58b1e072d6780d83613abfef825121598924012f39aa4b88a2b7e5`). The artifact contains a Unix-preserving `k4-ipset-userspace-51997.tar.gz`; CI re-extracts it and verifies executable bits, library symlinks and manifest hashes before upload.

Build lineage:

- source: `c553d8e4b0bf3289683368b0d57172649b030039`;
- userspace: ipset 7.6 + libmnl 1.0.4;
- toolchain: pinned ARM32 HND GCC 5.3 / glibc 2.22;
- kernel family: K2 run `36556899650`.

The bundle contains an `ipset` wrapper, real ARM32/EABI5 `ipset.real`, `libipset.so.13` and `libmnl.so.0`. CI records the ELF NEEDED closure and reaches `ipset v7.6, protocol version: 7` under QEMU. The host QEMU environment has no real ipset kernel netlink session, so the build gate accepts rc=1 only when the exact `Cannot open session to kernel.` marker is present and no loader/ABI failure appears.

During physical K4, stage this companion together with the exact K2 modules only after the read-only preflight and host evidence verification have passed. The userspace artifact is a smoke-test dependency, not firmware payload and not runtime compatibility evidence.


### WireGuard

Run `36971511361` produces artifact `k4-wireguard-userspace-51997` (artifact id `11211229289`, ZIP digest `sha256:2a5d5ab85615a7cd069f58812986322f9b875b08b8a6410b268498c6773038f4`).

Build lineage:

- source: `c553d8e4b0bf3289683368b0d57172649b030039`;
- userspace: `wireguard-tools` / `wg` version `1.0.20200827`;
- toolchain: pinned ARM32 HND GCC 5.3 / glibc 2.22;
- kernel family: K3 run `36561957525`.

The bundle contains only the temporary `wg` userspace tool plus provenance reports. CI requires ARM32/EABI5, the stock ARM loader `/lib/ld-linux.so.3`, successful QEMU execution of `wg --version`, and a Unix-preserving tar.gz whose extracted executable and manifest hashes verify.

During physical K4, `wg` is staged only below `/tmp` after the WireGuard kernel module has passed the preceding K4 load gate. It is not firmware payload, does not create an interface by itself, and does not make the kernel module compatible merely because the userspace binary runs.


### Cake

Run `36972043724` produces artifact `k4-cake-userspace-51997` (artifact id `11212107182`, ZIP digest `sha256:4bc49da98adc4a32a0945a96a335aaf7b285471ba514dd330ac1fb5af898687b`).

Build lineage:

- source: `c553d8e4b0bf3289683368b0d57172649b030039`;
- userspace: CAKE-aware iproute2 / `tc` version `5.11.0`;
- toolchain: pinned ARM32 HND GCC 5.3 / glibc 2.22;
- kernel family: K3 run `36561957525`.

The c553 tree explicitly links `q_cake.o` into `tc`. The K4 companion is built through that tree's top-level Makefile with `SHARED_LIBS=n` and xtables disabled so the temporary smoke tool does not depend on ASUS iptables/libxtables. CI requires ARM32/EABI5, `/lib/ld-linux.so.3`, the linked `cake_qdisc_util` symbol, QEMU `tc -V` = iproute2-5.11.0, and a local `tc qdisc add dev lo root cake help` parse that exposes the expected CAKE option surface. The help parse exits before a qdisc request is sent.

During physical K4, stage this `tc` only below `/tmp` after `sch_cake.ko` passes the controlled load gate. A functional test must use a disposable/non-production qdisc context and must still obey the STOP conditions for HND/network instability. The userspace binary itself is not firmware payload or compatibility proof.


## Host-side symbol-name preflight gate

Before step 3 of the first mutating family test, run:

```sh
python3 scripts/verify-k4-symbol-preflight.py \
  --k4 <k4a-archive> \
  --modules-root <hardware-bundle>/modules \
  --closure <hardware-bundle>/reports/k4-module-dependency-closure.json \
  --report k4-symbol-preflight.json
```

Require `K4_SYMBOL_PREFLIGHT_PASS`.

CI run `36977341893` validates the verifier logic and its default project profile against the exact preserved 27-module artifact set. The full 27-module set is an offline host-side analysis input here; it is not a router staging instruction. A real PASS can only be produced from the future router's ASUS-52334 K4a archive.

A missing strong symbol is STOP before any load. A PASS is still not load authorization by itself: `/proc/kallsyms` name presence cannot prove `EXPORT_SYMBOL` visibility, MODVERSIONS/CRC compatibility, relocation success or runtime stability. The controlled physical load remains the authoritative next gate.
