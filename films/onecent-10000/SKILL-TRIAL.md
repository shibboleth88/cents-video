# Trial of `remotion-video-builder` on One Cent #10000

2026-11-21. Skill: NulightJens/jensai-skills, `remotion-video-builder/SKILL.md` (426 lines) with
`references/component-patterns.md` and `references/storytelling-templates.md`, commit 8598b58. Asked for
by the coordinator: try the skill on a One Cent episode, write `STYLE-GUIDE.md` from the house rules
instead of from a reference video, skip Pexels, and note what the skill adds and what gets in the way
compared with the current pipeline.

**Short answer.** The skill is a general recipe for B-roll explainers (stock footage, music bed, hard
cuts, karaoke captions, a hook and a call to action). Its eight steps map onto steps this pipeline
already has, and in every case ours is stricter. The one thing worth keeping is the exercise it forces
first: one `STYLE-GUIDE.md` that restates the rules scattered over CLAUDE.md, the series brief, project
memory and `src/style/`. I'd keep that file as a series document and not adopt the workflow.

## Step by step

| Skill step | What the skill does | What this episode did | Verdict |
|---|---|---|---|
| 1. Load and parse a style guide | Reads STYLE-GUIDE.md (canvas, visual, animation, layout, audio, editorial) | Wrote `STYLE-GUIDE.md` from the house rules in those categories, every value citing its source; §8 lists the 8 skill defaults overridden | **Adds.** The only new artefact. One file a new thread can read in place of four places |
| 2. Write the script | Pick a storytelling template, present the script with beat labels and timings, get approval: "the script is the contract" | Proposal v0.1 with beat labels and estimated starts, approved by shibboleth | Same as ours. Its templates (Brand Documentary, Proof Drop…) end on a thesis or a CTA, which the series forbids (CENTS has no ending; non-promotional), so the One Cent beat order was used |
| 3. Voiceover | ElevenLabs `text_to_speech`, multilingual_v2 example, ALL CAPS for stress, `--` for pauses | eee on eleven_v4 with `[thoughtfully] [calm]`, the user's pick | **In the way.** The tool name doesn't exist on this connector (`creative_generate_speech`), multilingual_v2 was rejected by the user on 27 Oct, and ALL CAPS and `--` fight the agreed tags |
| 4. Word timestamps | Gemini or whisper.cpp; check the first and last word | scribe_v1 on the take fetched by URL; `check_heard.py` compares every token with the voiced text (310 of 310), and its control (one word dropped) went red | **Ours is stricter.** The skill never checks that the take says the script. A first-and-last-word check passes a take that skips a line in the middle |
| 5. Collect assets | Pexels search per sentence, or ask the user | Real CENTS imagery only: cents.vision fronts, the Atlas page (control refused), three media library items | Pexels skipped as asked. Its asset checklist (min 1080 px, no watermark) is weaker than `assets.json`'s rights, source and native-size fields, which the Plate component enforces |
| 6. Components | New `[VideoName].tsx`, theme, fonts, one component per file under 200 lines | Existing `CentLook`, `CentScroll`, `CentSet`, `CentDissolve`, `Plate`, `Credits`; no new code | The skill contradicts itself here: its rule 1 says follow the project's structure, its rule 3 says under 200 lines per file. Rule 1 won (`onecent.tsx` is 671 lines) |
| 7. Scene sequence | Frame numbers from timestamps; "never hard-code timing" | Shots anchored to phrases in `timeline.json`, resolved from the alignment, with an ambiguity guard | Same principle, ours already enforced |
| 8. Preview and iterate | Visual checklist, Playwright screenshots, contact sheets, a graded loop for reference videos | Silent rehearsal (40 stills on a stand-in alignment), then 37 stills on the real take, read as contact sheets | **Small add.** Reading stills as contact sheets (7 frames to an image) made the 40-still pass quicker to read. The rehearsal itself is ours (#1328) |

## What caught problems in this run

Every catch came from the pipeline, none from the skill:

- `SafeText` refused the end card when the Reiss credit wrapped to four rows.
- The Atlas shot's control ("bullet" for "projectile") was refused, so the highlight is on the real sentence.
- `check_heard.py`'s control went red on both takes, so its 310-of-310 pass means something.
- `counts.py`'s floor (Assassin = 42) was seen red on a copy with one flag removed.
- The C001 mosaic turned out truncated in the media library (no JPEG end marker), found by decoding it, not by its byte count, which matched the catalogue.

The skill has no gates: no quote check, no count floor, no safe-area gate, no delivery check, and no
controls. Its Step 8 checklist is a list of things to look at.

## Skill defaults overridden

Listed in `STYLE-GUIDE.md` §8: Pexels B-roll; Gemini or whisper transcription; storytelling templates
with a CTA close; hard cuts only; a music bed at 0.05 to 0.1; ALL CAPS and `--` in the voice text;
"ask the user" for any style value the guide leaves open (the brief answers most, and a thread that
waits on a person stalls); one component per file under 200 lines.

## If the skill is used again

- Keep `STYLE-GUIDE.md`, but as a series file (`single-cent-series/STYLE-GUIDE.md`) that the brief
  points to, not a per-episode copy. It restates; the brief and code stay the source of truth.
- Don't load the skill's workflow into an episode thread. It costs reading time and its defaults have to
  be argued away one by one.
- For a film that really is a B-roll explainer with a reference video (not this series), its graded
  recreation loop in Step 8 (one scene at a time, scored against source frames) is the part worth
  trying.
