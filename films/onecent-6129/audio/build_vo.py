"""Build audio/vo.wav and script/alignment.json for Cent #6129 v3 from eo take 1.

Holds are inserted as silence in gaps between sentences, so the picture has time
where it needs it (the pan down the profile, the Faceless scroll, the patina
zooms). Word timings after each hold shift by the same amount. Each hold must
sit inside a gap of the recording: it refuses if a word spans the cut point.
The end is padded to give room for the closing spin card and the credits.

    python3 -I films/onecent-6129/audio/build_vo.py   (from the repo root)
"""
import json, pathlib, subprocess, sys
F = pathlib.Path(__file__).resolve().parents[1]
SRC = F / "audio/v3_take1.mp3"
WORDS = json.load(open(F / "audio/v3_take1_words.json"))["words"]
HOLDS = [("him.", 0.8), ("it.", 1.8), ("verdigris.", 1.2)]   # (word the hold follows, seconds)
END_PAD = 10.5

words = [w for w in WORDS if w["type"] == "word"]
cuts = []
for text, secs in HOLDS:
    hits = [i for i, w in enumerate(words) if w["text"] == text]
    if len(hits) != 1: sys.exit(f"REFUSING: {text!r} occurs {len(hits)} times")
    i = hits[0]
    t = (words[i]["end"] + words[i + 1]["start"]) / 2
    if not (words[i]["end"] < t < words[i + 1]["start"]): sys.exit(f"REFUSING: no gap after {text!r}")
    cuts.append((t, secs))

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
al = {"_source": "eo v3 take 1 (eleven_v4, script v0.5), transcribed with scribe_v1; word-for-word equal to "
                 f"audio/tts_text.txt; holds inserted by audio/build_vo.py: {HOLDS}",
      "duration": round(dur, 2),
      "words": [{"word": w["text"], "start": shift(w["start"]), "end": shift(w["end"])} for w in words]}
json.dump(al, open(F / "script/alignment.json", "w"), indent=1)
print(f"vo.wav {dur:.2f} s; holds at {[round(c, 2) for c, _ in cuts]}")
