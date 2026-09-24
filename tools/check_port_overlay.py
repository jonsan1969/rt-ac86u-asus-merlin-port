#!/usr/bin/env python3
import argparse,json
from pathlib import Path
P={"/bin/busybox","/sbin/rc","/usr/sbin/httpd","/usr/sbin/dnsmasq","/usr/sbin/openvpn","/usr/bin/dropbearmulti","/usr/lib/libssl.so.1.1","/usr/lib/libcrypto.so.1.1"}
def protected(x): return x in P or x.startswith("/lib/modules/")
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("manifest",nargs="?",default="ports/active.json"); a=ap.parse_args(); d=json.loads(Path(a.manifest).read_text())
 assert d.get("schema")==1 and d.get("asus_baseline")=="3.0.0.4.386_52334" and d.get("merlin_commit")=="6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b"
 seen=set()
 for i,e in enumerate(d.get("entries",[]),1):
  t=e.get("target",""); typ=e.get("type","copy"); assert t.startswith("/") and t not in seen and not protected(t)
  assert typ in {"copy","symlink","text_replace"}
  if typ=="copy": assert e.get("policy","add_only")=="add_only" and e.get("source") and e.get("sha256") and e.get("source_kind","merlin") in {"merlin","repo"}
  elif typ=="symlink": assert e.get("policy")=="add_only" and e.get("link_target")
  else: assert e.get("policy")=="patch_exact" and e.get("target_sha256") and "find" in e and "replace" in e and int(e.get("count",1))>0
  seen.add(t)
 print(f"SUCCESS: manifest valid; {len(seen)} entries")
if __name__=="__main__": main()
