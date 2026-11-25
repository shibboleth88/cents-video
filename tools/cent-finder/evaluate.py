import sys, os, glob, io, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0, os.path.dirname(__file__))
from feat import candidate_discs, crop64, raw16, chan_norm, finish, ROTS
idx = np.load(sys.argv[1]); QDIR = sys.argv[2]; PCA_K = int(sys.argv[3]) if len(sys.argv) > 3 else 0
NV = np.array([chan_norm(r.astype(np.float32)) for r in idx['raw']])
MEAN = NV.mean(0)
IDX = np.array([finish(v, MEAN) for v in NV]).astype(np.float32)
if PCA_K:
    U, S, Vt = np.linalg.svd(IDX - IDX.mean(0), full_matrices=False)
    P = Vt[:PCA_K].astype(np.float32); MU = IDX.mean(0)
    def proj(X): Y = (X - MU) @ P.T; return Y / np.linalg.norm(Y, axis=-1, keepdims=True)
    IDXP = proj(IDX)
    # int8 quantisation as it would ship
    sc = np.abs(IDXP).max(); IDXP = np.round(IDXP / sc * 127).astype(np.int8).astype(np.float32); IDXP /= np.linalg.norm(IDXP, axis=1, keepdims=True)
else:
    proj = lambda X: X; IDXP = IDX

def variants(im):
    out = {'orig': im}
    b = io.BytesIO(); im.resize((400, 400)).save(b, 'JPEG', quality=25); out['jpeg25_400'] = Image.open(io.BytesIO(b.getvalue())).convert('RGB')
    out['tiny120'] = im.resize((120, 120), Image.BILINEAR)
    sc = Image.new('RGB', (1170, 2532), (18, 18, 20)); d = ImageDraw.Draw(sc)
    d.rectangle((0, 0, 1170, 180), fill=(40, 40, 46)); d.rectangle((60, 1900, 1110, 1990), fill=(90, 60, 200)); d.text((80, 1500), 'CENT #???? 1964', fill=(230, 230, 230))
    sc.paste(im.resize((900, 900)), (100, 400)); out['screenshot_dark'] = sc
    sl = Image.new('RGB', (1400, 900), (250, 250, 250)); d = ImageDraw.Draw(sl)
    d.rectangle((0, 0, 1400, 70), fill=(30, 30, 30)); d.rectangle((760, 200, 1340, 260), fill=(220, 220, 225)); d.text((780, 300), 'Lincoln cent 1964', fill=(20, 20, 20))
    sl.paste(im.resize((640, 640)), (60, 150)); out['screenshot_light'] = sl
    w, h = im.size; out['tight_crop'] = im.crop((int(w*.16), int(h*.16), int(w*.84), int(h*.84)))
    out['rot4'] = im.rotate(4, resample=Image.BICUBIC, fillcolor=(255, 255, 255))
    ph = ImageEnhance.Brightness(im).enhance(0.8); ph = ImageEnhance.Color(ph).enhance(1.3)
    r, g, bb = ph.split(); r = r.point(lambda v: min(255, v*1.08)); bb = bb.point(lambda v: v*0.9)
    ph = Image.merge('RGB', (r, g, bb)).filter(ImageFilter.GaussianBlur(2.5)); out['phone_cast_blur'] = ph
    ph2 = ph.rotate(-3, resample=Image.BICUBIC, fillcolor=(235, 228, 215)); b = io.BytesIO(); ph2.save(b, 'JPEG', quality=40); out['phone_all'] = Image.open(io.BytesIO(b.getvalue())).convert('RGB')
    a = np.asarray(im).copy(); m = (a.astype(int).sum(2) > 700); a[m] = 0; out['black_bg'] = Image.fromarray(a)
    return out

def query(im):
    vs = []
    for disc in candidate_discs(im):
        for rot in ROTS:
            vs.append(finish(chan_norm(raw16(crop64(im, disc, rot))), MEAN))
    Q = proj(np.array(vs, dtype=np.float32))
    S = Q @ IDXP.T                     # (ncand, 10000)
    return S.max(0)                    # best over candidates, per Cent

files = sorted(glob.glob(os.path.join(QDIR, '*.webp')) + glob.glob(os.path.join(QDIR, '*.jpg')), key=lambda f: int(os.path.basename(f).split('.')[0]))
stats = {}
for f in files:
    n = int(os.path.basename(f).split('.')[0]); t = n - 1
    im = Image.open(f).convert('RGB')
    for name, v in variants(im).items():
        s = query(v); order = np.argsort(-s)
        st = stats.setdefault(name, {'r1': 0, 'r3': 0, 'true': [], 'gap': [], 'loo': [], 'loogap': [], 'fails': []})
        st['r1'] += int(order[0] == t); st['r3'] += int(t in order[:3])
        if order[0] != t: st['fails'].append((n, int(order[0])+1, round(float(s[t]), 3), round(float(s[order[0]]), 3)))
        st['true'].append(s[t])
        o = s.copy(); o[t] = -9; oo = np.sort(o)[::-1]
        st['loo'].append(oo[0]); st['loogap'].append(oo[0] - oo[1])
        if order[0] == t: st['gap'].append(s[t] - s[order[1]])
        g1 = s[order[0]] - s[order[1]]
        conf = s[order[0]] >= 0.86 and g1 >= 0.08
        st.setdefault('conf_ok', 0); st.setdefault('conf_wrong', 0); st.setdefault('conf_fp', 0)
        st['conf_ok'] += int(conf and order[0] == t); st['conf_wrong'] += int(conf and order[0] != t)
        st['conf_fp'] += int(oo[0] >= 0.86 and st['loogap'][-1] >= 0.08)
N = len(files)
print(f'{N} queries | PCA {PCA_K or "off"}')
print(f"{'variant':17s} rank1  top3 | true score min/med | gap(true-2nd) min | no-true: best min/med/max  gap max")
for name, st in stats.items():
    print(f"{name:17s} {st['r1']:2d}/{N} {st['r3']:2d}/{N} | {min(st['true']):.3f} {np.median(st['true']):.3f} | {min(st['gap']) if st['gap'] else float('nan'):.3f} | {min(st['loo']):.3f} {np.median(st['loo']):.3f} {max(st['loo']):.3f}  {max(st['loogap']):.3f}  {st['fails'][:3]} | MATCH-rule: correct {st['conf_ok']} wrong {st['conf_wrong']} false-when-absent {st['conf_fp']}")
