# One Cent #10000: proposal v0.1 (script for review, not voiced)

2026-11-21. Thread "Make the Cent #10000 video with Remotion". This episode is also a trial of the
`remotion-video-builder` skill (NulightJens/jensai-skills, commit 8598b58). The skill's Step 2 says
"present the script with beat labels and estimated timing per section" and "get user approval
before proceeding. The script is the contract." That is this file. Nothing is recorded yet.

The style guide the skill builds from is `STYLE-GUIDE.md` beside this file (also
`films/onecent-10000/STYLE-GUIDE.md` in cents-video). It restates our house rules in the skill's
categories and lists where the skill's defaults were overridden.

## 1. The Cent

| | Value | Source |
|---|---|---|
| Number | #10000. Cents are numbered 1 to 10000 with no gaps, so its number is also the count | Sep 2026 export; `counts.py` asserts it |
| Year, mint | 1976, no mint mark (Philadelphia) | export; read on the front |
| Inscription | 65987682 | export |
| Traits | Assassin and Notable Verdigris, nothing else | export |
| Assassin | 42 Cents. Rarer than Notable Verdigris (1,493), so it goes first (rarest first, §5) | `counts.py`, floor Assassin = 42 seen red on a copy with one flag removed |
| 1976 Assassins | two: #1413 and #10000 | `counts.py` |
| Exactly this pair | 11 Cents (not used in the script) | `counts.py` |
| 1976, no mark | 499 of 556 Cents of 1976, so the year is not the rare quality | `counts.py` |
| Template | #1256, 1976, no mark, Lustrous only. 15 such Cents; any can stand in | `counts.py`; contact sheet looked at |

## 2. Concept and quotes

- **Primary concept: C22 "An open signifier"** (sign family). Not used by an earlier episode.
- **Value tie:** carried inside the C22 quote itself. Reiss's sentence just before "open signifier"
  is "Their former economic meaning is unhooked from the object and turned into a vessel for
  socially agreed value." No second concept card.
- **Trait origin (C50, no card):** Reiss names Assassin among the traits the community invented,
  which states the trait's origin (the community, then the Trait Council) before its description,
  so nothing reads as Chang's choice.
- **Art literature (brief §3, rule of 2026-11-14):** QUOTE_BANK v0.7 **D37**, Lippard and Chandler,
  "The Dematerialization of Art" (1968), p. 273, from the bank's v0.7 finder "looks and meaning (for
  the traits)". About CENTS? **No**, so the voice says "long before CENTS". The bank's use note is
  ours too: "what a Cent looks like is not what CENTS is about."

Every card and Atlas line, checked on 2026-11-21 on the exact text that would go on screen:

| Text | Check | Result | Control (one word changed) |
|---|---|---|---|
| Reiss: "The community therefore began naming the spontaneous variations. Traits like 'Ghost', 'Faceless', or 'Assassin' were born." | check_quotes.py | FOUND, reiss__materiality-and-signification.md | "made" for "born": MISSING |
| Reiss: "Their former economic meaning is unhooked from the object and turned into a vessel for socially agreed value. The penny becomes an open signifier that can point to many signifieds - artistic, collector, historical, crypto." (adjacent sentences; 34 words, so two cards) | check_quotes.py | FOUND, same file | "worth" for "value": MISSING |
| Lippard and Chandler: "What something looks like and what it is about may be complementary but not necessarily (rarely) identical." | check_quotes.py | FOUND, lippard-chandler excerpts | "always" for "necessarily": MISSING |
| Atlas, Assassin: "Prominent spherical obsidian, verdigris or contamination striking Abe’s head, neck, or torso – the mark of an imagined projectile." | grep -F in `films/traits/script/atlas/` | 1 file | "bullet" for "projectile": 0 files |
| Atlas, Assassin: "singular placement transforms decay into narrative" | grep -F | 1 file | "turns": 0 files |
| Atlas, Verdigris: "Localised but clearly visible patches or films" | grep -F | 1 file | "flecks": 0 files |

## 3. Script v0.1, with the picture under each line

About **316 spoken words** (numbers spelled out): about 1:49 to 2:06 of narration at eee's
2.5 to 2.9 words a second, so about **2:05 to 2:25** with the spin, the closing turn and the
credits. Under 3:00, but past 2:00, so §6 lists cuts.

| # | Beat | Line (as captioned) | Picture | Est. start |
|---|---|---|---|---|
| 1 | Title | Cent #10000. Its number is also how many Cents there are in all. | Title card over the 3DCENTS turn, "Inscription #65987682", Story time pill | 0:00 |
| 2 | Look | A penny struck in 1976 with no mint mark, generally indicating the Philadelphia mint. | Hold the front; zoom to the date, then to where a mint mark would sit | 0:06 |
| 3 | Traits | Cent #10000 carries two traits, and the rarer is Assassin. | Whole front, push to the spot, readout "Assassin" | 0:12 |
| 4 | Traits | The Cents came with no traits, only a year and a mint mark. In the words of Steven Reiss, in his article "Materiality and Signification": "The community therefore began naming the spontaneous variations. Traits like 'Ghost', 'Faceless', or 'Assassin' were born." | The 300 px on-chain image of #10000 at native size with "1976 · no mint mark"; then the lit quote card over the dimmed coin | 0:17 |
| 5 | Traits | In the Traits Atlas, Assassin is "prominent spherical obsidian, verdigris or contamination striking Abe's head, neck, or torso – the mark of an imagined projectile." | The Atlas's Assassin entry (cents.vision, shot like #8820's), then the Atlas's own examples at "head, neck, or torso": #1894 headshot, #2755 neck shot, #6595 bodyshot | 0:32 |
| 6 | Traits | Here it is a single green spot at the back of Lincoln's neck. | Back to #10000, ringed zoom on spot A | 0:41 |
| 7 | Pool | 42 Cents carry Assassin. Two of them were struck in 1976. | CentScroll of all 42, #10000 last with the spotlight; then #1413 and #10000 side by side | 0:46 |
| 8 | Traits | The second trait is Notable Verdigris: in the Atlas, "localised but clearly visible patches or films". On Cent #10000, the spot itself is verdigris. *(second sentence waits on your answer, §7 Q1)* | Zooms to the verdigris areas you confirm | 0:51 |
| 9 | Template | Beside Cent #1256, struck the same year and close to mint state, the portrait is unmarked. As money, both meant exactly one cent. | CentDissolve #10000 ↔ #1256 | 1:01 |
| 10 | Concept | An open signifier. | Concept card AN OPEN SIGNIFIER, coin dimmed | 1:10 |
| 11 | Quote | Steven Reiss again: "Their former economic meaning is unhooked from the object and turned into a vessel for socially agreed value. The penny becomes an open signifier that can point to many signifieds - artistic, collector, historical, crypto." | Two lit quote cards; zoom on the attribution, pull back as the card lights (#9344 lesson) | 1:12 |
| 12 | Widen | The portrait is Abraham Lincoln, assassinated in 1865. In the Atlas, the Assassin's "singular placement transforms decay into narrative". | Brenner's Lincoln plaque (media library C047, native size); then #10000's spot again | 1:26 |
| 13 | Lens | In 1968, long before CENTS, Lucy Lippard and John Chandler wrote, in their essay "The Dematerialization of Art": "What something looks like and what it is about may be complementary but not necessarily (rarely) identical." | Lit quote card over the 10,000-Cent mosaic (media library C001), slow push | 1:34 |
| 14 | Value | To look at, Cent #10000 is a 1976 penny with one green spot. What it means, and what it is worth, the people who collect CENTS keep deciding. | Whole front of #10000; then the MAKES CENTS collector-interview covers (C048) at "the people who collect CENTS" | 1:47 |
| 15 | Close | Cent #10000, a great Cent. | Opening card, one 3DCENTS turn, then credits | 1:59 |

Shots: about 18, longest planned hold the Reiss cards (about 14 s), media library plates 3
(C047, C001, C048) plus the Atlas page, three Atlas example Cents, the pool, the template and the
on-chain image.

Spoken forms: "Cent number ten thousand"; "Steven Rice" (Reiss); "not necessarily, rarely,
identical" for the card's "(rarely)"; the en dash in the Atlas line is voiced as a comma.

## 4. How it reads in order (video-concept-relations passes)

**Referents.** Line 4's quoted "therefore" points back to "The Cents came with no traits", which the
line supplies first. "Steven Reiss again" (11) points to line 4. "The second trait" (8) avoids
"its" after the pool line, where "its" could mean the pool. Line 12's "the Assassin's" names its
referent, six lines after line 6.

**Order, the risk I checked.** In a first draft, "its number is also how many Cents there are" sat
directly before "the rarer is Assassin". Heard together, the highest number and an assassin could
read as a planned, dramatic finale, which invents a design (and an ending) nobody made. Now the
year and mint line sits between them, and nothing calls #10000 "last". Line 4 states the trait's
origin (the community) before line 5 describes it, so no property reads as a reason.

**Lincoln (line 12).** Put after Reiss's "historical", the line offers one historical reading of the
spot, and the Atlas line says the reading is the Council's ("transforms decay into narrative"). It
does not say why the Council chose the name; the order lets the viewer connect them. You sit on the
Trait Council, so §7 Q2 asks whether that connection is fair.

**Pictures with words.** "The portrait is Abraham Lincoln" over Brenner's plaque says: this relief is
the penny's Lincoln. True. "The people who collect CENTS" over the MAKES CENTS covers says: these are
collectors. True (collector interviews). I avoided UCCA visitors there, since visitors are not
collectors. The Lippard and Chandler card over the mosaic adds no claim.

**Shape.** Opens on the number, ends on people who "keep deciding" what the Cent means and is worth,
then the held card. That enacts "no ending". Line 14 is the risk: it could be heard as a closing
moral. It states an ongoing process, not a conclusion, which is how #8820 ended ("the ledger records
each transfer"). If it reads as a moral to you, §6 option B ends on the Lippard and Chandler card.

**Superlatives.** "The rarer" (42 against 1,493) and "two of them" are counted. No "only", "first"
or "last".

## 5. What I need from the picture side

- **3DCENTS turn for #10000.** The opening and closing need `cent-10000-360-1080x1920-25fps-reel`
  from "cents shortlist". Your Mac wasn't reachable from this thread when I looked. If the export
  isn't there yet, it needs making on 3DCENTS.
- Everything else is in reach: cents.vision fronts (fetched), the media library (catalogue fetched).
  The R2 bucket's public r2.dev address is blocked here, but the 1050 px fronts cover what R2 would
  give, so I'm not asking to open it.

## 6. Length options (pick any, or none)

- A. Cut "Two of them were struck in 1976." (−8 words, about 3 s).
- B. Cut line 14 and end on the Lippard and Chandler card before the closing card (−31 words,
  about 11 s). Value then rests on Reiss's "socially agreed value" alone.
- C. Cut the Atlas line in 12 and keep only "The portrait is Abraham Lincoln, assassinated in 1865."
  (−11 words).

## 7. Questions

1. **Which areas are Notable Verdigris?** See `10000_zoom_plan_v0.1.jpg`. The colour test finds green
   only in spot A (74 px), the Assassin spot itself. B, C and D are faint grey spots; D, below the
   "6", looks grey-green to me, which the reading guide says counts. Tell me which count, or pin
   others. Line 8's second sentence follows your answer.
2. **Lincoln line.** Is it fair to set "assassinated in 1865" beside the Atlas's "transforms decay
   into narrative", as one reading of the Council's name?
3. **The number line** ("Its number is also how many Cents there are in all"). Keep, or drop it and
   open straight on the year?

## Options not taken

- Steven Reiss on the White Album's serial number (Bitcoin Magazine, 2026): "it frames each copy as one
  among many … while simultaneously gesturing toward something like limited edition status through
  the very act of numbering." Tempting for a Cent numbered 10000, but it is about another of Chang's
  works, and a third author would push the film well past 2:00.
- 1976 as the US Bicentennial: the cent's design did not change for it, so it says nothing about this
  coin.

## Revision log

- v0.1, 2026-11-21: first draft for review.
