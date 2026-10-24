# The Sets — film 3 (treatment stage)

A film about the Trait Council's Sets, shown through the real Cents that make
each one up. **Not scripted or recorded.** The treatment, with three angles for
the user to pick from, is the Claude Doc "CENTS Sets film: brief and treatment
v0.1" (https://claude.ai/artifact/FSK9j38yEYMs1jiy384n33).

Set requirements follow cents.vision/sets.html as transcribed in cents-bot
`knowledge/cents-vision-guide.md`. Counts come from the Sep 2026 trait export.

## Measured, 2026-10-24

- 1949 and 1954 have one Cent each, so the 1940s Set, the 1950s Set and Full
  Decades can each be held by at most one collector at a time.
- Narrowest ingredients: Full Gold 9, Scotch Tape 7, S mint 60, Full Verdigris 15.
- Holder counts exist only as the 9 Sep 2026 snapshot of set-counts.php
  (Full Decades 0). cents.vision is unreachable from the cloud container; any
  holder count in narration needs a fresh read and an `as_of`.
- All 10,000 on-chain images sit on a white square. `pipeline/stage_cents.py`
  cuts each to a circle. Before a dust-removing opening was added, 4 of the
  10,000 (#2476, #2553, #6401, #9345) measured non-square and were refused;
  after it, all 10,000 measure 242–250px square.
- Under ~60px a Cent's trait is not visible. `CentImage` refuses to draw one
  smaller unless the shot declares it `texture`. The floor fired on the first
  real layout: four equal columns put the 71 Full Reds at 54px.

## Files

- `build_pools.py` → `data/pools.json`: the Cent numbers behind every Set ingredient.
- Shared components: `src/style/grids.tsx` (`CentImage`, `CentGrid`, `fitGrid`).
- Bench: `src/lab/` renders the components without a recording:

      cd <repo> && python3 pipeline/stage_cents.py --src <sovrn-onchain>/cents <numbers…>
      npx remotion still src/lab/index.ts FullsWall out.png --frame=90

  In the cloud container, add
  `--browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`,
  because Remotion's own browser download host is blocked.
