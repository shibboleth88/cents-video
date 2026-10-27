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
         ("Red.", 2, 1.5), ("fifty-seven.", 1, 1.0), ("over.", 1, 0.6)]
# Passages taken out of the recording: from the pause after the first word to the pause
# after the second. The user dropped the "Lustrous CENTS" quote on 2026-10-27, keeping it
# for another film; the hold after "fifty-seven." then joins straight to "Coin collecting".
DROPS = [(("fifty-seven.", 1), ('ways."', 1))]
END_PAD = 11.5
# The closing line (user, 2026-10-27), a separate take in the same setting, spoken over the
# closing spin card: its first word starts CLOSE_AT s after the card starts. The card starts
# 0.8 s after the last narration word ends (timeline s10_card).
CLOSE = F / "audio/close_take1.mp3"
CLOSE_WORDS = json.load(open(F / "audio/close_take1_words.json"))["words"]
CARD_AFTER, CLOSE_AT = 0.8, 1.0

# Audio tags ([calm]) are direction, not speech: they never reach the captions.
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

cuts = [(pause_after(text, nth), secs) for text, nth, secs in HOLDS]
drops = [(pause_after(*a), pause_after(*b)) for a, b in DROPS]
for d0, d1 in drops:
    if any(d0 < c < d1 for c, _ in cuts): sys.exit("REFUSING: a hold falls inside a dropped passage")

def shift_(t): return round(t + sum(s_ for c, s_ in cuts if c < t) - sum(d1 - d0 for d0, d1 in drops if d1 <= t), 3)

# ffmpeg: keep the source between the drops, split at each hold, put silence between the pieces.
keep, last = [], 0.0
for d0, d1 in sorted(drops):
    keep.append((last, d0)); last = d1
keep.append((last, None))
parts, filt = [], []
for a, b in keep:
    edges = [a] + sorted(c for c, _ in cuts if c > a and (b is None or c < b)) + [b]
    for k in range(len(edges) - 1):
        x, y = edges[k], edges[k + 1]
        tag = f"p{len(parts)}"
        filt.append(f"[0:a]atrim={x}" + (f":{y}" if y is not None else "") + f",asetpts=PTS-STARTPTS[{tag}]"); parts.append(f"[{tag}]")
        secs = next((s_ for c, s_ in cuts if c == y), None)
        if secs:
            filt.append(f"anullsrc=r=48000:cl=mono,atrim=0:{secs}[s{len(parts)}]"); parts.append(f"[s{len(parts)}]")
src_dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(SRC)],
                               capture_output=True, text=True, check=True).stdout)
cw = [w for w in CLOSE_WORDS if w["type"] == "word" and not re.fullmatch(r"\[[^\]]*\]", w["text"])]
main_end = shift_(src_dur)
close_start = shift_(words[-1]["end"]) + CARD_AFTER + CLOSE_AT - cw[0]["start"]
gap = round(close_start - main_end, 3)
if gap < 0.5: sys.exit(f"REFUSING: the closing line would start {gap} s after the narration")
filt.append(f"anullsrc=r=48000:cl=mono,atrim=0:{gap}[gap]")
filt.append(f"[1:a]aresample=48000,aformat=channel_layouts=mono[close]")
parts += ["[gap]", "[close]"]
filt.append(f"{''.join(parts)}concat=n={len(parts)}:v=0:a=1,aresample=48000,"
            f"loudnorm=I=-16:TP=-1.5:LRA=11,apad=whole_dur={main_end + END_PAD}[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-i", str(CLOSE), "-filter_complex", ";".join(filt),
                "-map", "[out]", "-ar", "48000", "-ac", "1", str(F / "audio/vo.wav")], check=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            str(F / "audio/vo.wav")], capture_output=True, text=True, check=True).stdout)

shift = shift_
dropped = lambda w: any(d0 < w["start"] < d1 for d0, d1 in drops)
al = {"_source": "eee v4 take 1 (eleven_v4, [thoughtfully] [calm], script v0.4), transcribed with scribe_v1; word-for-word equal to "
                 f"audio/tts_text.txt; holds inserted by audio/build_vo.py: {HOLDS}; passages dropped: {DROPS}; closing line from audio/close_take1.mp3",
      "duration": round(dur, 2),
      "words": [{"word": w["text"], "start": shift(w["start"]), "end": shift(w["end"])} for w in words if not dropped(w)]
               + [{"word": w["text"], "start": round(close_start + w["start"], 3), "end": round(close_start + w["end"], 3)} for w in cw]}
# Check the edit against the audio itself: every word that follows a hold, a drop or the
# gap before the closing line must start where the built file's measured pause ends.
# (v3's first build doubled the hold at a drop's edge and ran 1 s late from there on.)
out_log = subprocess.run(["ffmpeg", "-i", str(F / "audio/vo.wav"), "-af", "silencedetect=n=-35dB:d=0.2", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out_log)]
joins = sorted({c for c, _ in cuts} | {d1 for _, d1 in drops})
after = [next(w for w in words if w["start"] > j and not dropped(w)) for j in joins]
checks = [(w["text"], shift(w["start"])) for w in after] + [(cw[0]["text"], round(close_start + cw[0]["start"], 3))]
if len(checks) < 5: sys.exit(f"FLOOR: only {len(checks)} joins checked")
bad = [(t, s_) for t, s_ in checks if not any(abs(e - s_) < 0.3 for e in ends)]
if bad: sys.exit(f"REFUSING: words not where the audio puts them: {bad}")
json.dump(al, open(F / "script/alignment.json", "w"), indent=1)
print(f"vo.wav {dur:.2f} s; {len(checks)} joins match the audio; holds at {[round(c, 2) for c, _ in cuts]}; dropped {drops}")
