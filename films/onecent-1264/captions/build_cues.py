"""Captions for One Cent #1264 (copied from the Daidatep builder): cut-aware cues on the current eee take, with each
spoken number written back the way the script writes it. Each script word is
paired with its spoken words by a table of how many words it takes to say, so
the written form inherits their exact timing. Refuses unless the cue text
joins to exactly script/voiceover.txt.

    python3 -I films/onecent-8462/captions/build_cues.py   (run from the repo root)
"""
import json, re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pipeline"))
import cues as C
F = ROOT / "films" / "onecent-1264"
al = json.load(open(F / "script/alignment.json"))
tl = json.load(open(F / "timeline/timeline.json"))
norm = lambda s: re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("-", " ")).split()

# Written token (punctuation stripped) -> its spoken form, as in audio/tts_text.txt.
SPOKEN = {"#1264": "number twelve sixty-four", "1944": "nineteen forty-four", "1943": "nineteen forty-three",
          "22": "twenty-two", "10,000": "ten thousand", "1940s": "nineteen-forties", "2026": "twenty twenty-six",
          "12": "twelve", "70": "seventy", "69": "sixty-nine", "1956": "nineteen fifty-six", "#543": "number five forty-three",
          "1971": "nineteen seventy-one", "44": "forty-four", "1909": "nineteen oh nine", "1958": "nineteen fifty-eight",
          "208": "two hundred and eight", "US": "U.S.",
          "2024": "twenty twenty-four", "3.1": "three point one", "15": "fifteenth", "35": "thirty-five",
          "20th": "twentieth", "21st": "twenty-first",
          "–": ""}   # the spaced dash in the Lehnen quote is not said: it takes the time of the word before it

script = open(F / "script/voiceover.txt").read().split()
words, out, i = al["words"], [], 0
for tok in script:
    key = tok.rstrip(".,:;")
    n = len(SPOKEN[key].split()) if key in SPOKEN else 1
    said = words[i:i + n]
    if n == 0:
        out.append({"word": tok, "start": out[-1]["end"], "end": out[-1]["end"]}); continue
    if norm(" ".join(w["word"] for w in said)) != norm(SPOKEN.get(key, key)):
        sys.exit(f"REFUSING: script word {tok!r} does not match spoken {[w['word'] for w in said]}")
    out.append({"word": tok, "start": said[0]["start"], "end": said[-1]["end"]}); i += n
if i != len(words): sys.exit(f"REFUSING: {len(words) - i} spoken words left over")

# v3: the four example close-ups cut on single words ("paint,"), so the examples sentence is captioned as
# one sentence across those cuts instead of breaking into one-word cues at each.
RUN_ON = set()
flat = [(t, k) for k, w in enumerate(words) for t in norm(w["word"])]
def start_of(ph, end=False):
    n = norm(ph)
    hits = [flat[k][1] for k in range(len(flat) - len(n) + 1) if [x[0] for x in flat[k:k + len(n)]] == n]
    if len(hits) != 1: sys.exit(f"anchor {ph!r} found {len(hits)} times")
    if not end: return words[hits[0]]["start"]
    k = next(j for j in range(len(flat)) if flat[j][1] == hits[0])
    return words[flat[k + len(n) - 1][1]]["end"]
bounds = [start_of(s["start"]["at_phrase"]) if "at_phrase" in s["start"] else start_of(s["start"]["after_phrase"], True) + s["start"].get("plus", 0)
          for s in tl["shots"] if ("at_phrase" in s["start"] or "after_phrase" in s["start"]) and s["shot_id"] not in RUN_ON]

# #1264: "which no Wall had completed as of October 2026." wrapped to three Lead lines and left the safe
# area, so the cue is also broken at a phrase that is not a shot boundary.
EXTRA_BREAKS = []   # v1 broke the 1940s Set sentence; v2 has no such sentence
bounds = sorted(bounds + [start_of(ph) for ph in EXTRA_BREAKS])
cues = C.build(out, bounds)
problems = C.audit(cues, bounds)
joined = " ".join(c["text"] for c in cues)
want = " ".join(open(F / "script/voiceover.txt").read().split())
if problems or joined != want:
    sys.exit(f"REFUSING: audit={problems} equals_script={joined == want}")
json.dump(cues, open(F / "captions/cues.json", "w"), indent=1)
from align import srt
(F / "captions/captions.srt").write_text(srt(cues))
print(f"{len(cues)} cues, text equals the script, audit clean")
