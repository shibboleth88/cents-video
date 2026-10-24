import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { CentGrid, CentImage, CentTurn, fitGrid } from "./grids";
import { useEntrance, useShotFade, EASE } from "./motion";
import { COLOR, SAFE, TYPE } from "./tokens";
import { Imagery, SafeText } from "./Safe";
import { findPhrase, type Alignment } from "../lib/timeline";

/**
 * Shots for the Collector Wall series: one claimed Wall per episode, walked
 * through as cents.vision shows it. Everything a shot draws comes from the
 * episode's data/wall.json through the timeline props, and each shot checks
 * the numbers it is handed against the Cents it is handed, so a readout cannot
 * disagree with the coins under it.
 *
 * Only what the claimed Wall shows: the name as the card renders it, its Cents,
 * Sets and badges. Never a wallet address.
 */

type Anchored = { alignment: Alignment; shotStartFrame: number };

const useAt = ({ alignment, shotStartFrame }: Anchored) => {
  const { fps } = useVideoConfig();
  return (phrase: string) => {
    const f = Math.round(findPhrase(alignment, phrase).start * fps) - shotStartFrame;
    if (f < 0) throw new Error(`"${phrase}" is spoken before this shot starts`);
    return f;
  };
};

const E = SAFE.essential;
const X0 = E.x0 + 24, X1 = E.x1 - 24;
const TITLE = { y0: E.y0 + 30, y1: E.y0 + 180 };
const BAND = { y0: 1150, y1: 1330 };
const STAGE = { y0: TITLE.y1 + 20, y1: BAND.y0 - 20 };

const fadeIn = (frame: number, from: number, len = 10) =>
  interpolate(frame, [from, from + len], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out });

/** The Wall's name, small label above. The name renders exactly as the card does. */
const NameBand: React.FC<{ title: string; subtitle?: string }> = ({ title, subtitle }) => {
  const e = useEntrance("rise", 0);
  return (
    <div style={{ position: "absolute", left: X0, top: TITLE.y0, width: X1 - X0,
                  opacity: e.opacity, transform: `translateY(${e.y}px)` }}>
      <SafeText role="display" fontSize={68} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
      {subtitle ? <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim}>{subtitle}</SafeText> : null}
    </div>
  );
};

/** A badge as the card shows it: a pill of its own text. */
const Chip: React.FC<{ text: string; opacity: number; accent?: boolean }> = ({ text, opacity, accent }) => (
  <div style={{ opacity, transform: `translateY(${(1 - opacity) * 10}px)`, padding: "6px 22px", borderRadius: 40,
                border: `2px solid ${accent ? COLOR.accent : COLOR.rule}`, background: "rgba(255,255,255,0.04)" }}>
    <SafeText role="label" fontSize={42} maxLines={1} color={accent ? COLOR.accent : COLOR.ink}>{text}</SafeText>
  </div>
);

/** Opening card: COLLECTOR WALL, the name, and the signature Cent turning. */
export const WallCard: React.FC<Anchored & { title: string; signature: number; caption: string }> = ({ title, signature, caption }) => {
  const fade = useShotFade();
  const frame = useCurrentFrame();
  const e0 = useEntrance("rise", 0), e1 = useEntrance("rise", 1);
  const size = 520;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <div style={{ position: "absolute", left: X0, top: E.y0 + 40, width: X1 - X0 }}>
        <div style={{ opacity: e0.opacity, transform: `translateY(${e0.y}px)` }}>
          <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.accent}
                    style={{ fontFamily: TYPE.mono, letterSpacing: 4 }}>COLLECTOR WALL</SafeText>
        </div>
        <div style={{ opacity: e1.opacity, transform: `translateY(${e1.y}px)`, marginTop: 8 }}>
          <SafeText role="display" fontSize={104} maxLines={1} style={{ fontWeight: 700, letterSpacing: -2 }}>{title}</SafeText>
        </div>
      </div>
      <Imagery>
        <CentTurn n={signature} size={size} from={6}
                  style={{ position: "absolute", left: (1080 - size) / 2, top: 560 }} />
      </Imagery>
      <div style={{ position: "absolute", left: X0, top: BAND.y0 - 40, width: X1 - X0, opacity: fadeIn(frame, 24),
                    display: "flex", justifyContent: "center" }}>
        <SafeText role="body" fontSize={48} maxLines={1} color={COLOR.inkDim}>{caption}</SafeText>
      </div>
    </div>
  );
};

/**
 * Every Cent on the Wall, then its badges, each arriving when the narration
 * names it (or in order at the cut when no phrase is given). `readout` is the
 * count and must equal the number of Cents.
 */
export const WallGrid: React.FC<Anchored & {
  title: string; cents: number[]; readout: string; readout_at?: string;
  badges?: { text: string; at_phrase?: string; accent?: boolean }[];
}> = (props) => {
  const { title, cents, readout, readout_at, badges = [] } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  if (readout !== String(cents.length))
    throw new Error(`WallGrid: readout says ${readout} but the Wall is handed ${cents.length} Cents`);
  const W = X1 - X0, H = STAGE.y1 - STAGE.y0 - 120;
  const lay = fitGrid(cents.length, W, H, 0.1);
  const size = Math.min(lay.size, 240);
  const step = size + lay.gap;
  const rows = Math.ceil(cents.length / lay.cols);
  const left = X0 + (W - (lay.cols * step - lay.gap)) / 2;
  const top = STAGE.y0 + (H - (rows * step - lay.gap)) / 2;
  const rFrom = readout_at ? at(readout_at) : 12;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <NameBand title={title} />
      <Imagery>
        <CentGrid ns={cents} layout={{ ...lay, size }} enterFrames={Math.min(36, cents.length * 2)}
                  style={{ position: "absolute", left, top }} />
      </Imagery>
      <div style={{ position: "absolute", left: X0, top: STAGE.y1 - 110, width: W, opacity: fadeIn(frame, rFrom) }}>
        <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent}
                  style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{`${readout} Cents`}</SafeText>
      </div>
      <div style={{ position: "absolute", left: X0, top: BAND.y0, width: W, display: "flex", flexWrap: "wrap", gap: 14 }}>
        {badges.map((b, i) => (
          <Chip key={b.text} text={b.text} accent={b.accent}
                opacity={fadeIn(frame, b.at_phrase ? at(b.at_phrase) : rFrom + 10 + i * 6)} />
        ))}
      </div>
    </div>
  );
};

/**
 * The Wall by year: one row per year it holds, oldest first, with that year's
 * Cents along the row. Only years held get a row; the gaps show as jumps in
 * the labels, never as invented empty space.
 */
export const WallYears: React.FC<Anchored & {
  title: string; cents: { n: number; year: number }[]; caption?: string; caption_at?: string;
}> = (props) => {
  const { title, cents, caption, caption_at } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  const years = [...new Set(cents.map((c) => c.year))].sort((a, b) => a - b);
  if (years.some((y) => y < 1909 || y > 1982)) throw new Error("WallYears: a year outside 1909-1982 is not a CENTS year");
  const H = STAGE.y1 - STAGE.y0 + 40;
  const rowH = Math.floor(H / years.length);
  const most = Math.max(...years.map((y) => cents.filter((c) => c.year === y).length));
  const labelW = 150;
  const size = Math.min(rowH - 8, Math.floor((X1 - X0 - labelW) / most) - 8);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <NameBand title={title} />
      {years.map((y, r) => {
        const row = cents.filter((c) => c.year === y);
        const t0 = 4 + r * 2;
        return (
          <div key={y} style={{ position: "absolute", left: X0, top: STAGE.y0 - 20 + r * rowH, height: rowH,
                                display: "flex", alignItems: "center", opacity: fadeIn(frame, t0) }}>
            <div style={{ width: labelW }}>
              <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.inkDim}
                        style={{ fontFamily: TYPE.mono }}>{String(y)}</SafeText>
            </div>
            <Imagery>
              <div style={{ display: "flex", gap: 8 }}>
                {/* Markers for the year, not evidence of a trait: rows can fall under the trait floor. */}
                {row.map((c) => <CentImage key={c.n} n={c.n} size={size} texture />)}
              </div>
            </Imagery>
          </div>
        );
      })}
      {caption ? (
        <div style={{ position: "absolute", left: X0, top: BAND.y0 + 40, width: X1 - X0,
                      opacity: fadeIn(frame, caption_at ? at(caption_at) : 20) }}>
          <SafeText role="body" fontSize={48} maxLines={2}>{caption}</SafeText>
        </div>
      ) : null}
    </div>
  );
};

/** One Cent close, turning, with the fact that makes it stand out. */
export const WallStandout: React.FC<Anchored & { title: string; n: number; readout: string; caption: string }> = ({ title, n, readout, caption }) => {
  const fade = useShotFade();
  const frame = useCurrentFrame();
  const size = 500;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <NameBand title={title} subtitle={`CENT #${n}`} />
      <Imagery>
        <CentTurn n={n} size={size} style={{ position: "absolute", left: (1080 - size) / 2,
                                             top: STAGE.y0 + (STAGE.y1 - STAGE.y0 - size) / 2 }} />
      </Imagery>
      <div style={{ position: "absolute", left: X0, top: BAND.y0, width: X1 - X0, opacity: fadeIn(frame, 10) }}>
        <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent}
                  style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{readout}</SafeText>
        <SafeText role="body" fontSize={48} maxLines={2}>{caption}</SafeText>
      </div>
    </div>
  );
};

/**
 * A short list: one Cent per row with its label beside it, each row arriving
 * on its phrase (or in order at the cut). For labels too long to sit under a
 * coin, like contamination types.
 */
export const WallList: React.FC<Anchored & {
  title: string; subtitle?: string; rows: { n: number; label: string; at_phrase?: string }[];
  readout?: string; readout_at?: string;
}> = (props) => {
  const { title, subtitle, rows, readout, readout_at } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  if (rows.length === 0) throw new Error("WallList: no rows");
  const H = STAGE.y1 - STAGE.y0;
  const rowH = Math.floor(H / rows.length);
  const size = Math.min(220, rowH - 16);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <NameBand title={title} subtitle={subtitle} />
      {rows.map((r, i) => {
        const t = fadeIn(frame, r.at_phrase ? at(r.at_phrase) : 4 + i * 5, 12);
        return (
          <div key={`${r.n}-${i}`} style={{ position: "absolute", left: X0, top: STAGE.y0 + 20 + i * rowH, height: rowH,
                                display: "flex", alignItems: "center", gap: 36, opacity: t,
                                transform: `translateX(${(1 - t) * -24}px)` }}>
            <Imagery><CentImage n={r.n} size={size} /></Imagery>
            <div style={{ width: X1 - X0 - size - 36 }}>
              <SafeText role="body" fontSize={52} maxLines={1}>{r.label}</SafeText>
            </div>
          </div>
        );
      })}
      {readout ? (
        <div style={{ position: "absolute", left: X0, top: BAND.y0 + 20, width: X1 - X0,
                      opacity: fadeIn(frame, readout_at ? at(readout_at) : 12) }}>
          <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent}
                    style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{readout}</SafeText>
        </div>
      ) : null}
    </div>
  );
};

export const WALL = { WallCard, WallGrid, WallYears, WallStandout, WallList } as const;
for (const C of Object.values(WALL)) (C as any).wantsAlignment = true;
