"""Captions for One Cent #9344 (copied from films/onecent-1264/captions/build_cues.py): cut-aware cues on the current eee take, with each
spoken number written back the way the script writes it. Each script word is
paired with its spoken words by a table of how many words it takes to say, so
the written form inherits their exact timing. Refuses unless the cue text
joins to exactly script/voiceover.txt.

    python3 -I films/onecent-9344/captions/build_cues.py   (run from the repo root)
"""
import json, re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pipeline"))
import cues as C
F = ROOT / "films" / "onecent-9344"
al = json.load(open(F / "script/alignment.json"))
tl = json.load(open(F / "timeline/timeline.json"))
norm = lambda s: re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("-", " ")).split()

# Written token (punctuation stripped) -> its spoken form, as in audio/tts_text.txt.
SPOKEN = {"#9344": "number ninety-three forty-four", "#851": "number eight fifty-one", "1974": "nineteen seventy-four",
          "2017": "twenty seventeen", "1967": "nineteen sixty-seven", "UCCA": "U C C A"}

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

# Breaks at phrase edges where the length rule alone split a phrase ("with no mint | mark", "close | to mint state").
EXTRA_BREAKS = ["with no mint mark", "struck the same year", "whatever time had", "every one of those", "a particularly powerful", "of coins on Bitcoin"]
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
