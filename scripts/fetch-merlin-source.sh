#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DST="$ROOT/source/asuswrt-merlin.ng-386.14_2"
REPO='https://github.com/RMerl/asuswrt-merlin.ng.git'
REF='386.14_2'
EXPECTED='6a5df61aab6f3fa2dffc518994d42e4f2a27fb2b'

if [[ ! -d "$DST/.git" ]]; then
  git clone --branch "$REF" --single-branch "$REPO" "$DST"
fi

git -C "$DST" fetch --tags --force origin
ACTUAL="$(git -C "$DST" rev-parse HEAD)"
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "FAILURE: Merlin source ref mismatch" >&2
  echo " expected: $EXPECTED" >&2
  echo " actual:   $ACTUAL" >&2
  exit 1
fi

git -C "$DST" status --short
printf '%s  %s\n' "$ACTUAL" "$REF" > "$ROOT/source/MERLIN_SOURCE.lock"
echo "SUCCESS: Merlin source pinned at $ACTUAL"
