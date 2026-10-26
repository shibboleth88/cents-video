# One Cent: #6129

The first episode of the One Cent series. The series brief is `/mnt/project-files/single-cent-series/BEST_PRACTICES.md`; the concept base is `concepts.py` beside it. Script v0.5 is in `/mnt/project-files/single-cent-series/6129/6129_proposal_v0.5.md`. It applies the user's notes of 2026-10-26 11:49Z. Earlier versions are in `archive/`: v0.4 was the 2026-10-25 19:20Z round, and v1 used script v0.3.

- **Concepts:** C24 "The mark as index: a time-stamp, not an image" (primary) and C26 "Coin collecting turned over" (the value tie). Each is named on screen by a concept card and carried by a credited quote.
- **Narration:** eo v3 take 1 (eleven_v4), 90.1 s. It was transcribed with scribe_v1 and matches `audio/tts_text.txt` word for word (214 tokens). The control, "patina" changed to "surface", does not match.
  - `audio/build_vo.py` inserts silent holds in three sentence gaps and shifts the word timings to match. It refuses if a hold would fall inside a word.
  - The TTS text spells Reiss as "Rice" for the pronunciation. The captions keep "Reiss", mapped in `build_cues.py`.
  - Earlier takes: v1 take 1 and v2 take 2.
  - Caveat: scribe on this flow returns text identical to the prompt, so the transcript works as forced alignment and is weak evidence of what was actually said (see project memory `cents-sets-film-b`).
- **Audio:** loudnorm I=-16, TP=-1.5, LRA=11. It is padded with 10.5 s for the closing spin card (one 5 s turn) and the credits.
- **Captions:** `captions/build_cues.py`, copied from the Daidatep builder with its own spoken-number table. It refuses on a mismatch: the control "patina" changed to "surface" was refused.

## Claims and checks

| Claim | Check |
|---|---|
| #6129: 1979, no mint mark; Faceless, Notable Gold, Notable Verdigris, Significant Obsidian; contaminated with Obscure Adhesive | `knowledge/data/cents_traits_sep2026.json` (the Sep 2026 export) |
| 85 Faceless Cents | `cents_by_trait.json` counts.faceless = 85 |
| 7 Cents are both Faceless and gold | faceless ∩ (notable or full gold): 1864, 2016, 3109, 3260, 4413, 6129, 9344 |
| The glossy patch over LIBERTY is the Obscure Adhesive | the user confirmed it, 2026-10-25 17:09Z |
| Reiss quote (card text) | `check_quotes.py --quote`: FOUND in `knowledge/sources/cents-bot/reiss__materiality-and-signification.md` |
| #1605 is a 1979 whose only trait is Lustrous (the template Cent, the user's choice) | trait export: year 1979, lustrous, nothing else; inscription 66001324 |
| #6129 inscription number 65998562 | trait export |
| Rees quote | FOUND in `shibboleth__makes-cents.md`, and at line 330 of `knowledge/sources/medium/2024-10-17_makes-cents.md` |

#6129 is not on the cents.vision 1/1 Trait Combo list, so the film never calls it one.

## Shots

- `CentLook` (new, `src/style/onecent.tsx`) holds the 1050px cents.vision front or back of one Cent.
  - Camera moves happen on phrases, each to a measured box (from `6129_zoom_plan.jpg`).
  - It can do a flat 2D flip.
  - It lays the concept card and a quote card over the dimmed coin. The quote's credit sits in the readout band.
- At frame 0 the coin, name and readout are fully visible.
- `CentCompare` puts the Cent beside a template Cent; `CentField` shows every Cent with a trait (here the 85 Faceless), the episode's Cent ringed, and refuses if the readout differs from the list length.
- Trait-area boxes (fractions of the 1050px image): adhesive [0.105,0.305,0.4,0.629] (user-confirmed); gold, front [0.38,0.36,0.64,0.62]; obsidian, back [0.30,0.20,0.62,0.40]; verdigris, back [0.66,0.16,0.88,0.42]. The last three are Claude's reading of the photographs.
- v2 had a separate 3DCENTS variant (now `archive/timeline_v2_3dcents.json`). From v3 the spin is part of the one film.
  - The export is 25 fps, retimed frame for frame to 30 fps; the result has 150 frames.
  - The coin was measured on frame 0: centre 539.5, 959.5; diameter 775.
  - It is credited on screen and in the end credits: "3D render: 3DCENTS by sinvalli".

## Renders

- `exports/one-cent-6129_v2_{captioned,clean}.mp4` (and v1) are gitignored. Copies are in `/mnt/project-files/single-cent-series/6129/`.
- `one-cent-6129_v2-3dcents_*` is the same film with the 3DCENTS turn as the recap.

## v3 shots (2026-10-26)
- `CentSpin` is the Cent's card with the 3DCENTS turn. It opens the film, and closes it held for exactly 150 frames, one turn.
- `CentLook` moves can now:
  - start late (`plus`);
  - run slowly (`dur`);
  - zoom closer (`max`, refused past 4.5x);
  - ring several areas at once (`marks`).
- Quote cards light each word as it is spoken. Card and recording must agree word for word, or the render fails.
- `CentDissolve` dissolves between whole cards: the episode's Cent and the template.
- `CentScroll` is a close-up quick scroll of a whole pool. It refuses a readout that differs from its list.
- `CentSet` shows a small set, numbered.
- All Cents are cut out on black.
- Trait areas, all on the front, as fractions of the 1050px image. They were mapped from the user's circled screenshots by fitting the coin's circle:
  - adhesive [0.097,0.299,0.37,0.657] and [0.31,0.11,0.48,0.26];
  - gold [0.20,0.20,0.40,0.36];
  - obsidian [0.384,0.228,0.537,0.357] and [0.374,0.595,0.438,0.66];
  - verdigris [0.771,0.437,0.901,0.59], [0.455,0.584,0.511,0.655] and [0.544,0.727,0.654,0.85].
- `timeline.json` anchors gained `after_phrase` + `plus` (seconds), for the wordless closing hold (`src/lib/timeline.ts`, `pipeline/anchors.py`).
