# One Cent: #10000

An episode of the One Cent series, and the trial of the `remotion-video-builder` skill
(NulightJens/jensai-skills, `remotion-video-builder/SKILL.md`, commit 8598b58). The series brief is
`/mnt/project-files/single-cent-series/BEST_PRACTICES.md`. Working files are in
`/mnt/project-files/single-cent-series/10000/`.

**Status: built and voiced; v1 waits only on the user's 3DCENTS export of #10000.** The timeline points
at a labelled flat STAND-IN for the turn (`script/make_standin_spin.py`, "STAND-IN" written on every frame);
no render is delivered while any shot names a STANDIN file. Only the user approves a version.

- **The Cent.** 1976, no mint mark (Philadelphia), inscription 65987682. Traits: Assassin and Notable
  Verdigris, nothing else.
- **Concept.** C22 "An open signifier"; the value tie is inside the Reiss quote ("a vessel for socially
  agreed value").
- **Art literature.** Lippard and Chandler, "The Dematerialization of Art" (1968), QUOTE_BANK v0.7 D37.
- **Counts.** `script/counts.py` recomputes every spoken figure from the raw export and refuses to run
  if its floor (Assassin = 42) fails. The floor was seen red on a copy with one Assassin flag removed.
- **Style guide.** `STYLE-GUIDE.md`, written from the house rules in the skill's Step 1 categories.
- **Voice.** eee (`pp4OmJ3yyWS9Jyhejh5f`), eleven_v4, `[thoughtfully] [calm]`, default settings;
  `audio/tts_text.txt` is the exact text voiced (318 spoken words). Two takes (2,012 credits each),
  123.9 s and 124.1 s. Each was fetched by URL into a prompt-free asset and transcribed by scribe_v1
  (no tags in the transcript, numbers as digits, so it is the audio, not the prompt): `audio/check_heard.py`
  found both equal to the text, 310 of 310 tokens, no folds needed ("Rice" was heard as "Rice");
  `--control` (one word dropped) went red on both. **Take 2 is used**: the two are equal on every check,
  and take 2's transcript reads "not necessarily, rarely, identical" and "signifieds, artistic", where
  take 1's reads "rarely identical" (no comma) and "signifieds - artistic", so take 2's reading is nearer
  the card's aside. That is a recogniser's punctuation, not a listen.
- **Build.** `python3 -I films/onecent-10000/audio/build_vo.py --take 2` (copied from #8820's, which keeps
  the #9344 clip-timing fix) inserts 22 holds, every one in a measured pause (none needed the quiet-run
  fallback; dry run on both takes); loudnorm to -16 LUFS target; 6.5 s end pad: `audio/vo.wav` 145.88 s
  (2:26) and `script/alignment.json`. The year zoom lands at frame 214, after the 150-frame turn. Closing
  card exactly 150 frames (frames 4057 to 4207, `plus` 1.133 s after "a great Cent."). Captions:
  `captions/build_cues.py`, 56 cues, text equal to `script/voiceover.txt`, audit clean.
- **Template.** #1256, 1976, no mint mark, Lustrous only (one of 15 such Cents).
- **Media library.** C001 (the obverse mosaic) is truncated in the library: the file ends on an RST
  marker (`ff d3`) with no JPEG end marker, and its last 0.8% of rows decode as flat grey. Only a 9 x 9
  section from the middle is used (each coin masked onto the stage colour, as `stage_cents.py` does), and
  nothing claims it shows all 10,000 or their order: a correlation test of cells against cents.vision
  fronts could not tell (own-cell scores within the spread of random cells). C047 (Brenner's Lincoln
  plaque) and C048 (the MAKES CENTS cover montage, audio removed) are used unchanged.

## Revision log

- **v0.1 script, 2026-11-21.** `script/10000_proposal_v0.1.md` (copy of the project-files proposal),
  `script/10000_zoom_plan_v0.1.jpg`. Voice text draft: `audio/tts_text_v0.1.txt` (316 spoken words).
- **Script v0.1.1 (voiced), 2026-11-21.** shibboleth approved v0.1 ("please proceed and make the video").
  Two changes before voicing, both reported in the thread: line 9 "Beside Cent #1256, struck the same
  year and close to mint state, the portrait is unmarked." became "Cent #1256 was struck the same year,
  and is close to mint state. Its portrait is unmarked." (the old sentence has no subject, so "the
  portrait" could be heard as #10000's, which carries the spot); the closing line is voiced "Cent number
  ten thousand, a great Cent." as the series closes, where the draft voice text had "Cent ten thousand".
  The three questions in the proposal went unanswered; the defaults stated in the thread were used: only
  spot A (the Assassin spot) is shown as Notable Verdigris; the Lincoln line and the number line stay.
- **Silent rehearsal, 2026-11-21** (brief §7). `audio/make_standin.py` (stand-in alignment, silent
  vo.wav) and a flat stand-in turn; `review_times.py` and `review_stills.mjs` rendered 40 stills. What it
  caught, fixed before any voice credits:
  1. The Reiss credit on one line wrapped to four rows on the end card and SafeText refused the frame
     (the #8820 lesson again). It is now two lines.
  2. The mosaic section at 9 x 11 came out height-limited, each coin about 68 px. Now 9 x 9 at 732 px,
     about 81 px a coin.
  Stills on the real take 2 timing (37 key moments): all render, none refused.
- **Atlas.** `script/atlas_shoot.cjs` (renamed from #8820's `.js`: the repo's package.json makes `.js`
  an ES module, so `require` failed). Assassin entry shot at a 240 px viewport, 3x, summary sentence
  highlighted, cropped to whole lines; control with "bullet" for "projectile" refused. The entry names
  its examples: #1894 Headshot, #6595 Bodyshot, #2755 Neck shot (all three in the 42-Cent pool).
- **Quote reuse, noted.** #478 quoted a longer Reiss passage that contains line 4's two sentences. No
  rule forbids it, and the script with this quote was approved.
