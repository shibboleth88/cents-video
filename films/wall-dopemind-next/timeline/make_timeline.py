"""Timeline for "What should DOPEMIND add next?", v2: the first film in the "What to
add next" format (user, 2026-11-09): a collector's own question, the real Discord
screenshots read in zoomed sections, then what is listed and what is interesting
about each suggested Cent.

Every figure is recomputed here from the dated snapshots and checked before it is
written, so a stale number refuses instead of rendering:

    python3 -I films/wall-dopemind-next/timeline/make_timeline.py   (from the repo root)

Snapshots: /mnt/project-files/collectors/snapshots/2026-11-09/ (cents.vision, fetched
2026-11-09 15:56Z) and its listings/listings_redacted.json (GET /api/listings,
18:52Z, prices and addresses removed). v1's timeline is make_timeline_v1.py.
"""
import collections, json, pathlib, sys

F = pathlib.Path(__file__).resolve().parents[1]
SNAP = pathlib.Path("/mnt/project-files/collectors/snapshots/2026-11-09")
m = json.load(open(SNAP / "raw/merged-new2.json"))
rp = json.load(open(SNAP / "replay.json"))
lst = json.load(open(SNAP / "listings/listings_redacted.json"))
al = json.load(open(F / "script/alignment.json"))
sims = json.load(open(F / "data/sim/sims.json"))
wall = {w["name"]: w for w in rp["claimed"]}
D, CEN = wall["DOPEMIND"], wall["centoshi"]

def need(cond, msg):
    if not cond: sys.exit(f"REFUSING: {msg}")

yr = lambda n: m[str(n)]["year"]
mint = lambda n: m[str(n)]["mint_mark"]
traits = lambda n: {k for k, v in m[str(n)].items() if v is True}
years = collections.Counter(c["year"] for c in m.values())
pool = lambda *ts: sorted(int(n) for n, c in m.items() if all(c.get(t) is True for t in ts))
VISUAL = {"ghost", "faceless", "vandalized", "assassin", "fingerprint", "striated", "lustrous", "wheat"}  # flags that are traits too

# --- the Wall and centoshi, as narrated -----------------------------------------
need(D["count"] == 12 and D["years"] == [1963, 1981], "DOPEMIND's count or span changed")
need(D["count1971"] == 0 and D["count1969"] == 0 and D["wheat_count"] == 0, "the Wall now holds a 1971, a 1969 or a wheat penny")
c71 = [n for n in CEN["cent_ids"] if yr(n) == 1971]
need(len(c71) == 16, "centoshi's 1971 count changed")
wi = json.load(open(SNAP / "raw/wallet_index_cents.json")); wg = json.load(open(SNAP / "raw/wallet-groups.json"))
sec = {s: p for p, ss in wg.items() for s in ss}
walls = collections.defaultdict(list)
for w, cs in wi.items(): walls[sec.get(w, w)] += cs
artist = wall["Rutherford Chang"]["wallet"]          # the artist wallet is not a collector (brief §2)
best_other = max(sum(yr(c) == 1971 for c in cs) for w, cs in walls.items() if w not in (artist, CEN["wallet"]))
need(best_other < 16, f"another collector holds {best_other} 1971 Cents")

# --- listings, 9 November 2026 ------------------------------------------------------
need(lst["fetched_at"].startswith("2026-11-09"), "listings snapshot is not from 9 November 2026")
listed = {r["cent"] for r in lst["listings"]}
need(all("price" not in k.lower() and "address" not in k.lower() for r in lst["listings"] for k in r), "listings file carries prices or addresses")
L71 = sorted(n for n in listed if yr(n) == 1971)
need(L71 == [2779, 5298, 8556], f"listed 1971s are now {L71}")
need(years[1971] == 362, "1971 count changed")
PICKS = [8657, 8820, 6451, 6875, 6782, 5888]
need(all(p in listed for p in PICKS), "a pick is no longer in the listings snapshot")
need(all(p not in D["cent_ids"] for p in PICKS + L71), "a Cent shown is already on the Wall")

# --- the three listed 1971s ------------------------------------------------------------
GD = pool("ghost", "full_desert")
need(traits(2779) == {"ghost", "full_desert"} and len(GD) == 13 and 2779 in GD, "#2779 / Ghost + Full Desert changed")
need(mint(8556) == "D" and traits(8556) == {"significant_verdigris"} and m["8556"].get("contaminated") == ["Alien Secretion"], "#8556 changed")
need(traits(5298) == set() and not m["5298"].get("contaminated"), "#5298 now carries a trait")
G = ("set_badges", "meta_badges", "trait_tags")
badges = lambda key: {x for g in G for x in sims[key]["rendered"][g]}
added = lambda key: badges(key) - badges("baseline")
need(added("+1971") == {"1971 1"}, "replay: a 1971 (#149 in the replay; the badge goes by year) no longer adds only the 1971 Club badge")

# --- Daidatep's six --------------------------------------------------------------------
need(yr(8657) == 1965 and traits(8657) == {"notable_desert"}, "#8657 changed")
need(years[1965] == 90 and all(years[y] > 90 for y in range(1960, 1970) if y != 1965), "1965 is no longer the scarcest 1960s year at 90")
need(all(c["mint_mark"] in (None, "") for c in m.values() if c["year"] == 1965), "a 1965 Cent now carries a mint mark")
need(yr(8820) == 1972 and traits(8820) == {"notable_verdigris", "significant_red"} and len(pool("significant_red")) == 183, "#8820 / significant red changed")
need(yr(6451) == 1980 and traits(6451) == {"significant_obsidian"} and len(pool("significant_obsidian")) == 220, "#6451 / significant obsidian changed")
need(yr(6875) == 1967 and traits(6875) == {"heavily_abraded"} and len(pool("heavily_abraded")) == 44, "#6875 / heavy abrasion changed")
need(yr(6782) == 1969 and mint(6782) == "D" and traits(6782) == {"notable_obsidian", "significant_verdigris"}, "#6782 changed")
need(yr(5888) == 1956 and mint(5888) == "D" and traits(5888) == {"notable_verdigris"}, "#5888 changed")
Y56 = sorted(int(n) for n, c in m.items() if c["year"] == 1956)
need(len(Y56) == 28 and sum(mint(n) == "D" for n in Y56) == 18, "1956 counts changed")
for key, badge in (("+8820", "Patina Set"), ("+6782", "1969 1"), ("+5888", "Wheat 1")):
    need(badge in added(key), f"replay: {key} no longer adds {badge}")

# Inscription numbers, for the name band (knowledge/data/cents_traits.csv, the trait export).
import csv
CSV = {int(r["cent"]): r["inscription_number"] for r in csv.DictReader(open("/mnt/project-files/knowledge/data/cents_traits.csv"))}
INS = {n: m[str(n)]["inscription_number"] for n in L71 + PICKS}
for n in INS:   # two sources, both required to agree for every Cent named
    need(CSV[n] and int(CSV[n]) == INS[n], f"#{n}: inscription numbers disagree ({CSV[n]!r} vs {INS[n]})")

# --- shots ----------------------------------------------------------------------------
H = lambda n: f"hires/{n}.webp"
DS = "assets/dopemind/"
DATE = lambda n: [0.62, 0.56, 0.87, 0.75]    # date (and mint mark, or the empty place for one): measured on each photo, same place on all nine
def look(n, moves, reads, **kw):
    return {"component": "CentLook", "props": {"inscription": INS[n], "n": n, "front": H(n), "moves": moves, "reads": reads, **kw}}
pick = lambda i: f"Daidatep's pick, {i} of 6"

shots = [
 {"shot_id": "s00_question", "start": {"at_start": True}, "end": {"at_phrase": "As of November twenty"},
  "purpose": "DOPEMIND's question, the user's screenshot. Opens readable on frame 0 (name, time, first sentence), then reads the line in sections.",
  "component": "ScreenCrop", "props": {"title": "Numismatists Discord", "subtitle": "DOPEMIND · 8 November 2026",
   "src": DS + "discord_question.png", "width": 1662, "height": 240, "start": [20, 40, 800, 215], "min_scale": 1.5,
   "moves": [{"at_phrase": "What should I add", "box": [155, 150, 795, 215]},
             {"at_phrase": "Wondering about the", "box": [790, 150, 1430, 215]},
             {"at_phrase": "for this collection", "box": [990, 150, 1630, 215]}]}},
 {"shot_id": "s01_wall", "start": {"at_phrase": "As of November twenty"}, "end": {"at_phrase": "centoshi replied"},
  "purpose": "The Wall's 12 Cents, counting up (snapshot 2026-11-09).",
  "component": "WallBoard", "props": {"wall": "dopemind", "show": "grid",
   "moves": [{"at_phrase": "As of November twenty", "until_phrase": "to nineteen eighty-one", "target": {"grid_end": True}}],
   "readout": {"at_phrase": "vision holds twelve", "count": {"from": 0, "to": 12, "until_phrase": "Cents, from nineteen sixty-three", "suffix": " Cents"}}}},
 {"shot_id": "s02_centoshi", "start": {"at_phrase": "centoshi replied"}, "end": {"at_phrase": "Dopemind wrote back"},
  "purpose": "centoshi's reply, the user's screenshot (pre-cropped above the sticker). Framed on the text: the avatar, which carries uncleared art, stays out.",
  "component": "ScreenCrop", "props": {"title": "Numismatists Discord", "subtitle": "centoshi · 9 November 2026",
   "src": DS + "discord_centoshi.png", "width": 1720, "height": 260, "start": [150, 0, 800, 175]}},
 {"shot_id": "s03_1971", "start": {"at_phrase": "Dopemind wrote back"}, "end": {"at_phrase": "centoshi holds sixteen"},
  "purpose": "DOPEMIND's answer, the user's screenshot (pre-cropped: no sticker, no later messages).",
  "component": "ScreenCrop", "props": {"title": "Numismatists Discord", "subtitle": "DOPEMIND · 9 November 2026",
   "src": DS + "discord_1971.png", "width": 1720, "height": 170, "start": [150, 0, 800, 168]}},
 {"shot_id": "s04_c71", "start": {"at_phrase": "centoshi holds sixteen"}, "end": {"at_phrase": "Of nineteen seventy-one, Martin"},
  "purpose": "centoshi's Wall: its 16 Cents from 1971 ringed (most of any collector; artist wallet excluded).",
  "component": "WallBoard", "props": {"wall": "centoshi", "show": "grid",
   "moves": [{"at_phrase": "centoshi holds sixteen", "until_phrase": "more than any other", "target": {"grid_end": True}}],
   "highlights": [{"at_phrase": "centoshi holds sixteen", "group": "y1971"}],
   "readout": {"at_phrase": "centoshi holds sixteen", "text": "16 from 1971"}}},
 {"shot_id": "s05_lehnen", "start": {"at_phrase": "Of nineteen seventy-one, Martin"}, "end": {"at_phrase": "On November ninth"},
  "purpose": "NYT front page, 16 Aug 1971 (cleared by the user); Lehnen's line, verbatim from 'CENTS – Reflections on Mint Years' (Medium, 8 Mar 2025).",
  "component": "QuoteOver", "props": {"title": "1971", "subtitle": "The year money left gold",
   "src": "assets/dopemind/nyt_1971_crop.jpg", "img_w": 713, "img_h": 391, "img_caption": "The New York Times, 16 August 1971",
   "quote": "“It was the year the United States abandoned the gold standard, severing the connection between currency and tangible value…”",
   "attribution": "Martin Lehnen, 2025", "quote_at": "It was the year", "quoteSize": 50}},
 {"shot_id": "s06_market71", "start": {"at_phrase": "On November ninth"}, "end": {"at_phrase": "Number twenty-seven seventy-nine"},
  "purpose": "cents.vision in Market mode, *1971, On Sale: Hits 362, the three listed first. Prices hidden before capture (README).",
  "component": "ScreenCrop", "props": {"title": "cents.vision", "subtitle": "1971 · Market · 9 Nov 2026",
   "src": "vision/dm_1971_market.jpg", "width": 2160, "height": 2600, "start": [600, 40, 1300, 400],
   "moves": [{"at_phrase": "three of the three", "box": [10, 1300, 640, 1560], "mark": True}]}},
 {"shot_id": "s07_2779", "start": {"at_phrase": "Number twenty-seven seventy-nine"}, "end": {"at_phrase": "Only thirteen Cents"},
  "purpose": "#2779: the Ghost portrait, then the whole face for the Full desert patina.",
  **look(2779, [{"at_phrase": "is a Ghost Cent", "box": [0.27, 0.15, 0.73, 0.82], "mark": True},
                {"at_phrase": "pale toning that", "box": None}],
         [{"readout": "1971", "caption": "Listed 9 November 2026"},
          {"at_phrase": "is a Ghost Cent", "readout": "Ghost", "caption": "set apart from the field"},
          {"at_phrase": "with full desert", "readout": "Full Desert", "caption": "dominates the coin"}])},
 {"shot_id": "s08_gd", "start": {"at_phrase": "Only thirteen Cents"}, "end": {"at_phrase": "Number eighty-five fifty-six"},
  "purpose": "All 13 Cents that are both Ghost and Full Desert (trait-pool rule: a small pool is shown whole).",
  "component": "CentScroll", "props": {"title": "Ghost + Desert", "ns": GD, "mark": 2779, "readout": str(len(GD)), "caption": "Ghost, with Full Desert", "until": "are both", "cols": 4}},
 {"shot_id": "s09_8556", "start": {"at_phrase": "Number eighty-five fifty-six"}, "end": {"at_phrase": "And number fifty-two"},
  "purpose": "#8556: date and D, the contaminated patch, then the whole face.",
  **look(8556, [{"at_phrase": "seventy-one from Denver, is", "box": DATE(8556), "mark": True},
                {"at_phrase": "is contaminated", "box": [0.55, 0.12, 0.87, 0.37], "mark": True},
                {"at_phrase": "a major presence", "box": None}],
         [{"readout": "1971-D", "caption": "Listed 9 November 2026"},
          {"at_phrase": "is contaminated", "readout": "Contaminated", "caption": "Alien Secretion"},
          {"at_phrase": "with significant verdigris", "readout": "Verdigris", "caption": "Significant"}])},
 {"shot_id": "s10_5298", "start": {"at_phrase": "And number fifty-two"}, "end": {"at_phrase": "Any one of them"},
  "purpose": "#5298: no visual trait; the date.",
  **look(5298, [{"at_phrase": "a clean record", "box": DATE(5298), "mark": True}],
         [{"readout": "1971", "caption": "Listed 9 November 2026"},
          {"at_phrase": "carries no visual", "readout": "No trait", "caption": "a clean record of its year"}])},
 {"shot_id": "s11_club", "start": {"at_phrase": "Any one of them"}, "end": {"at_phrase": "Daidatep suggested six"},
  "purpose": "The three listed 1971s; any one adds the 1971 Club badge (replay +1971: '1971 1').",
  "component": "GapSlots", "props": {"title": "DOPEMIND", "subtitle": "Listed 1971s · 9 Nov 2026", "cols": 3,
   "slots": [{"label": f"#{n}", "src": H(n)} for n in (2779, 8556, 5298)],
   "readouts": [{"at_phrase": "seventy-one Club badge", "text": "1971 Club", "caption": "a badge for a 1971 Cent"}]}},
 {"shot_id": "s12_daidatep", "start": {"at_phrase": "Daidatep suggested six"}, "end": {"at_phrase": "all six were listed"},
  "purpose": "Daidatep's reply, the user's screenshot, read in four sections (min_scale 1.25: the screenshot's text then stands taller than the 48px captions).",
  "component": "ScreenCrop", "props": {"title": "Numismatists Discord", "subtitle": "Daidatep · 8 November 2026",
   "src": DS + "discord_daidatep.png", "width": 1694, "height": 352, "start": [150, 95, 830, 250], "min_scale": 1.25,
   "moves": [{"at_phrase": "six more", "box": [815, 135, 1610, 250]},
             {"at_phrase": "I could go on", "box": [150, 190, 940, 250]},
             {"at_phrase": "On the same day", "box": [300, 190, 1060, 250]}]}},
 {"shot_id": "s13_market6", "start": {"at_phrase": "all six were listed"}, "end": {"at_phrase": "Number eighty-six fifty-seven"},
  "purpose": "cents.vision Market, the six numbers, On Sale: all six listed (Hits 6).",
  "component": "ScreenCrop", "props": {"title": "cents.vision", "subtitle": "Daidatep's six · Market",
   "src": "vision/dm_six_market.jpg", "width": 2160, "height": 1700, "start": [10, 1290, 1290, 1570],
   "moves": [{"at_phrase": "listed for sale as well", "box": [10, 1300, 1290, 1560], "mark": True}]}},
 {"shot_id": "s14_8657", "start": {"at_phrase": "Number eighty-six fifty-seven"}, "end": {"at_phrase": "Only ninety Cents"},
  "purpose": "#8657: the date.",
  **look(8657, [{"at_phrase": "is from nineteen sixty-five", "box": DATE(8657), "mark": True}],
         [{"readout": "1965", "caption": pick(1)}])},
 {"shot_id": "s15_years", "start": {"at_phrase": "Only ninety Cents"}, "end": {"at_phrase": "and none of them"},
  "purpose": "Cents per year in the 1960s (merged-new2.json, 2026-11-09): 1965 has the fewest, 90.",
  "component": "YearBars", "props": {"title": "CENTS by year", "subtitle": "the 1960s", "highlight": "1965", "highlight_at": "Only ninety Cents",
   "bars": [{"label": str(y), "value": years[y]} for y in range(1960, 1970)],
   "readouts": [{"at_phrase": "Only ninety Cents", "text": "90", "caption": "the fewest of any 1960s year"}]}},
 {"shot_id": "s16_8657b", "start": {"at_phrase": "and none of them"}, "end": {"at_phrase": "Number eighty-eight twenty"},
  "purpose": "#8657 again: under the date, no mint mark; then the whole face for the notable desert patina (no zoom: the patch is not pinned down on the photo).",
  **look(8657, [{"at_phrase": "and none of them", "box": [0.62, 0.6, 0.87, 0.79], "mark": True},
                {"at_phrase": "It has a notable", "box": None}],
         [{"readout": "No mint mark", "caption": "generally Philadelphia"},
          {"at_phrase": "It has a notable", "readout": "Desert", "caption": "Notable: visible, local"}])},
 {"shot_id": "s17_8820", "start": {"at_phrase": "Number eighty-eight twenty"}, "end": {"at_phrase": "On Dopemind's Wall, it"},
  "purpose": "#8820: date; verdigris along the left rim; red across the face; the pool size.",
  **look(8820, [{"at_phrase": "from nineteen seventy-two", "box": DATE(8820), "mark": True},
                {"at_phrase": "verdigris along the rim", "box": [0.06, 0.24, 0.42, 0.9], "mark": True},
                {"at_phrase": "significant red across", "box": None}],
         [{"readout": "1972", "caption": pick(2)},
          {"at_phrase": "verdigris along the rim", "readout": "Verdigris", "caption": "Notable, along the rim"},
          {"at_phrase": "significant red across", "readout": "Red", "caption": "Significant"},
          {"at_phrase": "one hundred and eighty-three", "readout": "183", "caption": "with significant red"}])},
 {"shot_id": "s18_patinaset", "start": {"at_phrase": "On Dopemind's Wall, it"}, "end": {"at_phrase": "Number sixty-four fifty-one"},
  "purpose": "The Wall's verdigris, obsidian and desert, then #8820's red drops in: Patina Set (replay: +8820 adds 'Patina Set').",
  "component": "GapSlots", "props": {"title": "DOPEMIND", "subtitle": "Patina Set", "cols": 4,
   "slots": [{"label": "Verd.", "sub": "#951", "src": H(951)}, {"label": "Obs.", "sub": "#6935", "src": H(6935)},
             {"label": "Desert", "sub": "#3396", "src": H(3396)}, {"label": "Red", "sub": "#8820", "src": H(8820), "fill_at": "would complete a Patina"}],
   "readouts": [{"at_phrase": "all four base patinas", "text": "Patina Set", "caption": "all four base patinas"}]}},
 {"shot_id": "s19_6451", "start": {"at_phrase": "Number sixty-four fifty-one"}, "end": {"at_phrase": "Number sixty-eight seventy-five"},
  "purpose": "#6451: date; the darkened portrait; the pool size.",
  **look(6451, [{"at_phrase": "from nineteen eighty", "box": DATE(6451), "mark": True},
                {"at_phrase": "has significant obsidian", "box": [0.28, 0.12, 0.88, 0.72]},
                {"at_phrase": "two hundred and twenty", "box": None}],
         [{"readout": "1980", "caption": pick(3)},
          {"at_phrase": "has significant obsidian", "readout": "Obsidian", "caption": "Significant"},
          {"at_phrase": "two hundred and twenty", "readout": "220", "caption": "with significant obsidian"}])},
 {"shot_id": "s20_6875", "start": {"at_phrase": "Number sixty-eight seventy-five"}, "end": {"at_phrase": "In the Traits Atlas"},
  "purpose": "#6875: date; the abraded right side.",
  **look(6875, [{"at_phrase": "from nineteen sixty-seven", "box": DATE(6875), "mark": True},
                {"at_phrase": "heavily abraded Cents", "box": [0.55, 0.15, 0.92, 0.9], "mark": True}],
         [{"readout": "1967", "caption": pick(4)},
          {"at_phrase": "is one of forty-four", "readout": "1 of 44", "caption": "heavily abraded"}])},
 {"shot_id": "s21_atlas", "start": {"at_phrase": "In the Traits Atlas"}, "end": {"at_phrase": "Number sixty-seven eighty-two"},
  "purpose": "The Atlas's Heavy grade, verbatim (films/traits/script/atlas/abraded.txt).",
  "component": "QuoteOver", "props": {"title": "Cent #6875", "subtitle": "Heavily abraded", "cent": H(6875),
   "quote": "Heavy: “abrasion dominates the read of the coin; broad fields/devices visibly missing metal.”",
   "attribution": "Traits Atlas, CENTS Trait Council", "quote_at": "heavy abrasion", "quoteSize": 52}},
 {"shot_id": "s22_6782", "start": {"at_phrase": "Number sixty-seven eighty-two"}, "end": {"at_phrase": "And number fifty-eight"},
  "purpose": "#6782: date and D; the green right side; the badge (replay +6782: '1969 1').",
  **look(6782, [{"at_phrase": "sixty-nine from Denver", "box": DATE(6782), "mark": True},
                {"at_phrase": "with obsidian and", "box": [0.45, 0.28, 0.97, 0.85]},
                {"at_phrase": "It would add the nineteen", "box": None}],
         [{"readout": "1969-D", "caption": pick(5)},
          {"at_phrase": "with obsidian and", "readout": "Verdigris", "caption": "Significant + obsidian"},
          {"at_phrase": "It would add the nineteen", "readout": "1969 Club", "caption": "a badge for a 1969 Cent"}])},
 {"shot_id": "s23_5888", "start": {"at_phrase": "And number fifty-eight"}, "end": {"at_phrase": "Only twenty-eight Cents"},
  "purpose": "#5888: date and D; the whole face for the notable verdigris (no zoom: not pinned down on the photo).",
  **look(5888, [{"at_phrase": "fifty-six from Denver", "box": DATE(5888), "mark": True},
                {"at_phrase": "with notable verdigris", "box": None}],
         [{"readout": "1956-D", "caption": pick(6)},
          {"at_phrase": "with notable verdigris", "readout": "Verdigris", "caption": "Notable: visible, local"}])},
 {"shot_id": "s24_1956", "start": {"at_phrase": "Only twenty-eight Cents"}, "end": {"at_phrase": "It would be the Wall's"},
  "purpose": "Every Cent from 1956, all 28 (18 from Denver).",
  "component": "CentScroll", "props": {"title": "1956", "ns": Y56, "mark": 5888, "readout": str(len(Y56)), "caption": "from 1956; 18 from Denver", "until": "of them from Denver", "cols": 4}},
 {"shot_id": "s25_wheat", "start": {"at_phrase": "It would be the Wall's"}, "end": {"at_phrase": "To see every Cent"},
  "purpose": "#5888 turns over: the wheat ears (replay +5888: 'Wheat 1').",
  **look(5888, [], [{"at_phrase": "first wheat penny", "readout": "Wheat", "caption": "the Wall's first"}],
         back="hires/5888_back.webp", flip_at="first wheat penny")},
 {"shot_id": "s26_lab", "start": {"at_phrase": "To see every Cent"}, "end": {"at_phrase": "from Lab to Market"},
  "purpose": "cents.vision Traits Lab, the Lab/Market switch.",
  "component": "ScreenCrop", "props": {"title": "cents.vision", "subtitle": "Traits Lab", "src": "vision/traits_lab.png", "width": 2964, "height": 1654,
   "start": [300, 0, 1700, 1210], "moves": [{"at_phrase": "switch cents dot vision", "box": [680, 135, 1020, 225], "mark": True}]}},
 {"shot_id": "s27_market", "start": {"at_phrase": "from Lab to Market"}, "end": {"at_phrase": "What should Dopemind add"},
  "purpose": "The same switch, set to Market.",
  "component": "ScreenCrop", "props": {"title": "cents.vision", "subtitle": "Market", "src": "vision/dm_six_market.jpg", "width": 2160, "height": 1700,
   "start": [590, 140, 945, 225], "moves": [{"at_phrase": "Lab to Market", "box": [590, 140, 945, 225], "mark": True}]}},
 {"shot_id": "s28_ask", "start": {"at_phrase": "What should Dopemind add"}, "end": {"after_phrase": "Tell us what you think", "plus": 2.0},
  "purpose": "The question to viewers, over the options the film put forward.", "component": "AskCard",
  "props": {"question": "What should DOPEMIND add next?", "cols": 4, "note": "Tell us what you think",
   "options": [{"label": "1971"}] + [{"label": f"#{n}", "src": H(n)} for n in PICKS]}},
 {"shot_id": "s29_credits", "start": {"after_phrase": "Tell us what you think", "plus": 2.0}, "end": {"at_end": True},
  "purpose": "End credits.", "component": "Credits",
  "props": {"lines": ["Images: Rutherford Chang via cents.vision (site by Dr. Martin Lehnen)",
                      "Discord: Numismatists server, 8 and 9 November 2026",
                      "Listings and Collector Walls: cents.vision, 9 November 2026",
                      "Quote: Martin Lehnen, “CENTS – Reflections on Mint Years”, March 2025",
                      "Trait grades: Traits Atlas, CENTS Trait Council",
                      "Front page: The New York Times, 16 August 1971"], "url": "cents.gallery"}},
]
for s in shots: s["visual_kind"] = "code"
tl = {"essay": {"title": "What to add next", "subtitle": "DOPEMIND's question", "author": "shibboleth",
                "source": "Numismatists Discord; https://cents.vision", "version": "v2 (2026-11-09)"},
      "_what": "First film in the 'What to add next' format: a collector's question, the real Discord screenshots, what is listed and what is interesting about each suggestion. Every coin is a real Cent by number; every figure is checked above against the 2026-11-09 snapshots. No prices, no wallet addresses.",
      "shots": shots}
json.dump(tl, open(F / "timeline/timeline.json", "w"), indent=1, ensure_ascii=False)
json.dump({"assets": {}, "_note": "No Plate assets. Screenshots (user's uploads, 2026-11-09) and the NYT crop are in public/assets/dopemind/ (gitignored; copies in /mnt/project-files/collector-wall/dopemind/). cents.vision captures are in public/vision/."},
          open(F / "timeline/assets.json", "w"), indent=1)
print(f"{len(shots)} shots; all figures checked against {SNAP.name}")
