# Collector Wall videos: best practices

This is the one source for the format of every Collector Wall episode. Read it before you write a script. Episode threads send their lessons back to the "Make Collector Wall video series" thread, which folds them in here and in the repo copy (`docs/collector-wall/BEST_PRACTICES.md` in shibboleth88/cents-video).

The reference episode is **blacktongue** (`films/wall-blacktongue/` on branch `claude/project-thread-nkzn17`, PR #5). Copy its folder layout, timeline shape and caption builder.

Last updated 2026-10-25, from the user's notes on blacktongue v1 to v4 and the Daidatep thread's first findings. 2026-10-26: §5 "Delivery check" added from the GPT WBWA reel handover. 2026-10-27: narration voice changed to "eee" (§5); showcase opener is the series opening (§3); 3DCENTS credit wording approved (§4); badge zooms get the opener-style highlight (§4a); audit against the day's decisions: lead with the Wall's standout fact (§1), graded traits, fronts only, Cents on black, Daidatep (§2), no long still holds (§4a), dated snapshots (§4a).

## 1. What an episode is

- One claimed Wall per episode, as it appears on cents.vision/collectors.html under the Claimed filter.
- The tone is matter-of-fact. Each episode just walks through what that collector has: standout Cents, Sets and badges.
- Don't add essayistic framing or a reflection at the close. The user cut "the traits were named by collectors…" and "every Wall is a record that keeps changing".
- **Lead with what is extraordinary about this Wall.** When a Wall has one standout distinction, build the episode around it and keep the rest short. For ScrappyT, that is one Cent of every one of the 19 visual traits (user, 2026-10-27). Before building on such a claim, check it against every claimed Wall, the artist wallet included. ScrappyT's holds: no other Wall has all 19, not even the artist wallet, which has no Iridescent.
- The length is whatever the Wall needs: blacktongue v5 is 84 s, ScrappyT about 2 min.
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
- **Graded traits:** when a film names a grade (Notable, Significant, Full), say what the grade means, worded from the Traits Atlas (`films/traits/script/atlas/<trait>.txt`). Credit "Traits Atlas, CENTS Trait Council". (User, 2026-10-26.)
  - **Traits are read from the front only.** Every trait zoom or piece of evidence uses the 1050px front. A back may appear for another reason, such as the wheat flip, but never as evidence of a trait. (User, 2026-10-26.)
  - **Cents on black.** Show Cents cut out on black (`clipPath: circle(40.5%)`), not on their white image squares. The exception is the Wall card itself, which is drawn white as the site draws it. (User, 2026-10-26.)
- **Daidatep** is the Council name of Martin Lehnen, who built cents.vision (confirmed for the project, 2026-10-25). His Wall's episode may say so. Credit the site as "Images: Rutherford Chang via cents.vision (site by Dr. Martin Lehnen)", as in the One Cent series.
- **Pronouns:** narration needs none. If one is needed, use they/them unless the user has stated otherwise.

## 3. Structure (the order that worked)

1. **Open on the Wall, with the showcase opener (series format, user 2026-10-27).** "This is the Wall of NAME." Frame 0 must already read as a video with more to come, not a still. The user asked for this in the ScrappyT thread, then asked for blacktongue and Daidatep to be redone with it.
   - **What it shows from frame 0:**
     - the Wall card (`WallBoard`, `show: "card"`), with the signature Cent turning in its slot as its 3DCENTS spin;
     - the mosaic Cents lighting up one after another, with a copper ring, 5 frames apart;
     - at the same time, every badge in reading order (tags, sets, fulls, meta), 3 frames apart;
     - a thin copper progress bar across the top.
   - It runs until "Its signature Cent". The card then zooms onto the signature Cent, which carries a copper mark, and the film cuts to that Cent on its own (`WallStandout` with the same `clip`).
   - **Shot:** `WallOpener` (src/style/wallopener.tsx, from PR #14):
     ```json
     {"component": "WallOpener", "start": {"at_start": true}, "end": {"at_phrase": "number <signature in words>"},
      "props": {"variant": "showcase", "wall": "<slug>", "show": "card", "until_phrase": "Its signature Cent",
       "moves": [{"at_phrase": "Its signature Cent", "target": {"cent": <n>, "in": "signature"}, "mark": true}],
       "progress": {"total_frames": <round(alignment duration * 30)>},
       "clip": {"src": "3dcents/<n>-360-30fps.mp4", "width": 1080, "height": 1920, "frames": 150,
                "coin": {"cx": 539.5, "cy": 959.5, "d": 776}, "credit": "3D render: 3DCENTS by sinvalli"}}}
     ```
   - **It needs the signature Cent's 3DCENTS spin** (§4), so ask the user to export it at the start of an episode. It throws without a clip or a credit.
   - **Key the clip for the white card.** On the card, the opener uses an alpha copy of the spin, not the black-background mp4: with a dark disc, the coin shows a black circle whenever it turns edge-on. Make it from the 30 fps retime:
     ```bash
     ffmpeg -i cent-<n>-360-1080x1920-30fps-retimed.mp4 -vf "format=yuva420p,geq=lum='lum(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='clip((lum(X,Y)-18)*40,0,255)'" -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0 -b:v 4M cent-<n>-360-1080x1920-30fps-alpha.webm
     ```
     Then set `"src": "3dcents/<n>-360-30fps-alpha.webm", "alpha": true` in the opener's clip. The render's black sits at luma 16, so a threshold near 0 keys nothing. The `WallStandout` shot that follows stays on black and keeps the mp4. Keep both files in `/mnt/project-files/collector-wall/3dcents/`.
   - The credit under the card fades out before the zoom onto the signature Cent (PR #14 a3ee33b), so it never sits on the zoomed badges.
   - **Still being tuned:** the user may change the speed, the order or the progress bar in the ScrappyT thread. Take the current settings from that thread. Reference renders: ScrappyT v1, and `/mnt/project-files/collector-wall/openers/opener-showcase_v1.mp4`.
   - The earlier opening, a cents.vision screenshot of the card zoomed onto the signature Cent, is retired for new episodes.
2. **Zoom to the signature Cent on the card.** Once that sentence ends, the camera zooms onto the signature Cent on the card. Only then does the film cut to the individual view of that Cent: its number, year, and its traits ("…and is a Ghost Cent").
3. **Count and span:** "The Wall holds N Cents, from YEAR to YEAR." Then the size club, zooming onto the club badge, with the club's range ("…which puts it in the Dime Club, for ten to twenty-four Cents").
4. **Standout Cents.** For each one, say what makes it rare, as "one of only N" with a measured N. Where the trait sits in one place on the coin, zoom into it (see §4).
5. **Mint-year badges:** Wheat, 1971 Club, 1969 Club, 1/1 Year, 1/1 Mint, 1/1 Trait Combo. Zoom onto the badge, then show the Cents behind it.
   - **Wheat:** flip one wheat Cent to its back with `CentFlip` in wall.tsx, so viewers see what "wheat" means. The flip is a flat 2D flip from front to back, using cents.vision `pics/backswebp/<n>.webp`. (User, 2026-10-25.)
6. **Sets and Fulls.** Zoom onto each Set badge as the Set is named. Then show the Cents that complete it as a Cent row (`CentRow`), each Cent arriving as it is named, the way blacktongue shows its Full Spectrum.
   - The Fulls work the same way.
   - Never show a Set or the Fulls as highlights on the collection rows. (User, 2026-10-25.)
   - **Individuals first, then together.** For a Set named Cent by Cent, show each Cent on its own, large, as it is named. Then gather them into the row. In `CentRow`, set `solo_until: "<phrase>"`: before that phrase each anchored Cent shows alone with its caption, and at the phrase they gather into the row with the readout. The user asked for this for the Full Contamination Set, and it applies to any Set named Cent by Cent. (User, 2026-10-25 13:39Z; added on PR #8.) The solo Cents are large, then the row is smaller. Give each Cent in a `solo_until` row `src: "hires/<n>.webp"` so that solo mode draws it at full stage height, clipped to the coin. Fetch those fronts first. (User, Daidatep v4; PR #8 commit aca40d5.)
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
- **Cents do not rotate,** apart from the two exceptions below. Our own animations show each Cent still. The signature Cent turns only in its 3DCENTS render, in the opener (§3) and in its own shot. `WallCard` and `WallStandout` now default to `spin: 0`. Never use a 3D tilt. (User, 2026-10-25 13:56Z. The earlier rule allowed a flat 2D spin; blacktongue v4 and Daidatep v3 were made under it and are accepted as they are.)
  - Exception: the wheat flip (`CentFlip`) is a separate move and is still used.
  - **Exception: the signature Cent can rotate in a 3DCENTS render.** The user approved this on 2026-10-25 14:13Z. 3DCENTS is sinvalli's tool, not Chang's. sinvalli is happy for the tool and its renders to be used and shared.
    - **Credit (approved by the user, 2026-10-27):** "3D render: 3DCENTS by sinvalli". It sits small under the coin for the whole clip shot, and also goes in the end credits.
    - **Files:** the user exports the spins by hand into "/Users/moobook/Pictures/cents shortlist", using the site's own file names: `cent-<n>-360-1080x1920-25fps-reel` (Daidatep's #9908 came first).
      - Each episode thread copies its file into `/mnt/project-files/collector-wall/3dcents/`.
      - The exports are 25 fps. Retime them frame for frame to 30 fps:
        `ffmpeg -i <in> -vf setpts=N/30/TB -r 30 <out>`
        - This keeps all 150 frames with none duplicated: each frame matches its source at 55 dB PSNR, against 31.8 dB when compared one frame off.
        - The spin becomes 5 s instead of 6.
        - A plain `fps=30` filter duplicates 30 frames and judders.
      - Copy the retimed file to `public/3dcents/` (gitignored).
      - **Shot:** `WallStandout` with `clip: {src, width, height, frames, coin: {cx, cy, d}, credit}`. It arrives with Daidatep v5 (commit a044ca3, PR #8).
        - The clip loops and is scaled so the coin's diameter `d` matches the standard 500px coin.
        - Measure `cx`, `cy` and `d` on frame 0. For the reel export: 539.5, 959.5, 776.
        - The clip's black background drops out with a lighten blend onto a group filled with `COLOR.bg`. Keep that fill: any opacity above it isolates the blend, and the black rectangle shows.
        - It throws with `zoom` or `spin`, or with an empty `credit`.
        - The credit sits under the coin in the body font (mono doesn't fit one line at the 42px floor).
      - **The reverse shows upside down mid-turn.** US cents are struck in coin alignment, so this is correct and not a render bug.
      - Ask the user for the export if it isn't there. Don't screen-record the site.
    - **Facts:** the render makes one full turn about the vertical axis every 6 s. The export offers IG Reel 1080x1920 framing at 720p to 4K. It is rebuilt from the 1050px cents.vision photos, so it carries no more detail than they do, and it is darker and lower in contrast than the photo.
    - **Zoom:** for a trait zoom, still use the high-res photo in `WallStandout`.
    - **Test frames:** in `/mnt/project-files/collector-wall/3dcents-test/`. Project memory `cents-3dcents` has the notes.
    - **Scope:** the "no rotation" rule still applies to our own animations.
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

## 4a. WallBoard: rebuild the Wall instead of screenshotting it

Use `WallBoard` (`src/style/wallboard.tsx`) for every shot that moves around a Wall: zooms to the signature Cent, to a badge, to a Cent in the collection, and scrolls through the whole collection. It redraws the card from data the way collectors.html lays it out, with the "View collection" grid opened beneath it. That makes every zoom sharp, it needs no measured boxes, and it handles a Wall of any length.

**Why not a screenshot for these shots:**
- A screenshot goes soft when the camera zooms into it.
- It only holds one screen of the page.
- Live capture of collectors.html now times out in the cloud container: gstatic is refused, and the `window.firebase` stub no longer lets `state.collectors` load (Daidatep thread, 2026-10-25).

*(Superseded 2026-10-27: this line said a real cents.vision screenshot was welcome for the first second. The opening is now the showcase opener, §3 step 1.)*

**1. Snapshot the Wall's data.** Prefer a fresh dated snapshot: `pipeline/wall_board.py --name <Name> --slug <slug> --snapshot /mnt/project-files/collectors/snapshots/YYYY-MM-DD` (ScrappyT, 27 Oct). Check the Set counts against cents.vision `set-counts.php`; ScrappyT's matched 17/17. The site now renders the patina badge as "Patina count N"; it is still left out (§3). The command writes `films/wall-<slug>/data/wall_board.json` (committed) and `public/walls/<slug>.json` (what the component fetches):

```
cd /home/claude/cents-video
python3 pipeline/wall_board.py --name "<name as claimed>" --slug <slug>
python3 pipeline/wall_board.py --self-test      # all claimed Walls build; two controls go red
python3 pipeline/stage_cents.py --src <sovrn-onchain>/cents <every Cent number on the Wall>
```

- It refuses if a badge count disagrees with the Cents behind it, or if anything wallet-like would be written.
- Run `--self-test` after changing the script.
- Stage every Cent on the Wall. The collection grid shows them all.

**2. Write the shot.** Props: `wall` (slug), `moves`, `highlights`, and `readout` (optional).

```json
{"component": "WallBoard", "props": {"wall": "daidatep",
  "moves": [
    {"at_phrase": "Its signature Cent", "target": {"cent": 9908, "in": "signature"}},
    {"at_phrase": "The Wall holds", "target": {"grid_start": true}},
    {"at_phrase": "a hundred and thirty-two", "until_phrase": "Among them", "target": {"grid_end": true}},
    {"at_phrase": "only one-nine-fifty-five-D", "target": {"cent": 3640}, "mark": true},
    {"at_phrase": "Wheat", "target": {"badge": "Wheat"}, "mark": true}],
  "highlights": [{"at_phrase": "ten wheat pennies", "until_phrase": "Among them", "group": "wheat"}],
  "readout": {"at_phrase": "The Wall holds", "count": {"from": 0, "to": 132, "until_phrase": "Among them", "suffix": " Cents"}}}}
```

**Targets:**
- `{top: true}` is the card at 1:1. It is also the frame before the first move.
- `{card: true}` fits the whole card.
- `{cent: n, in: "signature" | "mosaic" | "grid"}` frames one Cent. The default is the grid.
- `{badge: "<text it starts with>"}` frames one badge. It must match exactly one badge.
- `{grid_start: true}` and `{grid_end: true}` show the first or last rows of the collection.
- `{box: [x0, y0, x1, y1]}` is in board units (1000 wide).

**Moves:**
- A move eases over 18 frames.
- With `until_phrase`, the move pans linearly until that phrase. That is how to scroll.
- `mark: true` outlines the target in copper.
- **No long still holds.** Keep something moving or changing at least every few seconds. ScrappyT v1's Spectrum row sat still for about 10 s while a grade was explained, and its thread flagged it.
- **A badge being talked about gets the opener's highlight (user, 2026-10-27).** When the narration names a single badge and the camera zooms onto it, light that badge up more prominently than the thin `mark` outline. Use the same style as the showcase opener's light-up: a copper ring with a glow, a slight brightness lift, and a small scale-up, held while it is spoken. Until `mark` does this by default on badge targets, add it explicitly in the episode. A `sweep` limited to that badge's row will not do, because it lights the whole row. This applies to every badge zoom (club, Wheat, Sets, Diamond Hands, Mint Keeper, trait tags).
- `zoom` caps the magnification. The default is 2.6.

**What the board shows:** `show: "card"` draws the card alone. The user wants this for the Wall itself: the card should not carry the "N CENTS in this wall" collection rows. `show: "grid"` draws the collection rows alone, which are for singling out Cents (the wheat pennies, a 1955-D). The default "all" draws both and is only kept for older episodes. (User, 2026-10-25; added on PR #8.)

**Highlights:**
- A highlight dims everything else and rings the chosen Cents.
- Use `group` for any key in the board's `groups`: `wheat`, `y1971`, `y1969`, `one_of_one_year`, `one_of_one_mint`, `trait_combo`, `mint_keeper`, `full_mint`, `full_<patina>`, `full_any`, `contamination_one_each`. Use `cents` for an explicit list.

**Readout:** `text`, or a `count` that runs from one number to another during a scroll. It sits below the board.

For a trait you must see on the coin itself (a date, a mint mark), cut from the board to `WallStandout` with a high-res zoom (§4). The board's Cent images are the 300px inscriptions.

## 5. Narration, captions, delivery

- **Voice (from 2026-10-27):** the user's ElevenLabs voice "eee" (`pp4OmJ3yyWS9Jyhejh5f`), via the ElevenLabs MCP (`creative_list_voices` search "eee" finds it). It replaces "eo" (`G9J6fFeGgUrIramcuC3q`), which stays only on episodes already voiced in it (blacktongue, Daidatep); do not re-voice those unless the user asks.
  - **Setting:** model `eleven_v4`, with `[thoughtfully] [calm]` at the start of every line. The user picked this in the #2616 thread, and ScrappyT uses it. *(Correction, 2026-10-27: this line first said `eleven_multilingual_v2`. That was only the model of the cloud test takes in `/mnt/project-files/voice/`.)*
  - **scribe_v1 returns the audio tags as tiny word tokens.** Strip them from the transcript before the word-for-word check and the alignment.
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

### Delivery check (added 2026-10-26, from the GPT WBWA reel handover)

Run on each delivered MP4 before reporting it. Tested on One Cent #6129 v3.1; each check went red on a control (1 s of black prepended; a file cut at 3 MB).

```bash
f=/mnt/project-files/<series>/<file>.mp4
# 1. format: h264, 1080x1920, 30/1, frame count, duration
ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=codec_name,width,height,r_frame_rate,nb_read_frames -show_entries format=duration -of compact=p=0 "$f"
# 2. decodes end to end: must print nothing
ffmpeg -v error -i "$f" -f null -
# 3. first frame not black: YMAX well above 16 (the control gave 16)
ffmpeg -hide_banner -i "$f" -vf "select=eq(n\,0),signalstats,metadata=print:key=lavfi.signalstats.YMAX" -frames:v 1 -an -f null - 2>&1 | grep -o "YMAX=[0-9.]*"
# 4. black and frozen intervals: a list to LOOK AT, not a pass/fail
ffmpeg -hide_banner -i "$f" -vf "blackdetect=d=0.1:pix_th=0.10,freezedetect=n=0.001:d=2" -an -f null - 2>&1 | grep -oE "black_start:[0-9.]+ black_end:[0-9.]+|freeze_start: [0-9.]+"
```

- **Black on our stage is often by design.** The approved #6129 v3.1 has seven dips of 0.2–0.6 s between shots and a dark credits card, all flagged by step 4. A zero count is therefore not the target. Look at a frame inside each interval and fail only a black frame 0, a black run that is not a transition, or a black tail.
- **Also:** look at the last frame; confirm each change the user asked for in the export, not the timeline; on a visual-only revision, keep the audio and compare it with the previous version.
- **Report it as "exported and verified"**, saying which checks ran. Only the user approves.
- More from that handover (repeats, asset usage counts, portraits, press marks, footage labels): `docs/gpt-handover.md` in the repo.

### Practical notes from episodes (Daidatep v1 and v2, 2026-10-25)

- **Fresh container setup:** run `npm ci` in the repo root before the first `npx remotion`.
- **Alignment duration:** `script/alignment.json` must have a `duration` key, set to the length of `vo.wav` (the take plus 2.5 s of padding). Without it, the anchors and caption cutting throw a KeyError.
- **Caption builder:** prefer the generic builder in `films/wall-daidatep/captions/build_cues.py` over the per-episode WRITTEN lists.
  - A table maps each written token (5185, 1968, cents.vision) to its spoken form.
  - Each script word takes the timing of its spoken words.
  - It refuses on any mismatch.
  - Copy it into new episodes and extend the table.
- **Quick stills:** before a full render, use a small Node script that bundles once and calls `renderStill` per timestamp. It is much faster than one CLI call per frame, and the CLI's `--frames` needs a range and a directory.
- **CentRow layout:**
  - For 6 or more Cents, leave `cols` unset so `fitGrid` sizes them. A fixed `cols` with many Cents renders them small.
  - With `labelsUnder` and around 20 or more Cents, set `cols: 6`, or the top row runs into the title.
- **WallStandout captions stay on one line.** A caption that wraps to two lines runs under the burned-in captions.
- **Readouts:** the 84 px readout fits about 8 characters, so SafeText refuses "1 of 2 collectors". Keep the number in the readout ("1 of 2") and put the words in the caption line beneath it.

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

- **Re-fetch first.** Take a dated snapshot under `/mnt/project-files/collectors/snapshots/YYYY-MM-DD/`. It holds the raw files, a `fetch_log`, and `replay.json` from `replay.js`; Daidatep's is the example. The episode's figures and its "As of" date come from that snapshot.
- **Source:** the per-Wall data is in `/mnt/project-files/collectors/claimed_walls.json` (39 Walls). Snapshot the episode's Wall into `films/wall-<name>/data/wall.json` with no wallet address.
- **Verify every figure** before it goes in the script: every "one of only N" and every Set ceiling, checked against `raw/merged-new2.json` and `raw/set-counts.php`.
- **Screenshot:** capture the Wall card at 1080 px wide with the wallet line hidden. `cents-vision-capture` in project memory has the Playwright recipe. Measure every box you zoom to.
- **Failures:** record them with the failure-shapes skill. Before posting any link, run the link-safety check.
