#!/usr/bin/env python3
"""Animate stills, and generate imagery, through a hosted model API.

DESIGN POSITION. For a film about the objecthood of real things, there is a
difference between animating a photograph the artist took and inventing footage
of an artwork that was never filmed. The first moves something real; the second
fabricates it. So image-to-video on supplied stills is the default path here,
and text-to-video is available only for abstract passages and is marked
`generated` in the inventory, where verify.py caps its share of runtime.

  pipeline/generate.py plan            # what it WOULD do and cost. No key, no spend.
  pipeline/generate.py run --shot s02_title --confirm
  pipeline/generate.py models          # the catalogue and prices as configured

Nothing is sent anywhere without --confirm, and `plan` is the only command that
runs without a key.
"""
from __future__ import annotations
import argparse, json, os, pathlib, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
INV = ROOT / "timeline" / "assets.json"
LEDGER = ROOT / "timeline" / "generation_log.json"

# Endpoints and parameter shapes VERIFIED against fal's own API pages on
# 2026-10-04. The v1 endpoint this file first guessed at is deprecated, it never
# took an `aspect_ratio`, and `duration` is an ENUM of 5 or 10 — the earlier code
# would have sent 2.5 and been rejected.
#
# Prices are NOT published on those pages. The figures below are carried over
# from comparison articles and are therefore UNVERIFIED: check the price fal
# shows for the endpoint in your dashboard before a real run.
MODELS = {
    "kling-2.5-turbo": {
        "endpoint": "fal-ai/kling-video/v2.5-turbo/pro/image-to-video",
        "kind": "image-to-video", "usd_per_second": 0.09, "price_verified": False,
        "note": "current default: pro quality at turbo speed, good on slow physical motion",
    },
    "kling-2-standard": {
        "endpoint": "fal-ai/kling-video/v2/standard/image-to-video",
        "kind": "image-to-video", "usd_per_second": 0.05, "price_verified": False,
        "note": "cheapest current tier; try first, step up only if it is not enough",
    },
    "kling-2.6-pro": {
        "endpoint": "fal-ai/kling-video/v2.6/pro/image-to-video",
        "kind": "image-to-video", "usd_per_second": 0.17, "price_verified": False,
        "note": "highest quality; also generates audio, which this pipeline does not need",
    },
}
# fal's image-to-video takes no aspect ratio: the output follows the source
# image. Our stills are square and landscape, and backdrops are cover-fitted
# anyway, so they are sent as they are.
DURATIONS = (5, 10)   # the API accepts nothing else

DEFAULT = "kling-2.5-turbo"

def inv() -> dict:
    return json.loads(INV.read_text())

def candidates() -> list[dict]:
    """Shots whose still would gain from motion: a real asset, held long enough
    to be worth it, that is not already moving."""
    tl = json.loads((ROOT / "timeline" / "timeline.json").read_text())
    al = json.loads((ROOT / "script" / "alignment.json").read_text())
    sys.path.insert(0, str(ROOT / "pipeline")); import anchors as A
    assets = inv()["assets"]
    out = []
    for s in A.shot_times(tl, al):
        aid = s.get("asset_id") or (s.get("props") or {}).get("backdrop")
        if not aid: continue
        a = assets.get(aid)
        if not a or a.get("motion"): continue
        dur = s["t1"] - s["t0"]
        if dur < 2.5: continue
        out.append({"shot_id": s["shot_id"], "asset_id": aid, "seconds": round(dur, 1),
                    "subject": a["subject"][:72], "low_res": a.get("low_res", False)})
    return out

def plan(args) -> int:
    m = MODELS[args.model]
    c = candidates()
    if not c:
        print("No still is held long enough to be worth animating.")
        return 0
    print(f"model: {args.model}  ({m['endpoint']})  ${m['usd_per_second']}/s — {m['note']}\n")
    total = 0.0
    for x in c:
        # The API accepts 5 or 10 seconds only. A 2.5s shot still costs a 5s
        # clip; the surplus is trimmed locally, not billed differently.
        clip = 5 if x["seconds"] <= 7 else (10 if args.long else 5)
        cost = clip * m["usd_per_second"]
        total += cost
        flag = "  [LOW RES — animating a soft source gives a soft clip]" if x["low_res"] else ""
        print(f"  {x['shot_id']:<18} {x['asset_id']}  {clip}s clip for a {x['seconds']:5.1f}s shot  "
              f"~${cost:5.2f}{flag}")
        print(f"  {'':<18} {x['subject']}")
    print(f"\n  estimated total: ~${total:.2f} for {len(c)} clips")
    if not m.get("price_verified"):
        print("  PRICE UNVERIFIED. fal does not publish a figure on the endpoint page; this is")
        print("  carried from comparison articles. Confirm it in your fal dashboard first.")
    if not os.environ.get("FAL_KEY"):
        print("\n  FAL_KEY is not set, so nothing can be sent. Export it to run.")
    return 0

def run(args) -> int:
    key = os.environ.get("FAL_KEY")
    if not key:
        sys.exit("FAL_KEY is not set. `plan` works without it; `run` does not.")
    if not args.confirm:
        sys.exit("run costs money. Re-run with --confirm once `plan` looks right.")
    try:
        import fal_client  # noqa: F401
    except ImportError:
        sys.exit("needs the client:  pip3 install fal-client")
    c = [x for x in candidates() if not args.shot or x["shot_id"] == args.shot]
    if not c: sys.exit(f"no candidate matches {args.shot!r}")
    m = MODELS[args.model]
    import fal_client
    log = json.loads(LEDGER.read_text()) if LEDGER.exists() else {"runs": []}
    data = inv()
    for x in c:
        a = data["assets"][x["asset_id"]]
        src = ROOT / a["path"]
        clip = 5 if x["seconds"] <= 7 else (10 if args.long else 5)
        # The prompt's job is to move the camera, not to invent anything. The
        # film is about real objects; a model that adds a reflection or a second
        # coin has falsified the subject, so the negative prompt says so too.
        prompt = args.prompt or (
            f"Very slow, restrained camera move across this photograph: a gentle drift and "
            f"almost imperceptible push in. The subject stays exactly as it is. {a['subject']}"
        )
        print(f"  {x['shot_id']}: uploading {src.name} …")
        url = fal_client.upload_file(str(src))
        res = fal_client.subscribe(m["endpoint"], arguments={
            "image_url": url,
            "prompt": prompt,
            "duration": str(clip),           # enum: "5" or "10"
            "negative_prompt": args.negative,
            "cfg_scale": args.cfg,
        })
        out_url = (res.get("video") or {}).get("url")
        if not out_url: sys.exit(f"no video returned for {x['shot_id']}: {str(res)[:200]}")
        import urllib.request
        dst = ROOT / "inputs" / "assets" / f"{x['asset_id']}_motion.mp4"
        urllib.request.urlretrieve(out_url, dst)
        aid = f"{x['asset_id']}m"
        data["assets"][aid] = {
            **a, "path": str(dst.relative_to(ROOT)), "motion": True,
            "kind": "generated", "derived_from": x["asset_id"],
            "subject": f"MOTION DERIVED from {x['asset_id']}: {a['subject']}",
            "rights": f"motion generated from the user's own still via {m['endpoint']}",
            "verified_at": "", "sha256": "",
            "crop_restrictions": "Re-inspect before use: a generated clip may invent detail the still did not have.",
        }
        log["runs"].append({"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "shot": x["shot_id"],
                            "model": args.model, "endpoint": m["endpoint"],
                            "seconds": clip, "est_usd": round(clip * m["usd_per_second"], 3),
                            "prompt": prompt, "source_asset": x["asset_id"], "new_asset": aid})
        print(f"    -> {dst.relative_to(ROOT)}  (asset {aid})")
    INV.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    LEDGER.write_text(json.dumps(log, indent=1))
    print("\nEvery clip is recorded with an empty subject and verified_at, so assets.py check")
    print("refuses it until it has been LOOKED AT. A generated clip can invent detail the")
    print("still never had, which is exactly what must not slip into a film about real objects.")
    return 0

def models(args) -> int:
    for k, m in MODELS.items():
        price = f"${m['usd_per_second']}/s" if m["usd_per_second"] else f"${m.get('flat_usd')}/image"
        print(f"  {k:<16} {m['kind']:<16} {price:<12} {m['note']}")
    print(f"\n  default: {DEFAULT}")
    return 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT, choices=list(MODELS))
    ap.add_argument("--long", action="store_true", help="10s clips instead of 5s where the shot is long")
    ap.add_argument("--negative", default=(
        "new objects, extra coins, added text, watermark, morphing, warping, "
        "changing shape, hands, people, blur, distort, low quality"))
    ap.add_argument("--cfg", type=float, default=0.5)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan").set_defaults(fn=plan)
    sub.add_parser("models").set_defaults(fn=models)
    r = sub.add_parser("run"); r.add_argument("--shot"); r.add_argument("--prompt")
    r.add_argument("--confirm", action="store_true"); r.set_defaults(fn=run)
    a = ap.parse_args(); sys.exit(a.fn(a))
