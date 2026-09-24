#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

PROTECTED_EXACT = {
    "/bin/busybox",
    "/sbin/rc",
    "/usr/sbin/httpd",
    "/usr/sbin/dnsmasq",
    "/usr/sbin/openvpn",
    "/usr/bin/dropbearmulti",
    "/usr/lib/libssl.so.1.1",
    "/usr/lib/libcrypto.so.1.1",
}
PROTECTED_PREFIXES = ("/lib/modules/",)

def protected(path):
    return path in PROTECTED_EXACT or any(path.startswith(p) for p in PROTECTED_PREFIXES)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest", nargs="?", default="ports/active.json")
    args=ap.parse_args()
    data=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    assert data.get("schema")==1, "unsupported schema"
    assert data.get("asus_baseline")=="3.0.0.4.386_52334", "wrong ASUS baseline"
    assert data.get("merlin_commit")=="6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b", "wrong Merlin donor pin"
    seen=set()
    for i,e in enumerate(data.get("entries",[]),1):
        t=e.get("target","")
        assert t.startswith("/"), f"entry {i}: target must be absolute"
        assert t not in seen, f"entry {i}: duplicate target {t}"
        assert not protected(t), f"entry {i}: protected target {t}"
        assert e.get("policy","add_only")=="add_only", f"entry {i}: only add_only allowed"
        assert e.get("type","copy") in {"copy","symlink"}, f"entry {i}: unsupported type"
        seen.add(t)
    print(f"SUCCESS: manifest valid; {len(seen)} entries")

if __name__=="__main__":
    main()
