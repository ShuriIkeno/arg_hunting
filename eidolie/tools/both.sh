#!/bin/bash
# try each keyword in both the EIDOLie site search and the in-game browser search
cd "$(dirname "$0")/.."
for k in "$@"; do
  python tools/play.py search "エイドリー" >/dev/null
  python tools/play.py click "アイドルグループ「エイドリー」公式" >/dev/null
  python tools/play.py typeat 835 185 "$k" >/dev/null; sleep 3
  s=$(python tools/play.py look | sed -n '/の検索結果/,/TOPへ戻る/p' | sed '1d;$d' | tr '\n' '|')
  b=$(python tools/play.py search "$k" | sed -n '/件が見つかりました\|に一致する結果/,$p' | grep -v -e dummy.com -e '^Dummy' -e '^\.\.\.$' | head -4 | tr '\n' '|')
  echo "=== $k"; echo "  site: $s"; echo "  web : $b"
done
