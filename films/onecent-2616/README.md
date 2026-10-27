# One Cent: #2616

Episode 3 of the One Cent series. Series brief: `/mnt/project-files/single-cent-series/BEST_PRACTICES.md`. Script and decisions: `/mnt/project-files/single-cent-series/2616/2616_proposal_v0.2.md`. Reference episode: `films/onecent-6129`.

- **Concepts:** C57 "Scarcity written by survival" (primary) and C26 "Coin collecting turned over" (value tie), each named on a concept card and carried by a credited quote (Lehnen, Dagmar; both FOUND by `check_quotes.py`). Grades (Full, Significant) are explained from the Traits Atlas v1.1.
- **Narration:** "eee" (`pp4OmJ3yyWS9Jyhejh5f`, eleven_multilingual_v2), v2 take 2, 94.3 s. Transcribed with scribe_v1, equal to `audio/tts_text.txt` (the scribe caveat in the 6129 README applies). Take 1 (96.1 s) is kept. Script v0.1 ran 125.7 s in this voice and was cut; its takes are in `archive/`.
- **Audio:** `audio/build_vo.py` adds five holds and pads 10.5 s for the closing turn and credits; loudnorm I=-16, TP=-1.5, LRA=11. `vo.wav` 109.57 s.
- **Captions:** `captions/build_cues.py` (from 478, own SPOKEN table, including the card's "…1912").
- **Quote card with digits:** the Lehnen card writes years as digits, so the quote carries `spoken` ({"…1912,": "nineteen twelve", "1911": "nineteen eleven"}); `useSpokenWords` in `src/style/onecent.tsx` consumes several spoken words for such a card word. A punctuation-only token lights with the word before it (shared with the #8462 episode).
- **3DCENTS:** the user's export `cent-2616-360-1080x1920-25fps-reel`, retimed to 30 fps (150 frames) into `public/3dcents/2616-360-30fps.mp4`. Coin on frame 0: centre 539.5, 959.5; diameter 776. The photo coin here is 0.822 of the image (not 0.815), so `d` is given as 769 to keep the handover at the same size.
- **Images:** 1050px fronts of #2616, #9540, #1073 from cents.vision in `public/hires/`; the 71 Full Red and 12 1/1 Year Cents downscaled from cents.vision fronts to 300px in `public/cents/` (all gitignored).
- **Trait areas** (fractions of the 1050px front; Claude's reading, pending the user): date [0.64,0.60,0.84,0.70]; red field [0.58,0.24,0.93,0.64]; verdigris [0.40,0.27,0.62,0.52], [0.40,0.54,0.58,0.70], [0.26,0.68,0.44,0.83].

Render (from the repo root, after `python3 pipeline/film.py switch onecent-2616`):

    npx remotion render src/index.ts Video films/onecent-2616/exports/one-cent-2616_v1_clean.mp4
    npx remotion render src/index.ts VideoCaptioned films/onecent-2616/exports/one-cent-2616_v1_captioned.mp4

In the cloud container add `--browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`.
