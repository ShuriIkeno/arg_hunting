"""神経衰弱: 1枚以上のカードを素早くめくって、各クリック直後の画面を保存する(画面操作のみ)。
usage: flip.py <tag> <x,y> [<x,y> ...]"""
import sys, json, time, datetime, pathlib
from playwright.sync_api import sync_playwright
root=pathlib.Path(__file__).resolve().parents[1]
tag=sys.argv[1]; pts=[tuple(map(int,a.split(","))) for a in sys.argv[2:]]
with sync_playwright() as p:
    ctx=p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
    page=[pg for pg in ctx.pages if "siosaigame" in pg.url][0]
    shots=[]
    for i,(x,y) in enumerate(pts):
        page.mouse.click(x,y); page.wait_for_timeout(450)
        f=root/"data"/"screenshots"/f"{datetime.datetime.now():%Y%m%d-%H%M%S}-flip-{tag}-{i}.png"
        page.screenshot(path=str(f)); shots.append(f.name)
    with open(root/"data"/"actions.jsonl","a") as fp:
        fp.write(json.dumps({"time":datetime.datetime.now().isoformat(timespec="seconds"),"cmd":"flip","arg":sys.argv[2:],"note":tag,"result":"ok","url":page.url,"shot":shots},ensure_ascii=False)+"\n")
    print("\n".join(shots))
