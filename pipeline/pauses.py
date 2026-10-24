#!/usr/bin/env python3
"""Open held silences in a recorded voiceover, and move its word timings with it.

Narration drives timing, so the only honest way to give a picture more screen
time is to give it more audio time. This inserts silence after named phrases
of an existing take — no re-recording, no time-stretch, the voice untouched —
and shifts every later word timing by exactly the silence inserted.

  python3 pipeline/pauses.py films/<film>/audio/takeA.mp3 \
      films/<film>/audio/takeA_words.json films/<film>/audio/pauses.json \
      --out-wav films/<film>/audio/vo.wav --out-words films/<film>/audio/vo_words.json

pauses.json: [{"after": "<phrase ending at the cut>", "seconds": 1.4}, ...]
Each phrase must match the transcript exactly once. The cut goes at the
quietest 10 ms near the gap after the phrase's last word. Word timings from
a recogniser run a little late, so the search starts up to 0.3 s before the
word's reported end. A cut is refused unless the LOUDEST 10 ms within 25 ms of
it is below QUIET_DB (relative to the take's RMS): a single quiet 10 ms window
can sit inside a word (the "features to" join measured -32 dB there and was
heard as a glitch), while a real gap stays quiet on both sides.
"""
from __future__ import annotations
import argparse, json, pathlib, re, subprocess, sys
import numpy as np

SR = 48000
TAIL = 4.0   # trailing silence, as the unpaused vo.wav had
QUIET_DB = -35.0
GAP = 0.015   # half-width of the stretch that must stay quiet around a cut

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().replace("'", "").replace("’", "")
                  .translate(str.maketrans("", "", "\".,?!;:—-"))).strip()

def decode(p: pathlib.Path) -> np.ndarray:
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(SR),
                        "-f", "f32le", "-"], capture_output=True)
    if r.returncode != 0: sys.exit(f"ffmpeg could not decode {p}")
    return np.frombuffer(r.stdout, dtype=np.float32).copy()

def find_end(words: list[dict], phrase: str) -> int:
    toks, idx = [], []
    for i, w in enumerate(words):
        for t in norm(w["text"]).split(): toks.append(t); idx.append(i)
    n = norm(phrase).split()
    hits = [i for i in range(len(toks) - len(n) + 1) if toks[i:i + len(n)] == n]
    if len(hits) != 1: sys.exit(f"pause after {phrase!r} matched {len(hits)} times; it must match once")
    return idx[hits[0] + len(n) - 1]

def level_db(audio: np.ndarray, at: int, ref: float) -> float:
    half, step = int(GAP * SR), 240
    lv = [float(np.sqrt(np.mean(audio[s:s + 480] ** 2))) for s in range(max(0, at - half), at + half - 480 + 1, step)]
    return 20 * np.log10(max(lv) / ref + 1e-9)

def quietest(audio: np.ndarray, t0: float, t1: float, ref: float) -> int:
    """The point in [t0, t1] whose surrounding stretch is quietest, by the same
    measure the refusal uses."""
    a, b = int(t0 * SR), max(int(t0 * SR) + 1, int(t1 * SR))
    cands = range(a, b + 1, 240)
    return min(cands, key=lambda s: level_db(audio, s, ref))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio"); ap.add_argument("words"); ap.add_argument("pauses")
    ap.add_argument("--tail", type=float, default=TAIL, help="trailing silence for credits and end graphics")
    ap.add_argument("--append", nargs=2, action="append", default=[], metavar=("AUDIO", "WORDS"),
                    help="a later pickup line (same voice) to join after the take, before pauses are opened")
    ap.add_argument("--join", type=float, default=0.3, help="silence between the take and each pickup")
    ap.add_argument("--out-wav", required=True); ap.add_argument("--out-words", required=True)
    a = ap.parse_args()
    load = lambda p: [w for w in json.loads(pathlib.Path(p).read_text()) if w.get("type", "word") == "word"]
    audio = decode(pathlib.Path(a.audio))
    words = load(a.words)
    main_ref = float(np.sqrt(np.mean(audio ** 2)))
    for pa, pw in a.append:
        pick = decode(pathlib.Path(pa))
        # Match loudness to the take, so the pickup does not jump out.
        pick *= main_ref / float(np.sqrt(np.mean(pick ** 2)))
        off = len(audio) / SR + a.join
        audio = np.concatenate([audio, np.zeros(int(a.join * SR), np.float32), pick])
        more = load(pw)
        if not more: sys.exit(f"{pw} has no words")
        words += [{**w, "start": round(w["start"] + off, 3), "end": round(w["end"] + off, 3)} for w in more]
        print(f"  appended {pathlib.Path(pa).name} at {off:.2f}s ({len(more)} words)")
    spec = json.loads(pathlib.Path(a.pauses).read_text())
    ref = main_ref
    if not spec: sys.exit("no pauses given; nothing to do is not a result")

    cuts = []
    for p in spec:
        i = find_end(words, p["after"])
        if i + 1 >= len(words): sys.exit(f"pause after {p['after']!r} falls after the last word")
        lo = max(words[i]["start"] + 0.05, words[i]["end"] - 0.3)
        hi = min(words[i + 1]["end"] - 0.05, words[i + 1]["start"] + 0.1)
        at = quietest(audio, lo, hi, ref)
        db = level_db(audio, at, ref)
        if db > QUIET_DB:
            sys.exit(f"pause after {p['after']!r}: the quietest point near it is {db:.0f} dB, "
                     f"inside speech; refusing to cut a sound in two")
        cuts.append((at, float(p["seconds"]), i, p["after"]))
    cuts.sort()
    if len({c[0] for c in cuts}) != len(cuts): sys.exit("two pauses fall in the same gap")

    fade = int(0.005 * SR)
    parts, prev = [], 0
    for s, sec, _, _ in cuts:
        seg = audio[prev:s].copy()
        if prev: seg[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)
        seg[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
        parts += [seg, np.zeros(int(round(sec * SR)), np.float32)]
        prev = s
    last = audio[prev:].copy(); last[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)
    parts += [last, np.zeros(int(a.tail * SR), np.float32)]
    out = np.concatenate(parts)

    shifted = []
    for w in words:
        d = sum(round(sec * SR) / SR for s, sec, _, _ in cuts if w["start"] >= s / SR)
        shifted.append({**w, "start": round(w["start"] + d, 3), "end": round(w["end"] + d, 3)})

    # Floor: the output must be exactly the input plus every pause plus the tail,
    # and no word may have moved by anything but whole pauses.
    added = sum(round(sec * SR) for _, sec, _, _ in cuts)
    if len(out) != len(audio) + added + int(a.tail * SR):
        sys.exit("output length is not input + pauses + tail; refusing to write")
    total = round(added / SR, 3)
    if abs((shifted[-1]["start"] - words[-1]["start"]) - total) > 1e-3:
        sys.exit("the last word did not move by the sum of the pauses; refusing to write")

    pcm = (np.clip(out, -1, 1) * 32767).astype("<i2").tobytes()
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1",
                        "-i", "-", a.out_wav], input=pcm)
    if r.returncode != 0: sys.exit("ffmpeg could not write the wav")
    pathlib.Path(a.out_words).write_text(json.dumps(shifted, indent=1, ensure_ascii=False) + "\n")
    for s, sec, i, ph in cuts:
        print(f"  +{sec:.2f}s at {s / SR:7.2f}s ({level_db(audio, s, ref):.0f} dB) after {ph!r}")
    print(f"{len(cuts)} pauses, +{total:.2f}s; {len(audio) / SR:.2f}s -> {len(out) / SR:.2f}s")
    return 0

if __name__ == "__main__":
    sys.exit(main())
