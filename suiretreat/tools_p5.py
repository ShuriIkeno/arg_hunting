"""PROGRAM5 experiment: set 4 slots by character, long-press, print result. usage: tools_p5.py <c1c2c3c4>"""
import sys, json, datetime
from playwright.sync_api import sync_playwright
CYCLE = ["水","鏡","淨","心","神","凪","歸","淵","忘"]
want = sys.argv[1]
with sync_playwright() as p:
    c = p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
    pg = [x for x in c.pages if x.url.endswith('/portal')][0]; pg.bring_to_front(); m = pg.mouse
    m.move(640, 400); pg.mouse.wheel(0, 400); pg.wait_for_timeout(600)
    xs = [513, 593, 673, 753]
    for x, ch in zip(xs, want):
        cur = pg.evaluate("document.body.innerText").split("念じてください。")[1].split("念じる")[0].split()
    # read current slots
    cur = pg.evaluate("document.body.innerText").split("念じてください。")[1].split("念じる")[0].split()
    for i, (x, ch) in enumerate(zip(xs, want)):
        for _ in range((CYCLE.index(ch) - CYCLE.index(cur[i])) % 9):
            m.click(x, 407); pg.wait_for_timeout(120)
    cur = pg.evaluate("document.body.innerText").split("念じてください。")[1].split("念じる")[0].split()
    print("slots:", cur)
    m.move(633, 500); m.down(); pg.wait_for_timeout(3600); m.up(); pg.wait_for_timeout(3000)
    t = pg.evaluate("document.body.innerText"); print(t[:300])
    open('/home/user/arg_hunting/suiretreat/data/actions.jsonl','a').write(json.dumps({"time":datetime.datetime.now().isoformat(timespec='seconds'),"cmd":"hold","arg":"PROGRAM5 slots="+"".join(cur),"note":"END Bを探す実験","result":t.split("SUI RETREAT - ")[-1][:8] if "SUI RETREAT - END" in t else "no-end"},ensure_ascii=False)+"\n")
