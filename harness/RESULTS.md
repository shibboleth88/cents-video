# Reviewer run 1 — results

24 cells: 3 reviewers × 4 cases × 2 versions. 24/24 parseable, 0 malformed.
Blinding enforced structurally: script inline in the prompt, all tools disallowed.
Reviewer prompts use invented examples, not the SKILL.md examples, because those
examples are these corpus cases.

## Scores (against the adjudicated key, thresholds declared first)

| reviewer | recall | precision | arguable | verdict |
|---|---|---|---|---|
| synonym-repetition | 6/6 = 1.00 | 1/2 = 0.50 | 0 | precision not measurable, n=2 |
| dangling-premise   | 3/5 = 0.60 | 0/3 = 0.00 | 0 | not deployable |
| order-causation    | 1/1 = 1.00 | 1/1 = 1.00 | 6/8 | not scoreable |

**None of the three is deployable, and they fail for three different reasons.
That is the useful part: each reason names a different fix.**

1. **synonym-repetition works.** It found the redefinition triple in all six
   scripts that contain it and returned NONE on exactly the one where it was
   cut. Its single false positive is on the oldest script. But the corpus has
   only **two** absent cells for this relation, so 0.50 is an anecdote, not a
   measurement. **Fix the corpus, not the reviewer** — it needs clean drafts.

2. **dangling-premise misses a whole defect class.** It found every instance of
   the unanchored *"The object remained"* and missed both instances of
   *"Each object, initially identical…"* with no set of ten thousand to belong
   to. Backward-pointing words it sees; a **quantifier over a set that was never
   introduced** it does not, although the prompt names that case explicitly.
   It also returned the same instance — *"Yet, here we are"* — on four separate
   scripts, which is why its precision is 0/3. **Fix the prompt.**

3. **order-causation cannot be scored at all.** Six of its eight cells are
   ARGUABLE: the reports are defensible readings that I can neither confirm nor
   refute from the text. A relation with no sharp boundary cannot be a gate, and
   reporting this as a low score would have hidden that. **Fix the definition.**

## Predictions, settled

- **1 — recall 4/4 on the labelled cells: FAILED.** 3/4. `dangling-premise-set`
  was missed. The reading stands as 3/4 rather than being reinterpreted.
- **2 — over-reporting: held in direction, premise void.** The key it was stated
  against was wrong, so the "≥2 of 12" form cannot be settled. 4 false positives
  across 6 decidable absent cells.
- **3 — order-causation worst on precision: held in substance.** It did have the
  largest surface area, and the consequence was unscoreability rather than a low
  precision number.
- **4 — dangling-premise fires on `order-causation-brenner/after`: CONFIRMED**, line 5.

## Two observations about the finished film

Neither is a corpus artefact; both concern lines in the shipped objecthood script.

- *"Yet here we are."* (shipped, line 8) asserts that cents have changed hands
  for thousands of dollars. The draft states the absurdity but never shows the
  fact. I judge this an unsupported assertion rather than a cut premise — hence
  ABSENT in the key — but the reviewer raised it on four scripts independently
  and it is a fair thing to raise. Your call.
- *"Chang initiated an ongoing process of redefinition."* was read as asserting
  intention. It was cut before release, so nothing shipped.

## What the key got wrong, and why it mattered

My first key assumed each case's defect lived only in that case's `before`. The
four cases are successive revisions of **one** script, so a defect persists from
the revision that introduced it to the revision that fixed it — the unanchored
line is in four of eight scripts. Its evidence line numbers were also read off
diff hunks rather than files, so several were wrong.

Scored against that key the result read **22/24 FOUND — catastrophic precision**.
That was the key failing, not the reviewers. The reviewers' disagreement with it
is what exposed it.
