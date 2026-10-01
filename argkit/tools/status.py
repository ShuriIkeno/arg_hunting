"""Quick status while playing: pages found, missing ids, recent misses, hints used.

Usage: python argkit/tools/status.py <game_dir>
"""
import sys, json, re, pathlib
g = pathlib.Path(sys.argv[1]).resolve(); d = g / "data"
game = json.loads((g / "game.json").read_text())
acts = [json.loads(l) for l in (d / "actions.jsonl").read_text().splitlines() if l.strip()]
pages = json.loads((d / "pages.json").read_text()) if (d / "pages.json").exists() else []
hints = [json.loads(l) for l in (d / "hints.jsonl").read_text().splitlines() if l.strip()] if (d / "hints.jsonl").exists() else []
seen = {}
for a in acts:
    if a.get("progress"):
        seen.setdefault(a["progress"], a["time"])
ids = sorted({p["id"] for p in pages} | set(seen), key=lambda x: (not x.isdigit(), int(x) if x.isdigit() else 0, x))
total = game.get("total_pages")
print(f"{game.get('title')}: {len(ids)}/{total or '?'} pages, {len(acts)} actions, {len(hints)} hint opens")
if total and str(total).isdigit():
    missing = [str(i) for i in range(1, int(total) + 1) if str(i) not in ids]
    print("missing:", " ".join(missing) or "none")
unannotated = [i for i in ids if not next((p for p in pages if p["id"] == i and p.get("source")), None)]
if unannotated:
    print("pages without source annotation (log.py page <id> source=...):", " ".join(unannotated))
misses = [a.get("keyword") for a in acts[-200:] if a.get("hit") is False]
print("recent misses:", ", ".join(misses[-30:]) or "-")
