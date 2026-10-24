"""Captions for the blacktongue pilot: cut-aware cues on eo take A, with the
spoken numbers written back as the script writes them (5185, 1968, 24 October
2026). Refuses unless the cue text joins to exactly script/voiceover.txt.

    python3 -I films/wall-blacktongue/captions/build_cues.py   (run from the repo root)
"""
import json, re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pipeline"))
import cues as C
F = ROOT / "films" / "wall-blacktongue"
al = json.load(open(F / "script/alignment.json"))
tl = json.load(open(F / "timeline/timeline.json"))
norm = lambda s: re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("-", " ")).split()

# Spoken run -> written form, merged into one timed word.
WRITTEN = [("fifty-one eighty-five,", "5185,"), ("nineteen sixty-eight,", "1968,"),
           ("nineteen thirty-eight", "1938"), ("nineteen thirty-eight.", "1938."), ("nineteen eighty.", "1980."),
           ("October twenty twenty-six,", "October 2026,"), ("cents dot vision", "cents.vision")]
words = [dict(w) for w in al["words"]]
out, i = [], 0
while i < len(words):
    for spoken, written in WRITTEN:
        n = len(spoken.split())
        if " ".join(w["word"] for w in words[i:i + n]) == spoken:
            out.append({"word": written, "start": words[i]["start"], "end": words[i + n - 1]["end"]}); i += n; break
    else:
        out.append(words[i]); i += 1

flat = [(t, k) for k, w in enumerate(al["words"]) for t in norm(w["word"])]
def start_of(ph):
    n = norm(ph)
    hits = [flat[k][1] for k in range(len(flat) - len(n) + 1) if [x[0] for x in flat[k:k + len(n)]] == n]
    if len(hits) != 1: sys.exit(f"anchor {ph!r} found {len(hits)} times")
    return al["words"][hits[0]]["start"]
bounds = [start_of(s["start"]["at_phrase"]) for s in tl["shots"] if "at_phrase" in s["start"]]

cues = C.build(out, bounds)
problems = C.audit(cues, bounds)
joined = " ".join(c["text"] for c in cues)
want = " ".join(open(F / "script/voiceover.txt").read().split())
if problems or joined != want:
    sys.exit(f"REFUSING: audit={problems} equals_script={joined == want}")
json.dump(cues, open(F / "captions/cues.json", "w"), indent=1)
print(f"{len(cues)} cues, text equals the script, audit clean")
