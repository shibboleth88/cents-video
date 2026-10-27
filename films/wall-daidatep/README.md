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

## v2 (user notes, 2026-10-25 13:15Z)

- The card shots show the Wall card alone (`WallBoard show: "card"`), without the opened collection rows. The rows (`show: "grid"`) are used only to single out Cents: the wheats, the 1971s and 1969s, and #845.
- Wheat: #4028 turns over (`CentFlip`, a flat 2D flip) to show the wheat reverse, from the cents.vision back image `pics/backswebp/4028.webp`.
- The Fulls and all five Sets are shown as `CentRow`s, the way blacktongue showed its Full Spectrum Set, with each Cent arriving as it is named. The script now names each Spectrum patina and all twelve contamination types.
- Picks: Spectrum 3867 / 1511 / 1186 / 9908 / 7957 / 857 · Chronicle 7671 / 2755 / 1430 · Full Mint 3474 (1945-S) / 3640 (1955-D) / 4028 (no mark) · Three Decades: the lowest-numbered Cent of each year, 1960 to 1982 · Contamination: one Cent per type, each checked against merged-new2.json.

## v3 (user note, 13:39Z)

- Full Contamination: each Cent appears alone as its type is named (`CentRow solo_until`), then all twelve gather into one row for the holders line, with "1 of 2". This replaces the separate holders shot.

## v4 (user notes, 13:56-13:57Z)

- No Cent rotates: the signature Cent is now still (spin defaults to 0, from the series branch).
- Full Contamination: each Cent is shown large from its 1050px cents.vision front (`Hero.src` in CentRow solo mode, full stage height), then the smaller grid.
- The signature caption is shortened to "Full Desert · Faceless", so it no longer wraps under the captions. Special Oddities is still spoken.

## v5 (user request, 14:2xZ)

- The signature Cent turns again, but now as the 3DCENTS render by sinvalli (cleared for use), not an animation of our own. Source: the user's export `cent-9908-360-1080x1920-25fps-reel.mp4` (one full turn, 150 frames at 25 fps, kept in `/mnt/project-files/collector-wall/3dcents/`).
- Retimed to 30 fps frame for frame (`setpts=N/30/TB`): 150 frames still, each output frame matches its source frame (PSNR 55 dB, against 31.8 dB for the same comparison offset by one frame), no duplicated frames (a plain `fps=30` would have duplicated 30, which judders). The turn is 20% faster: 5 s instead of 6 s, looped across the shot.
- `WallStandout clip`: the clip is scaled so its coin (measured on frame 0: centre 539.5, 959.5, diameter 776 px) matches the 500 px coin of the other shots, and its black background is dropped with a lighten blend on a stage-coloured group. A small credit, "3D render: 3DCENTS by sinvalli", sits under the coin for the whole shot. This film has no end credits, so the on-screen credit is the only one.
- The reverse shows upside down as the coin turns about its vertical axis. That is how a US cent is struck (coin alignment), not a render error.

## v6 (user request, 2026-10-27 18:16Z)

- New series opening: `WallOpener` variant `showcase` (from the ScrappyT episode, PR #14) replaces the plain card. From frame 0 the Wall card shows the signature Cent #9908 turning in its slot (the same 3DCENTS clip as d01), the mosaic Cents and the badges light up one after another, and a thin progress bar runs across the top. At "Its signature Cent" it hands over to the card, which zooms onto the signature as before. The rest of the film is v5 unchanged.
- The showcase's credit line now fades out as the card zooms in (8 frames from the handover): before, it sat on top of the zoomed white card.
