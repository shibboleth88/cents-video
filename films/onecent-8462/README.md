# One Cent: #8462

An episode of the One Cent series. The series brief is `/mnt/project-files/single-cent-series/BEST_PRACTICES.md`. The script, decisions and claims table are in `/mnt/project-files/single-cent-series/8462/8462_proposal_v0.1.md`. The reference episode is `films/onecent-6129`.

- **Concepts.** The primary is C23 "Difference makes meaning", carried by a Reiss quote. The value tie is C08 "Can destruction create value?", carried by a Lehnen quote from "Rutherford Chang's Conceptual Collecting". check_quotes.py reported both quotes FOUND.
- **Narration.** This is "eee" v1 take 1 (eleven_multilingual_v2), 121.0 s of the full script `archive/tts_text_v0.1_full.txt`.
  - It was transcribed with scribe_v1, and the transcript equals the TTS text. The scribe caveat in the 6129 README applies.
  - Take 2 (123.9 s) is on the ElevenLabs flow and is not used.
- **Audio.** `audio/build_vo.py` cuts two whole sentences out of the take at gap midpoints: the Council-debate line and "altered twice". It then inserts five holds, pads 10.5 s, and applies loudnorm I=-16, TP=-1.5, LRA=11.
  - `vo.wav` is 120.41 s, with 109.9 s of narration.
  - The alignment is remapped through the edits, and it equals the cut `audio/tts_text.txt`.
- **Captions.** `captions/build_cues.py` is copied from #478, with its own SPOKEN table. The spaced dash in the Reiss quote takes zero spoken words.
  - It also writes `captions.srt`.
  - Control: "engraved" changed to "carved" in the script was refused.
- **3DCENTS.** The source is the user's export `cent-8462-360-1080x1920-25fps-reel`, retimed to 30 fps (150 frames) as `public/3dcents/8462-360-30fps.mp4`.
  - The coin on frame 0 has centre 539.5, 959.0 and diameter 776 × 775.
  - The photo coin is 0.81–0.82 of the image, depending on the threshold. The component uses 0.815.
- **Images.** The 1050px fronts of #8462 and #2125 come from cents.vision, in `public/hires/`. The 26 Vandalized fronts are downscaled to 300px in `public/cents/`. All of these are gitignored.
- **Pour footage.** Asset a14 (`public/assets/a14.mp4`) is copied from the objecthood film's assets.json and captioned "Casting CENTS Block Copper".
- **Shared change.** In `src/style/onecent.tsx`, `useSpokenWords` now skips punctuation-only card tokens, and quotes take an optional `spoken` map. This text is identical to the #2616 branch, so the two merge cleanly.

Render (from the repo root, after `python3 pipeline/film.py switch onecent-8462`):

    npx remotion render src/index.ts Video films/onecent-8462/exports/one-cent-8462_v1_clean.mp4
    npx remotion render src/index.ts VideoCaptioned films/onecent-8462/exports/one-cent-8462_v1_captioned.mp4

In the cloud container, add `--browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`.

## v2 (2026-10-27): the calm voice
- **Voice.** v2 uses the setting the user picked in the #2616 thread: "eee" on eleven_v4, with `[thoughtfully] [calm]` once at the start of the prompt and default voice settings.
  - The full script (v0.1, nothing cut) is 246 words and ran 93.0 s, about 2.65 words/s.
  - The scribe transcript equals `audio/tts_text.txt`. A control word change does not match.
  - The two v1 cuts are no longer needed for length, so v2 keeps them both. The v1 build is in `archive/`.
- **Holds.** v2 has 15 holds. Each sits at the middle of a silencedetect pause (n=-35dB, d=0.2), not at the midpoint between scribe word timings.
  - On v4 takes, scribe word ends run about 0.4 s into the following pause, so 9 of 15 gap midpoints fell on the next word's attack. The #2616 thread saw the same trap.
  - `vo.wav` is 112.84 s, of which 102.4 s is narration.
- **Renders.** `one-cent-8462_v2_{clean,captioned}.mp4` run 1:53 (3385 frames). Copies are in `/mnt/project-files/single-cent-series/8462/`.
