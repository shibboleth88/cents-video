"""Write timeline/timeline.json for Cent #2616 v2 (script v0.4, eee v4 take 1).

Order (user, 2026-10-27): the 1/1 Year first, then the mint-year charts and the
Lehnen quotes, then the traits, the Full Red pool, the value tie and the closing
card with its closing line. Shot props that v1 measured (coin centre, trait boxes,
the two Cent lists) are read from v1's timeline in git, not retyped.

    python3 -I films/onecent-2616/timeline/build_timeline.py   (from the repo root)
"""
import json, pathlib, subprocess
F = pathlib.Path(__file__).resolve().parents[1]
v1 = {s["shot_id"]: s for s in json.loads(subprocess.run(
    ["git", "show", "17489b4:films/onecent-2616/timeline/timeline.json"], cwd=F, capture_output=True, text=True, check=True).stdout)["shots"]}
open_ = v1["s01_open"]["props"]
COIN = {k: open_[k] for k in ("inscription", "n", "front")}
moves = {m["at_phrase"]: m for m in open_["moves"]}
reads = {r["at_phrase"]: r for r in open_["reads"]}
LEHNEN_MINT = "In the words of Martin Lehnen, in his essay Reflections"

def shot(sid, start, end, comp, props, purpose):
    return {"shot_id": sid, "start": start, "end": end, "purpose": purpose, "visual_kind": "code", "component": comp, "props": props}
at = lambda p: {"at_phrase": p}

shots = [
    shot("s01_open", {"at_start": True}, at("One of twelve one-of-one"), "CentLook",
         {**COIN, "spin": open_["spin"], "moves": [moves["The only Cent"]],
          "reads": [reads["struck in nineteen twelve"], reads["The only Cent"]]},
         "Standard opening (v1 measurements): the 3DCENTS turn, then the 1050px front; the date ringed on 'The only Cent'."),
    shot("s02_ones", at("One of twelve one-of-one"), at("Scarcity written by"), "CentScroll",
         {**v1["s06_ones"]["props"], "until": "Scarcity written by"},
         v1["s06_ones"]["purpose"] + " Moved first in v2: the rarer quality leads (user, 2026-10-27)."),
    shot("s03_concept", at("Scarcity written by"), at("Among the ten thousand"), "CentLook",
         {**COIN, "concept": {"at_phrase": "Scarcity written by", "label": "Scarcity written by survival"}},
         "Concept C57 named on screen."),
    shot("s04_charts", at("Among the ten thousand"), at(LEHNEN_MINT), "MintRing",
         {"title": "Mint years", "subtitle": "After charts by @daidatep", "n": 2616, "front": "hires/2616.webp", "total": 10000,
          "steps": [{"before": 1970, "count": 2126, "pct": "21.26%"},
                    {"at_phrase": "Before nineteen sixty", "before": 1960, "count": 291, "pct": "2.91%"},
                    {"at_phrase": "Before nineteen fifty", "before": 1950, "count": 96, "pct": "0.96%"},
                    {"at_phrase": "Before nineteen forty", "before": 1940, "count": 26, "pct": "0.26%"}]},
         "The mint-year charts by @daidatep from Lehnen's 'Reflections on Mint Years' (Medium, 8 Mar 2025), redrawn for the tall frame "
         "(user, 2026-10-27: the wide originals were too small): one ring around #2616 that shrinks step by step. Counts measured on "
         "knowledge/data/cents_traits.csv: 2,126 / 291 / 96 / 26 of 10,000, matching the charts' percentages; MintRing refuses a percentage that does not match its count. "
         "The 2.08% Wheat step is skipped, as the narration skips it."),
    shot("s05_quote_mint", at(LEHNEN_MINT), at("And of the one-of-one"), "CentLook",
         {**COIN, "quote": {"at_phrase": "This data reveals", "text": "This data reveals how quickly scarcity accelerates the further back in time you go.",
                            "credit": "Martin Lehnen, Reflections on Mint Years"}},
         "Lehnen quote (C57), check_quotes.py: FOUND (cents.gallery Trait Council text)."),
    shot("s06_quote_ones", at("And of the one-of-one"), at("Its surface has"), "CentLook",
         {**COIN, "quote": v1["s07_quote"]["props"]["quote"]}, v1["s07_quote"]["purpose"]),
    shot("s07_traits", at("Its surface has"), at("Seventy-one Cents are"), "CentLook",
         {**COIN, "moves": [moves["Its surface has"], moves["full means red"], moves["Across Lincoln's head"]],
          "reads": [reads[k] for k in ("Its surface has", "full means red", "Across Lincoln's head", "Significant means a")]},
         "The trait zooms of v1, front only: the Full Red field, then the verdigris on head and shoulder."),
    shot("s08_scroll", at("Seventy-one Cents are"), at("This is the oldest"), "CentScroll", v1["s02_scroll"]["props"], v1["s02_scroll"]["purpose"]),
    shot("s09_oldest", at("This is the oldest"), at("Coin collecting turned"), "CentDissolve", v1["s03_oldest"]["props"], v1["s03_oldest"]["purpose"]),
    shot("s10_value", at("Coin collecting turned"), {"after_phrase": "these fiat coins", "plus": 0.8}, "CentLook", v1["s08_value"]["props"], v1["s08_value"]["purpose"]),
    {**v1["s09_card"], "shot_id": "s11_card", "purpose": "The opening card again, held for one full turn (150 frames), with the closing line (user, 2026-10-27) spoken over it."},
    {**v1["s10_credits"], "shot_id": "s12_credits", "props": {**v1["s10_credits"]["props"], "lines": [
        "Images: Rutherford Chang via cents.vision (site by Dr. Martin Lehnen)",
        "3D Cent render from 3DCENTS.vercel.app (site by sinvalli)",
        "Trait names and grades: the CENTS Trait Council, Traits Atlas",
        "Mint-year charts after @daidatep",
        "Quotes: Martin Lehnen, “Reflections on Mint Years”",
        "Quote: Dagmar, MAKES CENTS interview"]}},
]
tl = {"essay": {**json.loads(subprocess.run(["git", "show", "17489b4:films/onecent-2616/timeline/timeline.json"], cwd=F,
                capture_output=True, text=True, check=True).stdout)["essay"], "version": "v2, script v0.4 (2026-10-27)",
                "source": "/mnt/project-files/single-cent-series/2616/2616_script_v0.4.md"},
      "_what": "Cent #2616. Concepts C57 (primary) and C26 (value tie). Every count from the Sep 2026 trait export. Traits are read from the front only.",
      "shots": shots}
json.dump(tl, open(F / "timeline/timeline.json", "w"), indent=1, ensure_ascii=False)
print(len(shots), "shots")
