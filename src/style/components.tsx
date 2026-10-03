import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig, Img, OffthreadVideo, staticFile } from "remotion";
import { COLOR, MOTION, REGIONS, TYPE } from "./tokens";
import { Imagery, Region, SafeText } from "./Safe";

const useFade = () => {
  const f = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return interpolate(
    f,
    [0, MOTION.enterFrames, durationInFrames - MOTION.exitFrames, durationInFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
};

export const TitleCard: React.FC<{ title: string; subtitle?: string; author: string }> = ({
  title, subtitle, author,
}) => {
  const o = useFade();
  return (
    <div style={{ opacity: o }}>
      <Region region="title" justify="center">
        <SafeText role="display" fontSize={96} style={{ fontWeight: 700, letterSpacing: -2 }}>
          {title}
        </SafeText>
        {subtitle ? (
          <SafeText role="body" fontSize={52} color={COLOR.inkDim} style={{ marginTop: 18 }}>
            {subtitle}
          </SafeText>
        ) : null}
        <div style={{ width: 160, height: 3, background: COLOR.accent, margin: "32px 0" }} />
        <SafeText role="body" fontSize={46} color={COLOR.inkDim}>{author}</SafeText>
      </Region>
    </div>
  );
};

export const PullQuote: React.FC<{ quote: string; attribution?: string }> = ({ quote, attribution }) => {
  const o = useFade();
  return (
    <div style={{ opacity: o }}>
      <Region region="quote" justify="center">
        <div>
          <SafeText role="display" fontSize={76} maxLines={6} style={{ fontWeight: 500, textWrap: "balance" }}>
            {quote}
          </SafeText>
          {attribution ? (
            <SafeText role="body" fontSize={46} color={COLOR.accent} style={{ marginTop: 28 }}>
              {attribution}
            </SafeText>
          ) : null}
        </div>
      </Region>
    </div>
  );
};

/** A number that counts into place. For data passages. */
export const StatReveal: React.FC<{ value: number; suffix?: string; caption: string }> = ({
  value, suffix = "", caption,
}) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [0, 24], [0, 1], { extrapolateRight: "clamp" });
  const shown = Math.round(value * (1 - Math.pow(1 - t, 3)));
  return (
    <Region region="stat" justify="center" align="center">
      {/* Routed through SafeText, not a raw div: a styled div bypasses the
          bounds gate entirely, which is how a 220px number silently overflowed
          into both side bands. Components must emit text ONLY via SafeText. */}
      <SafeText role="display" fontSize={150} maxLines={1} color={COLOR.accent}
                style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>
        {`${shown.toLocaleString()}${suffix}`}
      </SafeText>
      <SafeText role="body" fontSize={50} style={{ textAlign: "center", marginTop: 20 }} maxLines={3}>
        {caption}
      </SafeText>
    </Region>
  );
};

/** Photography or footage. Full-bleed is fine for pictures; never for information. */
export const AssetShot: React.FC<{ src: string; motion?: boolean; label?: string }> = ({
  src, motion = false, label,
}) => (
  <>
    <Imagery>
      <div style={{ position: "absolute", inset: 0 }}>
        {motion ? (
          <OffthreadVideo src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : (
          <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        )}
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(transparent 55%, rgba(0,0,0,0.72))" }} />
      </div>
    </Imagery>
    {label ? (
      <Region region="labels" justify="end">
        <SafeText role="label" fontSize={42} maxLines={2}>{label}</SafeText>
      </Region>
    ) : null}
  </>
);

export const Credits: React.FC<{ lines: string[]; url?: string }> = ({ lines, url }) => {
  const o = useFade();
  return (
    <div style={{ opacity: o }}>
      <Region region="credits" justify="center">
        {lines.map((l, i) => (
          <SafeText key={i} role="body" fontSize={46} color={COLOR.inkDim} style={{ marginBottom: 14 }}>
            {l}
          </SafeText>
        ))}
        {url ? <SafeText role="body" fontSize={50} color={COLOR.accent} style={{ marginTop: 20 }}>{url}</SafeText> : null}
      </Region>
    </div>
  );
};

/**
 * Burned-in captions, driven by the same alignment file the edit is cut from.
 * Sits in its own region so it cannot collide with labels.
 */
export const CaptionLayer: React.FC<{ cues: { start: number; end: number; text: string }[] }> = ({ cues }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const cue = cues.find((c) => t >= c.start && t < c.end);
  if (!cue) return null;
  const { x0, y0, x1, y1 } = REGIONS.caption;
  return (
    <div style={{ position: "absolute", left: x0, top: y0, width: x1 - x0, height: y1 - y0, display: "flex", alignItems: "center" }}>
      <div style={{ background: COLOR.captionBack, padding: "14px 22px", borderRadius: 10 }}>
        <SafeText role="caption" fontSize={48} maxLines={2} style={{ textWrap: "balance" }}>
          {cue.text}
        </SafeText>
      </div>
    </div>
  );
};

export const REGISTRY = { TitleCard, PullQuote, StatReveal, AssetShot, Credits } as const;
export type ComponentName = keyof typeof REGISTRY;
