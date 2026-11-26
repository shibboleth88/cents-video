"""Write timeline.json and assets.json for One Cent #189 v1 (script v0.2, approved by shibboleth 2026-11-26 02:43Z,
"go ahead with the video creation please"). Shots are anchored on phrases of the recording, so this file does not
change when the take does. Run from the repo root: python3 -I films/onecent-189/timeline/make_timeline.py"""
import json, pathlib, hashlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
F = ROOT / "films/onecent-189"
pools = json.load(open(F / "script/pools.json"))
hops = json.load(open(F / "ledger/hops.json"))
SPIN = {"src": "3dcents/189-360-30fps.mp4", "width": 1080, "height": 1920, "frames": 150,
        "coin": {"cx": 539.5, "cy": 959.5, "d": 776}, "credit": "3D render: 3DCENTS by sinvalli", "credit_at_end": True}
C189 = {"inscription": 66001226, "n": 189, "front": "hires/189.webp"}
DATE = [0.6, 0.58, 0.88, 0.77]               # the date and the D, the same box on #189 and #9794 (both photos checked)
HAIR, CHEEK, COAT = [0.32, 0.22, 0.52, 0.40], [0.50, 0.30, 0.64, 0.50], [0.24, 0.64, 0.40, 0.80]   # Claude's reading
S = []
def shot(i, start, end, purpose, component=None, props=None, asset=None, join=False):
    s = {"shot_id": i, "start": start, "end": end, "purpose": purpose, "visual_kind": "real" if asset else "code"}
    if component: s["component"] = component
    if asset: s["asset_id"] = asset
    s["props"] = props or {}
    if join: s["join_prev"] = True
    S.append(s)
P = lambda t: {"at_phrase": t}
shot("s01_open", {"at_start": True}, P("Cards, sneakers, watches"),
     "Look C opening as #1867: play button, CENTS STORY TIME, the 'look closer' sticker, one 3DCENTS turn. No year or mint opening.",
     "StoryOpen", {**C189, "spin": SPIN, "sticker": "look closer"})
shot("s02_words", P("Cards, sneakers, watches"), P("and coins are graded"),
     "Each kind of collectible as it is said. No picture claims to show grading.",
     "StoryWords", {"words": [{"at_phrase": "Cards, sneakers", "text": "Cards"}, {"at_phrase": "sneakers, watches and", "text": "Sneakers"},
                              {"at_phrase": "watches and coins", "text": "Watches"}]})
shot("s03_convention", P("and coins are graded"), P("traded like securities"),
     "Coins. LoC photo of coins on display at a numismatic convention; it is not said to show grading.",
     props={"caption": "Rare coins on display at a numismatic convention, Washington, D.C., 1937", "maxWidth": 732}, asset="loc_convention_1937", join=True)
shot("s04_sale", P("traded like securities"), P("and a grade rewards"),
     "Traded: a coin offered for sale at a store counter, 1967.",
     props={"caption": "A coin for sale at a department store counter, Washington, D.C., 1967", "maxWidth": 732}, asset="loc_coin_sale_1967", join=True)
shot("s05_scale", P("and a grade rewards"), P("The collectors of CENTS"),
     "The grade scale of the source (Littleton's terms and numbers); the marker reaches 70 as 'how little has happened' is said. Says nothing about any Cent.",
     "StoryScale", {"kicker": "Coin grades", "source": "Grading terms: Littleton Coin Company",
                    "ticks": [{"v": 1, "label": "Poor"}, {"v": 12, "label": "Fine"}, {"v": 20, "label": "Very Fine"}, {"v": 40, "label": "Extra Fine"},
                              {"v": 50, "label": "About Uncirculated"}, {"v": 60, "label": "Uncirculated"}, {"v": 70, "label": "Perfect Uncirculated"}],
                    "stops": [{"at_phrase": "and a grade rewards", "to": 30, "dur": 1.0}, {"at_phrase": "how little has happened", "to": 70, "dur": 1.0}]})
shot("s06_concept", P("The collectors of CENTS"), P("In a conversation in"),
     "Concept C26 named on screen with the episode's Cent, at the turn from grading to CENTS.",
     "StoryCard", {"n": 189, "front": "hires/189.webp", "concept": {"at_phrase": "The collectors of CENTS", "label": "Coin collecting turned over"}})
shot("s07_book", P("In a conversation in"), P("Barbara Kruger"),
     "Where Myers quoted Kruger (shibboleth 02:10Z): the book, typeset. QUOTE_BANK E111/H25.",
     "StoryText", {"chip": "Book", "title": "Proof of Work", "italic": True,
                   "lines": [{"text": "Rhea Myers, 2022", "look": "sub"}, {"text": "In conversation with Maya B. Kronic", "look": "note"}]})
shot("s08_kruger", P("Barbara Kruger"), P("A circulated copper cent"),
     "Kruger's line on plain black, lit word by word, so it is not presented as being about these coins (QUOTE_BANK H25: About CENTS? No).",
     "StoryQuote", {"quote": {"at_phrase": "Money is an information", "text": "Money is an information-destroying medium."},
                    "who": "Barbara Kruger", "where": "quoted by Rhea Myers, Proof of Work (2022)"})
shot("s09_pitching", P("A circulated copper cent"), P("is the exception"),
     "Pennies in circulation, 1940 (bronze, 95% copper, so 'copper cent' holds).",
     props={"caption": "Pitching pennies at a band concert, Lincoln, Vermont, 1940", "maxWidth": 732}, asset="loc_pitching_1940")
shot("s10_scramble", P("is the exception"), P("Its wear and patina"), "Pennies in circulation, 1910.",
     props={"caption": "Scramble for pennies, Thanksgiving, 1910", "maxWidth": 732}, asset="loc_scramble_1910", join=True)
shot("s11_diving", P("Its wear and patina"), P("record where it has"), "Pennies in circulation, 1915.",
     props={"caption": "Diving for pennies, Madison Square, 1915", "maxWidth": 732}, asset="loc_diving_1915", join=True)
shot("s12_desk", P("record where it has"), P("In the image of Cent"), "Pennies Chang gathered, at his studio.",
     props={"caption": "Pennies at Rutherford Chang's studio", "maxWidth": 732}, asset="desk_c063", join=True)
shot("s13_setup", P("In the image of Cent"), P("that record is red"),
     "'In the image of': the setup in which each coin was photographed. The script does not call the Cent a photograph.",
     props={"caption": "Rutherford Chang's penny photography setup", "maxWidth": 732}, asset="photo_setup_c062", join=True)
shot("s14_red", P("that record is red"), P("In the Traits Atlas"), "#189 itself, slow push-in, the trait as a chip.",
     "StoryOpen", {**C189, "mode": "lens", "moves": [{"at_phrase": "that record is red", "box": None, "zoom": 1.12, "dur": 2.0}],
                   "reads": [{"at_phrase": "a trait called Full", "chip": "Full Red"}]})
shot("s15_atlas_red", P("In the Traits Atlas"), P("surface film resulting"), "The Atlas entry, its definition highlighted.",
     props={"caption": "Traits Atlas, Red Patina", "maxWidth": 720}, asset="atlas_red")
shot("s16_chem", P("surface film resulting"), P("and Full Red means"),
     "The Atlas's chemistry line, quoted with its 'primarily'. No claim about #189's own chemistry.",
     "StoryText", {"chip": "Traits Atlas: chemistry", "title": "Cu₂O", "titleSize": 200,
                   "lines": [{"text": "cuprite", "look": "sub"}, {"text": "“Primarily composed of cuprite”", "look": "quote"}]}, join=True)
shot("s17_red_ladder", P("and Full Red means"), P("generally over about"),
     "The Atlas's own three red examples with its scale, qualifiers kept ('roughly', 'or less if', 'generally').",
     "StoryLadder", {"title": "Atlas scale: red", "credit": "Traits Atlas, CENTS Trait Council",
                     "rows": [{"n": 4075, "front": "hires/4075.webp", "level": "Notable", "range": "roughly up to 20%"},
                              {"n": 9507, "front": "hires/9507.webp", "level": "Significant", "range": "about 20–70%, or less if strongly red"},
                              {"n": 9427, "front": "hires/9427.webp", "level": "Full", "range": "generally over about 70%", "at_phrase": "dominant surface condition"}]})
shot("s18_full", P("generally over about"), P("Seventy-one Cents are"),
     "The Atlas's Full red example, then #189, which the Trait Council placed in Full Red. No coverage is measured or drawn on #189.",
     "StoryDissolve", {"first": "a", "cards": {"a": {"n": 9427, "inscription": 66001191, "front": "hires/9427.webp", "chip": "Atlas example: Full"},
                                              "b": {**C189, "chip": "Full Red"}},
                       "swaps": [{"at_phrase": "percent of the coin", "to": "b"}]})
shot("s19_dots", P("Seventy-one Cents are"), P("Cent number one eighty-nine is the only"),
     "All 10,000 in number order, the 71 Full Red lit, #189 ringed (Sep 2026 export, recounted from raw flags).",
     "StoryDots", {"lit": pools["full_red"], "mark": 189, "count": "71", "label": "Full Red"})
fr = sorted(n for n in pools["full_red"] if n != 189) + [189]
shot("s20_scroll", P("Cent number one eighty-nine is the only"), P("dated nineteen sixty"),
     "The whole Full Red pool, fast, settling on #189 (spotlight).",
     "StoryScroll", {"ns": fr, "dir": "assets/189/thumbs", "label": "Full Red", "count": "71", "mark": 189, "until": "dated nineteen sixty"}, join=True)
shot("s21_date", P("dated nineteen sixty"), P("Pale, sandy films"), "The date and the D on #189.",
     "StoryOpen", {**C189, "mode": "lens", "moves": [{"at_phrase": "dated nineteen sixty", "box": DATE, "mark": True, "dur": 0.6}],
                   "reads": [{"at_phrase": "dated nineteen sixty", "chip": "Dated 1960"}]})
shot("s22_desert_ladder", P("Pale, sandy films"), P("lie on Lincoln's hair"),
     "The Atlas desert scale, Notable lit, the others dim.",
     "StoryLadder", {"title": "Atlas scale: desert", "credit": "Traits Atlas, CENTS Trait Council",
                     "rows": [{"n": 7884, "front": "hires/7884.webp", "level": "Notable", "range": "roughly up to 20%"},
                              {"n": 5553, "front": "hires/5553.webp", "level": "Significant", "range": "about 20–70%, or less if strongly colored", "lit": False},
                              {"n": 5320, "front": "hires/5320.webp", "level": "Full", "range": "generally over about 70%", "lit": False}]})
shot("s23_zooms", P("lie on Lincoln's hair"), P("clearly visible, but local"),
     "The three desert areas on #189, each as it is named. The areas are Claude's reading (flagged to shibboleth).",
     "StoryOpen", {**C189, "mode": "lens",
                   "moves": [{"at_phrase": "Lincoln's hair", "box": HAIR, "mark": True, "dur": 0.5},
                             {"at_phrase": "cheek and coat", "box": CHEEK, "mark": True, "dur": 0.4},
                             {"at_phrase": "and coat clearly", "box": COAT, "mark": True, "dur": 0.4}],
                   "reads": [{"at_phrase": "lie on Lincoln's", "chip": "Notable Desert"}]})
shot("s24_atlas_desert", P("clearly visible, but local"), P("up to about a fifth"), "The Atlas's own words for Notable desert, highlighted.",
     props={"caption": "Traits Atlas, Desert", "maxWidth": 720}, asset="atlas_desert")
shot("s25_whole", P("up to about a fifth"), P("Compare Cent number"), "#189 whole again.",
     "StoryOpen", {**C189, "mode": "lens", "moves": [{"at_phrase": "up to about a fifth", "box": None, "zoom": 1.06, "dur": 1.2}],
                   "reads": [{"at_phrase": "up to about a fifth", "chip": "Notable Desert"}]})
shot("s26_flip", P("Compare Cent number"), P("As money, any cent"),
     "The fast back-and-forth (shibboleth 02:10Z): about 0.6 s a side, the name swapping with the coin, both zoomed to the date and D, back out for 'close to mint state', settling on #189.",
     "StoryFlip", {"a": {**C189, "chip": "Two traits"}, "b": {"n": 9794, "inscription": 65966150, "front": "hires/9794.webp", "chip": "Close to mint state"},
                   "period": 0.6, "settle": "close to mint state", "chips_at": "and close to mint",
                   "moves": [{"at_phrase": "also a nineteen sixty", "box": DATE, "dur": 0.6}, {"at_phrase": "and close to mint", "box": None, "dur": 0.6}]})
shot("s27_1960", P("As money, any cent"), P("As a Cent, none is"),
     "Every Cent dated 1960, fast: as money each was as good as any other.",
     "StoryScroll", {"ns": sorted(pools["year1960"]), "dir": "assets/189/thumbs", "label": "Dated 1960", "until": "As a Cent, none is"})
shot("s28_alone", P("As a Cent, none is"), P("A Cent's worth is set"), "#189 alone.",
     "StoryOpen", {**C189, "mode": "lens", "moves": [{"at_phrase": "As a Cent, none", "box": None, "zoom": 1.08, "dur": 1.2}]})
shot("s29_people", P("A Cent's worth is set"), P("exchange, catalog and"), "The people of the collection (MAKES CENTS), no wallet addresses.",
     props={"caption": "MAKES CENTS interviews", "maxWidth": 720}, asset="makes_cents")
rows = [(h["date"][:10], h["txid"][:12]) for h in hops]
shot("s30_ledger", P("exchange, catalog and"), P("catalog and compare"),
     "Exchange: the satoshi's moves on Bitcoin (ledger/LEDGER_189.md), dates and short transaction ids only.",
     "StoryText", {"chip": "Moves on Bitcoin", "title": "Cent #189", "titleSize": 96, "rows": rows, "rows_head": ["Date", "Transaction"], "rows_top": 610}, join=True)
shot("s31_council", P("catalog and compare"), P("compare it, and set"), "Catalog: the Trait Council's process document.",
     props={"caption": "Trait Council", "maxWidth": 732}, asset="trait_council_s1075", join=True)
shot("s32_compare", P("compare it, and set"), P("and set again each"), "Compare: two Cents side by side (cents.gallery).",
     props={"caption": "Shiny and wild", "maxWidth": 732}, asset="shiny_wild_s0565", join=True)
shot("s33_zoomout", P("and set again each"), {"after_phrase": "each time.", "plus": 0.3}, "The field of Cents, pulling back.",
     props={"caption": "", "maxWidth": 732}, asset="zoom_out_c020", join=True)
shot("s34_close", {"after_phrase": "each time.", "plus": 0.3}, P("Find out more about"), "Closing card, one turn (as #1867).",
     "StoryOpen", {**C189, "mode": "close", "spin": SPIN})
shot("s35_gallery", P("Find out more about"), P("and explore the traits"), "End card: cents.gallery (reused from #1867).",
     props={"caption": "cents.gallery", "maxWidth": 600}, asset="endcard_gallery")
shot("s36_vision", P("and explore the traits"), {"after_phrase": "on cents dot vision.", "plus": 0.6}, "End card: cents.vision (reused from #1867).",
     props={"caption": "cents.vision", "maxWidth": 732}, asset="endcard_vision")
shot("s37_credits", {"after_phrase": "on cents dot vision.", "plus": 0.6}, {"after_phrase": "on cents dot vision.", "plus": 3.3}, "Credits 1.",
     "Credits", {"lines": ["Images: Rutherford Chang; cents.gallery media library", "3D render: 3DCENTS by sinvalli",
                           "Traits Atlas: CENTS Trait Council, via cents.vision", "cents.vision screenshots courtesy Dr. Martin Lehnen"]})
shot("s38_credits", {"after_phrase": "on cents dot vision.", "plus": 3.3}, {"after_phrase": "on cents dot vision.", "plus": 6.0}, "Credits 2: where Myers quoted Kruger, in full.",
     "Credits", {"lines": ["Barbara Kruger, quoted by Rhea Myers in conversation with Maya B. Kronic,",
                           "\u201c\u2018Hurt Me! No, Not Like That!\u2019 A Conversation with Rhea Myers\u201d,",
                           "in Proof of Work (Urbanomic, 2022)"]}, join=True)
shot("s39_credits", {"after_phrase": "on cents dot vision.", "plus": 6.0}, {"at_end": True}, "Credits 3.",
     "Credits", {"lines": ["Archival photographs: Library of Congress, Prints & Photographs Division", "Grading terms: Littleton Coin Company"],
                 "url": "cents.gallery"}, join=True)

tl = {"essay": {"title": "Cent #189", "subtitle": "Inscription #66001226", "author": "shibboleth",
                "source": "/mnt/project-files/single-cent-series/189/189_proposal_v0.2.md",
                "version": "v1 (2026-11-26): script v0.2 approved by shibboleth ('go ahead with the video creation please', 02:43Z)"},
      "_what": "Cent #189 (1960 D): Full Red, Notable Desert. Baseline format: concept C26 (coin collecting turned over) from the baseline text's 'Now', Kruger via Myers, then the traits, then value set again (C04). A new picture about every 2-3 s.",
      "shots": S}
json.dump(tl, open(F / "timeline/timeline.json", "w"), indent=1, ensure_ascii=False)

# ---- assets
def entry(path, subject, source, rights, motion=False, **kw):
    p = ROOT / path
    from PIL import Image
    if motion:
        import subprocess
        w, h = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(p)],
                              capture_output=True, text=True, check=True).stdout.strip().split(",")
        w, h = int(w), int(h)
    else:
        w, h = Image.open(p).size
    return {"path": path, "staged_as": path.removeprefix("public/assets/"), "sha1": hashlib.sha1(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size,
            "width": w, "height": h, "motion": motion, "kind": "real", "subject": subject, "source": source, "rights": rights,
            "verified_at": "2026-11-26", **kw}
LOC = "Library of Congress, Prints & Photographs Division; LoC rights statement 'No known restrictions on publication'. Shown to shibboleth in proposal v0.2 with the PD/CC0 question; approved with 'go ahead' 02:43Z (taken as yes, said so in the thread)."
LIB = "cleared (user's media library)"
old = json.load(open(F.parent / "onecent-1867/timeline/assets.json"))["assets"]
A = {
 "loc_convention_1937": entry("public/assets/189/loc_convention_1937.jpg", "Rare coins under glass at the American Numismatic Convention, Washington, D.C., 24 Aug 1937 (Harris & Ewing).", "LoC item 2016872233 (hec 23258v), 1024 px", LOC),
 "loc_coin_sale_1967": entry("public/assets/189/loc_coin_sale_1967.jpg", "A woman's hands holding a gold coin for sale on a display case with other coins, Woodward & Lothrop department store, Washington, D.C., 1967 (U.S. News & World Report).", "LoC item 2025160034 (ppmsca 89529v), 1024 px", LOC),
 "loc_pitching_1940": entry("public/assets/189/loc_pitching_1940.jpg", "Boys pitching pennies at a band concert, Lincoln, Vermont, 1940 (FSA/OWI).", "LoC item 2017764722 (fsa 8b30814v), 1024 px", LOC),
 "loc_scramble_1910": entry("public/assets/189/loc_scramble_1910.jpg", "Scramble for pennies, Thanksgiving, about 1910 (Bain News Service).", "LoC item 2014689989 (ggbain 10005v), 1024 px", LOC),
 "loc_diving_1915": entry("public/assets/189/loc_diving_1915.jpg", "Diving for pennies, Madison Sq., about 1915 (Bain News Service).", "LoC item 2014702817 (ggbain 22867v), 1024 px", LOC),
 "desk_c063": entry("public/assets/189/desk_c063.jpg", "Pennies arranged across a desk at Rutherford Chang's studio, with rolls, a scale and a bowl of pennies.", "cents.gallery media library C063, scaled from 4032 px", LIB),
 "photo_setup_c062": entry("public/assets/189/photo_setup_c062.jpg", "Rutherford Chang's penny photography setup: a camera on a stand over a lit stage, a laptop showing a penny.", "cents.gallery media library C062, scaled from 4032 px", LIB),
 "atlas_red": entry("public/assets/189/atlas_red_whole_lines.png", "The cents.vision Traits Atlas entry 'Red (Patina)': its summary, 'A red to reddish-brown surface film resulting from oxidative conversion of copper.' marked by a copper highlight added by us.", "Screenshot with script/atlas_shoot.cjs (from #1867) of https://cents.vision/traits-atlas/red.html, cropped to whole lines", "cents.vision (Dr. Martin Lehnen; cleared); Atlas text by the CENTS Trait Council", max_display_width=720),
 "atlas_desert": entry("public/assets/189/atlas_desert_whole_lines.png", "The cents.vision Traits Atlas desert entry, Intensity Scale: 'Notable desert: Clearly visible desert toning, but still localised' highlighted by us.", "Screenshot with script/atlas_shoot.cjs of https://cents.vision/traits-atlas/desert.html, cropped to whole lines", "cents.vision (Dr. Martin Lehnen; cleared); Atlas text by the CENTS Trait Council", max_display_width=720),
 "trait_council_s1075": entry("public/assets/189/trait_council_s1075.jpg", "The CENTS Trait Council's process document (aims, phases, tasks).", "cents.gallery media library S1075, scaled from 3184 px", LIB),
 "shiny_wild_s0565": entry("public/assets/189/shiny_wild_s0565.jpg", "Two Cents side by side: a bright 1971 and a heavily patinated 1976.", "cents.gallery media library S0565 'both shiny and wild', scaled from 2100 px", LIB),
 "zoom_out_c020": entry("public/assets/189/zoom_out_c020.mp4", "A fast two-second move from a few large pennies out to a dense field of Cents.", "cents.gallery media library C020 (web encode), 30 fps, 1280 px", LIB, motion=True, duration=2.03),
 "makes_cents": {**old["makes_cents"], "copied_from": "films/onecent-1867/timeline/assets.json"},
 "endcard_gallery": {**old["endcard_gallery"], "copied_from": "films/onecent-1867/timeline/assets.json"},
 "endcard_vision": {**old["endcard_vision"], "copied_from": "films/onecent-1867/timeline/assets.json"},
}
json.dump({"assets": A}, open(F / "timeline/assets.json", "w"), indent=1, ensure_ascii=False)
print(len(S), "shots;", len(A), "assets")
