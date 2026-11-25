"""Write the Cent Finder page's data files from the index and the trait export.
usage: python3 make_site.py <idx.npz> <sovrn-onchain/cents dir> <traits json> <sample image> <out dir>
"""
import sys, os, json, numpy as np
from PIL import Image
idx_npz, cents_dir, traits_json, sample, out = sys.argv[1:6]
os.makedirs(os.path.join(out, 'thumbs'), exist_ok=True)
raw = np.load(idx_npz)['raw']; assert raw.shape == (10000, 148, 3) and raw.dtype == np.uint8
Image.fromarray(raw, 'RGB').save(os.path.join(out, 'index.png'), optimize=True)
print('index.png checksum (put in cent-finder.html):', int(raw.astype(np.int64).sum()))
d = json.load(open(traits_json))
skip = {'unique_id', 'year', 'mint_mark', 'id', 'inscription_number', 'contaminated', 'rare_sats'}
names = sorted({k for v in d.values() for k, x in v.items() if k not in skip and x is True})
rows = []
for n in range(1, 10001):
    v = d[str(n)]
    mask = sum(1 << i for i, k in enumerate(names) if v.get(k) is True)
    rows.append([v['year'], v.get('mint_mark') or '', mask, ';'.join(v.get('contaminated') or []), v.get('inscription_number') or 0])
json.dump({'traits': names, 'cents': rows}, open(os.path.join(out, 'cents.json'), 'w'), separators=(',', ':'))
C = 120   # 100 sprite sheets of 10 x 10 Cents
for k in range(100):
    sheet = Image.new('RGB', (C * 10, C * 10), (255, 255, 255))
    for j in range(100):
        im = Image.open(os.path.join(cents_dir, f'{k*100+j+1}.webp')).convert('RGB').resize((C, C), Image.LANCZOS)
        sheet.paste(im, ((j % 10) * C, (j // 10) * C))
    sheet.save(os.path.join(out, 'thumbs', f's{k:02d}.webp'), 'WEBP', quality=72, method=6)
Image.open(sample).convert('RGB').resize((480, 480), Image.LANCZOS).save(os.path.join(out, 'sample.jpg'), quality=84)
print('wrote', out)
