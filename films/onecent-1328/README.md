# One Cent: #1328

An episode of the One Cent series. The series brief is `/mnt/project-files/single-cent-series/BEST_PRACTICES.md`. The script, the quotes table and the open questions are in `/mnt/project-files/single-cent-series/1328/1328_proposal_v0.1.md` (with a "Changes after v0.1" section). The build is copied from `films/onecent-1264` (branch `claude/project-thread-apps81`, PR #26), and the components `src/style/onecent.tsx` and `src/style/plates.tsx` are that branch's versions.

- **Cent.** 1979, no mint mark (Philadelphia). Inscription #66001019. Traits: Fingerprints and White Drips and Streaks; nothing else (Sep 2026 export, recounted from the 9 Nov 2026 cents.vision snapshot; both agree).
  - 640 Cents are dated 1979, 224 carry Fingerprints, 82 carry White Drips and Streaks. The traits are rarer than the year, so they lead after the opening.
  - Three Cents carry both traits: #1170, #1328, #8400. Only #1328 has no other trait. It is not on cents.vision's 1/1 Trait Combo list, so the film never says "1/1".
  - 79 of the 82 White Drips Cents are also Desert; #217, #1328 and #5626 are not.
- **Concepts.** Primary C24 "The mark as index", carried by Rosalind Krauss, "Notes on the Index" (October 3, 1977), QUOTE_BANK D13. Value tie C03, shown as "Transformations of value". The m4rtr3d quote is from his MAKES CENTS interview. check_quotes.py reported both FOUND; the Atlas sentence is an exact substring of `films/traits/script/atlas/fingerprint.txt`.
- **Narration.** eee on eleven_v4 with `[thoughtfully] [calm]` once at the start, default settings. Two takes on flow Nh7DBox7bQJKxQzO2cSu: take 1 (generation 1KXNNHSQOaQwpKjX7Nvl, 101.4 s) and take 2 (generation cOlqXKDOY59fucO4LACb, 105.8 s, about 2.9 words/s). Take 2 is used: slower, with longer sentence pauses.
  - **Heard check.** Each take was attached to the flow by URL as a fresh asset and transcribed with scribe_v1, so the transcript comes from the audio, not the prompt (no tag tokens, numbers as digits). `audio/check_heard.py` (copied from the Dopemind Wall branch; it now reads "sixteen-oh-five" and "two hundred and twenty-four") reports 296 tokens equal for both takes, with one accepted homophone: "Martrid" for "Martred". The control (one word dropped) goes red for both.
  - **Timings.** `check_heard.py --write-alignment` maps the heard word timings onto the words of `audio/tts_text.txt` (`audio/v1_take2_textwords.json`, then `audio/v1_take_words.json`), so captions and anchors use the spoken words, timed from the audio.
- **Audio.** `audio/build_vo.py` inserts 20 holds at silencedetect pauses (none fell back to quiet runs) and pads 7 s, then loudnorm I=-16, TP=-1.5, LRA=11. `vo.wav` is 128.26 s. The first hold (2.0 s after "twenty-eight.") puts "struck" at 5.12 s, after the 150-frame turn, so the year zoom starts on a settled front.
- **Captions.** `captions/build_cues.py` with its own SPOKEN table (#1328, 1979, 224, 82, 79, #1605, 1977, m4rtr3d). 46 cues; the audit is clean.
- **Shots.** 20 shots, median 5.2 s; the long ones are the opening card (17.4 s: the turn, then four moves), the Krauss card (16.9 s, two moves then the quote) and the m4rtr3d quote card (11.1 s). The closing spin card runs 5.3 s, one full turn.
- **3DCENTS.** The user's export in cents shortlist, retimed to 30 fps (150 frames) as `public/3dcents/1328-360-30fps.mp4`.
- **Images.** 1050 px fronts of #1328 and #1605 (template: 1979, close to mint state) and the back of #1328 in `public/hires/`; the 224 Fingerprints Cents, the 82 White Drips Cents and the sets in `public/cents/` (300 px, from `shibboleth88/sovrn-onchain`). Plates in `public/assets/1328/` and the objecthood assets a14 (pour) and a17 (photography setup). All gitignored; `timeline/assets.json` holds source, rights and sha256 for each plate.
- **Blocked here:** ordinals.com api.hiro.so ordiscan.com static.unisat.io. The inscribed image is the sovrn-onchain mirror's copy, not re-fetched from chain.

Render (from the repo root, after `python3 pipeline/film.py switch onecent-1328`):

    npx remotion render src/index.ts VideoCaptioned films/onecent-1328/exports/one-cent-1328_v1_captioned.mp4

In the cloud container, add `--browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`. Restore the root symlinks with `git checkout` before committing.

## v1 delivery check (2026-11-11)

- `exports/one-cent-1328_v1_captioned.mp4` (not committed; copied to `/mnt/project-files/single-cent-series/1328/` with `one-cent-1328_v1.srt`). 1080×1920, 30 fps, 3848 frames, 128.28 s, 47.5 MB.
- Full decode with ffmpeg: no errors. Loudness -17.3 LUFS integrated, LRA 5.2.
- First frame: the opening card (title, Story time pill, the turn's first frame), not black. Last frame: black, the fade after the credits; the credits hold from 123.8 s.
- blackdetect (0.3 s, pixel threshold 0.10): six dips of 0.3 to 0.6 s, each at a shot boundary (57.3, 74.2, 80.7, 91.7, 112.0, 122.7 s), the shot fades. freezedetect (3 s): only the credits card, 123.77 to 128.03 s.
- Audio: the render's envelope correlates 1.0 with `public/vo.wav`; control, the unused take 1, correlates 0.04.
- Stills of every shot (start, middle, end) and the middle of each caption over 40 characters rendered without a layout error before the full render.
- Exported and verified is not approved: only the user approves a version.
