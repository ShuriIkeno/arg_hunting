#!/bin/bash
# siteopen.sh <keyword> <result text>: EIDOLie site search, then open a result
cd "$(dirname "$0")/.."
python tools/play.py search "エイドリー" >/dev/null
python tools/play.py click "アイドルグループ「エイドリー」公式" >/dev/null
python tools/play.py typeat 835 185 "$1" >/dev/null; sleep 3
tools/p.sh click "$2"
