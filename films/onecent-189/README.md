# One Cent: #189

An episode of the One Cent series in the baseline format. Brief: `/mnt/project-files/single-cent-series/BEST_PRACTICES.md`. Working files: `/mnt/project-files/single-cent-series/189/`.

**Status (2026-11-26): script v0.2 approved by shibboleth 02:43Z ("go ahead with the video creation please"). The film is built on stand-in timing; the voice is not recorded yet, because the ElevenLabs account ran out of credits (both eee v4 takes refused: 1,169 credits left, 1,485 needed per take).** Only the user approves a version.

- **The Cent.** Dated 1960, D mark, unique ID 1960d 051, inscription 66001226. Traits: Full Red, Notable Desert. Not a 1/1 trait combo (nine Cents share the profile), so no uniqueness claim. Of the 71 Full Red Cents it is the only one dated 1960 (Sep 2026 export).
- **Concept.** C26 "Coin collecting turned over", from the baseline text's "Now": a grade rewards an object for how little has happened to it; the collectors of CENTS value what happened to each coin. Value tie C04 in the closing line.
- **Quote.** Barbara Kruger, quoted by Rhea Myers in conversation with Maya B. Kronic, *Proof of Work* (Urbanomic, 2022): "Money is an information-destroying medium." On plain black (QUOTE_BANK H25, "About CENTS? No").
- **Script.** `script/189_proposal_v0.2.md`, `script/voice_v0.2.txt`; `script/voiceover.txt` is the written form, `audio/tts_text.txt` the spoken form (adds "number" for "#" and "dot" in the site names).
- **3DCENTS.** Exported in the container with `pipeline/export_3dcents.cjs` (150 frames, 25 fps, black, coin d 776 at 539.5, 959.5); retimed to `public/3dcents/189-360-30fps.mp4` with `-pix_fmt yuv420p` (ignored by git). The export is in the working files.
- **Ledger.** `ledger/trace.py` (from #1867), `ledger/LEDGER_189.md`: 11 transfers after the reveal, the latest on 23 Nov 2026. Not cross-checked (Hiro API 403).
- **Atlas plates.** `script/atlas_shoot.cjs` on cents.vision (red.html, desert.html), cropped to whole lines, in `public/assets/189/`.
- **Timeline.** `timeline/make_timeline.py` writes `timeline.json` (39 shots) and `assets.json`. Phrase anchors only, so the take does not change it.
- **New shots.** `src/style/storykit.tsx`, Look C: StoryWords, StoryScale (Littleton's grade terms), StoryText (typeset plates, the ledger rows), StoryQuote, StoryScroll (a pool, fast, with spotlight), StoryDots (all 10,000 in number order), StoryFlip (the fast back-and-forth, at least six swaps, the name swapping with the coin), StoryLadder (the Atlas's three examples).
- **Not used, and why.** Media library S0905 and S0906 are labeled "notable desert" but both Cents (#528, #5448) are Significant Desert in the export. C027 (collector cards) shows wallet addresses, as #1867 found. The grading-red lines were dropped by shibboleth.
- **Readings to confirm.** The desert areas (hair and temple, cheek, coat at lower left) and "close to mint state" for #9794 are Claude's readings of the photos.
- **Audio, when credits allow.** Voice `tts_text.txt` with eee on eleven_v4; fetch each take by URL, transcribe with scribe_v1, `audio/check_heard.py <words> audio/tts_text.txt` and `--control`; `--write-alignment`; then `python3 -I films/onecent-189/audio/build_vo.py --dry`, then without `--dry`; `captions/build_cues.py`.
