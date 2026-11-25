"""Cent finder v2: candidate discs + rotation search + colour-cast-robust colour fingerprint."""
import numpy as np
from PIL import Image

WORK = 200; THR = 40

def _components(mask):
    h, w = mask.shape; lab = np.zeros((h, w), np.int32); comps = []; cur = 0
    for y0, x0 in zip(*np.nonzero(mask)):
        if lab[y0, x0]: continue
        cur += 1; stack = [(y0, x0)]; lab[y0, x0] = cur; n = 0; y1 = y2 = y0; x1 = x2 = x0
        while stack:
            y, x = stack.pop(); n += 1
            if y < y1: y1 = y
            if y > y2: y2 = y
            if x < x1: x1 = x
            if x > x2: x2 = x
            for yy, xx in ((y+1, x), (y-1, x), (y, x+1), (y, x-1)):
                if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = cur; stack.append((yy, xx))
        comps.append((n, x1, y1, x2, y2))
    return comps

def candidate_discs(im, depth=0, offset=(0, 0)):
    """List of (cx, cy, r) in original-image pixels."""
    W, H = im.size; s = WORK / max(W, H)
    sm = np.asarray(im.convert('RGB').resize((max(1, round(W*s)), max(1, round(H*s))), Image.BILINEAR), dtype=np.int16)
    h, w, _ = sm.shape
    bg = np.median(np.concatenate([sm[0], sm[-1], sm[:, 0], sm[:, -1]]), axis=0)
    mask = np.abs(sm - bg).sum(axis=2) > THR
    out = []
    comps = sorted(_components(mask), reverse=True)[:6]
    for n, x1, y1, x2, y2 in comps:
        bw, bh = x2 - x1 + 1, y2 - y1 + 1
        if n < 0.01 * h * w or min(bw, bh) < 12: continue
        aspect = bw / bh; fill = n / (bw * bh)
        cx = (x1 + x2 + 1) / 2 / s + offset[0]; cy = (y1 + y2 + 1) / 2 / s + offset[1]
        if 0.85 <= aspect <= 1.18 and 0.6 <= fill <= 0.9:
            out.append((cx, cy, max(bw, bh) / 2 / s))
        elif fill > 0.9 and depth < 2:
            # a filled rectangle (an image pasted on a page): look inside it
            m = int(np.ceil(1.5 / s))   # step inside the rectangle so its border is not the page
            box = (int(x1/s) + m, int(y1/s) + m, int((x2+1)/s) - m, int((y2+1)/s) - m)
            out += candidate_discs(im.crop(box), depth+1, (offset[0]+box[0], offset[1]+box[1]))
    if depth == 0:
        r0 = min(W, H) / 2
        # oversize circles only when no coin outline was found (a crop tighter than the coin)
        for k in (1.0, 1.15, 1.3, 1.45):
            out.append((W/2, H/2, r0 * k))
    return out

ROTS = (0, -5, 5, -10, 10)
_yy, _xx = np.mgrid[0:16, 0:16]
CIRC16 = ((_xx - 7.5)**2 + (_yy - 7.5)**2) <= (7.5*0.92)**2

def crop64(im, disc, rot=0):
    cx, cy, r = disc
    box = tuple(int(round(v)) for v in (cx - r, cy - r, cx + r, cy + r))
    c = im.convert('RGB').crop(box).resize((64, 64), Image.BILINEAR)
    if rot: c = c.rotate(rot, resample=Image.BILINEAR)
    return c

def raw16(c64):
    a = np.asarray(c64.resize((16, 16), Image.BOX), dtype=np.float32)
    return a[CIRC16]           # (npix, 3)

def chan_norm(px):
    """Per-channel z-score: removes brightness, contrast and colour cast."""
    return ((px - px.mean(0)) / (px.std(0) + 1e-3)).flatten()

def finish(v, mean):
    v = v - mean
    return v / (np.linalg.norm(v) + 1e-9)
