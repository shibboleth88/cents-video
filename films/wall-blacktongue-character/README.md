# Collector Wall: blacktongue, the collection's character

An updated episode for blacktongue's Wall, made after the Wall collected Cent
#7476 (user, 2026-11-14). It opens on the overall character of the collection,
not the standard walk-through: every grade of every patina, then traits per
Cent, the range of wear, the 1960s, and blacktongue's own words. It follows the
series brief (`/mnt/project-files/collector-wall/BEST_PRACTICES.md`). The
standard blacktongue episode is `films/wall-blacktongue/` (v1 to v3).

## Sources

- **Data.** The collector snapshot of 2026-11-14
  (`/mnt/project-files/collectors/snapshots/2026-11-14/`). Every claim in the
  narration is measured by `data/character.py`, which writes
  `data/character.json` and refuses when a claim fails. `--control` goes red twice
  (a rival planted with the missing values; ladder cells swapped). Findings and
  the corrections beside them: `/mnt/project-files/collector-wall/blacktongue-character/FINDINGS_2026-11-14.md`.
- **The fifteen values.** The user's list (2026-11-14): verdigris, obsidian,
  desert and red at notable, significant and full; gold at notable and full; and
  orange, which has no grades. blacktongue holds all fifteen with 25 Cents. The
  best other collector holds thirteen (CL7 with 165 Cents and Daidatep with 133
  are two of them). The artist wallet also holds fifteen, with 1,000 Cents, and is
  never counted as a collector.
  - *Correction, 2026-11-14 (draft 3):* draft 2 counted fourteen graded values
    (best other collector twelve) and said "of the eight patinas, only iridescent
    is missing". Iridescent is not a patina (user); that line was cut, and orange
    joined the counted list.
- **Art quote.** Jim Drobnick, "Rutherford Chang. The Record Collector as
  Artist-Curator", *Revue musicale OICRM* 10 no. 1 (June 2023), p. 19, on Chang's
  *We Buy White Albums*, never on CENTS (quote bank QB-B39). The quoted words are
  checked against the verified excerpt by `check_quotes.py --quote`; the control
  ("…surface and colour") is MISSING.
- **blacktongue's words.** The MAKES CENTS interview (@sovrnart on X, 20 Nov 2024)
  and blacktongue's post on #5755 (@blktng on X, 21 Aug 2026), quoted verbatim.

## v1 (2026-11-14)

- **Script.** Draft 3 (`script/voiceover.txt` = `script/voiceover_draft3.txt`),
  21 lines, the user's edits to draft 2 applied. Drafts 1 and 2 are kept beside it.
- **Narration.** eee (`pp4OmJ3yyWS9Jyhejh5f`) on eleven_v4, `[thoughtfully] [calm]`
  once at the head of the prompt (`audio/tts_prompt_v1.txt`, 2,973 characters),
  flow lAv77x1ptbxSG6nUGk7K.
  - Take 2 (`audio/v1_take2.mp3`, 177.95 s, generation CKfMIbKEAX88loCGfqBD) was
    chosen. Take 1 (176.51 s) was heard as "CLS7" where the script says "C L seven".
  - **Words checked by recognition.** Each take was fetched by URL into an asset
    with no prompt and transcribed with scribe_v1 (`audio/v1_take*_urlscribe_words.json`).
    `audio/check_heard.py` (copied from the DOPEMIND film, with the recogniser's
    written conventions folded and each fold printed): take 2, 468 tokens equal;
    take 1 fails at "CLS7". Controls: one word deleted fails; "thirteen" swapped
    for "fourteen" fails. The new checker still passes DOPEMIND v3 (377 tokens).
  - The recogniser spelled Daidatep "DidaTep" (take 2) and "Die2Tepp" (take 1).
    The spelling is accepted from a fixed list. How the voice says the name has
    not been checked by ear.
  - `vo.wav`: take 2, loudnorm I=-16, TP=-1.5, LRA=11 (measures -17.5 LUFS; the
    true-peak ceiling holds it under target, as on DOPEMIND at -17.3), 48 kHz
    mono, padded to 185.24 s.
  - `script/alignment.json` takes its word timings from the recognised transcript
    (`check_heard.py --write-alignment`).
- **Captions.** `captions/build_cues.py` (from the DOPEMIND film) writes 72 cues
  whose text joins to exactly `script/voiceover.txt`, using `script/spoken.json`.
  No cue spans any of the 25 picture cuts; a cut-blind build spans 5 (control).
  `captions/captions.srt` is written from the same cues.
- **Pictures.** 26 shots (`timeline/make_timeline.py`); the cover is gapless from
  0 to 185.24 s. New components in `src/style/character.tsx`: `PatinaLadder`,
  `GradeStrips`, `CentTiers`.
  - `QuoteOver` (`src/style/asknext.tsx`) gains `shrinkTo` and `order:
    "picture-first"`, both optional; other films are unchanged. Under the square
    MAKES card and the Wall picture, the quote was laid out (unseen) under the
    full-size picture, below the essential box, and SafeText refused those
    frames. "picture-first" shrinks the picture in the 14 frames before the cue
    and mounts the quote only at its cue, already in place.
