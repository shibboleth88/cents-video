import React from "react";
import { Composition, registerRoot } from "remotion";
import { CANVAS } from "../style/tokens";
import { Animatic, DURATION as ANIMATIC_DURATION } from "./Animatic";
import { FilmCaptioned, FilmClean, DURATION } from "./Film";

/** Secret History of a Penny. Its own root, so it never touches the shared film
 *  root or the top-level symlinks.
 *    npx remotion render src/secret-history/index.ts Film out.mp4
 *    npx remotion render src/secret-history/index.ts FilmCaptioned out.mp4 */
const base = { width: CANVAS.width, height: CANVAS.height, fps: CANVAS.fps };
const Root: React.FC = () =>
  React.createElement(React.Fragment, null,
    React.createElement(Composition, { ...base, id: "Animatic", component: Animatic, durationInFrames: ANIMATIC_DURATION }),
    React.createElement(Composition, { ...base, id: "Film", component: FilmClean, durationInFrames: DURATION }),
    React.createElement(Composition, { ...base, id: "FilmCaptioned", component: FilmCaptioned, durationInFrames: DURATION }),
  );
registerRoot(Root);
