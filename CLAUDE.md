# CENTS essay videos

A **series** of short films about Rutherford Chang's artwork CENTS, built with a
Remotion pipeline in this repo. Several films, not one. The user (Ezra
Shibboleth, shibboleth88@gmail.com) authored the CENTS essay and sits on the
Trait Council, so the films speak the project's ideas directly rather than
reporting on them.

**Read [HANDOFF.md](HANDOFF.md) first.** It holds current state, what is done,
what is next, and the traps. This file is only the standing rules.

## Standing editorial constraints

These came from the user's corrections. Each was given at least once, several
twice. Breaking them is the most likely way to waste a session.

- **Value is the governing frame.** CENTS is about value being continually
  redefined. An incidental fact must not become the organizing principle.
- **Never imply an intention Chang did not have.** A property of the readymade
  is not a reason for choosing it. Script *order* alone can invent a motive
  that every individual sentence is innocent of. This error was shipped twice.
- **CENTS has no ending.** Present it as a continual process, becoming, a
  system. Do not close on the artist's death or the penny's discontinuation;
  both are facts that belong early or at a hinge, never last.
- **Past tense for Chang.** He died 24 January 2025. (Corrected 2026-10-24: this line said 9 February
  2025, which is the date of the NYT obituary, not of his death.) Never "Chang is/believes/
  thinks/wants" — the glossary enforces this.
- **Narration speaks ideas directly.** No "the essay argues", "the author
  writes". Attribution belongs in credits.
- **It is "within emptiness"**, in the black-hole-humour line.
- **Epochs.** A source's deictic — now, still, currently, today — resolves to
  the SOURCE'S date and must be converted to an absolute date in narration.
  See `films/introduction/script/essay.txt` block [10]. Enforced by a gate.

## Terminology — four things, kept apart

- `CENTS` the project · `Cents` the collection pieces · `cents`/`pennies`
  ordinary money
- `CENTS Block Copper` the physical 31 kg block · `CENTS Block 839969` the
  inscription of its 3D model. Not the same object.
- `satoshi` the unit · the `inscription` · the `image` · the physical `penny`.
  Four things. Ten thousand images went onto ten thousand satoshis; the block's
  model went onto one whole block. Conflating these shipped a misleading shot.
- `struck` (cumulative since 1909) vs `in existence` (surviving now) answer
  different questions.

## Working discipline

The user's global practices govern and are not optional here:

- **Measure before reporting.** An unrun claim is not a finding. Another
  agent's result is a claim too.
- **An assertion never seen red means nothing.** Build the variant that should
  break a check and run both. `fidelity.py --self-test` is this repo's control
  suite; run it after touching any gate.
- **Floor every scan.** A count of zero means "nothing there" or "the counter
  broke", and they render identically.
- **Never furnish the subject with what the test needs.** Do not edit a script
  so a gate passes. Make the subject more correct for a reason that stands on
  its own, and say the justification in that order.
- **Corrections stay beside what they correct.** Do not quietly delete a wrong
  claim.

## Secrets

`FAL_KEY` lives in `~/.bash_profile`. **Claude does not need to see it and must
not be given it.** Do not print it, do not read it back, do not `tail` the
profile. It was exposed once this way and still needs rotating (see HANDOFF).

## Commands

```bash
python3 pipeline/film.py status              # which film is active
python3 pipeline/film.py switch <name>       # swap the symlinks
python3 pipeline/fidelity.py                 # the gates
python3 pipeline/fidelity.py --self-test     # the controls — must all go red
python3 harness/build_corpus.py              # rebuild the review corpus
python3 harness/score.py <run>               # score stored reviewer verdicts
```

## Index

[HANDOFF.md](HANDOFF.md) current state · [LEDGER.md](LEDGER.md) failure shapes
and the current episode · [LEDGER_ARCHIVE.md](LEDGER_ARCHIVE.md) superseded
episodes, verbatim · [README.md](README.md) pipeline and art direction ·
[harness/RESULTS.md](harness/RESULTS.md) reviewer scores ·
[docs/archive/](docs/archive/) the v1 handoff
