#!/usr/bin/env python3
"""Stage real Cent images into public/cents/<n>.webp as circular cutouts.

The on-chain images (sovrn-onchain cents/<n>.webp, 300px) sit on a white
square. On this series' dark palette that square reads as a sticker, so each
image is cropped to the coin's measured bounding box and masked to a circle
with a transparent outside. Only the numbers a film uses are staged; public/cents
is gitignored because the source repo is the record.

    python3 pipeline/stage_cents.py --src <sovrn-onchain>/cents 3981 7823 ...
    python3 pipeline/stage_cents.py --src <sovrn-onchain>/cents --from-json films/sets/cents.json
    python3 pipeline/stage_cents.py --self-test

The bounding box is measured, not assumed: pixels darker than WHITE_CUT are
coin. A crop that comes back far from square means the measurement broke (a
background that isn't white, a shadow), and the script refuses rather than
staging a squashed coin.
"""
import argparse, json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "cents"
WHITE_CUT = 235      # 0-255 luminance; above this is background
MAX_ASPECT = 1.08    # a coin's box is square; worse than this is a broken measurement
OPEN_PX = 5         # morphological opening, px; must be odd
SUPERSAMPLE = 4      # mask drawn larger then reduced, for a clean edge


def coin_box(im: Image.Image) -> tuple[int, int, int, int]:
    mask = im.convert("L").point(lambda v: 255 if v < WHITE_CUT else 0)
    # Opening removes specks of dust on the white field. Without it 4 of the
    # 10,000 (#2476, #2553, #6401, #9345) measured 20-28px too wide or tall.
    mask = mask.filter(ImageFilter.MinFilter(OPEN_PX)).filter(ImageFilter.MaxFilter(OPEN_PX))
    box = mask.getbbox()
    if box is None:
        raise ValueError("no coin pixels found (all background)")
    w, h = box[2] - box[0], box[3] - box[1]
    if max(w, h) / min(w, h) > MAX_ASPECT:
        raise ValueError(f"coin box {w}x{h} is not square; measurement broke")
    return box


def cutout(src: Path) -> Image.Image:
    im = Image.open(src).convert("RGB")
    im = im.crop(coin_box(im))
    s = max(im.size)
    im = im.resize((s, s), Image.LANCZOS)
    big = Image.new("L", (s * SUPERSAMPLE, s * SUPERSAMPLE), 0)
    ImageDraw.Draw(big).ellipse((1, 1, s * SUPERSAMPLE - 2, s * SUPERSAMPLE - 2), fill=255)
    out = im.convert("RGBA")
    out.putalpha(big.resize((s, s), Image.LANCZOS))
    return out


def stage(src_dir: Path, numbers: list[int]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    done = 0
    for n in numbers:
        if not 1 <= n <= 10000:
            raise SystemExit(f"#{n} is not a Cent number")
        src = src_dir / f"{n}.webp"
        if not src.exists():
            raise SystemExit(f"missing source image {src}")
        cutout(src).save(OUT / f"{n}.webp", lossless=False, quality=92)
        done += 1
    return done


def self_test() -> int:
    """Controls: each must be refused. A check never seen red means nothing."""
    import tempfile
    fails = 0
    with tempfile.TemporaryDirectory() as t:
        blank = Path(t) / "blank.webp"
        Image.new("RGB", (300, 300), "white").save(blank)
        smear = Path(t) / "smear.webp"
        im = Image.new("RGB", (300, 300), "white")
        ImageDraw.Draw(im).rectangle((20, 100, 280, 200), fill=(120, 70, 40))
        im.save(smear)
        good = Path(t) / "good.webp"
        im = Image.new("RGB", (300, 300), "white")
        ImageDraw.Draw(im).ellipse((30, 30, 270, 270), fill=(150, 90, 50))
        im.save(good)
        for name, path in [("all-white image", blank), ("non-square smear", smear)]:
            try:
                cutout(path)
                print(f"GREEN (wrong): {name} was staged"); fails += 1
            except ValueError as e:
                print(f"RED (right): {name}: {e}")
        out = cutout(good)
        corner, centre = out.getpixel((0, 0))[3], out.getpixel((out.width // 2, out.height // 2))[3]
        if corner == 0 and centre == 255 and abs(out.width - 241) <= 2:
            print(f"OK: synthetic coin cut to {out.width}px, corner clear, centre opaque")
        else:
            print(f"FAIL: synthetic coin {out.width}px corner={corner} centre={centre}"); fails += 1
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, help="sovrn-onchain/cents directory")
    ap.add_argument("--from-json", type=Path, help="JSON file with a list of Cent numbers, or {'cents': [...]}")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("numbers", nargs="*", type=int)
    a = ap.parse_args()
    if a.self_test:
        sys.exit(1 if self_test() else 0)
    nums = list(a.numbers)
    if a.from_json:
        j = json.loads(a.from_json.read_text())
        nums += j["cents"] if isinstance(j, dict) else j
    nums = sorted(set(nums))
    if not nums or not a.src:
        ap.error("need --src and at least one Cent number")
    print(f"staged {stage(a.src, nums)} Cents to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
