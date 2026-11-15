"""Counts behind the #8820 script (v0.1, v0.2). Run from anywhere:

    python3 -I films/onecent-8820/script/counts.py /mnt/project-files/knowledge/data/cents_traits_sep2026.json

Every figure the script speaks comes from the raw Sep 2026 export, and the
script refuses to print if its floor fails (Full Red must be 71, the figure in
knowledge/data/README.md), so a broken counter can't pass as a small count.
"""
import json
import sys

META = {"unique_id", "year", "mint_mark", "id", "inscription_number", "rare_sats"}


def profile(rec):
    return sorted(k for k, v in rec.items() if k not in META and v)


def main(path):
    d = json.load(open(path))
    assert len(d) == 10000, f"expected 10,000 records, got {len(d)}"
    floor = sum(1 for r in d.values() if r.get("full_red"))
    assert floor == 71, f"floor failed: Full Red counted {floor}, expected 71"

    me = d["8820"]
    pair = profile(me)
    assert pair == ["notable_verdigris", "significant_red"], pair
    assert me["year"] == 1972 and me["mint_mark"] is None, me

    out = {
        "significant_red": sum(1 for r in d.values() if r.get("significant_red")),
        "notable_verdigris": sum(1 for r in d.values() if r.get("notable_verdigris")),
        "both": sum(1 for r in d.values() if r.get("significant_red") and r.get("notable_verdigris")),
        "exact_pair": sum(1 for r in d.values() if profile(r) == pair),
        "year_1972": sum(1 for r in d.values() if r["year"] == 1972),
        "year_1972_no_mark": sum(1 for r in d.values() if r["year"] == 1972 and not r["mint_mark"]),
        "template_candidates_1972_P_lustrous_only": sorted(
            int(n) for n, r in d.items()
            if r["year"] == 1972 and not r["mint_mark"] and profile(r) == ["lustrous"]
        ),
    }
    for k, v in out.items():
        print(f"{k}: {v}")

    # The pools the film shows, written for the timeline (--write-pools PATH). Each list is checked
    # against the count printed above, so a shown pool can't drift from a spoken number.
    if "--write-pools" in sys.argv:
        dest = sys.argv[sys.argv.index("--write-pools") + 1]
        nums = lambda f: sorted(int(n) for n, r in d.items() if f(r))
        pools = {
            "significant_red": nums(lambda r: r.get("significant_red")),
            "exact_pair": nums(lambda r: profile(r) == pair),
            "year_1972_no_mark": nums(lambda r: r["year"] == 1972 and not r["mint_mark"]),
        }
        for k, v in pools.items():
            assert len(v) == out[k], (k, len(v), out[k])
            assert 8820 in v, k
        json.dump(pools, open(dest, "w"), indent=0)
        print("pools written:", {k: len(v) for k, v in pools.items()}, "->", dest)


if __name__ == "__main__":
    main(sys.argv[1])
