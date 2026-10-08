#!/usr/bin/env python3
"""Score stored reviewer verdicts against the adjudicated key."""
import json, pathlib, sys, importlib.util
H = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("key", H / "key.py")
k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
KEY = k.KEY

def main(tag="run1"):
    d = H / "runs" / tag
    recs = [json.loads(p.read_text()) for p in sorted(d.glob("*__*.json"))]
    assert recs, f"no run records in {d} - nothing to score"
    assert len(recs) == len(KEY), f"{len(recs)} records but {len(KEY)} key cells"

    per = {}
    for r in recs:
        cell = (r["relation"], r["case"], r["version"])
        assert cell in KEY, f"no key entry for {cell}"
        status, key_lines, _ = KEY[cell]
        v = r["verdict"]
        found = v and v["verdict"] == "FOUND"
        got = sorted({n for ins in (v["instances"] if found else []) for n in ins["lines"]})
        s = per.setdefault(r["relation"], {"hit": 0, "miss": 0, "fp": 0, "tn": 0,
                                           "arg_found": 0, "arg_none": 0, "wrong_place": []})
        if status == k.Q:
            s["arg_found" if found else "arg_none"] += 1
        elif status == k.P:
            if found and set(got) & set(key_lines): s["hit"] += 1
            elif found:
                s["miss"] += 1; s["wrong_place"].append(f"{r['case']}/{r['version']}: said {got}, key {key_lines}")
            else:
                s["miss"] += 1; s["wrong_place"].append(f"{r['case']}/{r['version']}: said NONE, key {key_lines}")
        else:
            s["fp" if found else "tn"] += 1

    print(f"SCORES  (run={tag})\n")
    verdicts = {}
    for rel in sorted(per):
        s = per[rel]
        P = s["hit"] + s["miss"]; A = s["fp"] + s["tn"]; Q = s["arg_found"] + s["arg_none"]
        rec = f"{s['hit']}/{P}" + (f" = {s['hit']/P:.2f}" if P else "  UNSCOREABLE: no present cells")
        pre = f"{s['tn']}/{A}" + (f" = {s['tn']/A:.2f}" if A else "  UNSCOREABLE: no absent cells")
        print(f"  {rel}")
        print(f"    recall    (present cells) {rec}")
        print(f"    precision (absent cells)  {pre}")
        print(f"    arguable cells            {Q} ({s['arg_found']} flagged, {s['arg_none']} silent)")
        for w in s["wrong_place"]:
            print(f"      MISS {w}")
        if P < 2 or A < 2:
            verdicts[rel] = "NOT SCOREABLE - too few decidable cells"
        elif s["hit"] / P >= 0.9 and s["tn"] / A >= 0.6:
            verdicts[rel] = "DEPLOYABLE"
        else:
            verdicts[rel] = "NOT DEPLOYABLE on this corpus"
        print(f"    -> {verdicts[rel]}\n")
    # Floor: a scoring pass that decided nothing must not print like a clean sweep.
    assert verdicts, "scored no relations at all"
    print("Thresholds declared before scoring: recall >= 0.90 AND precision >= 0.60,")
    print("and at least 2 decidable cells on each side. Arguable cells score neither way.")
    return 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
