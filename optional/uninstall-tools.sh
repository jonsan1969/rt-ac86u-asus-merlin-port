#!/bin/sh
set -eu
ROOT="${1:-/jffs/addons/merlin-tools}"
case "$ROOT" in /jffs/addons/merlin-tools|/tmp/*) ;; *) echo "refusing unsafe uninstall root: $ROOT" >&2; exit 1;; esac
rm -rf -- "$ROOT"
echo "Removed $ROOT"
