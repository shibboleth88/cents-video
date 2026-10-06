#!/usr/bin/env python3
"""Asset stage: find, record, inspect and gate the images a film uses.

Four sub-commands:

  ingest   pull candidates from a folder, a zip, or a saved web page, keeping
           PROVENANCE. For a saved page, only figures inside the article body
           are taken - a Medium export is mostly sidebar advertising, and a
           filename cannot tell you which is which.
  sheet    contact sheet + per-asset thumbnails, so each asset can be LOOKED AT.
  check    release gate: nothing is usable without a written subject, a rights
           basis, and a hash that still matches the file on disk.
  plan     which shots want imagery, and whether anything available satisfies it.

The rule this enforces: an asset is identified by looking at it, never by its
filename. Everything else here exists to make that rule checkable.
"""
from __future__ import annotations
import argparse, hashlib, html, json, pathlib, re, shutil, subprocess, sys, zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
INV = ROOT / "timeline" / "assets.json"
STORE = ROOT / "inputs" / "assets"
MIN_PX = 400          # below this a web image is a thumbnail or an icon
MIN_BYTES = 20_000

def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def probe(p: pathlib.Path) -> dict:
    r = subprocess.run(["ffprobe","-v","error","-show_entries",
                        "stream=width,height,nb_frames,codec_name:format=duration",
                        "-of","json",str(p)], capture_output=True, text=True)
    if r.returncode != 0: return {}
    d = json.loads(r.stdout); st = (d.get("streams") or [{}])[0]
    return {"width": st.get("width"), "height": st.get("height"),
            "codec": st.get("codec_name"),
            "frames": int(st.get("nb_frames") or 0),
            "duration": float((d.get("format") or {}).get("duration") or 0)}

def load() -> dict:
    if INV.exists():
        d = json.loads(INV.read_text())
        return d if "assets" in d else {"assets": {}}
    return {"assets": {}}

def save(d: dict) -> None:
    INV.write_text(json.dumps(d, indent=1, ensure_ascii=False))

# ---------------------------------------------------------------- ingest

def body_figures(page: pathlib.Path) -> list[tuple[str, str]]:
    """(filename, caption) for figures inside the article body only."""
    s = page.read_text(errors="ignore")
    end = s.find("Written by")
    body = s[:end] if end > 0 else s
    out = []
    for g in re.findall(r"<figure[^>]*>(.*?)</figure>", body, re.S):
        srcs = [x.split("/")[-1] for x in re.findall(r'src="([^"]+)"', g) if "_files/" in x]
        cap = re.findall(r"<figcaption[^>]*>(.*?)</figcaption>", g, re.S)
        cap = html.unescape(re.sub(r"<[^>]+>", "", cap[0])).strip() if cap else ""
        if srcs: out.append((srcs[0], cap))
    return out

def ingest(args) -> int:
    src = pathlib.Path(args.source)
    STORE.mkdir(parents=True, exist_ok=True)
    inv = load()
    pool = pathlib.Path("/tmp/_asset_pool")
    shutil.rmtree(pool, ignore_errors=True); pool.mkdir(parents=True)

    wanted: list[tuple[str, str]] | None = None
    if args.page:
        wanted = body_figures(pathlib.Path(args.page))
        if not wanted: sys.exit("no figures found in the article body — wrong page file?")
        print(f"{len(wanted)} figures in the article body")

    if src.suffix.lower() == ".zip":
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                if n.endswith("/"): continue
                t = pool / pathlib.Path(n).name
                with z.open(n) as f, t.open("wb") as o: shutil.copyfileobj(f, o)
    elif src.is_dir():
        for p in src.rglob("*"):
            if p.is_file(): shutil.copy(p, pool / p.name)
    else:
        sys.exit(f"{src} is not a folder or a zip")

    picked, skipped = 0, 0
    for fname, caption in (wanted or [(p.name, "") for p in sorted(pool.iterdir())]):
        p = pool / fname
        if not p.exists():
            print(f"  MISSING {fname} — listed in the page but not in the archive"); continue
        if p.stat().st_size < MIN_BYTES: skipped += 1; continue
        m = probe(p)
        motion = (m.get("frames") or 0) > 1 or (m.get("duration") or 0) > 0.3
        # A pixel floor alone throws away real material: the Block animation came
        # back from Medium at 385x338 across 111 frames and 5 MB, and was
        # discarded as a thumbnail. Judge motion assets on substance, and record
        # low resolution as a USAGE CONSTRAINT rather than a reason to drop it.
        small = (m.get("width") or 0) < MIN_PX and (m.get("height") or 0) < MIN_PX
        if small and not motion and p.stat().st_size < 120_000:
            skipped += 1; continue
        digest = sha256(p)
        if any(a.get("sha256") == digest for a in inv["assets"].values()):
            skipped += 1; continue
        aid = f"a{len(inv['assets']) + 1:02d}"
        dst = STORE / f"{aid}{p.suffix.lower()}"
        shutil.copy(p, dst)
        inv["assets"][aid] = {
            "path": str(dst.relative_to(ROOT)),
            "sha256": digest, "bytes": p.stat().st_size,
            "width": m.get("width"), "height": m.get("height"),
            "motion": motion, "codec": m.get("codec"),
            "source": args.label, "original_filename": fname,
            "source_caption": caption,
            # Written by LOOKING. Empty means unusable; check() enforces it.
            "subject": "", "kind": args.kind, "rights": args.rights,
            "verified_at": "", "crop_restrictions": "",
            # 1080 canvas: anything under ~760px wide softens noticeably full-bleed.
            "low_res": bool((m.get("width") or 0) < 760),
            "max_display_width": min(1080, int((m.get("width") or 0) * 1.6)) or None,
        }
        picked += 1
    save(inv)
    # FLOOR: an ingest that found nothing must read as a failure, not as "clean".
    if picked == 0: sys.exit(f"ingested 0 assets ({skipped} skipped) — nothing to work with")
    print(f"ingested {picked}, skipped {skipped}; inventory now {len(inv['assets'])}")
    print("NEXT: pipeline/assets.py sheet, look at every one, then write its subject.")
    return 0

# ---------------------------------------------------------------- sheet

def sheet(args) -> int:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        sys.exit("needs pillow:  pip3 install pillow")
    inv = load()["assets"]
    if not inv: sys.exit("inventory is empty — run ingest first")
    out = ROOT / "review" / "assets"; out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.png"): f.unlink()
    S, C = 340, 4
    tiles = []
    for aid, a in sorted(inv.items()):
        p = ROOT / a["path"]
        t = out / f"{aid}.png"
        subprocess.run(["ffmpeg","-v","error","-y","-i",str(p),"-frames:v","1",
                        "-vf",f"scale={S}:{S}:force_original_aspect_ratio=decrease,"
                              f"pad={S}:{S}:(ow-iw)/2:(oh-ih)/2:color=0x1a1a1a",str(t)])
        if t.exists(): tiles.append((aid, t))
    if len(tiles) < len(inv):
        print(f"  WARNING only {len(tiles)}/{len(inv)} assets rendered a thumbnail")
    R = (len(tiles) + C - 1) // C
    sh = Image.new("RGB", (C*S, R*S), (34,34,34)); d = ImageDraw.Draw(sh)
    for i, (aid, t) in enumerate(tiles):
        sh.paste(Image.open(t).convert("RGB"), ((i%C)*S, (i//C)*S))
        d.rectangle([(i%C)*S+4,(i//C)*S+4,(i%C)*S+56,(i//C)*S+30], fill=(0,0,0))
        d.text(((i%C)*S+12,(i//C)*S+10), aid, fill=(255,215,0))
    dst = ROOT/"review"/"assets_sheet.png"; sh.save(dst)
    print(f"{len(tiles)} thumbnails -> {dst.relative_to(ROOT)}  (look at it, then write subjects)")
    return 0

# ---------------------------------------------------------------- check

def check(args) -> int:
    inv = load()["assets"]
    tl = json.loads((ROOT/"timeline"/"timeline.json").read_text())
    used = {s["asset_id"] for s in tl["shots"] if s.get("asset_id")}
    for s in tl["shots"]:
        pr = s.get("props") or {}
        # Backdrops are used assets too. Leaving them out made this gate report
        # "all used assets are fine" while never looking at either generated
        # clip — the exact shape of a check that passes by not checking.
        if pr.get("backdrop"): used.add(pr["backdrop"])
        for a in pr.get("asset_ids", []) or []: used.add(a)
    problems = []
    if not inv: problems.append("asset inventory is empty")
    # FLOOR: "all used assets are fine" is vacuous when none are used. If real
    # material has been identified and the film uses none of it, say so.
    identified = [k for k, a in inv.items() if a.get("subject", "").strip()]
    if identified and not used:
        problems.append(f"{len(identified)} identified assets available and the film uses none of them")
    for aid in sorted(used):
        a = inv.get(aid)
        if not a: problems.append(f"{aid}: used by a shot but not in the inventory"); continue
        p = ROOT / a["path"]
        if not p.exists(): problems.append(f"{aid}: file missing at {a['path']}"); continue
        # The drift gate exists to catch a model RETOUCHING SOMETHING REAL. A
        # clip derived from a generated image has no real subject to falsify,
        # and abstract footage is supposed to change — billowing dust that held
        # still would be the failure. Scope it to real sources.
        src_kind = (inv.get(a.get("derived_from") or "", {}) or {}).get("kind")
        if not a.get("subject", "").strip():
            problems.append(f"{aid}: no subject — it was never looked at, so what is in it is unknown")
        if not a.get("rights", "").strip():
            problems.append(f"{aid}: no rights basis recorded")
        if a.get("kind") == "generated" and a.get("derived_from") and src_kind != "real":
            if not a.get("subject", "").strip():
                problems.append(f"{aid}: generated-from-generated clip still needs a written subject")
        cr = a.get("crop_restrictions", "")
        import re as _re
        if _re.search(r"\b(text|burn\w*)\b", cr.lower()) and not a.get("crop"):
            problems.append(f"{aid}: its restrictions describe burned-in text but no crop is declared — "
                            f"a restriction that is only advice gets ignored")
        if a.get("kind") == "generated" and a.get("derived_from") and src_kind == "real":
            try:
                drift = _object_drift(aid, a, inv)
            except Exception as e:
                problems.append(f"{aid}: drift check failed: {e}")
                drift = None
            if drift is None:
                problems.append(f"{aid}: generated clip could not be compared with its source "
                                f"(PIL missing, or the source is not on disk)")
            elif drift > 12.0:
                problems.append(f"{aid}: the subject drifts {drift:.1f} levels between the clip's start "
                                f"and its midpoint — the model is altering the object, not moving the camera")
        if a.get("low_res") and not a.get("crop_restrictions", "").strip():
            problems.append(f"{aid}: low resolution ({a.get('width')}x{a.get('height')}) and no usage "
                            f"constraint recorded — it will soften if used full-bleed")
        if not a.get("verified_at", "").strip():
            problems.append(f"{aid}: never verified")
        elif sha256(p) != a.get("sha256"):
            problems.append(f"{aid}: file changed since it was verified — re-inspect it")
    for p in problems: print(f"  \033[31mFAIL\033[0m {p}")
    if not problems:
        print(f"  \033[32mPASS\033[0m {len(used)} assets used, all identified by inspection and rights-cleared")
    return 1 if problems else 0

def _object_drift(aid: str, a: dict, inv: dict) -> float | None:
    """How far the OBJECT in a generated clip has wandered from how it starts.

    Image-to-video was asked to move a camera, not to retouch. A clip that
    brightens, cleans or restores the subject has changed it — a falsification in
    a film about real objects, and one that arrives gradually enough that no
    frame looks wrong beside the one before it.

    Measured as median luminance and median saturation of the CENTRAL HALF of
    the frame, comparing the clip's first frame with its midpoint.

    Two earlier versions of this measured the wrong thing. Mean luminance over
    the whole frame conflates the camera moving with the object changing: a
    push-in replaces background with subject and shifts the mean on its own, so
    a faithful clip and a retouched one score alike. The centre stays subject
    throughout, and a median ignores the edge pixels the zoom is churning.
    """
    try:
        from PIL import Image
    except ImportError:
        return None
    staged = ROOT / "public" / "assets" / (a.get("staged_as") or "")
    clip = staged if staged.exists() else ROOT / a["path"]
    if not clip.exists(): return None
    import tempfile, colorsys
    # Some containers report format=duration as "N/A"; fall back to the video
    # stream, then to frames/rate. A duration that fails to parse must not read
    # as "no drift".
    def _dur(path) -> float:
        for args in (["-show_entries","format=duration"],
                     ["-select_streams","v:0","-show_entries","stream=duration"],
                     ["-select_streams","v:0","-count_frames",
                      "-show_entries","stream=nb_read_frames,avg_frame_rate"]):
            r = subprocess.run(["ffprobe","-v","error",*args,"-of","json",str(path)],
                               capture_output=True, text=True)
            if r.returncode != 0: continue
            try: j = json.loads(r.stdout)
            except Exception: continue
            v = (j.get("format") or {}).get("duration")
            if v and v != "N/A": return float(v)
            st = (j.get("streams") or [{}])[0]
            v = st.get("duration")
            if v and v != "N/A": return float(v)
            nf, rate = st.get("nb_read_frames"), st.get("avg_frame_rate")
            if nf and rate and "/" in rate:
                a, b = rate.split("/")
                if float(b): return int(nf) / (float(a) / float(b))
        return 0.0
    dur = _dur(clip)
    if dur < 0.5:
        raise RuntimeError(f"could not determine the duration of {aid}'s clip")
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        for ss, name in ((0.05, "a.png"), (dur * 0.5, "b.png")):
            subprocess.run(["ffmpeg","-v","error","-y","-ss",str(ss),"-i",str(clip),
                            "-frames:v","1","-vf","crop=iw/2:ih/2,scale=120:120",
                            str(d/name)], check=False)
        for name in ("a.png", "b.png"):
            if not (d/name).exists():
                raise RuntimeError(f"could not sample {name} from {aid}")
        def stats(path):
            im = Image.open(path).convert("RGB")
            px = list(im.getdata())
            lum = sorted(0.299*r + 0.587*g + 0.114*b for r, g, b in px)
            sat = sorted(colorsys.rgb_to_hsv(r/255, g/255, b/255)[1] for r, g, b in px)
            n = len(lum)
            return lum[n//2], sat[n//2]
        l0, s0 = stats(d/"a.png"); l1, s1 = stats(d/"b.png")
    # Saturation is scaled to the same range as luminance so one number covers
    # both "it got brighter" and "it got more colourful".
    return max(abs(l1 - l0), abs(s1 - s0) * 255)

def self_test(args) -> int:
    """CONTROL for the drift gate.

    The threshold was set after seeing real numbers, which on its own is worth
    little. So: take a faithful clip, apply the exact fault the gate exists to
    catch — a progressive brightening, as if the model were retouching — and
    require the gate to call it. A threshold that passes a deliberately
    retouched clip is not a threshold.
    """
    import tempfile, json as _j
    inv = load()["assets"]
    base = next((k for k, a in inv.items() if a.get("kind") == "generated"), None)
    if not base: sys.exit("no generated clip to build a control from")
    src = ROOT / "public" / "assets" / (inv[base].get("staged_as") or "")
    if not src.exists(): sys.exit(f"{base} is not staged")
    clean = _object_drift(base, inv[base], inv)
    print(f"  faithful clip {base}: drift {clean:.1f}")
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        out = ROOT / "public" / "assets" / "_control_retouched.mp4"
        # Ramp brightness over the clip: the exact failure mode, at a size the
        # gate must notice.
        r = subprocess.run(["ffmpeg","-v","error","-y","-i",str(src),
                            # eval=frame is load-bearing: eq evaluates its
                            # expressions ONCE at init by default, so without it
                            # the "ramp" is a constant zero and the control
                            # silently tests nothing.
                            "-vf","eq=eval=frame:brightness=0.18*t/3:saturation=1+0.25*t/3",
                            "-an","-c:v","libx264","-pix_fmt","yuv420p",str(out)],
                           capture_output=True, text=True)
        if r.returncode != 0: sys.exit(f"could not build the control: {r.stderr[:160]}")
        fake = {**inv[base], "staged_as": out.name}
        bad = _object_drift("_control", fake, inv)
        # FLOOR on the control itself: if the retouch did not actually change
        # the pixels, a green result means nothing.
        if abs(bad - clean) < 1.0:
            print("  \033[31mCONTROL BROKEN\033[0m the retouched copy is indistinguishable from the "
                  "original — the control is not applying the fault, so this proves nothing.")
            out.unlink(missing_ok=True)
            return 1
        out.unlink(missing_ok=True)
    print(f"  deliberately retouched copy: drift {bad:.1f}")
    if bad <= 12.0:
        print("  \033[31mVACUOUS\033[0m the gate passes a clip it was written to catch."); return 1
    print(f"  \033[32mRED\033[0m the gate flags the retouched copy and passes the faithful one.")
    return 0

# ---------------------------------------------------------------- plan

def plan(args) -> int:
    inv = load()["assets"]
    tl = json.loads((ROOT/"timeline"/"timeline.json").read_text())
    sys.path.insert(0, str(ROOT/"pipeline")); import anchors as A
    al = json.loads((ROOT/"script"/"alignment.json").read_text())
    print(f"{len(inv)} assets in inventory "
          f"({sum(1 for a in inv.values() if a.get('subject'))} identified)\n")
    for s in A.shot_times(tl, al):
        has = s.get("asset_id") or (s.get("props") or {}).get("asset_ids")
        mark = "has imagery" if has else "NO IMAGERY"
        print(f"  {s['shot_id']:<20} {s['t1']-s['t0']:5.1f}s  {s['visual_kind']:<10} {mark}")
        print(f"  {'':<20} says: {s['narration'][:72]!r}")
    return 0

def stage(args) -> int:
    """Copy used assets into public/ for the renderer, leaving inputs/ untouched.

    A declared `crop` is APPLIED HERE, not at render time. a01 carries another
    essay's title burned into its lower third; a crop recorded only as advice
    was ignored by an object-position that could not honour it, and the wrong
    title went on screen. Cutting the pixels at staging means the renderer has
    no way to show them. Originals are never modified."""
    inv = load()["assets"]
    dst = ROOT / "public" / "assets"
    shutil.rmtree(dst, ignore_errors=True); dst.mkdir(parents=True)
    n, cropped = 0, 0
    for aid, a in inv.items():
        src = ROOT / a["path"]
        if not src.exists(): continue
        out = dst / src.name
        # A generated clip can drift away from its source over time. The honest
        # fix is to keep only the faithful window and play it forward then
        # backward, so a short window still covers a long shot without a cut —
        # and the drifted frames do not exist in what the renderer can reach.
        tp = a.get("trim_pingpong")
        if tp:
            keep = float(tp["keep_seconds"])
            fwd, rev = dst / f"_f_{src.stem}.mp4", dst / f"_r_{src.stem}.mp4"
            lst = dst / f"_l_{src.stem}.txt"
            ok = True
            # `-t` AFTER `-i` limits the OUTPUT. The reverse filter buffers the
            # whole input first, so "-i clip -t 2.5 -vf reverse" yields the LAST
            # 2.5s reversed — precisely the drifted frames this is meant to drop.
            # Trim inside the filter chain instead, where it applies before reverse.
            for vf, o in ((f"trim=0:{keep},setpts=PTS-STARTPTS", fwd),
                          (f"trim=0:{keep},setpts=PTS-STARTPTS,reverse", rev)):
                r = subprocess.run(["ffmpeg","-v","error","-y","-i",str(src),"-vf",vf,
                                    "-an","-c:v","libx264","-pix_fmt","yuv420p",str(o)],
                                   capture_output=True, text=True)
                ok = ok and r.returncode == 0
            lst.write_text(f"file '{fwd}'\nfile '{rev}'\n")
            out = dst / f"{src.stem}.mp4"
            r = subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",str(lst),
                                "-c","copy",str(out)], capture_output=True, text=True)
            if not ok or r.returncode != 0:
                sys.exit(f"{aid}: trim/ping-pong failed: {r.stderr[:160]}")
            for f in (fwd, rev, lst): f.unlink(missing_ok=True)
            pr = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                                 "-of","csv=p=0",str(out)], capture_output=True, text=True)
            a["staged_as"] = out.name
            a["staged_width"], a["staged_height"] = a.get("width"), a.get("height")
            a["staged_duration"] = round(float(pr.stdout.strip() or 0), 3)
            n += 1
            continue
        c = a.get("crop")
        if c:
            W, H = a.get("width") or 0, a.get("height") or 0
            x, y = int(c.get("x", 0) * W), int(c.get("y", 0) * H)
            w, h = int(c.get("w", 1) * W), int(c.get("h", 1) * H)
            if w < 16 or h < 16: sys.exit(f"{aid}: crop leaves {w}x{h}")
            r = subprocess.run(["ffmpeg","-v","error","-y","-i",str(src),
                                "-vf",f"crop={w}:{h}:{x}:{y}","-frames:v","1",
                                str(out.with_suffix(".png"))], capture_output=True, text=True)
            if r.returncode != 0: sys.exit(f"{aid}: crop failed: {r.stderr[:160]}")
            out = out.with_suffix(".png")
            a["staged_as"] = out.name; a["staged_width"] = w; a["staged_height"] = h
            cropped += 1
        else:
            shutil.copy(src, out); a["staged_as"] = out.name
            a["staged_width"] = a.get("width"); a["staged_height"] = a.get("height")
        n += 1
    save({"assets": inv, "_note": "staged_* fields are written by assets.py stage"})
    if n == 0: sys.exit("staged 0 assets")
    print(f"staged {n} assets to public/assets/ ({cropped} cropped at staging)")
    return 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("ingest"); g.add_argument("source")
    g.add_argument("--page", help="saved HTML page; only figures in its article body are taken")
    g.add_argument("--label", required=True, help="where these came from")
    g.add_argument("--kind", default="real", choices=["real","stock","generated"])
    g.add_argument("--rights", default="", help="the basis for using these")
    g.set_defaults(fn=ingest)
    for name, fn in (("sheet", sheet), ("check", check), ("plan", plan), ("stage", stage),
                     ("self-test", self_test)):
        sub.add_parser(name).set_defaults(fn=fn)
    a = ap.parse_args()
    sys.exit(a.fn(a))
