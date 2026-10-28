"""Writes timeline.json for the ScrappyT episode, v2: reoriented around its one
of every trait (user, 2026-10-27 18:18Z). v1 is make_timeline_v1.py. The opener variant is the one
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

TRAITS = ["Desert", "Ghost", "Verdigris", "Obsidian", "Red", "Gold", "Orange", "Iridescent", "Corroded", "Lustrous",
          "Striated", "Abraded", "Faceless", "Fingerprint", "White drips", "Contaminated", "Assassin", "Vandalized", "Wheat"]
CONT = [372, 1399, 2387, 8899]
it = lambda trait, n, ph, cap, **kw: dict({"trait": trait, "n": n, "src": f"hires/{n}.webp", "at_phrase": ph, "caption": cap}, **kw)
ITEMS = [
 it("Desert", 7139, None, "#7139 · Full"), it("Ghost", 7139, None, "#7139"),
 it("Verdigris", 8550, "Verdigris, green to teal", "#8550 · Significant"),
 it("Obsidian", 8394, "Obsidian, dark brown to", "#8394 · Significant"),
 it("Red", 9258, "Red, scarlet to russet", "#9258 · Full"),
 it("Gold", 5856, "Gold, honey gold to", "#5856 · Notable"),
 it("Orange", 9469, "Orange, given only to", "#9469"),
 it("Iridescent", 7713, "Iridescent, a copper surface", "#7713 · 1 of 20"),
 it("Corroded", 366, "Corroded, oxidation that", "#366"),
 it("Lustrous", 830, "Lustrous, original mint shine", "#830"),
 it("Striated", 1295, "Striated, parallel lines", "#1295"),
 it("Abraded", 8136, "Abraded, copper missing", "#8136 · Heavily abraded"),
 it("Faceless", 1965, "Faceless", "#1965"),
 it("Fingerprint", 508, "Fingerprint, ridges clear", "#508", zoom={"box": [0.22, 0.1, 0.82, 0.7]}),
 it("White drips", 2654, "White drips and streaks", "#2654"),
 {"trait": "Contaminated", "cents": CONT, "at_phrase": "Contaminated, foreign matter", "caption": "4 of 12 types"},
 it("Assassin", 739, "Assassin, one round mark", "#739", zoom={"box": [0.32, 0.2, 0.44, 0.32]}),
 it("Vandalized", 7745, "Vandalized, marks that show", "#7745 · 1 of 26", zoom={"box": [0.3, 0.17, 0.66, 0.52]}),
 it("Wheat", 3824, "And Wheat, struck", "#3824 · 1956", zoom={"box": [0.62, 0.58, 0.86, 0.71], "at_phrase": "from nineteen fifty-six, the"}),
]
tally = lambda **kw: dict({"title": T, "traits": TRAITS, "items": [dict(i) for i in ITEMS]}, **kw)

opener = {"variant": variant, "wall": W, "show": "card", "until_phrase": "Its forty-one Cents", "moves": [],
          "progress": {"total_frames": TOTAL}}
if variant in ("turn", "showcase"):
    opener["clip"] = dict(CLIP, src="3dcents/7139-360-30fps-alpha.webm", alpha=True) if use_clip else PLACEHOLDER
sig = {"title": T, "n": 7139, "readout": "1967", "caption": "Full Desert · Ghost"}
if use_clip: sig["clip"] = CLIP

shots = [
 shot("s00_open", None, "Its forty-one Cents", "WallOpener", opener,
      f"Opening ({variant}): the card from frame 0, signature turning, Cents and badges lighting in turn."),
 shot("s01_all", "Its forty-one Cents", "Even the artist wallet", "TraitTally",
      tally(mode="grid", at_phrase="Its forty-one Cents", until_phrase="no other Wall on"),
      "The 19 Atlas traits as a checklist, each with this Wall's Cent, filling as the line is spoken (counts: merged-new2.json, 27 Oct 2026)."),
 shot("s01b_artist", "Even the artist wallet", "Its signature Cent", "TraitTally",
      tally(mode="grid", lit_all=True, focus={"trait": "Iridescent", "at_phrase": "has no Iridescent"}),
      "The artist wallet holds 18 of 19: no Iridescent. Iridescent stands out."),
 shot("s02_sig", "Its signature Cent", "Ghost means a full", "WallStandout", sig, "The signature Cent #7139: Desert and Ghost."),
 shot("s02b_ghost", "Ghost means a full", "Of the thirty-three Ghost", "WallStandout",
      {"title": T, "n": 7139, "readout": "Ghost", "caption": "Lincoln set apart from the field", "src": "hires/7139.webp"},
      "What Ghost means (Traits Atlas wording). Whole-face trait: no zoom."),
 shot("s02c_13", "Of the thirty-three Ghost", "Here are the other seventeen", "WallStandout",
      {"title": T, "n": 7139, "readout": "13 of 33", "caption": "Full desert Ghost Cents", "src": "hires/7139.webp"},
      "13 of the 33 Ghost Cents are full desert."),
 shot("s03_walk", "Here are the other seventeen", "Nineteen of nineteen", "TraitTally",
      tally(mode="walk", lit_before=["Desert", "Ghost"]),
      "One Cent per trait, large, as each is named; the band of 19 Cents keeps count. Zooms on the fingerprint, the assassin mark, the vandal's outline, and the date."),
 shot("s04_full", "Nineteen of nineteen", "The Wall spans two wallets", "TraitTally",
      tally(mode="grid", lit_all=True), "All nineteen, lit."),
 shot("s05_count", "The Wall spans two wallets", "which puts it in the Quarter", "WallBoard",
      board("grid", [{"at_phrase": "The Wall spans two wallets", "until_phrase": "which puts it in the Quarter", "target": {"grid_end": True}}],
            readout={"at_phrase": "The Wall spans two wallets", "count": {"from": 0, "to": 41, "until_phrase": "nineteen fifty-six to", "suffix": " Cents"}}),
      "The opened collection: all 41 Cents scrolling with a count."),
 shot("s05b_quarter", "which puts it in the Quarter", "It completes six Sets", "WallBoard",
      board("card", [badge("which puts it in the Quarter", "Quarter Club")]), "Quarter Club badge."),
 shot("s06_sets", "It completes six Sets", "all four base patinas", "WallBoard",
      board("card", [badge("among them a Spectrum Set", "Spectrum")]), "The Sets rows, then the Spectrum Set badge."),
 shot("s06b_spectrum", "all four base patinas", "The Wall carries Diamond", "CentRow",
      row("Spectrum Set", [{"n": n, "src": f"hires/{n}.webp"} for n in (8550, 8394, 9258, 7139, 5856, 9469)],
          readout="1 of 15", caption="collectors who hold a Spectrum Set", readout_at="one of only fifteen collectors", cols=3),
      "The six patina Cents of the Spectrum Set; '1 of 15' collectors (16 Walls hold one; the artist wallet is excluded)."),
 shot("s07_diamond", "The Wall carries Diamond", "And it is a Mint", "WallBoard",
      board("card", [badge("The Wall carries Diamond", "Diamond")]), "Diamond Hands badge."),
 shot("s08_keeper", "And it is a Mint", "minted four of its", "WallBoard",
      board("card", [badge("And it is a Mint", "Mint Keeper")]), "Mint Keeper x 4 badge."),
 shot("s08b_keeper", "minted four of its", "Find all of the Collector", "WallBoard",
      board("grid", [{"at_phrase": "minted four of its", "until_phrase": "never sold", "target": {"grid_end": True}}],
            highlights=[{"at_phrase": "minted four of its", "group": "mint_keeper"}]), "The four Mint Keeper Cents ringed in the rows."),
 shot("s09_collectors", "Find all of the Collector", None, "WallShot",
      {"src": "vision/traits_lab.png", "width": 2964, "height": 1654, "moves": [{"at_phrase": "under Collectors", "box": [1185, 1575, 1358, 1635], "mark": True}]},
      "cents.vision Traits Lab; one zoom, onto Collectors."),
]
tl = {"essay": {"title": "Collector Wall", "subtitle": T, "author": "shibboleth", "source": "https://cents.vision/collectors.html",
                "version": f"v2, one of every trait, opener {variant}{' + 3DCENTS clip' if use_clip else ''} (2026-10-27)"},
      "_what": "Collector Wall: ScrappyT. Every coin is a real Cent by number; every figure comes from data/wall_board.json and merged-new2.json (cents.vision, 27 Oct 2026). No wallet address appears.",
      "shots": shots}
json.dump(tl, open(F / "timeline.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(shots)} shots, opener {variant}, clip {use_clip}")
