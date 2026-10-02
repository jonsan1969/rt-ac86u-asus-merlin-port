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

SRC_PAGE="$ROOT/page.asp"
SRC_CHART="$ROOT/chart.min.js"
DEST_PAGE="$WEBROOT/user$SLOT.asp"
DEST_CHART="$WEBROOT/merlin-monthly-chart.min.js"
test -f "$SRC_PAGE"
test -f "$SRC_CHART"

install -d -m 0755 "$WEBROOT"
if [ -e "$DEST_PAGE" ] && ! cmp -s "$SRC_PAGE" "$DEST_PAGE"; then
  echo "refusing to replace foreign runtime page: $DEST_PAGE" >&2
  exit 5
fi
if [ -e "$DEST_CHART" ] && ! cmp -s "$SRC_CHART" "$DEST_CHART"; then
  echo "refusing to replace foreign runtime chart asset: $DEST_CHART" >&2
  exit 6
fi

install -m 0644 "$SRC_PAGE" "$DEST_PAGE"
install -m 0644 "$SRC_CHART" "$DEST_CHART"
cmp -s "$SRC_PAGE" "$DEST_PAGE"
cmp -s "$SRC_CHART" "$DEST_CHART"
echo "Materialized M49 into user$SLOT.asp under $WEBROOT"
