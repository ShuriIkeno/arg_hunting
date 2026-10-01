"""Replay PROGRAM 1-4 with already-known answers, stop at PROGRAM 5 (for ending experiments)."""
import math, time
from playwright.sync_api import sync_playwright
def txt(pg): return pg.evaluate("document.body.innerText")
with sync_playwright() as p:
    c = p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
    pg = [x for x in c.pages if x.url.endswith('/portal')][0]; pg.bring_to_front(); m = pg.mouse
    if pg.get_by_text("開始する", exact=True).count() and pg.get_by_text("開始する", exact=True).first.is_visible(): pg.get_by_text("開始する", exact=True).first.click(); pg.wait_for_timeout(1200)
    def circle(cx, cy, r, turns):
        m.move(cx + r, cy); m.down()
        for i in range(1, turns * 36 + 1):
            a = 2 * math.pi * i / 36; m.move(cx + r * math.cos(a), cy + r * math.sin(a)); pg.wait_for_timeout(12)
        m.up()
    if "完了しました" not in txt(pg):
        circle(633, 435, 60, 4); circle(633, 435, 60, 4); pg.wait_for_timeout(800); pg.get_by_text("飲み干す").click(); pg.wait_for_timeout(1000)
    pg.get_by_text("マイページへ戻る").locator("visible=true").first.click(); pg.wait_for_timeout(1200)
    pg.get_by_text("進む", exact=True).locator("visible=true").first.click(); pg.wait_for_timeout(1200)
    m.move(474, 585); m.down(); m.move(676, 585, steps=20); m.up(); pg.keyboard.press("ArrowRight")
    print(pg.evaluate("document.body.innerText").split("sHz")[0][-8:])
    pg.get_by_text("同調する").locator("visible=true").first.click(); pg.wait_for_timeout(1000); pg.get_by_text("マイページへ戻る").locator("visible=true").first.click(); pg.wait_for_timeout(1200)
    pg.get_by_text("進む", exact=True).locator("visible=true").first.click(); pg.wait_for_timeout(1200)
    for (x, y, n) in [(633, 492, 1), (633, 608, 2), (633, 550, 3)]:
        for _ in range(n): m.click(x, y); pg.wait_for_timeout(200)
    pg.get_by_text("トリートメントを開始").locator("visible=true").first.click(); pg.wait_for_timeout(1000); pg.get_by_text("マイページへ戻る").locator("visible=true").first.click(); pg.wait_for_timeout(1200)
    pg.get_by_text("進む", exact=True).locator("visible=true").first.click(); pg.wait_for_timeout(1200)
    y = 330
    m.move(480, y); m.down()
    while y < 480:
        m.move(785, y, steps=12); y += 14; m.move(785, y, steps=2); m.move(480, y, steps=12); y += 14; m.move(480, y, steps=2)
    m.up(); pg.wait_for_timeout(1000); pg.get_by_text("完了する").locator("visible=true").first.click(); pg.wait_for_timeout(1000); pg.get_by_text("マイページへ戻る").locator("visible=true").first.click(); pg.wait_for_timeout(1200)
    pg.get_by_text("進む", exact=True).locator("visible=true").first.click(); pg.wait_for_timeout(1500)
    print(txt(pg)[:200])
