# CENTS — a three-minute introduction

**Live treatment.** Script below is current and recordable: **24 lines, 357
words, ≈3:12** at the 114 wpm measured from your existing recordings.

Superseded reasoning is kept verbatim at
[`archive/cents_introduction_3min_2026-10-08_superseded.md`](archive/cents_introduction_3min_2026-10-08_superseded.md).
Where the archive disagrees with this file, **this file is right**.

Sources: the corpus at sovrn.art/cents (18 essays, 24 collector interviews, 12
press pieces, 2 books), the project description, the UCCA page, the Block page,
Tinari's Taschen text, the NYT obituary, the artist's own exhibition list, and
the CENTS catalogue measured directly.

---

## 1. The script

**I — THREE PRICES, ONE OBJECT**
1. After a century in circulation, the penny is considered a worthless nuisance.
2. The Treasury says it is worth exactly one cent, and always will be, whatever year it was struck.
3. Those made before 1983 are copper, and in 2024 that copper was worth about three cents.
4. Three valuations of the same small object, and none of them agree.
5. Recognising those discrepancies, Rutherford Chang removed ten thousand copper cents from circulation and called the work CENTS.

**II — THE ARTIST**
6. He had spent his working life collecting ordinary things until time made them singular.
7. More than three and a half thousand copies of the same Beatles record, no two worn alike.
8. Shown for two decades, from the ICA in London to the Art Gallery of Ontario.
9. He died in February 2025, at forty-five, on the day the President ordered the Treasury to stop making pennies.

**III — WHAT A CENTURY HAD DONE TO THEM**
10. Every one of the ten thousand was photographed first.
11. The portrait on them, Victor David Brenner's Lincoln, is the most reproduced artwork on Earth. Two hundred and eighty-eight billion still in existence.
12. Circulation made the marks: verdigris, abrasion, a fingerprint, the way each one left.
13. No algorithm assigned any of it. The names came afterwards, from the collectors, over two years of voting.
14. More than half the set carries no mark at all, which is what makes the rest mean anything.

**IV — THE TRANSFORMATION**
15. Then he destroyed them, smelted into one block of thirty-one kilograms.
16. Each photograph he inscribed on a satoshi, the smallest unit of Bitcoin.
17. The block he had scanned, and inscribed as the whole of Bitcoin block 839969.
18. An ingot so dense it cannot be destroyed.
19. He released all ten thousand at one sat each.

**V — WHAT IT IS DOING**
20. The set is closed. It stops at 1982, because in 1983 the penny stopped being copper.
21. Only one of the years it misses means anything. In 1943 the copper went to the war, and the cent was struck in steel.
22. A set with edges nobody chose.
23. The last penny was struck in November 2025, which the project had described as coming.
24. As the coin fades, its value goes on being redefined, through ten thousand objects and the block that holds their transformation.

---

## 2. The shape, and why

| | movement | time | does |
|---|---|---|---|
| I | **Three prices, one object** | 0:00–0:38 | a nuisance, exactly 1¢ by decree, three cents of copper — and none agree |
| II | **The artist** | 0:38–1:09 | two decades of collecting until time makes things singular |
| III | **What a century had done to them** | 1:09–1:52 | the portrait, the marks, who named them, and how ordinary most are |
| IV | **The transformation** | 1:52–2:25 | destroy, inscribe, release |
| V | **What it is doing** | 2:25–3:11 | edges nobody chose; the coin ends, the revaluation doesn't |

**The spine is the work's own.** Its project description opens on three
valuations that disagree — *"considered a worthless nuisance… **yet** worth
exactly 1¢… **furthermore** a metal value of approximately 3.1¢… **recognizing
these discrepancies**, Rutherford Chang removed 10,000"* — and closes on *"as
the traditional penny fades into irrelevance and its production is ultimately
terminated, its value can continue to be redefined."* Written March 2024, a
year before the penny's end was ordered. The film opens and closes where the
work does.

**The film does not end.** CENTS is a becoming — a set whose form is fixed and
whose meaning is not — so closing on the artist's death and the penny's
discontinuation would frame as finished the one work whose claim is that it is
open. Both facts are true, sourced, and stay; they belong to the **object** and
the **artist**, in movements I and II. Their coincidence — the order to stop
minting and the obituary on the same day — is stronger as the hinge between
those two movements than as a terminus. Movement V is in the present continuous
and stays there.

**Movement IV rests on two measured facts, not on exotic patina.** More than
half the set carries no catalogued trait at all, which is what makes the rest
mean anything; and the collection's edges were set by metallurgy and a war.
Both are in §4.

---

## 3. Imagery

No generation and no API spend: every frame is an asset already on this
machine. From `~/Pictures/cents shortlist` (249 files) and the staged
inventory.

| movement | material |
|---|---|
| I | `most reproduced images.jpg` · a06 Brenner plaque · a01 cent · the penny's end as dated record |
| II | White Albums material · `Rutherford's desk with cents` (the sort in progress) · a15/a16 desk views |
| III | photo setup (a17) → `copper pour cube pour.mov` → `cents to cube.mp4` → `BLOCK loop.mp4` |
| IV | `patina sets diagram.png` · `cents traits final.png` · the year histogram, drawn from the CSV · the 1943 gap |
| V | a13 market band · UCCA installation stills · `Block copper still.png` |

**The one thing worth building:** a mosaic of all 10,000 real cent images.
Unlike the existing `10K all heads` print file, a built one can zoom and
resolve to single coins — movement IV's argument in a single move. The images
are **already on this disk** at `/Users/moobook/sovrn-onchain/cents/` (10,000
WebP, 1–10000, no gaps, plus `index.json`), so this costs nothing and needs no
network. At native 300px it is a 30,000×30,000 canvas; decode in one process.

Before either the mosaic or the histogram ships, run `derived-not-decorated`:
perturb the source and confirm the output moves. The 1964 spike (356 against
neighbours near 120) is the specific thing a hand-drawn curve would smooth away.

---

## 4. Figures, measured against the catalogue

Measured by the CENTS bot from `metadata.json`, and spot-verified here against
its CSV (73 rows, sum 10,000, 15 zero-count years, exactly one ANOMALOUS).

**Used:** 10,000 records, contiguous, no duplicates · years 1910–1982, 58
distinct · mint marks 8,343 none / 1,597 D / **60 S** · 19 traits in five
families · 50.20% struck before 1976, 25.79% in 1980–82, 2.91% before 1960
(true, but 0.09pp from false — give the number rather than "under 3%").

**The two facts movement IV is built on:**

1. **53.06% of cents carry no catalogued trait at all.** Introductions lead
   with exotic patina and imply a typical CENT is a riot of colour. It is not,
   and saying so beats the montage: a population where half the objects are
   unremarkable is what makes the remarkable ones mean something.
2. **The edges were set by metallurgy and a war.** 867 cents dated 1982 and
   *zero* later — the ceiling **is** the copper-to-zinc cutoff. And 1943 is
   missing entirely (1942 has 2, 1944 has 22), because that year the cent was
   struck in zinc-coated steel to save copper. **Fifteen years are absent and
   only 1943's means anything**: P(zero by chance) = 2.75 × 10⁻⁵ against a
   local mean of 10.5, where the 1913–1933 gaps run 0.37–0.85 and are simply
   small numbers — 1910–1939 holds 26 cents across 30 years, where you would
   expect 12.4 empty years and there are 14.

**Not used, and why:**

- *The Readymade of Loss* (25 cents in large exchange outputs) — unverifiable
  from anything held locally; no UTXO or custodian fields exist and exchange
  attribution is a third-party heuristic. Would have to be attributed to
  Lehnen, not asserted. Also 362 cents are dated 1971, so "a matched pair of
  1971s" is not constrained by rarity.
- *1/1 by trait combination (38)* — not derivable from the metadata; cite
  cents.vision, never a calculation.
- *Per-cent curation membership* (Genesis Day 110, Taschen 99) — counts sound,
  membership transcribed by eye from screenshots. Never name a specific cent.
- *A dated melt value* — line 4 uses the durable form, "has long been worth
  more", because any figure needs a date attached or it goes wrong after
  release and the film cannot know.
- *1971 and the Nixon footage* — a good interpretive overlay, but 1943 is
  intrinsic, measured, and almost never said. At 349 words the intrinsic one
  wins. The footage stays available.

**Time-varying facts carry an epoch, chosen for what the claim does.** Several
figures moved across the writings, so "most recent" and "most relevant" are not
always the same answer:

| fact | values, with dates | used, and why |
|---|---|---|
| melt value of a copper cent | **3.1¢** (project description, Mar 2024) · **2.5¢** (essay, Oct 2025) | **3.1¢, dated "in 2024"** — the epoch that matters is when the work was made, not when a later writer wrote. The source frames it the same way: *"will **always** be worth exactly 1¢ … **now** have a metal value of approximately 3.1¢"*, a decree against a market. Line 2 carries "always", line 3 carries the date. |
| *We Buy White Albums* copies | **3,400+** (NYT obituary, Feb 2025) · **3,555** (UCCA materials list, 2026) | **the current one.** The collection grew until he died and 3,555 is what was exhibited; the script says "more than three and a half thousand", true against 3,555 and not against the superseded figure. |
| Lincolns in existence | **288 billion** (project description, Mar 2024) | that figure, with **"still in existence"** said aloud so the population is named rather than implied. |

*Failure-shape: a figure without an epoch is not a fact, it is a snapshot
presented as one.* It will be wrong at some point after release and the film
will not know. Either date it or use a form that stays true — line 3 is dated
because the exact number carries the argument; the earlier film's melt value
used the durable form instead.

**288 billion vs 500+ billion** are different populations — surviving today
versus struck since 1909. Line 2 says **"still in existence"** and names which.

---

## 5. Sourcing, with the legs named

A URL slug is not confirmation: if the date comes from the slug, the date and
the source are one artifact doing both jobs.

- **Penny order, 9 Feb 2025** — independent press, retrieved this session.
- **Obituary the same day** — Tinari's Taschen text verbatim in the local
  corpus, plus an archive.today capture stamped 9 Feb 2025 22:24 UTC. Say
  *"the same day"*; "the same night" is not sourced.
- **Last penny struck November 2025** — `knowledge/cents.md` and the UCCA text.

**Which copy to trust.** Three defects in the local corpus, verified here: its
README claims frontmatter carries `source` and `retrieved` (measured: **0/58
and 0/58**, so no corpus page can date itself); all six `museum-*.md` carry
`/museums/<slug>` URLs that **404**; and `museum-ucca.md` undercounts the UCCA
curators in three places. **For institutional facts, `data/museums.json` and
the live site are the fact; `corpus/pages/museum-*.md` is the prose.**

**House style on Chang's death:** past tense, raised only where it adds
something, never speculated about. The 2026 retrospective is posthumous.

---

## 6. Credentials — in, and held back

From the artist's own list (rutherfordchang.com/exhibitions.html, 2002–2024).
Ocula's page is behind bot verification and was not worked around.

**In:** *"Shown for two decades, from the ICA in London to the Art Gallery of
Ontario"* (two real anchors spanning the record — ICA 2005, AGO 2022 — rather
than a list no viewer retains), and *"Christie's sold the block in 2024. UCCA
Beijing gave him a retrospective in 2026"*, placed in movement **V** because
the institutional afterlife is evidence the work is still running.

**Held in reserve, all verified, any one line:** Akademie der Künste Berlin
(2021) · Kunsthal Rotterdam (2020) · Deichtorhallen Hamburg (2019) · Rhizome &
the New Museum (2016) · BALTIC Newcastle (2015) · FACT Liverpool (2014) ·
Indianapolis MCA (2013) · CAFA Museum Beijing (2012) · Queens Museum (2006) ·
Haus der Kulturen der Welt (2005) · Singapore Art Museum (2004) · The Bronx
Museum (2003). Plus Tinari's text in Taschen's *On NFTs*.

**Paid for by cutting** *"A ceiling set by metallurgy, and a hole cut by a
war."* Both facts are still spoken; only the sentence binding them is gone.
Twelve words, one line to restore in place of Christie's and UCCA.

---

## 7. Open

- **The two facts in I and II are yours to approve.** They are verified and
  they are an obituary. The craft decisions here are mine; that one is not.
- **Deliberately omitted:** the five natures and five transformations (the
  first film has them), digital objecthood (its own film), the collector
  community, the 25 stuck cents. A three-minute introduction that mentions
  everything introduces nothing.
- **Then:** record §1, align, rebuild the shot list against the recording.

---

## 8. What this forces on the finished 2:21 film

1. **"More than five hundred billion Lincoln cents were produced."** The
   project description says ~288 billion *in existence*. Both can be true —
   struck versus surviving — but the film states one and the project the other.
2. **"about two and a half cents as copper."** The description says ~3.1¢. The
   recorded qualifier *"at the time he made the piece"* saves it, and holds.
3. **Present tense throughout.** Chang died in February 2025. The source essay
   is dated October 2025 and also uses the present tense, so the film is
   faithful to it — but a viewer who knows will hear it. Author's call.
