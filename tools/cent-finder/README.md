# Cent Finder

A private web page that identifies a Cent from a photo or screenshot of its obverse.
Live page: https://claude.ai/artifact/6npvEACHwbeiJ1pBgQk9jn (published 2026-11-25).

## How it works

1. **Find the coin.** Downscale to 200 px, mask pixels that differ from the border colour,
   and take connected components that look like a filled circle. A filled rectangle (an
   image pasted on a page) is searched inside. Four centred circles (1.0 to 1.45 times the
   inscribed circle) are always added for crops tighter than the coin.
2. **Fingerprint.** Crop each candidate circle to 64 x 64, box-average to 16 x 16, keep
   the 148 cells inside the face, z-score each colour channel (removes brightness,
   contrast and colour cast), subtract the mean over all Cents, and L2-normalise.
3. **Compare** with all 10,000 obverses (cosine), at rotations 0, ±5, ±10 degrees, taking
   the best candidate. Verdict: **Match** if top score ≥ 0.86 and lead over the second
   ≥ 0.08; **Check by eye** if top ≥ 0.75; otherwise **No clear match**.

The index is built from the 300 px images in `shibboleth88/sovrn-onchain` (`cents/<n>.webp`).
It ships as `index.png` (148 x 10000 RGB, lossless, one row per Cent); the page checks a
byte checksum on load.

## Test results (2026-11-25)

Queries came from a different source than the index: 63 cents.vision 1050 px fronts (all
1964 no-mint-mark Cents with a verdigris trait) and 55 random Instagram-set 800 px heads.
Each was tested in 10 kinds of copy: original, JPEG q25 at 400 px, 120 px, dark-UI phone
screenshot, light-UI desktop screenshot, tight crop (inner 68%), 4° rotation, colour cast
with blur, phone-style (cast, blur, rotation, JPEG q40), and black background.

- Python (`evaluate.py`): right Cent first in 1,179 of 1,180; the miss (#9247, tight crop)
  was second. "Match" given 1,098 times, never wrong. With the true Cent removed from the
  index, "Match" appeared 0 times in 1,180 trials (best wrong score 0.828).
- In the page (`browser_test.cjs`, headless Chromium): 590 of 590 right on 5 of the kinds
  (original, JPEG q25, dark screenshot, tight crop, phone-style); 0 "Match" on 118 mirrored
  images and 20 reverses (none are Cents). About 0.15–0.2 s per image.

Not covered: reverses (not indexed), and new photos of a physical coin under new light.

## Rebuild

```bash
cd ~/cents-video/tools/cent-finder   # wherever the repo is cloned
git clone --depth 1 https://github.com/shibboleth88/sovrn-onchain.git /tmp/sovrn-onchain
python3 build_index.py /tmp/sovrn-onchain/cents idx.npz
python3 make_site.py idx.npz /tmp/sovrn-onchain/cents <path to cents_traits_sep2026.json> <sample image> site/
cp cent-finder.html site/   # update the checksum in it if make_site.py prints a new one
python3 evaluate.py idx.npz <folder of query images named <n>.webp or <n>.jpg>
```

Publish `site/cent-finder.html` with `site/` as root and the 103 data files
(`thumbs/s00.webp`–`s99.webp`, `index.png`, `cents.json`, `sample.jpg`).
`browser_test.cjs` expects the page wrapped as `site/test.html` and served on
port 8765, with test images in `jstest/<kind>/<n>.png`.
