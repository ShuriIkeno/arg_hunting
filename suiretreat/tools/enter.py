"""Open the portal from the official site and check in (name given as argv[1], default ゲスト)."""
import sys
from playwright.sync_api import sync_playwright
name = sys.argv[1] if len(sys.argv) > 1 else "ゲスト"
with sync_playwright() as p:
    c = p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
    pg = next((x for x in c.pages if 'sui-r.pages.dev' in x.url), None)
    if pg is None:
        pg = c.pages[0]; pg.goto("https://shop.daiyonkyokai.net/products/26082602?variant=51655331578162", wait_until="domcontentloaded"); pg.wait_for_timeout(2500)
        pg.get_by_text("プレイ開始").first.click(); pg.wait_for_timeout(2500)
    pg.bring_to_front()
    if not pg.url.endswith('/portal'):
        pg.get_by_text("LOGIN", exact=True).first.click(); pg.wait_for_timeout(1500)
        pg.get_by_text("ログイン", exact=True).first.click(); pg.wait_for_timeout(2500)
    if "チェックイン" in pg.evaluate("document.body.innerText")[:200]:
        pg.mouse.click(640, 393); pg.keyboard.type(name); pg.keyboard.press("Enter"); pg.wait_for_timeout(2500)
    print(pg.url, pg.evaluate("document.body.innerText")[:60].replace("\n"," "))
