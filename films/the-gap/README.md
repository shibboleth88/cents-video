# The Gap, a year on (current-events film)

Thread "Make a CENTS current-events video", started 2026-11-03. Angle chosen by Claude
as the recommendation of three (the user may still pick another): the first anniversary
of the last circulating cent (12 Nov 2025) plus the record copper price (Sep 2026), as a
widening of the value gap CENTS begins from. Closes on value still being decided, never
on the penny's end (standing rule: CENTS has no ending).

## v1 (2026-11-03)

- **Script:** `script/voiceover.txt` (written form, used for captions) and
  `script/voiceover_v0.1.txt` (spoken form). 254 words.
- **Narration:** eee (`pp4OmJ3yyWS9Jyhejh5f`), eleven_v4, `[thoughtfully] [calm]` once at the
  start (user setting, 2026-10-27). Take 1 used (90.7 s); take 2 (89.5 s) kept. ElevenLabs flow
  `IOo6MoNtU5HzVM5SpHES`. scribe_v1 transcript is word-for-word the TTS text.
- **Audio:** `audio/build_vo.py`, 14 holds placed in measured pauses, 6 s end pad,
  loudnorm I=-16. `vo.wav` 109.05 s. Copied to `public/the-gap/vo.wav` (gitignored).
  The join check (each word after a hold starts where the built file's pause ends) passes
  14/14. Its red control has NOT been built for this film.
- **Captions:** `captions/build_cues.py`, Lead look, 40 cues, text equals the script;
  `captions/the-gap.srt`.
- **Picture:** `src/the-gap/Film.tsx`, its own root `src/the-gap/index.ts`. Cuts in
  `build/scenes.json`; Cents in `build/picks.json`.

## Claims on screen and in narration, with sources and epochs

| Claim | Source | Epoch |
|---|---|---|
| Last circulating cent struck 12 Nov 2025, Philadelphia | US Mint press release; CNN 2025-11-12 | 2025-11-12 |
| Cent still legal tender | US Mint; Common Cents Act coverage | as of 2026-11-03 |
| 20 states had cash-rounding laws | Wikipedia "Penny debate in the United States" ("As of July 2026, 20 states…") | July 2026 |
| Congress passed the Common Cents Act, Sep 2026; would allow rounding nationwide | Wikipedia (28 Sep 2026); ABA Banking Journal; Convenience.org (Senate, 28/29 Sep). Not reported signed in coverage found up to ~12 Oct 2026 | Sep 2026 |
| Symmetric rounding ($4.97 to $4.95; 1,2,6,7 down) | Senate text as summarised by Lankford one-pager / shopappy | Sep 2026 |
| LME copper record $14,875/t | Reuters via Business Recorder (10 Sep) and Mining.com.au (11 Sep); date given on screen as 10 Sep | 2026-09-10 |
| Pre-1983 cent 95% copper, 3.11 g | US Mint specifications | — |
| ≈ 4.4¢ of copper at the record | computed: 3.11 g × 0.95 × $14,875/t = 4.395¢. Nov 3 COMEX ~$6.35/lb gives ~4.1¢, so "more than four cents" also held on the date of v1 | 2026-09-10 |
| Copper worth more than face "for most of twenty years" | brief §4 approved phrasing was "for twenty years"; softened because copper dipped below ~$1.54/lb in late 2008 | — |
| 10,000 removed from circulation, photographed front and back, melted into a block, 31 kg | project description; brief §1 (H) | 2024 |
| Each front inscribed on its own satoshi, March 2024 | brief §1 (H) | 2024-03 |
| Five natures | shibboleth, "CENTS & digital objecthood" (spoken directly, per CLAUDE.md) | — |
| Traits named over two years of voting | brief §4 approved wording | — |

Hero Cents (1050px cents.vision fronts, traits read from the front): #142 (1973) copper
hero, with its back under "front and back" only; #3981 Full Verdigris; #360 Full
Obsidian; #16 Fingerprints; #111 Ghost. Field: 320 random Cents (seed 20261112), texture only.

Not used, deliberately: the NYT-obituary/penny-order same-day fact (Tinari) — it risks
reading as fate or intent; the copper price as anything Chang chose; CENTS sale prices
(never appraise); the legality of melting cents.

Render (from the repo root):

    npx remotion render src/the-gap/index.ts FilmCaptioned films/the-gap/exports/the-gap_v1_captioned.mp4
    npx remotion render src/the-gap/index.ts Film films/the-gap/exports/the-gap_v1_clean.mp4

In the cloud container add `--browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`.
Assets to `public/the-gap/` (gitignored): `hi/*.webp` from cents.vision fronts (and
`142_back.webp`), `ftg/pour.mp4` and `ftg/rolls.jpg` from "cents shortlist/for videos"
(`copper pour clip.mov`, `Rutherford desk cent rools sent to Reapa.jpeg`), `vo.wav`.
Cents via `python3 pipeline/stage_cents.py --src <sovrn-onchain>/cents <numbers in build/picks.json>`.
