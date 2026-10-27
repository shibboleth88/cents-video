"""Build audio/vo.wav and script/alignment.json for Cent #2616 v2 from eee v4 take 1 (script v0.4).

Holds are inserted as silence in gaps between sentences, so the picture has time
where it needs it (the 1/1 Years scroll, the mint-year charts, the trait zooms,
the Full Red scroll). Word timings after each hold shift by the same amount.
eleven_v4 leaves almost no gap in its word timings, so each cut is placed in the
middle of a pause measured in the audio itself (ffmpeg silencedetect) that lies
between the word's start and the next word's end; it refuses if there is none.
The end is padded to give room for the closing spin card and the credits.

    python3 -I films/onecent-2616/audio/build_vo.py   (from the repo root)
"""
import json, pathlib, re, subprocess, sys
F = pathlib.Path(__file__).resolve().parents[1]
SRC = F / "audio/v4_take1.mp3"
WORDS = json.load(open(F / "audio/v4_take1_words.json"))["words"]
# (word the hold follows, which occurrence from 1, seconds)
HOLDS = [("nineteen.", 1, 0.6), ("survival.", 1, 0.8), ("seventy.", 1, 0.6), ("percent.", 1, 0.6), ("one.", 1, 0.6),
         ("Cents.", 1, 1.0), ('go."', 1, 0.6), ('relics."', 1, 1.0), ("glance.", 1, 0.8), ("dominant.", 1, 1.0),
         ("Red.", 2, 1.5), ("fifty-seven.", 1, 0.8), ('ways."', 1, 1.0), ("over.", 1, 0.6)]
END_PAD = 11.5

# Audio tags ([calm]) are direction, not speech: they never reach the captions.
words = [w for w in WORDS if w["type"] == "word" and not re.fullmatch(r"\[[^\]]*\]", w["text"])]
log = subprocess.run(["ffmpeg", "-i", str(SRC), "-af", "silencedetect=n=-35dB:d=0.2", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
ss = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", log)]
se = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]
pauses = list(zip(ss, se))
if len(pauses) < len(HOLDS): sys.exit(f"FLOOR: only {len(pauses)} pauses detected")
cuts = []
for text, nth, secs in HOLDS:
    hits = [i for i, w in enumerate(words) if w["text"] == text]
    if len(hits) < nth: sys.exit(f"REFUSING: {text!r} occurs {len(hits)} times, wanted occurrence {nth}")
    i = hits[nth - 1]
    gap = [p for p in pauses if words[i]["start"] < (p[0] + p[1]) / 2 < words[i + 1]["end"]]
    if len(gap) != 1: sys.exit(f"REFUSING: {len(gap)} measured pauses after {text!r}")
    cuts.append((round((gap[0][0] + gap[0][1]) / 2, 3), secs))

# ffmpeg: split at each cut, put silence between the pieces.
parts, filt, last = [], [], 0.0
for k, (t, secs) in enumerate(cuts):
    filt.append(f"[0:a]atrim={last}:{t},asetpts=PTS-STARTPTS[p{k}]")
    filt.append(f"anullsrc=r=48000:cl=mono,atrim=0:{secs}[s{k}]")
    parts += [f"[p{k}]", f"[s{k}]"]; last = t
filt.append(f"[0:a]atrim={last},asetpts=PTS-STARTPTS[pe]"); parts.append("[pe]")
filt.append(f"{''.join(parts)}concat=n={len(parts)}:v=0:a=1,aresample=48000,"
            f"loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur={END_PAD}[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-filter_complex", ";".join(filt),
                "-map", "[out]", "-ar", "48000", "-ac", "1", str(F / "audio/vo.wav")], check=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            str(F / "audio/vo.wav")], capture_output=True, text=True, check=True).stdout)

def shift(t): return round(t + sum(s for c, s in cuts if c < t), 3)
al = {"_source": "eee v4 take 1 (eleven_v4, [thoughtfully] [calm], script v0.4), transcribed with scribe_v1; word-for-word equal to "
                 f"audio/tts_text.txt; holds inserted by audio/build_vo.py: {HOLDS}",
      "duration": round(dur, 2),
      "words": [{"word": w["text"], "start": shift(w["start"]), "end": shift(w["end"])} for w in words]}
json.dump(al, open(F / "script/alignment.json", "w"), indent=1)
print(f"vo.wav {dur:.2f} s; holds at {[round(c, 2) for c, _ in cuts]}")
