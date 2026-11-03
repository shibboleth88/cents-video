"""Captions for The Gap: cut-aware cues on eee v4 take 1, numbers written as the script
writes them (from films/onecent-2616/captions/build_cues.py). Cuts come from
build/scenes.json. Refuses unless the cue text joins to exactly script/voiceover.txt.
Also writes captions/the-gap.srt.

    python3 -I films/the-gap/captions/build_cues.py   (run from the repo root)
"""
import json, re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pipeline"))
import cues as C
F = ROOT / "films" / "the-gap"
al = json.load(open(F / "script/alignment.json"))
scenes = json.load(open(F / "build/scenes.json"))["scenes"]
norm = lambda s: re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("-", " ")).split()

SPOKEN = {"2025": "twenty twenty-five", "2026": "twenty twenty-six", "2024": "twenty twenty-four", "20": "twenty",
          "1982": "nineteen eighty-two", "95%": "ninety-five percent", "10,000": "ten thousand", "31": "thirty-one"}

script = open(F / "script/voiceover.txt").read().split()
words, out, i = al["words"], [], 0
for tok in script:
    key = tok.rstrip(".,:;")
    n = len(SPOKEN[key].split()) if key in SPOKEN else 1
    said = words[i:i + n]
    if norm(" ".join(w["word"] for w in said)) != norm(SPOKEN.get(key, key)):
        sys.exit(f"REFUSING: script word {tok!r} does not match spoken {[w['word'] for w in said]}")
    out.append({"word": tok, "start": said[0]["start"], "end": said[-1]["end"]}); i += n
if i != len(words): sys.exit(f"REFUSING: {len(words) - i} spoken words left over")

flat = [(t, k) for k, w in enumerate(words) for t in norm(w["word"])]
def start_of(ph):
    n = norm(ph)
    hits = [flat[k][1] for k in range(len(flat) - len(n) + 1) if [x[0] for x in flat[k:k + len(n)]] == n]
    if len(hits) != 1: sys.exit(f"anchor {ph!r} found {len(hits)} times")
    return words[hits[0]]["start"]
bounds = [start_of(s["from"]) for s in scenes if s["from"]]
if len(bounds) != len(scenes) - 1: sys.exit("FLOOR: a scene cut was not resolved")

cues = C.build(out, bounds)
problems = C.audit(cues, bounds)
joined = " ".join(c["text"] for c in cues)
want = " ".join(script)
if problems or joined != want:
    sys.exit(f"REFUSING: audit={problems} equals_script={joined == want}")
json.dump(cues, open(F / "captions/cues.json", "w"), indent=1)
ts = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
with open(F / "captions/the-gap.srt", "w") as fh:
    for k, c in enumerate(cues, 1):
        fh.write(f"{k}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n\n")
print(f"{len(cues)} cues, text equals the script, audit clean, {len(bounds)} cuts")
