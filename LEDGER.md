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

- **The project's name reads as money.** `g_epochs` matches `\bcents?\b`
  case-insensitively, so "CENTS" in a span and "Cent" (the artwork) in narration
  are both flagged "states a money value". Three becoming-film claims were
  flagged this way (2026-10-24). Answered honestly with an epoch of "not
  time-varying" and an `epoch_note`, not by rewording the script. The detector is
  left as is: an over-trigger costs a note, an under-trigger ships an undated
  price.

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

- **A measurement baseline is not a threshold.** The static-passage gate was
  wrong twice before it was right: frame-to-frame called every tasteful slow
  move static, and sampling 0.5s apart still did. The same passage measures 0.4
  over half a second and 2.0 over two. Both times the instinct was to lower the
  threshold; both times the fault was the baseline. **Rule:** match the interval
  to the question — stillness is perceived over seconds, so compare across
  seconds.

- **Inherited environment is not a sourced profile.** A key plainly present in
  `~/.bash_profile` was plainly invisible to the pipeline, because this shell is
  non-login and non-interactive and never reads that file. Worse, the check that
  "verified" the mechanism was confounded: the PATH entries taken as proof of
  sourcing were inherited from the parent process. **Remedy:** `pipeline/falenv.py`
  looks in the environment first, then parses the single export line from the
  usual profiles. **Rule:** to prove a file is read, test a value that exists
  ONLY in that file — never one the parent could also supply.

- **An aggregate is not the question.** The generated-clip gate first measured
  mean luminance over the whole frame, which conflates the camera moving with
  the object changing: a push-in replaces background with subject and shifts the
  mean by itself, scoring a faithful clip like a retouched one. Now: median
  luminance and saturation of the CENTRAL HALF, clip start versus midpoint.

- **A broken control makes a good gate look vacuous.** The control for that gate
  "brightened" a clip with `eq=brightness=0.18*t/3` — but `eq` evaluates its
  expressions once at init, so the ramp was a constant zero and the control
  tested nothing. The gate was reported VACUOUS when it was fine. Controls need
  their own floor: assert the fault was actually applied before trusting that
  the gate missed it.

- **`-t` after `-i` limits the OUTPUT, and `reverse` buffers the whole input.**
  `-i clip -t 2.5 -vf reverse` yields the LAST 2.5s reversed, not the first.
  Staging meant to drop a clip's drifted tail was splicing that tail back in,
  and the drift gate caught it at 47 levels. Trim inside the filter chain.

- **`-ss 0` on a still image exits 0 and writes nothing.** It consumes the only
  frame while seeking. The comparison that depended on it returned "could not
  compare", which read as a missing file rather than a malformed command.

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

- **A drift slow enough to be tasteful is, per frame, indistinguishable from a
  freeze.** 1.8% of frame over 24 seconds is 0.14 px per second. This is correct
  behaviour that reads as a bug in any frame-differencing instrument, and it is
  why the gate needed a time baseline rather than a looser threshold.

- **Motion that means something beats motion added to pass a gate.** The fix for
  a still passage was a severed link whose dashes drift apart and captions that
  read in word by word — both carry the argument. Raising the drift amount would
  also have passed the gate and said nothing.

- **A 403 is four different facts.** No key, a malformed key, a rejected
  credential, a valid credential on an account with no balance, and an
  unreachable network all surface as "it did not work". The first run showed a
  bare `403 Forbidden` and looked like an authentication failure; the response
  BODY said `User is locked. Reason: Exhausted balance.` — a billing fact with a
  completely different remedy. `check_api.py` now names which of the five it
  found.

- **A gate that does not collect its subjects passes by not checking.** The
  asset gate built its "used" set from `asset_id` and ignored `props.backdrop`,
  so it reported "all used assets are fine" while never looking at either
  generated clip.

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
- Whether a reroll with an explicit anti-retouch negative ("do not brighten, do
  not clean, do not restore, keep the patina and wear") would give a fully
  faithful 5s on a01. Untested; costs $0.35.
- fal rejects an image whose aspect is outside 0.4-2.5, and does NOT bill for
  the rejection. Worth knowing before padding a wide crop.
- Sourcing imagery from the web with licence and provenance is still manual.
  `generate.py` now covers hosted generation, but has never been RUN — there is
  no key, so its request shape, response shape and prices are all unverified.
  Treat its cost estimates as configured numbers, not measurements.
- The static-passage gate passes at exactly 4.0s against a 4.0s limit. That is a
  pass, not a margin. `s07_objecthood` is 24 seconds carrying two circles.
- Whether reconciliation can distinguish a genuine adlib from a recogniser
  hallucination. It currently cannot, and flags both for human judgement. The
  small model invented 9 words on one pass; large-v3-turbo may not.
- Whether `say`-generated scratch timing is close enough to a human read to be
  worth trusting for shot lengths, or only for structure. Measured once at
  158 wpm against a 130–145 target, so it runs ~10% fast.

## Episode — the review harness and the time pass (2026-10-09/10)

### A control that cannot be built is not a control that passed

`corrupt_onscreen()` indexed `tl["shots"][1]`. On the introduction film the
timeline is a stub (`"shots": []`), so it raised `IndexError` **during list
construction** — before any control ran. The entire suite died, and the eight
controls that *were* buildable were never reported. The visible symptom was a
traceback; the invisible one was that a crash and a clean suite both leave you
knowing nothing about the other eight.

Three outcomes now render differently: **RED** (the gate fired), **VACUOUS**
(the gate is blind to the corruption), **UNBUILT** (the subject has nothing for
this control to corrupt yet). UNBUILT prints what was missing and how many shots
were found — the floor — and the summary names the undemonstrated gates
explicitly as *not passing, not failing*. The suite returns non-zero if more
than half its controls are unbuildable, because a suite that could not build
most of its controls has not vouched for itself.

**The pair:** *a crashed control is not a red control, and neither is an
unbuildable one.*

### A control hardcoded to one subject reads green on the next

`corrupt_equation()` appended the fixed sentence *"Attention is recovery."* That
pair is in the **objecthood** film's glossary. Run against the introduction
film's glossary — which holds apart entirely different pairs — the sentence
asserts nothing `g_equations` looks for, so the control passed and the gate
showed **VACUOUS**. Two films, one shared suite, and the control silently
stopped testing anything when the subject changed.

This is the second instance of the identical shape: `corrupt_misquote()` used
`claims[3]`, which had been a quotation when written and was a paraphrase by the
time it mattered. Both were fixed the same way — **derive the corruption from
the artefact under test**, here `gl["must_not_equate"][0]`, with an `Unbuildable`
floor when the list is empty. Verified afterwards on both films: the repaired
control goes RED on each, against each one's own first pair.

**The pair:** *a control written for a subject is not a control derived from it.*
Written twice now, so it is a rule.

*Third instance, 2026-10-24, becoming film.* `corrupt_fabricated_span()` still
used `claims[1]`. On this ledger `claims[1]` is an addition, which `g_spans`
never reads, so the control showed **VACUOUS**. Fixed the same way: the first
claim tagged quotation or paraphrase. Seen VACUOUS on the old code and RED on the
new against becoming, and RED on introduction and objecthood after the fix.

### The key is an instrument, and a wrong key reads as a failing subject

Three reviewer agents were scored against a key built from commit messages. The
first result read **22 of 24 cells FOUND — precision collapse, reviewers
unusable**. The reviewers were fine. The key was wrong in two ways:

- It assumed each case's defect existed only in that case's `before` script. But
  the cases are successive revisions of **one** script, so a defect persists from
  the revision that introduced it until the revision that fixed it. The
  unanchored "The object remained" line is in four of the eight scripts; the key
  claimed one.
- Its evidence line numbers were read off **diff hunks** rather than the files,
  so several pointed at the wrong lines, and a correct report scored as a miss.

Re-adjudicating every cell against the text moved one reviewer from "unusable"
to "works, and the corpus is too small to measure its precision".

**The pair:** *a subject that disagrees with the key is not a failing subject.*
Before concluding that a measured thing is broken, re-derive the key from the
primary artefact. The direction of the error is the tell: a key that makes
everything look broken is as suspect as one that makes everything look clean.

### Three ways a reviewer can fail to be a gate, and they need different fixes

Reported as one number they look like the same problem. They are not:

- **Works, unmeasurable.** `synonym-repetition`: recall 6/6, and NONE on exactly
  the script where the defect was cut. But the corpus holds only two cells where
  the relation is absent, so its precision figure rests on two observations.
  *Fix the corpus.*
- **Blind to a sub-case.** `dangling-premise` caught every backward-pointing word
  without an antecedent and missed every **quantifier over a set never
  introduced**, though the prompt names that case. It also returned one same
  instance on four different scripts. *Fix the prompt.*
- **Not sharply defined.** `order-causation`: six of eight cells adjudicated
  ARGUABLE — defensible readings neither confirmable nor refutable from the text.
  *Fix the definition.* A relation with no sharp boundary cannot be a gate, and a
  low score would have concealed that by making it look like a tuning problem.

An ARGUABLE verdict must therefore be a **first-class outcome of scoring**,
excluded from both recall and precision. Folding it into either direction
flatters or condemns the reviewer arbitrarily and destroys the distinction above.

### Two runs writing to one directory are indistinguishable from one run

A review run was launched twice: once with a shell `&` (which I believed had
been killed) and once properly. Both wrote into `runs/run2`, where records are
keyed by **cell** - relation, case, version - and not by run. So the later
finisher silently overwrote the earlier one, the directory held exactly the
expected 33 files, and nothing looked wrong.

It surfaced only because **scoring the same directory twice gave two different
answers** (1/7 then 3/7 recall). The confirming evidence was timestamps: the
manifest, which the runner writes last, predated 20 of the records.

Two floors, either of which would have caught it: the runner now refuses a tag
whose directory already holds records, and takes a lock file for the duration.

A second instrument failure sat on top of it: the liveness check
`pgrep -f run_reviews.py` **matched its own command line**, since the monitoring
loop contained that string. It reported "still running" about itself, forever,
and I read that as evidence the job was alive.

**The pairs:** *output keyed by subject is not output keyed by run.*
*A process checking for a pattern is not outside the set it searches.*

### Stability is a separate measurement from correctness, and it is the one that fails first

Three reviewers were scored on recall and precision, and one came out clean:
perfect recall, perfect precision, and 11/11 agreement across two independent
samples. Repeating every cell three times instead of two showed that reviewer at
**9/11** - the perfect stability figure was luck, and one extra sample per cell
was enough to refute it.

All three reviewers then failed on stability while two of them had acceptable
recall and precision. A number computed once is not a measurement of a
non-deterministic subject; it is one draw from a distribution nobody looked at.

Corollaries worth keeping:

- **Vote on the outcome, not the verdict.** A cell where three reps all answer
  FOUND but two cite the wrong lines is a majority *wrong place*, not a hit.
  Verdict-only voting scores it a hit, and a control was written for exactly
  this case before any real data was scored.
- **One rep is not unanimity.** A single-rep cell must report stability
  UNMEASURED, never 1.00. Re-scoring an older single-rep run was the test.
- **Pool the reps as well as voting them.** The majority said
  `synonym-repetition` had perfect recall; pooling showed it hit **18 of 18**
  reps and that both its flips were false positives on clean drafts. Same
  reviewer, and the two readings imply different fixes - more reps, not a better
  prompt.
- **Report against the threshold you declared, do not move it.** 0.90-unanimous
  at three reps is a hard bar and all three subjects failed it. The honest note
  is that three reps cannot separate "flips rarely" from "flips often" - which
  is an argument for more reps, not for a lower bar.

**The pair:** *a score is not a measurement until it has been repeated.*

### A status line nobody reads is worse than no status line

`README.md` ended with a Status section saying the pipeline ran only against the
synthetic fixture and that "real asset handling comes next". It had been false
since the objecthood film rendered from real assets — days of work, two films,
and the one paragraph a new reader reaches first still described the scaffold.

No gate covers prose. The fidelity suite checks the script against its sources;
nothing checks whether the repo's own description of itself is true. The fix was
to correct it and leave the correction *in place* rather than swap the text, so
the next reader learns that this file can lie.

**The pair:** *a document that is checked is not a document that is current.*
Prose about state goes stale silently, and the more authoritative its position
the longer it survives.

### I reported a gate count one better than it was

Draft C was wired to the ledger and scored **9/11**. I reported **10/11** in
conversation and wrote 10/11 into the commit message for `7d551c1`. The run
output was on screen and said 9/11; two gates failed and I counted one.

Both failures were "nothing to measure" rather than violations, which is
probably how the slip happened — a failure that is not the subject's fault still
reads as not-a-failure. It is still a failure, and the arithmetic is still
arithmetic.

The commit message stands uncorrected with the correction beside it, in
`HANDOFF.md`. Rewriting it would destroy the more useful artefact.

**The pair:** *a gate that failed for a benign reason is not a gate that passed.*

### A new gate can fail an artefact that already shipped

`g_epochs` was added for the introduction film and immediately failed the
**objecthood** film, 10/11, because that ledger predates the gate and declares
no epochs. Nothing about the released film changed; the gate is right and the
old ledger is incomplete.

This is the correct and desirable behaviour, and it is worth writing down
because the instinct is to scope a new gate to the film it was written for so
the suite stays green. That instinct converts a backlog item into an invisible
exemption. A suite that only ever examines the newest subject cannot tell you
that the older ones were never checked.

**The pair:** *a gate scoped to its motivating case is not a gate.*
