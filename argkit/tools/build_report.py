"""Build the play-log dashboard for one game directory.

Usage: python argkit/tools/build_report.py <game_dir> [--out <game_dir>/viz/index.html]

Reads the files described in argkit/FORMAT.md (game.json, data/actions.jsonl, data/pages.json,
data/hints.jsonl, data/events.jsonl, and the optional data/phases.json, data/stuck.json,
data/deps.json, data/endings.json), computes the summary numbers, and writes one self-contained
HTML page from argkit/dashboard/template.html.
"""
import json, re, sys, pathlib, datetime
from collections import OrderedDict

KIT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = KIT / "dashboard" / "template.html"
SEARCH_CMDS = {"search", "typeat", "sitesearch", "type"}


def read_json(p, default=None):
    return json.loads(p.read_text()) if p.exists() else default


def read_jsonl(p):
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def parse(ts):
    return datetime.datetime.fromisoformat(ts)


def main():
    game_dir = pathlib.Path(sys.argv[1]).resolve()
    out = pathlib.Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else game_dir / "viz" / "index.html"
    data = game_dir / "data"
    game = read_json(game_dir / "game.json") or read_json(data / "game.json")
    if game is None:
        sys.exit("game.json not found")
    actions = read_jsonl(data / "actions.jsonl")
    hints = read_jsonl(data / "hints.jsonl")
    events = read_jsonl(data / "events.jsonl")
    pages = read_json(data / "pages.json", [])
    phases = read_json(data / "phases.json", [])
    stuck = read_json(data / "stuck.json")
    deps = read_json(data / "deps.json")
    endings = read_json(data / "endings.json")
    if not actions:
        sys.exit("data/actions.jsonl is empty")
    # the main play ends at game.json "play_end" (later rows are replays and are left out of the charts)
    if game.get("play_end"):
        actions = [a for a in actions if a["time"] <= game["play_end"]]

    t0 = parse(actions[0]["time"])
    day0 = t0.replace(hour=0, minute=0, second=0, microsecond=0)

    def hms(ts):
        """ISO time -> 'HH:MM:SS' counted from the first day's midnight (hours may pass 24)."""
        s = int((parse(ts) - day0).total_seconds())
        return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"

    def minutes(ts):
        return (parse(ts) - day0).total_seconds() / 60

    # pages: fill missing "found" from the progress counter in logged titles
    prog = re.compile(game.get("progress_regex", r"\[(\d+|ex|EX)/\d+\]"))
    first_seen = {}
    for a in actions:
        m = prog.search(a.get("title") or a.get("browser_title") or "")
        if m:
            first_seen.setdefault(m.group(1).upper() if m.group(1).lower() == "ex" else m.group(1), a["time"])
    for p in pages:
        if not p.get("found") and p["id"] in first_seen:
            p["found"] = first_seen[p["id"]]
    # pages seen through the progress counter but never annotated still count (method unknown)
    known = {p["id"] for p in pages}
    for pid, ts in first_seen.items():
        if pid not in known:
            pages.append({"id": pid, "found": ts, "title": f"#{pid}", "method": "link", "source": "（未注記）"})
    pages_out = [dict(p, t=hms(p["found"])) for p in pages if p.get("found")]

    # search activity in 5-minute bins
    lo = int(minutes(actions[0]["time"]) // 5 * 5)
    hi = int(minutes(actions[-1]["time"]) // 5 * 5)
    bins = OrderedDict((m, 0) for m in range(lo, hi + 5, 5))
    keywords, hit_keywords = [], set()
    nav = set(game.get("nav_keywords", []))
    for a in actions:
        if a["cmd"] not in SEARCH_CMDS:
            continue
        bins[int(minutes(a["time"]) // 5 * 5)] = bins.get(int(minutes(a["time"]) // 5 * 5), 0) + 1
        kw = a.get("keyword") or (a["arg"].split(" ", 2)[2] if a["cmd"] == "typeat" and a["arg"].count(" ") >= 2 else a["arg"])
        if kw not in keywords:
            keywords.append(kw)
        if a.get("hit") is True:
            hit_keywords.add(kw)

    # hint markers: hint opens closer than 2 minutes are one marker
    markers = []
    for h in hints:
        top = h["path"][0] if h.get("path") else ""
        if markers and (parse(h["time"]) - parse(markers[-1]["last"])).total_seconds() < 120:
            if top and top not in markers[-1]["tops"]:
                markers[-1]["tops"].append(top)
            markers[-1]["last"] = h["time"]
        else:
            markers.append({"time": h["time"], "last": h["time"], "tops": [top] if top else []})
    hint_markers = [{"t": hms(m["time"]), "label": "・".join(m["tops"]) or "ヒント"} for m in markers]

    # stuck episodes: compute times, failed keywords before the first hint, and the hints read
    page_kws = {p.get("keyword") for p in pages if p.get("keyword")}
    if stuck:
        for e in stuck.get("episodes", []):
            ep_hints = [h for h in hints if h.get("episode") == e.get("hint_episode", e["id"])]
            first_hint = min((h["time"] for h in ep_hints), default=e["end"])
            if e.get("tried_from_log"):
                tried = []
                for a in actions:
                    if a["cmd"] in SEARCH_CMDS and e["start"] <= a["time"] <= first_hint:
                        kw = a.get("keyword") or (a["arg"].split(" ", 2)[2] if a["cmd"] == "typeat" and a["arg"].count(" ") >= 2 else a["arg"])
                        if kw not in nav and kw not in page_kws and a.get("hit") is not True and kw not in tried:
                            tried.append(kw)
                limit = e.get("tried_limit", 36)
                e["tried"], e["tried_more"] = tried[:limit], (f"{len(tried) - limit}（計{len(tried)}）" if len(tried) > limit else None)
            e["hints"] = [{"label": " · ".join(h["path"][-2:]) if len(h["path"]) > 1 else h["path"][0], "text": h["text"]}
                          for h in ep_hints if h.get("text") and not h["text"].startswith("（見出し")]
            e["t_start"], e["t_end"] = hms(e["start"]), hms(e["end"])
            e["minutes"] = round((parse(e["end"]) - parse(e["start"])).total_seconds() / 60)

    dur = parse(actions[-1]["time"]) - t0
    over = game.get("stats_override", {})
    stats = {
        "actions": len(actions),
        "pages_found": len(pages_out),
        "start": t0.strftime("%H:%M"), "end": parse(actions[-1]["time"]).strftime("%H:%M"),
        "duration": f"{int(dur.total_seconds() // 3600)}:{int(dur.total_seconds() % 3600 // 60):02d}",
        "keywords": len(keywords),
        "keyword_hits": over.get("keyword_hits", len(hit_keywords) if hit_keywords else None),
        "hint_topics": len({h["path"][0] for h in hints if h.get("path")}),
        "hint_opens": len(hints),
        "retries": over.get("retries"), "retries_note": over.get("retries_note"),
    }
    D = {
        "game": game, "stats": stats, "pages": pages_out,
        "range": {"start": hms(actions[0]["time"]), "end": hms(actions[-1]["time"])},
        "phases": [{"label": p["label"], "start": hms(p["start"]), "end": hms(p.get("end") or actions[-1]["time"])} for p in phases],
        "hint_markers": hint_markers,
        "events": [dict(e, t=hms(e["time"])) for e in events],
        "search5": [[m, v] for m, v in bins.items()],
        "milestones": [{"t": hms(m["time"]), "label": m["label"]} for m in game.get("milestones", [])],
        "activity_notes": [{"t": hms(n["time"]), "label": n["label"]} for n in game.get("activity_notes", [])],
        "stuck": stuck, "deps": deps, "endings": endings,
    }
    html = TEMPLATE.read_text()
    html = html.replace("__TITLE__", game.get("title", "ARG play log"))
    html = html.replace("/*__DATA__*/null", json.dumps(D, ensure_ascii=False).replace("</", "<\\/"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print(f"wrote {out} ({len(html):,} bytes): {stats['pages_found']}/{game.get('total_pages')} pages, "
          f"{stats['actions']} actions, {len(hint_markers)} hint markers")


if __name__ == "__main__":
    main()
