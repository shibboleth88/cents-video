"""Check a voice take word for word against audio/tts_text.txt, then write script/alignment.json.

scribe_v1 returns the [thoughtfully] [calm] direction tags as tiny word tokens; they are
removed before the comparison. Punctuation becomes a space, never nothing, so a normalizer
cannot glue two words together. `--control` swaps one word of the TTS text and must fail.

    python3 -I films/wall-dopemind/audio/check_take.py v1_take1 <duration of vo.wav> [--control]
"""
import json, re, sys, pathlib
F = pathlib.Path(__file__).resolve().parents[1]
take, dur = sys.argv[1], float(sys.argv[2])
ws = [w for w in json.load(open(F / f"audio/{take}_words.json"))["words"] if w.get("type", "word") == "word"]
ws = [w for w in ws if not re.fullmatch(r"\[[a-z ]+\]", w["text"])]
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).split()
said = norm(" ".join(w["text"] for w in ws))
want = norm(open(F / "audio/tts_text.txt").read())
if "--control" in sys.argv:
    i = want.index("twelve"); want[i] = "eleven"
if said != want:
    k = next((i for i, (a, b) in enumerate(zip(said, want)) if a != b), min(len(said), len(want)))
    sys.exit(f"MISMATCH at word {k}: said {said[k-3:k+3]} vs script {want[k-3:k+3]} ({len(said)} vs {len(want)} words)")
print(f"{take}: {len(said)} words equal the TTS text")
if "--control" in sys.argv: sys.exit("CONTROL PASSED, which it must not")
al = {"_source": f"eee {take} (eleven_v4, [thoughtfully] [calm] per line, generation QmyfdR4scCGr4Zw27fhi, flow UZNvcf3IBLuAk76tCa40), script v1; scribe_v1 word timings with the tag tokens removed",
      "words": [{"word": w["text"], "start": w["start"], "end": w["end"]} for w in ws], "duration": dur}
json.dump(al, open(F / "script/alignment.json", "w"), indent=1)
print("wrote script/alignment.json, duration", dur)
