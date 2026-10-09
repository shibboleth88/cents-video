# Predictions for reviewer run 1

Written before any reviewer was run against the corpus. If a prediction fails,
the reading is withdrawn rather than reinterpreted.

The matrix is 3 reviewers x 4 cases x 2 versions = 24 cells. A cell's expected
answer is FOUND where that relation is annotated present, NONE otherwise:
12 cells expect FOUND, 12 expect NONE.

## Predicted

1. **Recall will be high, 4/4 on the own-relation `before` cells.** These are
   the four defects the commit messages name. They are blatant once the relation
   is stated, and the Brenner pair in particular is two adjacent lines.

2. **Precision is where this fails.** A reviewer told to look for one thing,
   handed a draft that does not contain it, will find a weak instance rather
   than return NONE. I predict **at least 2 of the 12 expect-NONE cells come
   back FOUND**, and that the false positives cluster on the `after` scripts of
   the reviewer's own cases, because those scripts still discuss the same
   subject matter in the same vicinity.

3. **The order-causation reviewer will be the worst offender on precision.**
   Every adjacency in a 20-line script can be read as asserting something, so
   the relation has the largest surface area for a plausible-sounding false
   positive.

4. **`dangling-premise` will fire on `order-causation-brenner/after`** (an
   expect-FOUND cell by annotation, since that script still carries the
   unanchored "The object remained" line). If it does not, the annotation is
   wrong, not the reviewer.

## What would falsify the whole approach

If precision on the 12 expect-NONE cells is below ~0.6, these reviewers are not
deployable as gates at all: a reviewer that cries wolf on half of all clean
drafts will be ignored within a week, which is worse than no reviewer. In that
case the finding is about the output contract, not about the relations.

## Known limits of any number computed here

- `other_relations_present` is my own annotation, not independently established.
  Only the own-relation `before` cells are evidenced by a commit message. Scores
  are therefore reported twice: on the 8 commit-evidenced cells, and on all 24.
- The corpus holds defects a human caught. Recall here is recall against
  known-findable problems, and is an upper bound.
- n=4 cases. Nothing here supports a confident percentage; it supports
  "deployable / not deployable / needs a different contract".

---

# Predictions for reviewer run 2

Changes since run 1: `dangling-premise` rewritten as an enumerate-then-judge
sweep with a required `inventory` field and two explicit out-of-scope cases;
`order-causation` replaced by the narrower `invented-motive`; three clean drafts
added. Key re-adjudicated, 33 cells, zero arguable.

1. **dangling-premise recall goes 3/5 -> 5/5.** The misses were both the
   quantifier case, and the sweep now forces every quantifier to be listed with
   its antecedent or `none`. If recall does not improve, the diagnosis was wrong
   and the problem is not that the reviewer skipped the case.
2. **dangling-premise precision goes 0/3 -> at least 4/6.** The sole false
   positive family was *"Yet, here we are"*, now named as out of scope with a
   worked example. Residual risk: it finds a new fixation instead.
3. **invented-motive recall at least 5/7, precision at least 3/4.** Run 1's
   wider reviewer already flagged the `Chang initiated` pair once unprompted, so
   the instance is findable; the narrow definition should make it findable
   consistently.
4. **synonym-repetition is unchanged, so recall should reproduce at 6/6.** Any
   deviation is run-to-run variance in the reviewer, not a prompt effect, and
   would mean single runs cannot be compared at all. Precision now has 5 cells;
   predict at least 4/5, the known false positive being `brenner/before`.
5. **At most 2 malformed reviews.** The new required `inventory` field is the
   risk: a reviewer that omits it is recorded as malformed rather than clean.

## Falsifier for the whole exercise, restated

If `dangling-premise` recall does not improve, prompt-level fixes do not address
blindness to a sub-case, and the honest conclusion is that relational review
needs a different mechanism than a better-written reviewer.
