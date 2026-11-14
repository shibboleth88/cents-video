"""What would each suggestion add to DOPEMIND's card? Measured with the page's own code.

For each scenario the Cents are moved, in a copy of wallet_index_cents.json, from their
current holder onto DOPEMIND's wallet, and collectors.html is replayed offline
(/mnt/project-files/collectors/replay.js). The card's rendered badges are read back.
Nothing is reimplemented: the badges are what the site would draw.

    python3 -I films/wall-dopemind-next/data/sim/run_sims.py <work dir>   (from the repo root)

Writes <work dir>/raw_*/, <work dir>/out_*.json and films/wall-dopemind-next/data/sim/sims.json.
"1971", "1982" and "S" scenarios use the first Cent of that year (or mint) that carries no
trait and is not on any claimed Wall, so the scenario adds the year and nothing else.
"""
import json, os, pathlib, subprocess, sys, shutil

D = "/mnt/project-files/collectors/snapshots/2026-11-09"
REPLAY = "/mnt/project-files/collectors/replay.js"
HERE = pathlib.Path(__file__).resolve().parent
W = pathlib.Path(sys.argv[1]).resolve()
m = json.load(open(D + "/raw/merged-new2.json"))
r = json.load(open(D + "/replay.json"))
wi = json.load(open(D + "/raw/wallet_index_cents.json"))
dw = [w for w in r["claimed"] if w["name"] == "DOPEMIND"][0]["wallet"]
claimed = set(w["wallet"] for w in r["claimed"])
for w in r["claimed"]: claimed |= set(w["secondary_wallets"] or [])
owner = {c: w for w, cs in wi.items() for c in cs}
META = {"unique_id", "year", "mint_mark", "id", "inscription_number"}
def plain(n): return not any(k not in META for k in m[str(n)])
def pick(year=None, mint="any"):
    for n in range(1, 10001):
        c = m[str(n)]
        if year and c["year"] != year: continue
        if mint != "any" and c["mint_mark"] != mint: continue
        if plain(n) and owner[n] not in claimed: return n
    sys.exit(f"REFUSING: no plain unclaimed Cent for {year} {mint}")
y71, y82, s_ = pick(1971), pick(1982), pick(mint="S")
print("generic picks: 1971", y71, "1982", y82, "S", s_, m[str(s_)]["year"])
picks = [8657, 8820, 6451, 6875, 6782, 5888]
scen = {"baseline": []}
for p in picks: scen[f"+{p}"] = [p]
scen["+all6"] = picks
scen["+1971"] = [y71]; scen["+1971+1982"] = [y71, y82]; scen["+S"] = [s_]
scen["+6451+1982"] = [6451, y82]; scen["+1982"] = [y82]
scen["+all6+1971"] = picks + [y71]
out = {}
for name, add in scen.items():
    tag = name.replace("+", "p")
    raw, o = W / f"raw_{tag}", W / f"out_{tag}.json"
    shutil.rmtree(raw, ignore_errors=True); raw.mkdir(parents=True)
    if o.exists(): o.unlink()          # a failed replay must not leave an old answer to read
    for f in os.listdir(D + "/raw"):
        if f != "wallet_index_cents.json": os.symlink(D + "/raw/" + f, raw / f)
    w2 = {k: list(v) for k, v in wi.items()}
    for c in add:
        w2[owner[c]].remove(c); w2[dw].append(c)
    w2 = {k: v for k, v in w2.items() if v}
    json.dump(w2, open(raw / "wallet_index_cents.json", "w"))
    p = subprocess.run(["node", REPLAY, str(raw), str(o)], cwd=W, capture_output=True, text=True)
    if p.returncode or not o.exists(): sys.exit(f"REFUSING: replay failed for {name}: {p.stderr[-400:]}")
    rr = json.load(open(o))
    d = [w for w in rr["claimed"] if w["name"] == "DOPEMIND"][0]
    if d["count"] != 12 + len(add): sys.exit(f"REFUSING: {name}: count {d['count']}, the move did not land")
    out[name] = {"add": add, "rendered": d["rendered"], "years": d["years"], "count": d["count"],
                 "sets": dict(d["sets"]), "agg": rr["aggregate"]}
    print(name, add, d["years"], "| SETS", d["rendered"]["set_badges"], "| META",
          [b for b in d["rendered"]["meta_badges"] if not b.startswith("Patina count")], "| TAGS", d["rendered"]["trait_tags"])
json.dump(out, open(HERE / "sims.json", "w"), indent=1)
