"""Timeline for "What should DOPEMIND add next?" (themed Collector Wall episode).

Every figure is recomputed here from the dated snapshot and checked before it is
written, so a stale number refuses instead of rendering:

    python3 -I films/wall-dopemind-next/timeline/make_timeline.py   (from the repo root)

Snapshot: /mnt/project-files/collectors/snapshots/2026-11-09/ (cents.vision, fetched
2026-11-09 15:56Z). What each suggestion would add to the card was measured by
replaying collectors.html with the Cent moved onto the Wall (see README).
"""
import collections, json, pathlib, sys

F = pathlib.Path(__file__).resolve().parents[1]
SNAP = pathlib.Path("/mnt/project-files/collectors/snapshots/2026-11-09")
m = json.load(open(SNAP / "raw/merged-new2.json"))
rp = json.load(open(SNAP / "replay.json"))
al = json.load(open(F / "script/alignment.json"))
wall = {w["name"]: w for w in rp["claimed"]}
D, CEN = wall["DOPEMIND"], wall["centoshi"]

def need(cond, msg):
    if not cond: sys.exit(f"REFUSING: {msg}")

yr = lambda n: m[str(n)]["year"]
mint = lambda n: m[str(n)]["mint_mark"]
years = collections.Counter(c["year"] for c in m.values())
PATINA = ("verdigris", "obsidian", "red", "desert")
pat = lambda n: {p for p in PATINA for k, v in m[str(n)].items() if v is True and k.endswith("_" + p)}

# --- the Wall as narrated -----------------------------------------------------
need(D["count"] == 12 and D["years"] == [1963, 1981] and D["club"] == "Dime Club", "count/span/club changed")
need(D["signature"] == 478 and yr(478) == 1963, "signature changed")
patina_cents = [n for n in D["cent_ids"] if pat(n)]
need(len(patina_cents) == 8, f"patina Cents now {len(patina_cents)}")
need(set().union(*(pat(n) for n in D["cent_ids"])) == {"verdigris", "obsidian", "desert"}, "patinas held changed")
need(D["count1969"] == 0 and D["count1971"] == 0 and D["wheat_count"] == 0, "1969/1971/wheat no longer absent")
need(1979 in {yr(n) for n in D["cent_ids"]} and 8741 in D["cent_ids"] and yr(8741) == 1979, "the Wall's 1979 changed")
need(2064 in D["cent_ids"] and yr(2064) == 1981, "the Wall's 1981 changed")
for n, p in ((951, "verdigris"), (6935, "obsidian"), (3396, "desert")):
    need(n in D["cent_ids"] and p in pat(n), f"#{n} no longer {p} on the Wall")

# --- centoshi and 1971 ------------------------------------------------------------
c71 = [n for n in CEN["cent_ids"] if yr(n) == 1971]
need(len(c71) == 16 and CEN["count1971"] == 16, "centoshi's 1971 count changed")
# "more than any other collector": every Wall (groups merged), the artist wallet excluded
wi = json.load(open(SNAP / "raw/wallet_index_cents.json")); wg = json.load(open(SNAP / "raw/wallet-groups.json"))
sec = {s: p for p, ss in wg.items() for s in ss}
walls = collections.defaultdict(list)
for w, cs in wi.items(): walls[sec.get(w, w)] += cs
artist = wall["Rutherford Chang"]["wallet"]
best_other = max(sum(yr(c) == 1971 for c in cs) for w, cs in walls.items() if w not in (artist, CEN["wallet"]))
need(best_other < 16, f"another collector holds {best_other} 1971 Cents")

# --- Daidatep's six ----------------------------------------------------------------
PICKS = [8657, 8820, 6451, 6875, 6782, 5888]
need(yr(8657) == 1965 and years[1965] == 90, "1965 count changed")
need(all(years[y] > 90 for y in range(1960, 1970) if y != 1965), "1965 is no longer the scarcest 1960s year")
need(yr(8820) == 1972 and "red" in pat(8820), "#8820 not a red 1972")
need(yr(6451) == 1980, "#6451 not 1980")
heavy = [n for n, c in m.items() if c.get("heavily_abraded")]
need(yr(6875) == 1967 and m["6875"].get("heavily_abraded") and len(heavy) == 44, "heavily abraded count changed")
need(yr(6782) == 1969 and mint(6782) == "D", "#6782 not 1969-D")
need(yr(5888) == 1956 and mint(5888) == "D", "#5888 not 1956-D")
held = {c for cs in walls.values() for c in cs}
need(all(p not in D["cent_ids"] for p in PICKS), "a pick is already on the Wall")

# --- shots ----------------------------------------------------------------------------
TOTAL = round(al["duration"] * 30)
H = lambda n: f"hires/{n}.webp"
CLIP = {"width": 1080, "height": 1920, "frames": 150, "coin": {"cx": 539.5, "cy": 959.0, "d": 775},
        "credit": "3D render: 3DCENTS by sinvalli", "credit_at_end": True}
PICKS_T = "Daidatep's picks"

shots = [
 {"shot_id": "n00_open", "start": {"at_start": True}, "end": {"at_phrase": "is number four seventy-eight"},
  "purpose": "Showcase opener (series format): the card from frame 0, #478 turning in its slot, Cents and badges lighting in turn; zoom onto the signature Cent.",
  "component": "WallOpener", "props": {"variant": "showcase", "wall": "dopemind", "show": "card", "until_phrase": "Its signature Cent",
   "moves": [{"at_phrase": "Its signature Cent", "target": {"cent": 478, "in": "signature"}, "mark": True}],
   "progress": {"total_frames": TOTAL},
   "clip": {**CLIP, "src": "3dcents/478-360-30fps-alpha.webm", "alpha": True}}},
 {"shot_id": "n01_sig", "start": {"at_phrase": "is number four seventy-eight"}, "end": {"at_phrase": "In the Numismatists Discord"}, "join_prev": True,
  "purpose": "The signature Cent #478 on its own, turning (3DCENTS). No still: no cue in this sentence lets the turn face front within 0.6-1.6x.",
  "component": "WallStandout", "props": {"title": "DOPEMIND", "n": 478, "readout": "1963", "caption": "Obsidian · Desert · Speckles",
   "clip": {**CLIP, "src": "3dcents/478-360-30fps.mp4", "sync": True, "enter_from": {"cx": 540, "cy": 800, "d": 495}}}},
 {"shot_id": "n02_ask", "start": {"at_phrase": "In the Numismatists Discord"}, "end": {"at_phrase": "As of November twenty"},
  "purpose": "The question, retyped word for word from the user's screenshot (no avatar). It shows from the start of the shot: on its cue (\"Dopemind asked\") the first render held an empty card for 1.7 s.",
  "component": "ChatCard", "props": {"title": "Numismatists Discord", "subtitle": "November 2026",
   "messages": [{"name": "DOPEMIND", "text": "What should I add to expand the set? Wondering about the direction for this collection", "at_phrase": "In the Numismatists Discord"}]}},
 {"shot_id": "n03_count", "start": {"at_phrase": "As of November twenty"}, "end": {"at_phrase": "Eight carry a patina"},
  "purpose": "All 12 Cents, counting up (snapshot 2026-11-09).",
  "component": "WallBoard", "props": {"wall": "dopemind", "show": "grid",
   "moves": [{"at_phrase": "As of November twenty", "until_phrase": "Eight carry a patina", "target": {"grid_end": True}}],
   "readout": {"at_phrase": "the Wall holds twelve", "count": {"from": 0, "to": 12, "until_phrase": "Cents, from nineteen sixty-three to", "suffix": " Cents"}}}},
 {"shot_id": "n04_patina", "start": {"at_phrase": "Eight carry a patina"}, "end": {"at_phrase": "What it does not hold"},
  "purpose": "The 8 patina Cents ringed: verdigris, obsidian, desert.",
  "component": "WallBoard", "props": {"wall": "dopemind", "show": "grid", "moves": [{"at_phrase": "Eight carry a patina", "target": {"grid_end": True}}],
   "highlights": [{"at_phrase": "Eight carry a patina", "cents": patina_cents}],
   "readout": {"at_phrase": "Eight carry a patina", "text": "8 of 12"}}},
 {"shot_id": "n05_gaps", "start": {"at_phrase": "What it does not hold"}, "end": {"at_phrase": "centoshi replied"},
  "purpose": "What the Wall does not hold, each ring arriving as it is named.",
  "component": "GapSlots", "props": {"title": "DOPEMIND", "subtitle": "Not on the Wall", "cols": 2,
   "slots": [{"label": "Red", "sub": "patina", "appear_at": "hold: a red patina"}, {"label": "Wheat", "sub": "penny", "appear_at": "a wheat penny, or"},
             {"label": "1969", "appear_at": "Cent from nineteen sixty-nine or"}, {"label": "1971", "appear_at": "sixty-nine or nineteen seventy-one"}]}},
 {"shot_id": "n06_centoshi", "start": {"at_phrase": "centoshi replied"}, "end": {"at_phrase": "centoshi holds sixteen"},
  "purpose": "centoshi's reply and DOPEMIND's answer, retyped word for word.",
  "component": "ChatCard", "props": {"title": "Numismatists Discord", "subtitle": "November 2026", "textSize": 64,
   "messages": [{"name": "centoshi", "text": "You already know my answer", "at_phrase": "centoshi replied"},
                {"name": "DOPEMIND", "text": "1971", "at_phrase": "Dopemind wrote back"}]}},
 {"shot_id": "n07_c71", "start": {"at_phrase": "centoshi holds sixteen"}, "end": {"at_phrase": "Of nineteen seventy-one, Martin"},
  "purpose": "centoshi's Wall: its 16 Cents from 1971 ringed (most of any collector; artist wallet excluded).",
  "component": "WallBoard", "props": {"wall": "centoshi", "show": "grid",
   "moves": [{"at_phrase": "centoshi holds sixteen", "until_phrase": "more than any other", "target": {"grid_end": True}}],
   "highlights": [{"at_phrase": "centoshi holds sixteen", "group": "y1971"}],
   "readout": {"at_phrase": "centoshi holds sixteen", "text": "16 from 1971"}}},
 {"shot_id": "n08_lehnen", "start": {"at_phrase": "Of nineteen seventy-one, Martin"}, "end": {"at_phrase": "A nineteen seventy-one Cent would"},
  "purpose": "NYT front page, 16 Aug 1971 (cleared by the user); Lehnen's line, verbatim from 'CENTS – Reflections on Mint Years' (Medium, 8 Mar 2025).",
  "component": "QuoteOver", "props": {"title": "1971", "subtitle": "The year money left gold",
   "src": "assets/dopemind/nyt_1971_crop.jpg", "img_w": 713, "img_h": 391, "img_caption": "The New York Times, 16 August 1971",
   "quote": "“It was the year the United States abandoned the gold standard, severing the connection between currency and tangible value…”",
   "attribution": "Martin Lehnen, 2025", "quote_at": "It was the year", "quoteSize": 50}},
 {"shot_id": "n09_chronicle", "start": {"at_phrase": "A nineteen seventy-one Cent would"}, "end": {"at_phrase": "Daidatep suggested six"},
  "purpose": "A 1971 adds the 1971 Club badge; Chronicle = 1971 + 1979 + 1982, the Wall has the 1979 (#8741). Measured by replay: +1971 adds '1971 1'; +1971 +1982 adds Chronicle Set.",
  "component": "GapSlots", "props": {"title": "DOPEMIND", "subtitle": "Chronicle Set",
   "slots": [{"label": "1971", "appear_at": "A nineteen seventy-one Cent would"},
             {"label": "1979", "sub": "#8741", "src": H(8741), "fill_at": "With the Wall's nineteen seventy-nine", "appear_at": "With the Wall's nineteen seventy-nine"},
             {"label": "1982", "appear_at": "Chronicle Set one nineteen eighty-two"}],
   "readouts": [{"at_phrase": "Cent would add the nineteen seventy-one", "text": "1971 Club", "caption": "a badge for a Cent from 1971"},
                {"at_phrase": "leave a Chronicle Set", "text": "Chronicle", "caption": "1971 + 1979 + 1982"}]}},
 {"shot_id": "n10_daidatep", "start": {"at_phrase": "Daidatep suggested six"}, "end": {"at_phrase": "Number eighty-six fifty-seven"},
  "purpose": "Daidatep's reply, retyped word for word (emoji left out).",
  "component": "ChatCard", "props": {"title": "Numismatists Discord", "subtitle": "November 2026", "textSize": 50,
   "messages": [{"name": "Daidatep", "text": "Right now I would have a look at: #8657 (only 90 1965 in the collection), #8820, #6451, #6875, #6782, #5888, … I could go on and on", "at_phrase": "Daidatep suggested six"}]}},
 {"shot_id": "n11_8657", "start": {"at_phrase": "Number eighty-six fifty-seven"}, "end": {"at_phrase": "Only ninety Cents are"},
  "purpose": "#8657, zoom to its date.", "component": "WallStandout",
  "props": {"title": PICKS_T, "subtitle": "CENT #8657 · 1 of 6", "n": 8657, "readout": "1965", "caption": "No mint mark", "src": H(8657),
            "zoom": {"at_phrase": "is from nineteen sixty-five", "box": [0.63, 0.57, 0.88, 0.72], "mark": True}}},
 {"shot_id": "n12_years", "start": {"at_phrase": "Only ninety Cents are"}, "end": {"at_phrase": "Number eighty-eight twenty"},
  "purpose": "Cents per year in the 1960s (merged-new2.json, 2026-11-09): 1965 has the fewest, 90.",
  "component": "YearBars", "props": {"title": "CENTS by year", "subtitle": "the 1960s", "highlight": "1965", "highlight_at": "Only ninety Cents are",
   "bars": [{"label": str(y), "value": years[y]} for y in range(1960, 1970)],
   "readouts": [{"at_phrase": "Only ninety Cents are", "text": "90", "caption": "the fewest of any 1960s year"}]}},
 {"shot_id": "n13_8820", "start": {"at_phrase": "Number eighty-eight twenty"}, "end": {"at_phrase": "With all four base patinas"},
  "purpose": "#8820, red patina (whole surface: no zoom).", "component": "WallStandout",
  "props": {"title": PICKS_T, "subtitle": "CENT #8820 · 2 of 6", "n": 8820, "readout": "1972", "caption": "Red patina", "src": H(8820)}},
 {"shot_id": "n14_patinaset", "start": {"at_phrase": "With all four base patinas"}, "end": {"at_phrase": "Number sixty-four fifty-one"},
  "purpose": "The Wall's verdigris, obsidian and desert, then #8820's red drops in: Patina Set (replay: +8820 adds 'Patina Set').",
  "component": "GapSlots", "props": {"title": "DOPEMIND", "subtitle": "Patina Set", "cols": 4,
   "slots": [{"label": "Verd.", "sub": "#951", "src": H(951)}, {"label": "Obs.", "sub": "#6935", "src": H(6935)},
             {"label": "Desert", "sub": "#3396", "src": H(3396)}, {"label": "Red", "sub": "#8820", "src": H(8820), "fill_at": "With all four base patinas"}],
   "readouts": [{"at_phrase": "add a Patina Set", "text": "Patina Set", "caption": "all four base patinas"}]}},
 {"shot_id": "n15_6451", "start": {"at_phrase": "Number sixty-four fifty-one"}, "end": {"at_phrase": "With the Wall's nineteen eighty-one"},
  "purpose": "#6451, zoom to its date.", "component": "WallStandout",
  "props": {"title": PICKS_T, "subtitle": "CENT #6451 · 3 of 6", "n": 6451, "readout": "1980", "caption": "Obsidian patina", "src": H(6451),
            "zoom": {"at_phrase": "is from nineteen eighty", "box": [0.63, 0.56, 0.88, 0.71], "mark": True}}},
 {"shot_id": "n16_1980s", "start": {"at_phrase": "With the Wall's nineteen eighty-one"}, "end": {"at_phrase": "Number sixty-eight seventy-five"},
  "purpose": "1980s Set = 1980, 1981, 1982; the Wall has 1981 (#2064). Replay: +6451 +1982 adds '1980s Set'.",
  "component": "GapSlots", "props": {"title": "DOPEMIND", "subtitle": "1980s Set",
   "slots": [{"label": "1980", "sub": "#6451", "src": H(6451)},
             {"label": "1981", "sub": "#2064", "src": H(2064), "fill_at": "With the Wall's nineteen eighty-one", "appear_at": "With the Wall's nineteen eighty-one"},
             {"label": "1982", "appear_at": "eighties Set one nineteen eighty-two"}],
   "readouts": [{"at_phrase": "leave a nineteen-eighties Set", "text": "1980s Set", "caption": "1980 + 1981 + 1982"}]}},
 {"shot_id": "n17_6875", "start": {"at_phrase": "Number sixty-eight seventy-five"}, "end": {"at_phrase": "In the Traits Atlas"},
  "purpose": "#6875, zoom onto the gouge.", "component": "WallStandout",
  "props": {"title": PICKS_T, "subtitle": "CENT #6875 · 4 of 6", "n": 6875, "readout": "1 of 44", "caption": "Heavily abraded", "src": H(6875),
            "zoom": {"at_phrase": "is heavily abraded", "box": [0.6, 0.15, 0.9, 0.55], "mark": True}}},
 {"shot_id": "n18_atlas", "start": {"at_phrase": "In the Traits Atlas"}, "end": {"at_phrase": "Number sixty-seven eighty-two"},
  "purpose": "The Atlas's Heavy grade, verbatim (films/traits/script/atlas/abraded.txt).",
  "component": "QuoteOver", "props": {"title": PICKS_T, "subtitle": "CENT #6875 · 1967", "cent": H(6875),
   "quote": "Heavy: “abrasion dominates the read of the coin; broad fields/devices visibly missing metal.”",
   "attribution": "Traits Atlas, CENTS Trait Council", "quote_at": "heavy abrasion", "quoteSize": 52}},
 {"shot_id": "n19_6782", "start": {"at_phrase": "Number sixty-seven eighty-two"}, "end": {"at_phrase": "And number fifty-eight eighty-eight"},
  "purpose": "#6782, zoom to its date and D mint mark; replay: +6782 adds '1969 1'.", "component": "WallStandout",
  "props": {"title": PICKS_T, "subtitle": "CENT #6782 · 5 of 6", "n": 6782, "readout": "1969-D", "caption": "Would add the 1969 Club", "src": H(6782),
            "zoom": {"at_phrase": "a nineteen sixty-nine from Denver", "box": [0.62, 0.56, 0.87, 0.76], "mark": True}}},
 {"shot_id": "n20_5888", "start": {"at_phrase": "And number fifty-eight eighty-eight"}, "end": {"at_phrase": "Find all of the Collector"},
  "purpose": "#5888 turns to its back: the wheat ears (replay: +5888 adds 'Wheat 1', years 1956-1981).", "component": "CentFlip",
  "props": {"title": PICKS_T, "subtitle": "CENT #5888 · 6 of 6", "n": 5888, "front": H(5888), "back": "hires/5888_back.webp",
            "flip_at": "Wall's first wheat penny", "readout": "1956-D", "caption": "Wheat penny"}},
 {"shot_id": "n21_collectors", "start": {"at_phrase": "Find all of the Collector"}, "end": {"at_phrase": "What should Dopemind add"},
  "purpose": "cents.vision Traits Lab; one zoom, onto Collectors.", "component": "WallShot",
  "props": {"src": "vision/traits_lab.png", "width": 2964, "height": 1654, "moves": [{"at_phrase": "under Collectors", "box": [1185, 1575, 1358, 1635], "mark": True}]}},
 {"shot_id": "n22_ask", "start": {"at_phrase": "What should Dopemind add"}, "end": {"after_phrase": "Tell us what you think", "plus": 2.0},
  "purpose": "The question to viewers, over the options the film put forward.", "component": "AskCard",
  "props": {"question": "What should DOPEMIND add next?", "cols": 4, "note": "Tell us what you think",
   "options": [{"label": "1971"}] + [{"label": f"#{n}", "src": H(n)} for n in PICKS]}},
 {"shot_id": "n23_credits", "start": {"after_phrase": "Tell us what you think", "plus": 2.0}, "end": {"at_end": True},
  "purpose": "End credits.", "component": "Credits",
  "props": {"lines": ["Images: Rutherford Chang via cents.vision (site by Dr. Martin Lehnen)",
                      "3D render: 3DCENTS by sinvalli",
                      "Quote: Martin Lehnen, “CENTS – Reflections on Mint Years”, March 2025",
                      "Trait grade: Traits Atlas, CENTS Trait Council",
                      "Front page: The New York Times, 16 August 1971",
                      "Collector Wall data: cents.vision, as of 9 November 2026"], "url": "cents.gallery"}},
]
for s in shots: s["visual_kind"] = "code"
tl = {"essay": {"title": "Collector Wall", "subtitle": "DOPEMIND: what to add next", "author": "shibboleth",
                "source": "https://cents.vision/collectors.html", "version": "v1 (2026-11-09)"},
      "_what": "Themed Collector Wall episode around DOPEMIND's question in the Numismatists Discord. Every coin is a real Cent by number; every figure is checked above against the 2026-11-09 snapshot. No wallet address appears.",
      "shots": shots}
json.dump(tl, open(F / "timeline/timeline.json", "w"), indent=1, ensure_ascii=False)
json.dump({"assets": {}, "_note": "No Plate assets. QuoteOver draws public/assets/dopemind/nyt_1971_crop.jpg (NYT front page, 16 Aug 1971, supplied and cleared by the user in the Cent #1264 thread; cropped below the masthead to drop browser controls)."},
          open(F / "timeline/assets.json", "w"), indent=1)
print(f"{len(shots)} shots; all figures checked against {SNAP.name}")
