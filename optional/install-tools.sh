#!/bin/sh
set -eu

ROOT="${1:-/jffs/addons/merlin-tools}"
SRC="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)/ports/files"
BIN="$ROOT/bin"
LIB="$ROOT/lib"

sha_check() {
  file="$1"; want="$2"
  got="$(sha256sum "$file" | awk '{print $1}')"
  [ "$got" = "$want" ] || { echo "checksum mismatch: $file" >&2; exit 1; }
}

install -d -m 0755 "$BIN" "$LIB"
sha_check "$SRC/usr/bin/nano" "82e9e6d755fb779315d8a7b9f3530182456b9544f0e14216ac3ca3dd481db5e8"
sha_check "$SRC/usr/lib/libncurses.so.6.0" "d7b57d0d6b327c11230793f58cc64327f6be7ce64ea9c1d2dbe4a39ac7387a0b"
sha_check "$SRC/usr/bin/scp" "d47ec3eba8bde2e244b96feb47ed0fc26d4556de5aebfd3771822970c5754851"

install -m 0755 "$SRC/usr/bin/nano" "$BIN/nano.real"
install -m 0644 "$SRC/usr/lib/libncurses.so.6.0" "$LIB/libncurses.so.6.0"
ln -sfn libncurses.so.6.0 "$LIB/libncurses.so.6"
cat > "$BIN/nano" <<'EOF'
#!/bin/sh
SELF_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
ROOT="$(CDPATH= cd -- "$SELF_DIR/.." && pwd)"
export LD_LIBRARY_PATH="$ROOT/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec "$SELF_DIR/nano.real" "$@"
EOF
chmod 0755 "$BIN/nano"
ln -sfn nano "$BIN/rnano"
install -m 0755 "$SRC/usr/bin/scp" "$BIN/scp"

cat > "$ROOT/README" <<'EOF'
Capacity-optionalized tools for RT-AC86U ASUS 386_52334 + Merlin overlay.
Add /jffs/addons/merlin-tools/bin to PATH manually or through profile.add once
the JFFS custom-script framework is enabled. Nothing here auto-starts.
EOF
chmod 0644 "$ROOT/README"

echo "Installed optional Nano/SCP tools under $ROOT"
echo "No firmware rootfs files, startup hooks, or NVRAM settings were changed."
