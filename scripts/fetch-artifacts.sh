#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IN="$ROOT/artifacts/incoming"
mkdir -p "$IN"

ASUS_URL_DEFAULT='https://dlcdnets.asus.com/pub/ASUS/wireless/RT-AC86U/FW_RT_AC86U_300438652334.zip?model=RT-AC86U'
MERLIN_URL='https://sourceforge.net/projects/asuswrt-merlin/files/RT-AC86U/Release/RT-AC86U_386.14_2.zip/download'
ASUS_URL="${ASUS_URL:-$ASUS_URL_DEFAULT}"

echo 'Fetching ASUS firmware...'
if ! curl -fL --retry 3 --retry-all-errors -o "$IN/FW_RT_AC86U_300438652334.zip" "$ASUS_URL"; then
  cat >&2 <<MSG
ASUS direct URL failed. The URL in this script is pattern-derived from ASUS' normal naming scheme and was not independently fetched when this scaffold was generated.
Download 3.0.0.4.386_52334 from the official ASUS RT-AC86U support page and save it as:
  $IN/FW_RT_AC86U_300438652334.zip
Then run verify-artifacts.sh.
MSG
fi

echo 'Fetching Merlin firmware...'
curl -fL --retry 3 --retry-all-errors -o "$IN/RT-AC86U_386.14_2.zip" "$MERLIN_URL"

echo 'Fetch step complete; now run scripts/verify-artifacts.sh.'
