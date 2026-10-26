# Lessons from the GPT productions

Distilled 2026-10-24 from the GPT "CENTS Video Production" handover (v1.0,
24 October 2026), written after the Schwartzman& announcement video and the
first *Secret History of a Penny* prototype. The user's framing: lessons
learned, **not** a proven process. Where this file and [CLAUDE.md](../CLAUDE.md)
disagree, CLAUDE.md wins.

Only what this repo does not already enforce is kept here.

## Editorial

- **Lead with the news.** For an announcement, name what happened in the first
  line. The Schwartzman& film first spent too long on context before saying
  that the firm is *representing* Chang's body of work. Use "representing" for
  the announcement; cataloguing and contextualising are activities, not the
  news.
- **Explain significance; do not assert prestige.** Institutional attention is
  context, never the source of the work's value. Never imply the art world has
  only now discovered Chang.
- **Connect CENTS to the practice.** Accumulation, repetition, classification,
  material transformation, value. CENTS is not an NFT collection dropped into
  an unrelated story.
- **No inflated phrasing.** The user cut "taking it to the next level" and
  generic claims about the future of art, repeatedly.
- **Set the audience before writing.** A film for collectors does not explain
  what CENTS is.

## Visual

- **An image of a person does not illustrate every claim about their firm.**
  The GPT edit recycled the easiest-to-find portrait to fill gaps. Find imagery
  that matches the specific sentence.
- **Balanced hierarchy.** Institution and artwork share the frame; the
  institution does not eclipse CENTS.
- **A removal request means removal**, not a smaller or shorter version.
- **Diagrams over generic footage.** A purposeful diagram beats stock footage
  of blockchains, computers or galleries. Use project-supplied diagrams before
  drawing substitutes.
- **Real Cents for any claim about a specific coin, year, trait or patina.**
  Generated imagery may be illustrative only and must not read as evidence.
  Never animate a Cent (an i2v model retouched a worn coin).
- **Reusable treatment:** a static or slowly moving contextual image above a
  continuously moving field of Cents. It links institutions or history to the
  actual objects.

## Audio

- The user found the GPT mix "too airy": wanted more body and warmth, less
  top end, and music about 5 dB louder for phones. That is one mix's fix, not a
  setting. Check every mix on phone speaker, headphones and laptop.
- When cleaning a take, check that no needed word was cut (GPT lost an instance
  of "repetition") and replace removed noise with clean, intentional pauses.

## Process

- **A technically complete file is not a strong film.** The first *Secret
  History* render had animated type and illustrative coins, no real Cents and
  no narration.
- **Do not change unrelated elements** while making a narrow revision.
- **Verify every preview or download link** from the viewer's side before
  calling it ready. A container's localhost is not the user's.

## Narration

The user records the narration, or uses their ElevenLabs clone of their own
voice. Either way the recording is authoritative and the edit retimes to it.

---

# From the WBWA GOLD reel (added 2026-10-26)

Distilled 2026-10-26 from a second GPT handover, "Video production preferences
and lessons for future agents", written after a 1:40 reel on the Serakai Studio
*records* exhibition at GOLD, Hong Kong (Rutherford Chang's *We Buy White
Albums*). Same status as above: lessons, not a proven process, and CLAUDE.md and
the series briefs win where they differ. Only what our docs did not already say
is kept. Already covered elsewhere and not repeated here: never open on black,
mobile-safe captions, verify links, numbered versions, real imagery as evidence.

## Editorial

- **Illustrate the concept while it is spoken.** An abstract line or section
  title ("one medium, two forms", a named concept) still needs visual substance:
  an image or sequence that makes the idea tangible, not a card alone.
- **Each named person gets their own portrait.** Two people, or a person and
  their organisation, never share one photograph. This is the second GPT
  production to recycle one portrait (see "An image of a person" above).
- **Press coverage shows the publication's official mark**, at its own
  proportions, not a generic icon or a typeset approximation; and the coverage
  claim must match the article. *Open question for the user:* project memory
  allows web-sourced images only if public domain or CC0, and a masthead is
  neither. Ask before the first use.
- **Label footage by where it was shot.** Footage from one venue must not read
  as another venue. Name the place on screen when the narration is about a
  different one.
- **Found is not used.** When the user supplies or asks for footage, assess it,
  select shots, cut them in and render. Discussing footage, or a revised script
  or timeline, does not answer a request for a new video.

## Visual and pacing

- **No repeated images, except agreed repeats.** Track each still and clip
  across the whole film; a repeat needs a reason the user has agreed to. A
  crop or zoom of the same context photograph does not count as a new image.
  - *Our agreed repeats (keep them):* the One Cent opening and closing spin
    card; the template-comparison dissolve; and every zoom into the Cent or Wall
    under study, which is the subject, not filler. The rule is about context
    imagery: photos, footage, portraits, documents.
- **When new material arrives, rebalance the whole edit**, not just the slot
  it fills. New footage is a chance to break up long holds elsewhere.
- **Variety from real change**: different viewpoints, scales (wide, medium,
  detail) and actions, not only camera moves on stills. Avoid both long static
  cards and frantic cuts; every caption must be readable in its hold.
- **Respect a clip's own movement.** A supplied clip may contain its own change
  (a push-in that ends on shelves). Keep it, or cut it on purpose; don't treat a
  clip as one uniform shot or trim it to an arbitrary length.
- **Reframe landscape footage for 9:16 on purpose**, without cropping away the
  artwork. Check source footage for burned-in subtitles or captions; crop or
  place around them so they never collide with ours.
- *Not adopted:* the GPT reel needed at least three images in its opening
  because one still held too long. The One Cent opening is one 3DCENTS turn
  then a hold, approved by the user on 2026-10-26; that format stands.

## Assets

- **Keep an asset list per film** with source, subject, location, the beat it
  serves, **usage count**, and credit or restriction. Assign assets across the
  whole sequence before rendering and read the usage counts: anything above 1
  must be an agreed repeat. (The essay films' `shared/assets.json` and
  `assets.py check` cover provenance and rights; they do not count uses.)
- **A source clip must decode end to end before it enters the edit.** A
  plausible filename, or a thumbnail extracted from the first second, does not
  prove the rest of a partial download exists. Exclude damaged and superseded
  clips from the active inputs.

## Revisions and delivery

- **A visual-only revision keeps the audio.** Same narration, mix and runtime,
  unless the change requires otherwise; then compare the new audio with the
  previous version's rather than assuming it is unchanged.
- **Check the export, not the edit script.** Before reporting a version:
  confirm each requested change in the rendered file; look at the first and the
  last frame; decode the whole file; read codec, size, frame rate, frame count
  and duration; list black and frozen intervals and look at each one; listen
  for clipped words and unexpected silence. The commands are in the Collector
  Wall brief, §5 "Delivery check".
- **"Exported and verified" is not "approved".** Report the first as what you
  checked; only the user's words make the second. Never call a version finished
  while a render or upload is pending.
- **Deliver the film first**; the editorial choices (what moved, where footage
  went, how the pacing changed) in a line or two after it; build detail only if
  asked.
