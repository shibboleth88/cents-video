"""Counts behind the #8820 script (v0.1). Run from anywhere:

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


if __name__ == "__main__":
    main(sys.argv[1])
