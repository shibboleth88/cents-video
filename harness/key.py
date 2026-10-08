#!/usr/bin/env python3
"""The adjudicated key: for each (relation, case, version) cell, is the relation
PRESENT, ABSENT, or ARGUABLE?

My first key was wrong and the reviewers' disagreement with it is what exposed
that. Two errors in it:

  1. It assumed each case's defect existed only in that case's `before`. But the
     four cases are successive revisions of ONE script, so a defect persists
     from the revision that introduced it until the revision that fixed it. The
     unanchored "The object remained" line is in four of the eight scripts, not
     one.
  2. Its `evidence_lines_before` were read off the diff hunks, not off the files,
     so several line numbers were simply wrong.

A cell is PRESENT or ABSENT only where I can point at the text. Where the
relation genuinely has no sharp boundary at that adjacency, the cell is ARGUABLE
and is excluded from both recall and precision rather than scored in whichever
direction flatters the reviewer. A relation with too many ARGUABLE cells is not
a reviewer problem - it is a relation that cannot be gated until it is defined
more sharply, and reporting it as a low score would hide that.
"""
P, A, Q = "present", "absent", "arguable"

KEY = {
 # ---- synonym-repetition: the "redefinition" triple -----------------------
 ("synonym-repetition", "order-causation-brenner", "before"):
   (A, [], "The triple does not exist yet. Lines 14-15 (commodification / split) "
           "state related but distinct propositions."),
 ("synonym-repetition", "order-causation-brenner", "after"):
   (P, [15, 17, 18], "Introduced here: 'continually redefined by decentralized consensus', "
                     "'indeterminate and continually redefined', 'an ongoing process of redefinition'."),
 ("synonym-repetition", "dangling-premise-remained", "before"): (P, [15, 17, 18], "Triple intact."),
 ("synonym-repetition", "dangling-premise-remained", "after"):  (P, [16, 17, 18], "Triple intact."),
 ("synonym-repetition", "dangling-premise-set", "before"):      (P, [16, 17, 18], "Triple intact."),
 ("synonym-repetition", "dangling-premise-set", "after"):       (P, [16, 17, 21], "Triple intact, now spread."),
 ("synonym-repetition", "synonym-repetition-redefinition", "before"):
   (P, [16, 17, 22], "The labelled case. Three statements sharing the root 'redefin'."),
 ("synonym-repetition", "synonym-repetition-redefinition", "after"):
   (A, [], "Fixed: two cut, survivors are register-distinct (collectors reading; canon)."),

 # ---- dangling-premise: two defects, each with its own lifetime ------------
 ("dangling-premise", "order-causation-brenner", "before"):
   (P, [7], "'The object remained' - nothing earlier says the penny lost its function."),
 ("dangling-premise", "order-causation-brenner", "after"):   (P, [5], "Same line, still unanchored."),
 ("dangling-premise", "dangling-premise-remained", "before"):
   (P, [5], "The labelled case. Same line, still unanchored."),
 ("dangling-premise", "dangling-premise-remained", "after"):
   (P, [19], "'remained' is anchored now, but 'Each object, initially identical' has no "
             "set of ten thousand to be a member of. Second defect, fixed later at 7fdce22."),
 ("dangling-premise", "dangling-premise-set", "before"):
   (P, [19], "The labelled case: the missing permanent-set premise."),
 ("dangling-premise", "dangling-premise-set", "after"):
   (A, [], "Both anchored. 'Yet, here we are' asserts a state the draft never shows, which is "
           "a real weakness but an unsupported assertion rather than a cut premise."),
 ("dangling-premise", "synonym-repetition-redefinition", "before"): (A, [], "As above."),
 ("dangling-premise", "synonym-repetition-redefinition", "after"):  (A, [], "As above."),

 # ---- order-causation -----------------------------------------------------
 ("order-causation", "order-causation-brenner", "before"):
   (P, [1, 2], "The labelled case. Property then 'This is the readymade Chang chose'."),
 ("order-causation", "order-causation-brenner", "after"):
   (Q, [], "Origin now precedes the property, which was the accepted fix - but 'The readymade "
           "he chose is...' still sits directly before the Brenner fact. No sharp boundary."),
 ("order-causation", "dangling-premise-remained", "before"): (Q, [], "Same adjacency as above."),
 ("order-causation", "dangling-premise-remained", "after"):
   (Q, [], "'Chang initiated an ongoing process of redefinition' after the indeterminacy line "
           "does read as intention. Defensible as a real instance; not sharply decidable."),
 ("order-causation", "dangling-premise-set", "before"):  (Q, [], "Treasury/copper adjacency; not sharply decidable."),
 ("order-causation", "dangling-premise-set", "after"):
   (Q, [], "Half-a-trillion mintings before 'dissolve into worthlessness' does propose volume "
           "as the cause. Defensible; not sharply decidable."),
 ("order-causation", "synonym-repetition-redefinition", "before"): (A, [], "No adjacency manufactures a motive."),
 ("order-causation", "synonym-repetition-redefinition", "after"):  (Q, [], "Collectors/marks adjacency; not sharply decidable."),
}
