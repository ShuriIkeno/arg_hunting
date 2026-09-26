"""Click the embedded video to play it, then capture the player area every N seconds."""
import sys, time, datetime, json, pathlib
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
x, y, dur, step = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
out = ROOT / "data" / "video"
out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    ctx = p.chromium.connect_over_cdp("http://localhost:9222").contexts[0]
    page = next(pg for pg in ctx.pages if "/eidoLie/docs/" in pg.url)
    page.bring_to_front()
    page.mouse.click(x, y)
    t0 = time.time(); i = 0
    while time.time() - t0 < dur:
        page.mouse.move(10, 10)  # keep the player controls hidden
        page.screenshot(path=str(out / f"mv_{i:03d}_{int(time.time()-t0):03d}s.png"), clip={"x": 186, "y": 216, "width": 900, "height": 477})
        i += 1
        time.sleep(step)
    with (ROOT / "data" / "actions.jsonl").open("a") as fp:
        fp.write(json.dumps({"time": datetime.datetime.now().isoformat(timespec="seconds"), "cmd": "watch_video",
                             "arg": f"{dur}s every {step}s", "frames": i}) + "\n")
print(i, "frames")
