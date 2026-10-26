#!/usr/bin/env python3
"""Pre-render all 10,000 Cents as one 100x100 mosaic, public/cents_field.webp.

A frame that loads 10,000 separate images times out in the renderer (33 s).
At 10px a Cent is texture anyway (grids.tsx MIN_TRAIT_PX), so one image of the
same cutouts, in number order, is the same picture at a fraction of the cost.

    python3 pipeline/field_mosaic.py [--cell 10]
"""
import argparse, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "public" / "cents"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cell", type=int, default=10)
    c = ap.parse_args().cell
    missing = [n for n in range(1, 10001) if not (SRC / f"{n}.webp").exists()]
    # Floor: a mosaic with holes would read as a complete collection.
    if missing:
        sys.exit(f"{len(missing)} cutouts missing from {SRC} (first: {missing[:5]}); run stage_cents.py first")
    out = Image.new("RGBA", (100 * c, 100 * c), (0, 0, 0, 0))
    for n in range(1, 10001):
        im = Image.open(SRC / f"{n}.webp").convert("RGBA").resize((c, c), Image.LANCZOS)
        i = n - 1
        out.alpha_composite(im, ((i % 100) * c, (i // 100) * c))
    dst = ROOT / "public" / "cents_field.webp"
    out.save(dst, quality=90)
    print(f"wrote {dst.relative_to(ROOT)} ({out.width}x{out.height}) from 10,000 cutouts")

if __name__ == "__main__":
    main()
