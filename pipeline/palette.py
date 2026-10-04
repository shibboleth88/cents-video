#!/usr/bin/env python3
"""Derive the film's palette from the artwork it is about.

A palette chosen by taste is a decision no one can check. A palette sampled from
the work is downstream of its source: swap the source and the colours move,
which is the whole test. CENTS gives two colours of its own — the copper and the
verdigris that grows on it — so the film is coloured by the thing it describes.

  python3 pipeline/palette.py build          # write src/style/palette.json
  python3 pipeline/palette.py --self-test    # prove the output follows the input
"""
from __future__ import annotations
import colorsys, json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "style" / "palette.json"
# The assets the palette is taken from, and what each contributes.
SOURCES = [("a03", "verdigris"), ("a05", "copper")]

def pixels(path: pathlib.Path, n: int = 96):
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "f.png"
        subprocess.run(["ffmpeg","-v","error","-y","-i",str(path),"-frames:v","1",
                        "-vf",f"scale={n}:{n}",str(p)], check=True)
        return list(Image.open(p).convert("RGB").getdata())

def hsv(c): 
    r, g, b = [x/255 for x in c]; return colorsys.rgb_to_hsv(r, g, b)

def dominant(px, min_sat=0.25, min_val=0.18, max_val=0.95):
    """Most common hue among pixels that actually carry colour. Greys and blown
    highlights are excluded: a white studio background would otherwise win."""
    buckets: dict[int, list] = {}
    for c in px:
        h, s, v = hsv(c)
        if s < min_sat or not (min_val < v < max_val): continue
        buckets.setdefault(int(h * 36), []).append((h, s, v))
    if not buckets: raise SystemExit("no saturated pixels — cannot derive a colour")
    key = max(buckets, key=lambda k: len(buckets[k]))
    grp = buckets[key]
    h = sum(x[0] for x in grp)/len(grp)
    s = sum(x[1] for x in grp)/len(grp)
    v = sum(x[2] for x in grp)/len(grp)
    return h, s, v, len(grp)/max(1, len(px))

def hexs(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, max(0, min(1, s)), max(0, min(1, v)))
    return "#%02x%02x%02x" % (int(r*255), int(g*255), int(b*255))

def derive(assets: dict) -> dict:
    out, shares = {}, {}
    for aid, role in SOURCES:
        a = assets.get(aid)
        if not a: raise SystemExit(f"{aid} is not in the inventory")
        h, s, v, share = dominant(pixels(ROOT / a["path"]))
        # Lift to a usable screen value without changing the hue it came from.
        out[role] = hexs(h, min(0.92, s * 1.15), min(0.86, max(0.52, v * 1.35)))
        out[role + "_deep"] = hexs(h, min(1.0, s * 1.2), max(0.16, v * 0.42))
        shares[role] = round(share, 4)
    # Ground and ink take the copper hue at very low saturation, so the neutrals
    # are not a default grey but a neutral belonging to this film.
    ch, cs, cv, _ = dominant(pixels(ROOT / assets[SOURCES[1][0]]["path"]))
    out["bg"] = hexs(ch, 0.10, 0.045)
    out["surface"] = hexs(ch, 0.09, 0.10)
    out["ink"] = hexs(ch, 0.05, 0.96)
    out["inkDim"] = hexs(ch, 0.08, 0.63)
    out["rule"] = hexs(ch, 0.10, 0.20)
    out["_sources"] = {aid: {"role": role, "share": shares[role]} for aid, role in SOURCES}
    out["_derived_from"] = {aid: assets[aid]["sha256"][:12] for aid, _ in SOURCES}
    return out

def build() -> int:
    assets = json.loads((ROOT/"timeline"/"assets.json").read_text())["assets"]
    pal = derive(assets)
    OUT.write_text(json.dumps(pal, indent=1))
    for k, v in pal.items():
        if not k.startswith("_"): print(f"  {k:<14} {v}")
    print(f"-> {OUT.relative_to(ROOT)}")
    return 0

def self_test() -> int:
    """CONTROL: perturb the source and the palette must move. If it does not,
    the palette is decoration wearing the costume of derivation."""
    from PIL import Image
    assets = json.loads((ROOT/"timeline"/"assets.json").read_text())["assets"]
    real = derive(assets)
    with tempfile.TemporaryDirectory() as td:
        fake = pathlib.Path(td) / "fake.png"
        Image.new("RGB", (256, 256), (40, 90, 220)).save(fake)   # flat blue
        perturbed = dict(assets)
        perturbed[SOURCES[1][0]] = {**assets[SOURCES[1][0]], "path": str(fake.relative_to(pathlib.Path("/")))}
        # derive() resolves ROOT/path, so hand it an absolute-safe stand-in
        import types
        saved = assets[SOURCES[1][0]]["path"]
        try:
            assets[SOURCES[1][0]]["path"] = str(fake)
            moved = derive(assets)
        finally:
            assets[SOURCES[1][0]]["path"] = saved
    changed = [k for k in ("copper", "bg", "ink", "rule") if real[k] != moved[k]]
    print(f"real copper={real['copper']} bg={real['bg']}")
    print(f"with a flat blue source: copper={moved['copper']} bg={moved['bg']}")
    if len(changed) < 3:
        print("\033[31mVACUOUS\033[0m palette barely moved when its source was replaced"); return 1
    print(f"\033[32mPASS\033[0m {len(changed)} tokens moved with the source: {', '.join(changed)}")
    return 0

if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else build())
