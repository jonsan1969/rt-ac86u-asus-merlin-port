#!/usr/bin/env python3
import argparse,hashlib,json,os,shutil
from pathlib import Path
PROTECTED_EXACT={"/bin/busybox","/sbin/rc","/usr/sbin/httpd","/usr/sbin/dnsmasq","/usr/sbin/openvpn","/usr/bin/dropbearmulti","/usr/lib/libssl.so.1.1","/usr/lib/libcrypto.so.1.1"}
PROTECTED_PREFIXES=("/lib/modules/",)
def sha256(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for c in iter(lambda:f.read(1048576),b""): h.update(c)
 return h.hexdigest()
def safe_child(base,rel,label):
 if Path(rel).is_absolute(): raise ValueError(f"{label} must be relative: {rel}")
 out=(base/rel).resolve()
 try: out.relative_to(base.resolve())
 except ValueError: raise ValueError(f"{label} escapes source tree: {rel}")
 return out
def safe_target(root,target):
 if not target.startswith("/"): raise ValueError(f"absolute target required: {target}")
 lexical=root/target.lstrip("/")
 cur=root
 for part in Path(target.lstrip("/")).parts:
  cur=cur/part
  if cur.is_symlink():
   rel=cur.relative_to(root).as_posix()
   raise ValueError(f"target traverses rootfs symlink /{rel}; use canonical target: {target}")
 out=lexical.resolve(strict=False)
 try: out.relative_to(root.resolve())
 except ValueError: raise ValueError(f"target escapes rootfs: {target}")
 return out
def protected(t): return t in PROTECTED_EXACT or any(t.startswith(p) for p in PROTECTED_PREFIXES)
def mode(v): return None if v is None else (v if isinstance(v,int) else int(str(v),8))
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--rootfs",required=True); ap.add_argument("--merlin-src",required=True); ap.add_argument("--repo-root",default="."); ap.add_argument("--manifest",default="ports/active.json"); ap.add_argument("--report",default="reports/port-overlay-provenance.tsv"); a=ap.parse_args()
 root=Path(a.rootfs).resolve(); merlin=Path(a.merlin_src).resolve(); repo=Path(a.repo_root).resolve()
 if not root.is_dir(): raise SystemExit(f"rootfs not found: {root}")
 if not merlin.is_dir(): raise SystemExit(f"Merlin source not found: {merlin}")
 d=json.loads(Path(a.manifest).read_text())
 if d.get("schema")!=1 or d.get("asus_baseline")!="3.0.0.4.386_52334" or d.get("merlin_commit")!="6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b": raise SystemExit("manifest provenance mismatch")
 rows=[]
 for i,e in enumerate(d.get("entries",[]),1):
  typ=e.get("type","copy"); t=e.get("target")
  if not t: raise SystemExit(f"entry {i}: missing target")
  if protected(t): raise SystemExit(f"entry {i}: protected target {t}")
  dst=safe_target(root,t)
  if typ=="copy":
   if e.get("policy","add_only")!="add_only" or dst.exists() or dst.is_symlink(): raise SystemExit(f"entry {i}: add_only violation {t}")
   kind=e.get("source_kind","merlin"); srcname=e.get("source"); expected=e.get("sha256")
   if kind not in {"merlin","repo"} or not srcname or not expected: raise SystemExit(f"entry {i}: invalid copy metadata")
   src=safe_child(merlin if kind=="merlin" else repo,srcname,kind)
   if not src.is_file(): raise SystemExit(f"entry {i}: missing source {srcname}")
   actual=sha256(src)
   if actual.lower()!=expected.lower(): raise SystemExit(f"entry {i}: source checksum mismatch")
   dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dst); m=mode(e.get("mode"))
   if m is not None: os.chmod(dst,m)
   rows.append((t,typ,kind,srcname,actual,"add_only"))
  elif typ=="symlink":
   if e.get("policy")!="add_only" or dst.exists() or dst.is_symlink(): raise SystemExit(f"entry {i}: symlink add_only violation")
   lt=e.get("link_target")
   if not lt: raise SystemExit(f"entry {i}: missing link target")
   dst.parent.mkdir(parents=True,exist_ok=True); os.symlink(lt,dst); rows.append((t,typ,"symlink",lt,"-","add_only"))
  elif typ=="text_replace":
   if e.get("policy")!="patch_exact" or not dst.is_file(): raise SystemExit(f"entry {i}: invalid exact patch target")
   pre=e.get("target_sha256"); find=e.get("find"); repl=e.get("replace"); count=int(e.get("count",1))
   if not pre or find is None or repl is None: raise SystemExit(f"entry {i}: patch metadata missing")
   actual=sha256(dst)
   if actual.lower()!=pre.lower(): raise SystemExit(f"entry {i}: preimage checksum mismatch expected {pre} got {actual}")
   enc=e.get("encoding","utf-8"); txt=dst.read_text(encoding=enc); found=txt.count(find)
   if found!=count: raise SystemExit(f"entry {i}: expected {count} exact match(es), found {found}")
   dst.write_text(txt.replace(find,repl,count),encoding=enc,newline=""); after=sha256(dst)
   if e.get("result_sha256") and after.lower()!=e["result_sha256"].lower(): raise SystemExit(f"entry {i}: result checksum mismatch")
   rows.append((t,typ,"asus-preimage",pre,after,"patch_exact"))
  else: raise SystemExit(f"entry {i}: unsupported type {typ}")
 report=Path(a.report); report.parent.mkdir(parents=True,exist_ok=True)
 with report.open("w") as f:
  f.write("target\ttype\tsource_kind\tsource_or_preimage\tresult_sha256\tpolicy\n")
  for r in rows: f.write("\t".join(r)+"\n")
 print(f"SUCCESS: applied {len(rows)} overlay entries")
if __name__=="__main__": main()
