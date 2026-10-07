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

### Revision 4b — physical ARTWORK, not physical object

Corrected wording: "The readymade he chose is the most reproduced physical
artwork. More than five hundred billion Lincoln cents, each carrying Victor
David Brenner's portrait."

**The addition disappeared, and that is the point.** "Most reproduced physical
OBJECT" ranked the penny against all manufactured things and exceeded the essay.
"Most reproduced physical ARTWORK" is the essay's own superlative with 'physical'
NARROWING it — the essay claims the image is the most reproduced artwork on
planet Earth outright. So the claim went from `addition / approved: true` back to
`paraphrase`, and the ledger holds no additions again.

**New distinction recorded: the IMAGE vs the PHYSICAL PENNY that carries it.**
The essay's superlative is about the image; this line applies it to the object,
and the word 'physical' is the whole of what licenses that. The glossary already
holds satoshi / inscription / image / penny apart as four things; this is the
same cut one step earlier in the work. Collapsing them would be invisible,
because the essay's own argument runs through the coin count.

**Correct-but-looks-wrong: the `additions approved` gate reads "no additions"
again.** For one revision it had a row to check. It is back to passing over an
empty set, which is the vacuous state noted in 4a — not a regression, but worth
knowing that this gate is only meaningful when the script actually reaches
beyond the essay.

### Revision 4c — a sentence whose antecedent had been cut

"The object remained, buoyed into physicality by the force of its context" did
not make sense in the film, and the user said so. Correctly: in the essay it
closes a decay passage — a cent once bought a newspaper, a streetcar ride, a
postage stamp; by 1979 nothing was sold for a single cent; by 2006 it cost more
than a cent to produce one — and only then "Yet the object remained." I had cut
that passage for word count in revision 1 and kept the conclusion. Nothing in
the film said the penny had lost its function, so "remained" pointed at nothing.

**Failure-shape: a line can survive a cut while its antecedent does not.** The
sentence stayed individually faithful to its span, and the span was real, and
the gate was green. What was missing was not in the sentence; it was the
sentence it answered. A span-mapping gate reads each claim alone, so it cannot
see a dangling reference — the same blind spot as revision 4's implied
intention, in the opposite direction. There, order ADDED a claim nobody made;
here, a cut REMOVED one the remaining line depended on.

**Both halves of the decay are not needed in the voice.** One restored line
("Nothing has been sold for a single cent since before Chang was born") supplies
the antecedent; the 2006 production-cost fact is now an on-screen string, with
the newspaper / streetcar / stamp list available to the frame as well. The
essay's "Yet" comes back to the hinge line now that there is something for it to
point at, which also makes the line an exact quotation again.

**Reordered so the connection cannot be missed:** discrepancy, decay, hinge,
then Brenner. The Brenner pair used to sit between the discrepancy and the
hinge, interrupting the only causal chain in the opening. Moved after it, the
scale of the thing — the most reproduced physical artwork, five hundred billion
of them — now lands immediately before "absurd that a nation's currency should
dissolve into worthlessness", which is the juxtaposition the film wants anyway.

**Paid for by cutting** "The assigned value is decoupled from the object, a
vessel for social consensus." It was the most redundant line in the script: the
mechanism is already in "continually redefined by decentralized consensus" and
the result is already in "its value and meaning are indeterminate and
continually redefined."

### Revision 4d — the same failure again, at the other end

The user could not follow 19 -> 20 -> 21: "Chang initiated an ongoing process of
redefinition" / "Each object, initially identical, bears the marks of touch and
time" / "CENTS is a becoming... through the actions of its participants." Right
again, and it is the SAME shape as 4c, which should have made me look for it:
**a conclusion kept while its premises were cut.**

In the essay the marks of touch and time arrive after the permanent set of
10,000 has become "a system with its own unique logics and rarities", and the
participants of the closing sentence are the collectors "intricately dissect[ing]
this set to determine its internal dynamics". With both of those cut, line 20
was a sentence about wear and line 21 invoked participants the film had never
shown.

**Two restored lines and a reorder, with the length extended on request:**

    Chang initiated an ongoing process of redefinition.
    A permanent set of ten thousand, with its own logics and rarities.
    Each one initially identical, each bearing the marks of touch and time.
    Collectors dissect the set for its internal dynamics.
    Its value and meaning are indeterminate and continually redefined.
    CENTS is a becoming, a gesture that unfolds continually through the
      actions of its participants in time.

Every transition now has a reason: the fifth transformation does not terminate,
so Chang started something ongoing; its form is a fixed finite set with internal
structure; the structure comes from each object's own history; people read those
differences; so value and meaning stay open; so the work is a becoming through
its participants' actions. The closing sentence is now earned by the line
directly above it rather than asserted.

**Also fixed in passing: three consecutive lines said "redefin-".** The
indeterminacy line moved from before the set to after the collectors, where it
concludes something the film has shown. Same words, different position, and the
repetition is gone.

**Failure-shape, now seen twice in two days — write the rule.** *A premise is
not a conclusion.* When a sentence is cut for length, the sentences that pointed
at it do not fail; they go quiet. `fidelity.py` maps each claim to a span
independently and cannot see a reference with nothing behind it, so this class
is green every time. Both instances were found by a reader, not a gate, and both
were at a seam where a passage had been compressed. The practical rule: after
cutting for length, read the SURVIVORS in order and ask of each what it refers
to.

**Length:** 217 words, 23 sentences, 90-100s of speech, 94-104s with credits.
Extended from the 90s brief on request. The brief is now "about 100 seconds".

### Revision 4e — the canon analogy, and a length the brief no longer covers

Added after the collectors line, which is what the analogy is FOR:

    Collectors dissect the set for its internal dynamics.
    Like words that accrue significance on entering the scarce set of
      meanings we call canon.

**Distinction recorded: an ANALOGY to canon is not a claim of entering one.**
The essay compares collectors reading a scarce set to words accruing
significance in a canon. Said slightly differently - "CENTS enters the canon" -
it becomes a claim about the work's art-historical standing that the essay never
makes and the film has no standing to make. On screen, 'canon' must not appear
beside the work's title or a date, which is where that reading would form.

**The first person was dropped, and that is a choice, not an oversight.** The
essay says "it reminds me of the way that...". The narrator here IS the essay's
author, so the hedged first-person form is equally legitimate and is recorded in
the claim beside the chosen wording. "Like" keeps it a comparison; what it loses
is that the comparison was offered as a personal association rather than
asserted.

**Length now exceeds the brief, and the brief has not been restated.** 232 words,
96-107s of speech, 100-111s with credits, mid 106s. The film began as "90
seconds"; it has been lengthened twice on request, first to carry the closing
passage's premises and now to carry the canon analogy. If 90 seconds was a
PLATFORM cap rather than a preference, this no longer meets it, and the three
cheapest cuts back to ~95s are: "Chang initiated an ongoing process of
redefinition" (7), "logics and" (2), and the second absurdity line (13). Written
down because the number in the brief and the number in the file have diverged,
and `script_target` now says so in the file itself rather than only here.

### Revision 4f — repetition that was lexical, not conceptual

Four sentences had stated continual redefinition: the fifth transformation
("continually redefined by decentralized consensus"), "Chang initiated an
ongoing process of redefinition", "its value and meaning are indeterminate and
continually redefined", and the closer ("unfolds continually"). Three of them
used the same root, and the two middle ones were abstract restatements that
added no new register.

**Both abstract restatements cut; the claim is still made four times, in four
different registers.** The mechanism is in the transformation list. The OBJECT
changing is in "now bearing the marks of touch and time". The MEANING changing
is in the collectors and canon lines. The nature of the work is in the closer.
Repetition of an idea across registers is argument; repetition of a sentence in
synonyms is padding, and only the second kind was cut. Both dropped lines are
now on-screen strings, so the frame names once what the voice shows.

**Failure-shape: showing a thing four ways is not saying it four times.** The
instinct when a point matters is to restate it, which is how the script arrived
at four near-identical sentences while believing it was emphasising. The test is
whether each instance adds a register - mechanism, object, reader, work - or
only a synonym.

**The collectors/canon pair was the weakest writing in the script, and the user
said so.** It read:

    Collectors dissect the set for its internal dynamics.
    Like words that accrue significance on entering the scarce set of
      meanings we call canon.

Two faults. "Dissect the set for its internal dynamics" is the essay's phrase
but opaque spoken aloud - it never says what is being determined. And nothing
linked the second sentence to the first, so the canon analogy floated, which is
the dangling-reference shape from 4c and 4d a third time. Now:

    Collectors read the set closely, deciding which Cents matter.
    Words accrue significance the same way, inside the scarce set of
      meanings we call canon.

"Read" is deliberate: the essay's analogy is TEXTUAL, so describing the
collectors' activity with the verb the canon line needs makes the metaphor
cohere rather than arrive from nowhere. "The same way" is the link. "Inside"
replaces the essay's "when they enter", because the CENTS set is already closed
at ten thousand - nothing enters it, and what varies is which members accrue
significance. That is also a sharper reading of the essay's own analogy than the
essay's wording gives, and it keeps the canon distinction intact: significance
accrues to MEMBERS of a scarce set, never to the work's standing.

**Length:** 217 words, 90-100s of speech, 94-104s with credits, mid 99s - back
within sight of the brief, because the cut repetition paid for the canon
passage.

### Revision 4g — the passage after the list had the wrong subject

Replaced:

    A permanent set of ten thousand, with its own logics and rarities.
    Each one initially identical, now bearing the marks of touch and time.
    Collectors read the set closely, deciding which Cents matter.
    Words accrue significance the same way, inside the scarce set of
      meanings we call canon.

with:

    Ten thousand inscriptions, and never any more.
    In a set this fixed, each Cent accrues its own significance.
    The way words do, inside the scarce set of meanings we call canon.

**What was wrong: a digression into collector-market behaviour in a film whose
subject is value ascription.** Four lines on how collectors dissect a set, in a
film that had spent the previous nine on what value is and who assigns it. It
was faithful to the essay and it answered a question the film had not asked.

**Why the passage kept sprawling, which is the useful part.** Line 17 - the
fifth transformation - already delivers the endpoint: value continually
redefined by decentralized consensus. Anything placed after it that is ALSO
about consensus, redefinition or participants restates it. Only three things
were left that are genuinely new after that line: the set is closed, its members
differentiate, and that differentiation is how canons work. The replacement is
exactly those three, and the repetition problem of 4f cannot recur in it.

**Each transition now has a reason, and the last one is grammatical.** The
inscriptions are finite, so the set is closed; a closed set differentiates its
members; that is how canons work; and that accrual, through participants over
time, is what the work IS. "The way words do" is a continuation of the sentence
before it rather than a new sentence, so the analogy cannot float - the failure
of 4c, 4d and 4f was always a reference with nothing behind it, and a
grammatical dependency is the strongest fix available.

**Deliberate vocabulary theft:** "each Cent accrues its own significance" borrows
the verb from the canon sentence that follows. Using the same verb on both sides
is what makes the next line read as a comparison instead of a new thought. The
essay's own word for the differentiation is "its own unique logics and rarities",
recorded as the span.

**Lost, and worth putting in the frame:** "initially identical, now bearing the
marks of touch and time" is the best single image in the essay for the object
still changing. It went with the passage. It is now an on-screen string.

**Length:** 200 words, 83-92s of speech, 87-96s with credits, mid 92s - back
inside the original 90s brief, which the canon passage had pushed to ~106s.

## Episode — the recording (2026-10-06)

321.4s of tape for a 200-word script. Retakes, revised lines and cut lines, as
the recording script invites. 124.78s kept.

### Four instrument failures, found before any of them reached the film

**1. The recogniser looped on real speech and I nearly read it as performance.**
The first transcription emitted "More than 500 billion Lincoln cents were
produced" three times, then "5 inscribed on bitcoin" fourteen times, then bare
"5" for seventeen seconds. The obvious reading is a speaker stuck in retakes.
Measured instead: that seventeen-second stretch is **-25 to -32 dB, i.e. normal
speech**, not silence. So the decoder degenerated over content, and the content
was unknown. `condition_on_previous_text=False` transcribes the same audio
cleanly and reveals the real line - the last take, the only one that reaches "on
the open market". Fixed in `align.py` with the measurement in the comment.

*Failure-shape: a looping instrument and a repeating subject render
identically.* The distinguishing measurement is not in the transcript at all -
it is in the audio energy. Had I trusted the first transcript, the film would
have been cut from a hallucination, and every sentence of it would have looked
plausible.

**2. The initial prompt echoed into the transcript.** `align.py` passed the
script's first 900 characters - prose - as the decoder's initial prompt. Over
audio that says "Rutherford Chang" once, with a 0.7s pause, it produced
"Rutherford. Rutherford Chang began CENTS with a simple value discrepancy."
twice. Reconciliation then reads the echo as an ADLIB and preserves it, because
an unmatched run of words is exactly what an adlib looks like. The prompt's
documented job is spellings, so it now carries proper nouns, numbers and long
technical words, comma separated - nothing for the decoder to finish.

**3. `cues.py` crashed, and the filter it crashed in was measuring the wrong
thing.** In `_merge_short`, the comprehension variable shadowed the cue being
folded away: `[c for c in cand if c[0] + len(_text(c)) ...]` handed `_text` a
`(len, index, side)` tuple. Beyond the crash, the filter never compared what it
claims to - neighbour length plus THIS cue's length. Both fixed.

*The first control I wrote for it was vacuous.* "Yet here we are." is a single
sentence, so it never reached `_merge_short` at all, and the pre-fix code
"passed". A real control needs a one-word SENTENCE beside a normal one. Against
that, pre-fix goes RED and the fix goes green.

**4. A hyphen-split token read as a departure from the script.** Whisper emits
"ready" + "-made"; the comparison sees 2-against-1, which is the shape of a
structural difference, so the artefact was preserved as though spoken and "The
ready -made he chose" reached the captions. A token that is only a hyphen plus
letters is a tokenisation seam, not a word. Healed before comparison, with a
self-test case that goes red against the pre-healing code.

### Take selection

`script/takes.json` records every kept segment, what it says, and which take it
is. Rule: last complete take, which is what the recording script asks for. Cut
points were placed at measured 10ms-RMS silence troughs, not at recogniser word
boundaries - four of the joins are butt-ended in the word timings, including one
where "undefinable" and the next "5" share a timestamp.

The heaviest: transformation five was attempted about twelve times between 165s
and 289s. Only the last reaches "as the objects are traded every day on the open
market".

### The script file is now a transcript

`script/voiceover.txt` holds what was SAID, not what was written. The written
version is archived at `script/archive/voiceover_2026-10-06_as-written.txt`. All
ten fidelity gates pass against the spoken text, and the ledger records what the
performance changed:

- "at the time he made the piece" - the speaker's qualifier, narrowing the
  essay's 2.5x claim rather than extending it.
- "also perhaps the most reproduced physical artwork" - a hedge, so safer than
  the written line.
- "that Victor David Brenner made in 1909" - NOT in the essay. Correct (the
  Lincoln cent was first struck in 1909) and said by the essay's author, so
  recorded as `addition / approved: true / by: user`.
- "melted into a block of copper" and "as the objects are traded every day on
  the open market" - both the essay's own content, said concretely.
- The closer says "through time" where the essay has "in time", so it is now a
  paraphrase rather than a quotation.

### Open

**Length.** 124.78s of voice, ~128.8s with the credit tail. The brief was 90
seconds. The lines were expanded in performance; nothing is wrong with the
recording, but the film is now 2:09 and that is a decision, not a detail.

**The timeline is not re-anchorable.** 48 of 52 anchors dangle across 14 of 15
shots. The shot list was written for a script that no longer exists.

## Episode — the film (2026-10-06)

14 shots, 128.77s, 18/18 release gates green, 6/6 controls red. **No new API
spend: $0.00.** Every image is an asset already on disk or drawn in code.

### Cost, as a design constraint rather than a budget

The brief was to keep generation costs down. The answer was not to generate
cheaply - it was to notice that the recording had made an unused asset usable.
`a06`, Victor David Brenner's bronze Lincoln plaque, was in the inventory marked
*"Not used: the script omits Brenner."* The delivered voiceover names him and
dates the portrait to 1909, so a06 became the right image for that line at no
cost. The other eight assets and three previously-generated motion clips carried
the rest, and six shots are drawn in code.

Prior spend on this production stands at $1.27 and did not move.

### The restriction that code could not honour

`a02` is the artist's vertical composite - cent, ordinal address, raw copper,
block, white circle - and its inventory says **"A figure, not a photograph - do
not crop into it; it loses the sequence."** I used it as a BACKDROP. Backdrop is
`object-fit: cover`, which is a crop. The render succeeded, `assets.py check`
passed, and all eighteen release gates were green on a frame that had cut the
sequence apart and doubled the same picture at two scales.

Only the vision pass found it, by looking.

**This is the a01 failure-shape repeating** - the README already records a crop
restriction that "recorded as advice, was ignored by an object-position that
could not honour it". The lesson had been learned about one asset and written
down as prose about that asset, which is to say it had not been learned. Fixed
properly this time: `no_crop: true` is now a FIELD on a02 and a04, and
`Backdrop` throws on it. Verified as a control - with the old timeline the
renderer now stops at frame 2092 with the reason.

*Failure-shape: a restriction stored where only a person can read it is not a
restriction, it is a note.*

### Three gate failures, and what each one actually meant

**Loudness, -17.22 against -16.0 +/- 1.0.** `loudnorm` was running in one pass,
where it works in dynamic mode and only approaches the target. Now two passes:
measure, then apply a linear gain from the measurements. -16.44 LUFS, -4.46
dBTP. The measurement pass had to run at `-v info` - loudnorm prints its JSON at
info level, so the original script's `-v error` measurement produced nothing and
had been silently useless.

**Static passage at 99.5s.** The chain held one state for 7.6s. Adding a state
did not fix it: a caption change is too few pixels to count as movement. What
fixed it was a drifting backdrop. Then the same gate failed at 74.0s on s09,
where a STILL backdrop at dim 0.88 drifted too little to register - fixed with a
motion asset. The gate is measuring the picture, not the intention, which is
what makes it useful.

**"500 billion" wrapped to two lines** and SafeText cancelled the render. The
fix is the one the README names: a shorter label, never a smaller film. "billion"
moved into the caption and the figure stands alone.

### Length

128.77s. The brief was 90s; the user chose to keep the full performance. The
credits needed four seconds of silence the recording does not contain, so the
cleaned voice is padded by 4.0s before `public/vo.wav` - a gain-and-pad change
that leaves every word time untouched, so the existing alignment stayed valid.

## Episode — audio re-fit and two corrections (2026-10-06)

### The EQ was fitted to a different microphone, and nobody had measured it

`audio_clean.sh` carried a comment saying the EQ was fitted to one microphone
and should be re-fitted for another. It never had been. Measured on this
recording, against its own 630-1000Hz band, the inherited chain was **adding
+4.6dB below 100Hz and cutting -4.3dB at 6-10kHz** - making a phone-recorded,
proximity-heavy voice boomier and duller still.

Re-fitted against the RAW CAPTURE: low end -3.9dB, presence +3.5dB, and SNR in
200Hz-8kHz improved from 30.5dB to 35.0dB. Better signal-to-noise with LESS
denoising, because most of what the old chain was removing at HF was voice and
most of what it was leaving at LF was rumble.

**Two failed predictions before the one that held, and the second failure was
the instructive one.** I predicted the change against the OLD CHAIN's output and
missed twice - the first fit moved twice as far as predicted, the second nearly
as far. The reference was wrong. The old chain is not a baseline of correctness;
it is the thing being corrected. Measured against the raw capture the same fit
lands inside the predicted band on every number.

*Failure-shape: a delta is meaningless without saying what it is a delta FROM,
and the tempting reference is the thing you are replacing.*

Also: an absolute noise reading in quiet frames said noise rose 1.9dB, while SNR
said it improved 4.5dB. Both were true of different quantities. SNR is the one
that answers "is this cleaner", because the files are at different levels.

### A true picture under a true sentence, asserting a third thing

The user caught the fifth transformation sitting over a Plate of the copper
Block, captioned "CENTS Block 839969". Every gate was green and nothing on
screen was false: the caption was true of the image, the image was a real
asset, the narration was faithful to the essay. But "Five, inscribed on
Bitcoin" over a picture of the Block says *the Block was the thing inscribed*,
when in fact **ten thousand cents were inscribed, one per sat**, and the block's
3D model was a separate full-block inscription the film never mentions.

*Failure-shape: the error was in the PAIRING. Image and sentence were each
checkable and each checked out; the claim they make together was asserted by
neither and verified by nothing.* No gate in this pipeline reads a picture
against a sentence - `review_shots.py` pairs them for a human precisely because
nothing else can.

Replaced with a FieldScan of ten thousand units, each inscribed, then repriced.
`a05` is now unused: the narration never mentions the full-block inscription, so
there is no line it can sit under without implying it is the thing inscribed.

### "within emptiness", and the hazard of a script derived from its own transcript

The speaker said the essay's phrase, "resonates within emptiness". Both
recogniser passes heard "with an emptiness" - acoustically all but identical.
Reconciliation could not help, because **this script was transcribed FROM the
recogniser**, so both sources carried the same error and there was nothing to
correct against.

*Failure-shape: a reconciler compares two sources. Deriving one from the other
collapses it into a single source wearing two names, and it goes on reporting
agreement.*

`script/corrections.json` now records the speaker's rulings, applied after
reconciliation. The pipeline previously removed a hand-keyed correction list
because it "could not survive a non-deterministic recogniser" - a sound
objection whose answer is not to omit the list but to make a miss FAIL: every
correction must match exactly once or the run stops.

Its first version silently ate the full stop on "emptiness.", because matching
ignores punctuation and the replacement did not carry it back - and `cues.py`
splits sentences on full stops, so the caption ran on into the next sentence.
The replacement now inherits the trailing punctuation of what it replaces, with
a control over the five shapes that matter.

## Episode — five visuals, a retitle, and a tighter sentence (2026-10-06)

17 shots, 127.24s, 18/18 gates. Still no new API spend; the one new asset is a
screenshot the author supplied.

**The two-second gap inside one sentence.** Whisper's word timings put the pause
between "to his work," and "laughing" at 1.34s. The measured energy says 2.00s -
and two seconds reads as a full stop in a sentence that has none. Cut to 0.46s.
*The timings a recogniser reports are not a measurement of the audio; the audio
is.* The cut was made on the energy, not the transcript.

**Five transformations, five visuals.** The ProcessChain gave the five one
picture between them. Now each gets its own, and the one that is not a picture
is the interesting one: transformation two is a SEVERING, not an object, so it
is the Distinction diagram with the link breaking on "subverted". A thing that
happens should not be drawn as a thing that exists.

**a13, the market screenshot.** Supplied by the author. Ingested with
provenance, cropped to keep coin, id and price together - the restriction
recorded on it is that a crop keeping the coins and losing the prices turns a
market into a contact sheet. Note the policy line this sits beside: the film may
never GENERATE a screenshot of a real interface, and this is a real one, which
is exactly why it is usable.

**Retitled "CENTS principles".** The essay is "CENTS & digital objecthood" and
its objecthood argument is a separate film. The essay keeps its own title in the
credits, so the film is titled for what it covers and the source is still named
accurately.

**Open: transformation three is standing in for itself.** It shows one of
Chang's archival photographs because an archival photograph is what we have. The
author has an image of the photography SETUP, which is the better picture -
process rather than product. Recorded as interim in the shot review rather than
quietly accepted.

**Open: the penultimate-to-final transition.** The film goes from the market to
"CENTS is a becoming" with nothing between. Adding a line needs a recording, so
it is a question for the author, not a fix.

## Episode — the artist's own process footage (2026-10-07)

The author supplied four assets from Rutherford Chang's workspace: his
photography setup, two desk views, and 110s of the CENTS Block being cast.
Ingested as a14-a17 with provenance. Still no API spend; the generated share
fell from 29% to 24% because real material replaced invented material.

**Transformation three was the product standing in for the process.** It showed
one of Chang's archival photographs, because an archival photograph was what we
had. The line is "archivally photographed" - a verb. It now shows the apparatus:
the copy stand, the lit pad with one cent on it, the laptop displaying the
capture, the penny rolls behind. *An image OF the result is not an image of the
act, and the two are close enough to swap without anyone noticing.*

**Transformation four was generated particulate; it is now the actual pour.**
Molten copper tilted from the crucible into the brick mould. For a film about
the objecthood of real things, invented copper standing in for the copper that
was actually melted is the substitution the project's own policy exists to
prevent - and it had passed every gate, because the policy forbids inventing a
picture OF a specific real thing and a generic abstraction is not that. It was
within the rules and still the wrong picture when the right one existed.

The pour was located by measurement, not by scrubbing: frames sampled every few
seconds across 110s put the tilt at ~76s, and a second pass at 1s resolution
fixed it. The clip is 8.0s against a 7.36s shot, so it plays straight and never
loops.

Held at 560px because the source is 480 wide. Small and true beats large and
soft, which is the same rule the Block animation already lives under.

**Open:** the author is recording the bridging line between the market and "CENTS
is a becoming".
