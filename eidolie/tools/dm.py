"""dm.py choice <text> | dm.py send <message>: act in the Twintter DM with task and print the new messages."""
import sys, json, datetime
from playwright.sync_api import sync_playwright
mode, arg = sys.argv[1], " ".join(sys.argv[2:])
with sync_playwright() as p:
    ctx = p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
    page = next(pg for pg in ctx.pages if "/eidoLie/docs/" in pg.url)
    fr = next(f for f in page.frames if "sns.html" in f.url)
    before = fr.evaluate("()=>document.body.innerText")
    if mode == "choice":
        fr.get_by_text(arg, exact=True).locator("visible=true").last.click()
    else:
        box = fr.locator("input[type=text]:visible").last
        box.fill(arg); box.press("Enter")
    page.wait_for_timeout(4000)
    after = fr.evaluate("()=>document.body.innerText")
    cut = after.split("「なう」を見つけよう")[0]
    prev = before.split("「なう」を見つけよう")[0]
    print(cut[len(prev) - 400:] if cut.startswith(prev[:200]) else cut[-2500:])
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    page.screenshot(path=f"data/screenshots/{ts}-dm.png")
    with open("data/actions.jsonl", "a") as fp:
        fp.write(json.dumps({"time": datetime.datetime.now().isoformat(timespec="seconds"), "cmd": "dm_" + mode, "arg": arg,
                             "screenshot": f"{ts}-dm.png"}, ensure_ascii=False) + "\n")
