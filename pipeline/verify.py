#!/usr/bin/env python3
"""Release gates for a CENTS essay video.

Every gate is a measurement on the ENCODED deliverable, not on an intermediate
and not on the renderer's own opinion of itself. Run with --self-test to build
deliberately broken videos and confirm each gate goes RED; a gate that has never
been red is not evidence.

  python3 pipeline/verify.py                 # gate the real exports
  python3 pipeline/verify.py --self-test     # prove the gates can fail
"""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
CANVAS, FPS = (1080, 1920), 30
ESSENTIAL = {"x0": 80, "y0": 270, "x1": 860, "y1": 1510}
LUMA_PRESENT = 40      # above this, something is drawn
LUMA_TEXT = 140        # light text sits near 0xf4
MIN_TEXT_FRAMES = 1

class Fail(Exception): pass

def sh(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True)

def probe(p: pathlib.Path) -> dict:
    r = sh(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(p)])
    if r.returncode != 0: raise Fail(f"ffprobe failed: {r.stderr.strip()[:200]}")
    return json.loads(r.stdout)

def ymax_series(p: pathlib.Path, crop: str | None, start: float | None = None) -> list[float]:
    """Per-frame peak luma, optionally within a crop. The primitive the pixel
    gates are built from."""
    vf = (f"crop={crop}," if crop else "") + \
         "signalstats,metadata=print:key=lavfi.signalstats.YMAX:file=-"
    args = ["ffmpeg","-v","error"]
    if start is not None: args += ["-ss", f"{start}"]
    args += ["-i",str(p),"-vf",vf,"-an","-f","null","-"]
    r = sh(args)
    vals = [float(m) for m in re.findall(r"YMAX=(\d+(?:\.\d+)?)", r.stdout)]
    if r.returncode != 0: raise Fail(f"ffmpeg scan failed: {r.stderr.strip()[:200]}")
    # FLOOR: a scan that returned nothing is a broken instrument, not a clean result.
    if not vals: raise Fail("luma scan produced no frames — the measurement failed, so neither pass nor fail can be claimed")
    return vals

# ---------------------------------------------------------------- gates

def g_decodes(p: pathlib.Path) -> str:
    r = sh(["ffmpeg","-v","error","-i",str(p),"-map","0:v:0","-f","null","-"])
    if r.returncode != 0 or r.stderr.strip():
        raise Fail(f"video does not decode cleanly: {r.stderr.strip()[:200]}")
    return "decodes end to end with no errors"

def g_format(p: pathlib.Path, expect_audio: bool = True) -> str:
    d = probe(p)
    v = next((s for s in d["streams"] if s["codec_type"]=="video"), None)
    if not v: raise Fail("no video stream")
    if (v["width"], v["height"]) != CANVAS:
        raise Fail(f"dimensions {v['width']}x{v['height']}, expected {CANVAS[0]}x{CANVAS[1]}")
    num, den = (int(x) for x in v["r_frame_rate"].split("/"))
    if round(num/den) != FPS: raise Fail(f"fps {num/den}, expected {FPS}")
    nb = int(v.get("nb_frames") or 0)
    dur = float(d["format"]["duration"])
    if nb < 1: raise Fail("frame count is 0 or absent — nothing to verify")
    if abs(nb - round(dur*FPS)) > 2:
        raise Fail(f"frame count {nb} disagrees with duration {dur:.3f}s at {FPS}fps ({round(dur*FPS)})")
    a = next((s for s in d["streams"] if s["codec_type"]=="audio"), None)
    if expect_audio:
        if not a: raise Fail("no audio stream")
        if abs(float(a.get("duration") or 0) - dur) > 0.25:
            raise Fail(f"audio {a.get('duration')}s vs video {dur:.3f}s — streams disagree")
    return f"{v['width']}x{v['height']} @{FPS}fps, {nb} frames, {dur:.2f}s" + (", audio present" if a else "")

def g_black_tail(p: pathlib.Path) -> str:
    """The 3:08 bug: a clean encoder exit says nothing about the tail."""
    dur = float(probe(p)["format"]["duration"])
    vals = ymax_series(p, None, start=max(0.0, dur-0.5))
    if max(vals) < LUMA_PRESENT:
        raise Fail(f"last {len(vals)} frames are black (peak luma {max(vals):.0f} < {LUMA_PRESENT})")
    return f"tail is not black (peak luma {max(vals):.0f} over last {len(vals)} frames)"

def g_frozen_tail(p: pathlib.Path) -> str:
    dur = float(probe(p)["format"]["duration"])
    r = sh(["ffmpeg","-v","error","-ss",f"{max(0.0,dur-2.0)}","-i",str(p),
            "-vf","tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YMAX:file=-",
            "-an","-f","null","-"])
    vals = [float(m) for m in re.findall(r"YMAX=(\d+(?:\.\d+)?)", r.stdout)]
    if not vals: raise Fail("frozen-tail scan produced no frames — instrument failed")
    if max(vals) < 3:
        raise Fail(f"last 2s appear frozen (max inter-frame difference {max(vals):.0f})")
    return f"tail is moving (max inter-frame difference {max(vals):.0f})"

def g_safe_area(p: pathlib.Path) -> str:
    """Pixel-level, measured on the ESSENTIAL export (text on black) so the
    check is independent of the component that claims to lay text out."""
    E = ESSENTIAL
    inside = f"{E['x1']-E['x0']}:{E['y1']-E['y0']}:{E['x0']}:{E['y0']}"
    bands = {
        "top":    f"{CANVAS[0]}:{E['y0']}:0:0",
        "bottom": f"{CANVAS[0]}:{CANVAS[1]-E['y1']}:0:{E['y1']}",
        "left":   f"{E['x0']}:{E['y1']-E['y0']}:0:{E['y0']}",
        "right":  f"{CANVAS[0]-E['x1']}:{E['y1']-E['y0']}:{E['x1']}:{E['y0']}",
    }
    # FLOOR FIRST: if no text was rendered inside the box, "no violations
    # outside" is vacuous. Establish the instrument sees text before trusting 0.
    ins = ymax_series(p, inside)
    lit = sum(1 for v in ins if v >= LUMA_TEXT)
    if lit < MIN_TEXT_FRAMES:
        raise Fail(f"no text found inside the safe box ({lit} frames above luma {LUMA_TEXT}) — "
                   f"a clean result outside the box would be meaningless")
    bad = []
    for name, crop in bands.items():
        m = max(ymax_series(p, crop))
        if m >= LUMA_PRESENT: bad.append(f"{name} band peak luma {m:.0f}")
    if bad: raise Fail("essential content outside the safe box: " + "; ".join(bad))
    return f"text present in {lit}/{len(ins)} frames, all bands clear"

def g_loudness(p: pathlib.Path, target=-16.0, tol=1.0, peak_ceiling=-1.0) -> str:
    r = sh(["ffmpeg","-v","info","-i",str(p),"-af","loudnorm=print_format=json","-f","null","-"])
    m = re.search(r"\{[^{}]*input_i[^{}]*\}", r.stderr, re.S)
    if not m: raise Fail("could not measure loudness")
    d = json.loads(m.group(0))
    i, tp = float(d["input_i"]), float(d["input_tp"])
    if i == float("-inf") or i < -70: raise Fail(f"audio is effectively silent (integrated {i} LUFS)")
    if abs(i-target) > tol: raise Fail(f"integrated loudness {i} LUFS, target {target}±{tol}")
    if tp > peak_ceiling: raise Fail(f"true peak {tp} dBTP exceeds {peak_ceiling}")
    return f"{i} LUFS, {tp} dBTP"

def audio_hash(p: pathlib.Path) -> str:
    r = sh(["ffmpeg","-v","error","-i",str(p),"-map","0:a:0","-c","copy","-f","hash","-hash","sha256","-"])
    if r.returncode != 0: raise Fail("could not demux audio")
    return r.stdout.strip()

def g_parity(clean: pathlib.Path, cap: pathlib.Path) -> str:
    """Captioned and clean must differ ONLY by the caption layer. Compare
    demuxed AUDIO STREAMS, never whole-container hashes."""
    if audio_hash(clean) != audio_hash(cap):
        raise Fail("clean and captioned audio streams differ")
    dc, dp = (float(probe(x)["format"]["duration"]) for x in (clean, cap))
    if abs(dc-dp) > 0.04: raise Fail(f"durations differ: clean {dc:.3f}s vs captioned {dp:.3f}s")
    return f"audio streams identical, durations match ({dc:.2f}s)"

def g_visual_mix(cap_frac=0.45) -> str:
    """Stock + generated imagery may not take over the film."""
    tl = json.loads((ROOT/"timeline"/"timeline.json").read_text())
    al = json.loads((ROOT/"script"/"alignment.json").read_text())
    shots = tl["shots"]
    if not shots: raise Fail("timeline has no shots")
    if any("purpose" not in s or not s["purpose"].strip() for s in shots):
        raise Fail("a shot has no stated purpose — a shot that cannot say why it exists is decoration")
    kinds = {}
    for s in shots: kinds[s["visual_kind"]] = kinds.get(s["visual_kind"], 0) + 1
    filler = kinds.get("stock",0) + kinds.get("generated",0)
    frac = filler/len(shots)
    if frac > cap_frac:
        raise Fail(f"{frac:.0%} of shots are stock/generated, cap is {cap_frac:.0%}")
    return f"{len(shots)} shots, mix {kinds}, filler {frac:.0%}"

def g_not_stale(outs: list[pathlib.Path]) -> str:
    """A gate that reads a stale export measures the previous film. Caught in
    development when a failed render left an old essential.mp4 in place and the
    safe-area gate happily re-reported its result."""
    srcs = [q for d in ("src","timeline","script","captions") for q in (ROOT/d).rglob("*")
            if q.is_file() and q.suffix in {".ts",".tsx",".json"}]
    if not srcs: raise Fail("no source files found — staleness cannot be established")
    newest = max(srcs, key=lambda q: q.stat().st_mtime)
    for o in outs:
        if not o.exists(): raise Fail(f"{o.name} does not exist")
        if o.stat().st_mtime < newest.stat().st_mtime:
            raise Fail(f"{o.name} is older than {newest.relative_to(ROOT)} — re-render before gating")
    return f"all {len(outs)} exports are newer than {newest.relative_to(ROOT)}"

def g_captions() -> str:
    """Well-formed is not the same as readable. Numeric gates passed a render
    whose captions were single-word orphans held for 0.37s."""
    sys.path.insert(0, str(ROOT/"pipeline")); import cues as C
    cs = json.loads((ROOT/"captions"/"cues.json").read_text())
    if len(cs) < 3: raise Fail(f"only {len(cs)} caption cues — the caption file is empty or truncated")
    al = json.loads((ROOT/"script"/"alignment.json").read_text())
    noise = C.audit_transcript(al["words"])
    if noise: raise Fail(f"{len(noise)} malformed transcript token(s) reaching the screen: " + "; ".join(noise[:3]))
    bad = C.audit(cs)
    if bad: raise Fail(f"{len(bad)} caption problems: " + "; ".join(bad[:3]))
    return f"{len(cs)} cues, none orphaned, too brief, too long or overlapping"

TEXT_PROPS = ("title", "subtitle", "quote", "attribution", "caption", "author")

def onscreen_strings(shot: dict) -> list[str]:
    pr = shot.get("props") or {}
    out = [str(pr[k]) for k in TEXT_PROPS if pr.get(k)]
    out += [str(x) for x in (pr.get("lines") or [])]
    return out

def g_caption_redundancy(thresh=0.75) -> str:
    """Reading the same sentence on screen and in the caption at the same moment
    wastes the shot. Found by looking at s02 and s05; gated here so it cannot
    come back."""
    import difflib
    tl = json.loads((ROOT/"timeline"/"timeline.json").read_text())
    al = json.loads((ROOT/"script"/"alignment.json").read_text())
    cs = json.loads((ROOT/"captions"/"cues.json").read_text())
    if not cs: raise Fail("no cues to compare against")
    sys.path.insert(0, str(ROOT/"pipeline")); import anchors as A
    times = A.shot_times(tl, al)
    n, bad = 0, []
    for sh in times:
        for text in onscreen_strings(sh):
            for c in cs:
                if c["end"] <= sh["t0"] or c["start"] >= sh["t1"]: continue
                n += 1
                a = re.sub(r"[^a-z ]", "", text.lower()); b = re.sub(r"[^a-z ]", "", c["text"].lower())
                r = difflib.SequenceMatcher(None, a, b).ratio()
                if r >= thresh:
                    bad.append(f"{sh['shot_id']}: on-screen {text[:34]!r} ~= caption {c['text'][:34]!r} ({r:.2f})")
    if n == 0: raise Fail("no on-screen text overlapped any caption — nothing was compared")
    if bad: raise Fail(f"{len(bad)} redundant pairs: " + "; ".join(bad[:2]))
    return f"{n} on-screen/caption pairs compared, none redundant"

def g_credits_after_narration(tol=0.3) -> str:
    """Credits must not run under the voice. In the fixture they started 7.2s
    before the narration finished."""
    tl = json.loads((ROOT/"timeline"/"timeline.json").read_text())
    al = json.loads((ROOT/"script"/"alignment.json").read_text())
    if not al["words"]: raise Fail("no words in alignment")
    last = al["words"][-1]["end"]
    sys.path.insert(0, str(ROOT/"pipeline")); import anchors as A
    cr = [s for s in A.shot_times(tl, al) if s.get("component") == "Credits"]
    if not cr: raise Fail("no Credits shot — the film has no ending credits")
    for c in cr:
        if c["t0"] < last - tol:
            raise Fail(f"{c['shot_id']} starts at {c['t0']:.2f}s, {last - c['t0']:.2f}s before narration ends ({last:.2f}s)")
    return f"credits start at {cr[0]['t0']:.2f}s, after narration ends ({last:.2f}s)"

def g_visual_variety(max_run=2, max_share=0.5) -> str:
    """Four of six fixture shots were the same centred-text card. The film had
    one visual idea. Measurable as a run length and a share of runtime."""
    tl = json.loads((ROOT/"timeline"/"timeline.json").read_text())
    al = json.loads((ROOT/"script"/"alignment.json").read_text())
    sys.path.insert(0, str(ROOT/"pipeline")); import anchors as A
    sh = A.shot_times(tl, al)
    if len(sh) < 2: raise Fail("fewer than 2 shots — variety is not measurable")
    run, worst, prev = 1, 1, None
    for s in sh:
        k = s.get("component")
        run = run + 1 if k == prev else 1
        worst = max(worst, run); prev = k
    if worst > max_run: raise Fail(f"{worst} consecutive shots use the same component (max {max_run})")
    total = sum(s["t1"] - s["t0"] for s in sh)
    share: dict = {}
    for s in sh: share[s.get("component")] = share.get(s.get("component"), 0) + (s["t1"] - s["t0"])
    top, sec = max(share.items(), key=lambda kv: kv[1])
    if sec / total > max_share:
        raise Fail(f"{top} occupies {sec/total:.0%} of runtime (max {max_share:.0%})")
    return f"longest same-component run {worst}, largest share {sec/total:.0%} ({top})"

def g_shot_review() -> str:
    """Every shot looked at, and the verdicts describe THIS render."""
    r = ROOT/"review"/"shot_review.json"
    if not r.exists(): raise Fail("no shot review — run pipeline/review_shots.py prepare and look at the frames")
    d = json.loads(r.read_text())
    tl = json.loads((ROOT/"timeline"/"timeline.json").read_text())
    if len(d["shots"]) != len(tl["shots"]):
        raise Fail(f"review covers {len(d['shots'])} of {len(tl['shots'])} shots")
    cap = ROOT/"exports"/"captioned.mp4"
    if cap.exists() and cap.stat().st_mtime > d.get("render_mtime", 0) + 1:
        raise Fail("the render changed after the review — verdicts describe an older film")
    un = [s["shot_id"] for s in d["shots"] if s["verdict"] is None]
    if un: raise Fail(f"{len(un)} shot(s) unreviewed: {', '.join(un[:4])}")
    rev = [s["shot_id"] for s in d["shots"] if s["verdict"] == "revise"]
    if rev: raise Fail(f"{len(rev)} shot(s) marked revise: {', '.join(rev[:4])}")
    mis = [s["shot_id"] for s in d["shots"] if s["matches_narration"] is False]
    if mis: raise Fail(f"{len(mis)} shot(s) show something other than what is said: {', '.join(mis)}")
    return f"all {len(d['shots'])} shots reviewed and accepted"

def g_fixture_not_shipped() -> str:
    al = json.loads((ROOT/"script"/"alignment.json").read_text())
    if al.get("scratch"):
        raise Fail("alignment came from the SCRATCH synthetic voice, not a recording. "
                   "The draft is for reviewing the edit; record the real voiceover before release.")
    if al.get("_fixture"):
        raise Fail("alignment.json is the SYNTHETIC fixture — timings were invented, "
                   "not measured from a recording. Run pipeline/align.py on the real voiceover.")
    return "alignment came from a real recording"

# ---------------------------------------------------------------- self-test

def make_broken(kind: str, d: pathlib.Path) -> pathlib.Path:
    """Build a video that SHOULD trip a specific gate."""
    out = d/f"{kind}.mp4"
    common = ["-c:v","libx264","-pix_fmt","yuv420p","-r",str(FPS)]
    if kind == "black_tail":
        sh(["ffmpeg","-v","error","-y","-f","lavfi","-i",f"color=c=white:s=1080x1920:r={FPS}:d=2",
            "-f","lavfi","-i",f"color=c=black:s=1080x1920:r={FPS}:d=1",
            "-filter_complex","[0:v][1:v]concat=n=2:v=1:a=0",*common,str(out)])
    elif kind == "frozen_tail":
        sh(["ffmpeg","-v","error","-y","-f","lavfi","-i",f"testsrc=s=1080x1920:r={FPS}:d=2",
            "-f","lavfi","-i",f"color=c=gray:s=1080x1920:r={FPS}:d=2.5",
            "-filter_complex","[0:v][1:v]concat=n=2:v=1:a=0",*common,str(out)])
    elif kind == "out_of_bounds":
        # white block at x=950 — under Instagram's right-side buttons
        sh(["ffmpeg","-v","error","-y","-f","lavfi","-i",f"color=c=black:s=1080x1920:r={FPS}:d=2",
            "-vf","drawbox=x=400:y=600:w=200:h=200:color=white:t=fill,"
                  "drawbox=x=950:y=600:w=80:h=200:color=white:t=fill",*common,str(out)])
    elif kind == "empty_essential":
        sh(["ffmpeg","-v","error","-y","-f","lavfi","-i",f"color=c=black:s=1080x1920:r={FPS}:d=2",*common,str(out)])
    elif kind == "silent":
        sh(["ffmpeg","-v","error","-y","-f","lavfi","-i",f"color=c=white:s=1080x1920:r={FPS}:d=2",
            "-f","lavfi","-i","anullsrc=r=48000:cl=mono","-t","2",*common,"-c:a","aac","-shortest",str(out)])
    return out

CONTROLS = [
    ("black_tail",      "black tail",        lambda p: g_black_tail(p)),
    ("frozen_tail",     "frozen tail",       lambda p: g_frozen_tail(p)),
    ("out_of_bounds",   "safe area",         lambda p: g_safe_area(p)),
    ("empty_essential", "safe-area FLOOR",   lambda p: g_safe_area(p)),
    ("silent",          "loudness",          lambda p: g_loudness(p)),
]

def self_test() -> int:
    print("CONTROLS — each of these MUST go red. A green here means the gate is vacuous.\n")
    bad = 0
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        for kind, label, fn in CONTROLS:
            p = make_broken(kind, d)
            if not p.exists():
                print(f"  ?? {label:<18} control video could not be built"); bad += 1; continue
            try:
                detail = fn(p)
                print(f"  \033[31mVACUOUS\033[0m {label:<18} passed a video that should fail it: {detail}")
                bad += 1
            except Fail as e:
                print(f"  \033[32mRED\033[0m     {label:<18} {str(e)[:96]}")
    print(f"\n{len(CONTROLS)-bad}/{len(CONTROLS)} gates demonstrated they can fail.")
    return 1 if bad else 0

# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--clean", default="exports/clean.mp4")
    ap.add_argument("--captioned", default="exports/captioned.mp4")
    ap.add_argument("--essential", default="review/essential.mp4")
    ap.add_argument("--allow-fixture", action="store_true",
                    help="permit the synthetic alignment (pipeline development only)")
    a = ap.parse_args()
    if a.self_test: return self_test()

    clean, cap, ess = (ROOT/a.clean, ROOT/a.captioned, ROOT/a.essential)
    checks: list[tuple[str, callable]] = []
    if not a.allow_fixture: checks.append(("real alignment", g_fixture_not_shipped))
    checks += [
        ("exports not stale",     lambda: g_not_stale([clean, cap, ess])),
        ("visual mix / purposes", g_visual_mix),
        ("caption quality",       g_captions),
        ("caption redundancy",    g_caption_redundancy),
        ("credits after voice",   g_credits_after_narration),
        ("visual variety",        g_visual_variety),
        ("shot review (vision)",  g_shot_review),
        ("captioned decodes",     lambda: g_decodes(cap)),
        ("captioned format",      lambda: g_format(cap)),
        ("captioned black tail",  lambda: g_black_tail(cap)),
        ("captioned frozen tail", lambda: g_frozen_tail(cap)),
        ("clean decodes",         lambda: g_decodes(clean)),
        ("clean format",          lambda: g_format(clean)),
        ("clean/captioned parity",lambda: g_parity(clean, cap)),
        ("safe area (pixels)",    lambda: g_safe_area(ess)),
        ("loudness",              lambda: g_loudness(cap)),
    ]
    fails = 0
    for name, fn in checks:
        try:
            print(f"  \033[32mPASS\033[0m {name:<24} {fn()}")
        except Fail as e:
            print(f"  \033[31mFAIL\033[0m {name:<24} {e}"); fails += 1
        except FileNotFoundError as e:
            print(f"  \033[31mFAIL\033[0m {name:<24} missing file: {e}"); fails += 1
    print(f"\n{len(checks)-fails}/{len(checks)} gates passed.")
    if fails: print("NOT RELEASABLE.")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
