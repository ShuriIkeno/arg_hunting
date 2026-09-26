"""Replay the ending branch from the pre-ending save with a given action plan, through the game UI only.

Usage: python ending_run.py <label> <plan...>
  plan steps (run in order):
    vguard:<NN>         send track NN from the V-Guard admin screen
    nikaido:<name>:<place>   answer Nikaido's "調査状況の確認" mail
    rebut:<name>:<page>      rebut task in the DM (culprit name, evidence page number)
    norebut                  choose 反論しない in the DM
    report:<name>            answer the final report mail
Writes data/endings/<label>.json (steps, texts, timings) and screenshots.
"""
import sys, json, time, datetime, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAVE = ROOT / "data" / "saves" / "save_before_ending.dat"
OUT = ROOT / "data" / "endings"
SHOTS = OUT / "screenshots"
label, plan = sys.argv[1], sys.argv[2:]
OUT.mkdir(parents=True, exist_ok=True); SHOTS.mkdir(exist_ok=True)
log = {"label": label, "plan": plan, "started": datetime.datetime.now().isoformat(timespec="seconds"), "steps": []}


def step(stepname, **kw):
    kw.update(step=stepname, time=datetime.datetime.now().isoformat(timespec="seconds"))
    log["steps"].append(kw); print("·", stepname, {k: v for k, v in kw.items() if k not in ("step", "time", "text")})


def frame(page, part, timeout=20):
    end = time.time() + timeout
    while time.time() < end:
        for f in page.frames:
            if part in f.url:
                return f
        page.wait_for_timeout(300)
    raise RuntimeError(f"frame {part} not found")


def open_app(page, name):
    page.get_by_text(name, exact=True).first.dblclick(); page.wait_for_timeout(1200)


def web_search(page, kw):
    open_app(page, "ブラウザ")
    c = frame(page, "console.html")
    c.fill("#url-input", kw); c.press("#url-input", "Enter"); page.wait_for_timeout(2500)


def click_in(f, text, exact=False, timeout=15000, first=False):
    loc = f.get_by_text(text, exact=exact).locator("visible=true")
    loc = loc.first if first else loc.last
    loc.wait_for(timeout=timeout); loc.click(); return loc


def open_dm(page):
    web_search(page, "エイドリー")  # makes sure the browser window is open
    c = frame(page, "console.html")
    c.locator("button, span, div").filter(has_text="⌂").last.click(); page.wait_for_timeout(2000)
    c.get_by_text("Twintter").first.click(); page.wait_for_timeout(3000)
    sns = frame(page, "sns.html")
    sns.get_by_text("✉️").locator("visible=true").first.click(); page.wait_for_timeout(1500)
    sns.get_by_text("task", exact=True).locator("visible=true").last.click(); page.wait_for_timeout(2000)
    return sns


def shot(page, name):
    p = SHOTS / f"{label}-{len(log['steps']):02d}-{name}.png"
    try:
        page.screenshot(path=str(p))
    except Exception:
        pass
    return p.name


with sync_playwright() as pw:
    ctx = pw.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
    page = next((pg for pg in ctx.pages if "yoryormary.com/eidoLie" in pg.url and "/hint/" not in pg.url), None) or ctx.new_page()
    page.bring_to_front()
    page.on("dialog", lambda d: d.accept())
    page.goto("https://yoryormary.com/eidoLie/docs/top.html", wait_until="networkidle")

    # --- load the pre-ending save
    open_app(page, "調査記録")
    s = frame(page, "spreadsheet.html")
    click_in(s, "セーブ")
    s.locator("input[type=file]").set_input_files(str(SAVE))
    page.wait_for_timeout(5000)
    page.goto("https://yoryormary.com/eidoLie/docs/top.html", wait_until="networkidle")
    step("load")
    t0 = time.time()

    for item in plan:
        kind, *args = item.split(":")
        if kind == "vguard":
            web_search(page, "スティレットプロモーション")
            click_in(frame(page, "console.html"), "株式会社スティレットプロモーション", exact=True, first=True)
            page.wait_for_timeout(2000)
            st = frame(page, "stiletto.html"); click_in(st, "PARTNERS", exact=True); page.wait_for_timeout(2000)
            lg = frame(page, "stiletto_partner.html")
            ins = lg.locator("input:visible"); ins.nth(0).fill("39865"); ins.nth(1).fill("kimigatame")
            lg.locator("button:visible").first.click(); page.wait_for_timeout(4000)
            click_in(frame(page, "stiletto_portal.html"), "V-Guard 管理画面"); page.wait_for_timeout(3000)
            v = frame(page, "v_guard.html")
            v.select_option("#track-d1", args[0][0]); v.select_option("#track-d2", args[0][1])
            click_in(v, "送信", exact=True); page.wait_for_timeout(1000)
            click_in(v, "送信する", exact=True); page.wait_for_timeout(20000)
            body = v.evaluate("()=>document.body.innerText")
            outcome = "NO RESPONSE" if "NO RESPONSE" in body else ("OFFLINE" if "OFFLINE" in body else "?")
            text = ""
            if outcome == "OFFLINE":
                try:
                    click_in(v, "追加音声データ", timeout=5000); page.wait_for_timeout(500)
                    for b in v.locator("text=▶").all():
                        if b.is_visible(): b.click(); break
                    page.wait_for_timeout(6000)
                    text = v.evaluate("()=>document.body.innerText").split("自動音声書き起こし", 1)[1].strip()
                except Exception as e:
                    text = f"(new log not readable: {e})"
            else:
                text = body[:300]
            step("vguard", track=args[0], outcome=outcome, text=text, shot=shot(page, "vguard"))
        elif kind == "readdm":
            sns = open_dm(page)
            sns.get_by_text("反論しない", exact=True).first.wait_for(timeout=90000)
            step("readdm", shot=shot(page, "readdm"))
        elif kind == "news":
            web_search(page, "エイドリー")
            c = frame(page, "console.html")
            c.locator("button, span, div").filter(has_text="⌂").last.click(); page.wait_for_timeout(2000)
            c.get_by_text("ニュース").first.click(); page.wait_for_timeout(4000)
            n = frame(page, "newssite.html")
            step("news", text=n.evaluate("()=>document.body.innerText")[:300], shot=shot(page, "news"))
        elif kind == "nikaido":
            name, place = args
            found = False
            for _ in range(8):
                open_app(page, "メール")
                m = frame(page, "mail.html")
                if m.get_by_text("件名：調査状況の確認").count():
                    found = True; break
                page.wait_for_timeout(5000)
            if not found:
                step("nikaido", result="mail not found"); continue
            click_in(m, "件名：調査状況の確認"); page.wait_for_timeout(1000)
            click_in(m, "わかる", exact=True); page.wait_for_timeout(1500)
            m.locator("input[type=text]:visible").fill(name)
            m.get_by_role("button", name="回答する").click(); page.wait_for_timeout(1000)
            m.get_by_role("button", name="はい").click(); page.wait_for_timeout(2500)
            m.locator("input[type=text]:visible").fill(place)
            m.get_by_role("button", name="回答する").click(); page.wait_for_timeout(1000)
            m.get_by_role("button", name="はい").click(); page.wait_for_timeout(3000)
            body = m.evaluate("()=>document.body.innerText")
            step("nikaido", name=name, place=place, text=body[body.find("その方は、今どこに"):][:600], shot=shot(page, "nikaido"))
        elif kind in ("rebut", "norebut"):
            sns = open_dm(page)
            click_in(sns, "反論する" if kind == "rebut" else "反論しない", exact=True, timeout=60000)
            page.wait_for_timeout(3000)
            if kind == "rebut":
                name, pageno = args
                click_in(sns, "誰かへの復讐", exact=True, timeout=60000); page.wait_for_timeout(2000)
                click_in(sns, "そう思わない", exact=True, timeout=60000); page.wait_for_timeout(2000)
                sns.locator("input.game-input-field:visible").last.wait_for(timeout=60000)
                sns.locator("input.game-input-field:visible").last.fill(name)
                click_in(sns, "回答", exact=True); page.wait_for_timeout(1000)
                click_in(sns, "はい", exact=True); page.wait_for_timeout(8000)
                try:
                    sns.get_by_text("証拠を提示できます").last.wait_for(timeout=40000)
                    sns.locator("input.game-input-field:visible").last.fill(pageno)
                    click_in(sns, "送信", exact=True); page.wait_for_timeout(1000)
                    click_in(sns, "はい", exact=True)
                except Exception as e:
                    step("rebut-evidence-skipped", error=str(e)[:200])
                page.wait_for_timeout(15000)
            body = sns.evaluate("()=>document.body.innerText").split("「なう」を見つけよう")[0]
            step(kind, args=args, text=body[body.find("クルミを殺したのは在原だ"):], shot=shot(page, kind))
        elif kind == "report":
            name = args[0]
            found = False
            for _ in range(12):
                open_app(page, "メール")
                m = frame(page, "mail.html")
                if m.get_by_text("件名：調査の報告について").count():
                    found = True; break
                page.wait_for_timeout(5000)
            if not found:
                step("report", result="mail not found"); continue
            click_in(m, "件名：調査の報告について"); page.wait_for_timeout(1000)
            m.locator("input[type=text]:visible").fill(name)
            m.get_by_role("button", name="回答する").click(); page.wait_for_timeout(1000)
            m.get_by_role("button", name="はい").click(); page.wait_for_timeout(8000)
            step("report", name=name)
            # --- follow the ending pages
            texts = []
            for i in range(6):
                ep = next((pg for pg in ctx.pages if "/end" in pg.url), None)
                src = ep or page
                cur = next((f for f in src.frames if "/end" in f.url), None)
                if not cur:
                    break
                src.bring_to_front()
                nx = cur.get_by_text("次へ", exact=True)
                try:
                    nx.first.wait_for(state="visible", timeout=40000)
                except Exception:
                    nx = None
                src.wait_for_timeout(1500)
                texts.append({"url": cur.url, "text": cur.evaluate("()=>document.body.innerText")})
                shot(src, f"ending{i+1}")
                if nx is None:
                    break
                nx.first.click(); src.wait_for_timeout(6000)
            log["ending_pages"] = texts
            last = texts[-1]["text"] if texts else ""
            log["ending"] = next((l for l in last.splitlines() if l.startswith("END")), None)
            print("ENDING:", log["ending"], [t["url"].rsplit("/", 1)[-1] for t in texts])
    log["elapsed_sec"] = round(time.time() - t0)
    (OUT / f"{label}.json").write_text(json.dumps(log, ensure_ascii=False, indent=1))
    with (ROOT / "data" / "actions.jsonl").open("a") as fp:
        fp.write(json.dumps({"time": datetime.datetime.now().isoformat(timespec="seconds"), "cmd": "ending_run",
                             "arg": label + " " + " ".join(plan), "result": log.get("ending")}, ensure_ascii=False) + "\n")
