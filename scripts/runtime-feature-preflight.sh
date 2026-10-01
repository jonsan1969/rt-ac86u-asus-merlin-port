#!/bin/sh
# Read-only runtime probe for image-safe/JFFS-facing Merlin features.
# Intended for the future ASUS 386_52334 runtime. Writes only below /tmp.

set -u
OUT="/tmp/rtac86u-merlin-runtime-probe"
ARCHIVE="/tmp/rtac86u-merlin-runtime-probe.tar.gz"
rm -rf "$OUT"
mkdir -p "$OUT"

have(){ command -v "$1" >/dev/null 2>&1; }
nvget(){ if have nvram; then nvram get "$1" 2>/dev/null || true; fi; }

{
 echo "RTAC86U_MERLIN_RUNTIME_READ_ONLY_PROBE"
 echo "expected_candidate_sha256=eac8a7778bbc68686f68f1750c496fe6ddf92d689aa5e5878bacb9f02b9204b3"
 echo "timestamp=$(date 2>/dev/null || true)"
 echo "productid=$(nvget productid)"
 echo "firmver=$(nvget firmver)"
 echo "buildno=$(nvget buildno)"
 echo "extendno=$(nvget extendno)"
 echo "uname=$(uname -a 2>/dev/null || true)"
} > "$OUT/summary.txt"

{
 echo "=== WEBUI LINKS ==="
 for p in /www/user /www/user1.asp /www/user20.asp; do
   if [ -L "$p" ]; then echo "$p -> $(readlink "$p")"; else ls -ld "$p" 2>&1 || true; fi
 done
 echo "=== WWWEXT ==="
 ls -ld /var/wwwext /tmp/var/wwwext 2>&1 || true
 find /var/wwwext /tmp/var/wwwext -maxdepth 1 -type f -o -type l 2>/dev/null | sort || true
} > "$OUT/webui.txt"

{
 echo "jffs2_scripts=$(nvget jffs2_scripts)"
 for p in /jffs/scripts /jffs/configs /jffs/addons /jffs/etc/profile /jffs/configs/profile.add; do
   ls -ld "$p" 2>&1 || true
 done
 echo "=== profile canaries ==="
 grep -n 'profile.add\|/jffs/etc/profile\|/opt/etc/profile' /rom/etc/profile 2>/dev/null || true
 echo "=== helper ==="
 ls -l /usr/sbin/helper.sh 2>&1 || true
 if [ -f /usr/sbin/helper.sh ] && have sha256sum; then sha256sum /usr/sbin/helper.sh; fi
} > "$OUT/jffs.txt"

{
 echo "=== HTTPD ==="
 ps 2>/dev/null | grep '[h]ttpd' || true
 if have netstat; then netstat -lntup 2>/dev/null || true
 elif have ss; then ss -lntup 2>/dev/null || true
 fi
 echo "=== rstats ==="
 ps 2>/dev/null | grep '[r]stats' || true
 ls -l /jffs/.sys/TrafficAnalyzer /jffs/.sys/TrafficAnalyzer/* 2>/dev/null || true
} > "$OUT/services.txt"

{
 echo "NO_MODULES_LOADED=1"
 echo "NO_NVRAM_WRITES=1"
 echo "NO_JFFS_WRITES=1"
 echo "NO_SERVICE_RESTARTS=1"
 echo "NO_HTTP_REQUESTS=1"
 echo "NO_REBOOT=1"
 echo "NO_FLASH_WRITES=1"
} > "$OUT/safety.txt"

rm -f "$ARCHIVE"
if tar -C /tmp -czf "$ARCHIVE" "$(basename "$OUT")" 2>/dev/null; then
 echo "RUNTIME_PROBE_COMPLETE $ARCHIVE"
else
 ARCHIVE="/tmp/rtac86u-merlin-runtime-probe.tar"
 tar -C /tmp -cf "$ARCHIVE" "$(basename "$OUT")"
 echo "RUNTIME_PROBE_COMPLETE $ARCHIVE"
fi
