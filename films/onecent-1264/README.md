# One Cent: #1264

An episode of the One Cent series. The series brief is `/mnt/project-files/single-cent-series/BEST_PRACTICES.md`. The script, claims table and flags are in `/mnt/project-files/single-cent-series/1264/1264_proposal_v0.1.md`. The reference episode is `films/onecent-6129`; the build is copied from `films/onecent-8462`.

- **Cent.** 1944, no mint mark; Notable Gold, Significant Obsidian, Contaminated: Paint (Sep 2026 export). The oldest Gold Cent by 12 years (next: #6789, 1956). Year first (22 Cents dated 1944) because that pool is smaller than Gold's 69.
- **Concepts.** Primary C17 "Time-based generative art"; value tie C55 "Years that carry meaning". Both quotes are from Martin Lehnen, "Thoughts about the unique nature of CENTS traits and their significance"; check_quotes.py reported both FOUND.
- **Narration.** eee on eleven_v4 with `[thoughtfully] [calm]` once at the start, default settings. Two takes (flow IlOj0SH2aPERgwPfYu67); take 2 (generation 6B8Iol8t0P57u3UCsVwG, 99.4 s, 274 words, about 2.75 words/s) is used. scribe_v1 transcript equals `audio/tts_text.txt` (the scribe caveat applies: listen as well).
- **Audio.** `audio/build_vo.py` inserts 18 holds and pads 6.5 s, then loudnorm I=-16, TP=-1.5, LRA=11. `vo.wav` is 119.26 s.
  - New here: this take often leaves less than 0.2 s between sentences, so `gap_after` finds no silencedetect pause. The builder now falls back to the longest quiet run (at least 150 ms, the comma rule from #8462) and prints which holds used it ("later.", "gold.", "code."").
  - The first hold (1.6 s after "sixty-four.") pushes the first zoom past frame 150, so the year zoom starts after the turn has settled.
- **Captions.** `captions/build_cues.py` with its own SPOKEN table; the spaced dash in the first quote takes zero spoken words. Control: "fleck" changed to "chip" in the script was refused.
- **3DCENTS.** The user's export `cent-1264-360-1080x1920-25fps-reel` (cents shortlist), retimed to 30 fps (150 frames) as `public/3dcents/1264-360-30fps.mp4`. Coin on frame 0: centre 539.5, 959.5; diameter 776. The photo coin is 0.824 of the image, so `d` is 768 (776 × 0.815 / 0.824) to keep the handover the same size.
- **Images.** 1050px fronts of #1264, #543 (template: 1944, no visual trait) and #4273 (the Atlas's Full Gold example) in `public/hires/`; the 22 Cents of 1944 and the 69 Gold Cents downscaled to 600px in `public/cents/`. All gitignored; fetched from cents.vision.

Render (from the repo root, after `python3 pipeline/film.py switch onecent-1264`):

    npx remotion render src/index.ts VideoCaptioned films/onecent-1264/exports/one-cent-1264_v1_captioned.mp4

In the cloud container, add `--browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`. Restore the root symlinks with `git checkout` before committing.
