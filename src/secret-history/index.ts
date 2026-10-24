import React from "react";
import { Composition, registerRoot } from "remotion";
import { CANVAS } from "../style/tokens";
import { Animatic, DURATION } from "./Animatic";

/** Secret History of a Penny, rough animatic. Its own root, so it never touches
 *  the shared film root or the top-level symlinks.
 *    npx remotion render src/secret-history/index.ts Animatic out.mp4 */
const Root: React.FC = () =>
  React.createElement(Composition, {
    id: "Animatic", component: Animatic, width: CANVAS.width, height: CANVAS.height,
    fps: CANVAS.fps, durationInFrames: DURATION,
  });
registerRoot(Root);
