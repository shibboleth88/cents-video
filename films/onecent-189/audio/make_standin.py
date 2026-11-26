"""STAND-IN timing for the silent rehearsal (brief §7, #1328 lesson 1). Not a recording.

Writes script/alignment.json with fake word timings from audio/tts_text.txt (about 2.7 words a second,
pauses at punctuation, plus the holds build_vo.py is expected to insert) and a silent audio/vo.wav of
the same length, so the whole film renders as stills before any voice credits are spent. Every run
marks the alignment "_source": "STAND-IN" so it can't be mistaken for a heard take.

    python3 -I films/onecent-189/audio/make_standin.py   (from the repo root)
"""
import json, pathlib, re, subprocess
F = pathlib.Path(__file__).resolve().parents[1]
text = open(F / "audio/tts_text.txt").read()
text = re.sub(r"\[[a-z ]+\]", "", text).split()
# Holds after these words (seconds), as planned for build_vo.py (#189 v1, script v0.2). The narration starts at 1.2 s, once
# play is pressed; "eighty-nine." holds the 3DCENTS turn so line 2 arrives after frame 184 (34 + 150).
LEAD = 1.0
HOLDS = {"eighty-nine.": 3.3, "coin.": 0.0, 'medium."': 0.9, "been.": 0.3, "Red.": 0.3, "surface.": 0.4,
         "state.": 0.8, "time.": 0.6, "Cent.": 1.2}
PAD = 9.5   # closing turn, end cards and three credit cards
t, words = LEAD, []
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
