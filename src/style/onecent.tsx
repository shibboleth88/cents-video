import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { EASE, OpeningShotCtx, useEntrance, useShotFade } from "./motion";
import { COLOR, SAFE, TYPE } from "./tokens";
import { Imagery, SafeText } from "./Safe";
import { findPhrase, type Alignment } from "../lib/timeline";
import { CentImage, fitGrid } from "./grids";

/**
 * Shots for the One Cent series: one Cent per episode, looked at closely, with
 * the concept it carries named on screen and quoted from its author.
 *
 * `CentLook` holds the 1050px cents.vision photo of one Cent and moves a camera
 * over it on phrases (each move a measured box, or null for the whole coin).
 * It can turn the coin over (a flat 2D flip, as CentFlip), and it can lay a
 * concept card and a credited quote over the coin. The quote is verbatim: the
 * card text is what check_quotes.py was run on, and narration reads the same.
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
const SIZE = 500;                       // the standard coin, as in the Wall shots
const R = 0.402;                        // cents.vision photos: the coin is a circle of radius 0.40 on white

const ramp = (frame: number, from: number, len: number) =>
  interpolate(frame, [from, from + len], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });

type Box = [number, number, number, number];
type Move = { at_phrase: string; box: Box | null; mark?: boolean };
type Read = { at_phrase?: string; readout?: string; caption?: string };
type Concept = { at_phrase: string; label: string };
type Quote = { at_phrase: string; text: string; credit: string };

export const CentLook: React.FC<Anchored & {
  /** The inscription number, shown under the Cent's name (from the trait export). */
  inscription: number; n: number; front: string; back?: string;
  moves?: Move[]; flip_at?: string; reads?: Read[]; concept?: Concept; quote?: Quote;
}> = (props) => {
  const { inscription, n, front, back, moves = [], flip_at, reads = [], concept, quote } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const opening = React.useContext(OpeningShotCtx);
  const at = useAt(props);
  const W = X1 - X0, H = STAGE.y1 - STAGE.y0;
  const S = SIZE * (0.5 / R);

  for (const m of moves) {
    if (!m.box) continue;
    const [x0, y0, x1, y1] = m.box;
    if (!(0 <= x0 && x0 < x1 && x1 <= 1 && 0 <= y0 && y0 < y1 && y1 <= 1))
      throw new Error(`CentLook #${n}: box ${m.box} is not inside the image`);
  }
  if (flip_at && !back) throw new Error(`CentLook #${n}: a flip needs the back image`);
  if (quote && !quote.credit) throw new Error(`CentLook #${n}: a quote must carry its credit`);

  // Camera: each move eases from the state before it. A state is the point of
  // the image at the stage centre and the scale; null is the whole coin.
  const state = (b: Box | null) => {
    if (!b) return { cx: 0.5, cy: 0.5, k: 1 };
    const [x0, y0, x1, y1] = b;
    return { cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, k: Math.min(W / ((x1 - x0) * S), H / ((y1 - y0) * S), 3.2) };
  };
  let cam = state(null);
  let markBox: Box | null = null, markT = 0;
  for (const m of moves) {
    const f0 = at(m.at_phrase);
    const t = ramp(frame, f0, 18);
    if (t <= 0) break;
    const to = state(m.box);
    cam = { cx: cam.cx + (to.cx - cam.cx) * t, cy: cam.cy + (to.cy - cam.cy) * t, k: cam.k + (to.k - cam.k) * t };
    if (m.mark && m.box) { markBox = m.box; markT = ramp(frame, f0 + 14, 12); } else { markBox = null; markT = 0; }
  }
  const sc = cam.k;
  const ox = 540 - cam.cx * S * sc, oy = H / 2 - cam.cy * S * sc;

  const fFlip = flip_at ? at(flip_at) : Infinity;
  const ft = flip_at ? ramp(frame, fFlip, 20) : 0;
  const sx = Math.max(0.02, Math.abs(Math.cos(Math.PI * ft)));
  const src = ft < 0.5 ? front : back!;

  const enter = opening ? 1 : ramp(frame, 0, 18);
  const fq = quote ? at(quote.at_phrase) : Infinity;
  const qT = quote ? ramp(frame, fq, 14) : 0;
  const fc = concept ? at(concept.at_phrase) : Infinity;
  const cT = concept ? ramp(frame, fc, 14) : 0;
  const dim = 1 - 0.45 * cT - 0.33 * qT;   // the concept card and the quote need the coin behind them dimmed to read

  let cur: Read | undefined, curFrom = 0;
  reads.forEach((r, i) => {
    const f = r.at_phrase ? at(r.at_phrase) : 0;
    if (frame >= f) { cur = r; curFrom = f; }
    if (i > 0 && r.at_phrase && reads[i - 1]!.at_phrase && f < at(reads[i - 1]!.at_phrase!))
      throw new Error(`CentLook: "${r.at_phrase}" is spoken before the read before it`);
  });
  const rT = cur ? (curFrom === 0 && opening ? 1 : ramp(frame, curFrom, 8)) : 0;

  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Imagery>
        <div style={{ position: "absolute", left: 0, top: STAGE.y0, width: 1080, height: H, overflow: "hidden", opacity: enter * dim }}>
          <div style={{ position: "absolute", left: ox, top: oy, width: S * sc, height: S * sc, transform: `scaleX(${sx})` }}>
            <Img src={staticFile(src)} style={{ width: S * sc, height: S * sc, clipPath: "circle(40.5% at 50% 50%)",
                                                filter: `drop-shadow(0 ${SIZE * 0.04}px ${SIZE * 0.06}px rgba(0,0,0,0.55))` }} />
          </div>
          {markT > 0 && markBox ? (
            <div style={{ position: "absolute", left: ox + markBox[0] * S * sc - 12, top: oy + markBox[1] * S * sc - 12,
                          width: (markBox[2] - markBox[0]) * S * sc + 24, height: (markBox[3] - markBox[1]) * S * sc + 24,
                          border: `5px solid ${COLOR.accent}`, borderRadius: 18, opacity: markT * (1 - qT) }} />
          ) : null}
        </div>
      </Imagery>
      <NameBand title={`Cent #${n}`} subtitle={`Inscription #${inscription}`} />
      {concept && cT > 0 ? (
        <div style={{ position: "absolute", left: X0, top: STAGE.y0 + 10, width: W, opacity: cT,
                      transform: `translateY(${(1 - cT) * 14}px)` }}>
          <SafeText role="display" fontSize={64} maxLines={2}
                    style={{ fontFamily: TYPE.mono, fontWeight: 700, color: COLOR.accent, textTransform: "uppercase",
                             letterSpacing: 1, textShadow: "0 2px 12px rgba(0,0,0,0.8)" }}>{concept.label}</SafeText>
        </div>
      ) : null}
      {quote && qT > 0 ? (
        <div style={{ position: "absolute", left: X0, top: STAGE.y0 + 190, width: W, height: H - 190,
                      display: "flex", alignItems: "center", opacity: qT }}>
          <SafeText role="body" fontSize={54} maxLines={9} style={{ fontWeight: 500, textWrap: "pretty", lineHeight: 1.22 }}>
            {`“${quote.text}”`}
          </SafeText>
        </div>
      ) : null}
      {quote && qT > 0 ? (
        <div style={{ position: "absolute", left: X0, top: BAND.y0 + 20, width: W, opacity: qT }}>
          <SafeText role="label" fontSize={42} maxLines={2} color={COLOR.accent}>{`— ${quote.credit}`}</SafeText>
        </div>
      ) : cur ? (
        <div style={{ position: "absolute", left: X0, top: BAND.y0, width: W, opacity: rT, transform: `translateY(${(1 - rT) * 14}px)` }}>
          {cur.readout ? (
            <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent}
                      style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{cur.readout}</SafeText>
          ) : null}
          {cur.caption ? <SafeText role="body" fontSize={48} maxLines={1}>{cur.caption}</SafeText> : null}
        </div>
      ) : null}
    </div>
  );
};

/** The Cent's name is the largest text on screen; the inscription number sits under it. */
const NameBand: React.FC<{ title: string; subtitle?: string }> = ({ title, subtitle }) => {
  const e = useEntrance("rise", 0);
  const opening = React.useContext(OpeningShotCtx);
  return (
    <div style={{ position: "absolute", left: X0, top: TITLE.y0, width: X1 - X0,
                  opacity: opening ? 1 : e.opacity, transform: `translateY(${opening ? 0 : e.y}px)` }}>
      <SafeText role="display" fontSize={84} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
      {subtitle ? <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim}>{subtitle}</SafeText> : null}
    </div>
  );
};

/**
 * Two Cents side by side, whole, from their 1050px fronts: the Cent of the
 * episode and a reference Cent (e.g. a lustrous 1982 with the portrait intact).
 * The second arrives on its phrase.
 */
export const CentCompare: React.FC<Anchored & {
  inscription: number; n: number; front: string; label: string; trait: string;
  other: { n: number; front: string; label: string; trait: string; at_phrase: string };
}> = (props) => {
  const { inscription, n, front, label, trait, other } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  const H = STAGE.y1 - STAGE.y0;
  const D = 360;                         // two coins side by side inside the essential area
  const S = D * (0.5 / R);
  const t2 = ramp(frame, at(other.at_phrase), 16);
  // The episode's Cent starts centred and makes room for the reference Cent.
  const L = 470 - 200 * t2, Rx = 670;
  const cy = STAGE.y0 + H / 2 - 60;
  const coin = (src: string, cx: number, o: number) => (
    <div style={{ position: "absolute", left: cx - S / 2, top: cy - S / 2, width: S, height: S, opacity: o,
                  transform: `scale(${0.92 + 0.08 * o})`, filter: "drop-shadow(0 18px 26px rgba(0,0,0,0.55))" }}>
      <Img src={staticFile(src)} style={{ width: S, height: S, clipPath: "circle(40.5% at 50% 50%)" }} />
    </div>
  );
  const lab = (a: string, b: string, cx: number, o: number) => (
    <div style={{ position: "absolute", left: cx - 170, top: cy + D / 2 + 24, width: 340, opacity: o, textAlign: "center" }}>
      <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.ink}>{a}</SafeText>
      <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono }}>{b}</SafeText>
    </div>
  );
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Imagery>
        {coin(front, L, 1)}
        {coin(other.front, Rx + 40 * (1 - t2), t2)}
      </Imagery>
      {lab(label, trait, L, 1)}
      {t2 > 0 ? lab(other.label, other.trait, Rx, t2) : null}
      <NameBand title={`Cent #${n}`} subtitle={`Inscription #${inscription}`} />
    </div>
  );
};

/**
 * Every Cent that carries a trait, all at once, with the episode's Cent ringed.
 * The count is declared as `readout` and checked against the list it is handed.
 */
export const CentField: React.FC<Anchored & {
  title: string; ns: number[]; mark: number; readout: string; caption: string;
}> = (props) => {
  const { title, ns, mark, readout, caption } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  if (readout !== ns.length.toLocaleString("en-US"))
    throw new Error(`CentField: readout says ${readout} but the list holds ${ns.length}`);
  if (!ns.includes(mark)) throw new Error(`CentField: #${mark} is not in the list`);
  const W = X1 - X0, H = STAGE.y1 - STAGE.y0;
  const lay = fitGrid(ns.length, W, H, 0.1);
  const step = lay.size + lay.gap;
  const rows = Math.ceil(ns.length / lay.cols);
  const left = X0 + (W - (lay.cols * step - lay.gap)) / 2;
  const top = STAGE.y0 + (H - (rows * step - lay.gap)) / 2;
  const ringT = ramp(frame, 30, 12);
  const rT = ramp(frame, 6, 8);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Imagery>
        {ns.map((n, i) => {
          const t = ramp(frame, Math.floor(i * 24 / ns.length), 8);
          const col = i % lay.cols, row = Math.floor(i / lay.cols);
          return (
            <div key={n} style={{ position: "absolute", left: left + col * step, top: top + row * step, opacity: t * (n === mark ? 1 : 1 - 0.35 * ringT) }}>
              <CentImage n={n} size={lay.size} />
              {n === mark ? <div style={{ position: "absolute", inset: -6, border: `4px solid ${COLOR.accent}`, borderRadius: 8, opacity: ringT }} /> : null}
            </div>
          );
        })}
      </Imagery>
      <div style={{ position: "absolute", left: X0, top: TITLE.y0, width: W }}>
        <SafeText role="display" fontSize={68} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
      </div>
      <div style={{ position: "absolute", left: X0, top: BAND.y0, width: W, opacity: rT }}>
        <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{readout}</SafeText>
        <SafeText role="body" fontSize={48} maxLines={1}>{caption}</SafeText>
      </div>
    </div>
  );
};

export const ONECENT = { CentLook, CentCompare, CentField } as const;
for (const C of [CentLook, CentCompare, CentField]) (C as any).wantsAlignment = true;
