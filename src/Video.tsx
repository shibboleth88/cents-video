import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { COLOR } from "./style/tokens";
import { ModeCtx, type RenderMode } from "./style/Safe";
import { REGISTRY, CaptionLayer, type ComponentName } from "./style/components";
import { resolveShots, type Alignment, type Timeline } from "./lib/timeline";

export type Props = {
  timeline: Timeline;
  alignment: Alignment;
  assets: Record<string, { path: string; motion: boolean; subject: string }>;
  cues: { start: number; end: number; text: string }[];
  mode: RenderMode;
  captions: boolean;
  voiceover?: string;
};

export const Video: React.FC<Props> = ({ timeline, alignment, assets, cues, mode, captions, voiceover }) => {
  const shots = resolveShots(timeline, alignment, 30);
  return (
    <ModeCtx.Provider value={mode}>
      <AbsoluteFill data-canvas-root="1" style={{ background: COLOR.bg }}>
        {voiceover && mode === "full" ? <Audio src={staticFile(voiceover)} /> : null}
        {shots.map((s) => {
          const name = (s.component ?? (s.asset_id ? "AssetShot" : "")) as ComponentName;
          const C = REGISTRY[name];
          if (!C) throw new Error(`${s.shot_id}: unknown component "${name}"`);
          const asset = s.asset_id ? assets[s.asset_id] : undefined;
          if (s.asset_id && !asset)
            throw new Error(`${s.shot_id}: asset_id "${s.asset_id}" is not in assets.json`);
          const props: Record<string, unknown> = {
            ...s.props,
            ...(asset ? { src: asset.path, motion: asset.motion } : {}),
          };
          return (
            <Sequence key={s.shot_id} from={s.fromFrame} durationInFrames={s.durationInFrames} name={s.shot_id}>
              {/* @ts-expect-error props are validated against the schema, not the type system */}
              <C {...props} />
            </Sequence>
          );
        })}
        {captions ? <CaptionLayer cues={cues} /> : null}
      </AbsoluteFill>
    </ModeCtx.Provider>
  );
};
