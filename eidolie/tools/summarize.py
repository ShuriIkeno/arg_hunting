"""Summarize data/actions.jsonl: page discovery timeline, search hit/miss counts, hint usage."""
import json, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = [json.loads(l) for l in (ROOT / "data" / "actions.jsonl").open()]
first = {}
for e in rows:
    m = re.search(r"\[(\d+)/43\]", e.get("browser_title") or "")
    if m and m.group(1) != "1":
        first.setdefault(int(m.group(1)), (e["time"], re.sub(r" - Web Browser.*", "", e["browser_title"])))
searches = [e for e in rows if e["cmd"] == "search"]
print(f"actions: {len(rows)}  searches: {len(searches)}  hints: {sum(e['cmd']=='hint' for e in rows)}")
print(f"pages found: {len(first)} + top(1) / 43")
for k in sorted(first):
    print(f"  {k:>2}  {first[k][0]}  {first[k][1]}")
