#!/usr/bin/env python3
"""Find the lead for a Collector Wall episode: what about this Wall is most notable.

A Wall's lead is the quality the fewest other Walls share. Every quality here is
measured on every Wall on cents.vision (wallets joined into Walls the way
collectors.html joins them), so "the only Wall that ..." and "one of three" are
counts, not impressions. The artist wallet is a Wall like any other in the
counts, but it is never a rival in the wording: "the only collector" excludes it,
and the report says where it stands.

    python3 pipeline/wall_focus.py --snapshot /mnt/project-files/collectors/snapshots/2026-10-27 [--wall ScrappyT] [--top 6]
    python3 pipeline/wall_focus.py --snapshot ... --self-test

Qualities (each with a direction; "share" = how many Walls are at least as far):
  - trait coverage: how many of the 19 Traits Atlas traits the Wall holds
  - contamination coverage: how many of the 12 contamination types
  - full patinas: how many of the 5 full patinas
  - year span: distinct years held; the oldest year held
  - hoards: how many Cents of one scarce trait or value (pool <= 120) the Wall holds
  - 1/1 Years and 1/1 Mints (year or year+mint held by one Cent in all 10,000)
  - each Set the site counts (set-counts.php), by how many Walls hold it
  - size (number of Cents)
NO wallet address is printed: unclaimed Walls appear only as counts.
"""
import argparse, collections, json, sys
from pathlib import Path

GRADES = ("notable_", "significant_", "full_", "heavily_")
ATLAS = 19                      # Traits Atlas: 19 traits (films/traits)
SKIP = {"unique_id", "id", "inscription_number", "year", "mint_mark", "rare_sats"}
SET_NAMES = {"spectrum": "Spectrum Set", "fullSpectrum": "Full Spectrum Set", "patina": "Patina Set", "sig": "Patina Sig Set",
             "fulls": "Patina Fulls Set", "chronicle": "Chronicle Set", "fullMint": "Full Mint Set",
             "contaminationSet": "Contamination Set", "contaminationHoard": "Contamination Hoard",
             "contaminationFull": "Full Contamination Set", "threeDecades": "Three Decades Set", "allDecades": "All Decades Set"}


def traits(c: dict) -> set:
    """The Atlas traits a Cent carries, grades folded (full desert -> desert)."""
    s = set()
    for k, v in c.items():
        if k in SKIP or not v: continue
        for g in GRADES:
            if k.startswith(g): k = k[len(g):]
        s.add("fingerprint" if k == "fingerprints" else k)
    if c["year"] <= 1958: s.add("wheat")
    return s


def values(c: dict) -> set:
    """Finer values for hoards: graded traits as they are, plus each contamination type."""
    s = {k for k, v in c.items() if k not in SKIP and v is True}
    s |= {"contamination: " + t for t in (c.get("contaminated") or [])}
    if c["year"] <= 1958: s.add("wheat")
    return s


def load(snap: Path):
    meta = json.load(open(snap / "raw/merged-new2.json"))
    wi = json.load(open(snap / "raw/wallet_index_cents.json"))
    groups = json.load(open(snap / "raw/wallet-groups.json"))
    rp = json.load(open(snap / "replay.json"))
    sc = json.load(open(snap / "raw/set-counts.php"))
    # Walls: a group's primary absorbs its siblings, as collectors.html does.
    absorbed = {s for sib in groups.values() for s in sib}
    walls = {}
    for w, cents in wi.items():
        if w in absorbed: continue
        ids = list(cents) + [n for s in groups.get(w, []) for n in wi.get(s, [])]
        if ids: walls[w] = ids
    names = {r["wallet"]: r["name"] for r in rp["claimed"]}
    sets = {r["wallet"]: r["sets"] for r in rp["claimed"]}
    return meta, walls, names, sets, sc, rp


def measure(meta, walls):
    """Every quality on every Wall: {quality: {wall: value}} plus pool sizes."""
    year_n = collections.Counter(c["year"] for c in meta.values())
    ym_n = collections.Counter((c["year"], c["mint_mark"]) for c in meta.values())
    pool = collections.Counter(v for c in meta.values() for v in values(c))
    contam_all = {v for v in pool if v.startswith("contamination: ")}
    Q = collections.defaultdict(dict)
    for w, ids in walls.items():
        cs = [meta[str(n)] for n in ids]
        Q["traits"][w] = len(set().union(*(traits(c) for c in cs)))
        Q["contamination types"][w] = len({v for c in cs for v in values(c)} & contam_all)
        Q["full patinas"][w] = len({k for c in cs for k, v in c.items() if k.startswith("full_") and v})
        Q["years"][w] = len({c["year"] for c in cs})
        Q["oldest"][w] = -min(c["year"] for c in cs)            # higher is older
        Q["1/1 Years"][w] = sum(1 for c in cs if year_n[c["year"]] == 1)
        Q["1/1 Mints"][w] = sum(1 for c in cs if ym_n[(c["year"], c["mint_mark"])] == 1 and year_n[c["year"]] > 1)
        Q["size"][w] = len(cs)
        held = collections.Counter(v for c in cs for v in values(c))
        for v, k in held.items():
            if pool[v] <= 120: Q["hoard: " + v][w] = k
    return Q, pool, len(contam_all)


def rank(Q, w, artist):
    """For each quality the Wall has (value > 0): how many OTHER collectors' Walls are at least as far."""
    out = []
    for q, vals in Q.items():
        v = vals.get(w, 0)
        if v <= 0: continue
        rivals = [x for x, y in vals.items() if x not in (w, artist) and y >= v]
        out.append((len(rivals), q, v, artist in vals and vals[artist] >= v))
    return out


def phrase(q, v, n_rivals, artist_ties, pool, n_contam):
    """Worded as the count says: 'at least' when others tie or pass it, 'no other' when none do."""
    if q == "traits": what = f"{v} of the {ATLAS} Atlas traits"
    elif q == "contamination types": what = f"{v} of the {n_contam} contamination types"
    elif q == "full patinas": what = f"{v} of the 5 full patinas"
    elif q == "years": what = f"{v} different years"
    elif q == "oldest": what = f"a Cent from {-v} or earlier"
    elif q == "size": what = f"{v} Cents"
    elif q.startswith("hoard: "):
        t = q[7:]; what = f"{v} of the {pool[t]} {t.replace('_', ' ')} Cents"
    elif q.startswith("set: "): what = f"a {q[5:]}"
    else: what = f"{v} {q}"
    if q.startswith("set: ") or q == "oldest":
        lead = "no other collector holds" if n_rivals == 0 else f"one of {n_rivals + 1} collectors holding"
    else:
        lead = f"no other collector holds as many: {what}" if n_rivals == 0 else f"one of {n_rivals + 1} collectors with at least {what}"
        what = ""
    tie = " (the artist wallet does too)" if artist_ties else ""
    return f"{lead} {what}".strip() + tie


FAMILY = lambda q: "hoard" if q.startswith("hoard: ") else "set" if q.startswith("set: ") else \
    "coverage" if q in ("traits", "contamination types", "full patinas") else "1/1" if q.startswith("1/1") else "span" if q in ("years", "oldest") else "size"


def pick(rows, top):
    """The best few, but no family takes more than two places, so the editor sees the kinds of lead on offer."""
    out, per = [], collections.Counter()
    for r in rows:
        f = FAMILY(r[1])
        if per[f] >= 2: continue
        out.append(r); per[f] += 1
        if len(out) == top: break
    return out


def report(snap, only=None, top=6, quiet=False):
    meta, walls, names, sets, sc, rp = load(snap)
    if len(meta) != 10000: sys.exit(f"FLOOR: {len(meta)} Cents, want 10000")
    if len(walls) != sc["totalCollectors"]: sys.exit(f"FLOOR: {len(walls)} Walls, the site counts {sc['totalCollectors']}")
    if sum(len(v) for v in walls.values()) != 10000: sys.exit("FLOOR: the Walls do not hold exactly 10000 Cents")
    Q, pool, n_contam = measure(meta, walls)
    if max(Q["traits"].values()) > ATLAS: sys.exit(f"FLOOR: a Wall holds {max(Q['traits'].values())} traits, the Atlas has {ATLAS}")
    artist = next(w for w, n in names.items() if n == "Rutherford Chang")
    results = {}
    for w, name in names.items():
        if name == "Rutherford Chang" or (only and name != only): continue
        r = rank(Q, w, artist)
        # Sets come from the site's own counts; the artist wallet is subtracted where it holds the Set.
        for key, label in SET_NAMES.items():
            flag = {"fullSpectrum": "full_spectrum", "fullMint": "full_mint", "threeDecades": "three_decades",
                    "allDecades": "all_decades"}.get(key, key)
            s = sets.get(w, {})
            has = s.get(flag) if flag in s else None
            if key == "contaminationSet": has = (s.get("contamination_types") or 0) >= 4
            if key == "contaminationHoard": has = (s.get("contamination_types") or 0) >= 8
            if key == "contaminationFull": has = (s.get("contamination_types") or 0) >= 12
            if key in ("patina", "sig", "fulls"): has = s.get("patina_level") == {"patina": "notable", "sig": "significant", "fulls": "full"}[key]
            if not has: continue
            a = sets.get(artist, {})
            a_has = a.get(flag) if flag in a else False
            r.append((sc["counts"][key] - 1 - (1 if a_has else 0), "set: " + label, 1, bool(a_has)))
        r.sort(key=lambda x: (x[0], -x[2]))
        results[name] = [(n, q, v, phrase(q, v, n, at, pool, n_contam)) for n, q, v, at in pick(r, top)]
    if not quiet:
        for name, rows in results.items():
            print(f"\n{name}")
            for n, q, v, p in rows: print(f"  {n:4d} rivals  [{FAMILY(q)}] {p}")
    return results


def self_test(snap):
    res = report(snap, quiet=True)
    lead = res["ScrappyT"][0]
    assert lead[1] == "traits" and lead[0] == 0, f"ScrappyT's lead should be 19 of 19 traits with no rival, got {lead}"
    print("control green as it should be: ScrappyT leads with", lead[3])
    # Control that must go red: drop Wheat from the trait fold and ScrappyT is no longer alone.
    global traits
    keep = traits
    traits = lambda c: keep(c) - {"wheat"}
    try:
        lead2 = report(snap, only="ScrappyT", quiet=True)["ScrappyT"][0]
        if lead2[1] == "traits" and lead2[0] == 0 and lead2[2] == ATLAS:
            sys.exit("CONTROL FAILED: a broken trait fold still reports 19 of 19")
        print("control red as it should be: without Wheat the lead becomes:", lead2[3])
    finally:
        traits = keep


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, required=True)
    ap.add_argument("--wall"); ap.add_argument("--top", type=int, default=6)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    self_test(a.snapshot) if a.self_test else report(a.snapshot, a.wall, a.top)
