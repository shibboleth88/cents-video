import sys, os, numpy as np
from multiprocessing import Pool
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from feat import candidate_discs, crop64, raw16
SRC = sys.argv[1]; OUT = sys.argv[2]
def one(n):
    im = Image.open(os.path.join(SRC, f'{n}.webp')).convert('RGB')
    d = candidate_discs(im)[0]
    return raw16(crop64(im, d)).astype(np.uint8), d
if __name__ == '__main__':
    with Pool(4) as p: res = p.map(one, range(1, 10001), chunksize=50)
    raw = np.array([r[0] for r in res]); discs = np.array([r[1] for r in res])
    np.savez(OUT, raw=raw, discs=discs)
    rr = discs[:, 2] / 300
    print('raw', raw.shape, 'disc r/w min %.3f max %.3f' % (rr.min(), rr.max()))
