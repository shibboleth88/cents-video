import React from "react";
import { Composition, registerRoot } from "remotion";
import { CANVAS } from "../style/tokens";
import { FilmCaptioned, FilmClean, DURATION } from "./Film";

/** The Gap, a year on. Its own root, so it never touches the shared film root.
 *    npx remotion render src/the-gap/index.ts Film out.mp4
 *    npx remotion render src/the-gap/index.ts FilmCaptioned out.mp4 */
const base = { width: CANVAS.width, height: CANVAS.height, fps: CANVAS.fps };
const Root: React.FC = () =>
  React.createElement(React.Fragment, null,
    React.createElement(Composition, { ...base, id: "Film", component: FilmClean, durationInFrames: DURATION }),
    React.createElement(Composition, { ...base, id: "FilmCaptioned", component: FilmCaptioned, durationInFrames: DURATION }),
  );
registerRoot(Root);
