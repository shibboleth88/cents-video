# One Cent: #8820

An episode of the One Cent series. The series brief is `/mnt/project-files/single-cent-series/BEST_PRACTICES.md`. Working files are in `/mnt/project-files/single-cent-series/8820/`.

**Status: script v0.2 for review (shibboleth's edits applied; the ending is open). Silent rehearsal done on stand-in timing; nothing is voiced or rendered.** Only the user approves a version.

- **The Cent.** 1972, no mint mark (Philadelphia), inscription 65907201. Traits: Significant Red and Notable Verdigris, nothing else.
- **Concept.** C21 "Permanence and decay", with C04 "Value made by consensus" as the value tie.
- **Art literature.** Walter Benjamin, "The Work of Art in the Age of Mechanical Reproduction" (1936), tr. Harry Zohn: QUOTE_BANK v0.7 rows D11 and D10, read through `art-historical-context.md` §2.7. Both FOUND by `check_quotes.py`; one-word controls went red.
- **Counts.** `script/counts.py` recomputes every spoken figure from the raw export and refuses to run if its floor (Full Red = 71) fails. The floor was seen red on a copy with one Full Red flag removed.
- **3DCENTS.** The user's export `cent-8820-360-1080x1920-25fps-reel.mp4` is in "cents shortlist" (150 frames, 25 fps). Not yet retimed.
- **Template.** #8653, the only 1972 no-mark Cent whose sole trait is Lustrous.

## Revision log

- **v0.1 script, 2026-11-14.** `script/8820_proposal_v0.1.md` (copy of the project-files proposal). Open questions there: length A or B, whether the grey-green patches on Lincoln's face count as verdigris, and Benjamin's pronunciation.
- **v0.2 script, 2026-11-15.** `script/8820_proposal_v0.2.md`. shibboleth's three edits: line 5 ends "like daubs of paint laid by time"; the photographed/inscribed/melted line and the "set and reset by the people" line are cut. The cut version ends on "The penny itself is gone"; the proposal recommends swapping the last two Benjamin lines so the film ends on the ledger. About 282 spoken words, about 1:50 to 2:10.
- **Silent rehearsal, 2026-11-15** (brief §7, #1328 lesson). Built on the #9344 branch (merged in for the latest components and `build_vo.py`), in the recommended ending order. `audio/make_standin.py` writes a STAND-IN `script/alignment.json` (about 2.6 words a second plus the planned holds) and a silent `audio/vo.wav`; `review_times.py` picks key moments of every shot and `review_stills.mjs` renders them. Sheets: `/mnt/project-files/single-cent-series/8820/rehearsal/`. Stand-in length 2:11. What it caught, all fixed before any voice credits:
  1. A CentScroll caption ("Significant Red, Notable Verdigris") wrapped and SafeText refused the frame. Now "only these two traits".
  2. At six and eight across, CentScroll's inset ring was a hairline on copper, and in number order #8820 scrolled past unseen. New opt-in `spotlight` on CentScroll: it settles about a second early, dims the others and rings the marked Cent outside its rim; #8820 is placed last in both pools so the scroll lands on it. Other films are unchanged (the default ring is as before).
  3. The 339 Cents of 1972 as a CentField came out about 30 px each, dots rather than Cents. Now a CentScroll eight across. (CentField also gained opt-in `cutout` and `texture`; unused now.)
  4. Seven rings at once on a coin reduced for marks read as clutter (s05, s14). Those shots now show the whole coin, no rings.
  5. "1972, no mint mark" is too long for a scroll title at 84 px. Title "1972", caption "Cents with no mint mark".
  6. The ledger plate's type was small at the plate's 732 px cap. Redrawn at that width with larger type.
  7. Still open for the build: in the stand-in, the rim zoom and the face-patch zoom land 0.8 s apart ("along the rim, with grey-green patches"). Plan a short hold at "rim," in `build_vo.py`.
- **Ledger, 2026-11-15.** `script/ledger/`: the satoshi carrying inscription 65907201 traced on mempool.space (five transfers since 26 March 2024, the last on 14 Nov 2026 into a wallet cents.vision groups under Daidatep's Wall), cross-checked against three cents.vision holder snapshots.
