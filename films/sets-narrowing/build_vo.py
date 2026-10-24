#!/usr/bin/env python3
"""Film B voiceover: chosen take -> paced master -> alignment, cues, SRT.

The voice is the user's ElevenLabs clone "eo" (take record in
audio/takes/takes.json). ElevenLabs returned word timings with the take, so
pipeline/align.py (mlx-whisper, Mac only) is not needed here; this script does
the rest of align.py's job with the same modules and the same floors.

The synthesis prompt spelled the numbers out ("five hundred ninety-eight") so
they would be read reliably. The captions use the script's numerals, through
script/corrections.json, and the result must equal script/voiceover.txt word
for word or nothing is written.

Pauses are added only at measured silences between sentences, never inside a
word, and every inserted gap is listed in takes.json so the edit is reviewable.

  python3 films/sets-narrowing/build_vo.py
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

FILM = pathlib.Path(__file__).resolve().parent
ROOT = FILM.parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
import cues as C  # noqa: E402
from align import srt  # noqa: E402

SR = 48000


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def apply_corrections(words: list[dict], doc: dict) -> list[dict]:
    """Same contract as align.apply_corrections: each must match exactly once."""
    out = list(words)
    for c in doc["corrections"]:
        want = [norm(t) for t in re.split(r"[\s-]+", c["heard"]) if norm(t)]
        said = c["say"].split()
        toks: list[tuple[str, int]] = []
        for i, w in enumerate(out):
            for t in re.split(r"[\s-]+", w["word"]):
                if norm(t): toks.append((norm(t), i))
        flat = [t for t, _ in toks]
        hits = [k for k in range(len(flat) - len(want) + 1) if flat[k:k + len(want)] == want]
        if len(hits) != 1:
            sys.exit(f"correction {c['heard']!r} matched {len(hits)} times, expected exactly 1")
        i, j = toks[hits[0]][1], toks[hits[0] + len(want) - 1][1] + 1
        t0, t1 = out[i]["start"], out[j - 1]["end"]
        m = re.search(r"[^\w']+$", out[j - 1]["word"])
        tail = m.group(0) if m else ""
        if tail and not re.search(r"[^\w']$", said[-1]):
            said = said[:-1] + [said[-1] + tail]
        step = (t1 - t0) / len(said)
        out = out[:i] + [{"word": w, "start": round(t0 + k * step, 3), "end": round(t0 + (k + 1) * step, 3)}
                         for k, w in enumerate(said)] + out[j:]
    return out


def main() -> int:
    takes = json.loads((FILM / "audio/takes/takes.json").read_text())
    take = takes["takes"][takes["chosen"]]
    src = FILM / "audio/takes" / take["file"]
    words = [{"word": w["text"], "start": w["start"], "end": w["end"]}
             for w in json.loads((FILM / "audio/takes" / take["words"]).read_text())["words"]
             if w.get("type", "word") == "word"]
    if len(words) < 50:
        sys.exit(f"FLOOR: only {len(words)} timed words in the take; refusing")

    # Inserted pauses. Each sits in the measured gap between two words; the cut
    # point is the middle of that gap, so no syllable is touched.
    cuts = []
    for p in takes["pauses"]:
        idx = [k for k in range(len(words) - 1)
               if norm(words[k]["word"]) == norm(p["after_word"]) and norm(words[k + 1]["word"]) == norm(p["before_word"])]
        if len(idx) != 1:
            sys.exit(f"pause {p['after_word']!r}|{p['before_word']!r} matched {len(idx)} places, expected 1")
        k = idx[0]
        gap = words[k + 1]["start"] - words[k]["end"]
        if gap < 0.15:
            sys.exit(f"pause after {p['after_word']!r}: only {gap:.3f}s of silence to cut in; refusing to split speech")
        cuts.append((round((words[k]["end"] + words[k + 1]["start"]) / 2, 3), p["add"], k))
    cuts.sort()

    # Build the master with ffmpeg: segments of the take with silence between.
    edges = [0.0] + [c[0] for c in cuts] + [None]
    parts, filters = [], []
    for n in range(len(edges) - 1):
        a, b = edges[n], edges[n + 1]
        trim = f"atrim=start={a}" + (f":end={b}" if b is not None else "")
        filters.append(f"[0:a]{trim},asetpts=PTS-STARTPTS,aresample={SR}[s{n}]")
        parts.append(f"[s{n}]")
        if n < len(cuts):
            filters.append(f"anullsrc=r={SR}:cl=mono,atrim=duration={cuts[n][1]}[z{n}]")
            parts.append(f"[z{n}]")
    tail = takes["tail_seconds"]
    filters.append(f"{''.join(parts)}concat=n={len(parts)}:v=0:a=1,aformat=channel_layouts=mono,apad=pad_dur={tail}[out]")
    out = FILM / "audio/vo.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter_complex", ";".join(filters),
                    "-map", "[out]", "-ar", str(SR), "-c:a", "pcm_s16le", str(out)], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                               capture_output=True, text=True, check=True).stdout)

    # Shift word timings by the silence inserted before them.
    for w_i, w in enumerate(words):
        shift = sum(add for _, add, k in cuts if w_i > k)
        w["start"] = round(w["start"] + shift, 3); w["end"] = round(w["end"] + shift, 3)

    words = apply_corrections(words, json.loads((FILM / "script/corrections.json").read_text()))

    script = (FILM / "script/voiceover.txt").read_text().split()
    said = [w["word"] for w in words]
    if [norm(x) for x in said] != [norm(x) for x in script]:
        import difflib
        d = "\n".join(difflib.unified_diff(script, said, "script", "recording", lineterm="", n=1))
        sys.exit(f"the corrected recording does not match script/voiceover.txt:\n{d}")
    # Script spelling and punctuation on screen, audio timing underneath.
    for w, s in zip(words, script):
        w["word"] = s

    noise = C.audit_transcript(words)
    if noise: sys.exit("malformed tokens:\n  " + "\n  ".join(noise))
    cues = C.build(words)
    bad = C.audit(cues)
    if bad: sys.exit("caption chunking produced unusable cues:\n  " + "\n  ".join(bad))
    if words[-1]["end"] > dur - tail + 0.05:
        sys.exit("FLOOR: last word ends inside the credits tail; timings did not shift with the audio")

    (FILM / "script/alignment.json").write_text(json.dumps(
        {"words": words, "duration": round(dur, 3), "source_audio": f"films/sets-narrowing/audio/vo.wav",
         "model": f"ElevenLabs {take['model']} voice {take['voice']} ({take['voice_id']}), timings from ElevenLabs",
         "divergences": []}, indent=1))
    (FILM / "captions/cues.json").write_text(json.dumps(cues, indent=1))
    (FILM / "captions/captions.srt").write_text(srt(cues))
    added = sum(c[1] for c in cuts)
    print(f"take {takes['chosen']}: {take['duration']:.2f}s + {added:.2f}s pauses + {tail:.2f}s tail = {dur:.2f}s master")
    print(f"{len(words)} words match the script; {len(cues)} cues")
    return 0


if __name__ == "__main__":
    sys.exit(main())
