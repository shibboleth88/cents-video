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
    # Oldest Cent of every trait, graded value and contamination type (user 2026-10-28: no margin needed)
    fine = collections.defaultdict(list)
    for n, c in meta.items():
        for v in (traits(c) - {"wheat"}) | (values(c) - {"wheat", "fingerprints"}): fine[v].append(int(n))
    for t, ns in fine.items():
        if len(ns) < 3: continue
        ys = sorted((meta[str(n)]["year"], n) for n in ns)
        oldest = [n for y, n in ys if y == ys[0][0]]
        second = next((y for y, _ in ys if y > ys[0][0]), None)
        gap = f" by {second - ys[0][0]} years; the next is {second}" if second and second - ys[0][0] >= 2 else ""
        who = " and ".join(f"#{n}" for n in oldest)
        out.append(F("extremes", f"Cent #{oldest[0]}" if len(oldest) == 1 else "collection",
                     f"{who} ({ys[0][0]}) {'is' if len(oldest) == 1 else 'are'} the oldest {nice(t)} Cent{'s' if len(oldest) > 1 else ''} (of {len(ns)}){gap}",
                     len(oldest) / len(ns), oldest, kind="oldest", trait=t))
    for t, ns in pool.items():
        if len(ns) < 10: continue
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
    selfnum = [int(n) for n, c in meta.items() if int(n) == c["year"]]
    exp = sum(year_n.get(k, 0) for k in range(1900, 1990)) / N
    out.append(F("extremes", "collection",
                 f"Cent number equals its date on {len(selfnum)} Cent(s): {', '.join('#%d' % n for n in selfnum)} (chance gives about {exp:.1f}; a curiosity, not a pattern)",
                 0.5, selfnum, kind="self-number"))
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
    # Unclaimed Walls by a short address prefix (user 2026-10-28: videos of unclaimed Walls will use the address)
    return artist, (lambda w: names.get(w) or f"unclaimed Wall {w[:8]}…")


def pools(meta):
    pv = collections.defaultdict(set)
    for n, c in meta.items():
        for v in values(c): pv[v].add(int(n))
        for t in traits(c): pv["trait: " + t].add(int(n))
        mm = c["mint_mark"] or "no mint mark"
        pv[f"year: {c['year']}"].add(int(n))
        pv[f"mint: {mm}"].add(int(n))
        pv[f"ym: {c['year']} {mm}"].add(int(n))
    return pv


DATE = ("year: ", "mint: ", "ym: ")


def an(v):
    return ("a Cent " if v.startswith(DATE) else "an " if nice(v)[0] in "aeiou" else "a ") + nice(v)


def nice(v):
    if v.startswith("year: "): return "dated " + v[6:]
    if v.startswith("mint: "): return v[6:] if v[6:] == "no mint mark" else v[6:] + "-mint"
    if v.startswith("ym: "):
        y, mm = v[4:].split(" ", 1)
        return f"{y} {'(no mint mark)' if mm == 'no mint mark' else mm}"
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
            if a.startswith(DATE) and b.startswith(DATE): continue
            both = has[a] & has[b]
            both_c = both - {artist}
            if len(both_c) == 1:
                w = next(iter(both_c))
                if w not in names: continue
                p = (len(has[a]) / len(walls)) * (len(has[b]) / len(walls))
                out.append(F("pair", names[w],
                             f"{names[w]} is the only collector holding both {an(a)} ({len(pv[a])} exist) and {an(b)} ({len(pv[b])} exist)"
                             + ("; the artist wallet does too" if artist in both else ""),
                             p, (hold[w] & pv[a]) | (hold[w] & pv[b])))
    return out


def lens_holders(extremes, walls, names):
    """Who holds each extreme Cent, claimed or not (user 2026-10-28: include unclaimed Walls),
    and which Walls hold the oldest Cent of the most traits."""
    artist, who = wall_names(walls, names)
    owner = {n: w for w, ids in walls.items() for n in ids}
    out, firsts = [], collections.defaultdict(list)
    for f in extremes:
        if not f["cents"] or f["n_cents"] > 3: continue
        hs = [who(owner[n]) + (" (the artist wallet)" if owner[n] == artist else "") for n in f["cents"]]
        out.append(F("holders", ", ".join(sorted(set(hs))),
                     f"{f['claim']}: held by " + ", ".join(f"#{n} {h}" for n, h in zip(f["cents"], hs)),
                     f["p"], f["cents"], on_site=f["on_site"]))
        if f.get("kind") == "oldest" and f["n_cents"] == 1:
            firsts[owner[f["cents"][0]]].append((f["trait"], f["cents"][0]))
    all_first = {n for ts in firsts.values() for _, n in ts}
    for w, ts in firsts.items():
        if len(ts) < 3: continue
        tag = " (the artist wallet)" if w == artist else ""
        cents = sorted({n for _, n in ts})
        out.append(F("holders", who(w) + tag,
                     f"{who(w)}{tag} holds the oldest Cent of {len(ts)} traits or grades, in {len(cents)} Cent(s): "
                     + "; ".join(f"#{n} ({', '.join(nice(t) for t, m in ts if m == n)})" for n in cents)
                     + f" ({len(all_first)} Cents are the single oldest of some trait; a Wall this size would hold {len(walls[w]) * len(all_first) / N:.1f})",
                     hyper_ge(len(cents), N, len(all_first), len(walls[w])), cents, kind="firsts"))
    return out


KNOWN = [  # facts collectors or our own brief already have: marked, not offered as new
    (r"No Cent carries two Full grades", "known to collectors (user, 2026-10-28)"),
    (r"most Atlas traits on one Cent is 9.*#9344", "knowledge brief: #9344 has 9 traits"),
    (r"both desert and ghost", "knowledge brief: 79% of Ghost Cents are desert"),
    (r"a 1/1 Year", "cents.vision 1/1 Year badge"),
]


def mark_known(found):
    for f in found:
        for pat, src in KNOWN:
            if re.search(pat, f["claim"]): f["on_site"] = True; f["known"] = src
    return found


def lens_keep(meta, walls, names, mk):
    """Cents still in the wallet that minted them (cents.vision mint_keeper.json, per wallet).
    The artist wallet is reported apart; rates are measured on the other 9,000."""
    artist, who = wall_names(walls, names)
    art = set(walls[artist])
    kept_all = {n for v in mk.values() for n in v}
    kept_art = len(kept_all & art)
    rest = set(range(1, N + 1)) - art
    kept = kept_all & rest
    base = len(kept) / len(rest)
    out = [F("keep", "collection",
             f"{len(kept)} of the {len(rest)} Cents outside the artist wallet ({base:.0%}) are still held by the wallet that minted them, "
             f"across {sum(1 for w, v in mk.items() if set(v) - art)} minting wallets; {kept_art} of the artist wallet's {len(art)} Cents are Mint Keeper Cents",
             0.5, [])]
    pv = pools(meta)
    for v, P in pv.items():
        if v.startswith("trait: ") or v.startswith("ym: "): continue
        P = P & rest
        if len(P) < 15: continue
        k = len(P & kept)
        exp = len(P) * base
        hi, lo = hyper_ge(k, len(rest), len(kept), len(P)), hyper_le(k, len(rest), len(kept), len(P))
        p = min(hi, lo) * 2
        if p < 2 ** -8:
            out.append(F("keep", "collection",
                         f"{nice(v).capitalize()} Cents stay with their minter {'more' if hi < lo else 'less'} often: {k} of {len(P)} ({k/len(P):.0%}) are still in the minting wallet, against {base:.0%} overall (chance gives {exp:.0f})",
                         p, P & kept if hi < lo else set()))
    return out


_TR = {}


def trait_vec(meta, ids):
    """Share of the Cents in `ids` carrying each Atlas trait (trait sets cached per metadata object)."""
    key = id(meta)
    if key not in _TR:
        tr = {int(n): traits(c) for n, c in meta.items()}
        _TR.clear(); _TR[key] = (tr, sorted(set().union(*tr.values())))
    tr, keys = _TR[key]
    cnt = collections.Counter(t for n in ids for t in tr[n])
    return [cnt[k] / len(ids) for k in keys], keys


def lens_mix(meta, walls, names, samples=300, seed=11):
    """How far a Wall's trait mix, age and untraited share sit from the collection's, against random Walls of the same size;
    and which two Walls are most alike."""
    artist, who = wall_names(walls, names)
    rnd = random.Random(seed)
    allids = list(range(1, N + 1))
    coll, keys = trait_vec(meta, allids)
    untr = {int(n) for n, c in meta.items() if not traits(c)}
    old = {int(n) for n, c in meta.items() if c["year"] < 1970}
    yrs = sorted(c["year"] for c in meta.values())
    dist = lambda v: sum(abs(a - b) for a, b in zip(v, coll))
    out, vecs = [], {}
    null = {}
    for w in names:
        ids = walls[w]; n = len(ids)
        if n < 15: continue
        tag = " (the artist wallet)" if w == artist else ""
        v, _ = trait_vec(meta, ids); vecs[w] = v
        if n not in null:
            null[n] = sorted(dist(trait_vec(meta, rnd.sample(allids, n))[0]) for _ in range(samples))
        d = dist(v)
        p = (sum(1 for x in null[n] if x >= d) + 1) / (samples + 1)
        top = sorted(zip(keys, v, coll), key=lambda t: -abs(t[1] - t[2]))[:3]
        out.append(F("mix", names[w] + tag,
                     f"{names[w]}{tag}: its trait mix is further from the collection's than {1 - p:.0%} of random Walls its size ({n}); most apart: "
                     + ", ".join(f"{label(k)} {a:.0%} vs {b:.0%}" for k, a, b in top), p, []))
        k = len(set(ids) & untr); exp = n * len(untr) / N
        p = 2 * min(hyper_ge(k, N, len(untr), n), hyper_le(k, N, len(untr), n))
        if p < 2 ** -6:
            out.append(F("mix", names[w] + tag,
                         f"{names[w]}{tag}: {k} of its {n} Cents carry no trait ({k/n:.0%}, against {len(untr)/N:.0%} in the collection)",
                         p, []))
        k = len(set(ids) & old); exp = n * len(old) / N
        p = 2 * min(hyper_ge(k, N, len(old), n), hyper_le(k, N, len(old), n))
        if p < 2 ** -6:
            med = sorted(meta[str(x)]["year"] for x in ids)[n // 2]
            out.append(F("mix", names[w] + tag,
                         f"{names[w]}{tag} leans {'old' if k > exp else 'new'}: {k} of its {n} Cents are dated before 1970 ({k/n:.0%}, against {len(old)/N:.0%}); median year {med} vs {yrs[N // 2]}",
                         p, []))
    # claimed Walls against the rest of the community (counts only for the unclaimed)
    cl = {n for w in names if w != artist for n in walls[w]}
    def u_share(ws):
        ids = [n for w in ws for n in walls[w]]
        return len(untr & set(ids)) / max(1, len(ids))
    small = u_share([w for w, ids in walls.items() if len(ids) <= 4 and w != artist])
    big = u_share([w for w, ids in walls.items() if len(ids) >= 100 and w != artist])
    k = len(cl & untr)
    rest_n = N - len(walls[artist]) - len(cl)
    rest_u = len(untr - cl - set(walls[artist]))
    out.append(F("mix", "collection",
                 f"Claimed Walls hold far more traited Cents: {k} of the {len(cl)} Cents on collectors' claimed Walls carry no trait ({k/len(cl):.0%}), "
                 f"against {rest_u/rest_n:.0%} on unclaimed Walls and {len(set(walls[artist]) & untr)/len(walls[artist]):.0%} in the artist wallet; Wall size alone does not do this ({small:.0%} on 1-4 Cent Walls, {big:.0%} on 100+)",
                 hyper_le(k, N, len(untr), len(cl)), []))
    pocket = [w for w, ids in walls.items() if len(ids) <= 4]
    out.append(F("mix", "collection",
                 f"{len(pocket)} of the {len(walls)} Walls ({len(pocket)/len(walls):.0%}) are Pocket Collections of 1-4 Cents; together they hold {sum(len(walls[w]) for w in pocket):,} Cents",
                 0.5, []))
    # twins: cosine similarity of trait mixes, against random pairs of the same sizes
    cos = lambda a, b: sum(x * y for x, y in zip(a, b)) / (math.sqrt(sum(x * x for x in a) * sum(y * y for y in b)) or 1)
    ws = [w for w in vecs if w != artist and len(walls[w]) >= 20]
    pairs = sorted(((cos(vecs[a], vecs[b]), a, b) for i, a in enumerate(ws) for b in ws[i + 1:]), reverse=True)
    for c, a, b in pairs[:3]:
        ra = [cos(trait_vec(meta, rnd.sample(allids, len(walls[a])))[0], trait_vec(meta, rnd.sample(allids, len(walls[b])))[0]) for _ in range(100)]
        p = (sum(1 for x in ra if x >= c) + 1) / 101
        out.append(F("mix", f"{names[a]}, {names[b]}",
                     f"{names[a]} and {names[b]} have the most alike trait mixes of any two collectors with 20+ Cents (similarity {c:.3f}; random Walls of these sizes reach it {p:.0%} of the time)",
                     p, []))
    return out


def lens_inscription(meta, walls, names, mk):
    """Inscription order: the first and last Cents inscribed, who holds them, and whether order follows date."""
    artist, who = wall_names(walls, names)
    owner = {n: w for w, ids in walls.items() for n in ids}
    kept = {n for v in mk.values() for n in v}
    ins = sorted((c["inscription_number"], int(n)) for n, c in meta.items() if "inscription_number" in c)
    missing = [int(n) for n, c in meta.items() if "inscription_number" not in c]
    out = []
    for label_, part in (("first", ins[:5]), ("last", ins[-3:])):
        txt = "; ".join(f"#{n} (inscription {i:,}, {meta[str(n)]['year']}) held by {who(owner[n])}{' (the artist wallet)' if owner[n] == artist else ''}"
                        f"{', still with its minter' if n in kept else ''}" for i, n in part)
        out.append(F("inscription", "collection", f"The {label_} Cents inscribed: {txt}", 1 / N, [n for _, n in part]))
    # Runs: the most Cents a Wall holds inside any window of 150 consecutive inscriptions, against random Walls its size
    rank = {n: i for i, (_, n) in enumerate(ins)}
    def best_run(ids, win=150):
        rs = sorted(rank[n] for n in ids if n in rank); j = 0; top = (0, 0)
        for i in range(len(rs)):
            while rs[i] - rs[j] >= win: j += 1
            if i - j + 1 > top[0]: top = (i - j + 1, j)
        return top[0], (rs[top[1]] if rs else 0)
    rnd = random.Random(5)
    nullrun = {}
    for w in names:
        ids = walls[w]; n = len(ids)
        if n < 10: continue
        k, start = best_run(ids)
        if n not in nullrun: nullrun[n] = [best_run(rnd.sample(range(1, N + 1), n))[0] for _ in range(200)]
        p = (sum(1 for x in nullrun[n] if x >= k) + 1) / 201
        if p <= 0.01 and k >= 5:
            tag = " (the artist wallet)" if w == artist else ""
            out.append(F("inscription", names[w] + tag,
                         f"{k} of {names[w]}{tag}'s {n} Cents fall inside one run of 150 consecutive inscriptions (from the {start + 1:,}th inscribed); random Walls its size reach {max(nullrun[n])} at most in 200 tries",
                         p, []))
    # Walls whose Cents sit in the first or last tenth of the inscription order
    dec = len(ins) // 10
    early, late = {n for _, n in ins[:dec]}, {n for _, n in ins[-dec:]}
    for w in names:
        ids = set(walls[w]); n = len(ids)
        if n < 15: continue
        tag = " (the artist wallet)" if w == artist else ""
        for part, S in (("first", early), ("last", late)):
            k = len(ids & S)
            p = hyper_ge(k, N, len(S), n)
            if p < 2 ** -8:
                out.append(F("inscription", names[w] + tag,
                             f"{k} of {names[w]}{tag}'s {n} Cents are among the {part} tenth inscribed ({dec:,} Cents) (chance gives {n * len(S) / N:.0f})",
                             p * len(names) * 2, ids & S))
    # rank correlation of inscription order with year
    r = {n: i for i, (_, n) in enumerate(ins)}
    ys = [(meta[str(n)]["year"], r[n]) for n in r]
    def ranks(xs):
        order = sorted(range(len(xs)), key=lambda i: xs[i]); rk = [0] * len(xs); i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]: j += 1
            for t in range(i, j + 1): rk[order[t]] = (i + j) / 2
            i = j + 1
        return rk
    a, b = ranks([y for y, _ in ys]), ranks([i for _, i in ys])
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    rho = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
    out.append(F("inscription", "collection",
                 f"Inscription order does {'not ' if abs(rho) < 0.05 else ''}follow date (rank correlation {rho:+.3f}); "
                 f"{len(missing)} Cents carry no inscription number in the data ({', '.join('#%d' % n for n in missing)})",
                 0.5, [], rho=rho))
    return out


def profile(c):
    return frozenset(values(c) - {"wheat"})


def lens_profile(meta, walls, names, site_combo):
    """Cents whose whole trait profile (graded values + contamination types) no other Cent shares.
    Broader than the site's 1/1 Trait Combo (a unique PAIR), which it must contain."""
    artist, who = wall_names(walls, names)
    prof = {int(n): profile(c) for n, c in meta.items()}
    cnt = collections.Counter(p for p in prof.values() if p)
    uniq = {n for n, p in prof.items() if p and cnt[p] == 1}
    out = []
    common = cnt.most_common(3)
    out.append(F("profile", "collection",
                 f"{len(uniq)} Cents have a trait profile no other Cent shares ({len(site_combo)} of them are the site's 1/1 Trait Combos); "
                 f"the commonest profiles are " + "; ".join(f"{' + '.join(sorted(map(label, p)))} ({k})" for p, k in common),
                 0.5, []))
    per = {w: len(uniq & set(ids)) for w, ids in walls.items()}
    for w in names:
        k = per[w]
        if k < 2: continue
        exp = len(walls[w]) * len(uniq) / N
        rivals = sum(1 for x, v in per.items() if v >= k and x not in (w, artist))
        tag = " (the artist wallet)" if w == artist else ""
        out.append(F("profile", names[w] + tag,
                     f"{names[w]}{tag} holds {k} Cents whose whole trait profile is unique (size predicts {exp:.1f}; {len(site_combo & set(walls[w]))} are site 1/1 Trait Combos); "
                     + ("no other collector holds as many" if rivals == 0 else f"{rivals} other Wall(s) hold as many"),
                     max(hyper_ge(k, N, len(uniq), len(walls[w])), 2 ** -20), uniq & set(walls[w])))
    return out, uniq


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
    mk = json.load(open(snap / "raw/mint_keeper.json"))
    combo = {r["cent"] for r in json.load(open(snap / "raw/unique-2-community-trait-1of1s-merged-new2.json"))["cents"]}
    prof, _ = lens_profile(meta, walls, names, combo)
    found = lens_keep(meta, walls, names, mk) + lens_mix(meta, walls, names) + lens_inscription(meta, walls, names, mk) + prof \
        + pairs + lens_era(meta) + ext + lens_share(meta, walls, names, pv) + lens_grip(meta, walls, names, pv) \
        + near + lens_smallyear(meta, walls, names) + lens_pair(meta, walls, names, pv) + lens_holders(ext, walls, names)
    # Multiple testing: a lens that tries many things will find 1-in-1000 events by chance.
    # p is multiplied by the number of things the lens tried (Bonferroni); the raw p stays as p_raw.
    artist = next(w for w, n in names.items() if n == "Rutherford Chang")
    claimed = len(names) - 1
    vals = [v for v, P in pv.items() if not v.startswith("trait: ")]
    scarce = [v for v in vals if 8 <= len(pv[v]) <= 60]
    tried = {"pairs": tests, "share": claimed * sum(1 for v in vals if len(pv[v]) <= 1500),
             "grip": sum(1 for v in vals if len(pv[v]) >= 8), "pair": claimed * len(scarce) * (len(scarce) - 1) // 2,
             "keep": sum(1 for v in vals if not v.startswith("ym: ")), "era": 19}
    for f in found:
        m = tried.get(f["lens"])
        if m and f["p"] < 0.5:
            f["p_raw"] = f["p"]; f["p"] = min(1.0, f["p"] * m); f["bits"] = bits(f["p"]); f["tests"] = m
    mark_known(found)
    if only: found = [f for f in found if only in f["subject"]]
    found.sort(key=lambda f: (-f["bits"], f["lens"]))
    floors = {lens: sum(1 for f in found if f["lens"] == lens) for lens in
              ("pairs", "era", "extremes", "share", "grip", "nearmiss", "smallyear", "pair", "holders", "keep", "mix", "inscription", "profile")}
    return found, dict(pair_tests=tests, tried=tried, floors=floors, walls=len(walls), claimed=len(names))


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
    # 7. keep: shuffling which Cents are Mint Keeper Cents must remove the by-value findings.
    mk = json.load(open(snap / "raw/mint_keeper.json"))
    real_k = [f for f in lens_keep(meta, walls, names, mk) if f["bits"] >= 8 and "stay with" in f["claim"]]
    art = set(walls[artist]); rest = sorted(set(range(1, N + 1)) - art)
    nk = len({n for v in mk.values() for n in v} - art)
    fake_mk = {"A": sorted(art), "B": rnd.sample(rest, nk)}
    shuf_k = [f for f in lens_keep(meta, walls, names, fake_mk) if f["bits"] >= 8 and "stay with" in f["claim"]]
    check(len(shuf_k) < max(1, len(real_k)), f"keep: shuffled Mint Keeper gives {len(shuf_k)} findings at 8+ bits (real {len(real_k)})",
          f"keep: shuffled Mint Keeper still gives {len(shuf_k)} (real {len(real_k)}): noise")
    # 8. mix: a planted Wall of 40 untraited Cents must be flagged; a clone of ScrappyT must be its twin at similarity 1.
    untr = sorted(int(n) for n, c in meta.items() if not traits(c))
    scrappy = next(w for w, n in names.items() if n == "ScrappyT")
    fake = {w: [n for n in ids if n not in set(untr[:40]) | set(walls[scrappy])] for w, ids in walls.items()}
    fake[scrappy] = walls[scrappy]
    fake["PLANT"] = untr[:40]; fake["CLONE"] = list(walls[scrappy])
    fn = dict(names); fn["PLANT"] = "PLANT"; fn["CLONE"] = "CLONE"
    mx = lens_mix(meta, {w: v for w, v in fake.items() if v}, fn, samples=50)
    check(any(f["subject"] == "PLANT" and "40 of its 40 Cents carry no trait" in f["claim"] for f in mx),
          "mix: planted all-untraited Wall flagged", "mix: planted all-untraited Wall NOT flagged")
    tw = [f for f in mx if "most alike" in f["claim"]]
    check(bool(tw) and "CLONE" in tw[0]["subject"] and "ScrappyT" in tw[0]["subject"] and "1.000" in tw[0]["claim"],
          "mix: a ScrappyT clone is found as its twin at 1.000", f"mix: clone not found as twin: {tw[:1]}")
    # 9. profile: every site 1/1 Trait Combo (a unique pair) must have a unique whole profile; a copied profile must lose it.
    combo = {r["cent"] for r in json.load(open(snap / "raw/unique-2-community-trait-1of1s-merged-new2.json"))["cents"]}
    _, uniq = lens_profile(meta, walls, names, combo)
    check(combo <= uniq, f"profile: all {len(combo)} site 1/1 Trait Combos are among our {len(uniq)} unique profiles",
          f"profile: {len(combo - uniq)} site combos missing from our unique profiles: {sorted(combo - uniq)}")
    c0 = min(uniq); twin = dict(meta); donor = next(n for n, c in meta.items() if not traits(c))
    twin[donor] = {**meta[str(c0)], "unique_id": "x"}
    _, uniq2 = lens_profile(twin, walls, names, set())
    check(c0 not in uniq2, f"profile: copying #{c0}'s traits onto #{donor} makes it no longer unique", f"profile: copied profile still unique")
    # 10. inscription runs: 20 consecutive inscriptions planted as a Wall must be flagged; 20 random Cents must not.
    ins = sorted((c["inscription_number"], int(n)) for n, c in meta.items() if "inscription_number" in c)
    block = [n for _, n in ins[5000:5020]]; scatter = rnd.sample([n for _, n in ins], 20)
    for nm, ids, want in (("BLOCK", block, True), ("SCATTER", scatter, False)):
        fk = {w: [n for n in v if n not in set(ids)] for w, v in walls.items()}; fk[nm] = ids
        fn = dict(names); fn[nm] = nm
        got = any(f["subject"] == nm and "one run of 150" in f["claim"] for f in lens_inscription(meta, fk, fn, mk))
        check(got == want, f"inscription runs: planted {nm} {'flagged' if want else 'not flagged'}, as it should be",
              f"inscription runs: planted {nm} {'NOT flagged' if want else 'flagged'}")
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
    print(f"# {len(found)} findings; per lens {info['floors']}")
    print(f"# bits are after correcting for how many things each lens tried: {info['tried']}; 0 bits = could be chance")
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
