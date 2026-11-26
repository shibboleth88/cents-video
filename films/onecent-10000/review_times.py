"""Times (s) for rehearsal stills: key moments of every shot, resolved from the timeline's anchors on
the current alignment (exact token match, as build_cues.py does). Prints space-separated seconds.

    python3 -I films/onecent-10000/review_times.py
"""
import json, re, pathlib
F = pathlib.Path(__file__).resolve().parent
al = json.load(open(F / "script/alignment.json")); tl = json.load(open(F / "timeline/timeline.json"))
W = al["words"]; norm = lambda s: re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("-", " ")).split()
flat = [(t, k) for k, w in enumerate(W) for t in norm(w["word"])]
def at(ph, end=False):
    n = norm(ph); hits = [k for k in range(len(flat) - len(n) + 1) if [x[0] for x in flat[k:k + len(n)]] == n]
    assert len(hits) == 1, (ph, len(hits))
    return W[flat[hits[0] + len(n) - 1][1]]["end"] if end else W[flat[hits[0]][1]]["start"]
def bound(b):
    if "at_start" in b: return 0.0
    if "at_end" in b: return al["duration"]
    if "at_phrase" in b: return at(b["at_phrase"])
    return at(b["after_phrase"], True) + b.get("plus", 0)
ts = []
for s in tl["shots"]:
    t0, t1 = bound(s["start"]), bound(s["end"]); p = s.get("props", {})
    keys = [p_["at_phrase"] for p_ in p.get("moves", [])] + ([p["quote"]["at_phrase"]] if "quote" in p else [])
    picks = [at(k) + 1.1 for k in keys if t0 <= at(k) < t1] or [(t0 + t1) / 2]
    if "quote" in p: picks.append(t1 - 0.3)
    if s["component"] in ("CentScroll",): picks = [t0 + 0.8, t1 - 0.3]
    if s["component"] == "CentDissolve": picks = [t0 + 0.8] + [at(w["at_phrase"]) + 0.8 for w in p["swaps"]]
    if s["shot_id"] == "s01_open": picks = [2.0, 4.9] + picks
    for t in picks: ts.append((round(min(t, t1 - 0.05), 2), s["shot_id"]))
print(" ".join(str(t) for t, _ in ts))
json.dump(ts, open(F / "review/times.json", "w"))
