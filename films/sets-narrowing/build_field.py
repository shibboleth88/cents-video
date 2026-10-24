#!/usr/bin/env python3
"""Bake the 10,000-Cent field into one image per state.

Drawing 10,000 <Img> elements timed the renderer out. At 8px a Cent is texture
anyway (below the 60px trait floor), so the field is composited once from the
same staged cutouts the walls use: every cell is the real Cent its position
names, in number order, 100 to a row. Nothing is generated or retouched; a lit
state only darkens the Cents outside the pool.

  python3 films/sets-narrowing/build_field.py
"""
import json, pathlib, sys
from PIL import Image, ImageEnhance

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CENTS = ROOT / "public" / "cents"
OUT = ROOT / "public" / "narrowing"
CELL, COLS = 8, 100
SCALE = 2  # baked at 2x so the 800px field stays sharp on a 1080 canvas

pools = json.loads((ROOT / "films/sets/data/pools.json").read_text())["pools"]
STATES = {"all": None, "desert-notable": "desert:notable+"}

missing = [n for n in range(1, 10001) if not (CENTS / f"{n}.webp").exists()]
if missing:
    sys.exit(f"{len(missing)} Cents not staged (first: {missing[:5]}); run pipeline/stage_cents.py")

px = CELL * SCALE
tiles = {}
for n in range(1, 10001):
    tiles[n] = Image.open(CENTS / f"{n}.webp").convert("RGBA").resize((px, px), Image.LANCZOS)

OUT.mkdir(parents=True, exist_ok=True)
for name, key in STATES.items():
    lit = set(pools[key]) if key else None
    if lit is not None and len(lit) == 0: sys.exit(f"pool {key} is empty")
    img = Image.new("RGBA", (COLS * px, COLS * px), (0, 0, 0, 0))
    for n, t in tiles.items():
        if lit is not None and n not in lit:
            t = t.copy(); a = t.getchannel("A").point(lambda v: int(v * 0.12)); t.putalpha(a)
        i = n - 1
        img.alpha_composite(t, ((i % COLS) * px, (i // COLS) * px))
    img.save(OUT / f"field-{name}.png", optimize=True)
    print(f"field-{name}.png: {img.size[0]}px, lit {len(lit) if lit else 10000}")
