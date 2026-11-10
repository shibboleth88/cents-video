"""Writes timeline.json for the DOPEMIND Collector Wall episode (standard format, series brief).

    python3 films/wall-dopemind/timeline/make_timeline.py     (from the repo root)

Every coin is a real Cent by number. Figures come from data/wall_board.json and the
2026-11-09 cents.vision snapshot; the dot chart from data/contamination_sets.json.
Zoom boxes are fractions of the 1050px cents.vision fronts, measured on crops
(the #478 boxes are the ones its One Cent episode used). No wallet address appears.
"""
import json, pathlib
F = pathlib.Path(__file__).resolve().parent
al = json.load(open(F.parent / "script/alignment.json"))
TOTAL = round(al["duration"] * 30)
CS = json.load(open(F.parent / "data/contamination_sets.json"))
W, T = "dopemind", "DOPEMIND"
SIG = 478
CREDIT = "3D render: 3DCENTS by sinvalli"
CLIP = {"src": f"3dcents/{SIG}-360-30fps.mp4", "width": 1080, "height": 1920, "frames": 150,
        "coin": {"cx": 539.5, "cy": 958.5, "d": 775}, "credit": CREDIT, "credit_at_end": True}

def shot(i, a, b, comp, props, purpose, **top):
    s = {"shot_id": i, "start": {"at_start": True} if a is None else {"at_phrase": a},
         "end": b if isinstance(b, dict) else {"at_phrase": b},
         "purpose": purpose, "visual_kind": "code", "component": comp, "props": props}
    s.update(top)
    return s
board = lambda show, moves=None, **kw: dict({"wall": W, "show": show, "moves": moves or []}, **kw)
badge = lambda ph, b: {"at_phrase": ph, "target": {"badge": b}, "mark": True}
hires = lambda n: f"hires/{n}.webp"
stand = lambda n, readout, caption, **kw: dict({"title": T, "n": n, "readout": readout, "caption": caption, "src": hires(n)}, **kw)

opener = {"variant": "showcase", "wall": W, "show": "card", "until_phrase": "Its signature Cent",
          "moves": [{"at_phrase": "Its signature Cent", "target": {"cent": SIG, "in": "signature"}, "mark": True}],
          "progress": {"total_frames": TOTAL},
          "clip": dict(CLIP, src=f"3dcents/{SIG}-360-30fps-alpha.webm", alpha=True)}

# #478: obsidian under TRUST; desert at the collar and by GOD; Speckles across LIBERTY and the bust.
Z478 = [
 {"at_phrase": "obsidian patina, a notable", "box": [0.485, 0.16, 0.79, 0.32], "mark": True},
 {"at_phrase": "notable desert patina", "box": [0.26, 0.12, 0.68, 0.62], "marks": [[0.28, 0.14, 0.4, 0.22], [0.55, 0.53, 0.64, 0.6]]},
 {"at_phrase": "and Speckles, small particles", "box": [0.1, 0.38, 0.82, 0.85], "marks": [[0.12, 0.4, 0.48, 0.69], [0.49, 0.65, 0.8, 0.83]]},
]
# #8741: the date; white flecks (paint); the raised brown deposit by TRUST (obscure adhesive).
Z8741 = [
 {"at_phrase": "from nineteen seventy-nine, one", "box": [0.64, 0.59, 0.86, 0.72], "mark": True},
 {"at_phrase": "carries two more types", "box": None},
 {"at_phrase": "paint, a colored layer", "box": [0.5, 0.58, 0.82, 0.82], "marks": [[0.71, 0.64, 0.76, 0.69], [0.54, 0.74, 0.58, 0.79]]},
 {"at_phrase": "and obscure adhesive, thick", "box": [0.46, 0.13, 0.72, 0.35], "marks": [[0.535, 0.19, 0.62, 0.29]]},
]
# #3396: the date, then the pale runs down the right field and along the shoulder.
Z3396 = [
 {"at_phrase": "from nineteen seventy-six", "box": [0.64, 0.59, 0.84, 0.7], "mark": True},
 {"at_phrase": "carries white drips and streaks", "box": [0.5, 0.2, 0.94, 0.8], "marks": [[0.77, 0.25, 0.88, 0.49], [0.53, 0.58, 0.65, 0.75]]},
 {"at_phrase": "pale runs across the", "box": [0.1, 0.45, 0.68, 0.85], "marks": [[0.13, 0.55, 0.34, 0.68], [0.53, 0.58, 0.65, 0.75]]},
]
TWO_TYPES = [1161, 1657, 1924, 6434, 6582, 6823, 7901, 7965, 8465, 8741, 9524, 9786, 9992]
WHITE_DRIPS = json.load(open(F.parent / "data/white_drips.json"))["cents"]
SP = json.load(open(F.parent / "data/speckles.json"))
Q1 = {"src": "media/dopemind_quote_value.jpg", "width": 1024, "height": 1024}
Q2 = {"src": "media/dopemind_quote_bitcoin.png", "width": 1024, "height": 1024}
# Quote framing, measured on the graphics (cream-text row/column scan): the camera holds the whole text block,
# with the aspect of the picture area (1000 x 860) so no line is cut at an edge; the passage being read stays
# lit and the rest dims. Value graphic text: x 122-869, y 135-709. Bitcoin graphic text: x 100-934, y 125-870.
TB1 = [82, 66, 909, 777]
TB2 = [70, 113, 964, 882]

shots = [
 shot("d00_open", None, "Cent, number four seventy-eight", "WallOpener", opener,
      "Showcase opener: the card from frame 0, #478 turning in its slot (3DCENTS, alpha), mosaic and badges lighting in turn; zoom onto the signature Cent."),
 shot("d01_sig", "Cent, number four seventy-eight", "Notable means clearly visible", "WallStandout",
      dict(stand(SIG, "1963", "Obsidian · Desert · Speckles"),
           clip=dict(CLIP, sync=True, enter_from={"cx": 540, "cy": 800, "d": 495},
                     still={"src": hires(SIG), "at_phrase": "a significant obsidian patina", "r": 0.41}),
           zooms=Z478),
      "Signature #478 grows out of its slot still turning, faces front as its patina is named, then three zooms on the front: obsidian, desert, Speckles.",
      join_prev=True),
 shot("d02_grades", "Notable means clearly visible", "Speckles is one of the", "CentRow",
      {"title": T, "subtitle": "Obsidian, two grades", "cols": 2, "labelsUnder": True,
       "cents": [{"n": 6935, "caption": "Notable", "at_phrase": "Notable means clearly visible"},
                 {"n": SIG, "caption": "Significant", "at_phrase": "and significant a major presence"}]},
      "What the grades mean (Traits Atlas wording), shown with this Wall's own obsidian Cents: #6935 notable, #478 significant."),
 shot("d03_atlas_speckles", "Speckles is one of the", "foreign matter added after", "WallShot",
      {"src": "vision/atlas_contaminated_speckles.png", "width": 1080, "height": 1920,
       "moves": [{"box": [20, 20, 1060, 940]}]},
      "cents.vision Traits Atlas, Contaminated: the Speckles entry and its example Cent (captured 2026-11-09)."),
 shot("d03b_atlas_top", "foreign matter added after", "Ninety-five Cents carry Speckles", "WallShot",
      {"src": "vision/atlas_contaminated_top.png", "width": 1080, "height": 1920,
       "moves": [{"box": [20, 460, 1060, 1110]}]},
      "Traits Atlas, Contaminated: the summary (foreign material adhered after minting)."),
 shot("d03c_speckles", "Ninety-five Cents carry Speckles", "Only five pair Speckles", "CentFilter",
      {"title": "Speckles", "subtitle": "Contaminated: Speckles", "pool": SP["speckles"],
       "steps": [{"at_phrase": "Ninety-five Cents carry Speckles", "readout": str(len(SP["speckles"])), "caption": "Cents carry Speckles"},
                 {"at_phrase": "Obsidian is on fewer", "readout": "17.6%", "caption": "of all 10,000 carry obsidian"},
                 {"at_phrase": "but on seventy of these", "keep": SP["speckles_obsidian"], "readout": str(len(SP["speckles_obsidian"])),
                  "caption": "of the 95 also carry obsidian"}]},
      "All 95 Speckles Cents; the 70 that also carry obsidian (any grade) stay lit. Obsidian is on 1,757 of 10,000 (17.6%). merged-new2.json, 2026-11-09."),
 shot("d03d_five", "Only five pair Speckles", "No other Cent of the", "CentFilter",
      {"title": "Speckles", "subtitle": "with significant obsidian", "pool": SP["speckles_significant_obsidian"],
       "steps": [{"at_phrase": "Only five pair Speckles", "readout": "5", "caption": "with significant obsidian"},
                 {"at_phrase": "the only one of them with", "keep": [SIG], "regroup": True, "readout": "1", "caption": "with desert as well: #478"}],
       "mark": {"n": SIG, "at_phrase": "the only one of them with"}},
      "The five Speckles Cents with significant obsidian (478, 2900, 5118, 6666, 8063); only #478 also carries desert (notable)."),
 shot("d03e_unique", "No other Cent of the", "Number eighty-seven forty-one, from", "WallStandout",
      dict(stand(SIG, "1 of 10,000", "#478 carries all three", title="Speckles", subtitle="+ significant obsidian + desert"), zooms=[{"at_phrase": "carries all three", "box": [0.12, 0.12, 0.88, 0.88]}]),
      "#478 large: no other Cent carries Speckles, significant obsidian and desert together (data/speckles.py: 1 under every reading; with obsidian of ANY grade it is 6, so the label must keep \"significant\"). Not on cents.vision's 1/1 Trait Combo list, which counts unique pairs; the film does not call it 1/1."),
 shot("d04_8741", "Number eighty-seven forty-one, from", "Together, these two Cents", "WallStandout",
      dict(stand(8741, "1979", "Paint · Obscure Adhesive"), zooms=Z8741),
      "#8741: its date (1979, a Chronicle Set year), then the paint flecks and the adhesive deposit. Which spot is which type is a reading of the photo against the Atlas definitions."),
 shot("d06_together", "Together, these two Cents", "which makes a Contamination Set", "CentRow",
      {"title": T, "subtitle": "Two contaminated Cents", "cols": 2, "labelsUnder": True,
       "cents": [{"n": SIG, "caption": "#478"}, {"n": 8741, "caption": "#8741"}],
       "readout": "3 of 12", "caption": "contamination types", "readout_at": "cover three of the twelve"},
      "The two Cents together: three of the twelve types."),
 shot("d07_badge", "which makes a Contamination Set", "As of November twenty", "WallBoard",
      board("card", [badge("which makes a Contamination Set", "Contamination Set")]),
      "Contamination Set (3/12) badge, lit."),
 shot("d08_chart", "As of November twenty", "Only thirteen of the ten", "DotColumns",
      {"title": "Contamination Sets", "subtitle": f"{CS['collectors']} collectors, November 2026",
       "axis": "contaminated Cents held", "bins": CS["bins"], "total": CS["collectors"],
       "dots_at": "fifty-eight collectors hold one",
       "highlight": {"bin": "2", "name": T, "at_phrase": "Mind holds only two"},
       "reads": [{"at_phrase": "fifty-eight collectors hold one", "readout": str(CS["collectors"]), "caption": "collectors hold one"},
                 {"at_phrase": "Mind holds only two", "readout": "2", "caption": "the fewest of any Wall with one"}]},
      "Every collector with a Contamination Set, one dot each, by how many contaminated Cents they hold (snapshot 2026-11-09; 59 Walls in set-counts.php, the artist wallet with 87 left out). DOPEMIND alone at 2."),
 shot("d05_thirteen", "Only thirteen of the ten", "The Wall holds twelve Cents", "CentScroll",
      {"title": "Two types at once", "ns": TWO_TYPES, "mark": 8741, "readout": "13",
       "caption": "Cents, of all 10,000", "until": "The Wall holds twelve Cents", "cols": 4},
      "All 13 Cents with two contamination types (merged-new2.json, 2026-11-09; recounted from cents_by_trait.json); #8741 ringed. None has three. Moved after the chart in v2 (user, 2026-11-09)."),
 shot("d09_count", "The Wall holds twelve Cents", "which puts it in the Dime", "WallBoard",
      board("grid", [{"at_phrase": "The Wall holds twelve Cents", "until_phrase": "which puts it in the Dime", "target": {"grid_end": True}}],
            readout={"at_phrase": "The Wall holds twelve Cents", "count": {"from": 0, "to": 12, "until_phrase": "from nineteen sixty-three to", "suffix": " Cents"}}),
      "The opened collection: all 12 Cents with a count."),
 shot("d10_dime", "which puts it in the Dime", "Two of them carry a D", "WallBoard",
      board("card", [badge("which puts it in the Dime", "Dime Club")]), "Dime Club badge."),
 shot("d11_4599", "Two of them carry a D", "and nineteen seventy-four.", "WallStandout",
      dict(stand(4599, "1963-D", "D: the Denver mint"), zooms=[{"at_phrase": "a D mint mark, for", "box": [0.64, 0.59, 0.86, 0.76], "mark": True}]),
      "#4599, 1963-D: zoom onto the date and the D."),
 shot("d11b_3010", "and nineteen seventy-four.", "The Wall holds both years", "WallStandout",
      dict(stand(3010, "1974-D", "D: the Denver mint"), zooms=[{"at_phrase": "and nineteen seventy-four.", "box": [0.64, 0.57, 0.86, 0.76], "mark": True}]),
      "#3010, 1974-D: the date and the D."),
 shot("d11c_pairs", "The Wall holds both years", "Number thirty-three ninety-six", "CentRow",
      {"title": T, "subtitle": "Two years, with and without a D", "cols": 2, "labelsUnder": True,
       "cents": [{"n": 4599, "caption": "1963-D"}, {"n": SIG, "caption": "1963"}, {"n": 3010, "caption": "1974-D"}, {"n": 8800, "caption": "1974"}]},
      "1963 and 1974, each with and without a mint mark."),
 shot("d12_3396", "Number thirty-three ninety-six", "Eighty-two Cents carry them", "WallStandout",
      dict(stand(3396, "1976", "White Drips and Streaks"), zooms=Z3396),
      "#3396: the date, then the pale runs (white drips and streaks)."),
 shot("d13_drips", "Eighty-two Cents carry them", "And the Wall carries Diamond", "CentScroll",
      {"title": "Drips and Streaks", "ns": WHITE_DRIPS, "mark": 3396, "readout": str(len(WHITE_DRIPS)),
       "caption": "Cents carry them", "until": "And the Wall carries Diamond", "cols": 7},
      "All 82 white-drips Cents (merged-new2.json, 2026-11-09), #3396 ringed."),
 shot("d14_diamond", "And the Wall carries Diamond", "has also written about", "WallBoard",
      board("card", [badge("And the Wall carries Diamond", "Diamond"), {"at_phrase": "with little to no selling", "target": {"card": True}}]),
      "Diamond Hands badge, lit; then the whole card."),
 shot("d14b_quote_value", "has also written about", "And: Bitcoin was the", "WallShot",
      dict(Q1, title=T, subtitle="Shared in the CENTS Discord",
           moves=[{"at_phrase": "Mass-produced objects become", "box": TB1, "focus": [183, 245, 797, 380]},
                  {"at_phrase": "Meaning doesn't come from", "box": TB1, "focus": [104, 392, 887, 571]},
                  {"at_phrase": "Value is not invented", "box": TB1, "focus": [217, 599, 737, 727]}]),
      "DOPEMIND's quote graphic (cents.gallery media library C103, shared in the CENTS graphics channel; creator to confirm), read in full; the camera holds the whole text and lights each passage as it is spoken."),
 shot("d14c_quote_bitcoin", "And: Bitcoin was the", "On X, on November", "WallShot",
      dict(Q2, title=T, subtitle="Shared in the CENTS Discord",
           moves=[{"at_phrase": "Bitcoin was the defining", "box": TB2, "focus": [85, 114, 950, 482]},
                  {"at_phrase": "Cents answers it materially", "box": TB2, "focus": [85, 405, 950, 596]}]),
      "DOPEMIND's second graphic (media library C132; creator to confirm). The first two sentences are read; the last (Satoshi Nakamoto) shows on screen."),
 shot("d14d_xpost", "On X, on November", "Find all of the Collector", "PostExcerpts",
      {"title": T, "subtitle": "@dopemind10 on X, 9 Nov 2026",
       "excerpts": [{"text": "CENTS by Rutherford Chang is next level concept art.", "at_phrase": "called Cents next level"},
                    {"text": "This is performance of value. I study it.", "at_phrase": "This is performance of value"}],
       "source": "Two lines of the post, verbatim"},
      "DOPEMIND's own post, x.com/dopemind10/status/2119890111471231434 (9 Nov 2026 20:29 UTC), fetched verbatim through twitterapi.io on 2026-11-10 (dopemind-x/twitterapi/). Two of its lines, as written; the thanks line and the Ordinals line are not shown. Added in v3 (user, 2026-11-09: use his posts about Cents)."),
 shot("d15_collectors", "Find all of the Collector", {"after_phrase": "under Collectors", "plus": 1.5}, "WallShot",
      {"src": "vision/traits_lab.png", "width": 2964, "height": 1654, "moves": [{"at_phrase": "Collector Walls on cents", "box": [600, 1250, 2200, 1654]},
                {"at_phrase": "under Collectors", "box": [1185, 1575, 1358, 1635], "mark": True}]},
      "cents.vision Traits Lab; in to the Cents row and the site menu, then onto Collectors."),
 {"shot_id": "d16_credits", "start": {"after_phrase": "under Collectors", "plus": 1.5}, "end": {"at_end": True},
  "purpose": "End credits.", "visual_kind": "code", "component": "Credits",
  "props": {"lines": ["Images: Rutherford Chang via cents.vision (site by Dr. Martin Lehnen)", CREDIT,
                      "Trait definitions and grades: Traits Atlas, CENTS Trait Council",
                      "Collector Wall data: cents.vision, as of November 2026",
                      "Quote graphics: DOPEMIND, CENTS Discord",
                      "Post: @dopemind10 on X, 9 November 2026"], "url": "cents.gallery"}},
]
tl = {"essay": {"title": "Collector Wall", "subtitle": T, "author": "shibboleth", "source": "https://cents.vision/collectors.html",
                "version": "v3 (2026-11-10)"},
      "_what": "Collector Wall: DOPEMIND. Data as of 2026-11-09 (cents.vision snapshot). No wallet address appears.",
      "shots": shots}
json.dump(tl, open(F / "timeline.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(shots)} shots, {TOTAL} frames")
