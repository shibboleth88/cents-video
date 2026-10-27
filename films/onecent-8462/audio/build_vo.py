"""Build audio/vo.wav and script/alignment.json for Cent #8462 v3 from the eee "calm" take
(eleven_v4, "[thoughtfully] [calm]" at the start of the prompt; the tags are dropped from the words).
v1 (multilingual_v2, two sentences cut) is archive/build_vo_v1.py; v2 is archive/build_vo_v2.py.

Whole sentences can be CUT out of the take (CUTS; v1 cut two), and silent HOLDS are inserted in sentence gaps so the picture has time
for the zooms, the pool and the dissolve. Every edit point is the midpoint of a
gap between words; it refuses if that point is not inside a gap. Word timings
are remapped through the edits. The end is padded for the closing spin card and
the credits.

    python3 -I films/onecent-8462/audio/build_vo.py   (from the repo root)
"""
import json, pathlib, re, subprocess, sys
F = pathlib.Path(__file__).resolve().parents[1]
SRC = F / "audio/v3_take1.mp3"
WORDS = [w for w in json.load(open(F / "audio/v3_take1_words.json"))["words"]
         if w["type"] == "word" and not w["text"].startswith("[")]
CUTS = []
# v4 leaves short gaps between sentences, so the holds give the picture (and the listener) room.
# A hold is (word, seconds) or (word, seconds, n) for the n-th time the word is spoken ("trait." is said twice).
HOLDS = [("Philadelphia.", 0.4), ("rabbit.", 0.5), ("date.", 0.6), ("penny.", 0.6), ("trait.", 0.5, 1), ("coin.", 0.4),
         ("intentionality.", 0.6), ("example.", 0.7), ("trait.", 2.0, 2),
         ("scratches,", 1.0), ("attempt,", 1.0), ("paint,", 1.3), ("liner.", 1.2),
         ("seventy-three.", 1.0), ("year.", 0.4), ("engraved.", 0.7), ("meaning.", 0.5), ("not.\"", 0.9),
         ("satoshi.", 0.7), ("melting.", 0.9), ("uniqueness?\"", 1.4)]
# The commas of the examples list have no pause that silencedetect (0.2 s) finds; each of those holds goes in
# the longest run of quiet 10 ms windows (RMS under -35 dB, at least 150 ms: a stop consonant's closure gives 60 ms, as the control after "struck" showed) instead (v3: one close-up per example).
COMMA_HOLDS = {"scratches,", "attempt,", "paint,"}
END_PAD = 6.5     # v3: the closing line is spoken over the card, so less tail is needed

# scribe word ENDS run ~0.4 s into the following pause on v4 takes (seen by the #2616 thread, confirmed here:
# 9 of 15 gap midpoints fell on the next word's attack). So each edit point is the middle of a pause that
# ffmpeg silencedetect finds between the word's start and the next word's end; it refuses if there is none.
_out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(SRC), "-af", "silencedetect=n=-35dB:d=0.2", "-f", "null", "-"],
                      capture_output=True, text=True).stderr
_st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", _out)]
_en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", _out)]
SILENCES = list(zip(_st, _en))
if len(SILENCES) < 10: sys.exit(f"FLOOR: only {len(SILENCES)} pauses detected")

def gap_after(i):
    lo, hi = WORDS[i]["start"], WORDS[i + 1]["end"]
    hits = [(a, b) for a, b in SILENCES if lo < a and b < hi]
    if len(hits) != 1: sys.exit(f"REFUSING: {len(hits)} pauses after {WORDS[i]['text']!r}")
    return (hits[0][0] + hits[0][1]) / 2

edits = []   # (source time, kind, value): kind "cut" value = end time, "hold" value = seconds
removed = set()
for a, b, last in CUTS:
    hits = [i for i in range(len(WORDS) - 1) if WORDS[i]["text"] == a and WORDS[i + 1]["text"] == b]
    if len(hits) != 1: sys.exit(f"REFUSING: cut start {a} {b} found {len(hits)} times")
    i0 = hits[0]; i1 = next(j for j in range(i0, len(WORDS)) if WORDS[j]["text"] == last)
    edits.append((gap_after(i0 - 1), "cut", gap_after(i1))); removed |= set(range(i0, i1 + 1))
import numpy as np
_pcm = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(SRC), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                                    capture_output=True, check=True).stdout, np.int16).astype(float) / 32768
def quiet_after(i):
    lo, hi = int(WORDS[i]["start"] * 100), int(WORDS[i + 1]["end"] * 100)
    q = [20 * np.log10(np.sqrt(np.mean(_pcm[k * 160:(k + 1) * 160] ** 2)) + 1e-9) < -35 for k in range(lo, hi)]
    best, run, start = (0, 0), 0, 0
    for k, v in enumerate(q):
        run, start = (run + 1, start) if v else (0, k + 1)
        if run > best[0]: best = (run, start)
    if best[0] < 15: sys.exit(f"REFUSING: no quiet run of 150 ms after {WORDS[i]['text']!r}")
    return (lo + best[1] + best[0] / 2) / 100
for text, secs, *nth in HOLDS:
    hits = [i for i, w in enumerate(WORDS) if w["text"] == text and i not in removed]
    if nth: hits = hits[nth[0] - 1:nth[0]]
    elif len(hits) != 1: sys.exit(f"REFUSING: hold word {text!r} occurs {len(hits)} times")
    if len(hits) != 1: sys.exit(f"REFUSING: hold word {text!r} occurrence {nth} not found")
    edits.append(((quiet_after if text in COMMA_HOLDS else gap_after)(hits[0]), "hold", secs))
edits.sort()

filt, parts, last = [], [], 0.0
for k, (t, kind, v) in enumerate(edits):
    filt.append(f"[0:a]atrim={last}:{t},asetpts=PTS-STARTPTS[p{k}]"); parts.append(f"[p{k}]")
    if kind == "hold":
        filt.append(f"anullsrc=r=48000:cl=mono,atrim=0:{v}[s{k}]"); parts.append(f"[s{k}]"); last = t
    else:
        last = v
filt.append(f"[0:a]atrim={last},asetpts=PTS-STARTPTS[pe]"); parts.append("[pe]")
filt.append(f"{''.join(parts)}concat=n={len(parts)}:v=0:a=1,aresample=48000,"
            f"loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur={END_PAD}[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-filter_complex", ";".join(filt),
                "-map", "[out]", "-ar", "48000", "-ac", "1", str(F / "audio/vo.wav")], check=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            str(F / "audio/vo.wav")], capture_output=True, text=True, check=True).stdout)

def shift(t):
    d = 0.0
    for c, kind, v in edits:
        if c < t: d += v if kind == "hold" else -(v - c)
    return round(t + d, 3)
# scribe ends overrun into the pause, so a word can straddle its own hold; its end is the edit point, not the end
# of the inserted silence (v2 let such words run on through the hold, which put "after_phrase" anchors past the pause).
def end_at(w):
    inside = [c for c, kind, _ in edits if w["start"] < c < w["end"]]
    return min(inside) - 1e-6 if inside else w["end"]
al = {"_source": "eee v3 calm take (eleven_v4, [thoughtfully] [calm], script v3), transcribed with scribe_v1; equal to "
                 f"audio/tts_text.txt; build_vo.py held {HOLDS}",
      "duration": round(dur, 2),
      "words": [{"word": w["text"], "start": shift(w["start"]), "end": shift(end_at(w))} for i, w in enumerate(WORDS) if i not in removed]}
json.dump(al, open(F / "script/alignment.json", "w"), indent=1)
print(f"vo.wav {dur:.2f} s; {len(al['words'])} words; edits {[(round(c, 2), k) for c, k, _ in edits]}")
