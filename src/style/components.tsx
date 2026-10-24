import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig, Img, OffthreadVideo, staticFile } from "remotion";
import { useEntrance, useShotFade, wordProgress } from "./motion";
import type { Alignment } from "../lib/timeline";
import { COLOR, MOTION, REGIONS, TYPE } from "./tokens";
import { Imagery, Region, SafeText } from "./Safe";
import { SETS } from "./sets";

const useFade = useShotFade;

/** One member of a staggered group. Keeps the motion role out of every call site. */
const Rise: React.FC<{ i: number; children: React.ReactNode; role?: "rise" | "place" }> = ({ i, children, role = "rise" }) => {
  const e = useEntrance(role, i);
  return <div style={{ opacity: e.opacity, transform: `translateY(${e.y}px) scale(${e.scale})`, transformOrigin: "left center" }}>{children}</div>;
};

/** The rule draws itself rather than fading in; a line that grows reads as an act. */
const Rule: React.FC<{ i: number }> = ({ i }) => {
  const e = useEntrance("place", i);
  return <div style={{ width: 160 * e.opacity, height: 3, background: COLOR.accent, margin: "32px 0", opacity: e.opacity }} />;
};

export const TitleCard: React.FC<{ title: string; subtitle?: string; author: string }> = ({
  title, subtitle, author,
}) => {
  const o = useFade();
  return (
    <div style={{ opacity: o }}>
      <Region region="title" justify="center">
        <Rise i={0}>
          <SafeText role="display" fontSize={96} style={{ fontWeight: 700, letterSpacing: -2 }}>
            {title}
          </SafeText>
        </Rise>
        {subtitle ? (
          <Rise i={1}>
            <SafeText role="body" fontSize={52} color={COLOR.inkDim} style={{ marginTop: 18 }}>
              {subtitle}
            </SafeText>
          </Rise>
        ) : null}
        <Rule i={2} />
        <Rise i={3}>
          <SafeText role="body" fontSize={46} color={COLOR.inkDim}>{author}</SafeText>
        </Rise>
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
          <Rise i={0}>
            <SafeText role="display" fontSize={76} maxLines={6} style={{ fontWeight: 500, textWrap: "balance" }}>
              {quote}
            </SafeText>
          </Rise>
          {attribution ? (
            <Rise i={1}>
              <SafeText role="body" fontSize={46} color={COLOR.accent} style={{ marginTop: 28 }}>
                {attribution}
              </SafeText>
            </Rise>
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
          <Rise key={i} i={i}>
            <SafeText role="body" fontSize={46} color={COLOR.inkDim} style={{ marginBottom: 14 }}>{l}</SafeText>
          </Rise>
        ))}
        {url ? (
          <Rise i={lines.length}>
            <SafeText role="body" fontSize={50} color={COLOR.accent} style={{ marginTop: 20 }}>{url}</SafeText>
          </Rise>
        ) : null}
      </Region>
    </div>
  );
};

/**
 * Burned-in captions, driven by the same alignment file the edit is cut from.
 * Sits in its own region so it cannot collide with labels.
 */
/**
 * Captions reveal word by word, as the word is spoken.
 *
 * The timings are the same per-word alignment the whole edit is cut from, so
 * this costs nothing to produce and cannot drift from the voice: if a word
 * moves, its reveal moves with it. The whole cue is laid out from the first
 * frame and words change opacity in place, so nothing reflows mid-cue.
 */
export const CaptionLayer: React.FC<{
  cues: { start: number; end: number; text: string }[];
  alignment?: Alignment;
}> = ({ cues, alignment }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const cue = cues.find((c) => t >= c.start && t < c.end);
  if (!cue) return null;
  const { x0, y0, x1, y1 } = REGIONS.caption;
  const words = cue.text.split(/\s+/).filter(Boolean);
  const spoken = (alignment?.words ?? []).filter(
    (w) => w.start >= cue.start - 0.01 && w.start <= cue.end + 0.01
  );
  // Only reveal word by word when the alignment and the cue agree on the word
  // count. Otherwise show the cue whole: a half-matched reveal would dim words
  // that have already been said.
  const op =
    spoken.length === words.length
      ? spoken.map((w) => 0.45 + 0.55 * wordProgress(f, fps, w.start))
      : undefined;
  return (
    <div style={{ position: "absolute", left: x0, top: y0, width: x1 - x0, height: y1 - y0, display: "flex", alignItems: "center" }}>
      <div style={{ background: COLOR.captionBack, padding: "14px 22px", borderRadius: 10 }}>
        <SafeText role="caption" fontSize={48} maxLines={2} style={{ textWrap: "balance" }} wordOpacity={op}>
          {cue.text}
        </SafeText>
      </div>
    </div>
  );
};

export const REGISTRY = { TitleCard, PullQuote, StatReveal, AssetShot, Credits, ...SETS } as const;
export type ComponentName = keyof typeof REGISTRY;
