#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 2 ]]; then
  echo "usage: $0 <firmware.w> <output-dir>" >&2
  exit 2
fi
FW="$(realpath "$1")"
OUT="$(mkdir -p "$2" && realpath "$2")"

if ! command -v binwalk >/dev/null 2>&1; then
  echo 'FAILURE: binwalk is required for the first extraction pass.' >&2
  echo 'Install a modern binwalk plus UBI/UBIFS extraction support, then retry.' >&2
  exit 1
fi

cp -f "$FW" "$OUT/"
cd "$OUT"
file "$(basename "$FW")" | tee firmware.file.txt
sha256sum "$(basename "$FW")" | tee firmware.sha256.txt
binwalk -Me "$(basename "$FW")" | tee binwalk.log

echo 'SUCCESS: extraction pass completed. Inspect the generated .extracted tree before comparison.'
