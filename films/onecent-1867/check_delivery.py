"""Delivery checks on the rendered #1867 file (Collector Wall brief section 5, as run by hand for #10000):
format, decode end to end, first and last frame, black and frozen intervals set against the shot boundaries,
the closing turn's length, and the soundtrack against audio/vo.wav (best lag and correlation, with a control
shifted 0.5 s that must fall apart), plus integrated loudness.

    python3 -I films/onecent-1867/check_delivery.py <file.mp4>   (from the repo root)
"""
import json, re, subprocess, sys, pathlib
import numpy as np
F = pathlib.Path(__file__).resolve().parent
MP4 = pathlib.Path(sys.argv[1])
sh = lambda *a: subprocess.run(a, capture_output=True, text=True)

pr = json.loads(sh("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(MP4)).stdout)
v = next(s for s in pr["streams"] if s["codec_type"] == "video"); a = [s for s in pr["streams"] if s["codec_type"] == "audio"]
print(f"format: {v['codec_name']} {v['width']}x{v['height']} {v['r_frame_rate']} frames={v.get('nb_frames')} "
      f"duration={float(pr['format']['duration']):.2f} s audio={[x['codec_name'] for x in a]}")

dec = sh("ffmpeg", "-v", "error", "-i", str(MP4), "-f", "null", "-")
print(f"decode: {'clean' if not dec.stderr.strip() else 'ERRORS: ' + dec.stderr.strip()[:300]}")

def ymax(t):
    r = sh("ffmpeg", "-v", "info", "-ss", str(t), "-i", str(MP4), "-frames:v", "1", "-vf", "signalstats,metadata=print", "-f", "null", "-")
    m = re.search(r"YMAX=([0-9.]+)", r.stderr + r.stdout)
    return float(m.group(1)) if m else None
dur = float(pr["format"]["duration"])
print(f"first frame YMAX {ymax(0)}; last frame YMAX {ymax(dur - 1 / 30)}")

# shot boundaries, resolved as review_times.py does
al = json.load(open(F / "script/alignment.json")); tl = json.load(open(F / "timeline/timeline.json"))
W = al["words"]; norm = lambda s: re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("-", " ")).split()
flat = [(t, k) for k, w in enumerate(W) for t in norm(w["word"])]
def at(ph, end=False):
    n = norm(ph); hits = [k for k in range(len(flat) - len(n) + 1) if [x[0] for x in flat[k:k + len(n)]] == n]
    assert len(hits) == 1, (ph, len(hits))
    return W[flat[hits[0] + len(n) - 1][1]]["end"] if end else W[flat[hits[0]][1]]["start"]
def bound(b):
    if "at_start" in b: return 0.0
    if "at_end" in b: return al["duration"]
    if "at_phrase" in b: return at(b["at_phrase"])
    return at(b["after_phrase"], True) + b.get("plus", 0)
cuts = [bound(s["start"]) for s in tl["shots"]][1:]
joined = {round(bound(s["start"]), 2) for s in tl["shots"] if s.get("join_prev")}
close = next(s for s in tl["shots"] if s.get("props", {}).get("mode") == "close")
c0, c1 = bound(close["start"]), bound(close["end"])
print(f"closing card {c0:.2f} to {c1:.2f} s = {round((c1 - c0) * 30)} frames (turn needs 150)")

bl = sh("ffmpeg", "-v", "info", "-i", str(MP4), "-vf", "blackdetect=d=0.1:pix_th=0.10", "-an", "-f", "null", "-").stderr
blacks = [(float(x), float(y)) for x, y in re.findall(r"black_start:([0-9.]+) black_end:([0-9.]+)", bl)]
def near_cut(s, e): return any(s - 0.5 <= c <= e + 0.5 for c in cuts)
odd = [(s, e) for s, e in blacks if not near_cut(s, e) and e < dur - 0.3]
print(f"black runs: {len(blacks)}; at a shot boundary: {sum(near_cut(s, e) for s, e in blacks)}; "
      f"at the end: {sum(e >= dur - 0.3 for s, e in blacks)}; elsewhere: {odd}")
if blacks and blacks[0][0] < 0.05: print("  NOTE: black at frame 0")

fz = sh("ffmpeg", "-v", "info", "-i", str(MP4), "-vf", "freezedetect=n=0.003:d=2", "-an", "-f", "null", "-").stderr
st = [float(x) for x in re.findall(r"freeze_start: ([0-9.]+)", fz)]; en = [float(x) for x in re.findall(r"freeze_end: ([0-9.]+)", fz)]
en += [dur] * (len(st) - len(en))
print("frozen runs (2 s or more):", [(round(s, 2), round(e, 2), round(e - s, 2)) for s, e in zip(st, en)])

pcm = lambda src: np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-ac", "1", "-ar", "8000",
                                               "-f", "s16le", "-"], capture_output=True).stdout, np.int16).astype(float)
x, y = pcm(MP4), pcm(F / "audio/vo.wav")
n = min(len(x), len(y)); x, y = x[:n], y[:n]
def corr(lag):
    if lag >= 0: p, q = x[lag:], y[:n - lag]
    else: p, q = x[:n + lag], y[-lag:]
    return float(np.dot(p, q) / (np.linalg.norm(p) * np.linalg.norm(q) + 1e-9))
best = max(range(-400, 401, 8), key=corr)
print(f"audio vs audio/vo.wav: best lag {best / 8:.0f} ms, correlation {corr(best):.3f}; control shifted 0.5 s: {corr(best + 4000):.3f}")
lo = sh("ffmpeg", "-hide_banner", "-i", str(MP4), "-af", "ebur128", "-f", "null", "-").stderr
m = re.findall(r"I:\s+(-?[0-9.]+) LUFS", lo)
print(f"integrated loudness {m[-1] if m else '?'} LUFS")
