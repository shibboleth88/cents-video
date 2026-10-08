---
name: video-concept-relations
description: >-
  Use this when the question is about how the parts of a film or script
  relate, not whether each part is accurate: where a line sits and what its
  position implies; whether moving, reordering, opening or ending with
  something changes what the piece argues; whether repeated lines are emphasis
  or padding; whether a trim left a conclusion without its premise; whether a
  shot and the words over it assert a third thing neither says; whether the
  ending's shape fits the thesis. Reach for it in any narration or voiceover
  work — drafting, cutting to length, resequencing, pairing shots to lines,
  reviewing before recording or locking — and especially when a line "doesn't
  land", a reader says "this doesn't follow", or every fidelity check passes
  and the piece still feels wrong. Per-sentence source checks read each claim
  alone and cannot see any of this.
---

# Relational failures in an essay film

Most verification in this pipeline is **per-item**: a sentence maps to a span of
the source, an on-screen string maps to the ledger, an asset has rights and a
subject. Those checks are good and they work.

They share one blind spot. **Every one of them reads a single item in
isolation.** So a whole class of error passes with all gates green:

> Each part is true. What they say *together* is not, and nothing checked the
> together.

Every finding below came from a real production in this repo where the gates
were green and a human found the problem by reading or looking. Treat the list
as the set of relations worth interrogating, not as a checklist to tick.

---

## 1. Order asserts causation

Putting B after A proposes that A explains B. No sentence has to say it.

**What happened.** A film opened on *"Brenner's Lincoln is the most reproduced
artwork on Earth"*, then introduced the artist and the work. Every sentence
mapped to a cited span. Ten fidelity gates passed. But the position made it read
as *why Chang chose the penny* — and the source says the opposite about origins:
he began from a value discrepancy. The portrait's ubiquity is a **property of
the object**, not a **reason for choosing it**, and those are close enough that
sequence alone converts one into the other.

**The check.** For each early fact ask: *what causal reading does this position
create, and does the source support it?* State the origin the source states
before describing properties.

**The general pair:** a property of the work is not a reason for making it.

---

## 2. A cut premise leaves its conclusion standing

When you cut a sentence for length, the sentences that pointed at it do not
fail. They go quiet. They still parse, still map to a span, still pass.

**What happened, twice.** *"Yet the object remained, buoyed into physicality by
the force of its context"* survived a trim that removed the passage it concludes
— the penny losing its function. "Remained" then referred to nothing. Later, at
the other end of the same film, *"each one initially identical, now bearing the
marks of touch and time"* survived while the permanent-set-of-10,000 premise it
depends on was cut, and the closing line invoked *participants* the film had
never shown.

**The check.** After any cut for length, **re-read the survivors in order and
ask of each one what it refers to.** Not whether it is true — whether its
referent is still in the piece.

A grammatical dependency is the strongest available fix: making the next
sentence a continuation (*"The way words do, inside…"*) means it cannot float,
where a new sentence can.

---

## 3. Repetition in synonyms, mistaken for emphasis

When a point matters, the instinct is to restate it. Four sentences saying the
same thing in different words feels like emphasis and reads as padding.

**What happened.** One film stated *continual redefinition* four times — in the
transformation list, as "an ongoing process of redefinition", as "indeterminate
and continually redefined", and in the closing line. Three shared a word root.

**The distinction that resolves it.** Repetition across **registers** is
argument; repetition in **synonyms** is padding. The fix kept four instances and
cut nothing conceptual, because each surviving one worked in a different
register: the *mechanism* (in the list), the *object* changing (marks of touch
and time), the *meaning* changing (collectors reading the set), the *work's
nature* (the closer).

**The check.** For each restatement: *which register does this add — mechanism,
object, reader, form — or is it only another word for the last one?*

---

## 4. A true picture under a true sentence, asserting a third thing

This is the one with no automated check anywhere, and the costliest.

**What happened.** The line *"Five, inscribed on Bitcoin"* played over a plate of
the copper Block, captioned *"CENTS Block 839969"*. The caption was true of the
image. The image was a real, rights-cleared asset. The narration was faithful to
the source. **All eighteen release gates passed.** And the pairing said *the
Block was the thing inscribed* — when in fact ten thousand cents were inscribed,
one per satoshi, and the block's 3D model was a separate inscription the film
never mentioned.

Neither the picture nor the sentence makes that claim. The pair does.

**The check.** For every shot, **say out loud the claim the image and the words
make together**, as one sentence beginning *"this is telling me that…"*. Then ask
whether the source supports *that* sentence. This is why a shot review pairs
frames with the words spoken over them — nothing else can do it.

**Related pair:** an image of the **result** is not an image of the **act**. A
finished archival photograph stood in for *"archivally photographed"* — a verb —
until the photography setup itself was available. Both are true pictures of the
work; only one is a picture of what the line says.

---

## 5. Form contradicting thesis

A piece's shape makes a claim independent of its sentences. A shape that
contradicts the thesis will quietly win, because form is felt and argument is
only heard.

**What happened.** A film whose closing line was *"CENTS is a becoming, a gesture
that unfolds continually"* ended on the artist's death and the discontinuation
of the penny. Both facts were true, sourced and verified. But ending there
frames as **finished** the one work whose entire claim is that it is **open** —
and the final line then arrives as consolation rather than as the thesis.

The fix kept both facts and moved them: they belong to the object and the artist,
early. The coincidence between them turned out to be stronger as a **hinge**
between two movements than as a terminus.

**The check.** Name the thesis in one sentence. Then ask: *does the shape of the
piece — where it opens, where it ends, what it gives the last word to — enact
that thesis or contradict it?* Endings are where this bites: an ending is a
claim that the subject is the kind of thing that ends.

---

## 6. A passage answering a question the piece never asked

Material can be faithful to the source, well made, and still foreign — because
it answers something the piece did not raise.

**What happened.** Four lines on how collectors dissect the set, inside a film
that had spent its length on what value is and who assigns it. Impeccably
sourced. It answered a question about collector dynamics that the film had never
asked.

**The check.** For each passage: *what question does this answer, and where did
the piece ask it?* If the question is not in the piece, either ask it or cut the
answer.

---

## 7. Anchors are positions in the words, so adding words moves them

Where an edit is anchored to a phrase rather than a timecode, inserting
narration **relocates** every anchor downstream of it. Nothing breaks. The
phrases still resolve — just later.

**What happened.** A shot ended at the anchor *"CENTS is a becoming"*. A new line
was recorded and spliced in before that phrase. The anchor still matched — 14
seconds later than before — so the shot silently swallowed the new line and
overlapped the shot built for it. Only a gapless-cover check caught it.

**The check.** After inserting or removing narration, **re-resolve every anchor
and verify the cover is gapless and non-overlapping**, rather than assuming that
anchors which still match are still correct.

---

## 8. Claims about relations among data points

A statement about how facts relate to each other needs its own measurement; it
does not follow from any single fact being right.

**What happened.** *"One year is missing"* — about a collection missing fifteen
years. One year's absence was *meaningful*; the sentence said it was the only
absence. The honest version was both stronger and more defensible: *"Only one of
the years it misses means anything."*

**The check.** Before stating that something is the only, the first, the largest
or the rarest, **count the others.** Superlatives and uniqueness claims are
claims about a set, and a fact about one member never establishes them.

---

## The passes

Four readings, each looking for one kind of relation. Do them separately —
looking for everything at once finds nothing.

1. **Read the script aloud, in order.** For each sentence: what does it refer
   to, and is that still in the piece? (Catches 2.)
2. **Read it again for sequence.** For each adjacency: what does the order
   assert? (Catches 1 and 6.)
3. **Read each shot against the words spoken over it**, saying the pair's claim
   as one sentence. (Catches 4.)
4. **Describe the shape in one line** — where it opens, where it ends, what gets
   the last word — and hold it against the thesis. (Catches 5.)

Then re-resolve anchors (7) and count the set behind any superlative (8).

---

## What to do when you find one

Record it where the next person will read it, in the form *A is not B* with A and
B close enough that confusing them was reasonable — *a property is not a reason*,
*a premise is not a conclusion*, *an image of the result is not an image of the
act*. The near-miss is the useful part; a shape written as an incident report
teaches nothing.

And note honestly which of these a gate can catch. Most of them cannot be
automated, because catching them requires understanding what the piece is
arguing. Saying so in the record is better than implying a check exists.
