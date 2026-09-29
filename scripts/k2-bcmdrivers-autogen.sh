#!/usr/bin/env bash
set -euo pipefail
B="${1:?bcmdrivers directory required}"
{
  printf '\n# Automatically generated file -- do not modify manually\n\n'
  while IFS= read -r autodetect; do
    dir="${autodetect%/*}"
    driver="$(grep -i '^DRIVER\|FEATURE:' "$B/$autodetect" | awk -F ': *' '{ print $2 }')"
    [ -n "$driver" ] || driver="${dir##*/}"
    if [ -f "$B/$dir/Kconfig.autodetect" ]; then
      printf 'menu "%s"\n' "$(printf '%s' "$driver" | tr '[:lower:]' '[:upper:]')"
      printf 'source "../../bcmdrivers/%s/Kconfig.autodetect"\n' "$dir"
      printf 'endmenu\n\n'
    fi
  done < <(cd "$B" && find * -type f -name autodetect | sort)
} > "$B/Kconfig.autogen"
test -s "$B/Kconfig.autogen"
grep -Fq '# Automatically generated file' "$B/Kconfig.autogen"
