"""拡大表示中の画像を高解像度で切り出す(見えている画面を拡大して撮るだけ)。
usage: hires.py <out.png> <x> <y> <w> <h> [scale=3]"""
import sys, base64
from playwright.sync_api import sync_playwright
out,x,y,w,h=sys.argv[1],*map(int,sys.argv[2:6]); sc=float(sys.argv[6]) if len(sys.argv)>6 else 3
with sync_playwright() as p:
    ctx=p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
    page=[pg for pg in ctx.pages if "siosaigame" in pg.url][0]
    s=ctx.new_cdp_session(page)
    r=s.send("Page.captureScreenshot",{"format":"png","clip":{"x":x,"y":y,"width":w,"height":h,"scale":sc}})
    open(out,"wb").write(base64.b64decode(r["data"]))
