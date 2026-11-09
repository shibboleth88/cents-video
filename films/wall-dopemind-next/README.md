# Collector Wall: DOPEMIND, "What should I add next?"

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
