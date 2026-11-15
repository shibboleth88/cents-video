import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { CentImage } from "./grids";
import { EASE, useEntrance, useShotFade } from "./motion";
import { COLOR, SAFE, TYPE } from "./tokens";
import { Imagery, SafeText } from "./Safe";
import { findPhrase, type Alignment } from "../lib/timeline";

/**
 * TraitLadder: how many traits each Cent carries, as a ladder of rows from the
 * most to none, with the Cents themselves on the rows that hold only a few.
 * Made for One Cent #9344 (2026-11-11): "more than any other Cent. No Cent
 * carries eight. Three carry seven." A superlative is a claim about the whole
 * set, so the ladder shows the whole set: the rows must add up to `total`, and
 * a row that shows its Cents must show every one of them.
 *
 * Rows light on phrases (`steps`); a row not yet named waits dim.
 */

type Anchored = { alignment: Alignment; shotStartFrame: number };
type Row = { traits: number; count: number; ns?: number[] };
type Step = { at_phrase?: string; plus?: number; rows: number[] };

const E = SAFE.essential;
const X0 = E.x0 + 24, X1 = E.x1 - 24;
const TOP = E.y0 + 30;
const ROWS = { y0: TOP + 250, y1: 1335 };
const THUMB = 72;
const MAX_THUMBS = 5;

export const TraitLadder: React.FC<Anchored & {
  title: string; subtitle?: string; rows: Row[]; total: number; mark?: number; steps: Step[];
}> = (props) => {
  const { title, subtitle, rows, total, mark, steps, alignment, shotStartFrame } = props;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useShotFade();
  const head = useEntrance("rise", 0);

  const sum = rows.reduce((a, r) => a + r.count, 0);
  if (sum !== total) throw new Error(`TraitLadder: the rows add up to ${sum}, not ${total}`);
  rows.forEach((r, i) => {
    if (i && r.traits >= rows[i - 1]!.traits) throw new Error("TraitLadder: rows must run from most traits to fewest");
    if (r.ns && r.ns.length !== r.count) throw new Error(`TraitLadder: row ${r.traits} shows ${r.ns.length} Cents but counts ${r.count}`);
    if (r.ns && r.ns.length > MAX_THUMBS) throw new Error(`TraitLadder: row ${r.traits} has more Cents than fit; give the count only`);
  });
  if (mark !== undefined && !rows.some((r) => r.ns?.includes(mark))) throw new Error(`TraitLadder: #${mark} is on no row`);

  const litAt = new Map<number, number>();
  let prev = -Infinity;
  for (const s of steps) {
    let f = 0;
    if (s.at_phrase) {
      f = Math.round(findPhrase(alignment, s.at_phrase).start * fps) - shotStartFrame;
      if (f < 0) throw new Error(`TraitLadder: "${s.at_phrase}" is spoken before this shot starts`);
    }
    f += Math.round((s.plus ?? 0) * fps);
    if (f < prev) throw new Error("TraitLadder: steps out of order");
    prev = f;
    for (const t of s.rows) {
      if (!rows.some((r) => r.traits === t)) throw new Error(`TraitLadder: no row for ${t} traits`);
      litAt.set(t, f);
    }
  }
  for (const r of rows) if (!litAt.has(r.traits)) throw new Error(`TraitLadder: row ${r.traits} never lights`);
  // The rows lit by the latest step that has begun are in the accent colour; earlier ones settle to ink.
  const latest = Math.max(...[...litAt.values()].filter((f) => f <= frame), -Infinity);

  const rh = (ROWS.y1 - ROWS.y0) / rows.length;
  const cDigit = 110, cCount = 230;   // column widths: traits, Cents
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <div style={{ position: "absolute", left: X0, top: TOP, width: X1 - X0, opacity: head.opacity, transform: `translateY(${head.y}px)` }}>
        <SafeText role="display" fontSize={68} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
        {subtitle ? <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim}>{subtitle}</SafeText> : null}
      </div>
      <div style={{ position: "absolute", left: X0, top: ROWS.y0 - 70, width: X1 - X0, display: "flex", opacity: 0.85 * head.opacity }}>
        <div style={{ width: cDigit }}>
          <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.inkDim}>traits</SafeText>
        </div>
        <div style={{ width: cCount, textAlign: "right" }}>
          <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.inkDim} style={{ textAlign: "right" }}>Cents</SafeText>
        </div>
      </div>
      <Imagery>
        {rows.map((r, i) => {
          const f = litAt.get(r.traits)!;
          const t = interpolate(frame, [f, f + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out });
          const hot = f === latest;
          const color = hot ? COLOR.accent : COLOR.ink;
          return (
            <div key={r.traits} style={{ position: "absolute", left: X0, top: ROWS.y0 + i * rh, width: X1 - X0, height: rh,
                                         display: "flex", alignItems: "center", opacity: 0.28 + 0.72 * t,
                                         borderTop: `2px solid ${COLOR.rule}` }}>
              <div style={{ width: cDigit }}>
                <SafeText role="body" fontSize={58} maxLines={1} color={color} style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{String(r.traits)}</SafeText>
              </div>
              <div style={{ width: cCount, textAlign: "right" }}>
                <SafeText role="body" fontSize={52} maxLines={1} color={color}
                          style={{ fontFamily: TYPE.mono, fontWeight: 700, textAlign: "right" }}>{r.count.toLocaleString("en-US")}</SafeText>
              </div>
              <div style={{ display: "flex", gap: 14, marginLeft: 34 }}>
                {(r.ns ?? []).map((n) => (
                  <div key={n} style={{ position: "relative", width: THUMB, height: THUMB }}>
                    <CentImage n={n} size={THUMB} style={{ clipPath: "circle(40.5% at 50% 50%)" }} />
                    {n === mark ? <div style={{ position: "absolute", inset: -4, border: `4px solid ${COLOR.accent}`, borderRadius: "50%" }} /> : null}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </Imagery>
    </div>
  );
};
(TraitLadder as any).wantsAlignment = true;
