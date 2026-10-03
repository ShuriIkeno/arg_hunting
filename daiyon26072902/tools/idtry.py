"""ID確認/PASSWORD確認フォームに複数の入力を順に試し、出た結果文言だけ表示する。usage: idtry.py idgo|passgo <v1> <v2> ..."""
import sys, json, datetime, pathlib
from playwright.sync_api import sync_playwright
root=pathlib.Path(__file__).resolve().parents[1]
mode=sys.argv[1]; vals=sys.argv[2:]
with sync_playwright() as p:
    ctx=p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
    page=[pg for pg in ctx.pages if "siosaigame" in pg.url][0]
    res={}
    for v in vals:
        page.goto(f"https://siosaigame.sakura.ne.jp/arg4/{mode}.html"); page.wait_for_timeout(300)
        page.locator("input:visible").first.fill(v); page.get_by_role("button",name="確認する").click(); page.wait_for_timeout(500)
        t=page.inner_text("body"); r=[l for l in t.split("\n") if ("：" in l and ("ID" in l or "PASSWORD" in l)) or "一致" in l and "しません" in l]
        res[v]=r; print(v,"=>",r,flush=True)
    with open(root/"data"/"actions.jsonl","a") as fp:
        fp.write(json.dumps({"time":datetime.datetime.now().isoformat(timespec="seconds"),"cmd":"idtry","arg":[mode]+vals,"result":res},ensure_ascii=False)+"\n")
