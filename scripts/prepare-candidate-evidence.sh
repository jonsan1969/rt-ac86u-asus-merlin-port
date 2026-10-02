#!/bin/sh
# Prepare a fail-closed evidence directory before any future candidate flash.
# This script does not flash, reboot, write NVRAM or alter JFFS contents.

set -eu
CANDIDATE="${1:-}"
OUT="${2:-candidate-evidence}"

if [ -z "$CANDIDATE" ] || [ ! -f "$CANDIDATE" ]; then
  echo "usage: $0 <UNVALIDATED.w> [evidence-dir]" >&2
  exit 2
fi

case "$(basename "$CANDIDATE")" in
  *UNVALIDATED*.w) ;;
  *) echo "refusing candidate without UNVALIDATED marker" >&2; exit 3 ;;
esac

mkdir -p "$OUT"
sha256sum "$CANDIDATE" > "$OUT/candidate-sha256.txt"
stat -c 'candidate=%n\nsize=%s\nmtime=%y' "$CANDIDATE" > "$OUT/candidate-stat.txt"

cat > "$OUT/REQUIRED-EVIDENCE.txt" <<'EOF'
Do not promote this candidate until evidence for this exact SHA-256 includes:
- K4 ASUS-52334 read-only preflight archive
- general runtime feature preflight archive
- host-side hardware evidence verifier PASS for the K4a/runtime archive pair
- host-side K4 symbol-name preflight PASS for the exact K4a/module/closure set
- K4 module compatibility/load-unload evidence for any optional modules intended for activation
- feature-specific runtime evidence (including M49 EJ dispatch if M49 is advertised)
- configuration/JFFS backup and recovery preparation
- explicit STATUS.md promotion of this exact candidate hash
EOF

cat > "$OUT/SAFETY.txt" <<'EOF'
NO_FLASH=1
NO_REBOOT=1
NO_NVRAM_WRITE=1
NO_JFFS_WRITE=1
NO_MODULE_LOAD=1
EOF

echo "EVIDENCE_SKELETON_READY $OUT"
