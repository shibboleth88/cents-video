"""Build audio/vo.wav and script/alignment.json for Cent #8462 v1 from eee take 1.

Two sentences are CUT out of the take (the v1 length decision: the full take ran
121 s), and silent HOLDS are inserted in sentence gaps so the picture has time
for the zooms, the pool and the dissolve. Every edit point is the midpoint of a
gap between words; it refuses if that point is not inside a gap. Word timings
are remapped through the edits. The end is padded for the closing spin card and
the credits.

    python3 -I films/onecent-8462/audio/build_vo.py   (from the repo root)
"""
import json, pathlib, subprocess, sys
F = pathlib.Path(__file__).resolve().parents[1]
SRC = F / "audio/v1_take1.mp3"
WORDS = [w for w in json.load(open(F / "audio/v1_take1_words.json"))["words"] if w["type"] == "word"]
CUTS = [("The", "Council", "this?"), ("The", "penny", "melting.")]     # (first word, second word, last word) of each sentence removed
HOLDS = [("rabbit.", 0.4), ("date.", 0.6), ("example.", 0.6), ("seventy-three.", 1.2), ("engraved.", 0.6)]
END_PAD = 10.5

def gap_after(i):
    t = (WORDS[i]["end"] + WORDS[i + 1]["start"]) / 2
    if not (WORDS[i]["end"] < t < WORDS[i + 1]["start"]): sys.exit(f"REFUSING: no gap after {WORDS[i]['text']!r}")
    return t

edits = []   # (source time, kind, value): kind "cut" value = end time, "hold" value = seconds
removed = set()
for a, b, last in CUTS:
    hits = [i for i in range(len(WORDS) - 1) if WORDS[i]["text"] == a and WORDS[i + 1]["text"] == b]
    if len(hits) != 1: sys.exit(f"REFUSING: cut start {a} {b} found {len(hits)} times")
    i0 = hits[0]; i1 = next(j for j in range(i0, len(WORDS)) if WORDS[j]["text"] == last)
    edits.append((gap_after(i0 - 1), "cut", gap_after(i1))); removed |= set(range(i0, i1 + 1))
for text, secs in HOLDS:
    hits = [i for i, w in enumerate(WORDS) if w["text"] == text and i not in removed]
    if len(hits) != 1: sys.exit(f"REFUSING: hold word {text!r} occurs {len(hits)} times")
    edits.append((gap_after(hits[0]), "hold", secs))
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
al = {"_source": "eee v1 take 1 (eleven_multilingual_v2, script v0.1 full), transcribed with scribe_v1; equal to "
                 f"archive/tts_text_v0.1_full.txt; build_vo.py cut {CUTS} and held {HOLDS}",
      "duration": round(dur, 2),
      "words": [{"word": w["text"], "start": shift(w["start"]), "end": shift(w["end"])} for i, w in enumerate(WORDS) if i not in removed]}
json.dump(al, open(F / "script/alignment.json", "w"), indent=1)
print(f"vo.wav {dur:.2f} s; {len(al['words'])} words; edits {[(round(c, 2), k) for c, k, _ in edits]}")
