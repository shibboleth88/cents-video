#!/usr/bin/env python3
"""Stage the cents.vision screenshots for the renderer (public/vision/, gitignored).

  python3 pipeline/stage_vision.py [/mnt/project-files/sets-video/vision-shots/]

The captures were made in another session (see that folder's README): 1080 px
wide, wallet addresses hidden and scanned for. The Collector Walls scroll frames
are 80% of a screen apart, so the top 1536 px of each consecutive frame tiles
into one tall strip without the fixed footer. Frames 00-01 are left out: they
hold the artist wallet, whose naming in this film is still the user's call.
"""
from __future__ import annotations
import pathlib, shutil, sys
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/sets-video/vision-shots/")
OUT = ROOT / "public" / "vision"
COPY = ["01_home_lab_viewport", "02_trait_atlas_verdigris_full", "03_sets_viewport"]
STRIP = range(2, 6)
# The user's own captures (24 Oct 2026), landscape. Scaled to 1080 wide so every
# screen shares one coordinate system. The Void cards list the holding wallet
# under each Cent; everything from that row down is cut away (ADDRESS_CUT, in
# the capture's own pixels), so no address reaches the screen.
USER = {"holders_floor": None, "sales_volume": None, "void": 1204, "traits_lab_filters": None, "centsbot": None}
STEP = 1536

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in COPY:
        p = SRC / f"{name}.png"
        if not p.exists(): sys.exit(f"missing {p}")
        im = Image.open(p)
        if im.width != 1080: sys.exit(f"{p.name} is {im.width} px wide, expected 1080")
        im.convert("RGB").save(OUT / f"{name}.jpg", quality=90)
    for name, cut in USER.items():
        p = SRC / "user" / f"{name}.png"
        if not p.exists(): sys.exit(f"missing {p}")
        im = Image.open(p).convert("RGB")
        if cut: im = im.crop((0, 0, im.width, cut))
        im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS).save(OUT / f"{name}.jpg", quality=90)
    frames = [Image.open(SRC / f"04_collectors_claimed_scroll_{k:02d}.png").convert("RGB") for k in STRIP]
    strip = Image.new("RGB", (1080, STEP * len(frames)))
    for i, f in enumerate(frames):
        if f.size != (1080, 1920): sys.exit(f"scroll frame {STRIP[i]} is {f.size}")
        strip.paste(f.crop((0, 0, 1080, STEP)), (0, i * STEP))
    # Seam check: the overlap a frame shares with the next must agree, or the
    # frames were not 1536 px apart and the strip would stutter.
    for i in range(len(frames) - 1):
        a = frames[i].crop((0, STEP, 1080, STEP + 200)).tobytes()
        b = frames[i + 1].crop((0, 0, 1080, 200)).tobytes()
        diff = sum(abs(x - y) for x, y in zip(a[::97], b[::97])) / len(a[::97])
        if diff > 6: sys.exit(f"seam {STRIP[i]}->{STRIP[i+1]} differs by {diff:.1f}; frames are not {STEP}px apart")
    strip.save(OUT / "collectors_strip.jpg", quality=88)
    print(f"staged {len(COPY)} pages + strip {strip.size} in {OUT}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
