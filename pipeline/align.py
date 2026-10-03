#!/usr/bin/env python3
"""Voiceover -> word-level alignment -> caption cues -> SRT.

This file is the pipeline's clock. Everything downstream — shot boundaries,
total duration, caption timing — is derived from what was actually said, so
re-recording the voiceover re-cuts the film without anyone re-timing anything.

  python3 pipeline/align.py public/vo.wav
  python3 pipeline/align.py public/vo.wav --script script/voiceover.txt

Passing --script supplies correct spellings (Cents vs cents, UTXO, Schrodinger,
the Block number) as an initial prompt. It never replaces the recorded wording:
adlibs and on-the-fly revisions must survive into the captions.
"""
from __future__ import annotations
import argparse, json, pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import cues as C

ROOT = pathlib.Path(__file__).resolve().parent.parent

def audio_duration(p: pathlib.Path) -> float:
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","csv=p=0",str(p)], capture_output=True, text=True)
    if r.returncode != 0: sys.exit(f"ffprobe failed on {p}")
    return float(r.stdout.strip())

def transcribe(p: pathlib.Path, prompt: str | None, model: str) -> list[dict]:
    try:
        import mlx_whisper
    except ImportError:
        sys.exit("mlx-whisper is not installed.  pip3 install mlx-whisper")
    res = mlx_whisper.transcribe(
        str(p), word_timestamps=True,
        path_or_hf_repo=model,
        initial_prompt=prompt)
    words = [w for seg in res["segments"] for w in seg.get("words", [])]
    return [{"word": w["word"].strip(), "start": round(w["start"],3), "end": round(w["end"],3)}
            for w in words if w["word"].strip()]

def srt(cues: list[dict]) -> str:
    def ts(t: float) -> str:
        h, r = divmod(t, 3600); m, s = divmod(r, 60)
        return f"{int(h):02}:{int(m):02}:{int(s):02},{int((s%1)*1000):03}"
    return "\n".join(f"{i+1}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n"
                     for i, c in enumerate(cues))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio"); ap.add_argument("--script")
    ap.add_argument("--model", default="mlx-community/whisper-large-v3-turbo",
                    help="use whisper-small-mlx for fast scratch passes")
    a = ap.parse_args()
    p = pathlib.Path(a.audio)
    if not p.exists(): sys.exit(f"{p} does not exist")
    dur = audio_duration(p)
    prompt = pathlib.Path(a.script).read_text()[:900] if a.script else None
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

    words = transcribe(p, prompt, a.model)

    # FLOORS. An aligner that returns nothing, or times that do not span the
    # recording, must read as RED — not as a short film.
    if len(words) < 20:
        sys.exit(f"alignment produced only {len(words)} words from {dur:.1f}s of audio — "
                 f"the transcription failed; refusing to write a timing file")
    # Whisper routinely emits zero-length words inside a fast phrase. That is
    # benign and repairable. What is NOT repairable is starts going backwards,
    # which would make the timeline incoherent — so the fatal check belongs
    # there, not on duration.
    if any(b["start"] < a["start"] - 1e-6 for a, b in zip(words, words[1:])):
        sys.exit("word start times go backwards — alignment is unusable")
    zero = [w for w in words if w["end"] <= w["start"]]
    if len(zero) > 0.4 * len(words):
        sys.exit(f"{len(zero)}/{len(words)} words have zero duration — the aligner degenerated")
    for i, w in enumerate(words):
        if w["end"] <= w["start"]:
            nxt = words[i + 1]["start"] if i + 1 < len(words) else w["start"] + 0.08
            w["end"] = round(min(max(w["start"] + 0.04, w["start"]), max(nxt, w["start"] + 0.02)), 3)
    if zero: print(f"repaired {len(zero)} zero-length word timing(s)")
    covered = words[-1]["end"] - words[0]["start"]
    if covered < 0.6 * dur:
        sys.exit(f"alignment covers {covered:.1f}s of a {dur:.1f}s recording — "
                 f"the tail was probably dropped; refusing to write a timing file")

    # Reconcile against the written script: script spelling, audio timing,
    # spoken words preserved wherever the speaker departed from the page.
    # Replaces a hand-keyed correction list, which could not survive a
    # non-deterministic recogniser.
    divergences = []
    if a.script:
        import reconcile as R
        words, divergences = R.reconcile(words, pathlib.Path(a.script).read_text())
        rec = [d for d in divergences if d["kind"] == "recognition"]
        spk = [d for d in divergences if d["kind"] == "spoken_differs"]
        print(f"reconciled: {len(rec)} recognition fixes, {len(spk)} place(s) where "
              f"the recording departs from the script")
        for d in spk:
            print(f"  ADLIB @{d['at']}s  said {d['heard']!r}  script had {d['script']!r}")

    noise = C.audit_transcript(words)
    if noise:
        sys.exit("transcription produced malformed tokens — fix these in the transcript "
                 "before rendering, do not let them reach the screen:\n  " + "\n  ".join(noise))

    cues = C.build(words)
    problems = C.audit(cues)
    if problems:
        sys.exit("caption chunking produced unusable cues:\n  " + "\n  ".join(problems))
    (ROOT/"script"/"alignment.json").write_text(
        json.dumps({"words": words, "duration": round(dur,3),
                    "source_audio": str(p), "model": a.model, "divergences": divergences}, indent=1))
    (ROOT/"captions").mkdir(exist_ok=True)
    (ROOT/"captions"/"cues.json").write_text(json.dumps(cues, indent=1))
    (ROOT/"captions"/"captions.srt").write_text(srt(cues))
    print(f"{len(words)} words, {dur:.2f}s, {len(cues)} cues")
    print("REVIEW captions/cues.json before rendering: check Cents vs cents, names, "
          "technical terms, and any adlib the model may have normalised away.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
