#!/usr/bin/env python3
"""Cent numbers for film B's closing shot: two 1940s Sets, one Cent per year.

The 1940s Set needs one Cent of each 1940s year the collection holds. 1943 is
absent from CENTS (steel year), so that is nine years. 1949 has exactly one
Cent, so only one of the two rows can hold it. Rows take the lowest-numbered
Cents of each year, A first, so the choice is mechanical, not curated.

  python3 films/sets-narrowing/build_data.py
"""
import collections, csv, json, pathlib, sys

FILM = pathlib.Path(__file__).resolve().parent
SRC = pathlib.Path("/mnt/project-files/knowledge/data/cents_traits.csv")

rows = list(csv.DictReader(SRC.open()))
if len(rows) != 10000: sys.exit(f"FLOOR: {len(rows)} rows in {SRC}, expected 10000")
by = collections.defaultdict(list)
for r in rows:
    y = int(r["year"])
    if 1940 <= y <= 1949: by[y].append(int(r["cent"]))
years = sorted(by)
if 1943 in years: sys.exit("1943 present: the Set definition here assumes it is not")
if len(by[1949]) != 1: sys.exit(f"1949 has {len(by[1949])} Cents; the film says one")
a = [sorted(by[y])[0] for y in years]
b = [sorted(by[y])[1] if y != 1949 else None for y in years]
out = {"_source": f"{SRC.name}, built by build_data.py", "years": years,
       "counts": {str(y): len(by[y]) for y in years}, "row_a": a, "row_b": b,
       "only_1949": by[1949][0]}
(FILM / "data/forties.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out))
