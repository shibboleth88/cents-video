"""Anchor resolution shared by review_shots.py and verify.py, so the review
and the gates can never describe different cuts of the same timeline."""
from __future__ import annotations
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load():
    tl = json.loads((ROOT/"timeline"/"timeline.json").read_text())
    al = json.loads((ROOT/"script"/"alignment.json").read_text())
    return tl, al

def shot_times(tl, al) -> list[dict]:
    """Resolve anchors the same way the renderer does. Kept deliberately simple
    and separate: if this disagrees with the renderer the review is of a
    different film, so the frame count is cross-checked below."""
    def norm(s): 
        import re
        return re.sub(r"\s+"," ", s.lower().replace("'","").replace("’","")
                      .translate(str.maketrans("","", "\".,?!;:—-"))).strip()
    toks, idx = [], []
    for i, w in enumerate(al["words"]):
        for t in norm(w["word"]).split():
            toks.append(t); idx.append(i)
    def find(phrase):
        n = norm(phrase).split()
        hits = [i for i in range(len(toks)-len(n)+1) if toks[i:i+len(n)] == n]
        if len(hits) != 1: sys.exit(f"anchor {phrase!r} matched {len(hits)} times")
        return idx[hits[0]], idx[hits[0]+len(n)-1]
    def t_of(a):
        if a.get("at_start"): return 0.0
        if a.get("at_end"): return al["duration"]
        if "at_phrase" in a: return al["words"][find(a["at_phrase"])[0]]["start"]
        return al["words"][find(a["after_phrase"])[1]]["end"] + a.get("plus", 0)
    out = []
    for s in tl["shots"]:
        t0, t1 = t_of(s["start"]), t_of(s["end"])
        spoken = " ".join(w["word"] for w in al["words"] if t0 <= w["start"] < t1)
        out.append({**s, "t0": round(t0,3), "t1": round(t1,3), "narration": spoken})
    return out

