import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { CentImage } from "./grids";
import { useEntrance, useShotFade, EASE } from "./motion";
import { COLOR, SAFE, TYPE } from "./tokens";
import { Imagery, SafeText } from "./Safe";
import { findPhrase, type Alignment } from "../lib/timeline";

/**
 * TraitTally: one Wall's Cents against the nineteen traits of the Traits Atlas.
 * Made for ScrappyT (2026-10-27), whose Wall holds one of every trait; usable
 * for any Wall or Set that is a checklist of traits.
 *
 * Each trait is a chip that lights when its Cent is named. Two modes:
 *  - "grid": every trait as a chip with its Cent's thumbnail. The chips light in
 *            turn between `at_phrase` and `until_phrase` (or all at once with
 *            `lit_all`), for the overview.
 *  - "walk": one trait at a time, its Cent large (a high-res front), with the
 *            trait's name and caption; the chips sit in a band underneath and
 *            keep count. An item may zoom to the mark that carries its trait.
 *
 * Every trait a chip names is checked against the item list, so a chip can
 * never light without a Cent behind it, and the count is the list's length.
 */

type Anchored = { alignment: Alignment; shotStartFrame: number };
export type TraitItem = {
  trait: string;            // chip label, e.g. "Verdigris"
  n?: number;               // the Cent; or `cents` for several (Contaminated)
  cents?: number[];
  src?: string;             // high-res front for the walk
  at_phrase?: string;       // walk: when it is named; grid: ignored
  caption?: string;         // walk: e.g. "#8550 · Significant"
  /** Zoom to the mark carrying the trait: a box on the front, as fractions of the image. */
  zoom?: { box: [number, number, number, number]; at_phrase?: string };
};

const E = SAFE.essential;
const TITLE = { y0: E.y0 + 30 };
const CX = (E.x0 + E.x1) / 2;
const BAND = { y0: 1150, y1: 1335 };   // walk: the chip band, above the captions

const useAt = ({ alignment, shotStartFrame }: Anchored) => {
  const { fps } = useVideoConfig();
  return (phrase: string) => {
    const f = Math.round(findPhrase(alignment, phrase).start * fps) - shotStartFrame;
    if (f < 0) throw new Error(`TraitTally: "${phrase}" is spoken before this shot starts`);
    return f;
  };
};

const Head: React.FC<{ title: string; count: number; total: number }> = ({ title, count, total }) => {
  const e = useEntrance("rise", 0);
  return (
    <div style={{ position: "absolute", left: E.x0 + 24, top: TITLE.y0, width: E.x1 - E.x0 - 48,
                  opacity: e.opacity, transform: `translateY(${e.y}px)`, display: "flex", alignItems: "flex-start" }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <SafeText role="display" fontSize={68} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
        <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim}>Traits Atlas</SafeText>
      </div>
      <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent}
                style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{`${count}/${total}`}</SafeText>
    </div>
  );
};

/** A checklist row: the trait's Cent and its name, lit (copper) or waiting (dim). */
const Chip: React.FC<{ label: string; t: number; w: number; h: number; thumb: React.ReactNode }> = ({ label, t, w, h, thumb }) => (
  <div style={{ width: w, height: h, boxSizing: "border-box", borderRadius: 14, display: "flex", alignItems: "center", gap: 12, padding: "0 10px",
                border: `3px solid ${t > 0 ? `rgba(175,107,57,${0.35 + 0.65 * t})` : "rgba(255,255,255,0.12)"}`,
                background: `rgba(175,107,57,${0.16 * t})` }}>
    <div style={{ opacity: 0.25 + 0.75 * t, transform: `scale(${1 + 0.12 * Math.sin(Math.PI * Math.min(1, t))})` }}>{thumb}</div>
    <div style={{ flex: 1, minWidth: 0, opacity: 0.4 + 0.6 * t }}>
      <SafeText role="body" fontSize={46} maxLines={1} color={t > 0 ? COLOR.ink : COLOR.inkDim} style={{ fontWeight: 600, whiteSpace: "nowrap" }}>{label}</SafeText>
    </div>
  </div>
);

export const TraitTally: React.FC<Anchored & {
  title: string;
  /** Every trait, in the order the chips are laid out. */
  traits: string[];
  items: TraitItem[];
  mode: "grid" | "walk";
  /** Traits already shown before this shot: lit from the first frame. */
  lit_before?: string[];
  /** grid: light the chips in turn from at_phrase to until_phrase; or lit_all. */
  at_phrase?: string;
  until_phrase?: string;
  lit_all?: boolean;
  /** grid: thumbnails on the chips. */
  thumbs?: boolean;
  /** grid: from this phrase, one chip stands out and the rest dim (e.g. the trait another Wall lacks). */
  focus?: { trait: string; at_phrase: string };
}> = (props) => {
  const { title, traits, items, mode, lit_before = [], at_phrase, until_phrase, lit_all, thumbs = true, focus } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  const byTrait = new Map(items.map((it) => [it.trait, it]));
  for (const t of [...items.map((i) => i.trait), ...lit_before]) if (!traits.includes(t)) throw new Error(`TraitTally: "${t}" is not one of the traits`);
  for (const t of traits) if (!byTrait.has(t)) throw new Error(`TraitTally: no Cent for the trait "${t}"`);
  for (const it of items) if (!it.n && !it.cents?.length) throw new Error(`TraitTally: "${it.trait}" has no Cent`);

  // When each chip lights (frame), or Infinity.
  const litAt = new Map<string, number>();
  for (const t of lit_before) litAt.set(t, -100);
  if (mode === "grid") {
    if (lit_all) traits.forEach((t) => litAt.set(t, Math.min(litAt.get(t) ?? 0, 0)));
    else {
      if (!at_phrase || !until_phrase) throw new Error("TraitTally grid: needs at_phrase and until_phrase, or lit_all");
      const f0 = at(at_phrase), f1 = at(until_phrase);
      if (f1 <= f0) throw new Error("TraitTally grid: until_phrase comes before at_phrase");
      const todo = traits.filter((t) => !litAt.has(t));
      todo.forEach((t, i) => litAt.set(t, f0 + ((f1 - f0) * i) / Math.max(1, todo.length)));
    }
  } else {
    let last = -1;
    for (const it of items) {
      if (lit_before.includes(it.trait)) continue;
      if (!it.at_phrase) throw new Error(`TraitTally walk: "${it.trait}" has no at_phrase`);
      const f = at(it.at_phrase);
      if (f < last) throw new Error(`TraitTally walk: "${it.trait}" is named out of order`);
      last = f; litAt.set(it.trait, f);
    }
  }
  const tOf = (t: string) => {
    const f = litAt.get(t);
    return f === undefined ? 0 : interpolate(frame, [f, f + 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out });
  };
  const count = traits.filter((t) => (litAt.get(t) ?? Infinity) <= frame).length;
  const thumbOf = (it: TraitItem, d: number) => <CentImage n={(it.n ?? it.cents![0])!} size={d} />;

  if (mode === "grid") {
    // A two-column checklist: every label at full legible size.
    const cols = 2, rows = Math.ceil(traits.length / cols);
    const x0 = E.x0 + 4, w = E.x1 - E.x0 - 8, y0 = TITLE.y0 + 180, h = BAND.y1 - y0;
    const cw = w / cols, ch = h / rows, gap = 8;
    const d = Math.floor(ch - gap - 14);
    if (focus && !traits.includes(focus.trait)) throw new Error(`TraitTally: focus "${focus.trait}" is not one of the traits`);
    const fz = focus ? interpolate(frame, [at(focus.at_phrase), at(focus.at_phrase) + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut }) : 0;
    return (
      <div style={{ position: "absolute", inset: 0, opacity: fade }}>
        <Head title={title} count={count} total={traits.length} />
        <Imagery>
          {traits.map((t, i) => {
            const it = byTrait.get(t)!;
            const col = Math.floor(i / rows), row = i % rows;      // read down each column
            const on = focus?.trait === t;
            return (
              <div key={t} style={{ position: "absolute", left: x0 + col * cw + gap / 2, top: y0 + row * ch + gap / 2,
                                    opacity: focus && !on ? 1 - 0.75 * fz : 1,
                                    boxShadow: on ? `0 0 ${28 * fz}px rgba(175,107,57,${fz})` : undefined, borderRadius: 14 }}>
                <Chip label={t} t={tOf(t)} w={cw - gap} h={ch - gap} thumb={thumbs ? thumbOf(it, d) : null} />
              </div>
            );
          })}
        </Imagery>
      </div>
    );
  }

  // Walk: the most recently named item, large.
  let cur: TraitItem | null = null, f0 = 0;
  for (const it of items) {
    const f = litAt.get(it.trait);
    if (!lit_before.includes(it.trait) && f !== undefined && f <= frame) { cur = it; f0 = f; }
  }
  const t = interpolate(frame, [f0, f0 + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out });
  const V = { x0: CX - 245, y0: TITLE.y0 + 165, d: 490 };   // the coin's viewport
  let zoom = 0;
  let zk = 1, zx = 0.5, zy = 0.5;
  if (cur?.zoom) {
    const zf = cur.zoom.at_phrase ? at(cur.zoom.at_phrase) : f0 + 24;
    zoom = interpolate(frame, [zf, zf + 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });
    const [bx0, by0, bx1, by1] = cur.zoom.box;
    const target = Math.min(3, 0.81 / Math.max(bx1 - bx0, by1 - by0));   // fit the box in the coin's diameter
    zk = 1 + (target - 1) * zoom; zx = 0.5 + ((bx0 + bx1) / 2 - 0.5) * zoom; zy = 0.5 + ((by0 + by1) / 2 - 0.5) * zoom;
  }
  const S = V.d / 0.81;   // cents.vision fronts: the coin is a circle of radius ~0.405 on white
  const chipCols = 10, chipRows = Math.ceil(traits.length / chipCols);
  const cw = (E.x1 - E.x0 - 8) / chipCols, chh = (BAND.y1 - BAND.y0) / chipRows, td = Math.floor(Math.min(cw, chh) - 14);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Head title={title} count={count} total={traits.length} />
      {cur ? (
        <Imagery>
          <div key={cur.trait} style={{ position: "absolute", left: V.x0, top: V.y0, width: V.d, height: V.d, opacity: t,
                                        transform: `scale(${0.92 + 0.08 * t})`, borderRadius: cur.cents && cur.cents.length > 1 ? 0 : "50%", overflow: "hidden",
                                        filter: "drop-shadow(0 14px 24px rgba(0,0,0,0.55))" }}>
            {cur.cents && cur.cents.length > 1 ? (
              <div style={{ position: "absolute", inset: 0, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, placeItems: "center" }}>
                {cur.cents.map((n) => <CentImage key={n} n={n} size={(V.d - 16) / 2} />)}
              </div>
            ) : cur.src ? (
              <Img src={staticFile(cur.src)} style={{ position: "absolute", width: S * zk, height: S * zk,
                                                      left: V.d / 2 - S * zk * zx, top: V.d / 2 - S * zk * zy }} />
            ) : (
              <CentImage n={cur.n!} size={V.d} />
            )}
          </div>
        </Imagery>
      ) : null}
      {cur ? (
        <div key={`r${cur.trait}`} style={{ position: "absolute", left: E.x0 + 24, top: V.y0 + V.d + 8, width: E.x1 - E.x0 - 48,
                                           opacity: t, transform: `translateY(${(1 - t) * 14}px)` }}>
          <SafeText role="display" fontSize={64} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{cur.trait}</SafeText>
          {cur.caption ? <SafeText role="body" fontSize={46} maxLines={1}>{cur.caption}</SafeText> : null}
        </div>
      ) : null}
      {/* The tally band: each trait's Cent, lit as it is named (names are in the readout above). */}
      <Imagery>
        {traits.map((tr, i) => {
          const col = i % chipCols, row = Math.floor(i / chipCols), tt = tOf(tr);
          const it = byTrait.get(tr)!;
          return (
            <div key={tr} style={{ position: "absolute", left: E.x0 + 4 + col * cw + (cw - td) / 2, top: BAND.y0 + row * chh + (chh - td) / 2,
                                   opacity: 0.2 + 0.8 * tt, borderRadius: "50%",
                                   boxShadow: tt > 0 ? `0 0 0 ${4 * tt}px rgba(175,107,57,${tt})` : undefined,
                                   transform: `scale(${1 + 0.18 * Math.sin(Math.PI * Math.min(1, tt))})` }}>
              {thumbOf(it, td)}
            </div>
          );
        })}
      </Imagery>
    </div>
  );
};
(TraitTally as any).wantsAlignment = true;
