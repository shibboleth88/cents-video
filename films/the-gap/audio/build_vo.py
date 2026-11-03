"""Build audio/vo.wav and script/alignment.json for The Gap v1 from eee v4 take 1 (script v0.1).

Holds are silence inserted in pauses measured in the audio itself (ffmpeg silencedetect),
so the picture has room at each turn: the opening date, the rounding, the copper gauge,
the gap, the pour. Word timings after each hold shift by the same amount. The end is
padded for the end card. Pattern from films/onecent-2616/audio/build_vo.py.

    python3 -I films/the-gap/audio/build_vo.py   (from the repo root)
"""
import json, pathlib, re, subprocess, sys
F = pathlib.Path(__file__).resolve().parents[1]
SRC = F / "audio/take1.mp3"
WORDS = json.load(open(F / "audio/take1_words.json"))["words"]
# (word the hold follows, which occurrence from 1, seconds)
HOLDS = [("circulation.", 1, 1.0), ("tender.", 1, 0.4), ("country.", 1, 0.6), ("away.", 1, 1.2), ("before.", 1, 0.5),
         ("cents.", 2, 1.0), ("more.", 1, 1.0), ("begins.", 1, 1.0), ("back.", 1, 0.6), ("kilograms.", 1, 1.4),
         ("satoshi.", 1, 1.0), ("measure.", 1, 0.8), ("ghost.", 1, 1.2), ("till.", 1, 0.6)]
END_PAD = 6.0

words = [w for w in WORDS if w["type"] == "word" and not re.fullmatch(r"\[[^\]]*\]", w["text"])]
log = subprocess.run(["ffmpeg", "-i", str(SRC), "-af", "silencedetect=n=-35dB:d=0.2", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
ss = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", log)]
se = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]
pauses = list(zip(ss, se))
if len(pauses) < len(HOLDS): sys.exit(f"FLOOR: only {len(pauses)} pauses detected")
def pause_after(text, nth):
    hits = [i for i, w in enumerate(words) if w["text"] == text]
    if len(hits) < nth: sys.exit(f"REFUSING: {text!r} occurs {len(hits)} times, wanted occurrence {nth}")
    i = hits[nth - 1]
    gap = [p for p in pauses if words[i]["start"] < (p[0] + p[1]) / 2 < words[i + 1]["end"]]
    if len(gap) != 1: sys.exit(f"REFUSING: {len(gap)} measured pauses after {text!r}")
    return round((gap[0][0] + gap[0][1]) / 2, 3)

cuts = [(pause_after(t, n), s) for t, n, s in HOLDS]
def shift(t): return round(t + sum(s for c, s in cuts if c < t), 3)

edges = [0.0] + sorted(c for c, _ in cuts) + [None]
parts, filt = [], []
for k in range(len(edges) - 1):
    x, y = edges[k], edges[k + 1]
    filt.append(f"[0:a]atrim={x}" + (f":{y}" if y is not None else "") + f",asetpts=PTS-STARTPTS[p{k}]"); parts.append(f"[p{k}]")
    secs = next((s for c, s in cuts if c == y), None)
    if secs:
        filt.append(f"anullsrc=r=48000:cl=mono,atrim=0:{secs}[s{k}]"); parts.append(f"[s{k}]")
src_dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(SRC)],
                               capture_output=True, text=True, check=True).stdout)
main_end = shift(src_dur)
filt.append(f"{''.join(parts)}concat=n={len(parts)}:v=0:a=1,aresample=48000,"
            f"loudnorm=I=-16:TP=-1.5:LRA=11,apad=whole_dur={main_end + END_PAD}[out]")
out = F / "audio/vo.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-filter_complex", ";".join(filt),
                "-map", "[out]", "-ar", "48000", "-ac", "1", str(out)], check=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                           capture_output=True, text=True, check=True).stdout)
al = {"_source": f"eee v4 take 1 (eleven_v4, [thoughtfully] [calm], script v0.1), scribe_v1; holds by audio/build_vo.py: {HOLDS}",
      "duration": round(dur, 2),
      "words": [{"word": w["text"], "start": shift(w["start"]), "end": shift(w["end"])} for w in words]}
# Every word after a hold must start where the built file's measured pause ends.
out_log = subprocess.run(["ffmpeg", "-i", str(out), "-af", "silencedetect=n=-35dB:d=0.2", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out_log)]
after = [next(w for w in words if w["start"] > c) for c, _ in cuts]
checks = [(w["text"], shift(w["start"])) for w in after]
if len(checks) < 5: sys.exit(f"FLOOR: only {len(checks)} joins checked")
bad = [(t, s) for t, s in checks if not any(abs(e - s) < 0.3 for e in ends)]
if bad: sys.exit(f"REFUSING: words not where the audio puts them: {bad}")
json.dump(al, open(F / "script/alignment.json", "w"), indent=1)
print(f"vo.wav {dur:.2f} s; {len(checks)} joins match the audio; holds at {[round(c, 2) for c, _ in cuts]}")
