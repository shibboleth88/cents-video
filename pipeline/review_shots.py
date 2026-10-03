#!/usr/bin/env python3
"""Prepare a shot-by-shot visual review, and gate on the verdicts.

Numeric gates establish that a file is well formed. They cannot see that an
image does not match what is being said over it, that a composition is crowded,
that the same picture has come back for the third time, or that a diagram state
conveys motion rather than a concept. Those need looking at.

This script extracts representative frames per shot and pairs each with THE
WORDS SPOKEN OVER IT, so correspondence can actually be judged. Claude fills in
a verdict per shot; verify.py refuses to release while any shot is unreviewed,
stale, or marked 'revise'.

  python3 pipeline/review_shots.py prepare    # frames + review template
  python3 pipeline/review_shots.py check      # gate the verdicts
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "review" / "shots"
REVIEW = ROOT / "review" / "shot_review.json"
FPS = 30

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from anchors import load, shot_times

def prepare() -> int:
    tl, al = load()
    shots = shot_times(tl, al)
    src = ROOT/"exports"/"captioned.mp4"
    if not src.exists(): sys.exit("exports/captioned.mp4 does not exist — render first")
    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob("*.png"): f.unlink()

    entries = []
    for s in shots:
        dur = s["t1"] - s["t0"]
        # Short shots get 2 frames, longer ones 3: enough to see a change, few
        # enough to actually look at every one.
        offs = [0.25, 0.75] if dur < 3 else [0.15, 0.5, 0.85]
        frames = []
        for k, o in enumerate(offs):
            p = OUT/f"{s['shot_id']}_{k}.png"
            subprocess.run(["ffmpeg","-v","error","-y","-ss",str(s["t0"]+dur*o),"-i",str(src),
                            "-vframes","1","-vf","scale=405:720",str(p)], check=True)
            frames.append(str(p.relative_to(ROOT)))
        entries.append({
            "shot_id": s["shot_id"], "t0": s["t0"], "t1": s["t1"],
            "purpose": s["purpose"], "visual_kind": s["visual_kind"],
            "asset_id": s.get("asset_id"),
            "narration": s["narration"],
            "frames": frames,
            # Filled in by looking. Nothing may be released while any is null.
            "verdict": None,          # "ok" | "revise"
            "matches_narration": None,# does what is shown belong to what is said
            "notes": None,
        })
    # FLOOR: a review covering no shots must not read as a clean review.
    if len(entries) < len(tl["shots"]):
        sys.exit(f"prepared {len(entries)} reviews for {len(tl['shots'])} shots")
    n_png = len(list(OUT.glob("*.png")))
    if n_png < len(entries) * 2:
        sys.exit(f"only {n_png} frames extracted for {len(entries)} shots — extraction failed")
    REVIEW.write_text(json.dumps({"render": "exports/captioned.mp4",
                                  "render_mtime": src.stat().st_mtime,
                                  "shots": entries}, indent=1))
    print(f"{len(entries)} shots, {n_png} frames -> {REVIEW.relative_to(ROOT)}")
    for e in entries:
        print(f"  {e['shot_id']:<18} {e['t0']:5.1f}-{e['t1']:5.1f}  {e['narration'][:58]!r}")
    return 0

def check() -> int:
    if not REVIEW.exists(): sys.exit("no shot_review.json — run 'prepare' and look at the frames")
    r = json.loads(REVIEW.read_text())
    src = ROOT/"exports"/"captioned.mp4"
    tl = json.loads((ROOT/"timeline"/"timeline.json").read_text())
    problems = []
    if not r["shots"]: problems.append("review contains no shots")
    if len(r["shots"]) != len(tl["shots"]):
        problems.append(f"review covers {len(r['shots'])} of {len(tl['shots'])} shots")
    if src.exists() and src.stat().st_mtime > r.get("render_mtime", 0) + 1:
        problems.append("the render changed after this review — the verdicts describe an older film")
    for s in r["shots"]:
        if s["verdict"] is None: problems.append(f"{s['shot_id']}: unreviewed")
        elif s["verdict"] == "revise": problems.append(f"{s['shot_id']}: marked revise — {s.get('notes')}")
        if s["matches_narration"] is False:
            problems.append(f"{s['shot_id']}: shown image does not match what is said over it")
    for p in problems: print(f"  \033[31mFAIL\033[0m {p}")
    if not problems: print(f"  \033[32mPASS\033[0m all {len(r['shots'])} shots reviewed and accepted")
    return 1 if problems else 0

def merge(path: str) -> int:
    """Fold verdicts collected on the review Artifact back into shot_review.json.

    Dump them with the ArtifactData tool (action "list", collection "verdicts")
    into a JSON file of {shot_id: {verdict, notes}} and pass it here, so the
    user's judgement reaches the release gate rather than only Claude's."""
    r = json.loads(REVIEW.read_text())
    incoming = json.loads(pathlib.Path(path).read_text())
    if not incoming: sys.exit("no verdicts in that file — nothing to merge")
    n = 0
    for s in r["shots"]:
        v = incoming.get(s["shot_id"])
        if not v: continue
        s["verdict"], s["notes"] = v.get("verdict"), v.get("notes")
        s["verdict_by"] = "user"; n += 1
    if n == 0: sys.exit("none of the verdicts matched a shot id — wrong file?")
    REVIEW.write_text(json.dumps(r, indent=1))
    print(f"merged {n} user verdict(s)")
    return 0

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "prepare"
    if cmd == "merge": sys.exit(merge(sys.argv[2]))
    sys.exit(prepare() if cmd == "prepare" else check())
