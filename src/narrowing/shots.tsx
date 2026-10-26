import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { CentGrid, CentImage, CentTurn, fitGrid } from "../style/grids";
import { EASE, useShotFade } from "../style/motion";
import { COLOR, REGIONS, TYPE } from "../style/tokens";
import { Imagery, Region, SafeText } from "../style/Safe";
import { findPhrase, type Alignment } from "../lib/timeline";
import poolsJson from "../../films/sets/data/pools.json";
import fortiesJson from "../../films/sets-narrowing/data/forties.json";

/**
 * Film B, "the narrowing": 10,000 Cents down to one. Each step shows every Cent
 * that can fill the scarcest slot of one Set, so the wall IS the count: nothing
 * here draws a number of coins that the trait data does not hold.
 *
 * Text goes only through SafeText, under the keys the on-screen gate reads
 * (readout, caption), so every string is checked against the claims ledger.
 */

const pools = (poolsJson as unknown as { pools: Record<string, number[]> }).pools;
const forties = fortiesJson as unknown as {
  years: number[]; row_a: number[]; row_b: (number | null)[]; only_1949: number;
};

const pool = (k: string): number[] => {
  const p = pools[k];
  if (!p || p.length === 0) throw new Error(`pool ${k} is empty or missing`);
  return [...p].sort((a, b) => a - b);
};

type Timed = { alignment: Alignment; shotStartFrame: number };

/** Frame, relative to this shot, at which a phrase of the narration starts. */
function useAtPhrase(t: Timed, phrase?: string): number {
  const { fps } = useVideoConfig();
  if (!phrase) return 0;
  return Math.round(findPhrase(t.alignment, phrase).start * fps) - t.shotStartFrame;
}

/** Where Cents are drawn: wide, but clear of the labels and the captions. */
const GRID = { x0: 60, y0: 300, x1: 1020, y1: 1100 };

/** The number and the Set's name, revealed as the narration says the number. */
const Readout: React.FC<{ readout: string; caption?: string; at: number }> = ({ readout, caption, at }) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [at, at + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out });
  return (
    <Region region="labels" justify="end">
      <div style={{ opacity: t, transform: `translateY(${(1 - t) * 18}px)` }}>
        <SafeText role="display" fontSize={88} maxLines={1} color={COLOR.accent}
                  style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{readout}</SafeText>
      </div>
      {caption ? (
        <SafeText role="label" fontSize={42} maxLines={2} color={COLOR.inkDim}>{caption}</SafeText>
      ) : null}
    </Region>
  );
};

/**
 * All 10,000 as a field, baked by films/sets-narrowing/build_field.py from the
 * staged cutouts (10,000 live images timed the renderer out). With `pool`, the
 * lit image fades in over the plain one. At 8px a Cent is texture: the pattern
 * shows how many, never what the trait looks like.
 */
const FIELD_STATES: Record<string, string> = { "desert:notable+": "desert-notable" };

export const NarrowField: React.FC<Timed & {
  pool?: string; readout?: string; caption?: string; reveal_phrase?: string; lit_phrase?: string;
}> = (p) => {
  const o = useShotFade();
  const f = useCurrentFrame();
  const at = useAtPhrase(p, p.reveal_phrase);
  const litAt = useAtPhrase(p, p.lit_phrase);
  if (p.pool && !FIELD_STATES[p.pool]) throw new Error(`NarrowField: no baked field for pool ${p.pool}`);
  const lit = p.pool ? interpolate(f, [litAt, litAt + 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 0;
  const side = 800;
  const img = (name: string, opacity: number) => (
    <Img src={staticFile(`narrowing/field-${name}.png`)} width={side} height={side}
         style={{ position: "absolute", left: 0, top: 0, width: side, height: side, opacity }} />
  );
  return (
    <AbsoluteFill style={{ opacity: o }}>
      <Imagery>
        <div style={{ position: "absolute", left: (1080 - side) / 2, top: GRID.y0, width: side, height: side }}>
          {img("all", 1 - lit)}
          {p.pool ? img(FIELD_STATES[p.pool]!, lit) : null}
        </div>
      </Imagery>
      {p.readout ? <Readout readout={p.readout} caption={p.caption} at={at} /> : null}
    </AbsoluteFill>
  );
};
Object.assign(NarrowField, { wantsAlignment: true });

/** Every Cent in one pool, as large as the box allows. Must clear the trait floor. */
export const NarrowWall: React.FC<Timed & {
  pool: string; readout: string; caption: string; reveal_phrase?: string;
}> = (p) => {
  const o = useShotFade();
  const at = useAtPhrase(p, p.reveal_phrase);
  const ns = pool(p.pool);
  if (String(ns.length) !== p.readout)
    throw new Error(`NarrowWall: pool ${p.pool} holds ${ns.length} Cents but the readout says ${p.readout}`);
  const w = GRID.x1 - GRID.x0, h = GRID.y1 - GRID.y0;
  const layout = fitGrid(ns.length, w, h);
  const step = layout.size + layout.gap;
  const gw = layout.cols * step - layout.gap;
  const gh = Math.ceil(ns.length / layout.cols) * step - layout.gap;
  return (
    <AbsoluteFill style={{ opacity: o }}>
      <Imagery>
        <div style={{ position: "absolute", left: GRID.x0 + (w - gw) / 2, top: GRID.y0 + (h - gh) / 2 }}>
          <CentGrid ns={ns} layout={layout} enterFrames={Math.min(30, ns.length * 3)} />
        </div>
      </Imagery>
      <Readout readout={p.readout} caption={p.caption} at={at} />
    </AbsoluteFill>
  );
};
Object.assign(NarrowWall, { wantsAlignment: true });

/** The one Cent dated 1949, turning. */
export const NarrowOne: React.FC<Timed & {
  n: number; readout: string; caption: string; reveal_phrase?: string;
}> = (p) => {
  const o = useShotFade();
  const at = useAtPhrase(p, p.reveal_phrase);
  if (p.n !== forties.only_1949) throw new Error(`NarrowOne: #${p.n} is not the only 1949 Cent (#${forties.only_1949})`);
  return (
    <AbsoluteFill style={{ opacity: o }}>
      <Imagery>
        <div style={{ position: "absolute", left: 300, top: 420 }}>
          <CentTurn n={p.n} size={480} maxTilt={14} />
        </div>
      </Imagery>
      <Readout readout={p.readout} caption={p.caption} at={at} />
    </AbsoluteFill>
  );
};
Object.assign(NarrowOne, { wantsAlignment: true });

/**
 * Two collections' 1940s Sets, one Cent per year. The only 1949 Cent moves from
 * row A to row B as the narration says "changes hands": B becomes whole, A is
 * left with a gap. An empty slot is an outline, never a drawn coin.
 */
export const NarrowSwap: React.FC<Timed & { move_phrase: string; complete_phrase: string; break_phrase: string }> = (p) => {
  const o = useShotFade();
  const f = useCurrentFrame();
  const moveAt = useAtPhrase(p, p.move_phrase);
  const completeAt = useAtPhrase(p, p.complete_phrase);
  const breakAt = useAtPhrase(p, p.break_phrase);
  const n = forties.years.length;
  const size = 92, gap = 12, step = size + gap;
  const x0 = (1080 - (n * step - gap)) / 2;
  const yA = 470, yB = 820;
  const last = n - 1;
  const t = interpolate(f, [moveAt, moveAt + 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });
  const glowB = interpolate(f, [completeAt, completeAt + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const dimA = interpolate(f, [breakAt, breakAt + 12], [1, 0.4], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const slot = (y: number, i: number, key: string) => (
    <div key={key} style={{ position: "absolute", left: x0 + i * step, top: y, width: size, height: size,
                            borderRadius: "50%", border: `3px dashed ${COLOR.inkDim}`, boxSizing: "border-box", opacity: 0.7 }} />
  );
  const row = (ns: (number | null)[], y: number, op: number, glow: number, tag: string) => (
    <div style={{ opacity: op }}>
      {ns.map((c, i) => (c == null || i === last ? slot(y, i, `${tag}${i}`) : (
        <div key={`${tag}${i}`} style={{ position: "absolute", left: x0 + i * step, top: y }}>
          <CentImage n={c} size={size} />
        </div>
      )))}
      <div style={{ position: "absolute", left: x0 - 18, top: y - 18, width: n * step - gap + 36, height: size + 36,
                    borderRadius: 24, border: `3px solid ${COLOR.accent2}`, opacity: glow, boxSizing: "border-box" }} />
    </div>
  );
  // The moving Cent: an arc from A's last slot down to B's.
  const mx = x0 + last * step;
  const my = yA + (yB - yA) * t - Math.sin(Math.PI * t) * 60;
  return (
    <AbsoluteFill style={{ opacity: o }}>
      <Imagery>
        {row(forties.row_a, yA, dimA, 0, "a")}
        {row(forties.row_b, yB, 1, glowB, "b")}
        <div style={{ position: "absolute", left: mx, top: my, transform: `scale(${1 + 0.12 * Math.sin(Math.PI * t)})` }}>
          <CentImage n={forties.only_1949} size={size} />
        </div>
      </Imagery>
    </AbsoluteFill>
  );
};
Object.assign(NarrowSwap, { wantsAlignment: true });

export const NARROWING = { NarrowField, NarrowWall, NarrowOne, NarrowSwap } as const;
