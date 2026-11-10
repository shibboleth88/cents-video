"""Every Wall with a Contamination Set (3+ of the 12 contamination types), by how many
contaminated Cents it holds, from the dated snapshot. Writes data/contamination_sets.json
for the dot chart. Walls are joined as collectors.html joins them (pipeline/wall_focus.load).
The artist wallet is counted for the check against set-counts.php, then left out of the
chart (it is not a collector). No wallet address is written.

    python3 films/wall-dopemind/data/contamination_sets.py /mnt/project-files/collectors/snapshots/2026-11-09 [--control]
"""
import collections, json, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pipeline"))
from wall_focus import load
snap = pathlib.Path(sys.argv[1])
meta, walls, names, sets, sc, rp = load(snap)
if "--control" in sys.argv:            # plant a second two-Cent Set: #6582 (Paint + Obscure Adhesive) into a Wall
    for w, ids in walls.items():       # that holds exactly one contaminated Cent, of a third type
        cc = [n for n in ids if meta[str(n)].get("contaminated")]
        if len(cc) == 1 and not set(meta[str(cc[0])]["contaminated"]) & {"Paint", "Obscure Adhesive"}:
            walls[w] = ids + [6582]; break
artist = next(w for w, n in names.items() if n == "Rutherford Chang")
rows = []
for w, ids in walls.items():
    cc = [n for n in ids if meta[str(n)].get("contaminated")]
    if len({t for n in cc for t in meta[str(n)]["contaminated"]}) >= 3:
        rows.append((w, len(cc)))
site = sc["counts"]["contaminationSet"]
if "--control" not in sys.argv and len(rows) != site:
    sys.exit(f"REFUSING: {len(rows)} Walls with a Contamination Set here, set-counts.php says {site}")
coll = [(w, k) for w, k in rows if w != artist]
low = min(k for _, k in coll)
at_low = [w for w, k in coll if k == low]
if len(at_low) != 1 or names.get(at_low[0]) != "DOPEMIND":
    sys.exit(f"REFUSING: the fewest is {low}, held by {len(at_low)} Wall(s): {[names.get(w, '(unclaimed)') for w in at_low]}")
if "--control" in sys.argv: sys.exit("CONTROL PASSED, which it must not")
counts = collections.Counter(k for _, k in coll)
bins = [{"label": str(k), "count": counts.get(k, 0)} for k in range(2, 11)]
bins.append({"label": "11+", "count": sum(c for k, c in counts.items() if k >= 11)})
out = {"_source": f"{snap.name} snapshot via wall_focus.load; set-counts.php contaminationSet = {site} (incl. the artist wallet, left out here)",
       "as_of": snap.name, "collectors": len(coll), "highlight": {"label": "2", "name": "DOPEMIND"}, "bins": bins,
       "artist_wallet_contaminated_cents": dict(rows)[artist]}
json.dump(out, open(pathlib.Path(__file__).parent / "contamination_sets.json", "w"), indent=1)
print(json.dumps(out))
