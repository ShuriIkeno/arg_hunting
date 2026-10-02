"""Generic ARG play driver: operate a web ARG only through what a player can see, and log every action.

Attaches to a long-running Chromium started by argkit/tools/browser.sh (DevTools on :9222), so page
state survives between commands. Site-specific details live in <game_dir>/game.json (see FORMAT.md).

Usage: python argkit/tools/play.py <game_dir> <cmd> [args...]
  start                     open game.json "url" in the game tab
  goto <url>                navigate the game tab (only for URLs a player was shown)
  look                      print the visible text (no action)
  shot                      screenshot only
  click <text>              click the visible element whose text contains <text>
  clickat <x> <y>           click a screen position
  typeat <x> <y> <text>     click a position, type, press Enter
  type <selector> <text>    fill a visible input matched by CSS selector, press Enter
  search <box> <keyword>    type into a search box named in game.json "search_boxes", press Enter
  select <selector> <value> choose an option in a visible <select>
  key <Key>                 press a key (Enter, Escape, PageDown ...)
  scroll [dy]               mouse-wheel scroll (default 600)
  back                      browser back
  open <app>                double-click a desktop icon named in game.json "apps"
Options: --note "<why>"  free text stored with the action (where the keyword came from, what you expect)
         --quiet         print only the RESULT line
"""
import json, re, sys, time, datetime, pathlib
from playwright.sync_api import sync_playwright


def load_game(game_dir):
    for p in (game_dir / "game.json", game_dir / "data" / "game.json"):
        if p.exists():
            return json.loads(p.read_text())
    sys.exit(f"{game_dir}/game.json not found (run argkit/tools/new_game.sh first)")


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


def find_frame(page, part):
    if not part:
        return page.main_frame
    return next((f for f in visible_frames(page) if part in f.url), None)


def game_title(page, game):
    sel = game.get("title_selector")
    try:
        if sel:
            el = page.query_selector(sel)
            if el and el.is_visible():
                return el.inner_text().strip()
        return page.title()
    except Exception:
        return None


def main():
    args = sys.argv[1:]
    note = None
    if "--note" in args:
        i = args.index("--note"); note = args[i + 1]; del args[i:i + 2]
    quiet = "--quiet" in args
    args = [a for a in args if a != "--quiet"]
    game_dir = pathlib.Path(args[0]).resolve()
    cmd, rest = args[1], args[2:]
    arg = " ".join(rest)
    game = load_game(game_dir)
    data = game_dir / "data"
    shots, texts = data / "screenshots", data / "texts"
    shots.mkdir(parents=True, exist_ok=True); texts.mkdir(parents=True, exist_ok=True)
    w, h = game.get("viewport", [1280, 800])
    entry = {"time": datetime.datetime.now().isoformat(timespec="seconds"), "cmd": cmd, "arg": arg}

    with sync_playwright() as p:
        ctx = p.chromium.connect_over_cdp(game.get("cdp", "http://localhost:9222")).contexts[0]
        match = game.get("match_url") or game["url"].split("/")[2]
        page = next((pg for pg in ctx.pages if match in pg.url), None)
        if cmd == "start" or page is None:
            page = page or (ctx.pages[0] if ctx.pages else ctx.new_page())
            page.set_viewport_size({"width": w, "height": h})
            page.goto(game["url"], wait_until="load")
        page.bring_to_front()
        result = "ok"
        before = visible_text(page) if cmd in ("search", "typeat", "type") else ""
        try:
            if cmd == "goto":
                page.goto(rest[0], wait_until="load")
            elif cmd == "click":
                result = "NOT FOUND"
                for f in reversed(list(visible_frames(page))):
                    loc = f.get_by_text(arg, exact=False)
                    for i in range(loc.count()):
                        n = loc.nth(i)
                        box = n.bounding_box() if n.is_visible() else None
                        if box and box["y"] >= 0:
                            try:
                                n.click(timeout=5000)
                            except Exception:
                                n.click(timeout=5000, force=True)
                            result = "ok"; break
                    if result == "ok":
                        break
            elif cmd == "clickat":
                page.mouse.click(float(rest[0]), float(rest[1]))
            elif cmd == "typeat":
                x, y, text = rest[0], rest[1], " ".join(rest[2:])
                entry["keyword"] = text
                page.mouse.click(float(x), float(y)); page.keyboard.type(text); page.keyboard.press("Enter")
            elif cmd == "type":
                sel, text = rest[0], " ".join(rest[1:])
                entry["keyword"] = text
                f = next((f for f in reversed(list(visible_frames(page))) if f.locator(sel).locator("visible=true").count()), None)
                if not f:
                    result = "NOT FOUND"
                else:
                    box = f.locator(sel).locator("visible=true").first
                    box.fill(text); box.press("Enter")
            elif cmd == "search":
                name, kw = rest[0], " ".join(rest[1:])
                conf = game.get("search_boxes", {}).get(name)
                if not conf:
                    sys.exit(f"search box '{name}' is not in game.json search_boxes")
                entry["keyword"], entry["box"] = kw, name
                if conf.get("open_app") and not (find_frame(page, conf.get("frame")) or page.main_frame).locator(conf["selector"]).first.is_visible():
                    page.get_by_text(game["apps"][conf["open_app"]], exact=True).first.dblclick(); page.wait_for_timeout(600)
                f = find_frame(page, conf.get("frame"))
                if f is None:
                    result = "NOT FOUND"
                else:
                    box = f.locator(conf["selector"]).locator("visible=true").first
                    box.fill(kw); box.press("Enter")
            elif cmd == "select":
                f = next((f for f in visible_frames(page) if f.locator(rest[0]).count()), None)
                if f: f.select_option(rest[0], rest[1])
                else: result = "NOT FOUND"
            elif cmd == "key":
                page.keyboard.press(rest[0])
            elif cmd == "scroll":
                page.mouse.move(w / 2, h / 2); page.mouse.wheel(0, float(rest[0]) if rest else 600)
            elif cmd == "back":
                page.go_back()
            elif cmd == "open":
                page.get_by_text(game["apps"][rest[0]], exact=True).first.dblclick()
            elif cmd not in ("start", "look", "shot"):
                sys.exit(f"unknown command {cmd}")
        except Exception as e:
            result = f"ERROR {type(e).__name__}: {str(e).splitlines()[0][:160]}"
        page.wait_for_timeout(game.get("settle_ms", 2500))

        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        shot = f"{ts}-{cmd}.png"
        try:
            page.screenshot(path=str(shots / shot))
        except Exception:
            shot = None
        text = visible_text(page)
        (texts / f"{ts}-{cmd}.txt").write_text(text)
        title = game_title(page, game)
        prog = re.search(game["progress_regex"], title or "") if game.get("progress_regex") else None
        if "keyword" in entry and game.get("miss_patterns"):
            new = text.replace(before, "") if before and before in text else text
            entry["hit"] = not any(re.search(pat, new) for pat in game["miss_patterns"])
        entry.update({"result": result, "title": title, "progress": prog.group(1) if prog else None,
                      "url": page.url, "frames": [f.url for f in visible_frames(page)][1:],
                      "screenshot": shot, "text": f"{ts}-{cmd}.txt"})
        if note:
            entry["note"] = note
        with (data / "actions.jsonl").open("a") as fp:
            fp.write(json.dumps(entry, ensure_ascii=False) + "\n")
        hit = f" | HIT: {entry['hit']}" if "hit" in entry else ""
        print(f"RESULT: {result} | TITLE: {title} | PROGRESS: {entry['progress']}{hit} | SHOT: {shot}")
        if not quiet and cmd != "shot":
            print(text)


if __name__ == "__main__":
    main()
