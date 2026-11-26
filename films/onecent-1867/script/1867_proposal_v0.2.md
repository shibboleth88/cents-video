# One Cent #1867: proposal v0.2 (script for review, not voiced)

2026-11-25. v0.1 is kept beside this file and holds the data table, the quote checks and the picture plan; they still stand except where this file says otherwise.

## 1. What changed from v0.1 (shibboleth, 2026-11-25 02:33Z)

1. Cut: "In the Traits Atlas, Significant means "a major visual actor", but "not yet fully dominant"." This sets aside, for this episode, the series rule of 26 Oct 2026 that a named grade is explained (brief §5). The Atlas plate under it goes too.
2. Cut: "As money, any cent was as good as any other. As a Cent, none is."
3. **The quotes come earlier**, so that viewers who know the series see at once that this one is new. The concept card and both quotes now follow the opening, at about 0:12 to 0:35 instead of after the traits (about 1:30 in v0.1).
4. **A new opening format** (asked as a decision in the thread; see §4).

"Traits Atlas" is now first named in line 9, so that line gives the full name.

## 2. Script v0.2

About **319 spoken words** (numbers spelled out): about 1:50 to 2:08 of narration, so about **2:10 to 2:30** finished. Under 3:00.

1. Cent #1867. A penny dated 1964, with no mint mark, generally indicating the Philadelphia mint. *(opening card, one 3DCENTS turn; then the date and where a mint mark would be)*
2. Circulation leaves traces. *(concept card)*
3. In the words of Emily Watlington, writing on Rutherford Chang in *Art in America*: "Circulation is another of Chang's key themes: how do things change as they move through the world?" *(lit quote card)*
4. Rhea Myers, in her book *Proof of Work*, quotes the artist Barbara Kruger: "Money is an information-destroying medium." *(lit quote card)*
5. A circulated copper cent is the exception. Three traits record where Cent #1867 has been: two patinas and a contamination.
6. A dark band of Significant Obsidian crosses the upper left, over the motto and Lincoln's head.
7. Green patches of Significant Verdigris gather on his cheek, behind his head and at his collar.
8. 220 Cents carry Significant Obsidian, and 376 Significant Verdigris. 29 carry both.
9. Both patinas grew from the copper. In the Traits Atlas, a patina "arises from internal chemistry".
10. The third trait came from outside: Contaminated, Alien Secretion. In the Atlas, contamination is "matter imposed upon copper", and Alien Secretion names "unidentifiable translucent or greenish films".
11. The Trait Council names such residues by reading the surface, without testing it. In the Atlas's words: "The subtrait names are therefore not claims of chemistry, but field names – tools for seeing."
12. 79 Cents carry Alien Secretion, and 70 of them carry verdigris too.
13. No other Cent has exactly this set of traits.
14. Cent #4421 is dated the same year, and is close to mint state. Its portrait is clean and bright.
15. In March 2024, Chang inscribed the image of Cent #1867 on a satoshi, and the physical coin was melted into CENTS Block Copper.
16. Released at one satoshi, the Cent's value moved from a figure set by the state into an ongoing process, set again each time someone reads it, keeps it or lets it go.
17. Cent #1867, a great Cent. *(closing card, one turn)*

## 3. How it reads in order (video-concept-relations passes, on v0.2)

**Order.**
- Name, concept, question, claim, exception, evidence. The Watlington question (3) is answered in two steps: Kruger's claim about money (4), then "A circulated copper cent is the exception" (5), and the traits that follow are the evidence. The quotes now frame the reading instead of closing it.
- **Motive check.** Chang's theme (3) now comes before this Cent's traces. Could it be heard as Chang choosing or making the marks? The quote is about his work in general; lines 9 and 10 then give the marks their causes in the Atlas's words (the copper's own chemistry; matter from outside). Nothing says he chose this coin.
- **The comparison (14) has lost its payoff.** In v0.1, "As money, any cent was as good as any other" followed it. Now #4421 stands as the picture of a cent with almost no record, after line 5's "the exception". Line 15 names #1867 again, so "the image" cannot be heard as #4421's. If the comparison feels loose, cutting line 14 saves 18 words and one shot.

**Referents.** Line 5's "the exception" points at line 4's claim. Line 11's quoted "therefore" has its premise in the line's first sentence (as in v0.1). Line 15 names the Cent (the #1328 lesson: "this one" after a comparison Cent).

**Value.** Kruger's line and line 16 carry it: money that forgets, a cent that kept a record, and a value set and set again. With line 2 of v0.1 gone, the state's one cent is named only in line 16 ("a figure set by the state").

**Shape.** Unchanged at the end: the last idea before the name is a process that goes on.

## 4. The opening format (decision in the thread)

Recommended: **Look C** from the series-look work (PR #25; shibboleth called it "quite good", 28 Oct 2026; the title arrangement was never picked). Frame 0: the Cent dimmed under a copper play button marked CENTS STORY TIME, Fraunces type, warm black; the button is pressed, a ripple leaves it, the Cent turns once. Viewers have not seen it in an episode, so it reads as new from the first frame. Samples on #2616: `/mnt/project-files/look/look-C_v3.1_Below.mp4`, `…_AboveBelow.mp4`, `…_Line.mp4`, `look-C_v3_arrangements.jpg`.

The alternative is the current card, with the Watlington question lit over a close-up of #1867's surface at frame 0, before the turn.

## 5. Still open from v0.1

1. The Alien Secretion area (box A? on `1867_zoom_plan_v0.1.jpg`).
2. Line 12 (70 of the 79 also carry verdigris): keep or cut.

## 6. Opening rehearsal (2026-11-25, silent, stand-in timing)

Built while the opening decision is open, on the recommended option (Look C, title below). Stills: `1867_opening_lookC_stills_v0.1.jpg`; silent preview of the first 35 s: `1867_opening_lookC_preview_v0.1.mp4` (stand-in word timings, no voice).

- **Opening** (`StoryOpen`, src/style/storyopen.tsx): frame 0 is the Cent under the copper play button and CENTS STORY TIME, "Cent #1867" in Fraunces below it and the inscription number under a copper rule. The button is pressed at about 0.5 s and the Cent makes one 3DCENTS turn. The narration starts at 1.2 s, once play is pressed. The turn hands over to the photo, and the coin's outline becomes a lens with a copper rim for the year and for where a mint mark would be (boxes 1 and 2 of the zoom plan). The reads replace the inscription line as copper chips.
- **Concept and quotes in the same look** (`StoryCard`): the concept takes the name's place under the coin; for the quotes the coin rises to the top and the quote is set in Fraunces italic on a copper rule, each word lit as it is spoken, the speaker in caps and the source in italic. So the new format runs from frame 0 to the end of the Kruger quote (about 0:35); the rest of the film is not built yet.
- **Spoken form fixed:** the voice text said "Cent eighteen sixty-seven"; every earlier episode says "Cent number …" for "#". The voice text now says "Cent number eighteen sixty-seven" and "Cent number forty-four twenty-one". The written script is unchanged.
- **A shared caption fix:** captions held every hyphen, so "information-destroying" became one long word and pushed the caption to three lines, out of the safe area (the gate caught it). A hyphen now holds only inside a number ("thirty-three"); other compounds may break at the hyphen, as in print.
- **The turn costs a pause:** the camera cannot look at the year until the turn ends (about 6.1 s), so after "Cent number eighteen sixty-seven" there is a pause of about 3 s over the turn. The alternative is a shorter turn or a line over it.

## Revision log

- v0.1, 2026-11-25: `1867_proposal_v0.1.md`.
- v0.2, 2026-11-25: shibboleth's two cuts; quotes moved up to follow the opening; new opening format proposed (Look C).
- v0.2 §6, 2026-11-25: opening rehearsal in Look C (stills and a silent preview); spoken "Cent number"; caption hyphen fix.
