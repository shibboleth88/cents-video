# Collector Wall: Daidatep

Follows `docs/collector-wall/BEST_PRACTICES.md` (the series brief). The reference episode is `films/wall-blacktongue/`.

- `data/wall_board.json` is a snapshot of the Wall as of 25 Oct 2026. It was built by `pipeline/wall_board.py` from a fresh fetch of cents.vision on 2026-10-25 at 12:20-12:21Z (`/mnt/project-files/collectors/snapshots/2026-10-25/`, with its own fetch log and replay). Daidatep's record matches the 24 Oct snapshot field for field. No wallet address is included.
- Every shot that moves around the Wall uses `WallBoard`. Date and mint-mark zooms use the 1050px cents.vision fronts in `public/hires/` (gitignored; copies are in `/mnt/project-files/collector-wall/highres/`). Each zoom box was measured on a gridded copy of the front.
- The narration is eo v1 take 1 (eleven_v4), transcribed with scribe_v1. The transcript matches `audio/tts_text.txt` word for word, and a control with one word changed does not match. `captions/build_cues.py` refuses when the script and the spoken words disagree (control: "Dollar" changed to "Dime" was refused).

Every figure was checked against `snapshots/2026-10-25/raw/merged-new2.json` and `set-counts.php` (generated 2026-10-25T12:21:08Z):

| Claim | Check |
|---|---|
| 132 Cents, 1944 to 1982, Dollar Club | the board build |
| Wheat 10 | the Cents minted 1958 or earlier: 1125, 1511, 2165, 3474, 3484, 3640, 4028, 4336, 5250, 9908 |
| The earliest Cent is from 1944 | #4028 |
| 1971 x 4 and 1969 x 4 | 1411, 4754, 4823, 7671 and 2475, 4011, 4121, 8094 |
| #3640 is the only 1955-D Cent | there is one (1955, D) across all 10,000; the page's ONE_OF_ONE_MINT_IDS lists it |
| 1/1 Trait Combo x 4 | 2755, 4336, 9828 and 9908; the signature Cent's unique pair is full desert with significant verdigris |
| Full x 7 | 4 full red, 2 full obsidian, 1 full desert |
| Full Mint Set: an S mint from 1945 | #3474, 1945-S, the Wall's only S mint |
| Three Decades: every year 1960-1982 is present | the year table |
| Full Contamination holders | contaminationFull = 3 = CL7, Daidatep and the artist wallet. That makes Daidatep one of two collectors. |
| Mint Keeper | mint_keeper_cents = [845] |
