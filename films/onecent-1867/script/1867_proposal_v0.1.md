# One Cent #1867: proposal v0.1 (script for review, not voiced)

2026-11-25. Thread "Make the Cent #1867 video". Nothing is recorded yet. The zoom plan is `1867_zoom_plan_v0.1.jpg` beside this file.

## 1. The Cent, measured

From the Sep 2026 trait export (`films/onecent-1867/script/counts.py` in cents-video; floors: verdigris 1,884 and 436 unique profiles both reproduced; a planted copy of #1867's profile on another Cent makes the uniqueness check fail).

| Fact | Value |
|---|---|
| Date, mint mark | 1964, none (unique ID 1964 093) |
| Inscription | 66001799 |
| Traits | Significant Obsidian, Significant Verdigris, Contaminated: Alien Secretion |
| Significant Obsidian | 220 Cents |
| Significant Verdigris | 376 |
| Both at Significant | 29 |
| Alien Secretion | 79, of which 70 also carry verdigris (any grade); verdigris is on 1,884 of 10,000 overall |
| Same whole trait profile | none: a trait profile no other Cent shares (not a cents.vision 1/1 Trait Combo, so never "1/1") |
| Closest | #2583 (1976) has all three plus Notable Abraded |
| 1964 Cents | 356 (244 no mark, 112 D): the year is common, so the traits lead (rarest first) |
| Template | #4421, 1964, no mark, Lustrous only (the other candidate, #4674, is duller) |

**"Dated 1964", not "struck in 1964".** The series wording is "a penny struck in <year>". Collector sources say the Mint went on striking 1964-dated cents through 1965, and that San Francisco struck some without a mint mark from September 1965 ([NGC, "The US Mint Coins Dated 1964", part 2](https://www.ngccoin.com/news/article/7777/USA-Coin-Album/)). So "dated" is the safe word for this year, and "generally indicating the Philadelphia mint" still holds. Not checked against a primary Mint record.

## 2. Concept and quotes

- **Primary concept: C20 "Circulation leaves traces"** (time family). Not used by any earlier episode. Its "show" note fits this Cent exactly: "residue that only use could leave".
- **The episode's spine is the Atlas's own distinction:** a patina "arises from internal chemistry", contamination is "matter imposed upon copper". #1867 carries both kinds of trace.
- **Value tie, from the presentation work (shibboleth, 2026-11-25: a guiding source for this and future videos).** Two lines of the art text v0.5.1 carry it: "As money, any cent was as good as any other. As a Cent, none is." and Kruger's line as Myers quotes it, with "A circulated copper cent is the exception". The close says the value move as the act's effect, in the art text's words ("from a figure set by the state into an ongoing process"), never as Chang's purpose.
- **Art-literature quote (brief §3, contemporary first):** QUOTE_BANK H25, Barbara Kruger as quoted by Rhea Myers, *Proof of Work* (2022). About CENTS: no. It is framed as a claim about money, and our line names the exception.
- **Concept quote:** Emily Watlington, "After His Untimely Death, Rutherford Chang's Survey Rewrites What a Square Can Do", *Art in America*, 1 May 2026. About Chang's work as a whole (her example is *We Buy White Albums*), so it is introduced as "writing on Rutherford Chang", never as a CENTS motive. **A press piece: brief §4 asks the user before building an episode around one.** It is short, one card.

| Quote or Atlas line | Check | Result | Control |
|---|---|---|---|
| Watlington: "Circulation is another of Chang’s key themes: how do things change as they move through the world?" | check_quotes.py | FOUND, aia_rutherford-chang-ucca-review_2026-05-01.txt | "main" for "key": MISSING |
| Kruger via Myers: "Money is an information-destroying medium" | check_quotes.py | FOUND, library-read excerpts | "preserving": MISSING |
| Atlas (obsidian.txt, verdigris.txt): "a major visual actor", "not yet fully dominant" | grep -F (the Atlas is not in the checker's corpus) | FOUND in both pages | "a minor visual actor": MISSING |
| Atlas (contaminated.txt): "arises from internal chemistry", "matter imposed upon copper", "Unidentifiable translucent or greenish films", "The subtrait names are therefore not claims of chemistry, but field names – tools for seeing." | grep -F | FOUND | "external chemistry", "upon metal", "opaque", "are therefore claims": all MISSING |

The card keeps the Atlas's dash ("field names – tools for seeing"); the voice reads it as a pause. "Unidentifiable" is lower case mid-sentence on the card.

## 3. Script v0.1

About **355 spoken words** (numbers spelled out): about 2:02 to 2:22 of narration at eee's 2.5 to 2.9 words a second, so about **2:20 to 2:40** with the spin, the closing turn and the credits. Under 3:00; longer than #8820 (2:02), close to #10000 (2:26). Cuts offered in §6.

1. Cent #1867. A penny dated 1964, with no mint mark, generally indicating the Philadelphia mint.
2. Three traits mark its obverse: two patinas and a contamination.
3. A dark band of Significant Obsidian crosses the upper left, over the motto and Lincoln's head.
4. Green patches of Significant Verdigris gather on his cheek, behind his head and at his collar.
5. In the Traits Atlas, Significant means "a major visual actor", but "not yet fully dominant".
6. 220 Cents carry Significant Obsidian, and 376 Significant Verdigris. 29 carry both.
7. Both patinas grew from the copper. In the Atlas, a patina "arises from internal chemistry".
8. The third trait came from outside: Contaminated, Alien Secretion. In the Atlas, contamination is "matter imposed upon copper", and Alien Secretion names "unidentifiable translucent or greenish films".
9. The Trait Council names such residues by reading the surface, without testing it. In the Atlas's words: "The subtrait names are therefore not claims of chemistry, but field names – tools for seeing."
10. 79 Cents carry Alien Secretion, and 70 of them carry verdigris too.
11. No other Cent has exactly this set of traits.
12. Cent #4421 is dated the same year, and is close to mint state. Its portrait is clean and bright.
13. As money, any cent was as good as any other. As a Cent, none is.
14. Circulation leaves traces. *(concept card)*
15. In the words of Emily Watlington, writing on Rutherford Chang in *Art in America*: "Circulation is another of Chang's key themes: how do things change as they move through the world?" *(quote card)*
16. Rhea Myers, in her book *Proof of Work*, quotes the artist Barbara Kruger: "Money is an information-destroying medium." *(quote card)*
17. A circulated copper cent is the exception. On Cent #1867, two patinas and a film record where the coin has been.
18. In March 2024, Chang inscribed its image on a satoshi, and the physical coin was melted into CENTS Block Copper.
19. Released at one satoshi, the Cent's value moved from a figure set by the state into an ongoing process, set again each time someone reads it, keeps it or lets it go.
20. Cent #1867, a great Cent. *(closing spin card, one turn)*

## 4. How it reads in order (video-concept-relations passes)

**Referents.** Line 9's quoted "therefore" needs its premise in the film. The Atlas's premise is "We don’t scrape, dissolve, or assay; we study photographs…"; line 9's first sentence supplies it ("by reading the surface, without testing it"). Line 15 is the first mention of Chang, so the attribution names him in full. Line 17's "a film" points back to line 8's "greenish films". Line 12 gives #4421 its own subject and "Its portrait", so nothing can be heard as #1867's (#10000 lesson).

**Order.**
- Lines 7 and 8 make the spine: from the copper, then from outside. Both halves are the Atlas's words.
- Line 10 after line 9: "seventy of them carry verdigris too" right after "not claims of chemistry" could be heard as "perhaps Alien Secretion is verdigris". It states a count and no cause, and the Atlas itself says substances on copper "age toward the same visual end". I moved the count after the names line to soften it. **Yours to judge as a Council member:** keep it, or cut it (saves 12 words).
- Line 15 after line 13: a quote about Chang's themes right after a fact about Cents can read as his reason for the fact (#9344 lesson). The concept card sits between them, the attribution says "writing on Rutherford Chang", and the quote is about his work in general, so I judged it safe.
- Lines 16 and 17: question (Watlington), general claim (Kruger), exception (this cent). Each answers the one before.
- Line 18 says Chang's acts in the active voice ("Chang inscribed") and gives the melt as fact, as the art text does. Nothing joins the inscription to a purpose.

**Shape.** Opens on the coin; reads its surface (inside, outside); sets it beside a coin with no traces; names the concept; says what money forgets and this cent kept; ends on value set again and again. Chang's acts are a hinge, not the end. No death, no discontinuation. The last idea before the name is a process that goes on.

**Repetition.** "Atlas" four times, each a different claim (grade, patina, contamination, names). "Record" once.

**Superlatives.** "No other Cent has exactly this set of traits": counted (§1), with a control. "29", "79", "70": counted.

**Not used, from the art text:** "a grade rewards an object for how little has happened to it; the traits of CENTS value what happened to each coin". With #4421 on screen it would be contradicted: #4421's one trait, Lustrous, rewards what survived ("a form of preservation within decay", Atlas), and Striated records the striking itself. The art text's line is too broad as written; worth a word to the presentation work. A corrected version could go after line 13 if you want it: "A coin grade rewards how little has happened to a coin. Lustrous names what survived; most of the nineteen traits name what happened."

## 5. Pictures (about 25 shots, 15 or more distinct plates)

| Line | Picture | Together they say | Source |
|---|---|---|---|
| 1 | 3DCENTS turn, title card "Cent #1867", "Inscription 66001799", Story time pill; then zoom to 1964, then where a mint mark would be | This is the Cent; its date; no mark | 3DCENTS export (running now in the container); 1050 px obverse |
| 2–4 | Zoom O (band), zoom V (patches, two areas, ringed) | These are the two patinas | `1867_zoom_plan_v0.1.jpg` |
| 5 | Traits Atlas text plate, the Significant line lit | The grade's meaning is the Council's | cents.gallery Traits Lab |
| 6 | Quick CentScrolls of the 220 and the 376 (8 across), then the 29 with #1867 in spotlight | These Cents carry these grades | 300 px images |
| 7 | Whole coin, no rings | Both patinas on one face | obverse |
| 8 | Zoom A (the film, ringed); then the Atlas's two Alien Secretion examples, #7459 and #8556, cut out on black | This is Alien Secretion | obverse; cents.vision fronts |
| 9 | Atlas text plate, "How we name what we can't test", the field-names sentence lit | The Council's own account | cents.gallery Traits Lab |
| 10 | CentScroll of the 79 at 6 across, #1867 last, in spotlight | These Cents carry it | 300 px images |
| 11 | TraitTally, the three traits lit | This set is #1867's alone | component |
| 12 | CentDissolve #1867 ↔ #4421 | The same year, with and without traces | 1050 px obverses |
| 13 | Whitman folder of Lincoln cents 1941–1974 at "as good as any other", back to #1867 at "none is" | Interchangeable as money, not as Cents | CC0 (Monocletophat123), used in the web intro |
| 14 | Concept card CIRCULATION LEAVES TRACES over the dimmed coin | | |
| 15 | UCCA photo at the attribution (captioned with the place only), then the lit quote card | Watlington wrote on the work shown here | media library, "Courtesy UCCA Center for Contemporary Art" |
| 16 | Lit quote card over the dimmed coin | | |
| 17 | Slow push from the band to the film | The record on this coin | obverse |
| 18 | The 300 px on-chain image at native size, "Inscription 66001799"; the pour "Casting CENTS Block Copper"; CENTS Block Copper | The image is the inscription; the coin went into this block | inscription content; media library / objecthood a14 |
| 19 | Ledger plate: the dated transfers of #1867's satoshi, no amounts | It keeps changing hands | mempool.space trace (as #8820) |
| 20 | Closing card, one 3DCENTS turn | | |

## 6. Open, for shibboleth

1. **The Alien Secretion area.** I read it as the thin ochre film over the cheek and ear, with the green crusts as the verdigris (box A? on the zoom plan). If it is the other way round, or somewhere else, please say or circle it; the zoom boxes follow your reading.
2. **The press quote** (Watlington, *Art in America*): OK to build on it, per brief §4?
3. **Line 10** (70 of the 79 also carry verdigris): keep or cut?
4. **Length** (~2:20 to 2:40). If shorter is better, the cuts in order of least loss: line 10 (12 words), the separate pool counts in line 6 (keep only "29 Cents carry both at Significant", 10 words), line 16's book title (4 words).

## Revision log

- v0.1, 2026-11-25: first script, C20 with the art text v0.5.1 as a guiding source (shibboleth, same day).
