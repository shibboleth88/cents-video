import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { CentGrid, CentImage, CentTurn, MAX_CENT_PX, fitGrid } from "./grids";
import { useEntrance, useShotFade, EASE } from "./motion";
import { COLOR, SAFE, TYPE } from "./tokens";
import { Imagery, SafeText } from "./Safe";
import { findPhrase, type Alignment } from "../lib/timeline";
import poolsJson from "../../films/sets/data/pools.json";

/**
 * Shots for the Sets films. Every coin on screen is a real Cent named by its
 * number (see grids.tsx); nothing here draws a coin.
 *
 * Text goes through SafeText and uses the prop names fidelity.py walks (title,
 * subtitle, caption, readout), so every string a viewer reads is ledgered.
 */

const pools = (poolsJson as unknown as { pools: Record<string, number[]> }).pools;
const pool = (k: string) => {
  const p = pools[k];
  if (!p || p.length === 0) throw new Error(`pool "${k}" is empty or missing`);
  return p;
};

type Anchored = { alignment: Alignment; shotStartFrame: number };

/** Frame within the shot at which a phrase is spoken. Before the shot is an error. */
const useAt = ({ alignment, shotStartFrame }: Anchored) => {
  const { fps } = useVideoConfig();
  return (phrase: string) => {
    const f = Math.round(findPhrase(alignment, phrase).start * fps) - shotStartFrame;
    if (f < 0) throw new Error(`"${phrase}" is spoken before this shot starts`);
    return f;
  };
};

/** The working area for coins: the essential box, under a title band and above a readout band. */
const E = SAFE.essential;
const TITLE = { y0: E.y0 + 30, y1: E.y0 + 180 };
const READOUT = { y0: 1150, y1: 1330 };
const STAGE = { x0: E.x0 + 24, x1: E.x1 - 24, y0: TITLE.y1 + 20, y1: READOUT.y0 - 20 };

const Title: React.FC<{ title?: string; subtitle?: string }> = ({ title, subtitle }) => {
  const e = useEntrance("rise", 0);
  if (!title) return null;
  return (
    <div style={{ position: "absolute", left: STAGE.x0, top: TITLE.y0, width: STAGE.x1 - STAGE.x0,
                  opacity: e.opacity, transform: `translateY(${e.y}px)` }}>
      <SafeText role="display" fontSize={68} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
      {subtitle ? <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim}>{subtitle}</SafeText> : null}
    </div>
  );
};

const Readout: React.FC<{ readout?: string; caption?: string; from?: number; k?: string | number }> = ({ readout, caption, from = 0, k }) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [from, from + 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out });
  if (!readout && !caption) return null;
  return (
    <div key={k} style={{ position: "absolute", left: STAGE.x0, top: READOUT.y0, width: STAGE.x1 - STAGE.x0,
                          height: READOUT.y1 - READOUT.y0, display: "flex", flexDirection: "column",
                          justifyContent: "center", opacity: t, transform: `translateY(${(1 - t) * 14}px)` }}>
      {readout ? (
        <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent}
                  style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{readout}</SafeText>
      ) : null}
      {caption ? <SafeText role="body" fontSize={48} maxLines={2}>{caption}</SafeText> : null}
    </div>
  );
};

type Hero = { n: number; caption?: string; at_phrase?: string };

/**
 * A handful of named Cents: the example Cents of a Set, or one per type as the
 * narration names it. A Cent with `at_phrase` arrives when that phrase is
 * spoken and its caption takes the readout; the rest arrive together at the cut.
 * `labelsUnder` puts each caption under its own coin instead (short labels only,
 * like years).
 */
export const CentRow: React.FC<Anchored & {
  title?: string; subtitle?: string; cents: Hero[]; labelsUnder?: boolean; cols?: number;
  readout?: string; caption?: string; readout_at?: string;
}> = (props) => {
  const { title, subtitle, cents, labelsUnder, cols, readout, caption, readout_at } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  if (cents.length === 0) throw new Error("CentRow: no Cents");
  const W = STAGE.x1 - STAGE.x0, H = STAGE.y1 - STAGE.y0;
  const labelH = labelsUnder ? 64 : 0;
  // Fit cells that include the label band, then take the coin out of the cell.
  // `cols` fixes the arrangement (three in a row reads as a set of three).
  const lay = cols
    ? (() => { const cell = Math.min(W / cols, H / Math.ceil(cents.length / cols));
               const size = Math.floor(cell / 1.12); return { cols, size, gap: Math.floor(cell - size) }; })()
    : fitGrid(cents.length, W, H, 0.12);
  const size = Math.min(MAX_CENT_PX, Math.floor(lay.size - labelH * (lay.size / (lay.size + labelH))));
  const cellW = lay.size + lay.gap, cellH = size + labelH + lay.gap;
  const rows = Math.ceil(cents.length / lay.cols);
  const ox = STAGE.x0 + (W - lay.cols * cellW + lay.gap) / 2;
  const oy = STAGE.y0 + (H - rows * cellH + lay.gap) / 2;
  const starts = cents.map((c, i) => (c.at_phrase ? at(c.at_phrase) : i * 3));
  for (let i = 1; i < starts.length; i++)
    if (cents[i]!.at_phrase && cents[i - 1]!.at_phrase && starts[i]! < starts[i - 1]!)
      throw new Error(`CentRow: "${cents[i]!.at_phrase}" is spoken before "${cents[i - 1]!.at_phrase}"`);
  // The readout follows the most recently arrived anchored Cent.
  let cur = -1;
  cents.forEach((c, i) => { if (c.at_phrase && frame >= starts[i]!) cur = i; });
  const rFrom = readout_at ? at(readout_at) : 0;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Title title={title} subtitle={subtitle} />
      <Imagery>
        {cents.map((c, i) => {
          const f0 = starts[i]!;
          const t = interpolate(frame, [f0, f0 + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out });
          const lit = cur === -1 || !cents.some((x) => x.at_phrase) || i === cur ? 1 : 0.55;
          const col = i % lay.cols, row = Math.floor(i / lay.cols);
          return (
            <div key={c.n} style={{ position: "absolute", left: ox + col * cellW + (lay.size - size) / 2, top: oy + row * cellH,
                                    opacity: t * lit, transform: `scale(${0.7 + 0.3 * t})`,
                                    filter: "drop-shadow(0 10px 18px rgba(0,0,0,0.5))" }}>
              <CentImage n={c.n} size={size} />
            </div>
          );
        })}
      </Imagery>
      {labelsUnder ? cents.map((c, i) => {
        const col = i % lay.cols, row = Math.floor(i / lay.cols);
        const t = interpolate(frame, [starts[i]! + 4, starts[i]! + 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return c.caption ? (
          <div key={`l${c.n}`} style={{ position: "absolute", left: ox + col * cellW, top: oy + row * cellH + size + 8,
                                        width: lay.size, display: "flex", justifyContent: "center", opacity: t }}>
            <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.inkDim}>{c.caption}</SafeText>
          </div>
        ) : null;
      }) : null}
      {!labelsUnder && cur >= 0 && cents[cur]!.caption ? (
        <Readout key={cur} k={cur} caption={cents[cur]!.caption} from={starts[cur]} />
      ) : null}
      {readout || caption ? <Readout readout={readout} caption={caption} from={rFrom} /> : null}
    </div>
  );
};

/**
 * Every Cent in a pool, as large as the stage allows. The count is declared in
 * the timeline as `readout`, so the ledger sees it, and checked here against
 * the pool's own length, so the number on screen cannot disagree with the wall.
 */
export const PoolWall: React.FC<Anchored & {
  pool: string; readout: string; title?: string; caption?: string; readout_at?: string;
}> = (props) => {
  const { title, caption, readout, readout_at } = props;
  const fade = useShotFade();
  const at = useAt(props);
  const ns = pool(props.pool);
  if (readout !== ns.length.toLocaleString("en-US"))
    throw new Error(`PoolWall ${props.pool}: readout says ${readout} but the pool holds ${ns.length}`);
  const W = STAGE.x1 - STAGE.x0, H = STAGE.y1 - STAGE.y0;
  const lay = fitGrid(ns.length, W, H, 0.1);
  const size = Math.min(lay.size, 300);
  const layout = { ...lay, size };
  const step = size + lay.gap;
  const rows = Math.ceil(ns.length / lay.cols);
  const left = STAGE.x0 + (W - (lay.cols * step - lay.gap)) / 2;
  const top = STAGE.y0 + (H - (rows * step - lay.gap)) / 2;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Title title={title} />
      <Imagery>
        <CentGrid ns={ns} layout={layout} enterFrames={Math.min(36, ns.length * 2)}
                  style={{ position: "absolute", left, top }} />
      </Imagery>
      <Readout readout={readout} caption={caption}
               from={readout_at ? at(readout_at) : 6} />
    </div>
  );
};

/** One Cent, turning. For what a trait looks like, close. */
export const CentHero: React.FC<Anchored & { n: number; title?: string; caption?: string }> = ({ n, title, caption }) => {
  const fade = useShotFade();
  const size = 500;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Title title={title} />
      <Imagery>
        <CentTurn n={n} size={size} style={{ position: "absolute", left: (1080 - size) / 2,
                                               top: STAGE.y0 + (STAGE.y1 - STAGE.y0 - size) / 2 }} />
      </Imagery>
      <Readout caption={caption} from={10} />
    </div>
  );
};

/**
 * All 10,000 as a field behind a title, in number order. Texture, never
 * evidence: at this size no trait is visible. It is one baked image of the same
 * cutouts (pipeline/field_mosaic.py), because 10,000 live images time out the
 * renderer.
 */
export const FieldTitle: React.FC<Anchored & { title: string; subtitle?: string }> = ({ title, subtitle }) => {
  const fade = useShotFade();
  const frame = useCurrentFrame();
  const e0 = useEntrance("rise", 0, 10), e1 = useEntrance("rise", 1, 10);
  const enter = interpolate(frame, [0, 24], [0, 1], { extrapolateRight: "clamp", easing: EASE.out });
  const drift = interpolate(frame, [0, 300], [1.0, 1.06], { extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Imagery>
        <Img src={staticFile("cents_field.webp")}
             style={{ position: "absolute", left: 40, top: 520, width: 1000, height: 1000,
                      opacity: 0.5 * enter, transform: `scale(${drift})` }} />
        <div style={{ position: "absolute", inset: 0,
                      background: "linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.1) 40%, rgba(0,0,0,0.5))" }} />
      </Imagery>
      <div style={{ position: "absolute", left: STAGE.x0, top: E.y0 + 40, width: STAGE.x1 - STAGE.x0 }}>
        <div style={{ opacity: e0.opacity, transform: `translateY(${e0.y}px)` }}>
          <SafeText role="display" fontSize={104} maxLines={2} style={{ fontWeight: 700, letterSpacing: -2 }}>{title}</SafeText>
        </div>
        {subtitle ? (
          <div style={{ opacity: e1.opacity, transform: `translateY(${e1.y}px)`, marginTop: 12 }}>
            <SafeText role="body" fontSize={52} maxLines={2} color={COLOR.inkDim}>{subtitle}</SafeText>
          </div>
        ) : null}
      </div>
    </div>
  );
};

// Video.tsx passes {alignment, shotStartFrame} to components that ask for it.
for (const C of [CentRow, PoolWall, CentHero, FieldTitle]) (C as any).wantsAlignment = true;

export const SETS = { CentRow, PoolWall, CentHero, FieldTitle } as const;
