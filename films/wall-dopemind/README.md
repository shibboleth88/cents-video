# Collector Wall: DOPEMIND

The standard episode for DOPEMIND's Wall. It follows the series brief
(`/mnt/project-files/collector-wall/BEST_PRACTICES.md`). Reference episodes are
`films/wall-scrappyt/` and `films/wall-daidatep/`.

A second, themed DOPEMIND episode lives in `films/wall-dopemind-next/` (another
thread). It is built around DOPEMIND's question in the Numismatists Discord about
what to add next. This film leaves that question alone, along with centoshi's 1971
hint and Daidatep's picks. The two films share one data snapshot and the #478 spin.

## Sources

- **Data.** `data/wall_board.json` is the Wall as of 9 Nov 2026.
  - Built with `pipeline/wall_board.py --name "DOPEMIND" --slug dopemind --snapshot /mnt/project-files/collectors/snapshots/2026-11-09`. The sister thread fetched that snapshot on 2026-11-09; its fetch log and replay are in the snapshot folder.
  - The Set counts match `set-counts.php` (generated 2026-11-09T15:56:43Z).
  - No wallet address is included.
- **Focus.** The Wall holds the fewest contaminated Cents (2) of any Wall with a Contamination Set.
  - `data/contamination_sets.py` writes `contamination_sets.json`. It refuses if its Wall count disagrees with `set-counts.php` (59, which includes the artist wallet; 58 collectors without it). It also refuses if the minimum is not held by DOPEMIND alone.
  - `--control` plants a contaminated Cent (#6582) into another Wall, and the script refuses, as it should.
- **Narration.** eee (`pp4OmJ3yyWS9Jyhejh5f`) on eleven_v4, every line prefixed `[thoughtfully] [calm]` (`audio/tts_prompt_v1.txt`).
  - v1 take 1 is 90.75 s of speech; `vo.wav` is 97.0 s, loudness-normalised to -16 LUFS.
  - Transcribed with scribe_v1. With the tag tokens removed, the words equal `audio/tts_text.txt` (247 words).
  - `audio/check_take.py --control` changes one word, and the check fails, as it should.
  - *Correction, 2026-11-09 (v2 work):* the two lines above did not check the audio. scribe on the TTS node returned the node's own prompt; the tags were in the transcript because it was the prompt. The match held by construction (LEDGER: "A transcript identical to the prompt is not evidence of what was said"). v1 has since been checked for real: the take fetched by URL into a prompt-free asset and transcribed (`audio/v1_take1_urlscribe_words.json`), then `audio/check_heard.py`: 233 tokens equal; the control fails.
  - The spoken forms come from `script/spoken.json`. `captions/build_cues.py` reads the same table and refuses unless the cue text joins to exactly `script/voiceover.txt`.
- **Opening.** `WallOpener` showcase with the user's 3DCENTS export of #478.
  - The export is `cent-478-360-1080x1920-25fps-reel.mp4`, retimed frame for frame to 30 fps, plus an alpha webm for the opener. All three files are in `/mnt/project-files/collector-wall/3dcents/`.
  - The hand-off from the card to the spin is seamless. The coin's box was measured either side of the cut: centre (551, 799) → (552, 800), height 490 → 492 px.
- **Images.** 1050 px cents.vision fronts are in `public/hires/` (gitignored; copies in `/mnt/project-files/collector-wall/highres/`). Traits Atlas captures are in `public/vision/` (copies and the capture script in `/mnt/project-files/collector-wall/dopemind/vision/`).

## v3 (2026-11-10)

DOPEMIND's own post about CENTS, which the user asked for on 2026-11-09 ("can we use dopemind's twitter posts about Cents"), was found on 2026-11-10 through the user's twitterapi.io access (record: `/mnt/project-files/collector-wall/dopemind-x/twitterapi/`). v2 is kept as `script/voiceover_v2.txt`, `script/alignment_v2.json`, `timeline/make_timeline_v2.py` and `audio/tts_text_v2.txt`.

- **The post.** https://x.com/dopemind10/status/2119890111471231434, 9 Nov 2026, 20:29 UTC. Verbatim text re-read from the raw API response (`user_last_tweets_dopemind10_2026-11-10.json`). The film uses two of its lines as he wrote them, "CENTS by Rutherford Chang is next level concept art." and "This is performance of value. I study it.". It leaves out the Ordinals line (its wording joins the penny and the inscription, which our narration keeps apart) and the thank-you line.
- **Narration.** One new line after the Bitcoin quote: *On X, on November 9, 2026, DOPEMIND called CENTS "next level concept art", and wrote: "This is performance of value. I study it."* It names DOPEMIND rather than "he", so the line still stands if the quote graphics are cut.
  - Voiced alone (eee, eleven_v4, `[thoughtfully] [calm]`, `audio/tts_prompt_v3.txt`); take 2 (`audio/v3_line_take2.mp3`, generation 9UPj2HFwih1bo6KcObqo) chosen for its pauses at the colon and between the two sentences.
  - Spliced into v2 take 1 at the pause after "history." (cut 130.73 s; 0.19 s and 0.05 s of silence either side, so both gaps are 0.58 s, the gap v2 left after each quote). `vo.wav` is 152.14 s.
  - **Words checked by recognition:** the line was pushed, fetched by URL into an asset with no prompt (0MpLNNislvRfMsRGZBIx) and transcribed (`audio/v3_line_take2_urlscribe_words.json`). The two recognised transcripts are joined at the cut (`audio/v3_spliced_urlscribe_words.json`). `check_heard.py`: 377 tokens equal, with two printed homophones ("where" for "wear", "sense" for "Cents"); the control fails. v1 and v2 still pass after the checker learned "9th" = "ninth" and the "Dope_Mind" spelling.
- **`PostExcerpts`** (`src/style/wallcharts.tsx`): quoted lines of a post, each lit as it is spoken, with the handle and date under the title. Plain type, not a mock-up of X. It refuses excerpts out of spoken order.

## v2 (2026-11-09)

The user asked for more on Speckles, for what else makes #478's combination unique, for the "13 with two types" line to follow "the fewest of any Wall with this Set", and for DOPEMIND's own posts about Cents. v1 is kept as `script/voiceover_v1.txt`, `script/alignment_v1.json`, `timeline/make_timeline_v1.py` and `audio/tts_text_v1.txt`.

- **Narration.** Same voice and direction (`audio/tts_prompt_v2.txt`, 18 lines, 370 words). Take 1 (`audio/v2_take1.mp3`, 135.08 s, generation F865Go0eFrPzQiWH2NzB) was chosen; take 2 is 140.59 s. `vo.wav` is 140.94 s.
  - **Words checked by recognition**, not by the prompt: the take was pushed, fetched by URL into an asset with no prompt (VgbJUlxrx3F9AUiIfBta) and transcribed (`audio/v2_take1_urlscribe_words.json`). `audio/check_heard.py`: 354 tokens equal, with one printed homophone ("where" heard for "wear"). The control (one word deleted) fails.
  - `script/alignment.json` takes its word timings from that recognised transcript (`check_heard.py --write-alignment`), not from the prompt.
  - Two lines now write "10,000" in figures (`script/spoken.json` speaks it "ten thousand"), because the caption renderer turns the word "ten" into "10" and showed "10 thousand". The voice text is byte-identical before and after.
- **Speckles narrowing.** `data/speckles.py` (from the snapshot's `merged-new2.json`) writes `data/speckles.json`. It refuses on a zero count, and refuses unless "no other Cent carries all three" is #478 alone under every reading. `--control` gives #2900 a desert and fails, as it must.
- **DOPEMIND's quotes.** Two graphics from the cents.gallery media library, shared in the CENTS Discord graphics channel: C103 (`IMG_6837.jpg`, catalogued "CENTS quote by Dopemind, meaning, time, value") and C132 (`dopemind_cents_text.png`). The catalogue marks both **"Creator credit to confirm"**, so the attribution waits on the user. X is blocked from this container, so his posts there were not searched. The files are in `public/media/` (gitignored) and `/mnt/project-files/collector-wall/dopemind/media/`.
- **Anchors.** v2 says "number 478" and "number 8741" twice each, so two shot anchors were lengthened. Every phrase in the timeline was checked with a port of the renderer's fuzzy `findPhrase`; the control (the old anchor) is reported ambiguous.

### New in v2

- **`CentFilter`** (`src/style/wallcharts.tsx`): a pool of Cents narrowed step by step. Each step can keep a subset (the rest dim) or regroup the kept Cents into a new layout, with a readout and a caption. It refuses a repeated Cent, a step that keeps a Cent no longer shown, steps out of spoken order, and a numeric readout that differs from the number lit.
- **`WallShot` `title`/`subtitle`** (`src/style/wall.tsx`): a name band above the picture, for a quoted post.
- **`WallShot` move `focus`**: dims the picture outside one area (a passage as it is read), easing from the previous move's focus, while the camera holds `box`. It refuses a focus outside the framed box; it caught one of mine (a focus 3 px above the box).
- The quote framing was measured on the graphics: a scan of the cream text gives each line's rows and columns. The camera box has the picture area's aspect (1000 × 860) and holds the whole text block, so no line is cut at an edge.

## New in v1

- **`zooms` on `WallStandout`** (`src/style/wall.tsx`): a list of zoom steps on the still, each with `at_phrase`, a `box` (or `null` to pull back to the whole coin) and one `mark` or several `marks`. The camera eases from step to step. A single step draws the same picture as the old `zoom` prop. The component throws if a shot sets both `zoom` and `zooms`.
- **`DotColumns`** (`src/style/wallcharts.tsx`): one dot per Wall, stacked by a measured value.
  - It refuses if the bins don't add up to the declared total.
  - The highlighted Wall's dot turns copper. Its name sits in a band reserved above the tallest column, with a leader line down to the dot, so the name never covers other dots.

## Claims

| Claim | Check (9 Nov 2026 snapshot unless stated) |
|---|---|
| Signature #478: 1963, no mint mark | collector's choice on the card; sovrn-onchain `cents/index.json` |
| #478 carries significant obsidian, notable desert, Speckles | merged-new2.json traits for #478; the zoom boxes are from the Cent #478 One Cent episode |
| Notable = clearly visible but local; significant = a major presence | Traits Atlas grade definitions |
| Speckles is one of twelve contamination types; contamination is foreign matter added after minting | Traits Atlas, Contaminated (captured `atlas_contaminated_*.png`) |
| #8741: 1979, paint and obscure adhesive | merged-new2.json; 1979 is one of the three Chronicle Set years (1971, 1979, 1982) |
| 13 of 10,000 Cents carry two contamination types; none carries three | `cents_by_trait.json`, counting `contaminated:` keys only: 1161, 1657, 1924, 6434, 6582, 6823, 7901, 7965, 8465, 8741, 9524, 9786, 9992 |
| The two Cents cover three of twelve types: a Contamination Set | Speckles (#478) + Paint and Obscure Adhesive (#8741); badge "Contamination Set (3/12)" |
| 58 collectors hold a Contamination Set, as of November 2026 | `set-counts.php` contaminationSet = 59, less the artist wallet |
| DOPEMIND holds only two contaminated Cents, the fewest of any Wall with this Set | `contamination_sets.py`: bins 2:1, 3:15, 4:12, 5:10, 6:1, 7:4, 8:4, 9:3, 10:4, 11+:4 (sum 58); the bin "2" is DOPEMIND alone |
| 12 Cents, 1963 to 1981, Dime Club (10 to 24 Cents) | board build; years from `cents/index.json` |
| Two D mint marks: #4599 1963-D, #3010 1974-D; both years also without a mark: #478 1963, #8800 1974 | `cents/index.json` |
| #3396, 1976, white drips and streaks; 82 Cents carry them | `data/white_drips.json` (82, from the snapshot), equal to `cents_by_trait.json` |
| Diamond Hands: held for at least a year, little to no selling | badge on the card; wording from the series brief §6 |
| **v2:** 95 Cents carry Speckles | `data/speckles.py` (Contaminated: Speckles) |
| **v2:** obsidian is on fewer than one in five Cents | 1,757 of 10,000 (17.6%), any grade |
| **v2:** 70 of the 95 carry obsidian | any grade |
| **v2:** only five pair Speckles with significant obsidian; #478 is the only one of them with desert | significant is the exact grade: 478, 2900, 5118, 6666, 8063; only #478 has desert (notable) |
| **v2:** no other Cent of the 10,000 carries all three | 1 under each reading (significant obsidian with desert of any grade; #478's exact grades; obsidian at significant or above). With obsidian of **any** grade it is 6 (478, 7313, 7927, 7965, 8360, 9643), so the on-screen label keeps "significant". #478 is **not** on cents.vision's 1/1 Trait Combo list (38 Cents, unique trait *pairs*), so the film does not call it 1/1 |
| **v2:** "DOPEMIND has also written about CENTS" and the two quotes | media library C103 and C132, catalogued as DOPEMIND's; **creator credit to confirm with the user** |
| **v3:** on 9 November 2026 DOPEMIND posted on X: "CENTS by Rutherford Chang is next level concept art." / "This is performance of value. I study it." | x.com/dopemind10/status/2119890111471231434, 20:29 UTC; verbatim in the raw twitterapi.io response of 2026-11-10 |

**The zoom areas are my own reading.** For #8741, I took the white flecks for paint and the raised brown deposit by TRUST for obscure adhesive. For #3396, I took the pale runs at the right rim, by the bust and under LIBERTY for the drips and streaks. Each reading compares the photo with the Atlas definitions. The Atlas assigns the traits but not where they sit on the coin.

Not covered on purpose: "Patina count 9" (it has no user-facing meaning yet, per the brief).
