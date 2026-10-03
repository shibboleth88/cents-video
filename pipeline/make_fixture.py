#!/usr/bin/env python3
"""Generate a SYNTHETIC alignment + cues so the renderer and gates can be
exercised before a real voiceover exists.

This is a FIXTURE, NOT A MEASUREMENT. Word times are invented at a constant
rate. Every file it writes is stamped so it cannot be mistaken for aligned
output from a real recording. align.py overwrites these with real timings.
"""
import json, pathlib, sys

WPM = 138.0
TEXT = (
    "What happens when a systems artwork produces something the system itself "
    "cannot witness. Rutherford Chang's CENTS begins with a discrepancy. "
    "A penny is photographed, catalogued, and inscribed. The object persists. "
    "The record of the object persists. What goes missing is the link between them. "
    "That gap is not an error in the work. It is the work's newest layer."
)
root = pathlib.Path(__file__).resolve().parent.parent
words, t, spw = [], 0.0, 60.0 / WPM
for w in TEXT.split():
    words.append({"word": w, "start": round(t, 3), "end": round(t + spw * 0.86, 3)})
    t += spw
al = {"_fixture": True, "_warning": "SYNTHETIC. Not measured from a recording.",
      "words": words, "duration": round(t + 0.6, 3)}
(root / "script").mkdir(exist_ok=True)
(root / "script" / "alignment.json").write_text(json.dumps(al, indent=1))

# Cues come from the SAME chunker the real pipeline uses, so the fixture
# exercises the real code path rather than a convenient simplification.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import cues as C
cues = C.build(words)
problems = C.audit(cues)
if problems:
    sys.exit("fixture cues are unusable:\n  " + "\n  ".join(problems))
(root / "captions").mkdir(exist_ok=True)
(root / "captions" / "cues.json").write_text(json.dumps(cues, indent=1))
print(f"fixture: {len(words)} words, {al['duration']}s, {len(cues)} cues")
