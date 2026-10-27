"""Writes timeline.json for the ScrappyT episode. The opener variant is the one
argument, so the three proposed openings render from one script.

    python3 films/wall-scrappyt/timeline/make_timeline.py [showcase|live|rush|turn] [--clip]
"""
import json, sys, pathlib
F = pathlib.Path(__file__).resolve().parent
variant = sys.argv[1] if len(sys.argv) > 1 else "rush"
use_clip = "--clip" in sys.argv          # the user's 3DCENTS export of #7139, retimed to 30 fps
al = json.load(open(F.parent / "script/alignment.json"))
TOTAL = round(al["duration"] * 30)
W, T = "scrappyt", "ScrappyT"
CLIP = {"src": "3dcents/7139-360-30fps.mp4", "width": 1080, "height": 1920, "frames": 150,
        "coin": {"cx": 539.5, "cy": 959.5, "d": 776}, "credit": "3D render: 3DCENTS by sinvalli"}
PLACEHOLDER = dict(CLIP, src="3dcents/9908-360-30fps.mp4", note="PREVIEW: #9908 SPIN STANDS IN")

def shot(i, a, b, comp, props, purpose):
    return {"shot_id": i, "start": {"at_start": True} if a is None else {"at_phrase": a},
            "end": {"at_end": True} if b is None else {"at_phrase": b},
            "purpose": purpose, "visual_kind": "code", "component": comp, "props": props}
board = lambda show, moves=None, **kw: dict({"wall": W, "show": show, "moves": moves or []}, **kw)
badge = lambda ph, b: {"at_phrase": ph, "target": {"badge": b}, "mark": True}
row = lambda sub, cents, **kw: dict({"title": T, "subtitle": sub, "cents": cents}, **kw)

opener = {"variant": variant, "wall": W, "show": "card", "until_phrase": "Its signature Cent",
          "moves": [{"at_phrase": "Its signature Cent", "target": {"cent": 7139, "in": "signature"}, "mark": True}],
          "progress": {"total_frames": TOTAL}}
if variant in ("turn", "showcase"):
    opener["clip"] = CLIP if use_clip else PLACEHOLDER
sig = {"title": T, "n": 7139, "readout": "1967", "caption": "Full Desert · Ghost"}
if use_clip: sig["clip"] = CLIP

shots = [
 shot("s00_open", None, "number seventy-one thirty-nine", "WallOpener", opener,
      f"Opening ({variant}): moving from frame 0, hands over to the Wall card, which zooms onto the signature Cent."),
 shot("s01_sig", "number seventy-one thirty-nine", "Ghost means a full", "WallStandout", sig,
      "The signature Cent #7139 on its own."),
 shot("s02_ghost", "Ghost means a full", "Of the thirty-three Ghost", "WallStandout",
      {"title": T, "n": 7139, "readout": "Ghost", "caption": "Lincoln set apart from the field", "src": "hires/7139.webp"},
      "What Ghost means, on the signature Cent (Traits Atlas wording). Whole-face trait: no zoom."),
 shot("s02b_13", "Of the thirty-three Ghost", "The Wall holds forty-one", "WallStandout",
      {"title": T, "n": 7139, "readout": "13 of 33", "caption": "Ghost Cents with a full desert patina", "src": "hires/7139.webp"},
      "13 of the 33 Ghost Cents are full desert (merged-new2.json, 27 Oct 2026)."),
 shot("s03_count", "The Wall holds forty-one", "which puts it in the Quarter", "WallBoard",
      board("grid", [{"at_phrase": "Cents in two wallets", "until_phrase": "which puts it in the Quarter", "target": {"grid_end": True}}],
            readout={"at_phrase": "The Wall holds forty-one", "count": {"from": 0, "to": 41, "until_phrase": "from nineteen fifty-six to", "suffix": " Cents"}}),
      "The opened collection: all 41 Cents scrolling with a count."),
 shot("s03b_quarter", "which puts it in the Quarter", "One of them is a wheat", "WallBoard",
      board("card", [badge("which puts it in the Quarter", "Quarter Club")]), "Quarter Club badge."),
 shot("s04_wheat", "One of them is a wheat", "minted nineteen fifty-eight or", "WallBoard",
      board("card", [badge("One of them is a wheat", "Wheat")]), "Wheat 1 badge."),
 shot("s04b_wheat_rows", "minted nineteen fifty-eight or", "with two ears of", "WallBoard",
      board("grid", [{"at_phrase": "minted nineteen fifty-eight or", "target": {"cent": 3824}, "mark": True}],
            highlights=[{"at_phrase": "minted nineteen fifty-eight or", "group": "wheat"}]), "The wheat Cent #3824 in the rows."),
 shot("s04c_flip", "with two ears of", "It is from nineteen fifty-six", "CentFlip",
      {"title": T, "n": 3824, "front": "hires/3824.webp", "back": "hires/3824_back.webp", "flip_at": "two ears of wheat",
       "readout": "Wheat", "caption": "Two ears of wheat on the back"}, "#3824 turns over to show the wheat reverse."),
 shot("s04d_1956", "It is from nineteen fifty-six", "It holds three Cents", "WallStandout",
      {"title": T, "n": 3824, "readout": "1956", "caption": "The earliest year on the Wall", "src": "hires/3824.webp",
       "zoom": {"at_phrase": "from nineteen fifty-six, the", "box": [0.62, 0.58, 0.86, 0.71], "mark": True}},
      "#3824 zoomed onto its date (box checked on the 1050px front)."),
 shot("s05_1971", "It holds three Cents", "for the nineteen seventy-one Club", "WallBoard",
      board("grid", [{"at_phrase": "It holds three Cents", "until_phrase": "for the nineteen seventy-one Club", "target": {"grid_end": True}}],
            highlights=[{"at_phrase": "It holds three Cents", "group": "y1971"}]), "The three 1971 Cents ringed in the rows."),
 shot("s05b_club", "for the nineteen seventy-one Club", "Two of its Cents carry", "WallBoard",
      board("card", [badge("for the nineteen seventy-one Club", "1971")]), "The '1971 3' badge."),
 shot("s06_fulls", "Two of its Cents carry", "the full desert and", "WallBoard",
      board("card", [badge("Two of its Cents carry", "Full x")]), "Full x 2 badge."),
 shot("s06b_fulls", "the full desert and", "Two are Iridescent", "CentRow",
      row("Full x 2", [{"n": 7139, "patina": "desert", "caption": "Full Desert · #7139", "at_phrase": "the full desert and"},
                       {"n": 9258, "patina": "red", "caption": "Full Red · #9258", "at_phrase": "and a full red"}], cols=2),
      "The two full-patina Cents, arriving as named."),
 shot("s07_irid", "Two are Iridescent", "a copper surface overlaid", "WallBoard",
      board("card", [badge("Two are Iridescent", "Iridescent")]), "Iridescent x 2 badge."),
 shot("s07b_irid", "a copper surface overlaid", "And two are Ghost", "CentRow",
      row("Iridescent x 2", [{"n": 2981, "caption": "#2981", "at_phrase": "a copper surface overlaid"},
                             {"n": 7713, "caption": "#7713", "at_phrase": "a copper surface overlaid"}], cols=2, labelsUnder=True),
      "The two Iridescent Cents."),
 shot("s08_ghost", "And two are Ghost", "The Wall completes six", "CentRow",
      row("Ghost x 2", [{"n": 7139, "caption": "#7139", "at_phrase": "And two are Ghost"},
                        {"n": 5448, "caption": "#5448", "at_phrase": "And two are Ghost"}], cols=2, labelsUnder=True),
      "The two Ghost Cents."),
 shot("s09_sets", "The Wall completes six", "a significant verdigris", "WallBoard",
      board("card", [{"at_phrase": "The Wall completes six", "target": {"card": True}}, badge("A Spectrum Set: a significant", "Spectrum")]),
      "The card, then the Spectrum Set badge."),
 shot("s09b_spectrum", "a significant verdigris", "A Chronicle Set", "CentRow",
      row("Spectrum Set", [
        {"n": 8550, "patina": "verdigris", "caption": "Significant Verdigris · #8550", "at_phrase": "a significant verdigris", "src": "hires/8550.webp"},
        {"n": 8394, "patina": "obsidian", "caption": "Significant Obsidian · #8394", "at_phrase": "a significant obsidian", "src": "hires/8394.webp"},
        {"n": 9258, "patina": "red", "caption": "Full Red · #9258", "at_phrase": "a full red, a", "src": "hires/9258.webp"},
        {"n": 7139, "patina": "desert", "caption": "Full Desert · #7139", "at_phrase": "a full desert, a", "src": "hires/7139.webp"},
        {"n": 2981, "patina": "gold", "caption": "Notable Gold · #2981", "at_phrase": "a notable gold", "src": "hires/2981.webp"},
        {"n": 9469, "patina": "orange", "caption": "Orange · #9469", "at_phrase": "and an orange", "src": "hires/9469.webp"}],
        solo_until="Notable means clearly", readout="1 of 15", caption="collectors with this Set", readout_at="one of only fifteen collectors"),
      "Each Spectrum Cent alone as named, then the row; '1 of 15' collectors (16 Walls hold one; the artist wallet is excluded)."),
 shot("s10_chron", "A Chronicle Set", "a Cent from nineteen seventy-one, from", "WallBoard",
      board("card", [badge("A Chronicle Set", "Chronicle")]), "Chronicle Set badge."),
 shot("s10b_chron", "a Cent from nineteen seventy-one, from", "A Full Mint Set", "CentRow",
      row("Chronicle Set", [{"n": 366, "caption": "1971", "at_phrase": "a Cent from nineteen seventy-one, from"},
                            {"n": 1965, "caption": "1979", "at_phrase": "from nineteen seventy-nine and"},
                            {"n": 372, "caption": "1982", "at_phrase": "and from nineteen eighty-two"}], cols=3, labelsUnder=True),
      "Chronicle Set: one Cent from each year."),
 shot("s11_mint", "A Full Mint Set", "an S mint, a D", "WallBoard",
      board("card", [badge("A Full Mint Set", "Full Mint")]), "Full Mint Set badge."),
 shot("s11b_mint", "an S mint, a D", "A Contamination Set", "CentRow",
      row("Full Mint Set", [{"n": 2446, "caption": "1974-S", "at_phrase": "an S mint, a D"},
                            {"n": 7713, "caption": "1973-D", "at_phrase": "a D mint and"},
                            {"n": 7139, "caption": "1967", "at_phrase": "a Cent with no mint"}], cols=3, labelsUnder=True),
      "Full Mint Set: an S, a D and a no-mint-mark Cent."),
 shot("s12_cont", "A Contamination Set", "special oddities", "WallBoard",
      board("card", [badge("A Contamination Set", "Contamination Set")]), "Contamination Set (4/12) badge."),
 shot("s12b_cont", "special oddities", "and a nineteen eighties Set", "CentRow",
      row("Contamination Set (4/12)", [
        {"n": 372, "caption": "Special Oddities · #372", "at_phrase": "special oddities", "src": "hires/372.webp"},
        {"n": 1399, "caption": "Obscure Adhesive · #1399", "at_phrase": "obscure adhesive", "src": "hires/1399.webp"},
        {"n": 2387, "caption": "Speckles · #2387", "at_phrase": "speckles", "src": "hires/2387.webp"},
        {"n": 8899, "caption": "Alien Secretion · #8899", "at_phrase": "alien secretion", "src": "hires/8899.webp"}],
        solo_until="And a nineteen seventies", cols=2),
      "One Cent per contamination type, alone as named, then the row."),
 shot("s13_decades", "and a nineteen eighties Set", "every mint year from", "WallBoard",
      board("card", [{"at_phrase": "and a nineteen eighties Set", "target": {"box": [572, 564, 876, 626]}, "mark": True}]),
      "1970s Set and 1980s Set badges together (box from layoutWall: 1970s [582,574,719,616], 1980s [729,574,866,616]). The Contamination row gathers over 'And a 1970s Set', so this shot starts one beat later."),
 shot("s13b_decades", "every mint year from", "The Wall carries Diamond", "CentRow",
      row("1970s Set · 1980s Set", [{"n": n, "caption": str(y), "at_phrase": "every mint year from"} for n, y in
          [(3838, 1970), (366, 1971), (4948, 1972), (1399, 1973), (2981, 1974), (830, 1975), (7599, 1976),
           (2387, 1977), (5430, 1978), (1965, 1979), (3815, 1980), (1295, 1981), (372, 1982)]], labelsUnder=True),
      "One Cent for every year 1970-1982."),
 shot("s14_diamond", "The Wall carries Diamond", "And it is a Mint", "WallBoard",
      board("card", [badge("The Wall carries Diamond", "Diamond")]), "Diamond Hands badge."),
 shot("s15_keeper", "And it is a Mint", "minted four of its", "WallBoard",
      board("card", [badge("And it is a Mint", "Mint Keeper")]), "Mint Keeper x 4 badge."),
 shot("s15b_keeper", "minted four of its", "Find all of the Collector", "WallBoard",
      board("grid", [{"at_phrase": "minted four of its", "until_phrase": "never sold", "target": {"grid_end": True}}],
            highlights=[{"at_phrase": "minted four of its", "group": "mint_keeper"}]), "The four Mint Keeper Cents ringed in the rows."),
 shot("s16_collectors", "Find all of the Collector", None, "WallShot",
      {"src": "vision/traits_lab.png", "width": 2964, "height": 1654, "moves": [{"at_phrase": "under Collectors", "box": [1185, 1575, 1358, 1635], "mark": True}]},
      "cents.vision Traits Lab; one zoom, onto Collectors."),
]
tl = {"essay": {"title": "Collector Wall", "subtitle": T, "author": "shibboleth", "source": "https://cents.vision/collectors.html",
                "version": f"v1, opener {variant}{' + 3DCENTS clip' if use_clip else ''} (2026-10-27)"},
      "_what": "Collector Wall: ScrappyT. Every coin is a real Cent by number; every figure comes from data/wall_board.json (cents.vision, 27 Oct 2026). No wallet address appears.",
      "shots": shots}
json.dump(tl, open(F / "timeline.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(shots)} shots, opener {variant}, clip {use_clip}")
