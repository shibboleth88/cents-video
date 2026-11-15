"""STAND-IN timing for the silent rehearsal (brief §7, #1328 lesson 1). Not a recording.

Writes script/alignment.json with fake word timings from audio/tts_text.txt (about 2.7 words a second,
pauses at punctuation, plus the holds build_vo.py is expected to insert) and a silent audio/vo.wav of
the same length, so the whole film renders as stills before any voice credits are spent. Every run
marks the alignment "_source": "STAND-IN" so it can't be mistaken for a heard take.

    python3 -I films/onecent-8820/audio/make_standin.py   (from the repo root)
"""
import json, pathlib, re, subprocess
F = pathlib.Path(__file__).resolve().parents[1]
text = open(F / "audio/tts_text.txt").read()
text = re.sub(r"\[[a-z ]+\]", "", text).split()
# Holds after these words (seconds), as planned for build_vo.py. The first moves the year zoom past frame 150.
HOLDS = {"twenty.": 2.0, "mint.": 0.4, "face.": 0.6, "zones.": 0.4, "it.": 1.2, "time.": 0.6, "else.": 1.0,
         "patinas\".": 0.8, "cent.": 0.8, "decay.": 0.8, "ownership.\"": 0.6, "own.": 0.6,
         "authenticity.\"": 0.4, "gone.": 1.4, "image.": 0.8}
PAD = 6.5   # closing turn and credits
t, words = 0.3, []
for w in text:
    letters = len(re.sub(r"[^A-Za-z]", "", w))
    d = 0.08 + 0.046 * letters
    words.append({"word": w, "start": round(t, 3), "end": round(t + d, 3)})
    t += d + 0.04
    if w.endswith((".", ".\"", "?")): t += 0.4
    elif w.endswith((",", ",\"", ":", ";")): t += 0.15
    t += HOLDS.get(w, 0)
dur = round(t + PAD, 2)
json.dump({"_source": "STAND-IN for the silent rehearsal: fake timings from audio/tts_text.txt, not a recording. Replace with the heard take (check_heard.py --write-alignment).",
           "duration": dur, "words": words}, open(F / "script/alignment.json", "w"), indent=1)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(dur),
                "-c:a", "pcm_s16le", str(F / "audio/vo.wav")], check=True)
print(f"{len(words)} words, narration ends {t:.1f} s, duration {dur} s ({len(words)/(t-sum(HOLDS.values())):.2f} words/s without holds)")
