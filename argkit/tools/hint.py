"""Open the game's official hint page in its own tab, click through labels, and log what was read.

Usage: python argkit/tools/hint.py <game_dir> [--episode <id>] [--why "<what you were stuck on>"] <label> [<label> ...]
  Each label is clicked in order (exact visible text). The text that appeared after the last click
  is stored in data/hints.jsonl as "text", together with the click path, so the dashboard can show
  which hint unlocked what. Use --episode to tie hints to one stuck episode (see FORMAT.md).
Requires game.json "hint_url".
"""
import sys, json, datetime, pathlib
from playwright.sync_api import sync_playwright

args = sys.argv[1:]
opts = {}
for k in ("--episode", "--why"):
    if k in args:
        i = args.index(k); opts[k] = args[i + 1]; del args[i:i + 2]
game_dir = pathlib.Path(args[0]).resolve(); labels = args[1:]
game = json.loads((game_dir / "game.json").read_text())
data = game_dir / "data"; (data / "screenshots").mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    ctx = p.chromium.connect_over_cdp(game.get("cdp", "http://localhost:9222")).contexts[0]
    pg = next((x for x in ctx.pages if x.url.startswith(game["hint_url"].split("#")[0])), None) or ctx.new_page()
    pg.bring_to_front()
    pg.goto(game["hint_url"], wait_until="networkidle")
    before = pg.evaluate("() => document.body.innerText")
    for label in labels:
        before = pg.evaluate("() => document.body.innerText")
        pg.get_by_text(label, exact=True).locator("visible=true").first.click()
        pg.wait_for_timeout(700)
    after = pg.evaluate("() => document.body.innerText")
    old = set(before.splitlines())
    new = "\n".join(l for l in after.splitlines() if l.strip() and l not in old)
    ts = datetime.datetime.now()
    shot = f"{ts:%Y%m%d-%H%M%S}-hint.png"
    pg.screenshot(path=str(data / "screenshots" / shot))
    row = {"time": ts.isoformat(timespec="seconds"), "path": labels, "text": new or "（見出しを開いただけ）",
           "episode": opts.get("--episode"), "why": opts.get("--why"), "screenshot": shot}
    with (data / "hints.jsonl").open("a") as fp:
        fp.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (data / "actions.jsonl").open("a") as fp:
        fp.write(json.dumps({"time": row["time"], "cmd": "hint", "arg": " > ".join(labels), "screenshot": shot}, ensure_ascii=False) + "\n")
    print(after if not labels else new)
