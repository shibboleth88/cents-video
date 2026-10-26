#!/usr/bin/env python3
"""Build Secret History captions so that no cue spans a picture cut.

Cut times come from build/scenes.json (the same anchors Film.tsx cuts on),
located in script/alignment.json. Writes captions/cues.json and captions.srt.

    python3 films/secret-history/build/captions.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]; FILM = ROOT / "films/secret-history"
sys.path.insert(0, str(ROOT / "pipeline")); import cues as C

norm = lambda t: re.sub(r"[^a-z0-9'-]", "", t.lower())

def locate(words, phrase):
    """Start time of `phrase` in the alignment. Exactly one match, or fail."""
    want = [norm(t) for t in phrase.split()]
    have = [norm(w["word"]) for w in words]
    hits = [i for i in range(len(have) - len(want) + 1) if have[i:i + len(want)] == want]
    if len(hits) != 1: raise SystemExit(f"anchor {phrase!r}: {len(hits)} matches, need exactly 1")
    return words[hits[0]]["start"]

def srt(cues):
    ts = lambda t: f"{int(t//3600):02}:{int(t%3600//60):02}:{int(t%60):02},{int(round(t%1*1000)):03}"
    return "\n".join(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n" for i, c in enumerate(cues, 1))

def main():
    words = json.loads((FILM / "script/alignment.json").read_text())["words"]
    scenes = json.loads((FILM / "build/scenes.json").read_text())["scenes"]
    cuts = [locate(words, s["from"]) for s in scenes if s["from"]]
    if len(cuts) < 5: raise SystemExit(f"FLOOR: only {len(cuts)} cuts located")

    # CONTROL: cues built blind to the cuts must trip the new audit check here,
    # or that check is measuring nothing on this film.
    blind = [b for b in C.audit(C.build(words), cuts) if "picture cut" in b]
    if not blind: raise SystemExit("VACUOUS: the cut check passes cues built without cuts")
    print(f"CONTROL  cut-blind build: {len(blind)} cue(s) span a cut, e.g. {blind[0]}")

    # Phrases the reader must see whole. The chunker knows function words, not
    # grammar, so an adjective can still be parted from its noun; this list
    # covers the narration's cases, and audit() catches the generic ones.
    keep = json.loads((FILM / "build/scenes.json").read_text()).get("keep_together", [])
    words = [dict(w) for w in words]
    for ph in keep:
        n = len(ph.split()); t = locate(words, ph)
        i = next(k for k, w in enumerate(words) if w["start"] == t)
        for w in words[i:i + n - 1]: w["nobreak"] = True
    cues = C.build(words, cuts)
    for c in cues: c.pop("nobreak", None)
    bad = C.audit(cues, cuts)
    for b in bad: print("  PROBLEM", b)
    (FILM / "captions/cues.json").write_text(json.dumps(cues, indent=1))
    (FILM / "captions/captions.srt").write_text(srt(cues))
    print(f"{len(cues)} cues, {len(cuts)} cuts, {len(bad)} problems")
    for c in cues: print(f"  {c['start']:6.2f} ({c['end']-c['start']:.2f}s) {c['text']}")
    return 1 if bad else 0

if __name__ == "__main__": sys.exit(main())
