"""Counts behind the #10000 script (v0.1). Run from anywhere:

    python3 -I films/onecent-10000/script/counts.py /mnt/project-files/knowledge/data/cents_traits_sep2026.json

Every figure the script speaks comes from the raw Sep 2026 export. The script
refuses to print if its floor fails (Assassin must be 42, the figure in the
knowledge brief and knowledge/data/README.md), so a broken counter can't pass
as a small count. Copied in shape from films/onecent-8820/script/counts.py.
"""
import json
import sys

META = {"unique_id", "year", "mint_mark", "id", "inscription_number", "rare_sats"}


def profile(rec):
    return sorted(k for k, v in rec.items() if k not in META and v)


def main(path):
    d = json.load(open(path))
    assert len(d) == 10000, f"expected 10,000 records, got {len(d)}"
    assert sorted(map(int, d)) == list(range(1, 10001)), "numbering is not 1..10000 without gaps"
    floor = sum(1 for r in d.values() if r.get("assassin"))
    assert floor == 42, f"floor failed: Assassin counted {floor}, expected 42"

    me = d["10000"]
    pair = profile(me)
    assert pair == ["assassin", "notable_verdigris"], pair
    assert me["year"] == 1976 and me["mint_mark"] is None, me

    assassin_1976 = sorted(int(n) for n, r in d.items() if r.get("assassin") and r["year"] == 1976)
    out = {
        "collection_size": len(d),
        "highest_number": max(map(int, d)),
        "inscription_number": me["inscription_number"],
        "assassin": floor,
        "notable_verdigris": sum(1 for r in d.values() if r.get("notable_verdigris")),
        "rarer_trait": "assassin" if floor < sum(1 for r in d.values() if r.get("notable_verdigris")) else "notable_verdigris",
        "assassin_1976": assassin_1976,
        "assassin_and_notable_verdigris": sum(1 for r in d.values() if r.get("assassin") and r.get("notable_verdigris")),
        "exact_pair": sorted(int(n) for n, r in d.items() if profile(r) == pair),
        "year_1976": sum(1 for r in d.values() if r["year"] == 1976),
        "year_1976_no_mark": sum(1 for r in d.values() if r["year"] == 1976 and not r["mint_mark"]),
        "template_candidates_1976_P_lustrous_only": sorted(
            int(n) for n, r in d.items()
            if r["year"] == 1976 and not r["mint_mark"] and profile(r) == ["lustrous"]
        ),
        "atlas_examples_present": {n: profile(d[str(n)]) for n in (1894, 6595, 3398, 2755, 3844)},
    }
    for k, v in out.items():
        print(f"{k}: {v}")

    if "--write-pools" in sys.argv:
        dest = sys.argv[sys.argv.index("--write-pools") + 1]
        assassin = sorted(int(n) for n, r in d.items() if r.get("assassin"))
        assert len(assassin) == out["assassin"] and 10000 in assassin
        # The featured Cent goes last, so CentScroll's spotlight lands on it (brief §7, #8820).
        pools = {"assassin": [n for n in assassin if n != 10000] + [10000], "assassin_1976": assassin_1976}
        json.dump(pools, open(dest, "w"), indent=0)
        print("pools written:", {k: len(v) for k, v in pools.items()}, "->", dest)


if __name__ == "__main__":
    main(sys.argv[1])
