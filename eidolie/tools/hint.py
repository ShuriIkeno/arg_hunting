"""Open the game's official hint page in a separate tab (same URL as the in-game ❓ button),
click through the given labels, print visible text, and log that a hint was used."""
import sys, json, datetime, pathlib
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
with sync_playwright() as p:
    ctx = p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
    pg = next((x for x in ctx.pages if "/hint/" in x.url), None) or ctx.new_page()
    pg.set_viewport_size({"width": 1280, "height": 800})
    pg.bring_to_front()
    pg.goto("https://yoryormary.com/eidoLie/hint/index.html")
    for label in sys.argv[1:]:
        pg.get_by_text(label, exact=True).locator("visible=true").first.click()
        pg.wait_for_timeout(700)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    pg.screenshot(path=str(ROOT / "data" / "screenshots" / f"{ts}-hint.png"))
    with (ROOT / "data" / "actions.jsonl").open("a") as fp:
        fp.write(json.dumps({"time": datetime.datetime.now().isoformat(timespec="seconds"), "cmd": "hint",
                             "arg": " > ".join(sys.argv[1:]), "screenshot": f"{ts}-hint.png"}, ensure_ascii=False) + "\n")
    print(pg.evaluate("() => document.body.innerText"))
