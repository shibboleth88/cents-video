# Collector Wall: ScrappyT

Follows `docs/collector-wall/BEST_PRACTICES.md` (the series brief). Reference episodes: `films/wall-blacktongue/`, `films/wall-daidatep/`.

- **Data.** `data/wall_board.json` is the Wall as of 27 Oct 2026. It was built by `pipeline/wall_board.py --snapshot` from a fresh fetch of cents.vision on 2026-10-27 at 16:33-16:34Z (`/mnt/project-files/collectors/snapshots/2026-10-27/`, with fetch log and replay). ScrappyT's record matches the 24 Oct snapshot field for field, except that the site now renders the badge "Patina 51" as "Patina count 51". All 17 Set counts from the replay match `set-counts.php` (generated 2026-10-27T16:33:38Z). No wallet address is included.
- **Narration.** "eee" (`pp4OmJ3yyWS9Jyhejh5f`, eleven_multilingual_v2), v1 take 1, 152.6 s. Transcribed with scribe_v1: equal to `audio/tts_text.txt` word for word (357 words); a control with one word changed does not match. `captions/build_cues.py` refused when "Quarter" was changed to "Dime" in the script.
- **Timeline.** `timeline/make_timeline.py <live|rush|turn> [--clip]` writes `timeline.json`. The first argument is the opening variant (`WallOpener`, `src/style/wallopener.tsx`); `--clip` uses the user's 3DCENTS export of #7139 (`public/3dcents/7139-360-30fps.mp4`) for the signature shot.
- **Images.** 1050px cents.vision fronts in `public/hires/` (gitignored; copies in `/mnt/project-files/collector-wall/highres/`), plus the back of #3824. The date and mint-mark boxes were checked by cropping them on the fronts.

| Claim | Check (27 Oct snapshot) |
|---|---|
| 41 Cents, 1956 to 1982, Quarter Club, two wallets | board build; replay `secondary_wallets` has one entry |
| Signature #7139: 1967, full desert, Ghost | merged-new2.json |
| 13 of the 33 Ghost Cents are full desert | 33 with `ghost`; 13 with `ghost` and `full_desert` (2464, 2779, 3554, 4323, 4561, 5185, 6275, 6712, 7139, 7210, 8013, 8119, 8494) |
| Wheat 1: #3824, 1956, the earliest year | the only Cent on the Wall dated 1958 or earlier |
| 1971 x 3 | 366, 619, 1671 |
| Full x 2 | #7139 full desert, #9258 full red |
| Iridescent x 2 · Ghost x 2 | 2981, 7713 · 7139, 5448 |
| Spectrum Set picks | sig. verdigris #8550, sig. obsidian #8394, full red #9258, full desert #7139, notable gold #2981, orange #9469 |
| One of only 15 collectors with a Spectrum Set | spectrum = 16 Walls, including the artist wallet (Spectrum true) → 15 collectors |
| Chronicle | 366 (1971), 1965 (1979), 372 (1982) |
| Full Mint | 2446 (1974-S), 7713 (1973-D), 7139 (no mark) |
| Contamination Set 4/12 | Special Oddities 372, Obscure Adhesive 1399, Speckles 2387 (also 7168), Alien Secretion 8899 |
| 1970s Set and 1980s Set | every year 1970-1982 present; the row shows one Cent per year |
| Diamond Hands · Mint Keeper x 4 | diamond_hands true · mint_keeper_cents 1671, 2478, 5856, 8899 |
| Grade wording, Ghost and Iridescent definitions | Traits Atlas, as worded in `films/traits/script/voiceover.txt` |

Not covered on purpose: "Patina count 51" (no user-facing meaning yet, per the brief) and the separate "Contaminated … x 1" tags, which the Contamination Set row shows.
