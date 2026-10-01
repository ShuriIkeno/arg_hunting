#!/bin/bash
# Scaffold a new game directory in the argkit format.
# Usage: argkit/tools/new_game.sh <slug> "<game title>" <start_url> [hint_url]
set -e
SLUG=${1:?slug}; TITLE=${2:?title}; URL=${3:?url}; HINT=${4:-}
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; DIR="$ROOT/$SLUG"
[ -e "$DIR" ] && { echo "$DIR already exists"; exit 1; }
mkdir -p "$DIR/data" "$DIR/viz"
sed -e "s|__SLUG__|$SLUG|g" -e "s|__TITLE__|$TITLE|g" -e "s|__URL__|$URL|g" -e "s|__HINT__|$HINT|g" \
    -e "s|__DATE__|$(date +%F)|g" "$ROOT/argkit/templates/game.json" > "$DIR/game.json"
: > "$DIR/data/actions.jsonl"; : > "$DIR/data/hints.jsonl"; : > "$DIR/data/events.jsonl"
echo "[]" > "$DIR/data/pages.json"; echo "[]" > "$DIR/data/phases.json"
cp "$ROOT/argkit/templates/notes.md" "$DIR/NOTES.md"
printf '.profile/\n__pycache__/\n' > "$DIR/.gitignore"
echo "created $DIR — edit game.json (search_boxes, progress_regex, miss_patterns), then:"
echo "  argkit/tools/browser.sh $SLUG &   # start Chromium"
echo "  python argkit/tools/play.py $SLUG start"
