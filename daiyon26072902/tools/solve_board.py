"""復活の神経衰弱を自動で解く。めくった絵柄の画像比較で同じパーツを見つけ、ペアをクリックする(画面操作のみ)。
usage: solve_board.py   (gisiki.html を開いて scroll 300 済みの状態で実行)"""
import io, json, time, datetime, pathlib
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright
root=pathlib.Path(__file__).resolve().parents[1]
xs=[197,319,441,563]; ys=[143,319,495]
pos=[(x,y) for y in ys for x in xs]
def crop(png,i):
    im=Image.open(io.BytesIO(png)).convert("L"); x,y=pos[i]
    return np.asarray(im.crop((x-45,y-60,x+45,y+30)).resize((30,30)),dtype=float)
with sync_playwright() as p:
    ctx=p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
    page=[pg for pg in ctx.pages if "gisiki" in pg.url][0]
    faces={}
    for a in range(0,12,2):
        for i in (a,a+1):
            page.mouse.click(*pos[i]); page.wait_for_timeout(450)
            faces[i]=crop(page.screenshot(),i)
        page.wait_for_timeout(1500)
    groups=[]
    for i in range(12):
        for g in groups:
            if np.abs(faces[g[0]]-faces[i]).mean()<12: g.append(i); break
        else: groups.append([i])
    print("groups:",groups)
    for g in groups:
        if len(g)==2:
            for i in g: page.mouse.click(*pos[i]); page.wait_for_timeout(450)
            page.wait_for_timeout(1500)
    print(page.inner_text("body")[-80:])
