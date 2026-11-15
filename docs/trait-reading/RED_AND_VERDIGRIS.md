# Reading red and verdigris on a Cent's photo

v0.1, 2026-11-15. Written in the thread "Make the Cent #8820 video" at shibboleth's request ("add this knowledge about identifying red and verdigris to the knowledge base for future videos"). shibboleth sits on the Trait Council. Everything under "What shibboleth taught" is their reading of Cent #8820. Everything under "What the measurements show" was measured on one photograph of one Cent, so treat it as a lead, not a rule.

Use this before choosing zoom areas for a red or verdigris trait in any film (One Cent, Collector Wall, What to add next). Traits are read from the **front** only.

## 1. The Atlas definitions (the source of truth)

From the Traits Atlas v1.1, `films/traits/script/atlas/red.txt` and `verdigris.txt` in shibboleth88/cents-video. Credit: "Traits Atlas, CENTS Trait Council".

**Red patina**
- "A red to reddish-brown surface film resulting from oxidative conversion of copper."
- Color: "Scarlet to russet tones; sometimes veering into brick, sienna, or dull crimson. Highlights often remain copper-bright, while recessed zones deepen to earthy reds or maroons."
- "Red Patina marks a transitional oxidation phase between bright copper and darker patinas."
- Grades: Notable, "Isolated but clearly visible reddish films or blushes, often in selected fields; roughly from the minimum threshold up to ~20% of the surface area." Significant, "Red patina is a major visual actor, with uneven but strong red toning across multiple zones; approximately ~20–70% coverage, or a smaller area with particularly saturated red chroma." Full, "Red tonality is the dominant surface condition with coherent continuity across the coin; generally > ~70% coverage, reading as a clearly “red” cent at first glance."
- Atlas examples: #4075 Notable (minimum), #9507 Significant, #9427 Full. Tonings: #1808 bright scarlet, #4236 burnt sienna, #8533 deep maroon.

**Verdigris**
- "Vivid green-to-teal patina formed by long-term oxidation of copper; valued for painterly variation."
- "On CENTS, it often pools in low-relief areas and along lettering."
- Grades: Notable, "Localised but clearly visible patches or films, typically emerging in multiple zones; roughly from the minimum threshold up to ~20–30% of the face area." Significant, "Verdigris is a major visual actor with strong presence, but not yet fully dominant; approximately ~30–70% coverage or a smaller area with exceptional chromatic intensity." Full, "Verdigris is the dominant surface condition, forming continuous regions that visually define the coin; generally > ~70% coverage with a clear green/blue-green read at first glance."
- Atlas examples: #2389 Notable (minimum), #3272 Significant, #3981 Full. Tonings: **#1047 silver-grey**, #5127 greenish, #8641 bluish.

## 2. What shibboleth taught, on Cent #8820 (2026-11-15)

#8820 is 1972, no mint mark, Significant Red and Notable Verdigris. Picture: `img/8820_zoom_plan_v0.4.jpg` (untouched photo on the left, the marks on the right).

**Verdigris comes in two looks on this Cent, and both count.**
- Bright green to teal, in the lettering (IN GOD WE TRUST, LIBERTY) and along the rim. This is the look the Atlas describes ("pools in low-relief areas and along lettering").
- **Grey-green patches on the portrait** (Lincoln's temple, cheek, jaw and collar). shibboleth: "yes those patches you note are verdigris". They are dull and low in saturation, closer to the Atlas's silver-grey toning (#1047) than to bright green. Don't skip them because they aren't vivid.

**Red comes in two forms on this Cent: spots and patches.**
- **Red spots:** fine dark-red to maroon speckles, scattered dots on the copper. On #8820 they cluster on Lincoln's cheek and jaw and in the field in front of the face. shibboleth pinned four (`img/8820_red_spots_and_patches.jpg`, top row).
- **Red patches:** broader crimson-to-rose blushes, redder and a little darker than the orange-brown copper around them. On #8820: behind and above Lincoln's head, on the upper face, and a long patch down the right arc, from the upper right field past the date to the rim. shibboleth pinned five, including the top and bottom of the right-arc patch (bottom row).
- shibboleth's first pins were the spots only, then: "the spots I marked are indeed red, but there's also red patches". So one look at the most obvious red is not enough. Look for both forms before choosing the zoom areas.

## 3. What the measurements show (one photo, one Cent)

These are leads for finding candidate areas, never a substitute for someone looking. Code and numbers are in the #8820 thread; the images are in `img/`.

| Test | What it caught on #8820 | What it missed |
|---|---|---|
| **Green test:** pixel G ≥ R − 5 and G > B, inside the coin | Bright verdigris in the lettering and rim (3,311 px). `img/8820_green_test.jpg` | **All the grey-green face patches.** A cheek patch measured RGB (111, 99, 83), hue about 34°, saturation 0.25: olive-grey, so a "green" rule can't see it |
| **Red-patch test:** blur 10 px, then hue below 15° and saturation above 0.35 | 4 of shibboleth's 5 patch pins (the fifth sat at 15.5°), about 4.6% of the coin. 0 of 4 control points in ordinary field. `img/8820_hue_test.jpg` | **The red spots** (3 of 4 outside the mask): the blur averages fine speckles away. The fourth spot is inside a patch |

- On this photo the coin's median hue was 18.4°; the patches ran about 11–15°, so they are a few degrees toward crimson from the coin's own base. **Compare a patch with the same coin's base colour, not with a fixed number.** Lighting and the camera differ between photographs.
- The spots need a different test: small dark dots with a red hue. None was built, and the eye found them easily.

## 4. How to choose zoom areas for these traits

1. Read the Atlas grade first, so the zoom shows what the grade means (Significant red is "across multiple zones": show more than one).
2. Look at the 1050 px front at full size for both forms of each trait: bright and grey-green verdigris; red spots and red patches.
3. Use the colour tests only to find candidates, and never put a test's output in front of the user without a legend and the untouched photo beside it. *(The #8820 v0.1 zoom plan painted the green test's pixels neon with no legend, and the user reasonably asked why the coin had bright green on it.)*
4. When unsure, ask shibboleth to pin the areas on a plan image. Convert the pins to coordinates on the 1050 px front (know your plan image's panel offsets and scale) and save them as JSON beside the episode, as `single-cent-series/8820/8820_zoom_boxes_v0.2.json` does. The build then uses the user's points, not a guess.
5. Label each zoom by what it shows ("red patch, right arc"; "verdigris, lettering"), and keep to the front.

## 5. Open, not yet known

- Whether the Trait Council distinguishes spots from patches when it grades red, or counts both toward coverage. This note only records that both are red on #8820.
- Whether the red-patch hue offset holds on other Cents and other photographs. Test it on the Atlas examples (#4075, #9507, #9427) before relying on it.

## Revision log

- v0.1, 2026-11-15: created from the #8820 thread (shibboleth's answers 00:19Z–00:23Z).
