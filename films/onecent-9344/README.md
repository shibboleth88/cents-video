# One Cent: #9344

An episode of the One Cent series. The series brief is `/mnt/project-files/single-cent-series/BEST_PRACTICES.md`. The script, sources and open points are in `/mnt/project-files/single-cent-series/9344/9344_proposal_v0.1.md` and `9344_proposal_v0.2.md`. The build is copied from `films/onecent-1264`.

## v1 (2026-11-11)

- **Ask.** The user picked #9344 "with the focus on this art context" (series thread, 2026-11-11 00:21Z): Boris Groys (QB-D24), Sol LeWitt via Osborne (QB-D18), concept C29 "Rules instead of taste", and Chang's A18 as his general method only.
- **Cent.** 1974, no mint mark, inscription 65,999,011. Nine of the nineteen Atlas traits: Faceless, Corroded, Orange, Significant Verdigris, Significant Obsidian, Significant Red, Notable Gold, Notable Abraded, Contaminated: Blood (Sep 2026 export).
- **The count, recounted** from `knowledge/data/cents_traits_sep2026.json`, counting the 19 Atlas traits (the export's 18 families plus Wheat, derived from year ≤ 1958; a graded trait counts once; any contamination counts as Contaminated; rare_sats is not a trait):

  | traits | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | Cents | 1 | 0 | 3 | 10 | 50 | 187 | 555 | 1,279 | 2,656 | 5,259 |

  The rows add to 10,000 and the 0 row equals the stories scan's 5,259. Without Wheat, two Cents carry seven, not three (#6991 is a 1948), so "three carry seven" depends on counting all nineteen. Seven: #5575, #6404, #6991. Blood: 17 Cents. The nine traits are known to collectors, so the film states the count and does not present it as news.
- **Concepts.** C29 "Rules instead of taste" (card at "No one chose these marks"); value tie C01 "CENTS is a becoming" (card at "A Cent's worth"). LeWitt and Groys are introduced as lenses ("Through LeWitt's lens"); neither wrote about CENTS and the film never says Chang drew on them. A18 is "of his work in general", dated 2017.
- **Quotes.** check_quotes.py on the exact card text: A18 FOUND (Lehnen's copy; the TCI interview holds the same words), D18 FOUND, D24 FOUND (verified excerpts, 2026-11-04). Control: D24 with "profane" changed to "sacred" gives MISSING.
- **Narration.** eee (pp4OmJ3yyWS9Jyhejh5f) on eleven_v4, `[thoughtfully] [calm]` once at the start, default settings. Flow vqkLiappdi3JAeB5L3mf. Take 2 (generation TlyQSah39QSrgc8v5qz9, 117.2 s) is used.
  - **Word check by recognition, not by echo.** The take was fetched by URL into a prompt-free asset and transcribed with scribe_v1 (`audio/v1_take{1,2}_urlscribe_words.json`). `audio/check_heard.py` (copied from the Dopemind Wall branch, with three folds this script needs: "U C C A" → "ucca", British → American spellings of catalogue, and "besides cent" accepted for "beside cent", printed) found both takes equal to `audio/tts_text.txt`, 317 of 317 tokens. Controls: one word dropped, one swapped (Groys → Gross) and one inserted ("close to the mint state") all fail.
  - The word timings in `audio/v1_take2_words.json` come from the recognised transcript (`check_heard.py --write-alignment`).
- **One line re-voiced.** The script as recorded said "CENTS carried the humblest of coins onto Bitcoin and into the galleries of U C C A Beijing." That puts the coins on Bitcoin; their images were inscribed, and their copper (CENTS Block Copper) went to UCCA (CLAUDE.md, terminology: the penny, the image, the inscription). The new line, voiced alone on the same voice and tags: "CENTS inscribed images of the humblest of coins on Bitcoin, and carried their copper into the galleries of U C C A Beijing." Take 2 of 2 (generation xSGqxEIVaiNqFSI4iQ2G), heard 20 of 20 ("Sense" for "CENTS", printed). `build_vo.py` cuts the old sentence and splices the new one in at the pause after `things."` with 0.8 s lead and 0.4 s tail, 0.7 dB down to match the take (-26.7 against -27.4 LUFS). Checked on the built file: the line's audio starts at 104.78 s; the alignment puts "CENTS" at 104.88.
- **Audio.** `audio/build_vo.py` inserts 18 holds, one cut and one clip, pads 6.5 s, then loudnorm I=-16, TP=-1.5, LRA=11. `vo.wav` is 141.28 s. Every hold found a silencedetect pause (no quiet-run fallbacks). The first hold (1.6 s after "forty-four.") puts the year zoom at frame 161, after where a 150-frame 3DCENTS turn will have settled.
  - **Fixed here, open in #1264:** the clip's words were placed at `c + d0 + lead` with `d0` summing only edits at an earlier time, so a hold at the same pause as a clip, played first, was left out. In #1264 v7 the 1944 line's audio starts at 19.18 s and its alignment says 18.66 s: the captions for that line run about half a second ahead of the voice. This build sums every edit before the clip in concat order. #1264 is not re-cut.
- **Captions.** `captions/build_cues.py` with its own SPOKEN table (#9344, #851, 1974, 2017, 1967, UCCA). 55 cues, text equals `script/voiceover.txt`, audit clean. EXTRA_BREAKS keep phrases whole ("with no mint mark", "struck the same year and close to mint state").
- **New components.**
  - `TraitTally` takes `light`: in the grid, only those traits light, in turn; the others stay dim and need no Cent. One Cent's nine against the Atlas's nineteen.
  - `TraitLadder` (`src/style/traitladder.tsx`): every Cent by how many traits it carries, from most to none. It refuses unless the rows add up to `total`, and a row that shows its Cents must show every one. A superlative is a claim about the set, so the set is on screen.
- **Pictures.** 24 shots. Plates from the cents.gallery media library (cleared): C063 desk, C030 studio, C061 penny rolls, C062 photography setup (under "photographed": the act, not a finished photograph), C008 grid of Cent images (under "inscribed images"), C037 CENTS Block Copper at UCCA (under "carried their copper"), S1140 Traits Lab, S1075 Trait Council, C027 collector cards; and a14, the pour, at 560 px as "Casting CENTS Block Copper". The penny pile (S0949) was staged and dropped: it shows modern pennies, some likely zinc, and would have sat under "ten thousand copper pennies".
- **Trait areas** are my reading of the front (`/mnt/project-files/single-cent-series/9344/9344_zoom_plan_v0.1.jpg`). Blood matches the Atlas examples #2359 and #2755; Obsidian, Red, Gold and Abraded are flagged to the user.
- **3DCENTS.** Not yet exported, so v1 opens and closes on the still photo. When `cent-9344-360-1080x1920-25fps-reel` arrives: retime to 30 fps (`setpts=N/30/TB`), measure the coin on frame 0, add `spin` to s01 and swap s23 for a CentSpin. No anchor moves.
- **Images.** 1050px fronts of #9344 and #851 (template: 1974, no mint mark, Lustrous only) in `public/hires/`; the 17 Blood Cents and the 7-trait Cents at 600px in `public/cents/`. All gitignored; fetched from cents.vision.

Render (from the repo root, after `python3 pipeline/film.py switch onecent-9344`, and check `python3 pipeline/film.py status` shows no DIFFERS):

    npx remotion render src/index.ts VideoCaptioned films/onecent-9344/exports/one-cent-9344_v1_captioned.mp4

In the cloud container, add `--browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`. Restore the root symlinks with `git checkout` before committing.
