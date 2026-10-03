import React from "react";
import { Composition } from "remotion";
import { CANVAS } from "./style/tokens";
import { Video } from "./Video";
import { resolveShots, totalFrames, type Alignment, type Timeline } from "./lib/timeline";
import timelineJson from "../timeline/timeline.json";
import alignmentJson from "../script/alignment.json";
import assetsJson from "../timeline/assets.json";
import cuesJson from "../captions/cues.json";

const timeline = timelineJson as unknown as Timeline;
const alignment = alignmentJson as unknown as Alignment;
const assets = assetsJson as unknown as Record<string, { path: string; motion: boolean; subject: string }>;
const cues = cuesJson as unknown as { start: number; end: number; text: string }[];

/** Duration comes from the recording. Nothing in this file names a number of seconds. */
const DURATION = totalFrames(resolveShots(timeline, alignment, CANVAS.fps));

const base = { width: CANVAS.width, height: CANVAS.height, fps: CANVAS.fps, durationInFrames: DURATION };
const common = { timeline, alignment, assets, cues, voiceover: "vo.wav" };

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Video" component={Video} {...base}
      defaultProps={{ ...common, mode: "full" as const, captions: false }} />
    <Composition id="VideoCaptioned" component={Video} {...base}
      defaultProps={{ ...common, mode: "full" as const, captions: true }} />
    {/* Text layers on black. The safe-area gate measures this export in pixels. */}
    <Composition id="EssentialOnly" component={Video} {...base}
      defaultProps={{ ...common, mode: "essential" as const, captions: true }} />
  </>
);
