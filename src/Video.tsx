import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { COLOR } from "./style/tokens";
import { ModeCtx, type RenderMode } from "./style/Safe";
import { REGISTRY, CaptionLayer, type ComponentName } from "./style/components";
import { DIAGRAMS, type DiagramName } from "./style/diagrams";
import { Backdrop, Plate, type Asset } from "./style/plates";
import { Atmosphere } from "./style/atmosphere";
import { OpeningShotCtx } from "./style/motion";
import { StyledCaptions, type CaptionStyle } from "./style/captions";
import { resolveShots, type Alignment, type Timeline } from "./lib/timeline";

export type Props = {
  timeline: Timeline;
  alignment: Alignment;
  assets: Record<string, Asset>;
  cues: { start: number; end: number; text: string }[];
  mode: RenderMode;
  captions: boolean;
  /** How captions are drawn. "lead" is the series look from 2026-10-28 (user pick);
   *  "classic" re-renders a version delivered before then. See style/captions.tsx. */
  captionStyle?: CaptionStyle;
  voiceover?: string;
};

export const Video: React.FC<Props> = ({ timeline, alignment, assets, cues, mode, captions, captionStyle = "lead", voiceover }) => {
  const shots = resolveShots(timeline, alignment, 30);
  return (
    <ModeCtx.Provider value={mode}>
      <AbsoluteFill data-canvas-root="1" style={{ background: COLOR.bg }}>
        {voiceover && mode === "full" ? <Audio src={staticFile(voiceover)} /> : null}
        {shots.map((s) => {
          const name = (s.component ?? (s.asset_id ? "Plate" : "")) as string;
          const bd = (s.props as any)?.backdrop as string | undefined;
          const bdAsset = bd ? assets[bd] : undefined;
          if (bd && !bdAsset) throw new Error(`${s.shot_id}: backdrop "${bd}" is not in the asset inventory`);
          const isPlate = name === "Plate";
          const isDiagram = name in DIAGRAMS;
          const C = isPlate
            ? (Plate as any)
            : isDiagram
            ? DIAGRAMS[name as DiagramName]
            : REGISTRY[name as ComponentName];
          if (!C) throw new Error(`${s.shot_id}: unknown component "${name}"`);
          if (isDiagram && !isPlate) {
            const st = (s.props as any)?.states;
            // A diagram with one state is a static picture wearing a diagram's
            // clothes. The production notes ask for states that convey the
            // concept; fewer than two cannot.
            if (!Array.isArray(st) || st.length < 2)
              throw new Error(`${s.shot_id}: diagram "${name}" declares ${st?.length ?? 0} state(s); a diagram needs at least 2`);
          }
          const asset = s.asset_id ? assets[s.asset_id] : undefined;
          if (s.asset_id && !asset)
            throw new Error(`${s.shot_id}: asset_id "${s.asset_id}" is not in assets.json`);
          const props: Record<string, unknown> = {
            ...s.props,
            ...(isPlate && asset ? { asset } : {}),
            // Diagrams resolve their own states against the recording, so they
            // need the alignment and where this shot begins. So does any
            // component that declares it reveals on a phrase.
            ...(isDiagram ? { alignment, shotStartFrame: s.fromFrame, seed: s.shot_id } : {}),
            ...(!isDiagram && (C as any).wantsAlignment ? { alignment, shotStartFrame: s.fromFrame } : {}),
          };
          return (
            <Sequence key={s.shot_id} from={s.fromFrame} durationInFrames={s.durationInFrames} name={s.shot_id}>
              <OpeningShotCtx.Provider value={s.fromFrame === 0}>
                {bdAsset ? <Backdrop asset={bdAsset} focus={(s.props as any)?.backdropFocus} dim={(s.props as any)?.backdropDim} seed={s.shot_id} /> : null}
                {/* @ts-expect-error props are validated against the schema, not the type system */}
                <C {...props} />
              </OpeningShotCtx.Provider>
            </Sequence>
          );
        })}
        <Atmosphere />
        {!captions ? null : captionStyle === "classic" ? (
          <CaptionLayer cues={cues} alignment={alignment} />
        ) : (
          <StyledCaptions cues={cues} alignment={alignment} look={captionStyle} />
        )}
      </AbsoluteFill>
    </ModeCtx.Provider>
  );
};
