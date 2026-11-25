# One Cent: #1867

An episode of the One Cent series. Brief: `/mnt/project-files/single-cent-series/BEST_PRACTICES.md`. Working files: `/mnt/project-files/single-cent-series/1867/`.

**Status: script v0.1 for shibboleth's review (2026-11-25). Nothing voiced.** Only the user approves a version.

- **The Cent.** Dated 1964, no mint mark, unique ID 1964 093, inscription 66001799. Traits: Significant Obsidian, Significant Verdigris, Contaminated (Alien Secretion). A whole trait profile no other Cent shares.
- **Concept.** C20 "Circulation leaves traces" (first use in the series). Spine: the Traits Atlas's patina ("arises from internal chemistry") against contamination ("matter imposed upon copper").
- **Guiding sources.** The series brief, the quote bank (H25, Kruger via Myers) and, from 2026-11-25 at shibboleth's request, the art/crypto presentation work (art text v0.5.1).
- **Counts.** `script/counts.py` recomputes every spoken figure from the raw export, with floors (verdigris 1,884; 436 unique profiles) and a control (a planted copy of #1867's profile breaks the uniqueness check).
- **3DCENTS.** Exported in the container with `pipeline/export_3dcents.cjs 1867 … Black` (150 frames, 25 fps, coin d 776 at 539.5, 958.5; `yuvj420p`, black at luma 0); retimed to `public/3dcents/1867-360-30fps.mp4` with `-pix_fmt yuv420p` (ignored by git). A copy is in the user's "cents shortlist".
- **Ledger.** `ledger/trace.py` (from #8820, reveal output as an argument: this is an i1 inscription on output 1), `ledger/LEDGER_1867.md`: three transfers, held by one wallet since 17 April 2024; matches cents.vision's wallet index on five dates.
- **Atlas plates.** `script/atlas_shoot.cjs` (from #10000) on cents.vision's Traits Atlas, into `public/assets/1867/`.
- **Pipeline copies.** `audio/build_vo.py`, `check_heard.py`, `make_standin.py`, `captions/build_cues.py`, `review_*.{py,mjs}` copied from #10000 (whose build_vo.py keeps the #9344 hold fix); not yet adapted.
