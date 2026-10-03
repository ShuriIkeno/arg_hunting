"""復活ボードの名前欄に座標指定で入力する(送信はしない)。 usage: ritual.py 頭=名前 右腕=名前 ... [--submit]"""
import sys, json, datetime, pathlib
from playwright.sync_api import sync_playwright
root=pathlib.Path(__file__).resolve().parents[1]
pos={"頭":(944,172),"右腕":(789,352),"胴体":(944,352),"左腕":(1094,352),"右足":(869,532),"左足":(1024,532)}
args=[a for a in sys.argv[1:] if a!="--submit"]; submit="--submit" in sys.argv
with sync_playwright() as p:
    ctx=p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
    page=[pg for pg in ctx.pages if "siosaigame" in pg.url][0]
    msgs=[]; page.on("dialog", lambda d:(msgs.append(d.message), d.accept()))
    for a in args:
        k,v=a.split("=",1); x,y=pos[k]
        page.mouse.click(x,y); page.keyboard.press("Control+A"); page.keyboard.type(v)
    page.wait_for_timeout(300)
    if submit:
        page.get_by_text("復活させる").first.click(); page.wait_for_timeout(2500)
    f=root/"data"/"screenshots"/f"{datetime.datetime.now():%Y%m%d-%H%M%S}-ritual.png"
    page.screenshot(path=str(f))
    vals=page.evaluate("()=>[...document.querySelectorAll('input')].map(e=>e.value)")
    with open(root/"data"/"actions.jsonl","a") as fp:
        fp.write(json.dumps({"time":datetime.datetime.now().isoformat(timespec="seconds"),"cmd":"ritual","arg":args,"submit":submit,"dialogs":msgs,"inputs":vals,"url":page.url,"shot":f.name},ensure_ascii=False)+"\n")
    print("dialogs:",msgs,"inputs:",vals,"url:",page.url); print(page.inner_text("body")[-300:])
