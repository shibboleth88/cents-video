"""Build audio/vo.wav and script/alignment.json for Cent #9344 v1 from eee v1 take 2
(eleven_v4, "[thoughtfully] [calm]" at the start of the prompt; the tags are dropped from the words).
Copied from films/onecent-1264/audio/build_vo.py; only the source, the holds and the pad differ.

The word timings come from scribe_v1 run on the take fetched by URL (check_heard.py --write-alignment),
not from a transcript of the TTS node, which echoes the prompt. check_heard.py found the take equal to
audio/tts_text.txt, 317 of 317 tokens (one accepted, printed pair: "besides cent" for "beside cent").

Silent HOLDS are inserted in sentence gaps so the picture has time for the zooms, the ladder, the Blood
pool and the dissolve. Every edit point is the midpoint of a gap between words; it refuses if that point
is not inside a gap. Word timings are remapped through the edits. The end is padded for the closing card
and the credits.

    python3 -I films/onecent-9344/audio/build_vo.py   (from the repo root)
"""
import json, pathlib, re, subprocess, sys
F = pathlib.Path(__file__).resolve().parents[1]
SRC = F / "audio/v1_take2.mp3"
WORDS = [w for w in json.load(open(F / "audio/v1_take2_words.json"))["words"]
         if w["type"] == "word" and not w["text"].startswith("[")]
# v1 (2026-11-11): "CENTS carried the humblest of coins onto Bitcoin and into the galleries of U C C A Beijing." is cut
# and re-voiced (CLIPS). It said the coins went onto Bitcoin; their images were inscribed, and their copper (CENTS Block
# Copper) went to UCCA. The terms rule in CLAUDE.md keeps the penny, the image and the inscription apart.
CUTS = [("CENTS", "carried", "Beijing.")]
# A hold is (word, seconds) or (word, seconds, n) for the n-th time the word is spoken.
# "forty-four." 1.6 s: the opening card holds, so the year zoom on "nineteen seventy-four" lands after frame 150,
# where a 3DCENTS turn (150 frames) will have settled when the user's export arrives (v2), without retiming.
# "seven." lets the ladder be read; the first three traits get 0.6 s each so each zoom is seen, not flashed;
# "Cents." gives the seventeen Blood Cents their scroll; "out." the dissolve with #851.
HOLDS = [("forty-four.", 1.6, 1), ("mint.", 0.3), ("seven.", 1.0),
         ("Faceless.", 0.6), ("Corroded.", 0.6), ("Orange.", 0.6), ("Full.", 0.4), ("Gold.", 0.6),
         ("missing.", 0.4), ("Cents.", 2.2), ("out.", 1.0), ("marks.", 0.5), ("mark.", 0.4),
         ('choice."', 0.6), ('premise."', 0.6), ("it.", 0.6),
         ("face.", 0.6), ("Council.", 0.4), ("part.", 0.8)]
# 'things."' and "Beijing." held 0.8 and 0.4 s in the first build; the new line's lead and tail silences take their place.
# (word, nth, lead silence, file, tail silence, gain dB, words file, quoted). The line is the same voice, model and tags,
# voiced alone (take 2 of 2; check_heard.py: 20 of 20 tokens, "Sense" heard for "CENTS", printed). It is -26.7 LUFS
# against the take's -27.4, so it goes in 0.7 dB down before the whole is normalised.
CLIPS = [('things."', 1, 0.8, F / "audio/line_ucca_take2.mp3", 0.4, -0.7, F / "audio/line_ucca_take2_words.json", False)]
COMMA_HOLDS = set()
END_PAD = 6.5     # the closing line is spoken over the card, then the credits

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
    if len(hits) != 1:
        if FALLBACK: return None
        sys.exit(f"REFUSING: {len(hits)} pauses after {WORDS[i]['text']!r}")
    return (hits[0][0] + hits[0][1]) / 2
FALLBACK = False

edits = []   # (source time, kind, value): kind "cut" value = end time, "hold" value = seconds
removed = set()
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
QUIET_USED = []
# v7: a cut edge may sit at a comma with no 0.2 s pause ("forty-four,"); it then goes in the longest quiet run,
# like a hold, and is recorded in QUIET_USED.
def edge(i):
    global FALLBACK
    FALLBACK = True; t = gap_after(i); FALLBACK = False
    if t is None: t = quiet_after(i); QUIET_USED.append(WORDS[i]["text"] + " (cut)")
    return t
for a, b, last in CUTS:  # (none in #1264)
    hits = [i for i in range(len(WORDS) - 1) if WORDS[i]["text"] == a and WORDS[i + 1]["text"] == b]
    if len(hits) != 1: sys.exit(f"REFUSING: cut start {a} {b} found {len(hits)} times")
    i0 = hits[0]; i1 = next(j for j in range(i0, len(WORDS)) if WORDS[j]["text"] == last)
    edits.append((edge(i0 - 1), "cut", edge(i1))); removed |= set(range(i0, i1 + 1))
for text, secs, *nth in HOLDS:
    hits = [i for i, w in enumerate(WORDS) if w["text"] == text and i not in removed]
    if nth: hits = hits[nth[0] - 1:nth[0]]
    elif len(hits) != 1: sys.exit(f"REFUSING: hold word {text!r} occurs {len(hits)} times")
    if len(hits) != 1: sys.exit(f"REFUSING: hold word {text!r} occurrence {nth} not found")
    # #1264: this take often leaves under 0.2 s between sentences; then the hold goes in the longest quiet
    # run (at least 150 ms, the comma rule), and the fallback is recorded.
    FALLBACK = True
    t = None if text in COMMA_HOLDS else gap_after(hits[0])
    FALLBACK = False
    if t is None: t = quiet_after(hits[0]); QUIET_USED.append(text)
    edits.append((t, "hold", secs))
CLIP_AT = []
for text, nth, lead, path, tail, gain, wpath, quoted in CLIPS:
    hits = [i for i, w in enumerate(WORDS) if w["text"] == text and i not in removed][nth - 1:nth]
    if len(hits) != 1: sys.exit(f"REFUSING: clip word {text!r} occurrence {nth} not found")
    FALLBACK = True; t = gap_after(hits[0]); FALLBACK = False
    if t is None: t = quiet_after(hits[0]); QUIET_USED.append(text)
    cd = float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=duration",
                               "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout)
    edits.append((t, "clip", (lead, path, cd, tail, gain, wpath, quoted)))
# a hold and a cut can share an edit point (v5: "resides." holds, then the traits section is cut); the hold must
# come first, or the concat restarts at the cut's start and puts the whole cut section back (seen: 187 s, not ~111).
edits.sort(key=lambda e: (e[0], e[1] == "cut"))

filt, parts, last, inputs = [], [], 0.0, ["-i", str(SRC)]
for k, (t, kind, v) in enumerate(edits):
    filt.append(f"[0:a]atrim={last}:{t},asetpts=PTS-STARTPTS[p{k}]"); parts.append(f"[p{k}]")
    if kind == "clip":
        lead, path, cd, tail, gain, _, _q = v; inputs += ["-i", str(path)]; j = len(inputs) // 2 - 1
        filt.append(f"anullsrc=r=48000:cl=mono,atrim=0:{lead}[l{k}]")
        filt.append(f"[{j}:a]aformat=sample_rates=48000:channel_layouts=mono,volume={gain}dB,asetpts=PTS-STARTPTS[c{k}]")
        filt.append(f"anullsrc=r=48000:cl=mono,atrim=0:{tail}[t{k}]")
        parts += [f"[l{k}]", f"[c{k}]", f"[t{k}]"]; last = t
    elif kind == "hold":
        filt.append(f"anullsrc=r=48000:cl=mono,atrim=0:{v}[s{k}]"); parts.append(f"[s{k}]"); last = t
    else:
        last = v
filt.append(f"[0:a]atrim={last},asetpts=PTS-STARTPTS[pe]"); parts.append("[pe]")
filt.append(f"{''.join(parts)}concat=n={len(parts)}:v=0:a=1,aresample=48000,"
            f"loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur={END_PAD}[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt),
                "-map", "[out]", "-ar", "48000", "-ac", "1", str(F / "audio/vo.wav")], check=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            str(F / "audio/vo.wav")], capture_output=True, text=True, check=True).stdout)

LEN = lambda kind, v: v if kind == "hold" else (v[0] + v[2] + v[3])
def shift(t):
    d = 0.0
    for c, kind, v in edits:
        if c < t: d += LEN(kind, v) if kind in ("hold", "clip") else -(v - c)
    return round(t + d, 3)
# scribe ends overrun into the pause, so a word can straddle its own hold; its end is the edit point, not the end
# of the inserted silence (v2 let such words run on through the hold, which put "after_phrase" anchors past the pause).
def end_at(w):
    inside = [c for c, kind, _ in edits if w["start"] < c < w["end"]]
    return min(inside) - 1e-6 if inside else w["end"]
al = {"_source": "eee v1 take 2 (eleven_v4, [thoughtfully] [calm], script v0.2), heard by scribe_v1 from the take "
                 f"fetched by URL; equal to audio/tts_text.txt (check_heard.py); build_vo.py held {HOLDS}",
      "duration": round(dur, 2),
      "words": [{"word": w["text"], "start": shift(w["start"]), "end": shift(end_at(w))} for i, w in enumerate(WORDS) if i not in removed]}
# the clip's own words, at the clip's place: the line is captioned like the narration
for idx, (c, kind, v) in enumerate(edits):
    if kind != "clip": continue
    lead, path, cd, tail, gain, wpath, quoted = v
    # #9344: every edit BEFORE this one in the concat order, not only those at an earlier time. With "c2 < c", a hold
    # at the same pause as the clip (played first) was left out, which would place the clip's words a hold too early.
    d0 = sum(LEN(k2, v2) if k2 in ("hold", "clip") else -(v2 - c2) for c2, k2, v2 in edits[:idx])
    base = c + d0 + lead
    cw = [{"word": w["text"], "start": round(base + w["start"], 3), "end": round(base + w["end"], 3)}
          for w in json.load(open(wpath))["words"]]
    if quoted: cw[0]["word"] = '"' + cw[0]["word"]; cw[-1]["word"] += '."'
    k = next(i for i, w in enumerate(al["words"]) if w["start"] > base)
    al["words"][k:k] = cw
    print(f"clip {path.name}: audio starts at {base:.3f} s, ends {base + cd:.3f} s")
al["words"].sort(key=lambda w: w["start"])
json.dump(al, open(F / "script/alignment.json", "w"), indent=1)
print("holds in quiet runs (no 0.2 s pause):", QUIET_USED)
print(f"vo.wav {dur:.2f} s; {len(al['words'])} words; edits {[(round(c, 2), k) for c, k, _ in edits]}")
