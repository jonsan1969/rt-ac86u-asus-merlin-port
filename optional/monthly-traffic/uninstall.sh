#!/bin/sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
WEBROOT="${1:-/var/wwwext}"

case "$ROOT" in
  /jffs/addons/merlin-monthly|/tmp/*) ;;
  *) echo "refusing unsafe package root: $ROOT" >&2; exit 2 ;;
esac
case "$WEBROOT" in
  /var/wwwext|/tmp/*) ;;
  *) echo "refusing unsafe runtime webroot: $WEBROOT" >&2; exit 3 ;;
esac
test -f "$ROOT/.rtac86u-m49-package"
SLOT="$(cat "$ROOT/slot")"
case "$SLOT" in
  1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20) ;;
  *) echo "invalid persisted user slot: $SLOT" >&2; exit 4 ;;
esac

PAGE="$WEBROOT/user$SLOT.asp"
CHART="$WEBROOT/merlin-monthly-chart.min.js"
if [ -e "$PAGE" ]; then
  cmp -s "$ROOT/page.asp" "$PAGE" || { echo "refusing to delete changed/foreign page: $PAGE" >&2; exit 5; }
  rm -f -- "$PAGE"
fi
if [ -e "$CHART" ]; then
  cmp -s "$ROOT/chart.min.js" "$CHART" || { echo "refusing to delete changed/foreign chart: $CHART" >&2; exit 6; }
  rm -f -- "$CHART"
fi
rm -rf -- "$ROOT"
echo "Removed optional M49 package and matching runtime files."
