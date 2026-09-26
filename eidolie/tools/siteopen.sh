#!/bin/bash
# siteopen.sh <keyword> <result text>: EIDOLie site search, then open a result
cd "$(dirname "$0")/.."
tools/sitesearch.sh "$1" >/dev/null
tools/p.sh click "$2"
