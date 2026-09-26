"""EIDOLie play driver: operates the game only through its visible UI and logs every action.

Attaches to a long-running headless Chromium (DevTools on :9222) so in-game state
(open windows, browser history) survives between commands.

Usage: python play.py <cmd> [arg]
  start                load the game desktop (fresh tab)
  look                 visible text of the desktop and every visible window
  open <app>           double-click a desktop icon (mail|memo|spreadsheet|browser)
  close <app>          close a window
  search <keyword>     type a keyword into the in-game browser and press Enter
  sitesearch <kw>      type into a search box shown inside the current in-game page
  click <text>         click the visible element whose text contains <text>
  shot                 screenshot only
"""
import json, sys, datetime, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "data" / "actions.jsonl"
SHOTS = ROOT / "data" / "screenshots"
URL = "https://yoryormary.com/eidoLie/docs/top.html"
APPS = {"mail": "メール", "memo": "メモ帳", "spreadsheet": "調査記録", "browser": "ブラウザ"}


def visible_frames(page):
    for f in page.frames:
        # only read what a player can see: skip frames inside hidden windows
        if f != page.main_frame:
            try:
                if not f.frame_element().is_visible():
                    continue
            except Exception:
                continue
        yield f


def visible_text(page):
    out = []
    for f in visible_frames(page):
        try:
            t = f.evaluate("() => document.body ? document.body.innerText : ''")
        except Exception:
            continue
        if t.strip():
            out.append(f"--- frame: {f.url}\n{t.strip()}")
    return "\n".join(out)


def browser_title(page):
    try:
        el = page.query_selector("#browser-title-text")
        return el.inner_text() if el and el.is_visible() else None
    except Exception:
        return None


def log(entry):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as fp:
        fp.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    cmd, arg = sys.argv[1], " ".join(sys.argv[2:])
    SHOTS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        ctx = browser.contexts[0]
        page = next((pg for pg in ctx.pages if "/eidoLie/docs/" in pg.url), None)
        if cmd == "start" or page is None:
            page = page or (ctx.pages[0] if ctx.pages else ctx.new_page())
            page.set_viewport_size({"width": 1280, "height": 800})
            page.goto(URL, wait_until="networkidle")
        result = "ok"
        if cmd == "open":
            page.get_by_text(APPS[arg], exact=True).first.dblclick()
        elif cmd == "close":
            page.click(f"#win-{arg} .close-btn, #win-{arg} [onclick*=close]")
        elif cmd == "search":
            fr = next(f for f in page.frames if "console.html" in f.url)
            if not fr.locator("#url-input").is_visible():
                page.get_by_text(APPS["browser"], exact=True).first.dblclick()
                page.wait_for_timeout(500)
            fr.fill("#url-input", arg)
            fr.press("#url-input", "Enter")
        elif cmd == "sitesearch":
            result = "NOT FOUND"
            for f in visible_frames(page):
                if f == page.main_frame or "console.html" in f.url:
                    continue
                box = f.locator("input:visible, textarea:visible, [contenteditable]:visible")
                if box.count():
                    box.first.click()
                    page.keyboard.press("Control+A")
                    page.keyboard.type(arg)
                    page.keyboard.press("Enter")
                    result = "ok"
                    break
        elif cmd == "typeat":
            # typeat <x> <y> <text>: click a screen position like a player would, then type + Enter
            x, y, text = arg.split(" ", 2)
            page.mouse.click(float(x), float(y))
            page.keyboard.type(text)
            page.keyboard.press("Enter")
        elif cmd == "clickat":
            x, y = arg.split(" ")[:2]
            page.mouse.click(float(x), float(y))
        elif cmd == "scroll":
            page.mouse.move(640, 400)
            page.mouse.wheel(0, float(arg or 600))
        elif cmd == "login":
            # login <id> <password>: fill the two visible inputs of the current page and press its button
            uid, pw = arg.split(" ", 1)
            f = [f for f in visible_frames(page) if f != page.main_frame and "console.html" not in f.url][-1]
            inputs = f.locator("input:visible")
            inputs.nth(0).fill(uid)
            inputs.nth(1).fill(pw)
            f.locator("button:visible").first.click()
            page.wait_for_timeout(1000)
            try:
                result = f.evaluate("() => document.body.innerText").strip().replace("\n", " / ")[-200:]
            except Exception:
                result = "navigated"
        elif cmd == "click":
            result = "NOT FOUND"
            for f in reversed(list(visible_frames(page))):
                loc = f.get_by_text(arg, exact=False)
                for i in range(loc.count()):
                    if loc.nth(i).is_visible() and loc.nth(i).bounding_box() and loc.nth(i).bounding_box()["y"] >= 0:
                        try:
                            loc.nth(i).click(timeout=5000)
                        except Exception:
                            loc.nth(i).click(timeout=5000, force=True)
                        result = "ok"
                        break
                if result == "ok":
                    break
        page.wait_for_timeout(2500)
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        shot = SHOTS / f"{ts}-{cmd}.png"
        page.screenshot(path=str(shot))
        title = browser_title(page)
        text = visible_text(page)
        log({"time": datetime.datetime.now().isoformat(timespec="seconds"), "cmd": cmd, "arg": arg,
             "result": result, "browser_title": title,
             "frames": [f.url for f in visible_frames(page)], "screenshot": shot.name})
        print("RESULT:", result, "| TITLE:", title, "| SHOT:", shot.name)
        if cmd != "shot":
            print(text)


if __name__ == "__main__":
    main()
