# One Cent: #478

Episode 2 of the One Cent series. Series brief: `/mnt/project-files/single-cent-series/BEST_PRACTICES.md`. Script and decisions: `/mnt/project-files/single-cent-series/478/478_proposal_v0.1.md`. Reference episode: `films/onecent-6129`.

- **Concepts:** C50 "Traits named by the community" (primary) and C04 "Value made by consensus" (value tie), each named on a concept card and carried by a credited quote (Reiss, Lehnen; both FOUND by `check_quotes.py`).
- **Narration:** eo v1 take 1 (eleven_v4), 93.4 s, transcribed with scribe_v1 (equal to `audio/tts_text.txt`; the scribe caveat in the 6129 README applies). Take 2 is kept.
- **Audio:** `audio/build_vo.py` adds five holds and pads 10.5 s for the closing turn and credits; loudnorm I=-16, TP=-1.5, LRA=11. `vo.wav` 108.66 s.
- **Captions:** `captions/build_cues.py` (from 6129, own SPOKEN table). Control: "dark" changed to "black" in the script was refused.
- **3DCENTS:** the user's export `cent-478-360-1080x1920-25fps-reel`, retimed to 30 fps (150 frames) into `public/3dcents/478-360-30fps.mp4`. Coin on frame 0: centre 539.5, 959.0; diameter 775. Photo coin: 0.816 of the image.
- **Images:** 1050px fronts of #478 and #3525 from cents.vision in `public/hires/`; the 95 Speckles Cents downscaled from cents.vision fronts to 300px in `public/cents/` (all gitignored).
- **Trait areas** (fractions of the 1050px front; Claude's reading, pending the user): obsidian [0.485,0.16,0.79,0.32]; desert [0.28,0.14,0.40,0.22] and [0.55,0.53,0.64,0.60]; Speckles [0.12,0.40,0.48,0.69] and [0.49,0.65,0.80,0.83].

Render (from the repo root, after `python3 pipeline/film.py switch onecent-478`):

    npx remotion render src/index.ts Video films/onecent-478/exports/one-cent-478_v1_clean.mp4
    npx remotion render src/index.ts VideoCaptioned films/onecent-478/exports/one-cent-478_v1_captioned.mp4

In the cloud container add `--browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`.
