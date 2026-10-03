#!/usr/bin/env python3
"""Write manifest.json describing what actually shipped.

GENERATED, never hand-written: a hand-kept handoff drifts from the files it
describes. Every field here is read back off the exports and the source data,
and the gate results are recorded with their verdicts so "checks completed" and
"limitations" cannot be asserted without evidence.
"""
from __future__ import annotations
import datetime, hashlib, json, pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import verify as V

ROOT = pathlib.Path(__file__).resolve().parent.parent

def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def main() -> int:
    tl = json.loads((ROOT/"timeline"/"timeline.json").read_text())
    al = json.loads((ROOT/"script"/"alignment.json").read_text())
    clean, cap, ess = ROOT/"exports/clean.mp4", ROOT/"exports/captioned.mp4", ROOT/"review/essential.mp4"

    gates = {}
    for name, fn in [
        ("exports not stale", lambda: V.g_not_stale([clean, cap, ess])),
        ("visual mix",        V.g_visual_mix),
        ("real alignment",    V.g_fixture_not_shipped),
        ("captioned decodes", lambda: V.g_decodes(cap)),
        ("captioned format",  lambda: V.g_format(cap)),
        ("black tail",        lambda: V.g_black_tail(cap)),
        ("frozen tail",       lambda: V.g_frozen_tail(cap)),
        ("parity",            lambda: V.g_parity(clean, cap)),
        ("safe area",         lambda: V.g_safe_area(ess)),
        ("loudness",          lambda: V.g_loudness(cap)),
    ]:
        try: gates[name] = {"verdict": "pass", "detail": fn()}
        except Exception as e: gates[name] = {"verdict": "FAIL", "detail": str(e)}

    files = {}
    for p in (clean, cap):
        if p.exists():
            d = V.probe(p); v = next(s for s in d["streams"] if s["codec_type"]=="video")
            files[p.name] = {"sha256": sha256(p), "bytes": p.stat().st_size,
                             "duration_s": round(float(d["format"]["duration"]),3),
                             "frames": int(v.get("nb_frames") or 0),
                             "size": f"{v['width']}x{v['height']}", "fps": v["r_frame_rate"]}

    m = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "essay": tl["essay"],
        "timing_source": {"alignment_is_fixture": bool(al.get("_fixture")),
                          "model": al.get("model"), "audio": al.get("source_audio"),
                          "duration_s": al.get("duration"), "words": len(al.get("words", []))},
        "canvas": {"width": 1080, "height": 1920, "fps": 30},
        # Recorded so you can tell whether the ledger changed between videos.
        "ledger_sha256": sha256(ROOT/"LEDGER.md") if (ROOT/"LEDGER.md").exists() else None,
        "shots": [{"shot_id": s["shot_id"], "purpose": s["purpose"],
                   "visual_kind": s["visual_kind"], "component": s.get("component"),
                   "asset_id": s.get("asset_id"), "start": s["start"], "end": s["end"]}
                  for s in tl["shots"]],
        "exports": files,
        "gates": gates,
        "releasable": all(g["verdict"] == "pass" for g in gates.values()),
        "limitations": [k for k, g in gates.items() if g["verdict"] != "pass"],
    }
    (ROOT/"manifest.json").write_text(json.dumps(m, indent=1))
    print(f"manifest.json written — releasable: {m['releasable']}")
    if m["limitations"]: print("open: " + ", ".join(m["limitations"]))
    return 0

if __name__ == "__main__":
    sys.exit(main())
