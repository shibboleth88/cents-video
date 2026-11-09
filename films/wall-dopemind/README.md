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
  - The spoken forms come from `script/spoken.json`. `captions/build_cues.py` reads the same table and refuses unless the cue text joins to exactly `script/voiceover.txt`.
- **Opening.** `WallOpener` showcase with the user's 3DCENTS export of #478.
  - The export is `cent-478-360-1080x1920-25fps-reel.mp4`, retimed frame for frame to 30 fps, plus an alpha webm for the opener. All three files are in `/mnt/project-files/collector-wall/3dcents/`.
  - The hand-off from the card to the spin is seamless. The coin's box was measured either side of the cut: centre (551, 799) → (552, 800), height 490 → 492 px.
- **Images.** 1050 px cents.vision fronts are in `public/hires/` (gitignored; copies in `/mnt/project-files/collector-wall/highres/`). Traits Atlas captures are in `public/vision/` (copies and the capture script in `/mnt/project-files/collector-wall/dopemind/vision/`).

## New in this episode

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

**The zoom areas are my own reading.** For #8741, I took the white flecks for paint and the raised brown deposit by TRUST for obscure adhesive. For #3396, I took the pale runs at the right rim, by the bust and under LIBERTY for the drips and streaks. Each reading compares the photo with the Atlas definitions. The Atlas assigns the traits but not where they sit on the coin.

Not covered on purpose: "Patina count 9" (it has no user-facing meaning yet, per the brief).
