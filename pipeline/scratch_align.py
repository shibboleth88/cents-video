#!/usr/bin/env python3
"""Scratch voiceover WITH timings, without transcribing anything.

Transcribing synthetic speech is both unnecessary and unreliable: we wrote the
words and we generated the audio, yet whisper-large-v3-turbo degenerated into
"s. a wild . a t. a wild." on this exact track, because TTS audio is outside
what it was trained on.

So synthesise one sentence at a time and MEASURE each clip. Sentence boundaries
are then exact. Word positions inside a sentence are interpolated by character
length and marked as such — they are good enough for anchoring a shot to a
sentence, which is what the timeline actually does.

  pipeline/scratch_align.py script/voiceover.txt public/vo.wav
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VOICE, RATE = "Daniel", 170
GAP, TAIL = 0.20, 4.0

def dur(p: pathlib.Path) -> float:
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def main() -> int:
    script = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "script/voiceover.txt")
    out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "public/vo.wav")
    body = "\n".join(l for l in script.read_text().splitlines() if l.strip())
    sents = [s.strip() for s in re.split(r"(?<=[.?!])\s+", body) if s.strip()]
    if len(sents) < 3: sys.exit(f"only {len(sents)} sentences — the script looks empty")

    tmp = pathlib.Path("/tmp/scratch_sents"); tmp.mkdir(exist_ok=True)
    for f in tmp.glob("*"): f.unlink()

    words, parts, t = [], [], 0.0
    for i, s in enumerate(sents):
        aiff, wav = tmp/f"{i:03}.aiff", tmp/f"{i:03}.wav"
        subprocess.run(["say","-v",VOICE,"-r",str(RATE),"-o",str(aiff),s], check=True)
        subprocess.run(["ffmpeg","-v","error","-y","-i",str(aiff),"-ar","48000","-ac","1",
                        "-c:a","pcm_s16le",str(wav)], check=True)
        d = dur(wav)
        if d <= 0.05: sys.exit(f"sentence {i} synthesised to {d}s — synthesis failed")
        parts.append(wav)

        # Distribute inside the measured sentence by character length.
        toks = s.split()
        total = sum(len(w) for w in toks) or 1
        cur = t
        for w in toks:
            share = len(w) / total * d
            words.append({"word": w, "start": round(cur, 3), "end": round(cur + share * 0.92, 3)})
            cur += share
        t += d + GAP

    # Concatenate with the same gaps the timings assume, then pad for credits.
    lst = tmp/"list.txt"
    sil = tmp/"gap.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","anullsrc=r=48000:cl=mono",
                    "-t",str(GAP),"-c:a","pcm_s16le",str(sil)], check=True)
    lines = []
    for p in parts: lines += [f"file '{p}'", f"file '{sil}'"]
    lst.write_text("\n".join(lines))
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",str(lst),
                    "-af",f"apad=pad_dur={TAIL}","-ar","48000","-ac","1","-c:a","pcm_s16le",str(out)],
                   check=True)

    total_dur = dur(out)
    # FLOOR: the measured file must match what the timings assume, or every
    # anchor downstream is placed against audio that is not there.
    drift = abs(total_dur - (t + TAIL))
    if drift > 0.25:
        sys.exit(f"assembled audio is {total_dur:.2f}s but timings assume {t + TAIL:.2f}s (drift {drift:.2f}s)")
    if words[-1]["end"] > total_dur:
        sys.exit("last word ends after the audio does")

    sys.path.insert(0, str(ROOT/"pipeline")); import cues as C
    noise = C.audit_transcript(words)
    if noise: sys.exit("malformed tokens in the script: " + "; ".join(noise[:3]))
    cs = C.build(words)
    problems = C.audit(cs)
    if problems: sys.exit("caption chunking failed:\n  " + "\n  ".join(problems))

    (ROOT/"script"/"alignment.json").write_text(json.dumps({
        "scratch": True,
        "_warning": "SCRATCH. Synthetic voice. Sentence boundaries are measured; "
                    "word positions inside a sentence are interpolated by character length.",
        "words": words, "duration": round(total_dur, 3),
        "source_audio": str(out), "model": "macos-say+measured",
        "narration_ends": round(words[-1]["end"], 3), "tail_silence": TAIL,
    }, indent=1))
    (ROOT/"captions"/"cues.json").write_text(json.dumps(cs, indent=1))
    print(f"{len(sents)} sentences, {len(words)} words, {total_dur:.2f}s "
          f"(voice ends {words[-1]['end']:.2f}s, {TAIL}s tail), {len(cs)} cues")
    return 0

if __name__ == "__main__":
    sys.exit(main())
