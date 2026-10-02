#!/bin/sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
WEBROOT="${1:-/var/wwwext}"

case "$WEBROOT" in
  /var/wwwext|/tmp/*) ;;
  *) echo "refusing unsafe runtime webroot: $WEBROOT" >&2; exit 2 ;;
esac
test -f "$ROOT/.rtac86u-m49-package"
SLOT="$(cat "$ROOT/slot")"
case "$SLOT" in
  1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20) ;;
  *) echo "invalid persisted user slot: $SLOT" >&2; exit 3 ;;
esac

PAGE="$ROOT/page.asp"
RUNTIME_PAGE="$WEBROOT/user$SLOT.asp"
RUNTIME_CHART="$WEBROOT/merlin-monthly-chart.min.js"

grep -Fq '<% bandwidth("monthly"); %>' "$PAGE"
grep -Fq 'src="/user/merlin-monthly-chart.min.js"' "$PAGE"
grep -Fq "name=\"current_page\" value=\"user$SLOT.asp\"" "$PAGE"
grep -Fq "name=\"next_page\" value=\"user$SLOT.asp\"" "$PAGE"
if grep -Fq '__USER_SLOT__' "$PAGE"; then
  echo "unresolved user-slot placeholder" >&2
  exit 4
fi
cmp -s "$PAGE" "$RUNTIME_PAGE"
cmp -s "$ROOT/chart.min.js" "$RUNTIME_CHART"
echo "M49 package/runtime file verification PASS for user$SLOT.asp"
echo "EJ execution itself remains a separate ASUS-52334 runtime gate."
