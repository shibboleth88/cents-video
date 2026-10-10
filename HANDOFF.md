# Handoff — state of play

Version 2 · 10 October 2026. Supersedes
[docs/archive/CENTS_video_agent_handoff_v1_2026-10-03.txt](docs/archive/CENTS_video_agent_handoff_v1_2026-10-03.txt),
which is kept verbatim and is now wrong in one important way: it says "a generic
introduction to CENTS is not the assignment". For film 2 that is exactly the
assignment. Where v1 and this file disagree, this file is right.

Read [CLAUDE.md](CLAUDE.md) for the standing editorial rules. This file is
current state only.

## Two films

**1. `objecthood` — CENTS & digital conceptual art. SHIPPED.**
18 shots, 140.69 s, rendered to `films/objecthood/exports/captioned.mp4` and
`clean.mp4`. Recorded in the user's voice. Adapted from the Medium essay.
Audience assumed already to know CENTS. **$0.00 new API spend.**

**2. `introduction` — the best possible introduction to CENTS. SCRIPT STAGE.**
Brief: brief, accurate, compelling, five minutes. Sources are
<https://www.sovrn.art/cents/> plus the measured catalogue. **Not recorded.**

## Where the introduction film stands

Active script is **draft C**: `films/introduction/script/voiceover.txt`,
31 lines, 541 words, **4:54** at the measured pace. Two earlier drafts are kept
for comparison and are not dead:

| draft | words | runtime | shape |
|---|---|---|---|
| A `voiceover_a.txt` | 388 | 3:30 | value discrepancy first, Brenner demoted, thesis close |
| B `voiceover_b.txt` | 353 | 3:11 | opens on one coin, price as hook, image last |
| **C `voiceover.txt`** | **541** | **4:54** | six movements, price reveal at the close |

**Gates: 9 of 11 pass. Controls: 10 of 10 buildable go red.**

Both failures are "nothing to measure", not fidelity violations:

- `on-screen text ledgered` — the timeline is a stub, `"shots": []`. Needs the
  recording. Two controls are **UNBUILT** for the same reason, so those two
  gates are undemonstrated on this film.
- `quotations exact` — draft C contains no direct quotation. I did **not** add
  one to make the gate pass; that would be measuring the scaffolding. If the
  user wants a quotation there is a good candidate: Philip Tinari's line on
  CENTS in Taschen's *On NFTs*, which would also add an institutional voice the
  film lacks. ~20 words, taking the film to about 5:05.

### Correction

I reported this as **10/11** in conversation and in the commit message for
`7d551c1`. It is **9/11**. The commit message is wrong and is left standing
with this correction beside it.

## What is measured, and where

- 42 narration sentences, all mapped to claims; all 42 spans resolve in
  `essay.txt`.
- **28 of 42 claims are time-varying** and each declares `epoch` (the moment it
  describes) and `as_of` (when its source was written or measured). Two-thirds
  of the film is dated material.
- `essay.txt` is the sources of record: 11 blocks, each naming provenance and
  epoch. Block [10] is the epoch convention. Block [11] records three
  descriptions that exist only in the assets, not in any written source.
- The catalogue figures were measured from `metadata.json` on 2026-10-08; the
  market figures observed in the interface on 2026-10-06.

## Next, in order

1. **Record draft C.** Everything downstream is blocked on it: phrase anchors
   (`at_phrase` / `after_phrase`) resolve against word-level alignment, so no
   timeline, no captions, no on-screen gate without the user's voice.
2. **Rebuild the shot plan.** `films/introduction/timeline/shot_plan.json` is
   marked `_STALE`: it is keyed to draft A's 24 lines and C has 31. The asset
   choices, crop compliance and pair-claims in it are still valid and worth
   porting. 26 entries; 19 supported, 4 with no asset, 3 flagged.
3. **Build the timeline** from the plan plus the alignment, then captions,
   render, shot review.

## Known open items

- **`FAL_KEY` still needs rotating.** I exposed it by printing
  `~/.bash_profile`. The user must rotate it at fal.ai/dashboard/keys. Not done
  as of this handoff.
- **The epoch gate fails on the shipped objecthood film** (10/11). Its ledger
  predates the gate and declares no epochs. The gate is right and the old
  ledger is incomplete; this is a real backlog item, not a false alarm. Nothing
  about the released film changes.
- **Assets with no coverage** for four lines of C: the Beatles records, the
  exhibition venues, a photograph of the finished physical block, and a 1943
  steel cent. Typographic plates are specified as fallbacks.
- **The Brenner superlative** ("the most reproduced artwork on Earth") is
  sourced to the project's own text, dated and attributed in narration, and is
  a claim about a set nobody can count. Flagged for the author, not resolved.
- **Two optional builds** that would earn their place: a 10,000-cent mosaic for
  the scale line, and a mint-year histogram for the "edges nobody chose"
  movement, where the current `g01` pairing is the weakest in the plan.

## The review harness — what it found

`harness/` holds a labeled defect corpus built from this repo's own script
history, and three relational reviewers run headlessly via `claude -p` with all
tools disallowed so they cannot read the commit message naming the answer.
Full write-up in [harness/RESULTS.md](harness/RESULTS.md).

Live result, run 4, 99 reviews, majority vote over outcomes:

| reviewer | recall | precision | stability | per-rep detection |
|---|---|---|---|---|
| synonym-repetition | 6/6 | 5/5 | 9/11 | **18/18** |
| dangling-premise | 4/5 | 5/6 | 7/11 | 12/15 |
| invented-motive | 1/7 | 3/4 | 8/11 | 5/21 |

**None is deployable.** All three fail the stability threshold declared before
the run (0.90 unanimous). `synonym-repetition` never misses — 18 of 18 reps —
and both its flips are false positives on clean drafts, so it is the one
plausibly deployable at five reps with no prompt change. `invented-motive`
detects its instance a quarter of the time: a detection failure that voting
cannot fix.

Obvious next step: `--reps 5`, about twelve minutes of wall clock, no new
design. `runs/run2-CONTAMINATED` is quarantined — two runners wrote into one
directory — but its records are individually valid and gave the free stability
comparison.

## Traps that cost time this session

Each of these produced a confident wrong number before it was caught. Full
entries in [LEDGER.md](LEDGER.md).

- **A wrong key reads as a failing subject.** Reviewer scores read 22/24 FOUND,
  "precision collapse". The reviewers were fine; the key was built from commit
  messages and diff hunks. Re-derive a key from the primary artefact before
  concluding the subject is broken.
- **Two runs in one output directory are indistinguishable from one run** when
  records are keyed by subject rather than by run. Caught only because scoring
  the same directory twice gave two different answers.
- **`pgrep -f run_reviews.py` matched its own command line** and reported
  "still running" about itself, forever.
- **A control hardcoded to one subject reads green on the next.** Happened
  three times — `claims[3]`, a glossary pair from the other film, and an epoch
  control that stripped a field from a claim the gate does not inspect. Always
  derive the corruption from the artefact under test.
- **`&` is not `run_in_background`.** A backgrounded run was killed when the
  tool call returned, and separately one survived when I assumed it had died.
- **Shell exit status through a pipe is the last command's.** `st=$?` after
  `msg=$(... | tail -1)` reported all four floors vacuous seconds after one had
  demonstrably fired.
- **I claimed a rewrite would be shorter without counting it.** Draft B's first
  version came out longer than the draft it was meant to compress.

## Repo layout

Per-film directories under `films/<name>/{script,timeline,captions,exports,review}`.
The top-level `script/ timeline/ captions/ exports/ review/` are **symlinks** to
the active film; `film.py switch` moves them. `public/vo.wav` is a staged
**copy**, not a symlink — Remotion 404s on symlinked public files — and
`film.py status` hash-checks it. `shared/assets.json` is the cross-film asset
inventory with rights, crop restrictions and verification dates. `harness/` is
cross-film and deliberately outside the symlinks.
