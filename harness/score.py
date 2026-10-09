#!/usr/bin/env python3
"""Score stored reviewer verdicts against the adjudicated key, by majority vote
across repeated samples of each cell.

Why majority rather than a single sample: two independent samples of the same 33
cells agreed on 27 of them. A one-cell difference in recall - which is the size
of most changes worth detecting here - is inside that noise, so single-sample
comparisons are uninterpretable. Repeating each cell an odd number of times and
scoring the majority makes a flip something measured instead of something
mistaken for an effect.

The vote is over OUTCOMES, not verdicts. A cell where two reps say FOUND at the
wrong lines and one says FOUND at the right lines is a majority `wrong_place`,
not a hit; voting on the verdict alone would have scored it as a hit.

Three states that a single number would render identically, kept apart:
  - stable      : every valid rep agreed
  - unstable    : reps disagreed (reported individually, with the split)
  - unmeasured  : only one valid rep, so stability was never tested
"""
import collections, importlib.util, json, pathlib, sys

H = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("key", H / "key.py")
k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
KEY = k.KEY

def outcome(status, key_lines, v):
    """Classify one rep. Returns a label in the vocabulary of its cell's status."""
    found = v["verdict"] == "FOUND"
    lines = {n for ins in v["instances"] for n in ins["lines"]} if found else set()
    if status == k.Q:
        return "flagged" if found else "quiet"
    if status == k.P:
        if not found: return "silent"
        return "hit" if lines & set(key_lines) else "wrong_place"
    return "fp" if found else "tn"

def main(tag="run3"):
    d = H / "runs" / tag
    recs = [json.loads(p.read_text()) for p in sorted(d.glob("*__*.json"))]
    assert recs, f"no run records in {d} - nothing to score"

    cells = collections.defaultdict(list)
    skipped, malformed = [], []
    for r in recs:
        cell = (r["relation"], r["case"], r["version"])
        if cell not in KEY:
            skipped.append("/".join(cell)); continue
        if r["malformed"]:
            malformed.append("/".join(cell) + f" r{r.get('rep','?')} -> {r['malformed']}")
            continue
        cells[cell].append(r)

    per = collections.defaultdict(lambda: collections.Counter())
    detail = collections.defaultdict(list)
    for cell, reps in sorted(cells.items()):
        rel = cell[0]
        status, key_lines, _ = KEY[cell]
        outs = [outcome(status, key_lines, r["verdict"]) for r in reps]
        tally = collections.Counter(outs)
        top, n = tally.most_common(1)[0]
        tied = sum(1 for o, c in tally.items() if c == n) > 1
        # Stability is a separate fact from correctness and must not be inferred
        # from it: a cell can be unanimously wrong, or right by one vote of three.
        if len(reps) < 2:
            per[rel]["unmeasured"] += 1
        elif len(set(r["verdict"]["verdict"] for r in reps)) == 1 and len(tally) == 1:
            per[rel]["stable"] += 1
        else:
            per[rel]["unstable"] += 1
            detail[rel].append(f"{cell[1]}/{cell[2]}: " + ", ".join(f"{o}x{c}" for o, c in tally.most_common()))
        if tied:
            per[rel]["tie"] += 1
            detail[rel].append(f"{cell[1]}/{cell[2]}: TIE, not scored - " +
                               ", ".join(f"{o}x{c}" for o, c in tally.most_common()))
            continue
        per[rel][top] += 1
        if status == k.P and top != "hit":
            detail[rel].append(f"MISS {cell[1]}/{cell[2]}: majority {top} ({n}/{len(reps)}), key {key_lines}")
        if status == k.A and top == "fp":
            detail[rel].append(f"FP   {cell[1]}/{cell[2]}: majority fp ({n}/{len(reps)})")
        if len(reps) < 2:
            detail[rel].append(f"NOTE {cell[1]}/{cell[2]}: only 1 rep - stability untested")

    reps_per = collections.Counter(len(v) for v in cells.values())
    print(f"SCORES  (run={tag})")
    print(f"  {len(cells)}/{len(KEY)} key cells covered; {len(recs)} records; "
          f"{len(skipped)} outside this key; {len(malformed)} malformed")
    print(f"  reps per cell: " + ", ".join(f"{n} rep(s) x{c} cells" for n, c in sorted(reps_per.items())))
    for m in malformed: print(f"    MALFORMED {m}")
    assert cells, "no records matched any key cell - nothing was scored"
    print()

    for rel in sorted(per):
        s = per[rel]
        P = s["hit"] + s["wrong_place"] + s["silent"]
        A = s["tn"] + s["fp"]
        stab_n = s["stable"] + s["unstable"]
        print(f"  {rel}")
        print(f"    recall    (present cells) {s['hit']}/{P}" + (f" = {s['hit']/P:.2f}" if P else "  NO PRESENT CELLS"))
        print(f"    precision (absent cells)  {s['tn']}/{A}" + (f" = {s['tn']/A:.2f}" if A else "  NO ABSENT CELLS"))
        print(f"    stability                 " + (
              f"{s['stable']}/{stab_n} cells unanimous = {s['stable']/stab_n:.2f}" if stab_n
              else "UNMEASURED - every cell has a single rep"))
        if s["unmeasured"]: print(f"      {s['unmeasured']} cell(s) with 1 rep: stability untested")
        if s["tie"]:        print(f"      {s['tie']} tied cell(s) excluded from scoring")
        for line in detail[rel]: print(f"      {line}")
        if P < 2 or A < 2:
            v = "NOT SCOREABLE - too few decidable cells"
        elif not stab_n:
            v = "NOT SCOREABLE - stability untested; repeat each cell"
        elif s["stable"] / stab_n < 0.9:
            v = f"NOT DEPLOYABLE - unstable ({s['stable']}/{stab_n} unanimous)"
        elif s["hit"] / P >= 0.9 and s["tn"] / A >= 0.6:
            v = "DEPLOYABLE"
        else:
            v = "NOT DEPLOYABLE on this corpus"
        print(f"    -> {v}\n")
    print("Thresholds declared before scoring: recall >= 0.90, precision >= 0.60,")
    print("stability >= 0.90 unanimous, and at least 2 decidable cells on each side.")
    print("Arguable cells score neither way; tied cells are excluded and reported.")
    return 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
