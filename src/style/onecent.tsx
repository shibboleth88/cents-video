import React from "react";
import { Img, Loop, OffthreadVideo, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
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

/**
 * The frame (in this shot) at which each word of a quote card is spoken, so the
 * card can light each word as it is read. The card and the recording must agree
 * word for word (punctuation and parentheses aside): a mismatch fails the render.
 */
const nrmWord = (w: string) => w.toLowerCase().replace(/[\u2019']/g, "").replace(/[^a-z0-9]/g, "");
const useSpokenWords = ({ alignment, shotStartFrame }: Anchored, quote?: { at_phrase: string; text: string; spoken?: Record<string, string> }) => {
  const { fps } = useVideoConfig();
  if (!quote) return [] as number[];
  const card = quote.text.split(/\s+/);
  const t0 = findPhrase(alignment, quote.at_phrase).start;
  let i = alignment.words.findIndex((w) => w.start === t0);
  // A card word written as digits ("1912,") is said as several words: `spoken` maps it to them.
  // A token that is punctuation alone (a spaced dash) is not said: it lights with the word before it.
  let last = Math.round(t0 * fps) - shotStartFrame;
  return card.map((w, j) => {
    if (!quote.spoken?.[w] && nrmWord(w) === "") return last;
    const say = (quote.spoken?.[w] ?? w).split(/\s+/);
    const said = alignment.words.slice(i, i + say.length);
    if (said.length < say.length || say.some((s, k) => nrmWord(s) !== nrmWord(said[k]!.word)))
      throw new Error(`quote card word ${j + 1} "${w}" is not the spoken "${said.map((x) => x.word).join(" ")}"`);
    i += say.length;
    return (last = Math.round(said[0]!.start * fps) - shotStartFrame);
  });
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
/** A camera move: to `box` (or the whole coin), starting `plus` s after the
 *  phrase and taking `dur` s. `marks` rings several areas at once; `max` lets a
 *  move go closer than the default 3.2x (the 1050px source softens past ~4). */
type Move = { at_phrase: string; plus?: number; dur?: number; box: Box | null; mark?: boolean; marks?: Box[]; max?: number };
type Read = { at_phrase?: string; readout?: string; caption?: string };
type Concept = { at_phrase: string; label: string };
type Quote = { at_phrase: string; text: string; credit: string; spoken?: Record<string, string> };

export const CentLook: React.FC<Anchored & {
  /** The inscription number, shown under the Cent's name (from the trait export). */
  inscription: number; n: number; front: string; back?: string;
  moves?: Move[]; flip_at?: string; reads?: Read[]; concept?: Concept; quote?: Quote;
  /** Open on the 3DCENTS turn of this Cent, played once (front, back, front), then
   *  settle on the photo at the same size and place, so the zooms follow without a cut. */
  spin?: Clip;
}> = (props) => {
  const { inscription, n, front, back, moves = [], flip_at, reads = [], concept, quote, spin } = props;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useShotFade();
  const opening = React.useContext(OpeningShotCtx);
  const at = useAt(props);
  const W = X1 - X0, H = STAGE.y1 - STAGE.y0;
  const S = SIZE * (0.5 / R);
  const spoken = useSpokenWords(props, quote);

  for (const m of moves) {
    for (const b of [m.box, ...(m.marks ?? [])]) {
      if (!b) continue;
      const [x0, y0, x1, y1] = b;
      if (!(0 <= x0 && x0 < x1 && x1 <= 1 && 0 <= y0 && y0 < y1 && y1 <= 1))
        throw new Error(`CentLook #${n}: box ${b} is not inside the image`);
    }
    if (m.max && m.max > 4.5) throw new Error(`CentLook #${n}: ${m.max}x is past what the 1050px photo holds`);
  }
  if (flip_at && !back) throw new Error(`CentLook #${n}: a flip needs the back image`);
  if (quote && !quote.credit) throw new Error(`CentLook #${n}: a quote must carry its credit`);
  if (spin && !spin.credit) throw new Error(`CentLook #${n}: a 3DCENTS clip must carry its credit`);
  if (spin && moves.length && at(moves[0]!.at_phrase) < spin.frames)
    throw new Error(`CentLook #${n}: the camera moves before the turn has settled on the front`);

  // Camera: each move eases from the state before it. A state is the point of
  // the image at the stage centre and the scale; null is the whole coin.
  const state = (b: Box | null, max = 3.2) => {
    if (!b) return { cx: 0.5, cy: 0.5, k: 1 };
    const [x0, y0, x1, y1] = b;
    return { cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, k: Math.min(W / ((x1 - x0) * S), H / ((y1 - y0) * S), max) };
  };
  let cam = state(null);
  let markBoxes: Box[] = [], markT = 0, prevF0 = -Infinity;
  for (const m of moves) {
    const f0 = at(m.at_phrase) + Math.round((m.plus ?? 0) * fps);
    if (f0 < prevF0) throw new Error(`CentLook #${n}: move "${m.at_phrase}" starts before the move before it`);
    prevF0 = f0;
    const len = Math.max(1, Math.round((m.dur ?? 0.6) * fps));
    const t = ramp(frame, f0, len);
    if (t <= 0) break;
    const to = state(m.box, m.max);
    if (m.mark || m.marks) to.k *= 0.88;   // leave room for the ring inside the stage
    cam = { cx: cam.cx + (to.cx - cam.cx) * t, cy: cam.cy + (to.cy - cam.cy) * t, k: cam.k + (to.k - cam.k) * t };
    markBoxes = m.marks ?? (m.mark && m.box ? [m.box] : []);
    markT = markBoxes.length ? ramp(frame, f0 + Math.min(len, 18) - 4, 12) : 0;
  }
  const sc = cam.k;
  const ox = 540 - cam.cx * S * sc, oy = H / 2 - cam.cy * S * sc;
  // The turn hands over to the photo over its last frames, when the front faces us again.
  const settle = spin ? ramp(frame, spin.frames - 10, 10) : 1;
  const COIN_D = 0.815 * S;              // the coin's measured width in the 1050px photo

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
        {spin && settle < 1 ? (
          // Lighten blend drops the clip's black onto the stage colour (as in WallStandout).
          <div style={{ position: "absolute", left: 0, top: STAGE.y0, width: 1080, height: H, overflow: "hidden",
                        background: COLOR.bg, isolation: "isolate" }}>
            <OffthreadVideo src={staticFile(spin.src)} muted
              style={{ position: "absolute", left: 540 - spin.coin.cx * (COIN_D / spin.coin.d), top: H / 2 - spin.coin.cy * (COIN_D / spin.coin.d),
                       width: spin.width * (COIN_D / spin.coin.d), height: spin.height * (COIN_D / spin.coin.d), mixBlendMode: "lighten" }} />
          </div>
        ) : null}
        <div style={{ position: "absolute", left: 0, top: STAGE.y0, width: 1080, height: H, overflow: "hidden", opacity: enter * dim * settle }}>
          <div style={{ position: "absolute", left: ox, top: oy, width: S * sc, height: S * sc, transform: `scaleX(${sx})` }}>
            <Img src={staticFile(src)} style={{ width: S * sc, height: S * sc, clipPath: "circle(40.5% at 50% 50%)",
                                                filter: `drop-shadow(0 ${SIZE * 0.04}px ${SIZE * 0.06}px rgba(0,0,0,0.55))` }} />
          </div>
          {markT > 0 ? markBoxes.map((b, i) => (
            <div key={i} style={{ position: "absolute", left: ox + b[0] * S * sc - 12, top: oy + b[1] * S * sc - 12,
                          width: (b[2] - b[0]) * S * sc + 24, height: (b[3] - b[1]) * S * sc + 24,
                          border: `6px solid ${COLOR.accent}`, borderRadius: 18, opacity: markT * (1 - qT),
                          boxShadow: "0 0 0 2px rgba(0,0,0,0.45), inset 0 0 0 2px rgba(0,0,0,0.45)" }} />
          )) : null}
        </div>
      </Imagery>
      <NameBand title={`Cent #${n}`} subtitle={`Inscription #${inscription}`} />
      {spin && settle < 1 ? (
        <div style={{ position: "absolute", left: X0, top: STAGE.y1 - 46, width: X1 - X0, opacity: 0.8 * (1 - settle) }}>
          <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.inkDim} style={{ fontFamily: TYPE.body, textAlign: "center" }}>{spin.credit}</SafeText>
        </div>
      ) : null}
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
          <SafeText role="body" fontSize={54} maxLines={9} style={{ fontWeight: 500, textWrap: "pretty" }}
                    wordOpacity={spoken.map((f) => (frame >= f ? 1 : 0.38))}
                    wordColor={spoken.map((f, i) => (frame >= f && (i === spoken.length - 1 || frame < spoken[i + 1]!) ? COLOR.accent : undefined))}>
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


const CUTOUT: React.CSSProperties = { clipPath: "circle(40.5% at 50% 50%)" };   // 300px images: the coin on black, not on its white square

type Clip = { src: string; width: number; height: number; frames: number; coin: { cx: number; cy: number; d: number }; credit: string };

/**
 * The Cent's card: its name, its inscription number, and the user's 3DCENTS turn
 * of it, looped. Opens the film and closes it. `reads` work as in CentLook; a
 * read without a phrase shows from the first frame.
 */
export const CentSpin: React.FC<Anchored & { inscription: number; n: number; clip: Clip; reads?: Read[]; size?: number }> = (props) => {
  const { inscription, n, clip, reads = [], size = 600 } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const opening = React.useContext(OpeningShotCtx);
  const at = useAt(props);
  if (!clip.credit) throw new Error(`CentSpin #${n}: a 3DCENTS clip must carry its credit`);
  const H = STAGE.y1 - STAGE.y0;
  const k = size / clip.coin.d;
  // No fade-in of our own: a partial opacity on the blend group shows its rectangle. The shot fade carries the entrance.
  const enter = 1;
  let cur: Read | undefined, curFrom = 0;
  for (const r of reads) { const f = r.at_phrase ? at(r.at_phrase) : 0; if (frame >= f) { cur = r; curFrom = f; } }
  const rT = cur ? (curFrom === 0 && opening ? 1 : ramp(frame, curFrom, 8)) : 0;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Imagery>
        {/* The clip's black background is dropped with a lighten blend onto the stage colour, as in WallStandout. */}
        <div style={{ position: "absolute", left: 0, top: STAGE.y0, width: 1080, height: H - 50, overflow: "hidden", opacity: enter,
                      background: COLOR.bg, isolation: "isolate" }}>
          <Loop durationInFrames={clip.frames} layout="none">
            <OffthreadVideo src={staticFile(clip.src)} muted
              style={{ position: "absolute", left: 540 - clip.coin.cx * k, top: (H - 50) / 2 - clip.coin.cy * k,
                       width: clip.width * k, height: clip.height * k, mixBlendMode: "lighten" }} />
          </Loop>
        </div>
      </Imagery>
      <NameBand title={`Cent #${n}`} subtitle={`Inscription #${inscription}`} />
      <div style={{ position: "absolute", left: X0, top: STAGE.y1 - 46, width: X1 - X0, opacity: 0.8 }}>
        <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.inkDim} style={{ fontFamily: TYPE.body, textAlign: "center" }}>{clip.credit}</SafeText>
      </div>
      {cur ? (
        <div style={{ position: "absolute", left: X0, top: BAND.y0, width: X1 - X0, opacity: rT, transform: `translateY(${(1 - rT) * 14}px)` }}>
          {cur.readout ? <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{cur.readout}</SafeText> : null}
          {cur.caption ? <SafeText role="body" fontSize={48} maxLines={1}>{cur.caption}</SafeText> : null}
        </div>
      ) : null}
    </div>
  );
};

type Card = { n: number; inscription: number; front: string; readout: string; caption: string };

/**
 * Two Cents in one place, dissolving into each other on phrases: the episode's
 * Cent and a template Cent. Each state is a whole card (name, inscription,
 * coin, readout), so the name on screen always belongs to the coin on screen.
 */
export const CentDissolve: React.FC<Anchored & { a: Card; b: Card; first: "a" | "b"; swaps: { at_phrase: string; to: "a" | "b" }[] }> = (props) => {
  const { a, b, first, swaps } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  let showB = first === "b" ? 1 : 0, last = first;
  for (const s of swaps) {
    if (s.to === last) throw new Error(`CentDissolve: "${s.at_phrase}" dissolves to the Cent already shown`);
    last = s.to;
    const t = ramp(frame, at(s.at_phrase), 16);
    showB = showB + ((s.to === "b" ? 1 : 0) - showB) * t;
  }
  const H = STAGE.y1 - STAGE.y0;
  const D = 600, S = D * (0.5 / R);
  const card = (c: Card, o: number) => (
    <div style={{ position: "absolute", inset: 0, opacity: o }}>
      <Imagery>
        <div style={{ position: "absolute", left: 540 - S / 2, top: STAGE.y0 + H / 2 - S / 2, width: S, height: S,
                      filter: "drop-shadow(0 18px 26px rgba(0,0,0,0.55))" }}>
          <Img src={staticFile(c.front)} style={{ width: S, height: S, clipPath: "circle(40.5% at 50% 50%)" }} />
        </div>
      </Imagery>
      <div style={{ position: "absolute", left: X0, top: TITLE.y0, width: X1 - X0 }}>
        <SafeText role="display" fontSize={84} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{`Cent #${c.n}`}</SafeText>
        <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim}>{`Inscription #${c.inscription}`}</SafeText>
      </div>
      <div style={{ position: "absolute", left: X0, top: BAND.y0, width: X1 - X0 }}>
        <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{c.readout}</SafeText>
        <SafeText role="body" fontSize={48} maxLines={1}>{c.caption}</SafeText>
      </div>
    </div>
  );
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      {card(a, 1 - showB)}
      {card(b, showB)}
    </div>
  );
};

/**
 * A quick close-up scroll through every Cent in a list (e.g. a trait's whole
 * pool), large enough to see each one, on black. The episode's Cent is ringed.
 * The scroll runs from the shot's start to `until`; the readout is checked
 * against the list.
 */
export const CentScroll: React.FC<Anchored & {
  title: string; ns: number[]; mark?: number; readout: string; caption: string; until: string; cols?: number;
}> = (props) => {
  const { title, ns, mark, readout, caption, until, cols = 4 } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  if (readout !== ns.length.toLocaleString("en-US"))
    throw new Error(`CentScroll: readout says ${readout} but the list holds ${ns.length}`);
  if (mark !== undefined && !ns.includes(mark)) throw new Error(`CentScroll: #${mark} is not in the list`);
  const W = X1 - X0, H = STAGE.y1 - STAGE.y0;
  const step = Math.floor(W / cols), size = Math.floor(step * 0.92);
  const rows = Math.ceil(ns.length / cols);
  const travel = Math.max(0, rows * step - H);
  const fEnd = at(until);
  // Hold the first rows a moment, run, and settle on the last rows before the cut.
  const p = interpolate(frame, [8, fEnd - 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });
  const y = -travel * p;
  const rT = ramp(frame, 4, 8);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Imagery>
        <div style={{ position: "absolute", left: X0, top: STAGE.y0, width: W, height: H, overflow: "hidden",
                      maskImage: "linear-gradient(to bottom, transparent 0, black 40px, black calc(100% - 40px), transparent 100%)",
                      WebkitMaskImage: "linear-gradient(to bottom, transparent 0, black 40px, black calc(100% - 40px), transparent 100%)" }}>
          {ns.map((n, i) => {
            const top = Math.floor(i / cols) * step + y;
            if (top < -step || top > H) return null;
            return (
              <div key={n} style={{ position: "absolute", left: (i % cols) * step + (step - size) / 2, top }}>
                <CentImage n={n} size={size} style={CUTOUT} />
                {n === mark ? <div style={{ position: "absolute", inset: size * 0.06, border: `5px solid ${COLOR.accent}`, borderRadius: "50%" }} /> : null}
              </div>
            );
          })}
        </div>
      </Imagery>
      <div style={{ position: "absolute", left: X0, top: TITLE.y0, width: W }}>
        <SafeText role="display" fontSize={84} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
      </div>
      <div style={{ position: "absolute", left: X0, top: BAND.y0, width: W, opacity: rT }}>
        <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{readout}</SafeText>
        <SafeText role="body" fontSize={48} maxLines={1}>{caption}</SafeText>
      </div>
    </div>
  );
};

/** A small set of Cents, all shown, on black, numbered under each. */
export const CentSet: React.FC<Anchored & { title: string; ns: number[]; readout: string; caption: string; cols?: number }> = (props) => {
  const { title, ns, readout, caption, cols = 3 } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  if (readout !== ns.length.toLocaleString("en-US"))
    throw new Error(`CentSet: readout says ${readout} but the list holds ${ns.length}`);
  const W = X1 - X0, H = STAGE.y1 - STAGE.y0, labelH = 56;
  const rows = Math.ceil(ns.length / cols);
  const cellW = W / cols, cellH = H / rows;
  const size = Math.floor(Math.min(cellW * 0.9, cellH - labelH - 8));
  const rT = ramp(frame, 6, 8);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Imagery>
        {ns.map((n, i) => {
          const r = Math.floor(i / cols), inRow = Math.min(cols, ns.length - r * cols);
          const left = X0 + (W - inRow * cellW) / 2 + (i % cols) * cellW + (cellW - size) / 2;
          const top = STAGE.y0 + r * cellH;
          return (
            <div key={n} style={{ position: "absolute", left, top, opacity: ramp(frame, i * 3, 8) }}>
              <CentImage n={n} size={size} style={CUTOUT} />
            </div>
          );
        })}
      </Imagery>
      {ns.map((n, i) => {
        const r = Math.floor(i / cols), inRow = Math.min(cols, ns.length - r * cols);
        const left = X0 + (W - inRow * cellW) / 2 + (i % cols) * cellW;
        return (
          <div key={n} style={{ position: "absolute", left, top: STAGE.y0 + r * cellH + size + 4, width: cellW, opacity: ramp(frame, i * 3, 8) }}>
            <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.inkDim} style={{ textAlign: "center" }}>{`#${n}`}</SafeText>
          </div>
        );
      })}
      <div style={{ position: "absolute", left: X0, top: TITLE.y0, width: W }}>
        <SafeText role="display" fontSize={84} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
      </div>
      <div style={{ position: "absolute", left: X0, top: BAND.y0, width: W, opacity: rT }}>
        <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{readout}</SafeText>
        <SafeText role="body" fontSize={48} maxLines={1}>{caption}</SafeText>
      </div>
    </div>
  );
};

/**
 * The mint-year charts of Lehnen's "Reflections on Mint Years" (made by
 * @daidatep), redrawn for the tall frame: a ring around one Cent, the share of
 * Cents older than a year in the light colour, the rest in slate, as in the
 * originals. Each step arrives on its phrase and the ring eases to it, so the
 * shrinking share is seen. The share is checked against the count it states.
 */
type MintStep = { at_phrase?: string; before: number; count: number; pct: string };
export const MintRing: React.FC<Anchored & {
  title: string; subtitle: string; n: number; front: string; total: number; steps: MintStep[];
}> = (props) => {
  const { title, subtitle, front, total, steps } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  if (steps.length === 0) throw new Error("MintRing: no steps");
  steps.forEach((s, k) => {
    if (k > 0 && !s.at_phrase) throw new Error(`MintRing: step ${k + 1} has no anchor`);
    if (s.pct !== `${((100 * s.count) / total).toFixed(2)}%`)
      throw new Error(`MintRing: ${s.pct} is not ${s.count} of ${total}`);
  });
  const starts = steps.map((s) => (s.at_phrase ? at(s.at_phrase) : 0));
  let i = 0;
  for (let k = 0; k < starts.length; k++) if (frame >= starts[k]!) i = k;
  // The ring eases from the share before to this one.
  const t = i === 0 ? 1 : ramp(frame, starts[i]!, 24);
  const share = (k: number) => steps[k]!.count / total;
  const f = i === 0 ? share(0) : share(i - 1) + (share(i) - share(i - 1)) * t;
  const W = X1 - X0, H = STAGE.y1 - STAGE.y0;
  const D = Math.min(W, H) - 20;                 // the ring's outer diameter
  const RO = D / 2, RI = RO - 54, cx = 540, cy = H / 2;
  // Older share drawn counter-clockwise from twelve o'clock, as in the originals.
  const arc = (r: number, frac: number) => {
    const a = -Math.PI / 2 - 2 * Math.PI * Math.min(frac, 0.9999);
    return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a), large: frac > 0.5 ? 1 : 0 };
  };
  const o = arc(RO, f), n = arc(RI, f);
  const wedge = `M ${cx} ${cy - RO} A ${RO} ${RO} 0 ${o.large} 0 ${o.x} ${o.y} L ${n.x} ${n.y} A ${RI} ${RI} 0 ${n.large} 1 ${cx} ${cy - RI} Z`;
  const face = arc(RI - 10, f);
  const faceWedge = `M ${cx} ${cy} L ${cx} ${cy - RI + 10} A ${RI - 10} ${RI - 10} 0 ${face.large} 0 ${face.x} ${face.y} Z`;
  const coinD = 2 * (RI - 10);
  const S = coinD / (2 * R);
  const step = steps[i]!;
  const rT = i === 0 ? ramp(frame, 4, 8) : ramp(frame, starts[i]!, 10);
  const OLD = "#d8c9ae", NEW = "#7d90a8";
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Imagery>
        <div style={{ position: "absolute", left: 0, top: STAGE.y0, width: 1080, height: H, opacity: ramp(frame, 0, 12) }}>
          <Img src={staticFile(front)} style={{ position: "absolute", left: cx - S / 2, top: cy - S / 2, width: S, height: S,
                                                clipPath: `circle(${(coinD / 2 / S) * 100}% at 50% 50%)` }} />
          <svg width={1080} height={H} style={{ position: "absolute", left: 0, top: 0 }}>
            <circle cx={cx} cy={cy} r={(RO + RI) / 2} fill="none" stroke={NEW} strokeWidth={RO - RI} />
            <path d={wedge} fill={OLD} />
            <path d={faceWedge} fill={OLD} opacity={0.42} />
            <line x1={cx} y1={cy - RO - 6} x2={cx} y2={cy} stroke={COLOR.accent} strokeWidth={3} opacity={0.9} />
          </svg>
        </div>
      </Imagery>
      <div style={{ position: "absolute", left: X0, top: TITLE.y0, width: W }}>
        <SafeText role="display" fontSize={84} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
        <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim}>{subtitle}</SafeText>
      </div>
      <div style={{ position: "absolute", left: X0, top: BAND.y0, width: W, opacity: rT, transform: `translateY(${(1 - rT) * 14}px)` }}>
        <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{step.pct}</SafeText>
        <SafeText role="body" fontSize={48} maxLines={1}>{`from before ${step.before}: ${step.count.toLocaleString("en-US")} Cents`}</SafeText>
      </div>
    </div>
  );
};

export const ONECENT = { CentLook, CentCompare, CentField, CentSpin, CentDissolve, CentScroll, CentSet, MintRing } as const;
for (const C of [CentLook, CentCompare, CentField, CentSpin, CentDissolve, CentScroll, CentSet, MintRing]) (C as any).wantsAlignment = true;
