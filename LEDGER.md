# Ledger

Read at the start of every video. Appended when something bites. Kept short on
purpose: a file that grows stops being read.

Rows are promoted to **Failure-shapes** only after a shape has bitten **twice**.
Once-bitten entries wait in Candidates. Nothing here is deleted — a superseded
row moves to `LEDGER_ARCHIVE.md` verbatim in the same edit that supersedes it.

## Failure-shapes

- **A recognised token is not a word.** Free transcription is non-deterministic:
  two runs over the *same* audio produced `.opherRutherford` and then
  `Rhodeford` for the same name. Anything keyed to exact recognised tokens — a
  correction list, an anchor phrase, a burned-in caption — is built on sand.
  *Bitten twice.* **Remedy:** `pipeline/reconcile.py`. The script supplies
  spelling, the audio supplies timing, and a structural divergence is kept as
  spoken and flagged rather than overwritten. Anchors match fuzzily
  (`MATCH_MIN`), keeping the ambiguity guard via a margin against the runner-up.

## Candidates — bitten once

Written as a near-miss identity: the two things are close enough that confusing
them was reasonable.

- **A clean encoder exit is not a correct film.** The previous production went
  black after 3:08 with a successful ffmpeg exit. *Measurement that would catch
  it:* `verify.py` black-tail gate, peak luma over the last 15 frames.

- **A render-time bounds check is not a bounds check.** A 220px number written as
  a raw `<div>` bypassed `SafeText` entirely and overflowed into both side bands;
  the in-render guard reported nothing. *Caught by:* the independent pixel gate
  on the encoded `EssentialOnly` export. *Rule:* components emit text only
  through `SafeText`.

- **A well-formed caption file is not a readable caption.** Every numeric gate
  passed a render whose cues were single words ("witness.", "inscribed.") held
  for 0.37s. *Caught by:* looking at a contact sheet. *Now caught by:*
  `cues.audit()`, controlled against the chunker it replaced.

- **Rounding a duration is not rounding a boundary.** Rounding each shot's
  duration independently drifted cut points by a frame. *Rule:* convert each
  boundary to a frame exactly once; derive durations as differences.

- **A gate reading a stale export measures the previous film.** A failed render
  left an old `essential.mp4` in place and the safe-area gate re-reported its
  result as a pass. *Caught by:* `g_not_stale`.

- **A scan that returns zero is not a scan that found nothing.** My own
  violation-locator read 0 offending frames because its frame-line regex never
  matched, so the threshold branch never ran. *Rule:* assert a floor on frame
  count before believing any count of violations.

- **A transcript that passes the caption gate is not a clean transcript.** The
  malformed token `.opherRutherford` had a normal length and a normal duration,
  so the caption audit passed it straight to the screen. *Caught by:*
  `cues.audit_transcript()`, which looks for merge seams rather than shape.

- **A floor in the wrong place is not a floor.** `align.py` rejected any word
  with `end <= start`, which Whisper emits routinely inside fast phrases; the
  unrepairable condition is *starts going backwards*. A check aimed at the wrong
  invariant blocks good data and still misses the bad kind.

- **A recorded restriction is not an enforced one.** `a01` carries another
  essay's title burned into its lower third. The constraint was written into
  `crop_restrictions`, and the renderer honoured it with an `object-position`
  that *could not* crop vertically — so the wrong title appeared on screen with
  every gate green. **Remedy:** crops are applied in `assets.py stage`, so the
  excluded pixels do not exist in what the renderer can reach, and `check`
  refuses an asset whose restrictions mention burned-in text without a crop rect.

- **A pixel floor is not a quality filter.** The CENTS Block animation came back
  from Medium at 385x338 and was discarded as a thumbnail — 111 frames and 5 MB
  of the film's most important asset. **Remedy:** judge motion assets on
  substance, and record low resolution as a *usage constraint* rather than a
  reason to drop the file.

## Refuted — killed by a measurement, do not re-investigate

- *"The left-band safe-area failure is a mispositioned element."* **Refuted** by
  inset test: moving text regions 24px inside the gate bounds cleared the band
  entirely. It was antialias bleed off glyphs sitting on the boundary.
  (2026-10-03)

## Correct, and looks like a bug

- **`loudnorm`'s `output_i` is not the output's loudness.** It is the filter's
  projection for a second pass. The measured value of the file is `input_i` when
  you re-measure the finished file. Reading `output_i` makes correct audio look
  8 dB wrong.

- **Zero-length words in a Whisper alignment are normal.** Ten of 68 words came
  back with `end == start` inside fast phrases. Benign and repairable; only
  non-monotonic starts are fatal.

- **`visual variety` passing while the film looks monotonous is the gate's real
  limit, not a false negative.** It counts component names. Four shots that are
  typographically identical under three different component names are invisible
  to it, and were caught only by looking. Do not loosen the eye because the gate
  is green.

- **The anchor resolver refusing an ambiguous phrase is the resolver working.**
  "The object persists" occurs twice in the fixture narration. The fix is a
  longer anchor, not a looser matcher.

- **Remotion's `<Loop>` is a `<Sequence>`, and a `<Sequence>` is an absolute
  fill.** The Block animation escaped its plate, covered the canvas and painted
  over the plate's own caption — and the render exited cleanly. Visible only by
  measuring where text appeared in the text-only export. `layout="none"` is
  load-bearing, not tidiness.

## Open — not yet investigated

- Whether burned-in captions plus Instagram's own auto-captions double up.
  Must be checked against the live upload preview.

- **The inherited bottom bound is probably too generous.** `SAFE.bottom = 1535`
  came from measuring the previous organic Reel. Third-party 2026 guidance
  (several independent sources, none official) puts bottom clearance at ~670 px
  — essential content ending near **y = 1250**, not 1535 — because the caption
  and audio rail occupy more than the buttons alone. The right rail (~230 px,
  x < 850) and top (~270 px) agree with what we have.
  *Status: EVIDENCED, NOT SETTLED.* These are blog figures, they disagree with
  each other at the margins, and the production notes warn specifically against
  treating them as spec. **Consequence if true:** `REGIONS.caption`
  (y 1340-1500) sits underneath Instagram's own caption overlay, so burned-in
  captions would be partly covered.
  *Resolution:* post a test Reel and look, or check the upload preview. Do not
  redesign the layout on blog numbers alone.
- Whether the 24px gutter is enough at other device scales.
- Whether `assets.py` should also SOURCE imagery (search, licence, provenance)
  and GENERATE it. Ingest, inspection, rights and staging exist; sourcing is
  manual, and this session has no image-generation tool, so 'generated' assets
  would have to be procedural (code) or come from an external service the user
  has keys for. Do not imply photographic generation is available.
- Whether reconciliation can distinguish a genuine adlib from a recogniser
  hallucination. It currently cannot, and flags both for human judgement. The
  small model invented 9 words on one pass; large-v3-turbo may not.
- Whether `say`-generated scratch timing is close enough to a human read to be
  worth trusting for shot lengths, or only for structure. Measured once at
  158 wpm against a 130–145 target, so it runs ~10% fast.
