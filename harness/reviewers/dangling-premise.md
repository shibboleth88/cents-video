# The problem you are looking for: a conclusion whose premise is absent

Scripts get cut for length. When a sentence is removed, the sentences that
depended on it do not break — they go quiet. They still parse, still sound
finished, and still read as true. But what they refer to is no longer in the
piece.

The near-miss to watch for: **a sentence that is still grammatical is not a
sentence that still refers to something.**

## Do this as a sweep, not a search

You will be tempted to read the draft, notice the one line that feels unmoored,
and report it. Do not work that way. A search stops at its first hit, and the
instances that matter most are the ones that *sound* fine — a quantifier over a
set the draft never counted reads perfectly well, which is exactly why it
survives a read-through.

So **enumerate first, judge second.**

**Pass 1 — inventory.** Walk the draft line by line and list *every* expression
that depends on something earlier. Three kinds, and you must look for all three:

- **Backward references**: *it, this, that, those, the object, that assignment* —
  any definite phrase standing in for something named before.
- **Contrasts and continuations**: *yet, but, still, remained, again, instead,
  here we are* — each presupposes a state of affairs to push against.
- **Quantifiers and partitives**: *each, every, all, half, the rest, both, one of
  them, the set* — each presupposes a **bounded collection** that the draft has
  introduced and whose membership is fixed.

For every entry, name the line number that establishes what it points at, or
write `none`. An entry whose antecedent is `none` is a candidate instance.

The quantifier case is the one most often missed, so be deliberate about it.
*Each one initially identical* needs more than a mention of the kind of thing —
it needs a **bounded set with a fixed membership**, because "initially
identical" and "each" are claims about a population. A draft that says "cameras
have shutters" has not introduced the set that "each one, bought the same day"
refers to.

**Pass 2 — report.** Report only the entries whose antecedent is `none`. Each
reported instance must concern a **different** referring expression; if one
unestablished premise makes three lines float, that is one instance, not three.

## Not this relation

Two things look like this problem and are not. Do not report them:

- **An assertion with no evidence shown.** *"It is absurd that a camera should
  sell for thousands. Yet here we are."* — the premise of *here we are* is the
  preceding line, which states it. That the draft never *shows* a sale is a
  weakness, but it is an unsupported claim, not a missing referent. A different
  reviewer handles it.
- **A reliance on general knowledge the audience has.** *The tide* needs no
  introduction. The test is whether the **draft** established the thing, not
  whether it is obvious.

## Invented example of the shape

```
1  Vivian Keller photographed the same stretch of coast for thirty years.
2  Yet the pier remained, propped up by nothing but habit.
3  Each one had faded differently by the end.
```

Line 2: *yet*, *remained* — antecedent `none`. Nothing says the pier was failing.
Line 3: *each one* — antecedent `none`. No bounded set of prints was introduced;
line 1 names an activity, not a collection. Two instances, two referents.

## Output

Use the JSON object from the contract, and add one required top-level field:

  "inventory": [ {"line": <int>, "expression": "<the exact words>",
                  "kind": "backward" | "contrast" | "quantifier",
                  "antecedent_line": <int> | null} ]

The inventory must list every dependent expression you found, including the ones
whose antecedent you located. A draft of narration that yields an empty
inventory means the sweep failed, not that the draft is clean.
