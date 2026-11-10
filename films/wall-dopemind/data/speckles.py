"""The Speckles narrowing in v2, from the dated snapshot's merged-new2.json. Writes data/speckles.json.

  95 Cents carry Speckles -> 70 of them carry obsidian (any grade) -> 5 carry significant obsidian
  -> only #478 also carries desert.  Obsidian over all 10,000: 1,757 (17.6%, "fewer than one in five").

"Significant" is the exact grade (notable < significant < full), as the script says it. The uniqueness
line ("No other Cent of the ten thousand carries all three") is measured under every reading a viewer
could give it, and the script refuses unless each one is #478 alone:
  Speckles + significant obsidian + desert (any grade)        -- the sentence before it
  Speckles + significant obsidian + notable desert            -- #478's exact grades, as the film opens
  Speckles + obsidian at significant or above + desert (any)  -- "significant" heard as "at least"
The looser reading (obsidian of any grade) is printed, not claimed.

    python3 -I films/wall-dopemind/data/speckles.py /mnt/project-files/collectors/snapshots/2026-11-09 [--control]

`--control` gives #2900 (Speckles, significant obsidian, no desert) a notable desert and must fail.
"""
import json, sys, pathlib
F = pathlib.Path(__file__).resolve().parent
snap = pathlib.Path(sys.argv[1])
d = json.load(open(snap / "raw/merged-new2.json"))
if len(d) != 10000: sys.exit(f"REFUSING: {len(d)} Cents in merged-new2.json, not 10,000")
if "--control" in sys.argv: d["2900"] = dict(d["2900"], notable_desert=True)
G = ("notable", "significant", "full")
has = lambda c, t, grades=G: any(c.get(f"{g}_{t}") for g in grades)
sp = sorted(int(n) for n, c in d.items() if "Speckles" in (c.get("contaminated") or []))
obs_all = [n for n, c in d.items() if has(c, "obsidian")]
sp_obs = [n for n in sp if has(d[str(n)], "obsidian")]
sp_sig = [n for n in sp if d[str(n)].get("significant_obsidian")]
floor = {"speckles": len(sp), "obsidian (all Cents)": len(obs_all), "speckles + obsidian": len(sp_obs), "speckles + significant obsidian": len(sp_sig)}
if min(floor.values()) == 0: sys.exit(f"INSTRUMENT: a count of zero, the scan is broken: {floor}")
readings = {
    "speckles + significant obsidian + desert (any)": [n for n in sp_sig if has(d[str(n)], "desert")],
    "speckles + significant obsidian + notable desert": [n for n in sp_sig if d[str(n)].get("notable_desert")],
    "speckles + obsidian >= significant + desert (any)": [n for n in sp if has(d[str(n)], "obsidian", G[1:]) and has(d[str(n)], "desert")],
}
loose = [n for n in sp_obs if has(d[str(n)], "desert")]
for k, v in readings.items(): print(f"{k}: {v}")
print(f"(not claimed) speckles + obsidian (any) + desert (any): {len(loose)} {loose}")
bad = {k: v for k, v in readings.items() if v != [478]}
if bad:
    if "--control" in sys.argv: print(f"control failed as it must: {bad}"); sys.exit(0)
    sys.exit(f"REFUSING: 'no other Cent carries all three' is false under {bad}")
if "--control" in sys.argv: sys.exit("CONTROL PASSED, which it must not")
print(f"speckles {len(sp)}, with obsidian {len(sp_obs)}, with significant obsidian {len(sp_sig)} {sp_sig}; "
      f"obsidian over all: {len(obs_all)} ({len(obs_all) / 100:.1f}%)")
json.dump({"_source": f"merged-new2.json, snapshot {snap.name} (Contaminated: Speckles; obsidian any grade; significant = exact grade); data/speckles.py",
           "speckles": sp, "speckles_obsidian": sp_obs, "speckles_significant_obsidian": sp_sig,
           "obsidian_all": len(obs_all)}, open(F / "speckles.json", "w"), indent=1)
