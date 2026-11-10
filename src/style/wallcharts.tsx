import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { EASE, useEntrance, useShotFade } from "./motion";
import { COLOR, SAFE, TYPE } from "./tokens";
import { SafeText } from "./Safe";
import { findPhrase, type Alignment } from "../lib/timeline";
import { CentImage, MAX_CENT_PX, MIN_TRAIT_PX, fitGrid } from "./grids";
import { Imagery } from "./Safe";

/**
 * Charts for Collector Wall episodes, drawn from measured data in the timeline.
 *
 * `DotColumns`: one dot per Wall (or per anything counted), stacked in columns by a
 * measured value, so a Wall that stands alone in its column is seen to stand alone.
 * The dots rise column by column as `dots_at` is spoken; the `highlight` dot turns
 * copper and is named when its phrase is spoken, and the rest dim. The total is
 * declared in the timeline and checked against the bins, so the readout cannot
 * disagree with the dots.
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
const ease = (frame: number, from: number, len: number) =>
  interpolate(frame, [from, from + len], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });

type Bin = { label: string; count: number };
type Read = { at_phrase?: string; readout: string; caption: string };

export const DotColumns: React.FC<Anchored & {
  title: string; subtitle?: string; axis: string; bins: Bin[]; total: number;
  dots_at: string; highlight: { bin: string; name: string; at_phrase: string }; reads: Read[];
}> = (props) => {
  const { title, subtitle, axis, bins, total, dots_at, highlight, reads } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  const head = useEntrance("rise", 0);
  const sum = bins.reduce((a, b) => a + b.count, 0);
  if (sum !== total) throw new Error(`DotColumns: the bins hold ${sum} dots but the timeline declares ${total}`);
  const hb = bins.findIndex((b) => b.label === highlight.bin);
  if (hb < 0 || bins[hb]!.count < 1) throw new Error(`DotColumns: no dot in bin "${highlight.bin}" to highlight`);
  const W = X1 - X0;
  const labelH = 64, axisH = 60, nameH = 64;                    // bin labels, axis caption, the name over the highlight
  const plotH = STAGE.y1 - STAGE.y0 - labelH - axisH - nameH;
  const maxN = Math.max(...bins.map((b) => b.count));
  const colW = W / bins.length;
  const pitch = Math.min(colW * 0.86, plotH / maxN);
  const d = Math.floor(pitch * 0.82);
  const base = STAGE.y0 + nameH + plotH;                       // the bottom of the dot stacks
  const f0 = at(dots_at), fh = at(highlight.at_phrase);
  if (fh < f0) throw new Error(`DotColumns: "${highlight.at_phrase}" comes before "${dots_at}"`);
  const hT = ease(frame, fh, 12);
  const readFrames = reads.map((r) => (r.at_phrase ? at(r.at_phrase) : 0));
  let cur = -1;
  readFrames.forEach((f, i) => { if (frame >= f) cur = i; });
  const order: number[] = [];                                  // dot arrival order: column by column, bottom up
  let k = 0;
  const arrive = bins.map((b) => Array.from({ length: b.count }, () => { order.push(k); return k++; }));
  const span = Math.max(1, Math.min(36, Math.round((fh - f0) * 0.7)));
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <div style={{ position: "absolute", left: X0, top: TITLE.y0, width: W, opacity: head.opacity, transform: `translateY(${head.y}px)` }}>
        <SafeText role="display" fontSize={68} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
        {subtitle ? <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim}>{subtitle}</SafeText> : null}
      </div>
      {bins.map((b, c) => {
        const cx = X0 + colW * (c + 0.5);
        return (
          <React.Fragment key={b.label}>
            {arrive[c]!.map((idx, j) => {
              const t = ease(frame, f0 + (idx / Math.max(1, sum - 1)) * span, 8);
              const isH = c === hb && j === 0;
              const dim = isH ? 1 : 1 - 0.55 * hT;
              const bg = isH ? interpolateColor(hT) : COLOR.inkDim;
              return (
                <div key={j} style={{ position: "absolute", left: cx - d / 2, top: base - (j + 1) * pitch + (pitch - d) / 2,
                                      width: d, height: d, borderRadius: "50%", background: bg,
                                      opacity: t * dim, transform: `scale(${(0.4 + 0.6 * t) * (isH ? 1 + 0.25 * hT : 1)})`,
                                      boxShadow: isH && hT > 0 ? `0 0 0 ${4 * hT}px ${COLOR.bg}, 0 0 0 ${9 * hT}px ${COLOR.accent}, 0 0 ${28 * hT}px ${COLOR.accent}` : "none" }} />
              );
            })}
            <div style={{ position: "absolute", left: cx - colW / 2, top: base + 12, width: colW, textAlign: "center",
                          opacity: ease(frame, 0, 10) }}>
              <SafeText role="label" fontSize={42} maxLines={1} color={c === hb && hT > 0.5 ? COLOR.accent : COLOR.ink}
                        style={{ fontFamily: TYPE.mono, fontWeight: 700, textAlign: "center" }}>{b.label}</SafeText>
            </div>
          </React.Fragment>
        );
      })}
      <div style={{ position: "absolute", left: X0, top: base + labelH + 4, width: W, opacity: ease(frame, 0, 10) }}>
        <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim} style={{ textAlign: "center" }}>{axis}</SafeText>
      </div>
      {/* The name sits in the band reserved above the tallest column, so it never covers a dot
          (a name placed just above its dot ran across the neighbouring columns and hid some of
          them), with a copper leader down the highlighted column's own empty space to its dot. */}
      <div style={{ position: "absolute", left: X0 + colW * hb, top: STAGE.y0, width: W - colW * hb,
                    opacity: hT, transform: `translateY(${(1 - hT) * 10}px)` }}>
        <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.accent} style={{ fontWeight: 700 }}>{highlight.name}</SafeText>
      </div>
      {(() => {
        const y0 = STAGE.y0 + nameH - 4, y1 = base - pitch + (pitch - d) / 2 - 16;  // to just above the ring
        return y1 > y0 ? (
          <div style={{ position: "absolute", left: X0 + colW * (hb + 0.5) - 1.5, top: y0, width: 3, height: y1 - y0,
                        background: COLOR.accent, transformOrigin: "top", transform: `scaleY(${hT})`, opacity: 0.85 }} />
        ) : null;
      })()}
      {cur >= 0 ? (
        <div key={cur} style={{ position: "absolute", left: X0, top: BAND.y0, width: W, opacity: ease(frame, readFrames[cur]!, 8) }}>
          <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{reads[cur]!.readout}</SafeText>
          <SafeText role="body" fontSize={48} maxLines={1}>{reads[cur]!.caption}</SafeText>
        </div>
      ) : null}
    </div>
  );
};

/** inkDim to copper, for the highlighted dot. */
const interpolateColor = (t: number) => {
  const a = hex(COLOR.inkDim), b = hex(COLOR.accent);
  const m = a.map((v, i) => Math.round(v + (b[i]! - v) * t));
  return `rgb(${m[0]},${m[1]},${m[2]})`;
};
const hex = (c: string): number[] => {
  const m = c.match(/^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i);
  if (!m) throw new Error(`DotColumns: colour ${c} is not #rrggbb`);
  return [parseInt(m[1]!, 16), parseInt(m[2]!, 16), parseInt(m[3]!, 16)];
};


/**
 * `CentFilter`: every Cent in a measured pool, narrowed step by step as the narration
 * names each condition. A step with `keep` dims the Cents that fail it; with `regroup`
 * the survivors also gather, larger, into a grid of their own, and the dimmed ones go.
 * Each step's `keep` must be drawn from the Cents still shown, so the narrowing can only
 * narrow. The readout band shows the step's number, which is checked against `keep`.
 */
type FilterStep = { at_phrase: string; keep?: number[]; regroup?: boolean; readout: string; caption: string };
type Spot = { x: number; y: number; s: number; o: number };

export const CentFilter: React.FC<Anchored & {
  title: string; subtitle?: string; pool: number[]; steps: FilterStep[]; mark?: { n: number; at_phrase: string };
}> = (props) => {
  const { title, subtitle, pool, steps, mark } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  const head = useEntrance("rise", 0);
  if (new Set(pool).size !== pool.length) throw new Error("CentFilter: the pool repeats a Cent");
  const W = X1 - X0, H = STAGE.y1 - STAGE.y0;
  const layout = (ns: number[]) => {
    const g = fitGrid(ns.length, W, H, 0.12);
    const size = Math.min(MAX_CENT_PX, g.size), step = size + g.gap;
    const cols = Math.min(ns.length, g.cols), rows = Math.ceil(ns.length / g.cols);
    const left = X0 + (W - (cols * step - g.gap)) / 2, top = STAGE.y0 + (H - (rows * step - g.gap)) / 2;
    return new Map(ns.map((n, i) => [n, { x: left + (i % g.cols) * step, y: top + Math.floor(i / g.cols) * step, s: size }]));
  };
  const first = layout(pool);
  const states: Map<number, Spot>[] = [new Map(pool.map((n) => [n, { ...first.get(n)!, o: 1 }]))];
  const frames = [0];
  let shown = [...pool];
  for (const st of steps) {
    const prev = states[states.length - 1]!;
    const next = new Map(prev);
    if (st.keep) {
      const keep = new Set(st.keep);
      for (const n of st.keep) if (!shown.includes(n)) throw new Error(`CentFilter: #${n} is not among the Cents still shown`);
      const kept = pool.filter((n) => keep.has(n));
      const np = st.regroup ? layout(kept) : null;
      for (const n of pool) {
        const q = prev.get(n)!;
        next.set(n, keep.has(n) ? (np ? { ...np.get(n)!, o: 1 } : q) : { ...q, o: np ? 0 : Math.min(q.o, 0.14) });
      }
      shown = kept;
    }
    const lit = pool.filter((n) => next.get(n)!.o === 1).length;
    if (/^\d+$/.test(st.readout) && Number(st.readout) !== lit)
      throw new Error(`CentFilter: readout ${st.readout} but ${lit} Cents are lit at "${st.at_phrase}"`);
    states.push(next);
    frames.push(at(st.at_phrase));
  }
  for (let i = 1; i < frames.length; i++)
    if (frames[i]! < frames[i - 1]!) throw new Error(`CentFilter: "${steps[i - 1]!.at_phrase}" comes before the step above it`);
  let k = 0;
  frames.forEach((f, i) => { if (frame >= f) k = i; });
  const t = k === 0 ? 1 : ease(frame, frames[k]!, 18);
  const A = states[Math.max(0, k - 1)]!, B = states[k]!;
  const markT = mark ? ease(frame, at(mark.at_phrase), 12) : 0;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <div style={{ position: "absolute", left: X0, top: TITLE.y0, width: X1 - X0, opacity: head.opacity, transform: `translateY(${head.y}px)` }}>
        <SafeText role="display" fontSize={68} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
        {subtitle ? <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim}>{subtitle}</SafeText> : null}
      </div>
      <Imagery>
        {pool.map((n, i) => {
          const a = A.get(n)!, b = B.get(n)!;
          const x = a.x + (b.x - a.x) * t, y = a.y + (b.y - a.y) * t, sz = a.s + (b.s - a.s) * t, o = a.o + (b.o - a.o) * t;
          const enter = ease(frame, Math.round((i / pool.length) * 24), 8);
          if (o * enter <= 0.001) return null;
          const ring = mark && mark.n === n && markT > 0;
          return (
            <div key={n} style={{ position: "absolute", left: x, top: y, width: sz, height: sz, opacity: o * enter,
                                  transform: `scale(${0.6 + 0.4 * enter})`, borderRadius: "50%",
                                  boxShadow: ring ? `0 0 0 ${6 * markT}px ${COLOR.bg}, 0 0 0 ${12 * markT}px ${COLOR.accent}, 0 0 ${36 * markT}px ${COLOR.accent}` : "none" }}>
              <CentImage n={n} size={Math.round(sz)} texture={sz < MIN_TRAIT_PX} />
            </div>
          );
        })}
      </Imagery>
      {k > 0 ? (
        <div key={k} style={{ position: "absolute", left: X0, top: BAND.y0, width: X1 - X0, opacity: ease(frame, frames[k]!, 8) }}>
          <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{steps[k - 1]!.readout}</SafeText>
          <SafeText role="body" fontSize={48} maxLines={1}>{steps[k - 1]!.caption}</SafeText>
        </div>
      ) : null}
    </div>
  );
};
(CentFilter as any).wantsAlignment = true;

/**
 * `PostExcerpts`: words a collector posted, quoted verbatim and credited under the title, one
 * excerpt per block. Each excerpt lights as its phrase is spoken and the others dim. Plain type,
 * never a mock-up of the platform's interface; the post itself is named in `source`.
 */
export const PostExcerpts: React.FC<Anchored & {
  title: string; subtitle: string; excerpts: { text: string; at_phrase: string }[]; source?: string;
}> = (props) => {
  const { title, subtitle, excerpts, source } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  const head = useEntrance("rise", 0);
  const fs = excerpts.map((e) => at(e.at_phrase));
  for (let i = 1; i < fs.length; i++) if (fs[i]! < fs[i - 1]!) throw new Error("PostExcerpts: excerpts are out of spoken order");
  let k = -1;
  fs.forEach((f, i) => { if (frame >= f) k = i; });
  const base = 0.6 - 0.28 * (fs.length ? ease(frame, fs[0]!, 12) : 0);   // all half-lit until the first is read
  const t = k >= 0 ? ease(frame, fs[k]!, 12) : 0;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <div style={{ position: "absolute", left: X0, top: TITLE.y0, width: X1 - X0, opacity: head.opacity, transform: `translateY(${head.y}px)` }}>
        <SafeText role="display" fontSize={68} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
        <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim}>{subtitle}</SafeText>
      </div>
      <div style={{ position: "absolute", left: X0, top: STAGE.y0 + 60, width: X1 - X0, display: "flex", flexDirection: "column", gap: 64 }}>
        {excerpts.map((e, i) => {
          const lit = i === k ? t : i === k - 1 ? 1 - t : 0;
          const enter = ease(frame, 6 + i * 6, 10);
          return (
            <div key={i} style={{ display: "flex", gap: 32, opacity: enter * (base + (1 - base) * lit) }}>
              <div style={{ width: 8, flex: "none", borderRadius: 4, background: COLOR.accent }} />
              <SafeText role="display" fontSize={66} maxLines={4} style={{ fontWeight: 500, textWrap: "balance" }}>{`\u201c${e.text}\u201d`}</SafeText>
            </div>
          );
        })}
      </div>
      {source ? (
        <div style={{ position: "absolute", left: X0, top: BAND.y0 + 40, width: X1 - X0, opacity: head.opacity }}>
          <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim}>{source}</SafeText>
        </div>
      ) : null}
    </div>
  );
};
(PostExcerpts as any).wantsAlignment = true;

export const WALLCHARTS = { DotColumns, CentFilter, PostExcerpts } as const;
(DotColumns as any).wantsAlignment = true;
