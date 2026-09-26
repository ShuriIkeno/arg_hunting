#!/bin/bash
# try each keyword in both the EIDOLie site search and the in-game browser search
cd "$(dirname "$0")/.."
for k in "$@"; do
  s=$(tools/sitesearch.sh "$k" | tr '\n' '|')
  b=$(python tools/play.py search "$k" | sed -n '/件が見つかりました\|に一致する結果/,$p' | grep -v -e dummy.com -e '^Dummy' -e '^\.\.\.$' | head -4 | tr '\n' '|')
  echo "=== $k"; echo "  site: $s"; echo "  web : $b"
done
