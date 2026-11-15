"""Writes timeline.json for the blacktongue "character" episode (Collector Wall, after #7476).

    python3 films/wall-blacktongue-character/timeline/make_timeline.py     (from the repo root)

The film opens on what the Wall holds taken together (user, 2026-11-14), then gives
the newest Cent and the standard Wall material. Every coin is a real Cent by number.
Every figure on screen comes from data/character.json, which data/character.py
measures from the 2026-11-14 cents.vision snapshot and refuses when a sentence is
no longer supported; the card and badges from data/wall_board.json (same snapshot).
Zoom boxes are fractions of the 1050px cents.vision fronts, read on gridded crops.
No wallet address appears. No price appears.
"""
import json, pathlib
F = pathlib.Path(__file__).resolve().parent
al = json.load(open(F.parent / "script/alignment.json"))
SCRATCH = al.get("_source", "").startswith("SCRATCH")
TOTAL = round(al["duration"] * 30)
C = json.load(open(F.parent / "data/character.json"))
W, T = "blacktongue-character", "blacktongue"
SIG = 5185
CREDIT = "3D render: 3DCENTS by sinvalli"
CLIP = {"src": f"3dcents/{SIG}-360-30fps.mp4", "width": 1080, "height": 1920, "frames": 150,
        "coin": {"cx": 539.5, "cy": 959.5, "d": 776}, "credit": CREDIT, "credit_at_end": True}
GH = C["grades_held"]
TPC = C["traits_per_cent"]

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

# The ladder, from character.json (character.py checks every cell against the snapshot).
LADDER_ROWS = [("Verdigris", "Verdigris, obsidian, desert"), ("Obsidian", "obsidian, desert and red"),
               ("Desert", "desert and red, each"), ("Red", "red, each at notable"), ("Gold", "full; gold, at notable")]
ORANGE = C["orange"]   # draft 3 (user, 2026-11-14): orange joins the list; it has no grades
assert [r["label"] for r in C["ladder"]] == [l.lower() for l, _ in LADDER_ROWS]
ladder = {"columns": ["Notable", "Significant", "Full"],
          "rows": [{"label": lab, "at_phrase": ph, "cells": r["cells"]} for (lab, ph), r in zip(LADDER_ROWS, C["ladder"])]
                  + [{"label": "Orange", "at_phrase": "and full, and orange", "cells": [ORANGE], "ungraded": True}],
          "lights": [{"at_phrase": "Notable means clearly visible", "column": 0},
                     {"at_phrase": "significant a major presence", "column": 1},
                     {"at_phrase": "and full the dominant", "column": 2}]}
# Key Cents over the strips: the Wall's own full-grade Cent of each patina (the ladder's right-hand column).
KEYS = [r["cells"][2] for r in C["ladder"]] + [ORANGE]
STRIP_AT = ["No other collector's Wall", "Even C L seven and", "and Daidatep, with more", "is the artist wallet"]
DROBNICK = "the patina stores the history of the object through surface and texture"   # QB-B39, check_quotes FOUND 2026-11-14
strips = [dict(s, count=sum(s["held"]), at_phrase=ph, **({"apart": True} if s["name"] == "Artist wallet" else {}))
          for s, ph in zip(GH["strips"], STRIP_AT)]

PER = TPC["per_cent"]
FULL_GOLD = [1040, 1864, 1924, 2930, 3231, 4273, 8002, 9085, 9581]   # snapshot meta, full_gold true (character.py: nine)
MAKES = {"src": "media/makes_cents_blacktongue_2024-11-20.jpg", "img_w": 2000, "img_h": 2000}
WALL25_IMG = {"src": "media/blacktongue_wall_25.jpg", "img_w": 1000, "img_h": 1000}

opener = {"variant": "showcase", "wall": W, "show": "card", "until_phrase": "Verdigris, obsidian, desert and", "moves": [],
          "progress": {"total_frames": TOTAL},
          "clip": dict(CLIP, src=f"3dcents/{SIG}-360-30fps-alpha.webm", alpha=True)}

shots = [
 shot("k00_open", None, "Verdigris, obsidian, desert and", "WallOpener", opener,
      "Showcase opener: the card from frame 0, the signature Cent #5185 turning in its slot (3DCENTS, alpha), mosaic and badges lighting in turn."),
 shot("k01_ladder", "Verdigris, obsidian, desert and", "No other collector's Wall", "PatinaLadder", ladder,
      "The claim made visible: the Wall's own Cents as a grid of patina by grade, one different Cent per cell, each row arriving as its patina is named; "
      "each column lights as its grade is explained (Traits Atlas wording). Gold has no significant grade (dash). Orange has no grades: "
      "#1757 drawn across the columns on a rule, dimmed whenever a single grade is lit."),
 shot("k02_strips", "No other collector's Wall", "Writing about Chang's earlier", "GradeStrips",
      {"title": "Patinas held", "subtitle": "As of November 2026", "groups": [3, 3, 3, 3, 2, 1], "keys": KEYS,
       "patinas": [r["label"] for r in C["ladder"]] + ["orange"],
       "rows": strips, "mark_missing_at": "reach thirteen"},
      f"Fifteen dots per Wall (the fourteen grades, then orange): blacktongue 15; CL7 and Daidatep (the two largest collector Walls) 13, each missing a full gold "
      f"and one other full; the artist wallet, set apart under a rule, 15. Best any other collector reaches: {GH['best_other_collector']} (character.py)."),
 shot("k03_drobnick", "Writing about Chang's earlier", "Of the Walls with ten", "QuoteOver",
      {"title": "Patina", "subtitle": "Cent #6054, full verdigris", "cent": hires(6054),
       "quote": f"“{DROBNICK}”", "attribution": "Jim Drobnick, on Chang's We Buy White Albums, 2023", "quote_at": "Jim Drobnick noted that"},
      "Art quote from the bank (QB-B39; Drobnick, Revue musicale OICRM, 2023, p. 19), verbatim and FOUND by check_quotes.py. It is about We Buy White "
      "Albums, not CENTS; the narration and the attribution both say so. Our narration paraphrases the first half of his sentence (wear lowers an album's "
      "value to a \"true\" vinyl collector). Shown over the Wall's full verdigris Cent; no motive of Chang's is stated."),
 shot("k04_traits", "Of the Walls with ten", "Number thirty-two seventeen", "CentTiers",
      {"title": T, "subtitle": "Its Cents by trait count", "total": C["count"],
       "tiers": [{"label": str(k), "cents": [n for n in C["cents"] if PER[str(n)] == k]} for k in (4, 3, 2, 1, 0)],
       "reads": [{"at_phrase": "two point four on", "readout": f"{TPC['wall']:.1f}", "caption": "traits per Cent, on average"},
                 {"at_phrase": "against under one across", "readout": f"{TPC['population']:.2f}", "caption": "across all 10,000 Cents"}]},
      f"The Wall's 25 Cents in rows by their count of visual traits (grades folded, wheat not counted; snapshot and Sep 2026 export agree): "
      f"seven carry four. Mean {TPC['wall']}, the highest of any Wall with 10+ (next {TPC['runner_up_10plus']}); CENTS {TPC['population']}."),
 shot("k05_3217", "Number thirty-two seventeen", "The wear runs from", "WallStandout",
      dict(stand(3217, "1970", "Verdigris · Obsidian · Desert · Red"),
           zooms=[{"at_phrase": "carries all four base", "box": [0.18, 0.12, 0.86, 0.8]}]),
      "#3217 (1970): all four base patinas on one Cent; a slow push onto the face."),
 shot("k06_wear", "The wear runs from", "And fourteen of the twenty-five", "CentRow",
      {"title": T, "subtitle": "The range of wear", "cols": 2, "solo_until": "No smaller Wall holds",
       "cents": [{"n": 2489, "src": hires(2489), "caption": "Close to mint state", "at_phrase": "The wear runs from"},
                 {"n": 1935, "src": hires(1935), "caption": "Faceless", "at_phrase": "to three Faceless Cents"},
                 {"n": 7906, "src": hires(7906), "caption": "Faceless", "at_phrase": "where Lincoln's face is"},
                 {"n": 9991, "src": hires(9991), "caption": "Faceless", "at_phrase": "all but gone"}]},
      "One Cent at a time, large: #2489 close to mint state (Lustrous trait), then the three Faceless Cents; gathered as the line ends. "
      "No smaller Wall holds both traits (smallest Walls with both: 25, 25, 34)."),
 shot("k07_decades", "And fourteen of the twenty-five", "In a twenty twenty-four", "YearBars",
      {"title": T, "subtitle": "Cents by decade",
       "bars": [{"label": k, "value": v} for k, v in C["decades"].items()],
       "highlight": "1960s", "highlight_at": "from the nineteen sixties",
       "readouts": [{"at_phrase": "fourteen of the twenty-five", "text": "14 of 25", "caption": "from the 1960s"},
                    {"at_phrase": "fewer than one in five", "text": f"{round(C['population_1960s_share'] * 100)}%", "caption": "of all 10,000 Cents"}]},
      "The Wall by decade (no Cents from the 1940s); the 1960s lit. Across CENTS 18.4% are from the 1960s."),
 shot("k08_quote_interview", "In a twenty twenty-four", "Some of the best pieces", "QuoteOver",
      dict(MAKES, title=T, subtitle="MAKES CENTS interview", img_caption="@sovrnart on X, 20 Nov 2024",
           quote="“…finding additional value in the artistic merit and time-worn aesthetic of each coin.”",
           attribution="blacktongue, 2024", quote_at="finding additional value in", shrinkTo=0.44, order="picture-first"),
      "The MAKES CENTS card (sovrnart, 20 Nov 2024; it shows blacktongue's Ghost #9684), then the interview line, verbatim."),
 shot("k08b_quote_patient", "Some of the best pieces", "In August twenty twenty-six", "QuoteOver",
      dict(WALL25_IMG, title=T, subtitle="MAKES CENTS interview", img_caption="The Wall, November 2026",
           quote="“…by being patient and trusting my eye (and gut).”",
           attribution="blacktongue, 2024", quote_at="by being patient and", shrinkTo=0.44, order="picture-first"),
      "The second interview line over the whole Wall as it stands (all 25 fronts on black). No single Cent is paired with it: "
      "the interview does not say which pieces came that way."),
 shot("k09_quote_5755", "In August twenty twenty-six", "The newest Cent is", "QuoteOver",
      {"title": T, "subtitle": "Cent #5755", "cent": hires(5755),
       "quote": "“Discoloration and dark deposits have created an accidental work of art.”",
       "attribution": "blacktongue (@blktng) on X, 21 Aug 2026", "quote_at": "Discoloration and dark deposits"},
      "#5755 (1964), the Cent the post shows (identified from the post image), with the post's line verbatim."),
 shot("k10_7476", "The newest Cent is", "It brings the Wall to", "WallStandout",
      dict(stand(7476, "1976", "Verdigris · Obsidian · Obscure Adhesive", subtitle="Newest: CENT #7476"),
           zooms=[{"at_phrase": "from nineteen seventy-six. It", "box": [0.6, 0.53, 0.86, 0.71], "mark": True},
                  {"at_phrase": "a significant verdigris patina", "box": [0.22, 0.05, 0.92, 0.45]},
                  {"at_phrase": "and obscure adhesive, thick", "box": None}]),
      "#7476: its date, then the green along the upper rim (verdigris); back to the whole Cent for the adhesive, which is not pointed at "
      "(not located with confidence on the photo)."),
 shot("k11_count", "It brings the Wall to", "and into the Quarter Club", "WallBoard",
      board("grid", [{"at_phrase": "It brings the Wall to", "until_phrase": "and into the Quarter Club", "target": {"grid_end": True}}],
            readout={"at_phrase": "It brings the Wall to", "count": {"from": 0, "to": C["count"], "until_phrase": "from nineteen thirty-eight to", "suffix": " Cents"}}),
      "The opened collection: all 25 Cents with a count."),
 shot("k11b_quarter", "and into the Quarter Club", "Its signature Cent", "WallBoard",
      board("card", [badge("into the Quarter Club", "Quarter Club")]), "Quarter Club badge (was Dime Club at 24)."),
 shot("k12_sig", "Its signature Cent", "That full desert, with", "WallStandout",
      dict(stand(SIG, "1968", "Full Desert · Ghost", subtitle="Signature: CENT #5185"),
           clip=dict(CLIP, still={"src": hires(SIG), "at_phrase": "carries a full desert patina", "r": 0.41})),
      "Signature #5185 turning (3DCENTS), settling to its front as the patina is named."),
 shot("k13_spectrum", "That full desert, with", "Only nine Full Spectrum", "CentRow",
      {"title": T, "subtitle": "Full Spectrum Set", "cols": 3,
       "cents": [{"n": 5185, "patina": "desert", "caption": "Full Desert · #5185", "at_phrase": "That full desert, with"},
                 {"n": 6054, "patina": "verdigris", "caption": "Full Verdigris · #6054", "at_phrase": "a full verdigris"},
                 {"n": 555, "patina": "obsidian", "caption": "Full Obsidian · #555", "at_phrase": "a full obsidian, a"},
                 {"n": 8185, "patina": "red", "caption": "Full Red · #8185", "at_phrase": "a full red, a"},
                 {"n": 3231, "patina": "gold", "caption": "Full Gold · #3231", "at_phrase": "a full gold and"},
                 {"n": 1757, "patina": "orange", "caption": "Orange · #1757", "at_phrase": "and an orange"}]},
      "The six Cents of the Full Spectrum Set, each lit as it is named, with the series' patina key dots (the Wall holds two full reds; #8185 stands for them)."),
 shot("k13b_gold", "Only nine Full Spectrum", "Across its Cents", "CentFilter",
      {"title": "Full Gold", "subtitle": "Every Full Gold Cent in CENTS", "pool": FULL_GOLD,
       "steps": [{"at_phrase": "only nine Full Gold", "readout": "9", "caption": "Full Gold Cents"}],
       "mark": {"n": 3231, "at_phrase": "only nine Full Gold"}},
      "All nine Full Gold Cents (snapshot meta); blacktongue's #3231 ringed. Nine full golds cap Full Spectrum Sets at nine."),
 # v2 (2026-11-14): k14_1938 and k14b_wheat cut with the oldest-Cent sentence, to bring the film under 3:00
 # (user rule). They are kept in make_timeline_v1.py.
 shot("k15_contam", "Across its Cents", "which makes a Contamination", "WallList",
      {"title": T, "subtitle": "Contamination types", "readout": "4 of 12", "readout_at": "four of the twelve contamination",
       "rows": [{"n": 5755, "label": "Alien Secretion"}, {"n": 7476, "label": "Obscure Adhesive"},
                {"n": 8185, "label": "Special Oddities"}, {"n": 9840, "label": "Dark Grime"}]},
      "One Cent for each of the four contamination types on the Wall (#6054 also carries Obscure Adhesive; #7476 stands for it, as the newest)."),
 shot("k15b_badge", "which makes a Contamination", "It holds four of the", "WallBoard",
      board("card", [badge("which makes a Contamination", "Contamination Set")]), "Contamination Set (4/12) badge, lit."),
 shot("k16_corroded", "It holds four of the", "Two are Ghost Cents", "CentRow",
      {"title": T, "subtitle": "Corroded", "cols": 2, "labelsUnder": True,
       "cents": [{"n": n, "caption": f"#{n}"} for n in (1055, 1935, 7449, 7906)],
       "readout": "4 of 69", "caption": "Corroded Cents", "readout_at": "four of the sixty-nine"},
      f"The Wall's four Corroded Cents; only {', '.join(n for n, _ in C['corroded']['collectors_as_many'])} hold as many (character.py)."),
 shot("k16b_ghost", "Two are Ghost Cents", "And the Wall carries Diamond", "CentRow",
      {"title": T, "subtitle": "Ghost and Vandalized", "cols": 2, "labelsUnder": True,
       "cents": [{"n": 5185, "caption": "Ghost", "at_phrase": "Two are Ghost Cents"}, {"n": 9684, "caption": "Ghost", "at_phrase": "Two are Ghost Cents"},
                 {"n": 7395, "caption": "Vandalized", "at_phrase": "and one is Vandalized"}]},
      "Ghost #5185 and #9684, Vandalized #7395."),
 shot("k17_diamond", "And the Wall carries Diamond", "Find all of the Collector", "WallBoard",
      board("card", [badge("And the Wall carries Diamond", "Diamond"), {"at_phrase": "with little to no selling", "target": {"card": True}}]),
      "Diamond Hands badge, lit; then the whole card."),
 shot("k18_collectors", "Find all of the Collector", {"after_phrase": "under Collectors", "plus": 1.5}, "WallShot",
      {"src": "vision/traits_lab.png", "width": 2964, "height": 1654, "moves": [{"at_phrase": "Collector Walls on cents", "box": [600, 1250, 2200, 1654]},
                {"at_phrase": "under Collectors", "box": [1185, 1575, 1358, 1635], "mark": True}]},
      "cents.vision Traits Lab; in to the site menu, then onto Collectors."),
 {"shot_id": "k19_credits", "start": {"after_phrase": "under Collectors", "plus": 1.5}, "end": {"at_end": True},
  "purpose": "End credits.", "visual_kind": "code", "component": "Credits",
  "props": {"lines": ["Images: Rutherford Chang via cents.vision (site by Dr. Martin Lehnen)", CREDIT,
                      "Trait definitions and grades: Traits Atlas, CENTS Trait Council",
                      "Quote: Jim Drobnick, “Rutherford Chang. The Record Collector as Artist-Curator” (2023)",
                      "Wall data: cents.vision, 14 Nov 2026",
                      "Interview: MAKES CENTS, @sovrnart on X, 20 November 2024",
                      "Post: @blktng on X, 21 Aug 2026"], "url": "cents.gallery"}},
]
tl = {"essay": {"title": "Collector Wall", "subtitle": T, "author": "shibboleth", "source": "https://cents.vision/collectors.html",
                "version": ("SCRATCH timing (no voice yet) - " if SCRATCH else "") + "v2 (2026-11-14), the collection's character, script draft 4 (under 3:00)"},
      "_what": "Collector Wall: blacktongue, after #7476. Data as of 2026-11-14 (cents.vision snapshot). No wallet address appears.",
      "shots": shots}
json.dump(tl, open(F / "timeline.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(shots)} shots, {TOTAL} frames" + ("  [SCRATCH alignment: layout only, never render this]" if SCRATCH else ""))
