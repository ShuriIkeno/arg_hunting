#!/bin/bash
# Start the shared headless Chromium that play.py / hint.py attach to (DevTools on :9222).
# Usage: argkit/tools/browser.sh <game_dir>      (profile kept in <game_dir>/.profile, so saves survive)
set -e
GAME_DIR="$(cd "${1:?usage: browser.sh <game_dir>}" && pwd)"
CHROME="${CHROME:-$(ls -d /opt/pw-browsers/chromium-*/chrome-linux/chrome 2>/dev/null | head -1)}"
[ -x "$CHROME" ] || { echo "Chromium not found; set CHROME=/path/to/chrome"; exit 1; }
# Chromium on Linux trusts the NSS store, not the system bundle: import the sandbox CA bundle once.
if command -v certutil >/dev/null && [ -f /root/.ccr/ca-bundle.crt ] && ! certutil -L -d sql:$HOME/.pki/nssdb 2>/dev/null | grep -q ccr-; then
  mkdir -p "$HOME/.pki/nssdb"; tmp=$(mktemp -d)
  awk -v d="$tmp" '/BEGIN CERT/{n++} {print > sprintf("%s/b%03d.pem", d, n)}' /root/.ccr/ca-bundle.crt
  for f in "$tmp"/b*.pem; do grep -q BEGIN "$f" && certutil -A -d sql:$HOME/.pki/nssdb -n "ccr-$(basename $f)" -t "C,," -i "$f" 2>/dev/null || true; done
  rm -rf "$tmp"
fi
curl -s -m 2 localhost:9222/json/version >/dev/null && { echo "Chromium already running on :9222"; exit 0; }
exec "$CHROME" --headless=new --no-sandbox --remote-debugging-port=9222 --user-data-dir="$GAME_DIR/.profile" \
  --window-size=1280,800 --lang=ja-JP --no-first-run --autoplay-policy=no-user-gesture-required \
  --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36" about:blank
