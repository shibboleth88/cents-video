"""Write timeline.json for the CENTS introduction film (script v0.3, 2026-11-27; shibboleth asked for the film:
"Let's please make a video of the introduction of approximately 2.2 minutes"). Shots are anchored on phrases of
the recording (spoken forms, as in audio/tts_text.txt), so this file does not change when the take does. Every
picture named here must be in timeline/assets.json (stage_assets.py) or be a cents.vision front in public/hires/.

    python3 -I films/intro-2min/timeline/make_timeline.py   (from the repo root)
"""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
F = ROOT / "films/intro-2min"
A = json.load(open(F / "timeline/assets.json"))["assets"]

def img(k):
    """An asset as the shot components take it: path under public/, and its size."""
    if k not in A: sys.exit(f"asset {k!r} is not in assets.json")
    a = A[k]
    return {"src": "assets/" + a["staged_as"], "w": a["width"], "h": a["height"]}
def front(n):
    p = ROOT / f"public/hires/{n}.webp"
    if not p.exists(): sys.exit(f"front {n} is not in public/hires (stage_assets.py)")
    return f"hires/{n}.webp"

S = []
def shot(i, start, end, purpose, component, props, join=False):
    s = {"shot_id": i, "start": start, "end": end, "purpose": purpose, "visual_kind": "code", "component": component, "props": props}
    if join: s["join_prev"] = True
    S.append(s)
P = lambda t: {"at_phrase": t}
CAM_IN = {"from": {"k": 1.0, "x": 0.5, "y": 0.5}, "to": {"k": 1.1, "x": 0.5, "y": 0.5}}
CHANG = "Rutherford Chang"
TCI = "The Creative Independent, 2017"
STATEMENT = "Statement for CENTS"

# ---- 1. Chang's words about the penny (script v0.3 opens on the hoarding)
shot("s01_title", {"at_start": True}, P("I'm going to start"),
     "The web introduction's cent sign melts away and the title rises where it was. Not black at frame 0: the sign is there.",
     "IntroTitle", {"melt": "assets/" + A["melt"]["staged_as"], "titleAt": 40})
shot("s02_hoard", P("I'm going to start"), P("The penny, he said"),
     "Chang's line lit as he is quoted, over his studio desk of pennies (dimmed).",
     "IntroQuote", {"quote": {"at_phrase": "I'm going to start", "text": "I'm going to start hoarding pennies."}, "who": CHANG, "where": TCI,
                    "bg": {**img("desk"), "dim": 0.74, "from": {"k": 1.15, "x": 0.45, "y": 0.5}, "to": {"k": 1.0, "x": 0.5, "y": 0.5}}})
shot("s03_table", P("The penny, he said"), P("the lowest common"),
     "Copper cents on a table at the studio: the pennies he means.",
     "IntroPhoto", {**img("coins_table"), "label": "Copper cents at Chang's studio", **CAM_IN})
shot("s04_junk", P("the lowest common"), P("He had, he said"),
     "'Junk, nothing': many different Cents in fast succession behind the quote. The pictures differ, the words say they are worth nothing.",
     "IntroFlash", {"fronts": [front(n) for n in [9344, 2616, 1511, 4273, 6129, 189, 1328, 9526, 478]],
                    "every": 4, "who": CHANG,
                    "quote": {"at_phrase": "the lowest common", "text": "the lowest common denominator, it's like junk, it's like nothing."}}, join=True)
shot("s05_noidea", P("He had, he said"), P("What he made, CENTS"),
     "His own words against an invented intention: he did not know what he would make. Over the studio (dimmed).",
     "IntroQuote", {"quote": {"at_phrase": "no idea what", "text": "no idea"}, "who": CHANG, "where": TCI, "size": 130, "top": 700,
                    "bg": {**img("studio"), "dim": 0.76, "from": {"k": 1.0, "x": 0.5, "y": 0.5}, "to": {"k": 1.12, "x": 0.55, "y": 0.5}}})

# ---- 2. What he made: medium and network (shibboleth: lead with this point, right after the hoarding)
shot("s06_title", P("What he made, CENTS"), P("Chang inscribed images"),
     "The work named: CENTS, a work of its medium.",
     "IntroFigure", {"items": [{"at_phrase": "What he made, CENTS", "big": "CENTS", "small": "a work of its medium"}]})
shot("s07_mosaic", P("Chang inscribed images"), P("and the work shows"),
     "Images of ten thousand copper cents: all 10,000 Cents in number order, the camera pulling back from a few to all.",
     "IntroPhoto", {**img("mosaic"), "kicker": "10,000 images, inscribed on Bitcoin", "label": "Every Cent in CENTS, in number order",
                    "from": {"k": 5.0, "x": 0.5, "y": 0.5}, "to": {"k": 1.0, "x": 0.5, "y": 0.5}})
shot("s08_plaque", P("and the work shows"), P("from a state to a public"),
     "Money as the state's record: Brenner's Lincoln, the face the cent carries.",
     "IntroPhoto", {**img("plaque"), "kicker": "Victor David Brenner", "label": "Lincoln plaque. Brenner designed the Lincoln cent of 1909",
                    "from": {"k": 1.0, "x": 0.5, "y": 0.42}, "to": {"k": 1.25, "x": 0.55, "y": 0.35}})
shot("s09_network", P("from a state to a public"), P("Released at one satoshi"),
     "A drawing of the idea, not a map of real nodes: one holder of the record, then many.",
     "IntroNetwork", {"net_at": "a public network", "one": "One state",
                      "lines": [{"at_phrase": "a public network", "text": "A public network"},
                                {"at_phrase": "anyone can read", "text": "Anyone can read"},
                                {"at_phrase": "no one runs", "text": "No one runs"}]})
shot("s10_one_sat", P("Released at one satoshi"), P("the inscriptions moved"),
     "Released at one satoshi each. No dollar price.",
     "IntroFigure", {"items": [{"at_phrase": "Released at one satoshi", "big": "1 satoshi", "small": "each, at release"}]})
shot("s11_ongoing", P("the inscriptions moved"), P("set and set again"),
     "From a figure the state sets to a process.",
     "IntroFigure", {"items": [{"at_phrase": "from a figure set", "big": "1¢", "small": "a figure set by the state"},
                               {"at_phrase": "into an ongoing", "big": "ongoing", "small": "a process"}]})
shot("s12_people", P("set and set again"), P("It began with copper"),
     "The people: collectors (MAKES CENTS), a reader at UCCA, the block's image at Christie's on 'exchange'.",
     "IntroSeq", {"items": [
         {**img("mc_rees"), "label": "MAKES CENTS: David Rees"},
         {**img("mc_archivist"), "at_phrase": "set again by", "label": "MAKES CENTS: Archivist"},
         {**img("mc_olly"), "at_phrase": "the people who", "label": "MAKES CENTS: ol1y"},
         {**img("mc_sk"), "at_phrase": "who keep", "label": "MAKES CENTS: SK"},
         {**img("ucca_book"), "at_phrase": "read and exchange", "label": "Reading the CENTS book, UCCA Beijing"},
         {**img("block_christies"), "at_phrase": "and exchange each", "label": "The image of CENTS Block 839969 used at Christie's"}]})

# ---- 3. Copper and value
shot("s13_1974", P("It began with copper"), P("holds more than"),
     "Copper cents, each from before 1983: four Cents dated 1974.",
     "IntroPhoto", {**img("one_year_1974"), "fit": "contain", "label": "Four Cents dated 1974", "from": {"k": 1.0, "x": 0.5, "y": 0.5}, "to": {"k": 1.5, "x": 0.38, "y": 0.5}})
shot("s14_stamp", P("holds more than"), P("Hoarding them, he said"),
     "More copper than a cent's worth: one design, many decades of Cents.",
     "IntroPhoto", {**img("one_stamp"), "fit": "contain", "label": "One design, struck across decades", **CAM_IN}, join=True)
shot("s15_copper", P("Hoarding them, he said"), P("Chang's statement for the work"),
     "The arithmetic set large as it is said, then Chang's words lit.",
     "IntroQuote", {"quote": {"at_phrase": "buying one point seven", "text": "buying 1.7 cents of copper for one cent and it's still worth one cent.",
                              "spoken": {"1.7": "one point seven"}},
                    "who": CHANG, "where": TCI, "top": 700, "size": 74,
                    "figure": {"text": "1.7¢ for 1¢", "at_phrase": "one point seven cents", "size": 130}})
shot("s16_discrepancy", P("Chang's statement for the work"), P("He took ten thousand"),
     "The statement's own words (Chang's), over every Cent dated 1971 (dimmed).",
     "IntroQuote", {"quote": {"at_phrase": "discrepancies in value", "text": "discrepancies in value"}, "who": CHANG,
                    "where": STATEMENT, "size": 110, "top": 640,
                    "bg": {**img("struck_1971"), "dim": 0.8, "from": {"k": 1.0, "x": 0.5, "y": 0.5}, "to": {"k": 1.15, "x": 0.5, "y": 0.5}}})

# ---- 4. Ten thousand, photographed
shot("s17_rolls", P("He took ten thousand"), P("and photographed every"),
     "Out of circulation: penny rolls at the studio.",
     "IntroPhoto", {**img("rolls"), "label": "Penny rolls at Chang's studio", **CAM_IN})
shot("s18_setup", P("and photographed every"), P("Coins made to be identical"),
     "The setup in which every coin was photographed.",
     "IntroPhoto", {**img("setup"), "label": "Chang's penny photography setup", "from": {"k": 1.2, "x": 0.5, "y": 0.45}, "to": {"k": 1.0, "x": 0.5, "y": 0.5}}, join=True)
shot("s19_die", P("Coins made to be identical"), P("turned out to differ"),
     "Made to be identical: a die strikes every cent alike.",
     "IntroPhoto", {**img("die"), "label": "A die for the Lincoln cent, 2025", "kicker": "United States Mint", "from": {"k": 1.0, "x": 0.5, "y": 0.5}, "to": {"k": 1.25, "x": 0.52, "y": 0.42}})
shot("s20_1971", P("turned out to differ"), P("each marked by its"),
     "Turned out to differ: every Cent dated 1971, side by side.",
     "IntroPhoto", {**img("struck_1971"), "fit": "contain", "label": "Every Cent dated 1971 in CENTS", "from": {"k": 1.0, "x": 0.5, "y": 0.5}, "to": {"k": 1.8, "x": 0.3, "y": 0.4}}, join=True)
CENTER = [0.3, 0.3, 0.7, 0.7]
shot("s21_three", P("each marked by its"), P("He had the coins melted"),
     "Wear, toning, color, one Cent each as the word is said. Traits from the Trait Council's data (Sep 2026).",
     "IntroTriple", {"cents": [
         {"at_phrase": "each marked by its", "front": front(4336), "n": 4336, "chip": "Wear", "trait": "Heavily Abraded", "box": CENTER},
         {"at_phrase": "toning and color", "front": front(1511), "n": 1511, "chip": "Toning", "trait": "Full Obsidian", "box": CENTER},
         {"at_phrase": "and color", "front": front(4273), "n": 4273, "chip": "Color", "trait": "Full Gold", "box": CENTER}]})

# ---- 5. Melt, block, inscriptions (the melt is said before the inscriptions; ledger 03 R20)
shot("s22_pour", P("He had the coins melted"), P("cast into one block"),
     "Casting CENTS Block Copper: the outdoor pour, at its own resolution (contained, not blown up).",
     "IntroPhoto", {**img("pour"), "video": True, "fit": "contain", "kicker": "Casting CENTS Block Copper", "label": "The pour",
                    "from": {"k": 1.0, "x": 0.5, "y": 0.5}, "to": {"k": 1.0, "x": 0.5, "y": 0.5}})
shot("s23_block", P("cast into one block"), P("In March twenty twenty-four"),
     "The block itself, a photograph on a floor.",
     "IntroPhoto", {**img("block_floor"), "kicker": "CENTS Block Copper", "label": "About 31 kg, cast from the coins",
                    "from": {"k": 1.0, "x": 0.5, "y": 0.55}, "to": {"k": 1.2, "x": 0.5, "y": 0.6}}, join=True)
shot("s24_obverses", P("In March twenty twenty-four"), P("one image to one satoshi"),
     "The image of each obverse: Cents in fast succession (not the ones in the opening flash).",
     "IntroFlash", {"fronts": [front(n) for n in [1, 2, 3, 4, 5, 6, 7, 8820, 5553, 219, 4336, 1264, 9002, 6749, 8462, 1867, 10000, 1605, 3525, 9794]],
                    "every": 3, "label": "The image of each obverse"})
shot("s25_sats", P("one image to one satoshi"), P("and in April the block's"),
     "One image to one satoshi; the satoshi as the smallest unit of bitcoin.",
     "IntroFigure", {"items": [{"at_phrase": "one image to one", "big": "1 image", "small": "on 1 satoshi"},
                               {"at_phrase": "the smallest unit", "big": "100,000,000", "small": "satoshis make 1 bitcoin", "size": 120}]})
shot("s26_model", P("and in April the block's"), P("which fills a whole"),
     "The block's model, turning.",
     "IntroPhoto", {**img("model"), "video": True, "fit": "contain", "kicker": "The block's model", "label": "The 3D model of CENTS Block Copper",
                    "from": {"k": 1.0, "x": 0.5, "y": 0.5}, "to": {"k": 1.0, "x": 0.5, "y": 0.5}})
shot("s27_mempool", P("which fills a whole"), P("CENTS Block eight three"),
     "The whole block of the chain that the model fills.",
     "IntroPhoto", {**img("mempool"), "fit": "contain", "kicker": "Bitcoin block 839,969", "label": "As mempool.space shows it",
                    "from": {"k": 1.0, "x": 0.5, "y": 0.5}, "to": {"k": 1.25, "x": 0.75, "y": 0.55}})
shot("s28_839969", P("CENTS Block eight three"), P("His statement calls it"),
     "The name said over the model again (later in the clip), so CENTS Block 839969 is shown as the model, never the copper.",
     "IntroPhoto", {**img("model"), "video": True, "startFrom": 150, "fit": "contain", "kicker": "CENTS Block 839969", "label": "The block's model, inscribed on Bitcoin",
                    "from": {"k": 1.0, "x": 0.5, "y": 0.5}, "to": {"k": 1.12, "x": 0.5, "y": 0.5}})
shot("s29_monument", P("His statement calls it"), P("The coin, its image"),
     "Chang's words for the inscription, over block 839,969 as mempool.space shows it (dimmed).",
     "IntroQuote", {"quote": {"at_phrase": "an immutable digital", "text": "an immutable digital monument."}, "who": CHANG, "where": STATEMENT + ", on CENTS Block 839969",
                    "size": 96, "top": 640,
                    "bg": {**img("mempool"), "dim": 0.88, "from": {"k": 1.0, "x": 0.5, "y": 0.5}, "to": {"k": 1.15, "x": 0.5, "y": 0.5}}})

# ---- 6. Every form a cent (coin, image, inscription: kept apart, CLAUDE.md terminology)
shot("s30_forms", P("The coin, its image"), P("Collectors preferred"),
     "Five forms, one tile per word: physical coins, a Cent's image, its inscription number, the copper block, the model. Then all five.",
     "IntroForms", {"tiles": [
         {"at_phrase": "The coin, its", "label": "the coin", "src": img("coins_table")["src"]},
         {"at_phrase": "its image, its", "label": "its image", "src": front(1867), "disc": True},
         {"at_phrase": "its inscription, the", "label": "its inscription", "text": ["Inscription", "66001799"]},
         {"at_phrase": "the copper and", "label": "the copper", "src": img("block_floor")["src"]},
         {"at_phrase": "and the model each", "label": "the model", "src": img("model_still")["src"]}],
                    "all_at": "each is a cent", "chip": "Each a cent"})

# ---- 7. The collectors
shot("s31_flip", P("Collectors preferred"), P("A council of collectors"),
     "Damaged and close to mint state, swapping fast (brief: comparisons cut back and forth), settling on the damaged one.",
     "StoryFlip", {"a": {"n": 9344, "inscription": 65999011, "front": front(9344), "chip": "Nine traits"},
                   "b": {"n": 4421, "inscription": 65998434, "front": front(4421), "chip": "Close to mint state"},
                   "period": 0.3, "settle": "to the clean", "chips_at": "Collectors preferred"})
shot("s32_council", P("A council of collectors"), P("voted on all ten"),
     "The Trait Council's own process document.",
     "IntroPhoto", {**img("trait_council"), "fit": "contain", "label": "The Trait Council's process", **CAM_IN})
shot("s33_rounds", P("voted on all ten"), P("and agreed on nineteen"),
     "All ten thousand, three times.",
     "IntroFigure", {"items": [{"at_phrase": "voted on all ten", "big": "10,000", "small": "Cents reviewed", "size": 150},
                               {"at_phrase": "three times", "big": "×3", "small": "three rounds of votes"}]}, join=True)
shot("s34_traits", P("and agreed on nineteen"), P("Chang's statement ends"),
     "The nineteen traits (still from the web introduction).",
     "IntroPhoto", {**img("traits19"), "fit": "contain", "label": "The nineteen traits", "from": {"k": 1.0, "x": 0.5, "y": 0.5}, "to": {"k": 1.6, "x": 0.6, "y": 0.45}})

# ---- 8. The statement's last words; no ending
shot("s35_shown", P("Chang's statement ends"), P("its value can continue"),
     "Where the work has been shown, while the statement is introduced.",
     "IntroSeq", {"items": [
         {**img("ucca_case"), "label": "UCCA Beijing: the block, the book, the model"},
         {**img("bankable"), "fit": "contain", "at_phrase": "statement ends", "plus": 0.5, "label": "BANKABLE, Basel Social Club, 2025"}]})
shot("s36_redefined", P("its value can continue"), {"after_phrase": "their transformation.", "plus": 1.2},
     "The statement's last sentence lit over all 10,000 Cents, the camera pulling back from a few to all. The film ends on 'continue to be redefined', not on an ending.",
     "IntroQuote", {"quote": {"at_phrase": "its value can continue",
                              "text": "its value can continue to be redefined through this digitally scarce set of 10,000 and the block that encapsulates their transformation.",
                              "spoken": {"10,000": "ten thousand"}},
                    "who": CHANG, "where": STATEMENT, "size": 66, "maxLines": 10, "top": 520,
                    "bg": {**img("mosaic"), "dim": 0.72, "from": {"k": 4.0, "x": 0.5, "y": 0.5}, "to": {"k": 1.0, "x": 0.5, "y": 0.5}}})
END = "their transformation."
shot("s37_end", {"after_phrase": END, "plus": 1.2}, {"after_phrase": END, "plus": 4.4}, "End card.",
     "IntroEnd", {"sites": ["cents.gallery", "cents.vision"]})
shot("s38_credits", {"after_phrase": END, "plus": 4.4}, {"at_end": True}, "Credits.",
     "Credits", {"lines": ["Words: Rutherford Chang, The Creative Independent, 2017, and his statement for CENTS",
                           "Images: Rutherford Chang; cents.gallery media library",
                           "UCCA Beijing installation views; MAKES CENTS",
                           "mempool.space · Princeton University Art Museum · U.S. Mint (public domain)"],
                 "url": "cents.gallery"})

tl = {"essay": {"title": "CENTS", "subtitle": "An introduction", "author": "shibboleth",
                "source": "/mnt/project-files/intro-videos/intro-2min/intro_proposal_v0.3.md",
                "version": "v0.3 rehearsal (2026-11-27): script v0.3, awaiting shibboleth's review"},
      "_what": "The CENTS introduction (about 2:12): Chang's hoarding, then medium and network (shibboleth: lead with it), copper and value, ten thousand photographed, the melt and the inscriptions, every form a cent, the collectors, the statement's 'continue to be redefined'. A new picture about every 2-3 s.",
      "shots": S}
json.dump(tl, open(F / "timeline/timeline.json", "w"), indent=1, ensure_ascii=False)
print(len(S), "shots")
