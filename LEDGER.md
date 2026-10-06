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

## Episode — 90-second cut (2026-10-06), revisions 1-4

**Script rewritten to a length brief.** The previous voiceover was 299 words
(125-138s). A 90-second film with the 4s credit tail needs ~196 words. The
previous script had no length target recorded anywhere, so nothing was wrong
with it — it answered a different question.

**Failure-shape: an estimate assembled by hand is not a measurement.** Drafting
the cut, I counted words line by line and predicted 185-200. `wc -w` said 236.
Per-line counting under-counts by compounding small errors in the same
direction. Write the file, then measure it.

**Defeated instrument found: `fidelity.py --self-test`'s misquotation control
could never go red.** It corrupted `claims[3]` and asserted `g_quotation_exact`
fails. But `claims[3]` was a *paraphrase* in both the old and new ledger, and
that gate only inspects claims tagged `quotation`, so the control passed every
script it had ever been run against — and a control that passes prints VACUOUS
only because the harness checks for it. This was NOT introduced by the rewrite;
measured against `HEAD:script/claims.json`, the old ledger's `claims[3]` is the
same paraphrase sentence. A fixed index into a ledger is not a reference to a
claim. Fixed to select the first claim tagged `quotation`, and to fail loudly if
no claim carries that tag. 9/10 -> 10/10 controls red.

**Failure-shape: a zero from the wrong key name is not a zero.** My first check
of whether timeline anchors survived the rewrite read `shot["at_phrase"]` and
`shot["id"]` and reported "15 shots; 0 anchors no longer in the script". Both
keys are wrong — the schema is `shot_id`, with anchors nested under `start`,
`end` and inside `props`. Flooring the scan (anchors found must be at least one
per shot) and walking recursively found 52 anchors, of which **21 are now
dangling**. A clean bill of health and a misspelled key render identically.

**Open, not refuted:** the timeline is still cut to the 299-word script. 21
anchors dangle; the render fails rather than mis-cutting, so this is safe but
unfinished. Re-anchoring is the next step, not a known-good state.

**Correct but looks wrong:** the five TRANSFORMATIONS of value are no longer
narrated as a list. They are enacted by the process narration (in circulation ->
removed -> photographed -> destroyed -> inscribed), which is the same five in
order. Only the five NATURES are spoken as a list. This removes rather than
creates the merge risk the distinction ledger was written against.

### Revision 2 — the brief was wrong about what to cut

The first 90s cut kept the project's process (sorted, photographed, melted,
inscribed, released) and spent its budget there, dropping the five
TRANSFORMATIONS, the five NATURES, Brenner and the black hole humor. The
audience is assumed to know the basics already, which inverts the priority: the
process is the part they have.

**The structural saving: the five transformations ARE the process.** In
circulation -> removed -> archivally photographed -> destroyed -> inscribed is
the same sequence of events as sorted/photographed/melted/inscribed/released,
stated as value-events rather than as biography. Narrating the transformations
therefore costs nothing extra — the preliminary information arrives inside the
argument instead of in front of it. This is why both fives, Brenner and the
humor now fit inside 197 words where the first cut could not hold even one of
the fives.

**Attribution hazard recorded as a distinction, not a note.** 'Black hole
humor' is the ESSAYIST'S coinage — the essay says "he brings what I call a
'black hole humor'". The humor is credited to Chang; the phrase is not his.
Putting the phrase on screen beside Chang's name would be the same class of
error as the quotation once credited to Chang in the previous production. The
narration credits him with the humor only, and the phrase appears quoted with
the essay credit.

**The merge risk between the two fives went UP in this revision, not down.**
They are now adjacent in the narration with only "And each is five natures at
once" between them. The distinction ledger previously relied on them being far
apart; now the visual difference — a left-to-right chain versus one object held
open — carries the whole load.

**Open:** 31 of 52 timeline anchors now dangle across 13 of 15 shots (the first
cut dangled 21). The timeline is no longer a near-miss re-anchoring; the shot
list itself wants rebuilding around the new structure. Floored and walked
recursively, so the count is a measurement, not a key-name artefact.

**Not in the voice:** Rutherford Chang's full name. Narration says "Chang"; the
full name is carried by the approved on-screen credit. For an audience that
knows the project this is correct, but it means the film must show that credit.

### Revision 3 — one list of five, and the essay's actual hinge

**One five, not two.** Both lists of five cost 76 of 197 words in revision 2 for
two statements of the same idea at different grains. The TRANSFORMATIONS are
kept in the voice because they are sequential (they carry the project's process
for free) and because they state the essay's subject, value ascription. The
NATURES move to on-screen text, and the closing line - "a thing is
simultaneously itself, not itself, and an interpretation of itself" - already
states their punchline in general form, so nothing is lost but the enumeration.

**The sentence the first two cuts both missed:** "Yet the object remained,
buoyed into physicality by the force of its context." This is the essay's hinge
and it was not in either earlier script. The penny is ALREADY an object held in
being by consensus rather than by intrinsic worth - which is exactly what
blockchain later supplies to digital flows. With that line in, the arc reads as
one claim about objecthood; without it, the film states the arc and asks the
viewer to take it on trust.

**"Conceptual art" moved from setup to payoff.** Both earlier cuts named
conceptual art as 1960s history at the top of the arc. The essay names it in its
CONCLUSION: "Digital objects on blockchain pose a novel form of contemporary
conceptual art". Naming it at the end costs the same words and lands the
article's own title claim as the result rather than the premise.

**Failure-shape: a merge risk moved, it did not go away.** With the two fives in
different channels - transformations in the voice, natures in the frame - no
SCRIPT gate can catch them being merged, because the script now contains only
one of them. Showing the natures while the voice reads the transformations would
read as one annotated list of five. The constraint is on art direction, and
review_shots.py is the only place it can be seen. Recorded in the distinction
ledger with that explicitly stated.

**Open:** 39 of 52 timeline anchors dangle, across 14 of the 15 shots
(measured, not estimated - an earlier draft of this entry said 24, which was a
number I had not re-run after the restructure). The shot list is not a
re-anchoring job; it wants rebuilding around this structure.

### Revision 4 — the order invented an intention

**The failure the gates could not see.** Revision 3 OPENED on "Brenner's Lincoln
is the most reproduced artwork on Earth", which implies Chang chose the penny
because of it. The essay says the opposite about origins: "Rutherford Chang began
this project with a simple value discrepancy." Every sentence in revision 3 was
individually faithful to a cited span, and ten fidelity gates were green. The
infidelity was in the ORDER.

**Failure-shape: a PROPERTY of the work is not a REASON for making it.** Those
are close enough that putting the property first reads as the reason, and no
sentence-level check can see the difference, because no sentence is wrong. The
test is positional: ask what causal reading the position creates. Recorded as a
distinction with verdict kept and `by: user`.

**Why no gate caught it, stated plainly:** `fidelity.py` maps sentences to spans.
It has no representation of narrative order, so claims about causation that arise
from sequence are outside what it can measure. This is a known blind spot now,
not a bug to fix — a gate that judged implied causation would have to understand
the film.

**Frame set for the series.** CENTS is primarily a work about VALUE, and there
will be several films. The essay's other argument - conceptual art, the loss of
objecthood in digital flows, blockchain as this era's objecthood - is now
recorded as a SECOND film's thesis rather than a compressed sub-section of this
one. Revisions 1-3 each carried fragments of both and served neither. The thesis
field in claims.json is now this film's thesis, not the essay's whole claim.

**The ongoing is the emphasis.** Four of the last five lines are about
non-closure: value decoupled into a vessel for social consensus, value and
meaning indeterminate and continually redefined, an ongoing process of
redefinition, objects initially identical bearing the marks of touch and time.
The film ends on the essay's FIRST sentence - "CENTS is a becoming, a gesture
that unfolds continually through the actions of its participants in time" - so
the film earns it rather than asserting it up front.

**Open:** 45 of 52 timeline anchors dangle across 14 of 15 shots.
Measured this revision, not carried over.

### Revision 4a — the first approved addition

The Brenner pair now reads "the readymade he chose is the most reproduced
physical object in history" / "the Lincoln on it, by Victor David Brenner, is
the most reproduced artwork."

**This is the ledger's first `addition`, and it is the author's claim, not the
film's.** The essay says "one of the most common objects in existence" and
reserves the superlative for the IMAGE ("the most reproduced artwork on planet
Earth"). "The most reproduced physical object in history" ranks the penny
against all manufactured objects — bottle caps, fasteners and other mass-produced
items plausibly exceed 500+ billion units. Requested by the essay's author on
2026-10-06, so it is recorded as `kind: addition, approved: true, by: user`
with the faithful alternative written beside it.

**Side effect worth noting: the `additions approved` gate stopped being
vacuous.** It had reported "no additions" on every run of this production. A
gate measuring an empty set passes for the wrong reason — it now has one row to
check, and the self-test control that appends an UNAPPROVED addition still goes
red, so both directions are now exercised.

Victor David Brenner's full name moves into the voice on this line, because this
is the line that credits the most reproduced artwork on Earth to him.
