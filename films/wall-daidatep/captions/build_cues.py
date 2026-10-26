"""Captions for the Daidatep episode: cut-aware cues on eo v1 take 1, with each
spoken number written back the way the script writes it. Each script word is
paired with its spoken words by a table of how many words it takes to say, so
the written form inherits their exact timing. Refuses unless the cue text
joins to exactly script/voiceover.txt.

    python3 -I films/wall-daidatep/captions/build_cues.py   (run from the repo root)
"""
import json, re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pipeline"))
import cues as C
F = ROOT / "films" / "wall-daidatep"
al = json.load(open(F / "script/alignment.json"))
tl = json.load(open(F / "timeline/timeline.json"))
norm = lambda s: re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("-", " ")).split()

# Written token (punctuation stripped) -> its spoken form, as in audio/tts_text.txt.
SPOKEN = {"9908": "ninety-nine oh eight", "3640": "thirty-six forty", "845": "eight forty-five",
          "132": "a hundred and thirty-two", "1/1": "one of one", "2026": "twenty twenty-six",
          "1960s": "nineteen sixties", "1970s": "nineteen seventies", "1980s": "nineteen eighties",
          "cents.vision": "cents dot vision", "3D": "three D"}
for y, s in {"1944": "forty-four", "1945": "forty-five", "1955": "fifty-five", "1956": "fifty-six", "1958": "fifty-eight",
             "1969": "sixty-nine", "1971": "seventy-one", "1979": "seventy-nine", "1982": "eighty-two"}.items():
    SPOKEN[y] = "nineteen " + s

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
bounds = [start_of(s["start"]["at_phrase"]) for s in tl["shots"] if "at_phrase" in s["start"]]

cues = C.build(out, bounds)
problems = C.audit(cues, bounds)
joined = " ".join(c["text"] for c in cues)
want = " ".join(open(F / "script/voiceover.txt").read().split())
if problems or joined != want:
    sys.exit(f"REFUSING: audit={problems} equals_script={joined == want}")
json.dump(cues, open(F / "captions/cues.json", "w"), indent=1)
print(f"{len(cues)} cues, text equals the script, audit clean")
