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

## v2 (2026-11-02, the user's notes on v1)

- **Changes asked for:**
  - Both gold areas the user circled are ringed together.
  - The 1940s Set line is gone, and so is the first quote.
  - Wheat is shown on the back and explained: "from 1909 to 1958, two ears of wheat framed the back of the penny".
  - The obsidian has the user's nickname line: "the Alien Cent".
  - The second quote is replaced with "Coins from significant years have acquired a special resonance."
  - New, near the start: Bretton Woods (July 1944, the dollar tied to gold), its end in 1971 (fiat), and the tie to CENTS: "what a cent is worth, and who decides". The film closes on that coincidence: "Struck in the year the dollar was tied to gold, and now toned the colour of gold: a coincidence no one planned."
- **Concepts:** C55 "Years that carry meaning", plus the 1971 / fiat card. No quotes.
- **Narration:**
  - eee, eleven_v4, `[thoughtfully] [calm]`.
  - Take 2 (generation 9xmBpcUZpl6Cn3Lqqzfi, 106.08 s, 314 words) is used.
  - Its scribe_v1 transcript equals `audio/tts_text.txt`.
  - The v1 files are in `archive/`.
- **Audio:** `audio/build_vo.py` inserts 21 holds and pads 6.5 s, giving `vo.wav` of 128.08 s.
  - Five holds fell back to quiet runs: light., Gold., later., Cent. and the third gold.
  - Each fallback cut point was checked against the waveform (each is below -60 dB).
  - Note: "Cent" in "the Alien Cent" is spoken softly. The voice trails off.
- **Archival photo:** Opening of the Bretton Woods Conference, July 1944.
  - US National Archives, RG 208, public domain (US government work).
  - It is 706 px wide, so it is shown at its own size on a Plate, never upscaled.
- **Captions:** the SPOKEN table gains 1971, 44, 1909, 1958, 208 and US. Control: "fleck" → "chip" was refused.

## v3 (2026-11-03): "Cent #1264 & Bretton Woods"

- **Script:** the user's edits of v0.3 (`/mnt/project-files/single-cent-series/1264/1264_proposal_v0.4.md`).
  - Opens on the value gap from the project description.
  - Then Bretton Woods, 1971, the user's lines on materiality, and the Glickstein quote (Spike, 13 May 2026).
  - Then the year, the traits, and the comparison: "Two very different histories within one history."
- **Narration:**
  - eee, eleven_v4. Take 2 is used: generation GFwdjN6uXRfOplUbKXQ1, 170.19 s, 459 words.
  - The scribe transcript equals `audio/tts_text.txt`.
  - 24 holds give 192.4 s of audio. Two of them fell back to quiet runs: "worth." (below -60 dB) and "dominant." (the soft tail of the word, about -48 dB).
- **Code:** `CentLook` takes an optional `title`. It may run to two lines, set at 68 px (`pre-line`), so it and the inscription line clear the coin on the opening card.
- **Asset:** a14, the pour footage. It is registered from the objecthood film, shown at 560 px or less, and never looped.

## v4 (2026-11-03): the user's three rounds of notes (14:14Z, 15:28Z, 15:50Z)

- **Opening card:** "Cent #1264" over "& Bretton Woods" (copper), the Story time pill under it, then the coin, and the inscription number under the coin (`CentLook` `title`, now a 64 px `TitleBand`; the coin drops 60 px).
- **Script:** the user's new two-sentence opening ("The story of the value discrepancy…"). The Full Gold sentence is out. Nixon's own line is in, as heard in his clip.
- **Narration:** eee, eleven_v4, `[thoughtfully] [calm]`. Take 2 (generation sIGtXpwnwKLpdn6YErEv, 164.99 s) is used; its scribe transcript equals `audio/tts_text.txt` (460 words). 23 holds plus the Nixon clip give 195.98 s. Five holds fell back to quiet runs; every edit point measures -85 dB or quieter over ±30 ms.
- **Nixon with sound:** `build_vo.py` has a `CLIPS` list. The clip's audio (4.116 s, turned down 17.5 dB from -9.1 LUFS) goes in at the pause after "dollars for gold." and its 13 scribe words go into the alignment, so the line is captioned. `s05a_nixon` starts on the clip's first sample (`after_phrase` "dollars for gold." + 0.25) and ends when the clip ends, so it never loops.
- **1971:** date card, Nixon, the NYT front page, then the Cent under "fiat" and "Dislocating". The three charts run through "wide-ranging effects, not only on wealth distribution and social equity" (holds after "effects," and "equity,").
- **Minecraft:** clip 1 of the two uploads (the player walks the length of the build; clip 2 only climbs down one corner), muted, under "but on materiality itself." (3.5 s of a 4.68 s clip).
- **Polymarket** under "in economics", **Justin Sun / Comedian** muted under "as well as art".
- **Strange tension:** three items from the cents.gallery media library: C037 (UCCA installation), C036 (the book under CENTS Block 839969 on screen), S0709 (copper futures, copper pasts).
- **#543:** five dissolves, 543 → 1264 → 543 → 1264 → 543 → 1264.
- **Removed:** the pour footage (a14 stays registered, unused) and the Full Gold shot of #4273.
- **Code:** `Plate` draws no caption block when the caption is empty (the gold bars and Minecraft carry none; SafeText refuses an empty string). Captions break before "and digital objecthood" (the cue wrapped to three lines and left the safe area).

**Correction to v4, 2026-11-03.** The v4 render played the **v3** voiceover. `public/vo.wav` was staged at 13:28, before the v4 take was built. The captions came from the v4 alignment, so the voice and the captions disagreed, and the user heard it. The v4 delivery check above read the master and the alignment, never the staged file, so it could not catch this. See LEDGER.md, "Rebuilding a master does not rebuild its staged copy".

## v5 (2026-11-03): the user's notes of 18:04Z

- **Voiceover fixed.** The v4 take is now staged in `public/vo.wav` (md5 equal to the master). An independent scribe transcript of that staged file matches every caption start to within 0.38 s.
- **The cube animation replaces the two UCCA stills.** This is the user's attachment, media library S0719, the Block turning over a grid of Cents. It is a 234 px GIF scaled 3× to 702 px. It runs 9.4 s of its 9.9 s, so it does not loop.
- **Ends at "…that CENTS resides."**, then "Cent #1264, a great Cent." over the closing card.
  - The traits section, from "Among collectors…" to "…all that's come between.", is cut from the same take. `CUTS` sits in `build_vo.py`.
  - The cut text is kept in `archive/held_for_next_video.txt` for another video, as the user asked.
- **Fix:** when a hold and a cut share an edit point, the hold now sorts first. Before the fix, the concat restarted at the cut and put the whole section back: the file came out 187 s instead of 111 s.
- **Credits:** the Traits Atlas line is dropped, since no trait is defined in the film any more.
- **Delivery check (v5 file):** 3337 frames, 111.25 s, decodes clean at −17.6 LUFS. No black ≥0.5 s; the only freeze over 3 s is the credits. The render's audio envelope correlates 1.000 with the staged `public/vo.wav`, against −0.02 for the control, the v3 take.

## v6 (2026-11-03): the user's notes of 18:37Z and 18:40Z

- **Two new passages.** The wording is Claude's; the facts and phrases are the user's.
  - After "Gold was the measure of money.": "Struck in 1944, Cent #1264 is the oldest Cent in the collection with a gold trait, by 12 years." The picture zooms to the gold areas, with rings and the "Oldest Gold" readout.
  - After "…trusted to be worth.": "Significant Obsidian is covering Lincoln's face: in the Atlas's words, a major visual actor with strong darkening, but not yet fully dominant. The unique form of the obsidian on this Cent gives it its nickname: the Alien Cent. This is an object that has become alien to itself." The picture zooms to the obsidian on the front, with marks and readouts.
- **Narration.** The whole script was re-voiced as eee v6 take 2 (generation Sr2Ws1WaY1TQLpSwwFmX). The transcript equals the TTS text. 14 holds plus the Nixon clip give 135.94 s.
- **New pictures, all user-attached.**
  - Desk of pennies (C063) under "The starting point…".
  - CENTS ∞ bitcoin diagram (C018) from "by the system that he created with CENTS".
  - Bubble popping under "materiality itself", then Minecraft.
  - UCCA still C077 in place of copper futures.
- **Timing.** "art." holds 1.0 s, down from 3.0 s. The banana clip is trimmed by 1.5 s at the start (`sun_banana_trim`).
- **Delivery check.**
  - 4078 frames, 135.94 s. It decodes clean at −17.3 LUFS.
  - No black ≥0.5 s. The only freeze over 3 s is the credits.
  - `public/vo.wav` md5 equals the master.
  - The render's audio envelope correlates 1.000 with the staged VO. The control, the v4 take, gives 0.02.
