#!/bin/bash
# sitesearch.sh <keyword>: go to EIDOLie top and run its site search, retrying until the result page shows
cd "$(dirname "$0")/.."
for try in 1 2 3; do
  python tools/play.py search "エイドリー" >/dev/null
  python tools/play.py click "アイドルグループ「エイドリー」公式" >/dev/null; sleep 2
  python tools/play.py typeat 835 185 "$1" >/dev/null; sleep 4
  out=$(python tools/play.py look | sed -n '/の検索結果/,/TOPへ戻る/p')
  if [ -n "$out" ] && ! echo "$out" | grep -q Searching; then echo "$out" | sed '1d;$d'; exit 0; fi
done
echo "(site search failed)"
