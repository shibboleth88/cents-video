#!/usr/bin/env python3
"""Mine the collection and the Walls for things collectors may not already know.

wall_focus.py answers one question: which of a Wall's qualities the fewest other
Walls share. This script asks wider ones, through eight lenses, and gives every
finding the same three fields so they can be ranked against each other:

  p        how likely the finding is by chance (hypergeometric tail, or the share
           of Walls that match); bits = -log2(p), so higher is more surprising
  on_site  whether cents.vision already shows it on a Wall card or Set badge.
           A finding the site shows is "known"; the rest are the candidates for
           "something the community may not have seen".
  cents    the Cent numbers that make it true, so any finding can be checked
           by eye on cents.vision

Collection lenses (Cents only, no Walls):
  pairs     traits that never meet, or meet far more than chance (19 Atlas traits + mint marks)
  era       traits whose Cents are much older or newer than the collection as a whole
  extremes  the oldest / newest Cent of each trait, the only one in its mint mark,
            the most traits on one Cent, more than one Full grade on one Cent
Wall lenses (claimed Walls by name; unclaimed Walls only ever as counts):
  share     a Wall holds a trait many times more than its size predicts
  grip      one Wall holds a large share of a whole trait pool
  nearmiss  a Wall is one Cent away from a Set or from complete coverage
  smallyear a Wall holds several Cents of a year that has very few
  pair      the only Wall that holds both of two scarce values
  holders   who holds each extreme Cent found by the collection lenses

    python3 pipeline/stories.py --snapshot /mnt/project-files/collectors/snapshots/2026-10-27 [--wall ScrappyT] [--json out.json]
    python3 pipeline/stories.py --snapshot ... --self-test

The artist wallet counts in pools and rivals but is never "a collector":
"the only collector" excludes it and the finding says where it stands.
NO wallet address is printed. Rare sats are left out (they stay out of public copy).
A finding is a lead to check, not a line of narration: the "why" (intention,
cause) is never in the data. Never imply Chang chose a Cent for a trait.
"""
import argparse, collections, json, math, random, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from wall_focus import ATLAS, load, traits, values  # same Wall join, same trait fold

N = 10000
PATINAS = ("verdigris", "obsidian", "red", "desert")
ATLAS_DIR = Path(__file__).parent.parent / "films/traits/script/atlas"


# ---------- statistics ----------
def lchoose(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def hyper_ge(k, N_, K, n):
    """P(X >= k) for X ~ Hypergeometric(population N_, K successes, n draws)."""
    hi = min(K, n)
    if k <= 0: return 1.0
    if k > hi: return 0.0
    base = lchoose(N_, n)
    return min(1.0, sum(math.exp(lchoose(K, i) + lchoose(N_ - K, n - i) - base) for i in range(k, hi + 1)))


def hyper_le(k, N_, K, n):
    lo = max(0, n - (N_ - K))
    if k < lo: return 0.0
    base = lchoose(N_, n)
    return min(1.0, sum(math.exp(lchoose(K, i) + lchoose(N_ - K, n - i) - base) for i in range(lo, k + 1)))


def bits(p):
    return round(-math.log2(max(p, 1e-300)), 1)


def F(lens, subject, claim, p, cents, on_site=False, **kw):
    return dict(lens=lens, subject=subject, claim=claim, p=p, bits=bits(p), on_site=on_site,
                cents=sorted(cents)[:40], n_cents=len(cents), **kw)


# ---------- the Cents ----------
def label(t):
    return t.replace("_", " ")


def cent_features(c):
    """Atlas traits (grades folded) plus mint marks: the vocabulary of the pairs lens."""
    s = traits(c)
    s.add("mint: " + (c["mint_mark"] or "none"))
    return s


def atlas_mentions(a, b):
    """Does either Atlas entry name the other trait? Then an exclusion may be by definition."""
    def text(t):
        f = ATLAS_DIR / (t.replace("_", "-").replace("fingerprints", "fingerprint") + ".txt")
        return f.read_text().lower() if f.exists() else ""
    ta, tb = text(a), text(b)
    return bool(re.search(r"\b" + re.escape(label(b).split()[0]), ta) or re.search(r"\b" + re.escape(label(a).split()[0]), tb))


def lens_pairs(meta):
    feats = {n: cent_features(c) for n, c in meta.items()}
    pool = collections.defaultdict(set)
    for n, fs in feats.items():
        for f in fs: pool[f].add(n)
    keys = sorted(k for k in pool if len(pool[k]) >= 15 and k != "mint: none")
    out, tests = [], 0
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if a.startswith("mint: ") and b.startswith("mint: "): continue
            A, B = pool[a], pool[b]
            both = A & B
            exp = len(A) * len(B) / N
            tests += 1
            if not both and exp >= 3:
                p = hyper_le(0, N, len(A), len(B))
                defn = atlas_mentions(a, b)
                out.append(F("pairs", "collection",
                             f"No Cent is both {label(a)} and {label(b)} ({len(A)} and {len(B)} Cents; about {exp:.0f} would overlap by chance)"
                             + (" [an Atlas entry names the other trait: may be by definition, check]" if defn else ""),
                             p, [], expected=round(exp, 1), observed=0, definitional_hint=defn))
            elif len(both) >= 3 and len(both) / exp >= 3:
                p = hyper_ge(len(both), N, len(A), len(B))
                out.append(F("pairs", "collection",
                             f"{len(both)} Cents are both {label(a)} and {label(b)}: {len(both)/exp:.1f}x what chance gives ({exp:.1f})",
                             p, [int(x) for x in both], expected=round(exp, 1), observed=len(both)))
    return out, tests


def lens_era(meta):
    years = sorted(c["year"] for c in meta.values())
    pre65_all = sum(1 for y in years if y < 1965)
    med_all = years[N // 2]
    pool = collections.defaultdict(list)
    for n, c in meta.items():
        for t in traits(c) - {"wheat"}: pool[t].append((c["year"], int(n)))
    out = []
    for t, ys in pool.items():
        if len(ys) < 15: continue
        k = sum(1 for y, _ in ys if y < 1965)
        exp = len(ys) * pre65_all / N
        med = sorted(y for y, _ in ys)[len(ys) // 2]
        if k >= 2 * exp and k >= 4:
            p = hyper_ge(k, N, pre65_all, len(ys))
            out.append(F("era", "collection",
                         f"{label(t).capitalize()} leans old: {k} of its {len(ys)} Cents are dated before 1965 ({k/len(ys):.0%}, against {pre65_all/N:.0%} of the whole collection); median year {med} vs {med_all}",
                         p, [n for y, n in ys if y < 1965]))
        elif exp >= 3 and k <= exp / 3:
            p = hyper_le(k, N, pre65_all, len(ys))
            out.append(F("era", "collection",
                         f"{label(t).capitalize()} leans new: only {k} of its {len(ys)} Cents are dated before 1965 (chance gives about {exp:.0f}); median year {med} vs {med_all}",
                         p, [n for y, n in ys if y < 1965]))
    return out


def lens_extremes(meta):
    """Superlative Cents. Each is a fact, p is the share of Cents it would apply to by chance (1/pool)."""
    out = []
    pool = collections.defaultdict(list)
    for n, c in meta.items():
        for t in traits(c) - {"wheat"}: pool[t].append(int(n))
    year_n = collections.Counter(c["year"] for c in meta.values())
    for t, ns in pool.items():
        if len(ns) < 10: continue
        ys = sorted((meta[str(n)]["year"], n) for n in ns)
        oldest = [n for y, n in ys if y == ys[0][0]]
        second = next((y for y, _ in ys if y > ys[0][0]), None)
        if len(oldest) == 1 and second and second - ys[0][0] >= 5:
            out.append(F("extremes", f"Cent #{oldest[0]}",
                         f"#{oldest[0]} ({ys[0][0]}) is the oldest {label(t)} Cent by {second - ys[0][0]} years; the next is {second}",
                         1 / len(ns), oldest, kind="oldest", trait=t))
        for mm in ("S", "D"):
            hit = [n for n in ns if meta[str(n)]["mint_mark"] == mm]
            share = sum(1 for c in meta.values() if c["mint_mark"] == mm) / N
            if len(hit) == 1 and len(ns) * share >= 2:
                out.append(F("extremes", f"Cent #{hit[0]}",
                             f"#{hit[0]} is the only {mm}-mint {label(t)} Cent (of {len(ns)}; about {len(ns)*share:.0f} would be by chance)",
                             hyper_le(1, N, int(share * N), len(ns)), hit, kind="only-mint", trait=t))
            if not hit and len(ns) * share >= 3:
                out.append(F("extremes", "collection",
                             f"No {mm}-mint Cent is {label(t)} (of {len(ns)}; about {len(ns)*share:.0f} would be by chance)",
                             hyper_le(0, N, int(share * N), len(ns)), [], kind="no-mint", trait=t))
    # The most traits on one Cent, and more than one Full grade
    cnt = {int(n): len(traits(c) - {"wheat"}) + (1 if c["year"] <= 1958 else 0) for n, c in meta.items()}
    dist = collections.Counter(cnt.values())
    top = max(cnt.values())
    tops = [n for n, k in cnt.items() if k == top]
    out.append(F("extremes", "collection" if len(tops) > 1 else f"Cent #{tops[0]}",
                 f"The most Atlas traits on one Cent is {top}, on {len(tops)} Cent(s): {', '.join('#%d' % n for n in sorted(tops))}. "
                 f"{dist[0]} Cents carry none ({dist[0]/N:.0%})", len(tops) / N, tops, kind="most-traits"))
    fulls = {int(n): [k[5:] for k, v in c.items() if k.startswith("full_") and v] for n, c in meta.items()}
    multi = {n: f for n, f in fulls.items() if len(f) >= 2}
    if not multi:
        out.append(F("extremes", "collection",
                     f"No Cent carries two Full grades: each of the {sum(1 for f in fulls.values() if f)} Full Cents is Full in one patina only",
                     1 / N, [], kind="multi-full"))
    else:
        out.append(F("extremes", "collection",
                     f"{len(multi)} Cent(s) carry two Full grades: " + "; ".join(f"#{n} ({' + '.join(f)})" for n, f in sorted(multi.items())),
                     len(multi) / N, list(multi), kind="multi-full"))
    nc = {int(n): len(c.get("contaminated") or []) for n, c in meta.items()}
    mx = max(nc.values())
    mxs = [n for n, k in nc.items() if k == mx]
    out.append(F("extremes", "collection",
                 f"The most contamination types on one Cent is {mx}, on {len(mxs)} Cent(s): {', '.join('#%d' % n for n in sorted(mxs)[:12])}",
                 len(mxs) / N, mxs, kind="most-contam"))
    # 1/1 Years the site already badges; listed so "holders" can name who has them
    for y, k in year_n.items():
        if k == 1:
            n = next(int(n) for n, c in meta.items() if c["year"] == y)
            out.append(F("extremes", f"Cent #{n}", f"#{n} is the only Cent dated {y} (a 1/1 Year)", 1 / N, [n],
                         on_site=True, kind="1/1 year"))
    return out


# ---------- the Walls ----------
def wall_names(walls, names):
    artist = next(w for w, n in names.items() if n == "Rutherford Chang")
    return artist, (lambda w: names.get(w) or "an unclaimed Wall")


def pools(meta):
    pv = collections.defaultdict(set)
    for n, c in meta.items():
        for v in values(c): pv[v].add(int(n))
        for t in traits(c): pv["trait: " + t].add(int(n))
    return pv


def nice(v):
    return label(v.replace("trait: ", "").replace("contamination: ", "contamination "))


def lens_share(meta, walls, names, pv):
    """A Wall holds a value far beyond what its size predicts. Selection is the collector's own:
    this reads as a taste or a focus, never as luck."""
    artist, who = wall_names(walls, names)
    out = []
    for w in names:
        if w == artist: continue
        held = set(walls[w]); n = len(held)
        for v, P in pv.items():
            if v.startswith("trait: ") or len(P) > 1500: continue
            k = len(held & P)
            exp = n * len(P) / N
            if k >= 3 and k >= 4 * exp:
                p = hyper_ge(k, N, len(P), n)
                out.append(F("share", names[w],
                             f"{names[w]}: {k} of its {n} Cents are {nice(v)} ({k/n:.0%}); across the collection it is {len(P)/N:.1%}, so {k/exp:.0f}x the expected {exp:.1f}",
                             p, held & P))
    return out


def lens_grip(meta, walls, names, pv):
    artist, who = wall_names(walls, names)
    out, best = [], (0, None, None)
    for v, P in pv.items():
        if v.startswith("trait: ") or len(P) < 8: continue
        holders = collections.Counter()
        for w, ids in walls.items():
            k = len(P & set(ids))
            if k: holders[w] = k
        # the top COLLECTOR (artist wallet reported beside it)
        coll = [(k, w) for w, k in holders.items() if w != artist]
        if not coll: continue
        k, w = max(coll)
        share = k / len(P)
        if share > best[0]: best = (share, v, who(w), k, len(P))
        if share >= 0.1 and k >= 2:
            size = len(walls[w])
            p = hyper_ge(k, N, len(P), size)
            a = holders.get(artist, 0)
            out.append(F("grip", who(w),
                         f"{who(w)} holds {k} of all {len(P)} {nice(v)} Cents ({share:.0%}); {len(holders)} Walls hold any"
                         + (f"; the artist wallet holds {a}" if a else ""),
                         p, P & set(walls[w]) if w in names else set(), claimed=w in names))
    if best[1]:
        out.append(F("grip", "collection",
                     f"No collector holds more than {best[0]:.0%} of any trait or contamination pool (of 8 or more Cents); the tightest grip is {best[2]} with {best[3]} of the {best[4]} {nice(best[1])} Cents",
                     0.5, []))
    return out


def wall_state(meta, ids):
    cs = [meta[str(n)] for n in ids]
    yrs = {c["year"] for c in cs}
    mm = {c["mint_mark"] for c in cs}
    pat = {}
    for c in cs:
        for t in PATINAS:
            g = next((gr for gr in ("full", "significant", "notable") if c.get(f"{gr}_{t}")), None)
            if g: pat[t] = max(pat.get(t, 0), {"notable": 1, "significant": 2, "full": 3}[g])
    gold = any(c.get("notable_gold") or c.get("full_gold") for c in cs)
    orange = any(c.get("orange") for c in cs)
    tr = set().union(*(traits(c) for c in cs))
    ct = {t for c in cs for t in (c.get("contaminated") or [])}
    return dict(years=yrs, mints=mm, patinas=pat, gold=gold, orange=orange, traits=tr, contam=ct)


def lens_nearmiss(meta, walls, names):
    """One Cent from a Set, measured with our own reading of the Set rules (checked against the site's counts in --self-test)."""
    artist, who = wall_names(walls, names)
    all_contam = {t for c in meta.values() for t in (c.get("contaminated") or [])}
    all_traits = set().union(*(traits(c) for c in meta.values()))
    year_set = {c["year"] for c in meta.values()}
    st = {w: wall_state(meta, ids) for w, ids in walls.items()}

    def misses(s):
        m = []
        miss = {1971, 1979, 1982} - s["years"]
        if len(miss) == 1: m.append(("Chronicle Set", f"a {miss.pop()} Cent"))
        miss = {None, "D", "S"} - s["mints"]
        if len(miss) == 1: m.append(("Full Mint Set", {None: "a no-mint-mark Cent", "D": "a D-mint Cent", "S": "an S-mint Cent"}[miss.pop()]))
        need = [t for t in PATINAS if t not in s["patinas"]] + (["gold"] if not s["gold"] else []) + (["orange"] if not s["orange"] else [])
        if len(need) == 1: m.append(("Spectrum Set", f"a {need[0]} Cent"))
        miss = all_contam - s["contam"]
        if len(miss) == 1: m.append(("Full Contamination Set", f"a {miss.pop()} contamination"))
        miss = all_traits - s["traits"]
        if len(miss) == 1: m.append(("all 19 Atlas traits", f"a {label(miss.pop())} Cent"))
        for d in (1960, 1970):
            miss = {y for y in range(d, d + 10) if y in year_set} - s["years"]
            if len(miss) == 1: m.append((f"{d}s Set", f"a {miss.pop()} Cent"))
        return m

    every = {w: misses(s) for w, s in st.items()}
    tally = collections.Counter(x[0] for m in every.values() for x in m)
    out = []
    for w in names:
        if w == artist: continue
        for setname, need in every[w]:
            others = tally[setname] - 1
            out.append(F("nearmiss", names[w],
                         f"{names[w]} is one Cent from the {setname}: it lacks only {need} ({others} other Walls are also exactly one short)",
                         (tally[setname]) / len(walls), [], set=setname))
    return out, every


def lens_smallyear(meta, walls, names, scarce=4):
    """Cents from years with at most `scarce` Cents in all 10,000 (pre-1944 mostly). No Wall holds
    two Cents of one such year, so the lens counts how many scarce YEARS a Wall reaches."""
    artist, who = wall_names(walls, names)
    yc = collections.Counter(c["year"] for c in meta.values())
    rare = {int(n) for n, c in meta.items() if yc[c["year"]] <= scarce}
    per = {w: len(rare & set(ids)) for w, ids in walls.items()}
    out = []
    for w in names:
        k = per[w]
        if k < 2: continue
        better = sum(1 for x, v in per.items() if v >= k and x not in (w, artist))
        tag = " (the artist wallet)" if w == artist else ""
        ys = sorted(meta[str(n)]["year"] for n in rare & set(walls[w]))
        out.append(F("smallyear", names[w] + tag,
                     f"{names[w]}{tag} holds {k} of the {len(rare)} Cents from years with {scarce} or fewer Cents ({', '.join(map(str, ys))}); "
                     + ("no other collector holds as many" if better == 0 else f"{better} other collector(s) hold as many"),
                     (better + 1) / len(walls), rare & set(walls[w])))
    return out


def lens_pair(meta, walls, names, pv):
    """Only one Wall holds both of two scarce values. Uses values with a pool of 8 to 60."""
    artist, who = wall_names(walls, names)
    scarce = [v for v, P in pv.items() if 8 <= len(P) <= 60 and not v.startswith("trait: ")]
    hold = {w: set(ids) for w, ids in walls.items()}
    has = {v: {w for w, h in hold.items() if h & pv[v]} for v in scarce}
    out = []
    for i, a in enumerate(scarce):
        for b in scarce[i + 1:]:
            if a.split("_")[-1] == b.split("_")[-1]: continue     # full_red vs significant_red: same trait
            both = has[a] & has[b]
            both_c = both - {artist}
            if len(both_c) == 1:
                w = next(iter(both_c))
                if w not in names: continue
                p = (len(has[a]) / len(walls)) * (len(has[b]) / len(walls))
                out.append(F("pair", names[w],
                             f"{names[w]} is the only collector holding both a {nice(a)} ({len(pv[a])} exist) and a {nice(b)} ({len(pv[b])} exist)"
                             + ("; the artist wallet does too" if artist in both else ""),
                             p, (hold[w] & pv[a]) | (hold[w] & pv[b])))
    return out


def lens_holders(extremes, walls, names):
    artist, who = wall_names(walls, names)
    owner = {n: w for w, ids in walls.items() for n in ids}
    out = []
    for f in extremes:
        if not f["cents"] or f["n_cents"] > 3: continue
        hs = [who(owner[n]) + (" (the artist wallet)" if owner[n] == artist else "") for n in f["cents"]]
        claimed = [h for n, h in zip(f["cents"], hs) if owner[n] in names]
        if claimed:
            out.append(F("holders", ", ".join(sorted(set(claimed))),
                         f"{f['claim']}: held by " + ", ".join(f"#{n} {h}" for n, h in zip(f["cents"], hs)),
                         f["p"], f["cents"], on_site=f["on_site"]))
    return out


# ---------- report ----------
def run(snap, only=None):
    meta, walls, names, sets, sc, rp = load(snap)
    if len(meta) != N: sys.exit(f"FLOOR: {len(meta)} Cents, want {N}")
    if len(walls) != sc["totalCollectors"]: sys.exit(f"FLOOR: {len(walls)} Walls, the site counts {sc['totalCollectors']}")
    if sum(len(v) for v in walls.values()) != N: sys.exit("FLOOR: the Walls do not hold exactly 10000 Cents")
    pv = pools(meta)
    pairs, tests = lens_pairs(meta)
    ext = lens_extremes(meta)
    near, _ = lens_nearmiss(meta, walls, names)
    found = pairs + lens_era(meta) + ext + lens_share(meta, walls, names, pv) + lens_grip(meta, walls, names, pv) \
        + near + lens_smallyear(meta, walls, names) + lens_pair(meta, walls, names, pv) + lens_holders(ext, walls, names)
    if only: found = [f for f in found if only in f["subject"]]
    found.sort(key=lambda f: (-f["bits"], f["lens"]))
    floors = {lens: sum(1 for f in found if f["lens"] == lens) for lens in
              ("pairs", "era", "extremes", "share", "grip", "nearmiss", "smallyear", "pair", "holders")}
    return found, dict(pair_tests=tests, floors=floors, walls=len(walls), claimed=len(names))


def self_test(snap):
    meta, walls, names, sets, sc, rp = load(snap)
    ok = True
    def check(cond, green, red):
        nonlocal ok
        print(("green " if cond else "RED   ") + (green if cond else red)); ok &= cond

    # 1. Our Set reading must match the site's own counts, or near-misses are wrong.
    st = {w: wall_state(meta, ids) for w, ids in walls.items()}
    chron = sum(1 for s in st.values() if {1971, 1979, 1982} <= s["years"])
    fmint = sum(1 for s in st.values() if {None, "D", "S"} <= s["mints"])
    spec = sum(1 for s in st.values() if all(t in s["patinas"] for t in PATINAS) and s["gold"] and s["orange"])
    allc = {t for c in meta.values() for t in (c.get("contaminated") or [])}
    cfull = sum(1 for s in st.values() if s["contam"] >= allc)
    for name, mine, key in (("Chronicle", chron, "chronicle"), ("Full Mint", fmint, "fullMint"),
                            ("Spectrum", spec, "spectrum"), ("Full Contamination", cfull, "contaminationFull")):
        check(mine == sc["counts"][key], f"{name}: our rule finds {mine}, the site counts {mine}",
              f"{name}: our rule finds {mine}, the site counts {sc['counts'][key]}")
    # 2. Plant a Wall one Cent short of a Chronicle: nearmiss must name the missing year.
    artist = next(w for w, n in names.items() if n == "Rutherford Chang")
    y71 = next(int(n) for n, c in meta.items() if c["year"] == 1971)
    y82 = next(int(n) for n, c in meta.items() if c["year"] == 1982)
    fake = dict(walls); fake["PLANT"] = [y71, y82]
    fnames = dict(names); fnames["PLANT"] = "PLANT"
    _, every = lens_nearmiss(meta, fake, fnames)
    check(("Chronicle Set", "a 1979 Cent") in every["PLANT"], "planted 1971+1982 Wall is reported one 1979 short",
          f"planted Wall not reported as one short: {every['PLANT']}")
    # 3. Plant a Wall holding every Ghost Cent: grip must report 100%.
    pv = pools(meta)
    g = sorted(pv["ghost"])
    fake = {w: [n for n in ids if n not in pv["ghost"]] for w, ids in walls.items()}
    fake["PLANT"] = g
    grip = [f for f in lens_grip(meta, fake, fnames, pv) if f["subject"] == "PLANT" and "ghost" in f["claim"]]
    check(bool(grip) and f"{len(g)} of all {len(g)}" in grip[0]["claim"], "planted Ghost hoard reported as all 33",
          f"planted Ghost hoard not reported: {grip}")
    # 4. Pairs: real data vs a shuffle. Shuffling one trait's Cents must destroy its strong findings.
    real, _ = lens_pairs(meta)
    strong = lambda fs, t: [f for f in fs if f["bits"] >= 20 and label(t) in f["claim"]]
    t = "faceless"
    rs = strong(real, t)
    rnd = random.Random(7)
    pick = set(rnd.sample(sorted(meta), len([1 for c in meta.values() if c.get("faceless")])))
    shuf = {n: {**{k: v for k, v in c.items() if k != "faceless"}, **({"faceless": True} if n in pick else {})} for n, c in meta.items()}
    ss = strong(lens_pairs(shuf)[0], t)
    check(len(ss) < max(1, len(rs)), f"shuffled faceless: {len(rs)} strong pair findings fall to {len(ss)}",
          f"shuffled faceless still gives {len(ss)} strong findings (real {len(rs)}): the lens finds noise")
    # 5. Floors: every lens must return something on the real data.
    found, info = run(snap)
    empty = [k for k, v in info["floors"].items() if v == 0]
    check(not empty, f"every lens returned findings: {info['floors']}", f"lenses returned nothing (counter broke?): {empty}")
    # 6. No wallet address leaks into any claim.
    leak = [f for f in found if re.search(r"bc1[a-z0-9]{20,}", json.dumps(f))]
    check(not leak, "no wallet address in any finding", f"{len(leak)} findings contain a wallet address")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, required=True)
    ap.add_argument("--wall"); ap.add_argument("--json", type=Path)
    ap.add_argument("--min-bits", type=float, default=0)
    ap.add_argument("--by-wall", type=int, default=0, help="also list each claimed Wall's top N findings the site does not show")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test: self_test(a.snapshot)
    found, info = run(a.snapshot, a.wall)
    if a.json: json.dump(dict(info=info, findings=found), open(a.json, "w"), indent=1, default=list)
    print(f"# {len(found)} findings; per lens {info['floors']}; {info['pair_tests']} pair tests (expect ~{info['pair_tests']*2**-10:.1f} false finds at 10 bits)")
    for f in found:
        if f["bits"] < a.min_bits: continue
        print(f"{f['bits']:6.1f}  [{f['lens']:9s}] {'(on site) ' if f['on_site'] else ''}{f['claim']}")
    if a.by_wall:
        meta, walls, names, *_ = load(a.snapshot)
        for name in sorted(names.values(), key=str.lower):
            if name == "Rutherford Chang": continue
            mine = [f for f in found if not f["on_site"] and f["subject"].split(" (")[0].split(", ") .count(name)]
            print(f"\n## {name}")
            for f in mine[:a.by_wall]: print(f"  {f['bits']:5.1f} [{f['lens']}] {f['claim']}")
            if not mine: print("  (no off-site finding; use wall_focus.py)")
