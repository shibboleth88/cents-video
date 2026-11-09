# What to add next: DOPEMIND's question

**v2 (2026-11-09) is the first film of a new series, "What to add next"** (user, 2026-11-09 18:50Z: "a new kind of video rather than a collector wall feature - it will be a feature about what's available and what's interesting, and we'll do more of these"). The series brief is `/mnt/project-files/what-to-add/BEST_PRACTICES.md`. v1, a themed Collector Wall episode, is described further down. Its files are kept with a `_v1` suffix. The folder keeps its v1 name.

The sibling film is `films/wall-dopemind`, the standard Collector Wall episode (thread "Make Dopemind Collector Wall episode", branch `claude/project-thread-fiom8o`). It covers the Contamination Set and stays off the Discord thread.

## v2: what changed and why

The user asked for four things:

1. **Start with the Discord conversation, using the actual screenshots, zoomed in so they read.**
2. **If Daidatep's Cents are listed, say so.**
3. **Treat the picks as interesting Cents in themselves**, not just as Set completion.
4. **Make this a new kind of video.**

| | v1 | v2 |
|---|---|---|
| Opening | Wall card with the 3DCENTS spin | DOPEMIND's question, the real screenshot, readable on frame 0 |
| Discord | recreated cards | the user's screenshots, read in zoomed sections (`ScreenCrop`) |
| Listings | not mentioned | dated: "On November 9, 2026", the three listed 1971s and all six picks, with no prices |
| Each pick | year, plus what it would add | year and mint (scarcity), traits with grades, contamination, small pools shown whole; then one line on what it would add |
| Chronicle and 1980s Sets (need a 1982 as well) | narrated | dropped: Set completion is no longer the frame |
| Close | "Find all of the Collector Walls" | the cents.vision Lab-to-Market switch |
| Length | 2:08 | 2:47 (30 shots, median 5.2 s; the longest single shot, #8820 under four camera moves, runs 10.6 s) |

## v2: how it was made

- **Listings.**
  - `GET https://cents.vision/api/listings` (an open endpoint), fetched 2026-11-09 18:52Z. The source's own `updatedAt` is 18:51:07Z.
  - Saved as `/mnt/project-files/collectors/snapshots/2026-11-09/listings/listings_redacted.json`, with `priceSats`, `sellerAddress` and `inscriptionId` removed. The timeline refuses if any field name in it contains "price" or "address".
  - Confirmed a second way, on the site's own Market view with On Sale checked:
    - `*1971`: Hits 362, three listed first, then "Not listed".
    - The six numbers: Hits 6.
- **Market captures** (`public/vision/dm_1971_market.jpg`, `dm_six_market.jpg`; copies in `/mnt/project-files/what-to-add/dopemind/`).
  - Playwright at 2x scale.
  - Prices were hidden before capture by matching element text against `/\d+\.\d{3,}/`.
  - **Instrument failure, caught.** The first version matched on the ฿ glyph and hid 0 elements. Its "0 visible prices left" check passed all the same, because the counter used the same failing match. The fixed match hid 249 and 12 elements, and both captures were inspected by eye.
- **Screenshots.**
  - The user's uploads, pre-cropped where needed: centoshi's reply and DOPEMIND's "1971" were cut out of one screenshot above and below the Pepe sticker and the later "Gm".
  - Shown with the new `ScreenCrop` (`src/style/asknext.tsx`). Its camera boxes are in the screenshot's own pixels.
  - With `min_scale`, a zoom that would leave the text too small refuses. The Daidatep shot's second box did refuse, at 1.37x under 1.4. It was re-planned at 1.25, which still sets the screenshot's text taller than the 48 px captions.
  - "Yesterday at 12:53" resolves to 8 November 2026 on screen (epoch rule).
  - centoshi's avatar (uncleared XCOPY art) is framed out.
- **Each Cent** uses the One Cent series' `CentLook`, titled "Cent #n" with the inscription number.
  - Inscription numbers come from the snapshot and must agree with `knowledge/data/cents_traits.csv`.
  - The camera goes to the date and mint mark first. It zooms to a trait only where its place on the photo is certain:
    - #2779's portrait;
    - #8556's contaminated patch;
    - #8820's left rim;
    - #6451's portrait;
    - #6875's abraded side;
    - #6782's right field.
  - #8657's desert and #5888's verdigris are not pinned down on the photos, so the camera pulls back to the whole coin there.
- **Pools.**
  - All 13 Ghost + Full Desert Cents, #2779 ringed.
  - All 28 Cents from 1956, #5888 ringed.
  - Both use `CentScroll`, with the 300 px images from `shibboleth88/sovrn-onchain`.
- **Narration.**
  - eee on eleven_v4, `[thoughtfully] [calm]` on every line, through `make_tts.py` and `spoken.json`. Take 1 of 2 runs 159.9 s, plus tail.
  - **Real recognition check.** Following the sibling thread's method, the pushed take was attached to a fresh ElevenLabs asset by its raw GitHub URL, so it carried no prompt, and transcribed there (`audio/v2_take1_heard.json`). That this transcript is real recognition shows in two ways: it has digits and no direction tags, and it misspells names by sound.
  - `audio/check_heard.py` compares it with `tts_text.txt`: **385 tokens equal**. The comparer was copied from `films/wall-dopemind`, with homophone folds added, and every fold it uses is printed:
    - Numismatist's
    - Sentoshi (twice)
    - Leinen
    - Dydatep
    - "reed" for "read"
  - Two normaliser gaps were found on the way and fixed: "three hundred **and** sixty-two" as one number, and "nineteen-sixties" = 1960s. `--control` drops a word and must fail. It fails.
  - `audio/v2_take1_words.json` is the flow's forced alignment, used only for word timings.
- **Timeline.** `timeline/make_timeline.py` recomputes every narrated figure, listings included, and refuses if one has changed. Four controls each mutate one expectation and refuse:
  - the 1971 count;
  - the listed 1971s;
  - the Ghost + Full Desert pool;
  - a replay badge.

  The replay checks compute the badges added against the baseline. An earlier draft of one check passed whenever its key was missing; it was rewritten before it ran.
- **Registry guard.** A first draft of `ScreenCrop`'s companion was also named `CentLook`. Spread into `REGISTRY` after `ONECENT`, it would have replaced the One Cent `CentLook` in every film, with no error. `components.tsx` now refuses a name exported by two groups. Control: with the duplicate still present, the render refused with `REGISTRY: "CentLook" is exported by both ONECENT and ASKNEXT`. The duplicate was removed, and the film uses the One Cent component.

## v2 claims and their checks (snapshots of 2026-11-09)

| Claim | Check |
|---|---|
| 12 Cents, 1963 to 1981 | replay: count 12, years [1963, 1981] |
| centoshi holds 16 from 1971, more than any other collector | as v1: next best 11; artist wallet (36) excluded |
| On 9 Nov 2026, three of the 362 Cents from 1971 were listed | listings: 1971s listed = #2779, #5298, #8556; merged-new2: 1971 = 362; Market view agrees |
| #2779 Ghost with Full Desert; only 13 are both | traits exactly {ghost, full_desert}; pool 13. Atlas: Ghost = portrait/field separation; Desert = pale toning; Full = dominates the coin |
| #8556 1971-D, contaminated, significant verdigris | merged-new2: D, `contaminated: ["Alien Secretion"]`, significant_verdigris |
| #5298 no visual trait | no trait flags, not contaminated |
| any one adds the 1971 Club badge | replay +1971 (#149; the badge goes by year) adds exactly "1971 1" |
| all six listed on the same day | all six in the listings snapshot; Market view Hits 6 |
| #8657 1965; 90 Cents, fewest of the 1960s; no 1965 has a mint mark; notable desert | merged-new2 |
| #8820 1972, notable verdigris + significant red; 183 significant red; completes a Patina Set | merged-new2; replay +8820 adds "Patina Set" |
| #6451 1980, significant obsidian; 220 | merged-new2 |
| #6875 1967, heavily abraded, 1 of 44; Atlas quote | merged-new2; `films/traits/script/atlas/abraded.txt` |
| #6782 1969-D, notable obsidian + significant verdigris; adds the 1969 Club badge | merged-new2; replay +6782 adds "1969 1" |
| #5888 1956-D, notable verdigris; 28 from 1956, 18 D; first wheat penny | merged-new2; replay +5888 adds "Wheat 1" |

## v2 delivery check (brief §5)

These checks were run on `/mnt/project-files/what-to-add/what-to-add-dopemind_v2_captioned.mp4`.

- **Format and decode.** h264, 1080x1920, 30/1, 5010 frames, 167.0 s. A full decode reports 0 errors.
- **First frame.** The question screenshot and title show from frame 0, at YMAX 255.
  - The previous render opened at YMAX 11, because `ScreenCrop` and its title faded in like any other shot.
  - Both now honour `OpeningShotCtx`, as the One Cent shots do.
  - Last frame: YMAX 13, the credits' fade-out.
- **Black and frozen intervals.** Black is detected at 161.8–162.3 s, the dip between the ask card and the credits. Frozen is detected at 163.3–166.8 s, the credits card holding. A frame inside each was looked at, and both are by design, as in v1.
  - Control: blackdetect finds 0–2 s in a test clip of 2 s black plus 2 s grey.
- **Audio.** It matches `vo.wav`, with a correlation of 1.000 at 5, 60, 115 and 150 s. With the reference offset by 1 s, the control gives between −0.002 and 0.024.
- **Shared copy.** The project-files copy has the same decoded video frames (framemd5) and the same audio (md5) as the render. The SRT is byte-identical to `captions/captions.srt`.
- **Script scan.** 0 hits for forbidden phrasing, prices, marketplaces or addresses. A control with two planted lines gets 2 hits.
- **Contact sheets.** Three frames per shot were looked at, after the start and at each move. That found the faults below, all fixed before this render:
  - The ring around a marked screenshot box had no sides, because the box filled the stage.
  - #8657's mint-mark zoom arrived 0.6 s into its shot.
  - The Lab capture opened with empty space above it.

---

# v1 (kept for the record)

A themed Collector Wall episode, the second of two on DOPEMIND's newly claimed Wall (user, 2026-11-09). The standard episode is `films/wall-dopemind` (thread "Make Dopemind Collector Wall episode", branch `claude/project-thread-fiom8o`). This one is built around DOPEMIND's question in the Numismatists Discord: "What should I add to expand the set? Wondering about the direction for this collection". It goes through centoshi's 1971 hint and Daidatep's six suggested Cents, then asks viewers what they think. The two films were split by agreement: the standard episode leads with the Contamination Set and stays off the Discord thread; this one stays off the Contamination Set.

Follows `docs/collector-wall/BEST_PRACTICES.md`. Reference episodes: `films/wall-scrappyt/`, `films/wall-daidatep/`.

## How it was made

- **Data.** Snapshot `/mnt/project-files/collectors/snapshots/2026-11-09/` (fetched 15:56Z, with fetch log and `replay.json`). 2089 collectors and 40 claimed Walls; DOPEMIND is the new one since 2026-10-27. All 17 Set counts from the replay match `set-counts.php`. `wallets-names.json` was not fetched. `data/wall_board.json` (DOPEMIND) and `data/wall_board_centoshi.json` come from `pipeline/wall_board.py --snapshot`. No wallet address appears anywhere in the film or its data files.
- **What a suggestion would add** was measured with the page's own code, not reimplemented. `data/sim/run_sims.py` moves the Cents onto DOPEMIND's wallet in a copy of `wallet_index_cents.json`, replays `collectors.html` offline (`/mnt/project-files/collectors/replay.js`) and reads back the badges the card would draw. Results are in `data/sim/sims.json`. A second run gave a result identical to the first. The instrument goes both ways: +1971 alone does not draw a Chronicle Set and +1971 +1982 does; +#6451 alone does not draw a 1980s Set and +#6451 +1982 does. The script refuses if a replay fails or the moved Cents do not land.
- **Narration.** "eee" (`pp4OmJ3yyWS9Jyhejh5f`) on eleven_v4, every line prefixed `[thoughtfully] [calm]` (`audio/tts_prompt.txt`). Numbers are spoken through `script/spoken.json` via `audio/make_tts.py`, which refuses a digit that would reach the voice and unused keys. v1 take 1, 128.0 s with tail. `audio/build_vo.py` checks the scribe_v1 transcript, with the tag tokens removed, against `audio/tts_text.txt` (316 words). A control with "patina" changed to "surface" fails.
  - **Caveat on that check.** On these ElevenLabs flows scribe returns the prompt's own text, so the transcript works as forced alignment and is weak evidence of what was actually said. An independent Whisper pass was tried twice and blocked: first the proxy refused Hugging Face's file host, then the model download returned 403. The take was not checked by an independent recogniser. Listen to it.
- **Captions.** `captions/build_cues.py` (pipeline `cues.build` and `audit`): 48 cues, audit clean. It refuses unless the cues join exactly to the script.
- **Timeline.** `timeline/make_timeline.py` recomputes every narrated figure from the snapshot and refuses if one has changed. It writes `timeline/timeline.json` (24 shots).
- **New components** in `src/style/asknext.tsx`, registered in `components.tsx`:
  - `ChatCard`: Discord messages retyped word for word under the claimed Wall name, with no avatars.
  - `GapSlots`: what a Set asks for. A real Cent fills a slot; an empty slot is a dashed ring, and a Cent can drop in on its cue.
  - `YearBars`: a count per year, with one year highlighted.
  - `QuoteOver`: a picture that shrinks as a verbatim quote and its attribution arrive.
  - `AskCard`: the closing question over the options. It refuses when its rows would run into the note.

## Claims and their checks (snapshot 2026-11-09)

| Claim | Check |
|---|---|
| 12 Cents, 1963 to 1981 | replay: count 12, years [1963, 1981] (card: "Dime Club", "Years 1963-1981") |
| Signature #478, 1963 | replay `signature`; merged-new2.json |
| Eight carry a patina: verdigris, obsidian or desert | 8 of the 12 carry a patina; the union of patinas is exactly {verdigris, obsidian, desert}. The card's "Patina count 9" counts patina traits (one Cent carries two) and is not narrated (brief: no user-facing meaning yet) |
| No red patina, no wheat, no 1969, no 1971 | union above; replay `wheat_count`, `count1969`, `count1971` all 0 |
| centoshi holds 16 Cents from 1971, more than any other collector | centoshi's Wall: 16 dated 1971. Every other Wall, wallet groups merged: next best 11. The artist wallet holds 36 and is not a collector (brief §2) |
| 1971 Club badge | the page's filter is named "1971 Club" ("Holds a 1971 CENT"); the card's badge reads "1971 1". Replay +1971 adds exactly that badge |
| With the Wall's 1979, one 1982 short of a Chronicle Set | Chronicle = 1971, 1979, 1982 (page: "A CENT from each of 1971, 1979 and 1982"); the Wall's 1979 is #8741; replay +1971 alone: no Chronicle; +1971 +1982: Chronicle Set |
| #8657 is from 1965; only 90 Cents are from 1965, fewer than any other year of the 1960s | merged-new2.json: 1965 = 90; every other year 1960-1969 is above 90 (lowest 1962, 112). Daidatep's own message gives the same "only 90 1965" |
| #8820, 1972, red patina; with all four base patinas the card would add a Patina Set | merged-new2.json; page: Patina Set = "Notable+ of all 4 base patinas"; replay +#8820 adds "Patina Set" |
| #6451 is from 1980; with the Wall's 1981, one 1982 short of a 1980s Set | the Wall's 1981 is #2064; replay +#6451 alone: no 1980s Set; +#6451 +1982: "1980s Set" |
| #6875, 1967, heavily abraded, one of 44 | 44 Cents carry `heavily_abraded`. Quote: Traits Atlas, Abraded, Intensity Scale, "Heavy: abrasion dominates the read of the coin; broad fields/devices visibly missing metal." (`films/traits/script/atlas/abraded.txt`) |
| #6782, a 1969 from Denver, would add the 1969 Club badge | merged-new2.json 1969-D; replay +#6782 adds "1969 1" (page filter "1969 Club") |
| #5888, a 1956 from Denver, the Wall's first wheat penny | merged-new2.json 1956-D; replay +#5888 adds "Wheat 1" and "Years 1956-1981" |
| Lehnen quote | `knowledge/sources/medium-lehnen/lehnen__reflections-on-mint-years.md` line 94, verbatim. The sentence continues "and redefining money as a purely abstract construct", so the on-screen quote ends in an ellipsis. Lehnen essays cleared by the user (2026-10-27) |
| The three Discord messages | retyped from the user's screenshots (uploads, 2026-11-09). Daidatep's list is shown as he wrote it, including "only 90 1965 in the collection" |
| NYT front page, 16 August 1971 | cleared by the user. The crop of the user's upload removes the browser controls (`public/assets/dopemind/nyt_1971_crop.jpg`, copy in `/mnt/project-files/collector-wall/dopemind/`) |

## Left out on purpose

- **The S-mint gap.** One S-mint Cent would complete a Full Mint Set (replay +S: "Full Mint Set"). Nobody in the Discord thread suggested it, and the film should report suggestions, not give advice.
- **The Contamination Set (3/12).** It is the standard episode's focus.
- **centoshi's pfp.** It includes XCOPY's "Empire Things", which is not cleared.
- **Avatars and screenshots** are not shown. The user was asked on 2026-11-09 how the messages may appear; v1 uses recreated cards, the recommended option, while that question is open.

## Delivery check, v1

See the brief, §5. A first render was rejected before delivery, for two layout faults found by looking at the export:

- The Discord question's card sat empty for 1.7 s (the message entered 51 frames into the shot). The message came in on "Dopemind asked", and it now shows from the start of the shot.
- On the ask card the seventh Cent sat on the note "Tell us what you think". Each option's label was d + gap wide, so four columns never fitted and the options wrapped to three rows.
  - The fix makes each option d wide.
  - `AskCard` now refuses when its rows would reach the note. A control with three columns refused with "3 rows end at y=1422, under the note at 1210".

The checks run on the delivered file are recorded in the PR.

## Open

- Discord messages: recreated cards (v1) or the user's screenshots.
- The film names the same person twice. He is "Martin Lehnen" for the essay quote and "Daidatep" in the Discord, and the two names are not linked on screen.
