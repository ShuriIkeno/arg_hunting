"""Record things the browser log cannot see.

Usage: python argkit/tools/log.py <game_dir> <kind> ...
  event human|contamination|environment|note "<text>"
        human         a person helped (gave a file, transcribed audio, changed settings)
        contamination you saw something a player would not (source code, file names, spoilers)
        environment   the sandbox blocked something (network, media, bot checks)
        note          anything else worth a timestamp
  page <id> [key=value ...]
        create or update an entry in data/pages.json. Keys: title, chapter, method (web|site|login|link|...),
        keyword, source (where the keyword came from), hint (true/false), human (true/false), found (ISO time).
        "found" defaults to now when the page is first recorded.
  phase "<label>" [start ISO] [end ISO]
        add a band to data/phases.json (start defaults to now; close it later with `phase-end`)
  phase-end
        set the end of the last open phase to now
"""
import sys, json, datetime, pathlib

game_dir = pathlib.Path(sys.argv[1]).resolve(); kind = sys.argv[2]; rest = sys.argv[3:]
data = game_dir / "data"; data.mkdir(parents=True, exist_ok=True)
now = datetime.datetime.now().isoformat(timespec="seconds")


def load(name, default):
    p = data / name
    return json.loads(p.read_text()) if p.exists() else default


def save(name, obj):
    (data / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")


if kind == "event":
    row = {"time": now, "type": rest[0], "text": " ".join(rest[1:])}
    with (data / "events.jsonl").open("a") as fp:
        fp.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(row)
elif kind == "page":
    pages = load("pages.json", [])
    pid = rest[0]
    p = next((x for x in pages if x["id"] == pid), None)
    if p is None:
        p = {"id": pid, "found": now}; pages.append(p)
    for kv in rest[1:]:
        k, v = kv.split("=", 1)
        p[k] = {"true": True, "false": False}.get(v, v)
    save("pages.json", pages); print(p)
elif kind == "phase":
    phases = load("phases.json", [])
    phases.append({"label": rest[0], "start": rest[1] if len(rest) > 1 else now, "end": rest[2] if len(rest) > 2 else None})
    save("phases.json", phases); print(phases[-1])
elif kind == "phase-end":
    phases = load("phases.json", [])
    open_ = [p for p in phases if not p.get("end")]
    if open_:
        open_[-1]["end"] = now
    save("phases.json", phases); print(open_[-1] if open_ else "no open phase")
else:
    sys.exit(__doc__)
