#!/usr/bin/env python3
"""Build the year chart: every Cent, one cell each, stacked in its year's column.

One cell is one Cent, so the chart's area is the collection's count; nothing is
scaled or binned. At 3 px a Cent is texture, never evidence of a trait.

    python3 films/secret-history/build/year_chart.py --src <sovrn-onchain>/cents
Writes public/secret-history/year_chart.png and films/secret-history/build/year_chart.json.
"""
import argparse, csv, json, sys
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
DATA = Path("/mnt/project-files/knowledge/data/cents_traits.csv")
Y0, Y1 = 1910, 1982
CELL, PER_ROW = 3, 3              # px per Cent, Cents per row in a column
COL_W = CELL * PER_ROW + 1        # 10 px with a 1 px gutter; 73 columns = 730 px
# Centred in the essential region (x 80-860), not the canvas: the right-hand
# platform rail would otherwise sit over 1975-1982, the years the film is about.
X0, BASE = 80 + (780 - (Y1 - Y0 + 1) * COL_W) // 2, 1290

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--src", required=True); a = ap.parse_args()
    src = Path(a.src)
    by = defaultdict(list)
    for r in csv.DictReader(open(DATA)):
        by[int(r["year"])].append(int(r["cent"]))
    total = sum(len(v) for v in by.values())
    if total != 10000: sys.exit(f"expected 10,000 Cents, read {total}")
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    mask = Image.new("L", (CELL * 8, CELL * 8), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, CELL * 8 - 1, CELL * 8 - 1), fill=255)
    mask = mask.resize((CELL, CELL), Image.LANCZOS)
    cols, placed = {}, 0
    for y in range(Y0, Y1 + 1):
        ns = sorted(by.get(y, []))
        x = X0 + (y - Y0) * COL_W
        rows = -(-len(ns) // PER_ROW)
        cols[y] = {"x": x, "w": COL_W, "count": len(ns), "top": BASE - rows * CELL}
        for i, n in enumerate(ns):
            c = Image.open(src / f"{n}.webp").convert("RGB")
            w, h = c.size; c = c.crop((int(w*.1), int(h*.1), int(w*.9), int(h*.9))).resize((CELL, CELL), Image.LANCZOS)
            im.paste(c, (x + (i % PER_ROW) * CELL, BASE - (i // PER_ROW + 1) * CELL), mask)
            placed += 1
    if placed != 10000: sys.exit(f"placed {placed} Cents, expected 10,000")
    out = ROOT / "public" / "secret-history"; out.mkdir(parents=True, exist_ok=True)
    im.save(out / "year_chart.png")
    json.dump({"cell": CELL, "per_row": PER_ROW, "x0": X0, "base": BASE, "columns": cols},
              open(Path(__file__).with_name("year_chart.json"), "w"), indent=1)
    print(f"placed {placed} Cents; tallest column {max(c['count'] for c in cols.values())} -> top y {min(c['top'] for c in cols.values())}")

if __name__ == "__main__": main()
