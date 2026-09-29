#!/bin/sh
# K4a read-only preflight for ASUS RT-AC86U 386_52334.
# This script MUST NOT load modules, modify NVRAM/JFFS, restart services, or reboot.

set -u

OUT="/tmp/rtac86u-k4-preflight"
ARCHIVE="/tmp/rtac86u-k4-preflight.tar.gz"
rm -rf "$OUT"
mkdir -p "$OUT"

have() {
	command -v "$1" >/dev/null 2>&1
}

nvget() {
	if have nvram; then
		nvram get "$1" 2>/dev/null || true
	fi
}

{
	echo "K4A_RTAC86U_52334_READ_ONLY_PREFLIGHT"
	echo "timestamp=$(date 2>/dev/null || true)"
	echo "productid=$(nvget productid)"
	echo "firmver=$(nvget firmver)"
	echo "buildno=$(nvget buildno)"
	echo "extendno=$(nvget extendno)"
	echo "odmpid=$(nvget odmpid)"
	echo "uname_r=$(uname -r 2>/dev/null || true)"
	echo "uname_m=$(uname -m 2>/dev/null || true)"
	echo "uname_a=$(uname -a 2>/dev/null || true)"
	if [ -r /proc/version ]; then
		printf "proc_version="
		cat /proc/version
	fi
	echo "rootfs=$(mount 2>/dev/null | head -n 1 || true)"
	echo "uptime=$(cat /proc/uptime 2>/dev/null || true)"
} > "$OUT/summary.txt"

if [ -r /proc/modules ]; then
	cat /proc/modules > "$OUT/proc-modules.txt"
else
	: > "$OUT/proc-modules.txt"
fi

if [ -r /proc/kallsyms ]; then
	cat /proc/kallsyms > "$OUT/proc-kallsyms.txt"
else
	echo "UNAVAILABLE /proc/kallsyms" > "$OUT/proc-kallsyms.txt"
fi

if have dmesg; then
	dmesg > "$OUT/dmesg-before.txt" 2>&1 || true
else
	echo "UNAVAILABLE dmesg" > "$OUT/dmesg-before.txt"
fi

: > "$OUT/module-tree.txt"
for root in /lib/modules /rom/lib/modules /usr/lib/modules; do
	if [ -d "$root" ]; then
		find "$root" -type f -name '*.ko' -print 2>/dev/null >> "$OUT/module-tree.txt" || true
	fi
done
sort -u "$OUT/module-tree.txt" -o "$OUT/module-tree.txt" 2>/dev/null || true

: > "$OUT/stock-module-vermagic.txt"
while IFS= read -r mod; do
	[ -f "$mod" ] || continue
	echo "===== $mod =====" >> "$OUT/stock-module-vermagic.txt"
	if have strings; then
		strings "$mod" 2>/dev/null | grep '^vermagic=' | head -n 1 >> "$OUT/stock-module-vermagic.txt" || true
	fi
	if have sha256sum; then
		sha256sum "$mod" >> "$OUT/stock-module-vermagic.txt" 2>/dev/null || true
	fi
done < "$OUT/module-tree.txt"

{
	echo "NO_MODULES_LOADED=1"
	echo "NO_NVRAM_WRITES=1"
	echo "NO_JFFS_WRITES=1"
	echo "NO_SERVICE_RESTARTS=1"
	echo "NO_REBOOT=1"
	echo "NO_FLASH_WRITES=1"
} > "$OUT/safety.txt"

rm -f "$ARCHIVE"
if tar -C /tmp -czf "$ARCHIVE" "$(basename "$OUT")" 2>/dev/null; then
	echo "K4A_COMPLETE $ARCHIVE"
else
	ARCHIVE="/tmp/rtac86u-k4-preflight.tar"
	tar -C /tmp -cf "$ARCHIVE" "$(basename "$OUT")"
	echo "K4A_COMPLETE $ARCHIVE"
fi
