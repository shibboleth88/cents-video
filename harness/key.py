#!/usr/bin/env python3
"""The adjudicated key: for each (relation, case, version) cell, is the relation
PRESENT, ABSENT, or ARGUABLE?

Every line number below was located by grepping the corpus files for the
sentence in question, not read off a diff hunk. The first version of this key
did the latter and scored correct reports as misses.

The four defect cases are successive revisions of ONE script, so a defect
persists from the revision that introduced it until the revision that fixed it.
The unanchored "The object remained" line is in four of eight scripts; the
"Chang initiated" pair is in six.

ARGUABLE is a first-class outcome, excluded from both recall and precision. In
run 1, six of eight order-causation cells were ARGUABLE, which is why that
relation was replaced by the narrower `invented-motive`. Under the narrow
definition every cell is decidable, which is the point of narrowing it.
"""
P, A, Q = "present", "absent", "arguable"

C_BRN, C_REM, C_SET, C_RED = ("order-causation-brenner", "dangling-premise-remained",
                              "dangling-premise-set", "synonym-repetition-redefinition")
CLEAN = ["clean-introduction", "clean-objecthood-shipped", "clean-objecthood-bridge"]

KEY = {}

# ---- dangling-premise ----------------------------------------------------
# Two defects with different lifetimes: the unanchored "The object remained"
# (fixed at 6ccd148) and "Each object, initially identical" with no bounded set
# of ten thousand to belong to (fixed at 7fdce22, which adds "A permanent set").
for cell, v in {
 (C_BRN, "before"): (P, [7],  "'The object remained' - nothing earlier says the penny lost its function."),
 (C_BRN, "after"):  (P, [5],  "Same line, still unanchored."),
 (C_REM, "before"): (P, [5],  "The labelled case. Same line, still unanchored."),
 (C_REM, "after"):  (P, [19], "'remained' anchored at 3-4 now, but 'Each object, initially identical' "
                              "at 19 has no bounded set; 'A permanent set' does not yet exist."),
 (C_SET, "before"): (P, [19], "The labelled case: same missing permanent-set premise."),
 (C_SET, "after"):  (A, [],   "'Each one' at 19 is anchored by 'A permanent set of ten thousand' at 18."),
 (C_RED, "before"): (A, [],   "'Each one' at 19 anchored by 18."),
 (C_RED, "after"):  (A, [],   "'Each one' at 18 anchored by 17."),
}.items(): KEY[("dangling-premise",) + cell] = v
for c in CLEAN: KEY[("dangling-premise", c, "only")] = (A, [], "Adjudicated clean; see corpus label.json.")

# ---- synonym-repetition --------------------------------------------------
# The triple: "continually redefined by decentralized consensus" / "an ongoing
# process of redefinition" / "indeterminate and continually redefined".
for cell, v in {
 (C_BRN, "before"): (A, [], "Triple does not exist yet; only line 13 states redefinition."),
 (C_BRN, "after"):  (P, [15, 17, 18], "Introduced here, all three present."),
 (C_REM, "before"): (P, [15, 17, 18], "Triple intact."),
 (C_REM, "after"):  (P, [16, 17, 18], "Triple intact."),
 (C_SET, "before"): (P, [16, 17, 18], "Triple intact."),
 (C_SET, "after"):  (P, [16, 17, 21], "Triple intact, now spread."),
 (C_RED, "before"): (P, [16, 17, 22], "The labelled case."),
 (C_RED, "after"):  (A, [], "Fixed: two cut; survivors are register-distinct."),
}.items(): KEY[("synonym-repetition",) + cell] = v
for c in CLEAN: KEY[("synonym-repetition", c, "only")] = (A, [], "Adjudicated clean; see corpus label.json.")

# ---- invented-motive -----------------------------------------------------
# Narrow: a property line immediately followed by a line attributing a decision
# to a person, with no stated reason for that decision preceding it. Two
# distinct instances exist in the corpus, and one of them recurs across six
# scripts - recall is therefore not six independent observations.
for cell, v in {
 (C_BRN, "before"): (P, [1, 2],   "Property at 1, 'This is the readymade Rutherford Chang chose' at 2, "
                                  "and the draft states no origin anywhere."),
 (C_BRN, "after"):  (P, [17, 18], "Origin now stated at 1-2, so the Brenner pair is clean. But "
                                  "'Chang initiated an ongoing process of redefinition' at 18 follows "
                                  "the indeterminacy property at 17, and no reason for THAT decision "
                                  "is stated anywhere."),
 (C_REM, "before"): (P, [17, 18], "Same 'Chang initiated' pair."),
 (C_REM, "after"):  (P, [17, 18], "Same pair."),
 (C_SET, "before"): (P, [17, 18], "Same pair."),
 (C_SET, "after"):  (P, [16, 17], "Same pair, one line earlier."),
 (C_RED, "before"): (P, [16, 17], "Same pair."),
 (C_RED, "after"):  (A, [], "'Chang initiated' was cut at 2f9c7cd. No property-then-decision pair remains."),
}.items(): KEY[("invented-motive",) + cell] = v
for c in CLEAN: KEY[("invented-motive", c, "only")] = (A, [], "Adjudicated clean; see corpus label.json.")

if __name__ == "__main__":
    from collections import Counter
    for rel in sorted({k[0] for k in KEY}):
        c = Counter(v[0] for k, v in KEY.items() if k[0] == rel)
        print(f"  {rel:<20} present={c[P]} absent={c[A]} arguable={c[Q]}")
    print(f"  {'TOTAL':<20} {len(KEY)} cells")
