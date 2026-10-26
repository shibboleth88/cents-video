#!/usr/bin/env python3
"""Snapshot one claimed Collector Wall for the WallBoard component.

Reads the project's Collector Wall data (/mnt/project-files/collectors/) and
writes films/wall-<slug>/data/wall_board.json plus its public copy
public/walls/<slug>.json, which WallBoard fetches at render time.

    python3 pipeline/wall_board.py --name Daidatep --slug daidatep --as-of 2026-10-25
    python3 pipeline/wall_board.py --self-test

What goes in is only what the claimed Wall shows: the name as rendered, the
signature, the Cents in the page's order, the badges exactly as the card renders
them, and the groups of Cents behind each badge so a shot can highlight them.
NO wallet address: every string is scanned before writing, and the script refuses
if anything looks like one.

Each group is checked against the badge text it explains (Wheat 10 must have ten
wheat Cents, "1971 4" four Cents from 1971, ...), so a highlight can never
disagree with the badge on screen.
"""
import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = Path("/mnt/project-files/collectors")
FULLS = ["verdigris", "obsidian", "red", "desert", "gold"]
WALLETISH = re.compile(r"^(bc1|tb1|[13][a-km-zA-HJ-NP-Z1-9]{25,})", re.I)


def label(trait: str) -> str:
    return trait.replace("_", " ").title()


def build(rec: dict, meta: dict, as_of: str) -> dict:
    ids = sorted(rec["cent_ids"])          # the page's "View collection" grid is ascending
    cm = {n: meta[str(n)] for n in ids}
    groups = {
        "wheat": [n for n in ids if cm[n]["year"] <= 1958],
        "y1971": [n for n in ids if cm[n]["year"] == 1971],
        "y1969": [n for n in ids if cm[n]["year"] == 1969],
        "one_of_one_year": rec["one_of_one"]["year"],
        "one_of_one_mint": rec["one_of_one"]["mint"],
        "trait_combo": rec["one_of_one"]["trait_combo"],
        "mint_keeper": rec["mint_keeper_cents"],
        "full_mint": rec["sets"].get("full_mint_cent_ids", []),
    }
    for p in FULLS:
        groups[f"full_{p}"] = [n for n in ids if cm[n].get(f"full_{p}")]
    groups["full_any"] = sorted({n for p in FULLS for n in groups[f"full_{p}"]})
    contam = {}
    for n in ids:
        for t in cm[n].get("contaminated") or []:
            contam.setdefault(t, []).append(n)
    groups["contamination"] = contam                       # type -> Cents
    groups["contamination_one_each"] = [v[0] for _, v in sorted(contam.items())]

    r = rec["rendered"]
    fulls = [f"Full {p.title()} x {len(groups[f'full_{p}'])}" for p in FULLS if groups[f"full_{p}"]]
    board = {
        "_source": f"claimed_walls.json + raw/merged-new2.json via pipeline/wall_board.py; as of {as_of}",
        "as_of": as_of,
        "name": rec["name"],
        "signature": rec["signature"],
        "count": rec["count"],
        "mosaic": rec["mosaic"],
        "cents": ids,
        "years": {str(n): cm[n]["year"] for n in ids},
        "badges": {"tags": r["trait_tags"], "sets": r["set_badges"], "fulls": fulls, "meta": r["meta_badges"]},
        "groups": groups,
    }
    check(board, rec)
    return board


def check(b: dict, rec: dict) -> None:
    errs = []
    if b["count"] != len(b["cents"]): errs.append(f"count {b['count']} != {len(b['cents'])} Cents")
    if b["signature"] not in b["cents"]: errs.append("signature Cent not on the Wall")
    meta = b["badges"]["meta"]
    def badge_n(prefix):
        hits = [m for m in meta if m.startswith(prefix)]
        if not hits: return 0
        if len(hits) > 1: errs.append(f"{len(hits)} badges start with {prefix!r}")
        t = hits[0]
        if prefix.endswith(" ") or " x " in t: return int(t.split()[-1])   # "Wheat 10", "Mint Keeper x 2"
        return 1                                                              # "1/1 Mint" alone means one
    for prefix, g in [("Wheat ", "wheat"), ("1971 ", "y1971"), ("1969 ", "y1969"),
                      ("1/1 Mint", "one_of_one_mint"), ("1/1 Year", "one_of_one_year"),
                      ("1/1 Trait Combo", "trait_combo"), ("Mint Keeper", "mint_keeper")]:
        want, got = badge_n(prefix), len(b["groups"][g])
        if want != got: errs.append(f"badge {prefix.strip()!r} says {want}, group {g} has {got}")
    full_tag = [t for t in b["badges"]["tags"] if t.startswith("Full x ")]
    if full_tag and int(full_tag[0].split()[-1]) != len(b["groups"]["full_any"]):
        errs.append(f"{full_tag[0]!r} but {len(b['groups']['full_any'])} Cents carry a full patina")
    for s in json.dumps(b).replace('"', " ").split():
        if WALLETISH.match(s.strip(",:[]{}")): errs.append(f"wallet-like string {s[:12]}...")
    if errs:
        sys.exit("REFUSING:\n  " + "\n  ".join(errs))


def load_walls() -> list:
    w = json.load(open(DATA / "claimed_walls.json"))
    return w["walls"] if isinstance(w, dict) else w


def self_test() -> None:
    meta = json.load(open(DATA / "raw/merged-new2.json"))
    walls = load_walls()
    ok = 0
    for rec in walls:
        build(rec, meta, "test"); ok += 1
    print(f"all {ok} claimed Walls build and pass their badge checks")
    # Controls: each must refuse.
    rec = dict(next(w for w in walls if w["name"] == "Daidatep"))
    bad = dict(rec, rendered=dict(rec["rendered"], meta_badges=[m.replace("Wheat 10", "Wheat 11") for m in rec["rendered"]["meta_badges"]]))
    for name, r in [("wrong Wheat count", bad), ("wallet leaks into a badge",
                    dict(rec, rendered=dict(rec["rendered"], trait_tags=rec["rendered"]["trait_tags"] + [rec["wallet"]])))]:
        try:
            build(r, meta, "test"); print(f"CONTROL FAILED to go red: {name}"); sys.exit(1)
        except SystemExit as e:
            if e.code == 1: raise
            print(f"control red as it should be: {name}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name"); ap.add_argument("--slug"); ap.add_argument("--as-of")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test: return self_test()
    meta = json.load(open(DATA / "raw/merged-new2.json"))
    recs = [w for w in load_walls() if w["name"] == a.name]
    if len(recs) != 1: sys.exit(f"{len(recs)} claimed Walls named {a.name!r}")
    gen = json.load(open(DATA / "claimed_walls.json")).get("generated_at", "")
    board = build(recs[0], meta, a.as_of or gen[:10])
    for out in [ROOT / f"films/wall-{a.slug}/data/wall_board.json", ROOT / f"public/walls/{a.slug}.json"]:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(board, indent=1))
        print("wrote", out.relative_to(ROOT))
    print(f"{board['name']}: {board['count']} Cents; stage them with pipeline/stage_cents.py")


if __name__ == "__main__":
    main()
