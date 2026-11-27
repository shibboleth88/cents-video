"""Stage the pictures for the introduction film into public/assets/intro/ and write timeline/assets.json.

Sources: the cents.gallery media library (shibboleth's own and cleared; ids C... and S...), the web introduction's
images (credited there), and the cents.vision fronts of single Cents (to public/hires/, which git ignores).
Stills are resized to at most 1600 px on the long side. Clips are cut and re-encoded to H.264.

    python3 -I films/intro-2min/timeline/stage_assets.py   (from the repo root; needs the media library files in
    MEDIA, fetched from https://media.cents.gallery/<key>, and network for the fronts)
"""
import hashlib, json, os, pathlib, subprocess, sys, urllib.request
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[3]
F = ROOT / "films/intro-2min"
OUT = ROOT / "public/assets/intro"
HI = ROOT / "public/hires"
MEDIA = pathlib.Path(os.environ.get("MEDIA", "/tmp/claude-0/-home-user/30e12ac9-b8b3-5051-a8bd-c02a3a4895b6/scratchpad/media"))
WEB = pathlib.Path("/mnt/project-files/presentations/web-intro/site/img")
MELT = pathlib.Path(os.environ.get("MELT", "/tmp/claude-0/-home-user/30e12ac9-b8b3-5051-a8bd-c02a3a4895b6/scratchpad/melt/melt.mp4"))
OUT.mkdir(parents=True, exist_ok=True); HI.mkdir(parents=True, exist_ok=True)

LIB = "cents.gallery media library (shibboleth's own, cleared)"
STILLS = {
    # id: (source file, subject, rights)
    "desk": (MEDIA / "C063_c063-pennies-arranged-across-desk-at-rutherford-chang-s-studio.jpg", "Pennies arranged across the desk at Rutherford Chang's studio (C063)", LIB),
    "rolls": (MEDIA / "C061_c061-penny-rolls-on-cutting-mat-at-rutherford-chang-s-studio.jpg", "Penny rolls on the cutting mat at Chang's studio (C061)", LIB),
    "setup": (MEDIA / "C062_c062-penny-photography-setup-at-rutherford-chang-s-studio.jpg", "The penny photography setup at Chang's studio (C062)", LIB),
    "studio": (WEB / "studio.webp", "Chang's studio desk (web introduction image; studio photograph by Rutherford Chang)", "Rutherford Chang, via the cents.gallery media library"),
    "block_floor": (MEDIA / "S0718_s0718-cube-still-photo.jpg", "CENTS Block Copper on a wooden floor (S0718)", LIB),
    "block_copper": (MEDIA / "S0036_s0036-block-copper-still.png", "CENTS Block Copper, still on black (S0036)", LIB),
    "block_christies": (MEDIA / "S0556_s0556-block-image-used-at-christies.jpg", "The image of the block used at Christie's for CENTS Block 839969 (S0556)", LIB),
    "ucca_case": (MEDIA / "C033_c033-ucca-beijing-physical-block-in-case-book-and-digital-model-behind.jpg", "UCCA Beijing: CENTS Block Copper in its case, the book, the model on screen (C033)", LIB),
    "ucca_photo": (MEDIA / "C040_c040-visitors-photographing-and-discussing-block.jpg", "UCCA Beijing: visitors photographing and discussing the block (C040)", LIB),
    "ucca_talk": (MEDIA / "C044_c044-visitors-talking-near-the-block.jpg", "UCCA Beijing: visitors talking near the block (C044)", LIB),
    "ucca_book": (MEDIA / "C038_c038-visitor-looking-closely-at-cents-book-at-ucca-beijing.jpg", "UCCA Beijing: a visitor reading the CENTS book (C038)", LIB),
    "ucca_title": (MEDIA / "C042_c042-hundreds-and-thousands-title-wall-at-ucca-beijing.jpg", "UCCA Beijing: the title wall of Hundreds and Thousands (C042)", LIB),
    "ucca_wide": (MEDIA / "C043_c043-wide-audience-view-with-book-and-block.jpg", "UCCA Beijing: audience with the book and the block (C043)", LIB),
    "bankable": (MEDIA / "S0667_s0667-cents-on-the-wall-strait.jpg", "BANKABLE, Basel Social Club, 2025: Cents of 1971 on the wall (S0667)", LIB),
    "taschen": (MEDIA / "C066_c066-taschen-on-nfts-open-cents-spread.jpg", "Taschen, On NFTs: the CENTS spread (C066)", LIB),
    "press_aia": (MEDIA / "C016_c016-art-in-america-retrospective-review.jpg", "Art in America review of the UCCA survey (C016)", LIB),
    "press_btc": (MEDIA / "C011_c011-bitcoin-magazine-retrospective-headline.jpg", "Bitcoin Magazine article by Steven Reiss (C011)", LIB),
    "mc_archivist": (MEDIA / "S0857_s0857-archivist.webp", "MAKES CENTS cover: Archivist (S0857)", LIB),
    "mc_dazza": (MEDIA / "S0860_s0860-dazza.webp", "MAKES CENTS cover: dazza9 (S0860)", LIB),
    "mc_lehnen": (MEDIA / "S0863_s0863-lehnen.webp", "MAKES CENTS cover: Martin Lehnen (S0863)", LIB),
    "mc_olly": (MEDIA / "S0864_s0864-ol1y.webp", "MAKES CENTS cover: ol1y (S0864)", LIB),
    "mc_proper": (MEDIA / "S0866_s0866-proper.webp", "MAKES CENTS cover: proper (S0866)", LIB),
    "mc_rees": (MEDIA / "S0867_s0867-rees.webp", "MAKES CENTS cover: David Rees (S0867)", LIB),
    "mc_reiss": (MEDIA / "S0868_s0868-reiss.webp", "MAKES CENTS cover: Steven Reiss (S0868)", LIB),
    "mc_sk": (MEDIA / "S0870_s0870-sk.webp", "MAKES CENTS cover: SK (S0870)", LIB),
    "one_year_1974": (WEB / "one-year-1974-four.webp", "Four Cents dated 1974, from close to mint state to marked (composite of CENTS images)", "Images: Rutherford Chang, CENTS"),
    "one_stamp": (WEB / "one-stamp-eight-decades.webp", "One stamp, eight decades: Cents from across the years (composite of CENTS images)", "Images: Rutherford Chang, CENTS"),
    "struck_1971": (WEB / "struck-alike-1971.webp", "Every Cent dated 1971 (composite of CENTS images)", "Images: Rutherford Chang, CENTS"),
    "mosaic": (WEB / "mosaic.webp", "All 10,000 Cents in number order (composite of CENTS images)", "Images: Rutherford Chang, CENTS"),
    "traits19": (WEB / "traits-19.webp", "The nineteen traits of the CENTS Trait Council (still from the web introduction)", "Images: Rutherford Chang; trait names: CENTS Trait Council"),
    "whitepaper": (WEB / "whitepaper.webp", "Satoshi Nakamoto's paper of 2008, section 2 (from bitcoin.org)", "bitcoin.org"),
    "die": (WEB / "die-2025.webp", "A die for the Lincoln cent of 2025", "United States Mint photograph, public domain"),
    "plaque": (WEB / "lincoln-plaque.webp", "Victor David Brenner's Lincoln plaque", "Princeton University Art Museum, free reuse"),
    "mempool": (WEB / "mempool.webp", "Bitcoin block 839,969 as shown by mempool.space", "mempool.space screenshot (web introduction)"),
    "coins_table": (WEB / "form-coins.webp", "Copper cents on a table at Chang's studio (web introduction image)", "Rutherford Chang, via the cents.gallery media library"),
}
CLIPS = {
    # id: (source, start s, length s, filter, subject, rights)
    "melt": (MELT, 0, None, None, "The cent sign of the web introduction melting into nothing (SVG rendered frame by frame)", "made for this film"),
    "pour": (MEDIA / "C029_c029-creation-of-the-cents-block-outdoor-molten-metal-pour-with-rutherford-chang-web.mp4", 2.0, 8.0, None,
             "Casting CENTS Block Copper: the outdoor pour (C029)", LIB),
    "model": (WEB / "block-model-slow.mp4", 0, 10.0, None, "The model of CENTS Block Copper turning (web introduction clip)", "Rutherford Chang, via the cents.gallery media library"),
}
CENTS = [1867, 9344, 4421, 6129, 2616, 478, 8462, 1264, 1328, 8820, 10000, 189, 9002, 9526, 6749, 4336, 1511, 5553, 219, 4273,
         9794, 1605, 3525, 1, 2, 3, 4, 5, 6, 7]

def sha1(p): return hashlib.sha1(open(p, "rb").read()).hexdigest()
assets = {}
for k, (src, subject, rights) in STILLS.items():
    if not src.exists(): sys.exit(f"missing source for {k}: {src}")
    im = Image.open(src).convert("RGB")
    im.thumbnail((1600, 1600), Image.LANCZOS)
    dst = OUT / f"{k}.jpg"
    im.save(dst, quality=88)
    assets[k] = {"path": f"public/assets/intro/{k}.jpg", "staged_as": f"intro/{k}.jpg", "sha1": sha1(dst), "bytes": dst.stat().st_size,
                 "width": im.width, "height": im.height, "motion": False, "kind": "real", "subject": subject, "source": str(src.name),
                 "rights": rights, "verified_at": "2026-11-27"}
for k, (src, ss, length, vf, subject, rights) in CLIPS.items():
    if not src.exists(): sys.exit(f"missing source for {k}: {src}")
    dst = OUT / f"{k}.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", str(src)] + (["-t", str(length)] if length else []) + \
          ["-an", "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18"] + (["-vf", vf] if vf else []) + [str(dst)]
    subprocess.run(cmd, check=True)
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height:format=duration", "-of", "json", str(dst)],
                        capture_output=True, text=True, check=True)
    j = json.loads(pr.stdout); st = j["streams"][0]
    assets[k] = {"path": f"public/assets/intro/{k}.mp4", "staged_as": f"intro/{k}.mp4", "sha1": sha1(dst), "bytes": dst.stat().st_size,
                 "width": st["width"], "height": st["height"], "motion": True, "duration": round(float(j["format"]["duration"]), 3),
                 "kind": "real", "subject": subject, "source": str(src.name), "rights": rights, "verified_at": "2026-11-27"}
# A still of the model, for the five-forms shot: frame 90 (3 s) of the model clip staged above.
ms = OUT / "model_still.jpg"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "3", "-i", str(OUT / "model.mp4"), "-frames:v", "1", "-q:v", "2", str(ms)], check=True)
im = Image.open(ms)
assets["model_still"] = {"path": "public/assets/intro/model_still.jpg", "staged_as": "intro/model_still.jpg", "sha1": sha1(ms), "bytes": ms.stat().st_size,
                         "width": im.width, "height": im.height, "motion": False, "kind": "real", "subject": "The model of CENTS Block Copper (frame at 3 s of the model clip)",
                         "source": "model.mp4", "rights": CLIPS["model"][5], "verified_at": "2026-11-27"}
# Reused from One Cent #189 (already staged there): the Trait Council's process document.
assets["trait_council"] = {**json.load(open(ROOT / "films/onecent-189/timeline/assets.json"))["assets"]["trait_council_s1075"],
                           "copied_from": "films/onecent-189/timeline/assets.json"}
for n in CENTS:
    dst = HI / f"{n}.webp"
    if not dst.exists():
        req = urllib.request.Request(f"https://cents.vision/pics/frontswebp/{n}.webp", headers={"User-Agent": "cents-video"})
        dst.write_bytes(urllib.request.urlopen(req, timeout=30).read())
    if Image.open(dst).size != (1050, 1050): sys.exit(f"front {n} is not 1050 px")
json.dump({"_what": "Pictures for the introduction film (stage_assets.py). Rights per item.", "assets": assets},
          open(F / "timeline/assets.json", "w"), indent=1)
print(len(assets), "assets;", len(CENTS), "fronts in public/hires")
