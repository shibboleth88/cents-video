"""STAND-IN for the 3DCENTS turn, for the silent rehearsal only. Not a 3DCENTS render.

The user's export cent-10000-360-1080x1920-25fps-reel.mp4 was not yet in "cents shortlist" on 2026-11-21.
This draws a flat 2D turn of the real 1050 px photos (front, back, front; 150 frames at 30 fps; coin 776 px
across at the centre of 1080x1920, on black, as the 3DCENTS exports are measured), with "STAND-IN" written
across it so no still can be mistaken for the real turn. The timeline points at it by a name containing
STANDIN, and the render refuses while any shot does (see README, Build).

    python3 -I films/onecent-10000/script/make_standin_spin.py <front.webp> <back.webp> <out.mp4>
"""
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
front, back, out = sys.argv[1:4]
D = 776; S = round(D / 0.80)                       # cents.vision photos: coin radius 0.40 of the square
imgs = [Image.open(p).convert("RGB").resize((S, S), Image.LANCZOS) for p in (front, back)]
mask = Image.new("L", (S, S), 0); ImageDraw.Draw(mask).ellipse(((S - D) // 2, (S - D) // 2, (S + D) // 2, (S + D) // 2), fill=255)
font = ImageFont.load_default(size=72)
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", "30",
                       "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], stdin=subprocess.PIPE)
for f in range(150):
    th = 2 * math.pi * f / 150
    sx = max(0.02, abs(math.cos(th)))
    im = imgs[0] if math.cos(th) >= 0 else imgs[1]
    w = max(2, round(S * sx))
    coin = im.resize((w, S)); m = mask.resize((w, S))
    fr = Image.new("RGB", (1080, 1920), (0, 0, 0))
    fr.paste(coin, (540 - w // 2, 960 - S // 2), m)
    ImageDraw.Draw(fr).text((540, 1500), "STAND-IN", fill=(255, 60, 60), font=font, anchor="mm")
    ff.stdin.write(fr.tobytes())
ff.stdin.close(); ff.wait()
print("wrote", out)
