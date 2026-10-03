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
        for a in (s.get("props") or {}).get("asset_ids", []) or []: used.add(a)
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
        if not a.get("subject", "").strip():
            problems.append(f"{aid}: no subject — it was never looked at, so what is in it is unknown")
        if not a.get("rights", "").strip():
            problems.append(f"{aid}: no rights basis recorded")
        cr = a.get("crop_restrictions", "")
        if ("text" in cr.lower() or "burn" in cr.lower()) and not a.get("crop"):
            problems.append(f"{aid}: its restrictions describe burned-in text but no crop is declared — "
                            f"a restriction that is only advice gets ignored")
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
    for name, fn in (("sheet", sheet), ("check", check), ("plan", plan), ("stage", stage)):
        sub.add_parser(name).set_defaults(fn=fn)
    a = ap.parse_args()
    sys.exit(a.fn(a))
