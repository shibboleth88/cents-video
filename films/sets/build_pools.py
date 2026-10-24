#!/usr/bin/env python3
"""Build films/sets/data/pools.json: the real Cent numbers behind every Set ingredient.

Source of record: cents_by_trait.json, derived from the Sep 2026 cents.vision
trait export (see /mnt/project-files/knowledge/data/README.md). Set requirements
follow cents.vision/sets.html as transcribed in cents-bot knowledge/cents-vision-guide.md.

    python3 films/sets/build_pools.py /mnt/project-files/knowledge/data/cents_by_trait.json

Each pool is floored: an empty or missing pool stops the build, because a pool
of zero renders as an empty wall that looks like a finding.
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = ["verdigris", "obsidian", "desert", "red"]


def main(src):
    idx = json.loads(Path(src).read_text())["index"]
    def get(k):
        if not idx.get(k):
            raise SystemExit(f"pool {k!r} is empty or missing; refusing to build")
        return idx[k]
    pools = {}
    for p in BASE:
        pools[f"{p}:notable+"] = get(f"{p}_any")
        pools[f"{p}:significant+"] = sorted(set(get(f"significant_{p}")) | set(get(f"full_{p}")))
        pools[f"{p}:full"] = get(f"full_{p}")
    pools["gold:any"] = get("gold_any")
    pools["gold:full"] = get("full_gold")
    pools["orange"] = get("orange")
    for k in idx:
        if k.startswith("contaminated:"):
            pools[k] = get(k)
    for y in (1971, 1979, 1982):
        pools[f"year:{y}"] = get(f"year:{y}")
    for m in ("S", "D", "none"):
        pools[f"mint:{m}"] = get(f"mint:{m}")
    years = sorted(int(k[5:]) for k in idx if k.startswith("year:"))
    pools["_years"] = {str(y): get(f"year:{y}") for y in years}
    out = HERE / "data" / "pools.json"
    out.write_text(json.dumps({"_source": "cents_by_trait.json (Sep 2026 export)", "pools": pools}, separators=(",", ":")))
    used = sorted({n for k, v in pools.items() if k != "_years" for n in v})
    print(f"wrote {out.relative_to(HERE.parent.parent)}: {len(pools)} pools, {len(used)} distinct Cents (excluding year columns)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/knowledge/data/cents_by_trait.json")
