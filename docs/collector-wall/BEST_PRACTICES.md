# Collector Wall videos: best practices

This is the one source for the format of every Collector Wall episode. Read it before you write a script. Episode threads send their lessons back to the "Make Collector Wall video series" thread, which folds them in here and in the repo copy (`docs/collector-wall/BEST_PRACTICES.md` in shibboleth88/cents-video).

The reference episode is **blacktongue** (`films/wall-blacktongue/` on branch `claude/project-thread-nkzn17`, PR #5). Copy its folder layout, timeline shape and caption builder.

Last updated 2026-10-25, from the user's notes on blacktongue v1 to v4.

## 1. What an episode is

- One claimed Wall per episode, as it appears on cents.vision/collectors.html under the Claimed filter.
- The tone is matter-of-fact. Each episode just walks through what that collector has: standout Cents, Sets and badges.
- Don't add essayistic framing or a reflection at the close. The user cut "the traits were named by collectors…" and "every Wall is a record that keeps changing".
- The length is whatever the Wall needs. blacktongue runs about 60 to 70 seconds.
- One thread per episode.

## 2. What may appear

- **Allowed:** only what the claimed Wall shows publicly:
  - the name exactly as the card renders it
  - the Cents, the Sets, and the badges
- **No wallet address**, ever. When capturing cents.vision, hide `.collector-wallet`.
- **Never use `wallets-names.json`.** Those are Council-only names given without consent. Block `**/*wallets-names*` when capturing pages.
- **No prices, no finances, no speculation.**
- **Never link sovrn.art.**
- **Real Cents only.** Use the inscription images, or the high-res fronts from cents.vision. Never use AI coins.
- **The artist wallet is not a collector wallet**, and the audience knows this.
  - If only the artist wallet and this collector hold a Set, say the collector is "the only collector to hold one of these rare … Sets".
  - Don't list the artist wallet as a holder.
- **Date every claim that can change.** Sets held, holder counts, Diamond Hands and claims all change daily. Say "As of <Month Year>". Re-fetch the data before an episode locks, and put the absolute date in the credits.
- **Wording:**
  - Say "pre-1983", never "pre-1982".
  - CENTS has no ending.
  - Use the past tense for Rutherford Chang.
  - Never imply Chang's intent.
- **Pronouns:** narration needs none. If one is needed, use they/them unless the user has stated otherwise.

## 3. Structure (the order that worked)

1. **Open on the Wall.** "This is the Wall of NAME." It sits over a cents.vision screenshot of that Wall's card.
2. **Zoom to the signature Cent on the screenshot.** Once that sentence ends, the camera zooms onto the signature Cent on the card. Only then does the film cut to the individual view of that Cent: its number, year, and its traits ("…and is a Ghost Cent").
3. **Count and span:** "The Wall holds N Cents, from YEAR to YEAR." Then the size club, zooming onto the club badge, with the club's range ("…which puts it in the Dime Club, for ten to twenty-four Cents").
4. **Standout Cents.** For each one, say what makes it rare, as "one of only N" with a measured N. Where the trait sits in one place on the coin, zoom into it (see §4).
5. **Mint-year badges:** Wheat, 1971 Club, 1969 Club, 1/1 Year, 1/1 Mint, 1/1 Trait Combo. Zoom onto the badge, then show the Cents behind it.
6. **Sets.** Zoom onto each Set badge on the screenshot as the Set is named, then show the Cents that complete it as each one is named.
   - Explain a Set's ceiling when it is the point, for example "Only nine Full Spectrum Sets can exist, as there are only nine Full Gold Cents."
7. **Remaining trait tags** (Ghost x N, Vandalized x N, …). Show the Cents, and use the tag's own text as the subtitle.
8. **Behaviour badges:** Diamond Hands and Mint Keeper. Zoom onto the badge and give its meaning in plain words (see §6).
9. **Close.** "Find all of the Collector Walls on cents.vision under Collectors."
   - It sits over the cents.vision Traits Lab screenshot (`films/wall-blacktongue/data/traits_lab.png`).
   - The camera makes **one** zoom, onto "Collectors" in the menu, as the word is spoken. Add no other move before it.

**Cover every badge on the card, as far as it makes sense.**
- Skip a badge only when another part of the film already shows it. blacktongue's "Full Patinas held" badges, for example, are already shown by the Full Spectrum Set.
- "Years A-B" is covered by the count-and-span line.
- "Patina N" is a total count of patina traits across the Wall (`patinaCount` in collectors.html). It has no user-facing meaning yet, so leave it out unless the user asks for it.

## 4. Camera and motion

- **Never open on black.** Many platforms use the first frame as the preview. The opening shot is fully visible at frame 0: `OpeningShotCtx` in `src/style/motion.ts` turns off the fade-in for the shot at frame 0. After rendering, check that frame 0 of the MP4 is not dark.
- **Spin Cents flat in 2D only.** Use `CentTurn maxTilt={0}`. Never use a 3D tilt.
- **Zoom to show the trait.** When narration names a trait that sits in one place on the coin (a date, a mint mark, a contamination spot, a die feature), zoom onto that part of the coin.
  - Use `WallStandout` with `src: "hires/<n>.webp"` and `zoom: {at_phrase, box: [x0,y0,x1,y1] as fractions of the image, mark: true}`.
  - Measure the box on the image; don't guess it.
  - Traits that cover the whole surface (full gold, full desert and other full patinas, Ghost, a coin scratched all over) get no zoom.
- **Zoom onto badges** on the Wall screenshot with `WallShot`.
  - Use `moves: [{at_phrase, box, mark: true}]`, with the box measured in screenshot pixels.
  - The copper outline (`mark`) shows the eye which badge is meant.
  - Make one move per idea. A move with no reason (for example, the menu bar before "Collectors") confuses.
- **The zoom must be readable.** The 300px inscription images go soft past about 500px on screen. For any zoom on a Cent, use the 1050px front: `https://cents.vision/pics/frontswebp/<n>.webp`, kept in `/mnt/project-files/*/highres/`. If your container can't reach cents.vision, ask the coordinator for a helper fetch.
- Screenshots never sit under captions. `WallShot` ends its area at y=1330.

## 5. Narration, captions, delivery

- **Voice:** the user's ElevenLabs voice "eo" (`G9J6fFeGgUrIramcuC3q`), model `eleven_v4`.
- **TTS text:**
  - Spell numbers out ("fifty-one eighty-five", "October twenty twenty-six").
  - Say "cents dot vision".
  - Keep `audio/tts_text.txt` beside `script/voiceover.txt`.
- **Transcribe the chosen take** with scribe_v1 (free).
  - Check it word for word against the TTS text.
  - Also run a control with one word changed, which must fail. A normalizer that deletes newlines glues words together, so replace punctuation with spaces.
- **Audio:** `loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur=2.5`, 48 kHz mono.
- **Captions:**
  - `captions/build_cues.py` maps the spoken numbers back to their written forms.
  - It refuses to run unless the joined cues equal `voiceover.txt` exactly.
  - Cues break at sentence and shot boundaries.
  - Captions must be safe on mobile.
- **Timeline anchors** are phrases from the alignment.
  - They must be unique. Use four words or more when a phrase repeats.
  - A move's phrase must fall after the start of its shot.
- **Before rendering:** render stills of every shot. `SafeText` fails a render when a label wraps past its line count, so shorten the label rather than the check.
- **Render** captioned (`VideoCaptioned`) and clean (`Video`), plus an SRT.
  - Use `--browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`.
  - Deliver to `/mnt/project-files/collector-wall/wall-<name>_vN_{captioned,clean}.mp4` and `_vN.srt`.
- **Numbering:** each revision is a new numbered version. Never overwrite an earlier one.
- **Git:**
  - Work on the episode branch and open a draft PR.
  - Never push to main without asking.
  - Restore the root symlinks after `film.py switch` with `git checkout -- captions exports review script timeline`.

## 6. Badge meanings (as cents.vision words them)

These come from `/mnt/project-files/collectors/README.md`.

| Badge | Meaning |
|---|---|
| Dollar / Half Dollar / Quarter / Dime / Nickel Club, Pocket Collection | 100+ / 50 to 99 / 25 to 49 / 10 to 24 / 5 to 9 / 1 to 4 Cents |
| Wheat N | holds N wheat pennies (minted 1958 or earlier) |
| 1971 Club / 1969 Club | holds a Cent from that year |
| 1/1 Year, 1/1 Mint, 1/1 Trait Combo | unique for its mint year / its year and mint mark / its two-trait combination |
| Diamond Hands | held its current position for at least a year with little to no selling |
| Mint Keeper x N | minted N Cents and still holds them, never sold |
| Set badges | per `set-counts.php` at the cents.vision root; check holder counts there |

## 7. Data and checks

- **Source:** the per-Wall data is in `/mnt/project-files/collectors/claimed_walls.json` (39 Walls). Snapshot the episode's Wall into `films/wall-<name>/data/wall.json` with no wallet address.
- **Verify every figure** before it goes in the script: every "one of only N" and every Set ceiling, checked against `raw/merged-new2.json` and `raw/set-counts.php`.
- **Screenshot:** capture the Wall card at 1080 px wide with the wallet line hidden. `cents-vision-capture` in project memory has the Playwright recipe. Measure every box you zoom to.
- **Failures:** record them with the failure-shapes skill. Before posting any link, run the link-safety check.
