import sys, json, numpy as np
"""Identify which Cents a diagram shows: match each coin blob against all 10,000
on-chain images. Trust a match only with a clear margin over the runner-up, and
check it against metadata.json. Usage: CENTS_SRC=<sovrn-onchain>/cents python3 -I pipeline/match_diagram.py <png>..."""
from PIL import Image, ImageFilter
from scipy import ndimage
import os
SRC=os.environ.get('CENTS_SRC','../sovrn-onchain/cents')+'/%d.webp'  # sovrn-onchain/cents
R=32
def vec(im):
    a=np.asarray(im.convert('RGB').resize((R,R),Image.LANCZOS),dtype=np.float32)
    yy,xx=np.mgrid[:R,:R]; m=((yy-R/2+.5)**2+(xx-R/2+.5)**2)<(R/2-1.5)**2
    v=a[m]; v=v-v.mean(0); return (v/ (np.linalg.norm(v)+1e-6)).ravel()
cache=os.environ.get('MATCH_CACHE','/tmp/lib32.npy')  # 32px vectors of all 10,000; ~2 min to build
try: LIB=np.load(cache)
except FileNotFoundError:
    vs=[]
    for n in range(1,10001):
        im=Image.open(SRC%n).convert('RGB'); g=im.convert('L').point(lambda v:255 if v<235 else 0).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))
        vs.append(vec(im.crop(g.getbbox())))
    LIB=np.stack(vs); np.save(cache,LIB)
out=[]
for path in sys.argv[1:]:
    im=Image.open(path).convert('RGB'); a=np.asarray(im.convert('L'))
    mask=a<225; mask=ndimage.binary_opening(mask,iterations=2); lab,k=ndimage.label(mask)
    for sl in ndimage.find_objects(lab):
        h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start
        if min(h,w)<60 or max(h,w)/min(h,w)>1.12: continue
        crop=im.crop((sl[1].start,sl[0].start,sl[1].stop,sl[0].stop))
        s=LIB@vec(crop); o=np.argsort(-s)[:2]
        out.append(dict(file=path.split('/')[-1],x=sl[1].start,y=sl[0].start,size=w,best=int(o[0])+1,score=round(float(s[o[0]]),3),runner=int(o[1])+1,runner_score=round(float(s[o[1]]),3)))
for r in sorted(out,key=lambda r:(r['file'],r['y']//100,r['x'])): print(r)
