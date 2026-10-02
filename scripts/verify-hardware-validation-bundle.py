#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, re, sys
from pathlib import Path, PurePosixPath
from typing import Dict

EXPECTED_MANIFEST_SHA256="1f1198fdc23bc656bdbf01b3beaafb9154c742ef22c9274ac5acf296042a3a8f"
EXPECTED_METADATA={
"official_stock_sha256":"1b4fe984e13afdf0a69c11bda759f3222822e12f5b8c929da33f334f2cc7483f",
"official_stock_size":"78250004","candidate_run":"36924014278",
"candidate_sha256":"eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3",
"candidate_size":"78250004","k2_run":"36556899650","k3_run":"36561957525",
"k4_ipset_userspace_run":"36971390631","k4_wireguard_userspace_run":"36971511361",
"k4_cake_userspace_run":"36972043724","k4_module_dependency_run":"36976006891",
"k4_family_staging_run":"36978077020","k4_symbol_preflight_ci_run":"36977341893",
"k4_family_staging_verifier_ci_run":"36994228096",
"docs_snapshot_commit":"854a0afc54db3684b957ab0e17dd749fee9bc987",
"source_commit":"854a0afc54db3684b957ab0e17dd749fee9bc987",
"classification":"UNVALIDATED_HARDWARE_VALIDATION_INPUT"}
CANDIDATE_REL="candidate/RT-AC86U_386_52334_merlin-port-UNVALIDATED.w"
STOCK_REL="official-stock/RT-AC86U_386_52334_OFFICIAL.w"

class GateError(RuntimeError): pass

def sha256_path(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as fh:
  for chunk in iter(lambda:fh.read(1024*1024),b""): h.update(chunk)
 return h.hexdigest()

def safe_manifest_rel(raw:str)->str:
 if not raw.startswith("bundle/"): raise GateError(f"manifest path lacks bundle/ prefix: {raw!r}")
 rel=raw[7:]
 if not rel or "\\" in rel: raise GateError(f"invalid manifest path: {raw!r}")
 p=PurePosixPath(rel)
 if p.is_absolute() or ".." in p.parts or "." in p.parts or str(p)!=rel: raise GateError(f"unsafe manifest path: {raw!r}")
 return rel

def parse_manifest(path:Path):
 if not path.is_file() or path.is_symlink(): raise GateError("missing regular BUNDLE-MANIFEST.txt")
 if path.stat().st_size>2*1024*1024: raise GateError("BUNDLE-MANIFEST.txt unexpectedly large")
 got=sha256_path(path)
 if got!=EXPECTED_MANIFEST_SHA256: raise GateError(f"BUNDLE-MANIFEST.txt SHA-256 mismatch {got} != {EXPECTED_MANIFEST_SHA256}")
 lines=path.read_text(encoding="utf-8").splitlines()
 try: marker=lines.index("===== FILE SHA256 =====")
 except ValueError as exc: raise GateError("manifest missing FILE SHA256 marker") from exc
 meta={}
 for raw in lines[:marker]:
  if not raw: continue
  if "=" not in raw: raise GateError(f"invalid manifest metadata line: {raw!r}")
  k,v=raw.split("=",1)
  if k in meta: raise GateError(f"duplicate manifest metadata key: {k}")
  meta[k]=v
 if meta!=EXPECTED_METADATA:
  missing=sorted(set(EXPECTED_METADATA)-set(meta)); extra=sorted(set(meta)-set(EXPECTED_METADATA))
  changed=sorted(k for k in EXPECTED_METADATA if k in meta and meta[k]!=EXPECTED_METADATA[k])
  raise GateError(f"manifest metadata mismatch: missing={missing} extra={extra} changed={changed}")
 rows={}; pat=re.compile(r"^([0-9a-f]{64})  (bundle/.+)$")
 for raw in lines[marker+1:]:
  if not raw: continue
  m=pat.fullmatch(raw)
  if not m: raise GateError(f"invalid manifest checksum line: {raw!r}")
  digest,raw_path=m.groups(); rel=safe_manifest_rel(raw_path)
  if rel in rows: raise GateError(f"duplicate manifest file path: {rel}")
  rows[rel]=digest
 if not rows: raise GateError("manifest contains no file hashes")
 return meta,rows

def discover_actual_files(root:Path):
 actual=set()
 for base,dirs,names in os.walk(root,followlinks=False):
  bp=Path(base)
  for name in dirs:
   p=bp/name
   if p.is_symlink(): raise GateError(f"symlink directory rejected: {p.relative_to(root)}")
  for name in names:
   p=bp/name; rel=p.relative_to(root).as_posix()
   if p.is_symlink(): raise GateError(f"symlink file rejected: {rel}")
   if not p.is_file(): raise GateError(f"non-regular file rejected: {rel}")
   if rel!="BUNDLE-MANIFEST.txt": actual.add(rel)
 return actual

def require_semantics(root:Path, rows:Dict[str,str]):
 required={CANDIDATE_REL,STOCK_REL,"scripts/verify-hardware-evidence.py","scripts/verify-k4-symbol-preflight.py",
 "scripts/verify-k4-family-staging.py","reports/k4-module-dependency-closure.json","k4-family-staging/package-sha256.txt",
 "docs/candidate-promotion-gate.md","docs/physical-validation-sequence.md","docs/thread-handoff.md","docs/STATUS.md"}
 missing=sorted(required-set(rows))
 if missing: raise GateError(f"required bundle files absent from manifest: {missing}")
 candidate=root/CANDIDATE_REL; stock=root/STOCK_REL
 if candidate.stat().st_size!=int(EXPECTED_METADATA["candidate_size"]): raise GateError("candidate size mismatch")
 if stock.stat().st_size!=int(EXPECTED_METADATA["official_stock_size"]): raise GateError("official stock size mismatch")
 if sha256_path(candidate)!=EXPECTED_METADATA["candidate_sha256"]: raise GateError("candidate SHA-256 mismatch")
 if sha256_path(stock)!=EXPECTED_METADATA["official_stock_sha256"]: raise GateError("official stock SHA-256 mismatch")
 sums=(root/"candidate/SHA256SUMS").read_text(encoding="utf-8")
 if EXPECTED_METADATA["candidate_sha256"] not in sums or "UNVALIDATED.w" not in sums: raise GateError("candidate/SHA256SUMS does not bind expected candidate")
 famroot=root/"k4-family-staging"; outer=famroot/"package-sha256.txt"; seen={}
 pat=re.compile(r"^([0-9a-f]{64})  (k4-family-([a-z0-9_-]+)\.tar\.gz)$")
 for raw in outer.read_text(encoding="utf-8").splitlines():
  if not raw: continue
  m=pat.fullmatch(raw)
  if not m: raise GateError(f"invalid family outer checksum line: {raw!r}")
  digest,filename,family=m.groups()
  if family in seen: raise GateError(f"duplicate family outer checksum: {family}")
  p=famroot/filename
  if not p.is_file() or sha256_path(p)!=digest: raise GateError(f"family outer checksum mismatch: {filename}")
  seen[family]=digest
 if set(seen)!={"ipset","cake","cifs","nfs","wireguard"}: raise GateError(f"family staging set mismatch: {sorted(seen)}")

def main()->int:
 ap=argparse.ArgumentParser()
 ap.add_argument("--bundle-root",required=True)
 ap.add_argument("--report")
 ns=ap.parse_args(); root=Path(ns.bundle_root)
 try:
  if not root.is_dir() or root.is_symlink(): raise GateError(f"bundle root is not a regular directory: {root}")
  meta,rows=parse_manifest(root/"BUNDLE-MANIFEST.txt")
  actual=discover_actual_files(root); expected=set(rows)
  if actual!=expected: raise GateError(f"bundle file set mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
  for rel,want in sorted(rows.items()):
   got=sha256_path(root/Path(*PurePosixPath(rel).parts))
   if got!=want: raise GateError(f"{rel}: SHA-256 mismatch {got} != {want}")
  require_semantics(root,rows)
  report={"status":"PASS","classification":"RTAC86U_52334_PRESERVED_HARDWARE_BUNDLE",
  "manifest_sha256":EXPECTED_MANIFEST_SHA256,"candidate_sha256":meta["candidate_sha256"],
  "official_stock_sha256":meta["official_stock_sha256"],"docs_snapshot_commit":meta["docs_snapshot_commit"],
  "file_count":len(rows),"k4_family_staging_verifier_ci_run":int(meta["k4_family_staging_verifier_ci_run"]),
  "limitations":["PASS verifies exact preserved bundle inventory/provenance and file hashes only.",
  "PASS does not prove flashability, router runtime identity, module loadability, K4 behavior, or M49 EJ dispatch.",
  "The candidate remains UNVALIDATED until the physical promotion gates pass."]}
  payload=json.dumps(report,indent=2,sort_keys=True)
  if ns.report: Path(ns.report).write_text(payload+"\n",encoding="utf-8")
  print(payload); print("HARDWARE_VALIDATION_BUNDLE_PASS"); return 0
 except (GateError,OSError,UnicodeError) as exc:
  print(f"HARDWARE_VALIDATION_BUNDLE_FAIL: {exc}",file=sys.stderr); return 1
if __name__=="__main__": raise SystemExit(main())
