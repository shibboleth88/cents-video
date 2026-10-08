# CENTS essay videos — pipeline

Give it an article. You get a recording script. You record it. You get a film.

## The two stages

**Stage 1 — the transcript.** This is the deliverable, and it comes first.

    (give Claude the article)
    python3 pipeline/fidelity.py        # is the script true to the source?
    python3 pipeline/transcript.py      # -> exports/recording_script.txt

`recording_script.txt` is laid out for reading aloud: one sentence per line,
numbered, with the words that trip a reader marked. Record it in one take to
`inputs/vo_raw.wav`, leaving four seconds of silence at the end for credits.

**Stage 2 — the film.** Built from your recording, not from a guess at it.

    pipeline/audio_clean.sh inputs/vo_raw.wav public/vo.wav
    python3 pipeline/align.py public/vo.wav --script script/voiceover.txt
    pipeline/assets.py ingest ... && pipeline/assets.py sheet     # the article's own images
    python3 pipeline/generate.py image --prompt ... --asset-id ... --confirm
    python3 pipeline/generate.py run --shot ... --confirm          # generated video
    npm run render && npm run render:captioned && npm run render:essential
    python3 pipeline/review_shots.py prepare && python3 pipeline/verify.py

Shots are anchored to phrases of the narration, so re-recording re-cuts the film.
Nothing is timed to seconds.

A synthetic scratch pass (`pipeline/scratch_align.py`) still exists for seeing an
edit before recording, but it is a side road, not the main one.

## Imagery: a mix

The film draws on three sources and `project.json` sets the balance per film:

| source | for |
|---|---|
| the article's own images | the work itself, people, places, documents |
| generated stills and video | abstraction, atmosphere, transitions, anything with no photograph |
| code | the argument: diagrams, data, type |

Most articles arrive with no pictures, so generated imagery is the normal case,
not a fallback. `max_generated_share` is policy, not a fixed rule.

One narrow line survives: **never generate a picture of a specific real thing** —
a real transaction or block, a screenshot of a real interface, a named artwork
the article photographed. Invented imagery is fine; an invented picture *of*
something real reads as evidence.

## The three ideas this rests on

**Audio is the clock.** No file in this repo names a number of seconds. Shots are
anchored to *phrases of the narration* (`"at_phrase": "What goes missing"`), which
`align.py` resolves to word times. Re-record the voiceover and the edit re-cuts
itself. An anchor that is missing or ambiguous fails the render rather than
silently mis-cutting.

**The script is gated before the film is.** The previous production's real
failures were comprehension failures — an invented thesis, a misattributed
quotation, collapsed distinctions — and no amount of ffmpeg catches those.
`fidelity.py` maps every narration sentence and every on-screen string to a span
of the essay, tagged quotation / paraphrase / addition. Additions are legitimate
and must be *approved*, not smuggled. Attributions are declared and signed off,
because crediting the essay's sentence to the artist is the quietest damaging
error a title card can make.

**Gates measure the encoded deliverable, not the renderer's opinion of itself.**
`verify.py --self-test` builds deliberately broken videos and requires every gate
to go red against them. A gate that has never failed is not evidence. Each scan
asserts a floor first, so a collapsed measurement reads RED rather than "clean" —
the safe-area gate refuses to report "no violations" until it has confirmed it
can see text at all.

## Layout

`src/style/tokens.ts` holds the canvas, the interface-safe bounds, named regions
and the legibility floor. Regions are inset from the safe bounds by a gutter, so
nothing essential sits on the boundary.

Components emit text **only** through `<SafeText>`. It cancels the render when
text falls outside the safe box, below the legibility floor, or wraps past its
line limit. A raw styled `<div>` bypasses all of it — that is how a 220px number
once overflowed into both side bands undetected.

The fix for an overflow is a shorter label, a split sequence, or a rearranged
region. Never a smaller film.

Safe bounds are a **starting guide measured from one Reel**, not an official
spec. Device, app version and expanded captions change coverage; ads need more
bottom clearance. Re-verify against the real upload preview.

## Motion and art direction

Colour is **sampled from the artwork**, not chosen: `pipeline/palette.py` takes
the copper and the verdigris off CENT #3981 and the Block, and builds the
neutrals on the copper hue so even the greys belong to this film. `--self-test`
replaces a source with flat blue and requires the palette to move; a palette that
did not move would be decoration wearing the costume of derivation.

`src/style/motion.ts` holds motion as TOKENS with roles — `rise`, `settle`,
`bloom`, `place` — plus stagger and a per-shot camera drift seeded by shot id.
Components pick a role; nobody tunes a curve per shot, and a new shot inherits
the film's character for free.

Captions reveal word by word from the same alignment the edit is cut from, so the
reveal cannot drift from the voice. Diagram captions read in the same way, and a
severed link's dashes drift apart while an intact one carries a travelling
highlight — motion that states the argument rather than keeping the frame busy.

`no static passage` gates the production notes' rule against long stills. It
compares frames **two seconds apart**, because a drift slow enough to be tasteful
moves nothing at all between adjacent frames.

## Connecting fal (one-time)

1. Create the key at **fal.ai/dashboard/keys** -> "Create Key". Choose the
   **API** scope, not ADMIN: API calls models, ADMIN also allows deploys and
   app management, which nothing here needs. The key is shown **once** — copy it
   before leaving the page, or make a new one.
   Then check **Billing**: fal is prepaid credits with starter credits on
   signup, and the account locks when the balance runs low. There is **no
   built-in spend cap**, so `plan` and `--confirm` are the only brake.
2. Put it in your shell profile — **this machine's shell is bash, so `~/.bash_profile`**
   (add it to `~/.zshrc` too if you use zsh in Terminal):

       export FAL_KEY="paste-your-key-here"

   Keep it out of this repo. `.env` and `.env.local` are gitignored as a
   backstop, but the profile is the better place: nothing in the project
   directory then holds a credential.
3. Check it (no new terminal needed — `falenv.py` reads the profile directly,
   because this pipeline runs in a non-login shell that does not):

       python3 pipeline/check_api.py

   It reports only whether the key is present and whether a call is accepted.
   It never prints, logs or stores the value, and redacts it from any error.

Claude does not need to see the key and should not be given it: the pipeline
reads it from the environment.

## Generated motion

    pipeline/check_api.py          # is the connection live?
    pipeline/generate.py models    # catalogue and configured prices
    pipeline/generate.py plan      # what it would do and cost; needs no key, spends nothing
    pipeline/generate.py run --shot s02_title --confirm

Endpoints, parameter shapes and prices are verified against fal's own model
pages (2026-10-04) and the verification date is recorded beside each price.
Prices appear on the model's gallery page, not its /api page.

`duration` accepts only 5 or 10 seconds, and image-to-video takes no aspect
ratio — the output follows the source image.

Image-to-video on **your own stills** is the default path. For a film about the
objecthood of real things, animating a photograph the artist took and inventing
footage of an artwork that was never filmed are different acts. Generated clips
enter the inventory with an empty `subject`, so `assets.py check` refuses them
until they have been looked at — a generated clip can invent detail the still
never had.

## Assets

    pipeline/assets.py ingest <folder|zip> --page <saved.html> --label ... --rights ...
    pipeline/assets.py sheet     # contact sheet - LOOK at every asset
    pipeline/assets.py stage     # copies into public/, applying declared crops
    pipeline/assets.py check     # release gate
    pipeline/assets.py plan      # which shots want imagery

Ingest keeps provenance. From a saved web page it takes only figures inside the
article body, because a Medium export is mostly sidebar advertising and a
filename cannot tell you which is which.

Nothing is usable until someone has **looked at it**: `subject` and
`crop_restrictions` are written from the image, never from its filename, and
`check` refuses an asset with no subject, no rights basis, or a hash that no
longer matches the file. It also fails when identified assets exist and the film
uses none of them - "all used assets are fine" is vacuous at zero.

A crop is applied at **staging**, not at render time. `a01` carries another
essay's title burned into its lower third; recorded as advice, the restriction
was ignored by an object-position that could not honour it, and the wrong title
went on screen. Cutting the pixels before the renderer sees them removes the
possibility.

Low resolution is a usage constraint, not a reason to discard: the Block
animation came back from Medium at 385x338 and `Plate` refuses to display it
wider than it can carry.

**Not yet built:** sourcing imagery from the web with licence and provenance, and
generating it. This session has no image-generation tool, so "generated" here can
only mean procedural/code imagery or an external service you hold keys for.

## Visual sourcing

Every shot declares `visual_kind`:

| kind | use for | note |
|---|---|---|
| `code` | argument, explanation, data, diagrams | default; the component library compounds |
| `real` | a specific work, person, place or event | required there — never fake these |
| `stock` | mood, transition | capped |
| `generated` | abstract metaphor | capped |

`stock` + `generated` may not exceed 45% of shots. Every shot must state a
`purpose`; a shot that cannot say why it exists is decoration.

## Looking is a stage, not a habit

`review_shots.py prepare` extracts frames per shot and pairs each with **the words
spoken over it**, so correspondence can be judged. Claude fills a verdict per
shot; `verify.py` refuses to release while any shot is unreviewed, marked
`revise`, or reviewed against an older render.

This is not decoration. On the fixture film every numeric and fidelity gate was
green while the vision pass found six substantive problems, including a quotation
from the essay credited on screen to the artist. Two of those findings became
permanent gates (`caption redundancy`, `credits after voice`). That is the
intended direction of travel: the eye finds the class, a rule catches it forever.

## Two films, one pipeline

Per-film state lives in `films/<slug>/`; the working directories at the repo
root are **symlinks** into the active one.

    python3 pipeline/film.py status            # which film is checked out
    python3 pipeline/film.py switch <slug>     # repoint at another
    python3 pipeline/film.py new <slug>        # scaffold one

Symlinks rather than copies, deliberately. A copy is how you get two versions
of a file with only one of them current — the failure this repo keeps meeting,
most recently in a corpus that reintroduced a corrected fact hours after it was
fixed. There is exactly one of every file; switching repoints and never
duplicates.

**Shared, never per-film:** `shared/assets.json` (the inventory both films draw
on), `shared/generation_log.json` (API spend is global), `inputs/` (raw
material), `public/assets/` (staged imagery), `pipeline/`, `src/`.

**The one exception is the voiceover.** Remotion serves `public/` over HTTP and
will not follow a link out of it — the render 404s. So the master stays in
`films/<slug>/audio/vo.wav` and `switch` *stages a copy* to `public/vo.wav`,
the same way `assets.py stage` populates `public/assets/`. `film.py status`
hashes both and fails if they differ, so the copy cannot silently go stale.

`status` also refuses to guess at a **mixed** state. Script from one film and
timeline from another would render a coherent-looking film of a script nobody
wrote, so a disagreement among the symlinks reports INCONSISTENT and exits
non-zero rather than picking a winner.

## Layout of the repo

    films/<slug>/   per-film state; the root script/ timeline/ captions/
                    exports/ review/ are symlinks into the active one
    shared/     assets.json (inventory), generation_log.json (API spend)
    inputs/     raw voiceover and supplied assets, unmodified
    script/     -> voiceover.txt, alignment.json (generated)
    timeline/   -> timeline.json (the edit); assets.json links to shared/
    captions/   -> cues.json, captions.srt (generated)
    src/        renderer: style/ tokens + components, lib/ anchor resolution
    pipeline/   fidelity, scratch_vo, align, reconcile, cues, audio_clean,
                review_shots, verify, manifest
    LEDGER.md   failure-shapes, refuted hypotheses, correct-but-looks-wrong
    public/     vo.wav and assets the renderer serves
    review/     contact sheets, essential.mp4 — gitignored
    exports/    clean.mp4, captioned.mp4
    manifest.json   GENERATED on export; records gates and their verdicts

## Status

The scaffold runs end to end against a **synthetic fixture** (`pipeline/make_fixture.py`)
with invented word times and silent audio. `verify.py` refuses to pass a film
built on it. The component library currently holds TitleCard, PullQuote,
StatReveal, AssetShot, Credits and CaptionLayer — enough to prove the mechanism,
not yet enough to make a good film. Diagrams and real asset handling come next.
