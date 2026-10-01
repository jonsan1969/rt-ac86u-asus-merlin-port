#!/bin/sh
set -eu
ROOT="${1:-/jffs/addons/merlin-tools}"
test -x "$ROOT/bin/nano.real"
test -x "$ROOT/bin/nano"
test -x "$ROOT/bin/scp"
test -L "$ROOT/bin/rnano"
test -f "$ROOT/lib/libncurses.so.6.0"
test -L "$ROOT/lib/libncurses.so.6"
[ "$(sha256sum "$ROOT/bin/nano.real" | awk '{print $1}')" = "82e9e6d755fb779315d8a7b9f3530182456b9544f0e14216ac3ca3dd481db5e8" ]
[ "$(sha256sum "$ROOT/lib/libncurses.so.6.0" | awk '{print $1}')" = "d7b57d0d6b327c11230793f58cc64327f6be7ce64ea9c1d2dbe4a39ac7387a0b" ]
[ "$(sha256sum "$ROOT/bin/scp" | awk '{print $1}')" = "d47ec3eba8bde2e244b96feb47ed0fc26d4556de5aebfd3771822970c5754851" ]
echo "Optional Nano/SCP payload verification PASS"
