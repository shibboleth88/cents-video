"""Times (s) for rehearsal stills of One Cent #189: for every shot, its middle and a moment just before it ends,
resolved from the timeline's anchors on the current alignment (exact token match, as build_cues.py does).
Prints "shot_id t" lines, or with --flat the seconds space-separated.

    python3 -I films/onecent-189/review_times.py [--flat]
"""
import json, re, sys, pathlib
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
out = []
for s in tl["shots"]:
    t0, t1 = bound(s["start"]), bound(s["end"])
    assert t1 > t0, (s["shot_id"], t0, t1)
    picks = sorted({round((t0 + t1) / 2, 2), round(t1 - 0.12, 2)})
    out += [(s["shot_id"], t, round(t1 - t0, 2)) for t in picks]
if "--flat" in sys.argv: print(" ".join(str(t) for _, t, _ in out))
else:
    for sid, t, d in out: print(sid, t, d)
