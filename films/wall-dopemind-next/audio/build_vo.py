"""Build vo.wav and script/alignment.json from the chosen take.

  python3 -I films/wall-dopemind-next/audio/build_vo.py   (from the repo root)

1. Word check: scribe_v1 words, with the [thoughtfully] [calm] tag tokens removed,
   must equal audio/tts_text.txt (punctuation replaced by spaces, case folded).
   A control with one word changed must FAIL, or the check proves nothing.
   Caveat (as in films/onecent-6129): scribe on these flows returns the prompt's
   text, so this is forced alignment and weak evidence of what was said.
2. Audio: loudnorm I=-16 TP=-1.5 LRA=11, 48 kHz mono, padded to PAD_TO seconds:
   the question card holds ~2 s after the last word, then ~4.5 s of credits.
3. INSERT (v2.1): a silence of INSERT[1] s at INSERT[0] s of the take, for a silent
   on-screen card; every word after it moves by the same amount in the alignment.
   Refuses unless the cut falls in a pause between two words. INSERT = None is v2.
"""
import json, pathlib, re, subprocess, sys
F = pathlib.Path(__file__).resolve().parents[1]
TAKE = "v2_take1"
PAD_TO = 170.0
INSERT = (156.95, 3.0)   # after "from Lab to Market." (ends 156.70), before "What should" (157.20): the #8820 update card
words = [w for w in json.load(open(F / f"audio/{TAKE}_words.json"))["words"]
         if w.get("type", "word") == "word" and not re.fullmatch(r"\[[a-z ]+\]", w["text"])]
norm = lambda s: re.sub(r"[^a-z0-9' -]+", " ", s.lower().replace("’", "'")).split()
said = [t for w in words for t in norm(w["text"])]
want = norm(open(F / "audio/tts_text.txt").read())
def same(a, b): return a == b
if not same(said, want):
    i = next((k for k, (x, y) in enumerate(zip(said, want)) if x != y), min(len(said), len(want)))
    sys.exit(f"REFUSING: transcript differs from tts_text at word {i}: {said[i-3:i+3]} vs {want[i-3:i+3]}")
ctrl = list(want); ctrl[ctrl.index("patina")] = "surface"
if same(said, ctrl): sys.exit("CONTROL FAILED: a changed word still matched; the check is blind")
print(f"word check: {len(said)} words equal tts_text; control ('patina' -> 'surface') does not match")
last = words[-1]["end"]
if last + 6.0 > PAD_TO: sys.exit(f"REFUSING: last word ends {last:.2f}s, PAD_TO {PAD_TO} leaves under 6 s")
if INSERT:
    at, gap = INSERT
    before = [w for w in words if w["end"] <= at]; after = [w for w in words if w["start"] >= at]
    if len(before) + len(after) != len(words) or not before or not after:
        sys.exit(f"REFUSING: the insert at {at}s falls inside a word")
    last += gap
    if last + 6.0 > PAD_TO: sys.exit(f"REFUSING: with the insert the last word ends {last:.2f}s, PAD_TO {PAD_TO} leaves under 6 s")
    fc = (f"[0:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,asplit=2[a][b];"
          f"[a]atrim=0:{at},asetpts=PTS-STARTPTS,apad=pad_dur={gap}[a1];[b]atrim={at},asetpts=PTS-STARTPTS[b1];"
          f"[a1][b1]concat=n=2:v=0:a=1,apad=whole_dur={PAD_TO}[o]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(F / f"audio/{TAKE}.mp3"), "-filter_complex", fc, "-map", "[o]",
                    "-ar", "48000", "-ac", "1", str(F / "audio/vo.wav")], check=True)
    words = before + [{**w, "start": round(w["start"] + gap, 3), "end": round(w["end"] + gap, 3)} for w in after]
else:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(F / f"audio/{TAKE}.mp3"),
                    "-af", f"loudnorm=I=-16:TP=-1.5:LRA=11,apad=whole_dur={PAD_TO}", "-ar", "48000", "-ac", "1",
                    str(F / "audio/vo.wav")], check=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            str(F / "audio/vo.wav")], capture_output=True, text=True).stdout)
al = {"_source": f"eee {TAKE} (eleven_v4, [thoughtfully] [calm] per line); scribe_v1 word timings, tag tokens removed" + (f"; {INSERT[1]} s silence inserted at {INSERT[0]} s" if INSERT else ""),
      "duration": round(dur, 3),
      "words": [{"word": w["text"].strip('"'), "start": w["start"], "end": w["end"]} for w in words]}
json.dump(al, open(F / "script/alignment.json", "w"), indent=1)
print(f"vo.wav {dur:.2f}s; last word ends {last:.2f}s; alignment {len(al['words'])} words")
