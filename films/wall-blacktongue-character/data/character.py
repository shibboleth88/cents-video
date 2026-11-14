#!/usr/bin/env python3
"""Measure every claim the blacktongue "character" episode makes, from the dated snapshot.

    python3 films/wall-blacktongue-character/data/character.py            # writes character.json
    python3 films/wall-blacktongue-character/data/character.py --control  # must refuse (twice)

Walls are joined from the snapshot's wallets the way collectors.html joins them
(pipeline/wall_focus.load). "Collector" never includes the artist wallet; where the
artist wallet matches or beats the Wall, that is recorded, not hidden.

Each claim is a refusal: if the snapshot no longer supports the sentence, the script
stops and names the sentence. Counts that come back zero stop it too (a zero cannot
be told apart from a broken counter). The patina ladder (which Cent stands in which
cell) is defined here and checked here; the timeline reads it from character.json.
"""
import argparse, collections, csv, json, statistics, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pipeline"))
import wall_focus as wf  # noqa: E402

SNAP = Path("/mnt/project-files/collectors/snapshots/2026-11-14")
EXPORT_CSV = Path("/mnt/project-files/knowledge/data/cents_traits.csv")   # second source: Sep 2026 trait export
OUT = Path(__file__).resolve().parent / "character.json"
NAME = "blacktongue"
BASE = ["verdigris", "obsidian", "desert", "red"]
GRADES = ["notable", "significant", "full"]
GRADED = [f"{g}_{b}" for b in BASE for g in GRADES] + ["notable_gold", "full_gold"]
PATINA8 = ["verdigris", "obsidian", "desert", "red", "gold", "orange", "corroded", "iridescent"]
# The ladder: rows are patinas, columns notable / significant / full. One Cent per cell,
# each a different Cent, each carrying exactly that grade. Gold has no significant grade.
LADDER = [
    ("verdigris", [9840, 7476, 6054]),
    ("obsidian", [7395, 1935, 555]),
    ("desert", [3317, 8059, 5185]),
    ("red", [3217, 9684, 8185]),
    ("gold", [7449, None, 3231]),
]


class Refuse(SystemExit):
    pass


def need(ok, sentence, detail):
    if not ok:
        raise Refuse(f"REFUSE: the snapshot does not support: {sentence!r}\n  {detail}")


def measure(meta, walls, names, control=None):
    by_name = {n: w for w, n in names.items()}
    me, artist = by_name[NAME], by_name["Rutherford Chang"]
    if control == "plant":
        # Control: give another collector's Wall the two grades it lacks; "no other collector" must fail.
        rival = by_name["Plutonium F"]
        has = {k for n in walls[rival] for k in wf.values(meta[str(n)]) if k in GRADED}
        donors = [n for n in walls[me] if (wf.values(meta[str(n)]) & set(GRADED)) - has]
        walls = dict(walls); walls[rival] = list(walls[rival]) + donors
    vals = lambda n: wf.values(meta[str(n)])
    trs = lambda n: wf.traits(meta[str(n)])
    ids = walls[me]
    N = len(ids)
    need(N > 0, "the Wall holds Cents", "zero Cents")
    held = lambda w: {k for n in walls[w] for k in vals(n) if k in GRADED}
    mine = held(me)
    need(len(mine) == len(GRADED), "every grade of patina recorded in CENTS", f"holds {len(mine)} of {len(GRADED)}: missing {sorted(set(GRADED) - mine)}")
    rivals = sorted(((len(held(w)), names.get(w, "unclaimed"), len(walls[w])) for w in walls if w not in (me, artist)), reverse=True)
    need(rivals[0][0] < len(GRADED), "No other collector's Wall holds all fourteen", f"{rivals[0]} also holds all")
    best_other = rivals[0][0]
    need(len(held(artist)) == len(GRADED) and len(walls[artist]) == 1000, "the artist wallet, with a thousand Cents (holds all fourteen)",
         f"artist holds {len(held(artist))} grades, {len(walls[artist])} Cents")
    for nm, n_cents in (("CL7", None), ("Daidatep", None)):
        w = by_name[nm]
        need(len(held(w)) == 12 and len(walls[w]) > 100, f"Even CL7 and Daidatep, with more than a hundred Cents each, reach twelve",
             f"{nm}: {len(held(w))} grades, {len(walls[w])} Cents")
    need(best_other == 12, "reach twelve (the best any other collector reaches)", f"best other collector reaches {best_other}")

    # Ladder cells: each Cent on the Wall and carrying exactly that grade.
    used = set()
    for patina, cells in LADDER:
        for g, n in zip(GRADES, cells):
            if n is None:
                need(patina == "gold" and g == "significant", "gold, at notable and full", f"empty cell {patina}/{g}")
                continue
            need(n in ids, f"ladder {patina}/{g}: #{n} is on the Wall", "not on the Wall")
            need(meta[str(n)].get(f"{g}_{patina}") is True, f"ladder {patina}/{g}: #{n} carries {g} {patina}", f"#{n} values {sorted(vals(n))}")
            need(n not in used, f"ladder: #{n} once", "repeated"); used.add(n)

    kinds = {t for n in ids for t in trs(n) if t in PATINA8}
    need(kinds == set(PATINA8) - {"iridescent"}, "of the eight patinas, only iridescent is missing", f"holds {sorted(kinds)}")

    # Traits per Cent (visual traits, grades folded, wheat not counted), two sources.
    export = {int(r["cent"]): int(r["visual_trait_count"]) for r in csv.DictReader(open(EXPORT_CSV))}
    per_cent = {n: len(trs(n) - {"wheat"}) for n in ids}
    need(all(per_cent[n] == export[n] for n in ids), "traits per Cent (two sources agree)",
         f"disagree on {[n for n in ids if per_cent[n] != export[n]]}")
    tpc = lambda w: sum(len(trs(n) - {"wheat"}) for n in walls[w]) / len(walls[w])
    mine_tpc = tpc(me)
    big = [w for w in walls if len(walls[w]) >= 10]
    beat = [(round(tpc(w), 3), names.get(w, "unclaimed"), len(walls[w])) for w in big if w != me and tpc(w) >= mine_tpc]
    need(not beat, "Of the Walls with ten or more Cents, none carries more traits per Cent", f"matched or beaten by {beat}")
    need(round(mine_tpc, 1) == 2.4, "two point four on average", f"{mine_tpc:.3f}")
    pop = sum(export.values()) / len(export)
    need(pop < 1, "against under one across CENTS", f"population mean {pop:.3f}")
    runner_up = max(tpc(w) for w in big if w != me)

    # 3217: all four base patinas.
    need(set(BASE) <= trs(3217) and 3217 in ids and meta["3217"]["year"] == 1970, "Number 3217, from 1970, carries all four base patinas", sorted(trs(3217)))

    # Wear range.
    lus = [n for n in ids if "lustrous" in trs(n)]
    fac = [n for n in ids if "faceless" in trs(n)]
    need(2489 in lus and meta["2489"]["year"] == 1968, "close to mint state, as on number 2489", f"lustrous {lus}")
    need(len(fac) == 3, "three Faceless Cents", f"faceless {fac}")
    both = sorted(len(walls[w]) for w in walls if any("lustrous" in trs(n) for n in walls[w]) and any("faceless" in trs(n) for n in walls[w]))
    need(both and both[0] >= N, "No smaller Wall holds both", f"sizes of Walls holding both: {both[:5]}")

    # Decades.
    yrs = [meta[str(n)]["year"] for n in ids]
    dec = collections.Counter(f"{y // 10 * 10}s" for y in yrs)
    all_years = [c["year"] for c in meta.values()]
    pop60 = sum(1960 <= y < 1970 for y in all_years) / len(all_years)
    need(dec["1960s"] == 14 and pop60 < 0.2, "fourteen of the twenty-five are from the 1960s, against fewer than one in five", f"{dec['1960s']}, CENTS {pop60:.3f}")

    # Newest Cent, club, span.
    c7476 = meta["7476"]
    need(7476 in ids and c7476["year"] == 1976 and c7476.get("significant_verdigris") and c7476.get("notable_obsidian")
         and c7476.get("contaminated") == ["Obscure Adhesive"], "number 7476, from 1976 ... obscure adhesive", c7476)
    need(N == 25 and min(yrs) == 1938 and max(yrs) == 1980, "twenty-five Cents, from 1938 to 1980, Quarter Club", f"{N}, {min(yrs)}-{max(yrs)}")

    # Signature, Full Spectrum, wheat, contamination, corroded, ghost, vandalized.
    s = meta["5185"]
    need(s["year"] == 1968 and s.get("full_desert") and s.get("ghost"), "5185, 1968, full desert, Ghost", s)
    full_gold = sum(1 for c in meta.values() if c.get("full_gold"))
    need(full_gold == 9, "only nine Full Gold Cents", full_gold)
    y1938 = sum(1 for c in meta.values() if c["year"] == 1938)
    wheat = sorted(n for n in ids if meta[str(n)]["year"] <= 1958)
    need(y1938 == 2 and wheat == [7863, 8626] and meta["7863"]["year"] == 1958, "one of only two from 1938 ... with a Cent from 1958", (y1938, wheat))
    ctypes = sorted({t for n in ids for t in (meta[str(n)].get("contaminated") or [])})
    need(len(ctypes) == 4, "four of the twelve contamination types", ctypes)
    corr = lambda w: sum("corroded" in trs(n) for n in walls[w])
    corr_pool = sum(1 for c in meta.values() if c.get("corroded"))
    as_many = sorted((names.get(w, "unclaimed"), corr(w)) for w in walls if w not in (me, artist) and corr(w) >= corr(me))
    need(corr(me) == 4 and corr_pool == 69 and len(as_many) == 2, "four of the sixty-nine Corroded Cents; only two other collectors hold as many",
         (corr(me), corr_pool, as_many))
    ghosts = [n for n in ids if "ghost" in trs(n)]; vand = [n for n in ids if "vandalized" in trs(n)]
    need(len(ghosts) == 2 and len(vand) == 1, "Two are Ghost Cents, and one is Vandalized", (ghosts, vand))

    # The strips shot: which of the fourteen grades each named Wall holds, in GRADED order.
    strips = [{"name": nm if nm != "Rutherford Chang" else "Artist wallet", "cents": len(walls[by_name[nm]]),
               "held": [g in held(by_name[nm]) for g in GRADED]} for nm in (NAME, "CL7", "Daidatep", "Rutherford Chang")]
    need([sum(s["held"]) for s in strips] == [14, 12, 12, 14], "the strips: 14, 12, 12, 14", [sum(s["held"]) for s in strips])

    bins = collections.Counter(len(held(w)) for w in big)
    return {
        "_source": f"{SNAP} (fetched 2026-11-14 18:51-18:52Z); second source {EXPORT_CSV.name}",
        "as_of": "2026-11-14", "name": NAME, "count": N, "cents": sorted(ids),
        "ladder": [{"label": p, "cells": c} for p, c in LADDER],
        "grades_held": {"walls_10plus": len(big), "bins": [{"label": str(k), "count": bins.get(k, 0)} for k in range(0, len(GRADED) + 1)],
                        "best_other_collector": best_other, "rivals_top": rivals[:6], "artist": len(held(artist)),
                        "order": GRADED, "strips": strips},
        "traits_per_cent": {"wall": round(mine_tpc, 3), "runner_up_10plus": round(runner_up, 3), "population": round(pop, 3),
                            "per_cent": {str(n): per_cent[n] for n in sorted(ids)}},
        "wear": {"close_to_mint_state": lus, "faceless": fac, "smallest_walls_with_both": both[:3]},
        "decades": dict(sorted(dec.items())), "population_1960s_share": round(pop60, 4),
        "contamination_types": ctypes, "corroded": {"wall": corr(me), "pool": corr_pool, "collectors_as_many": as_many},
        "ghost": ghosts, "vandalized": vand, "wheat": wheat,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--control", action="store_true")
    a = ap.parse_args()
    meta, walls, names, sets, sc, rp = wf.load(SNAP)
    if a.control:
        reds = 0
        try:
            measure(meta, walls, names, control="plant")
        except Refuse as e:
            reds += 1; print("control 1 red as it should be:", str(e).splitlines()[0])
        bad = list(LADDER)
        LADDER[0] = ("verdigris", [7476, 9840, 6054])       # swap notable and significant
        try:
            measure(meta, walls, names)
        except Refuse as e:
            reds += 1; print("control 2 red as it should be:", str(e).splitlines()[0])
        LADDER[:] = bad
        sys.exit(0 if reds == 2 else f"CONTROLS: only {reds} of 2 went red")
    out = measure(meta, walls, names)
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"wrote {OUT.name}: {out['count']} Cents, grades 14/14 (best other collector {out['grades_held']['best_other_collector']}), "
          f"traits/Cent {out['traits_per_cent']['wall']} (next {out['traits_per_cent']['runner_up_10plus']}, CENTS {out['traits_per_cent']['population']})")


if __name__ == "__main__":
    main()
