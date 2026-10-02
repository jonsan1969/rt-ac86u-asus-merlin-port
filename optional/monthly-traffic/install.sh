#!/bin/sh
set -eu

SLOT="${1:-}"
ROOT="${2:-/jffs/addons/merlin-monthly}"
WEBROOT="${3:-/var/wwwext}"
SELF_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SELF_DIR/../.." && pwd)"
TEMPLATE="$SELF_DIR/user-slot.asp"
CHART="$REPO_ROOT/ports/files/chart.min.js"

case "$SLOT" in
  1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20) ;;
  *) echo "usage: $0 <slot 1..20> [package-root] [runtime-webroot]" >&2; exit 2 ;;
esac
case "$ROOT" in
  /jffs/addons/merlin-monthly|/tmp/*) ;;
  *) echo "refusing unsafe package root: $ROOT" >&2; exit 3 ;;
esac
case "$WEBROOT" in
  /var/wwwext|/tmp/*) ;;
  *) echo "refusing unsafe runtime webroot: $WEBROOT" >&2; exit 4 ;;
esac

test -f "$TEMPLATE"
test -f "$CHART"

DEST="$WEBROOT/user$SLOT.asp"
if [ -e "$DEST" ] && ! grep -Fq 'RTAC86U_M49_USER_SLOT_TEMPLATE' "$DEST"; then
  echo "refusing occupied foreign user slot: $DEST" >&2
  exit 5
fi

install -d -m 0755 "$ROOT"
sed "s/__USER_SLOT__/user$SLOT.asp/g" "$TEMPLATE" > "$ROOT/page.asp"
if grep -Fq '__USER_SLOT__' "$ROOT/page.asp"; then
  echo "slot placeholder remained after rendering" >&2
  exit 6
fi
install -m 0644 "$CHART" "$ROOT/chart.min.js"
printf '%s\n' "$SLOT" > "$ROOT/slot"
printf '%s\n' 'RTAC86U_M49_OPTIONAL_PACKAGE=1' > "$ROOT/.rtac86u-m49-package"
install -m 0755 "$SELF_DIR/activate.sh" "$ROOT/activate.sh"
install -m 0755 "$SELF_DIR/verify.sh" "$ROOT/verify.sh"
install -m 0755 "$SELF_DIR/uninstall.sh" "$ROOT/uninstall.sh"
cat > "$ROOT/README" <<'EOF'
Optional M49 Monthly Traffic package for RT-AC86U ASUS 386_52334 + Merlin overlay.
The page is materialized into /var/wwwext through one existing userN.asp alias.
Nothing here changes NVRAM, firmware rootfs, services, startup hooks, or menu files.
After reboot, activate.sh must be run manually until generic JFFS lifecycle hooks exist.
HTTPD EJ expansion of bandwidth("monthly") through the user slot is NOT proven by install.
EOF
chmod 0644 "$ROOT/README"

"$ROOT/activate.sh" "$WEBROOT"
"$ROOT/verify.sh" "$WEBROOT"
echo "Installed dormant/manual M49 package in $ROOT using user$SLOT.asp"
echo "Runtime EJ dispatch is still UNVALIDATED and must be proven on ASUS 386_52334."
