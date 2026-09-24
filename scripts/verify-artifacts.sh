#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IN="$ROOT/artifacts/incoming"
OUT="$ROOT/artifacts/verified"
mkdir -p "$OUT"

verify() {
  local f="$1" expected="$2"
  if [[ ! -f "$f" ]]; then
    echo "MISSING: $f" >&2
    return 2
  fi
  local actual
  actual="$(sha256sum "$f" | awk '{print $1}')"
  if [[ "$actual" != "$expected" ]]; then
    echo "FAILURE: checksum mismatch: $f" >&2
    echo " expected: $expected" >&2
    echo " actual:   $actual" >&2
    return 1
  fi
  echo "SUCCESS: $f"
  cp -f "$f" "$OUT/"
}

verify "$IN/FW_RT_AC86U_300438652334.zip" 'e8fd0f3a26db4fe9cf6acb64272d2b78247eb9ccf3890fbdb8daace0bac10d61'
verify "$IN/RT-AC86U_386.14_2.zip" '1dedab53b08b93c529920c791291d04e36089a9c85d672a5a0fff9dea45bb49a'

(
  cd "$OUT"
  sha256sum *.zip > SHA256SUMS.local
)

echo 'SUCCESS: both firmware archives verified and copied to artifacts/verified/.'
