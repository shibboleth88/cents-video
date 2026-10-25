# One Cent: #6129

The first episode of the One Cent series. The series brief is `/mnt/project-files/single-cent-series/BEST_PRACTICES.md`; the concept base is `concepts.py` beside it. Script v0.3 is in `/mnt/project-files/single-cent-series/6129/6129_proposal_v0.3.md`. The user approved it in the thread on 2026-10-25 at 17:07Z ("the current script is good, but let's add that": the named concepts and credited quotes).

- **Concepts:** C24 "The mark as index: a time-stamp, not an image" (primary) and C26 "Coin collecting turned over" (the value tie). Each is named on screen by a concept card and carried by a credited quote.
- **Narration:** eo v1 take 1 (eleven_v4, generation E1Vb6vTI5XXJzj2XSvDZ), 63.0 s. It was transcribed with scribe_v1 and matches `audio/tts_text.txt` word for word (155 words). A control with one word changed ("patina" to "surface") does not match.
  - Caveat: scribe on this flow returns text identical to the prompt, so the transcript works as forced alignment and is weak evidence of what was actually said (see project memory `cents-sets-film-b`).
- **Audio:** loudnorm I=-16, TP=-1.5, LRA=11. It is padded with 6 s of silence rather than the usual 2.5 s, to give the end credits room.
- **Captions:** `captions/build_cues.py`, copied from the Daidatep builder with its own spoken-number table. It refuses on a mismatch: the control "patina" changed to "surface" was refused.

## Claims and checks

| Claim | Check |
|---|---|
| #6129: 1979, no mint mark; Faceless, Notable Gold, Notable Verdigris, Significant Obsidian; contaminated with Obscure Adhesive | `knowledge/data/cents_traits_sep2026.json` (the Sep 2026 export) |
| 85 Faceless Cents | `cents_by_trait.json` counts.faceless = 85 |
| 7 Cents are both Faceless and gold | faceless ∩ (notable or full gold): 1864, 2016, 3109, 3260, 4413, 6129, 9344 |
| The glossy patch over LIBERTY is the Obscure Adhesive | the user confirmed it, 2026-10-25 17:09Z |
| Reiss quote (card text) | `check_quotes.py --quote`: FOUND in `knowledge/sources/cents-bot/reiss__materiality-and-signification.md` |
| Rees quote | FOUND in `shibboleth__makes-cents.md`, and at line 330 of `knowledge/sources/medium/2024-10-17_makes-cents.md` |

#6129 is not on the cents.vision 1/1 Trait Combo list, so the film never calls it one.

## Shots

- `CentLook` (new, `src/style/onecent.tsx`) holds the 1050px cents.vision front or back of one Cent.
  - Camera moves happen on phrases, each to a measured box (from `6129_zoom_plan.jpg`).
  - It can do a flat 2D flip.
  - It lays the concept card and a quote card over the dimmed coin. The quote's credit sits in the readout band.
- At frame 0 the coin, name and readout are fully visible.
- The 3DCENTS variant (`timeline/timeline_3dcents.json`) adds the user's 3DCENTS export of #6129 as its own shot under "Around it, obsidian, verdigris and gold".
  - The export is 25 fps, retimed frame for frame to 30 fps; the result has 150 frames.
  - The coin was measured on frame 0: centre 539.5, 959.5; diameter 775.
  - It is credited on screen and in the end credits: "3D render: 3DCENTS by sinvalli".

## Renders

- `exports/one-cent-6129_v1_{captioned,clean}.mp4` are gitignored. Copies are in `/mnt/project-files/single-cent-series/6129/`.
- `one-cent-6129_v1-3dcents_*` is the same film with the 3DCENTS turn.
