"""フォームに入力して送信し、alert等のダイアログ文言と画面テキストを表示する(見えている結果のみ)。
usage: formtry.py <button text> <input1> [<input2> ...]   (表示中の入力欄に上から順に入力)"""
import sys, json, datetime, pathlib
from playwright.sync_api import sync_playwright
root=pathlib.Path(__file__).resolve().parents[1]
btn=sys.argv[1]; vals=sys.argv[2:]
with sync_playwright() as p:
    ctx=p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
    page=[pg for pg in ctx.pages if "siosaigame" in pg.url][0]
    msgs=[]
    page.on("dialog", lambda d:(msgs.append(d.message), d.accept()))
    ins=page.locator("input:visible")
    for i,v in enumerate(vals): ins.nth(i).fill(v)
    page.get_by_text(btn,exact=False).first.click()
    page.wait_for_timeout(1500)
    f=root/"data"/"screenshots"/f"{datetime.datetime.now():%Y%m%d-%H%M%S}-form.png"
    page.screenshot(path=str(f))
    body=page.inner_text("body")
    with open(root/"data"/"actions.jsonl","a") as fp:
        fp.write(json.dumps({"time":datetime.datetime.now().isoformat(timespec="seconds"),"cmd":"form","arg":[btn]+vals,"result":"ok","dialogs":msgs,"url":page.url,"shot":f.name},ensure_ascii=False)+"\n")
    print("URL:",page.url); print("DIALOG:",msgs); print(body[:600])
