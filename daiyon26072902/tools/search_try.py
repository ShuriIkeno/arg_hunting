"""トップの検索窓にキーワードを順に入れて『検索』ボタンを押し、出た本棚名を表示する(画面に出る結果のみ)。
usage: search_try.py <kw> [<kw> ...]"""
import sys, json, datetime, pathlib
from playwright.sync_api import sync_playwright
root=pathlib.Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    ctx=p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
    page=[pg for pg in ctx.pages if "siosaigame" in pg.url][0]
    out={}
    for kw in sys.argv[1:]:
        page.goto("https://siosaigame.sakura.ne.jp/arg4/main.html"); page.wait_for_timeout(500)
        page.fill("input[placeholder*='検索']",kw); page.get_by_role("button",name="検索").click(); page.wait_for_timeout(700)
        t=page.inner_text("body"); seg=t.split("他の人の本棚")[-1].split("このWebサイト")[0].strip().replace("\n"," / ")
        out[kw]=seg; print(f"{kw} => {seg}",flush=True)
    with open(root/"data"/"actions.jsonl","a") as fp:
        fp.write(json.dumps({"time":datetime.datetime.now().isoformat(timespec="seconds"),"cmd":"search_batch","arg":sys.argv[1:],"result":out},ensure_ascii=False)+"\n")
