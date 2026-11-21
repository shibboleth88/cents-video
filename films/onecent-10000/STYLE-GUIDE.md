# STYLE-GUIDE.md: One Cent series

Version 0.1, 2026-11-21. Written for the trial of the `remotion-video-builder` skill
(github.com/NulightJens/jensai-skills, `remotion-video-builder/SKILL.md`, commit 8598b58) on
Cent #10000. The skill builds a composition from a STYLE-GUIDE.md. Ours is written from the
house rules, not reverse-engineered from a reference video. It is organised in the skill's own
Step 1 categories (canvas, visual, animation, layout, audio, editorial) so the skill can parse it.

**Sources of truth, in order.** Where this file and these disagree, these win, and this file is
corrected:
1. The user's rules in this thread.
2. `CLAUDE.md` (standing editorial rules) and project memory.
3. The series brief, `/mnt/project-files/single-cent-series/BEST_PRACTICES.md` (cited as §n).
4. `src/style/tokens.ts`, `src/style/palette.json`, `src/style/captions.tsx`, `src/style/onecent.tsx`.

This file restates; it does not set new rules. Every value below names where it comes from.

---

## 1. Canvas

| Parameter | Value | Source |
|---|---|---|
| Size | 1080 × 1920, 9:16 | `tokens.ts` CANVAS |
| Frame rate | 30 fps | `tokens.ts` CANVAS |
| Duration | **under 3:00 including credits**, hard ceiling. Plan 75–95 s of narration; finished films have run 1:44–2:09. Ask the user past about 2:00 | §1, user 2026-11-14 |
| Safe area (essential text) | x 80–860, y 270–1510 | `tokens.ts` SAFE.essential |
| Regions | title 104/320–836/1180; quote 104/520–836/1280; caption 104/1340–836/1500; credits 104/700–836/1200 | `tokens.ts` REGIONS |
| Gate | The renderer fails a frame whose essential text leaves the safe box (SafeText) | `src/style/Safe.tsx` |

## 2. Visual

**Background.** `#0b0a0a` (palette `bg`), surface `#191817`. Cents are cut out on black, never on
white squares (§5, [26 Oct]). The first frame is never black (§5.1).

**Palette.** Sampled from the artwork by `pipeline/palette.py`, not chosen:

| Token | Hex | Use |
|---|---|---|
| ink | `#f4ede8` | primary text |
| inkDim | `#a09993` | secondary text, inscription number |
| copper (accent) | `#af6b39` | concept card, quote credit, readouts |
| verdigris (accent2) | `#76b7a6` | secondary accent |
| caption copper | `#d9925c` | the word being spoken in Lead captions |

**Type.** Display "Inter Tight", body "Inter", mono "IBM Plex Mono" (`tokens.ts` TYPE). Sentence
case in captions; the "Story time" pill and concept card are uppercase mono/display.

**Sizes (canvas px), with the legibility floor the renderer enforces** (`tokens.ts` MIN_FONT_PX:
caption 46, label 42, body 46, display 64):

| Text | Size | Source |
|---|---|---|
| Title "Cent #<n>" | 84 (one line) | `onecent.tsx` |
| Inscription number under the coin | 46, inkDim | `onecent.tsx` |
| Concept card | 64 display, copper; label fits two lines of about 18 characters | `onecent.tsx`, §7 (#1328) |
| Quote card body | 54, about 33 words per card | §3, `onecent.tsx` |
| Quote credit | 42, copper, one line (about 45 characters) | §4 |
| Readout under a zoom | 84 title, 48 caption, about 25 characters | `onecent.tsx`, §7 (#8462) |
| Captions (Lead) | 52, two lines max | `captions.tsx` |
| End credits | 46, five lines plus the URL | §7 (#8820) |

## 3. Animation

**Captions: "Lead" (captions-1), the default since 2026-10-28** (§7, PR #22). Karaoke-style, word
by word, from the word-level alignment:
- No box. A soft dark scrim (`rgba(11,10,10,0.62)` band, fading at its edges).
- Words already said are white, upcoming words dim, the word being spoken is copper `#d9925c`.
- Numbers 10–99 as digits; hyphenated words never break across lines.
- Written forms are mapped onto their spoken words for timing (the `SPOKEN` table: "Reiss" is
  voiced "Rice", "#10000" is voiced "number ten thousand").
- An SRT is delivered beside the film. Captions are a separate layer that can be switched off;
  only the captioned render is delivered (§7, [28 Oct]).

**Quote cards light word by word** as they are spoken (§3, [26 Oct]). The render fails if the card
and the recording disagree word for word.

**Camera.** Zooms to measured boxes on the 1050 px front, eased, one zoom box per named trait,
reduced by 0.88 when a ring is drawn (§7). No Ken Burns on archival plates; plates are shown at
native size, never upscaled (§5.6).

**Coins do not spin**, except the 3DCENTS render at the open and close, and CentFlip (§7).

**Transitions.** Short fades between shots (the delivery check counts each designed black dip at a
shot boundary). Dissolves are used on purpose: the template comparison is a CentDissolve (§5.5).
*Skill default not adopted:* "hard cut only, no dissolves".

## 4. Layout modes

| Mode | Component | When |
|---|---|---|
| Cent card (title, coin, inscription, readouts, concept and quote overlays) | `CentLook` | the spine: opening, zooms, cards |
| 3DCENTS turn | `CentLook` `spin` / `CentSpin` | open (once, 150 frames, then hold the front) and close (one turn) |
| Pool scroll, 3–8 across, featured Cent last with `spotlight` | `CentScroll` | a trait pool of any size (§5.5, §7 #8820) |
| Named small group | `CentSet` (`cols: 2` for three) | a handful of Cents |
| Template comparison | `CentDissolve` | same-year Cent "close to mint state" |
| Archival / media-library still or clip | `Plate` | context imagery, native size |

**Distribution.** The Cent card carries most of the film, but visual variety is a rule
([3 Nov]): a new visual every 3–6 s, every shot 9 s or shorter except the Cent card's zoom run and
quote cards. Benchmark #1264 v7: 24 shots, median 4.7 s, 17 distinct plates.

## 5. Audio

| Parameter | Value | Source |
|---|---|---|
| Voice | ElevenLabs "eee", voice_id `pp4OmJ3yyWS9Jyhejh5f` | §7, memory |
| Model | `eleven_v4`, default settings | §1, user pick 27 Oct |
| Tags | `[thoughtfully] [calm]` once at the start of the prompt | §1 |
| Pace | about 2.5–2.9 words a second; time each take from its audio | §1 |
| Numbers | spelled out in the voice text ("ten thousand", "nineteen seventy-six") | §7 |
| Respellings | voice text only, folded back for captions and the heard check ("Rice" for Reiss) | §3, §7 |
| Loudness | −16 LUFS target, `loudnorm I=-16:TP=-1.5:LRA=11` | §7 |
| Holds | silent holds inserted at measured pauses (silencedetect, 150 ms floor) | §7 |
| Music bed | **none** | house practice; no episode uses one |
| SFX | none | house practice |
| End pad | covers the closing turn and credits | §7 |

## 6. Editorial

**Beat template: the One Cent order (§5)**, used in place of the skill's storytelling templates:

| Beat | What | Typical share |
|---|---|---|
| Title | "Cent #<n>" over the 3DCENTS turn, Story time pill at frame 0 | 5 s |
| Look | year zoom, then mint mark zoom, with the Philadelphia/Denver wording; rarest quality first | 8–10% |
| Traits | each named trait: Atlas wording for its grade, zoom to it on the front, whole pool with this Cent spotlit | 30–35% |
| Template | dissolve with a same-year Cent "close to mint state" | 6–8% |
| Concept | concept card by name (no ID), quote card(s) attributed in the voice | 20–25% |
| Widen | history, an art-literature lens, the value tie | 15–20% |
| Close | the opening card again, one turn, "Cent <n>, a great Cent." | 5 s |

**Word count.** About 240–300 spoken words (numbers spelled out).

**Vernacular.**
- Narration speaks ideas directly; attribution only for verbatim quotes, said aloud ("In the words
  of Steven Reiss, in his article …") and on the card (§3).
- Past tense for Chang. Never imply his intention; script order alone can invent a motive.
- Value is the governing frame. CENTS has no ending: never close on an aphorism, the artist's death
  or the penny's discontinuation.
- Terms kept apart: CENTS / Cent / cent; satoshi, inscription, image, penny; "pre-1983" or
  "pre-zinc"; the template is "close to mint state", not "lustrous".
- A critic or theorist is a lens on CENTS, never Chang's source; say when they were not writing
  about CENTS.
- No prices, no advice, no calls to action. The film is non-promotional.

**TTS rules (the skill's universal rules, as adopted).**
- Adopted: spell out numbers; short sentences; avoid parenthetical asides in our own words; avoid
  semicolons; no filler phrases.
- Not adopted: ALL CAPS for stress and `--` for punchy pauses (eleven_v4 with audio tags is the
  agreed setting; emphasis is not added). "No rhetorical questions" holds anyway.
- Quotes are read as written, even where they break a TTS rule (a parenthesis in Lippard and
  Chandler is voiced "not necessarily, rarely, identical" and kept verbatim on the card).

**CTA style.** None.

## 7. Credits (end card)

"Images: Rutherford Chang"; "3D render: 3DCENTS by sinvalli"; "Trait names: the CENTS Trait
Council"; "Traits Atlas, CENTS Trait Council" when the Atlas is quoted; each quote in full form;
media library items as "cents.gallery media library". Five lines plus the URL (§4, §7).

## 8. Where the skill's defaults were overridden, and why

| Skill default | Ours | Why |
|---|---|---|
| Pexels B-roll | Real CENTS imagery only: 1050 px fronts, 300 px images, 3DCENTS, cents.gallery media library, cleared archives | Project rule: no stock, no AI coins |
| Gemini or whisper.cpp transcription | ElevenLabs scribe_v1 on the take fetched by URL (`check_heard.py`), timed from the audio | Already in the pipeline; no Gemini key needed |
| Storytelling templates (Brand Documentary, Proof Drop…) with a CTA closer | The One Cent beat order above | The templates close on a thesis or a CTA, which our rules forbid |
| Hard cuts only | Fades, plus deliberate dissolves | CentDissolve is a series device |
| Music bed at 0.05–0.1 | None | House practice |
| ALL CAPS emphasis, `--` pauses | eleven_v4 audio tags | Agreed voice setting |
| "Ask the user" for any unspecified style value | This file plus the brief | The brief already answers most of them |
| One component per file, under 200 lines | Existing `onecent.tsx` (671 lines) kept | Skill's own rule 1: follow the project's structure |
