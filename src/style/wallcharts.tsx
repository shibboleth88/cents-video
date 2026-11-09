import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { EASE, useEntrance, useShotFade } from "./motion";
import { COLOR, SAFE, TYPE } from "./tokens";
import { SafeText } from "./Safe";
import { findPhrase, type Alignment } from "../lib/timeline";

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

export const WALLCHARTS = { DotColumns } as const;
(DotColumns as any).wantsAlignment = true;
