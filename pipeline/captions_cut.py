#!/usr/bin/env python3
"""Rebuild the active film's captions so no cue spans a picture cut.

The cuts are the shot starts in timeline/timeline.json, resolved by anchors.py
exactly as the review resolves them. Same rules as Secret History's
build/captions.py (pipeline/cues.py: cut-aware build, weak-word breaks), for
films whose picture is a timeline.json.

    python3 pipeline/captions_cut.py [--keep "phrase" ...]

Phrases in timeline.json "caption_keep" are always kept whole.
"""
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
import anchors as A, cues as C
from align import srt

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--keep", nargs="*", default=[],
        help="phrases never to break inside")
    keep = ap.parse_args().keep
    tl, al = A.load()
    # A film can carry its own list, so a rebuild needs no remembered flags.
    keep = list(keep) + list(tl.get("caption_keep", []))
    words = [dict(w) for w in al["words"]]
    cuts = sorted({s["t0"] for s in A.shot_times(tl, al) if s["t0"] > 0})
    if len(cuts) < 3: sys.exit(f"FLOOR: only {len(cuts)} cuts in the timeline")
    # CONTROL: a cut-blind build must trip the cut check on this film.
    blind = [b for b in C.audit(C.build(words), cuts) if "picture cut" in b]
    if not blind: sys.exit("VACUOUS: the cut check passes cues built without cuts")
    print(f"CONTROL  cut-blind build: {len(blind)} cue(s) span a cut")
    toks = [w["word"].lower().strip(".,;:!?") for w in words]
    for ph in keep:
        p = ph.lower().split()
        hits = [i for i in range(len(toks) - len(p) + 1) if toks[i:i + len(p)] == p]
        if len(hits) != 1: sys.exit(f"keep {ph!r}: {len(hits)} matches, need exactly 1")
        for w in words[hits[0]:hits[0] + len(p) - 1]: w["nobreak"] = True
    cues = C.build(words, cuts)
    bad = C.audit(cues, cuts)
    for b in bad: print("  PROBLEM", b)
    (ROOT / "captions/cues.json").write_text(json.dumps(cues, indent=1))
    (ROOT / "captions/captions.srt").write_text(srt(cues))
    print(f"{len(cues)} cues, {len(cuts)} cuts, {len(bad)} problems")
    for c in cues: print(f"  {c['start']:6.2f} ({c['end']-c['start']:.2f}s) {c['text']}")
    return 1 if bad else 0

if __name__ == "__main__": sys.exit(main())
