import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { EASE, OpeningShotCtx, useEntrance, useShotFade } from "./motion";
import { COLOR, SAFE, TYPE } from "./tokens";
import { Imagery, SafeText } from "./Safe";
import { findPhrase, type Alignment } from "../lib/timeline";

/**
 * Shots for a themed Collector Wall episode built around a collector's own
 * question ("what should I add next?"): the question and the replies as chat
 * cards, the gaps a Set or badge would fill as empty slots, a year chart, a
 * quotation over its picture, and the closing question to viewers.
 *
 * Every Cent drawn is a real Cent by number (1050px cents.vision front); every
 * figure is handed in by the timeline, which takes it from the dated snapshot.
 * Names render exactly as the claimed Walls render them. No avatars, no wallet
 * addresses.
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

const NameBand: React.FC<{ title: string; subtitle?: string }> = ({ title, subtitle }) => {
  const e = useEntrance("rise", 0);
  const opening = React.useContext(OpeningShotCtx);   // the film's first frame is its preview: already in
  return (
    <div style={{ position: "absolute", left: X0, top: TITLE.y0, width: X1 - X0,
                  opacity: opening ? 1 : e.opacity, transform: `translateY(${opening ? 0 : e.y}px)` }}>
      <SafeText role="display" fontSize={68} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
      {subtitle ? <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim}>{subtitle}</SafeText> : null}
    </div>
  );
};

/** Readout + caption in the band under the stage, as WallStandout draws them. Steps through states on cue. */
type ReadoutState = { at_phrase?: string; text: string; caption?: string };
const Band: React.FC<{ states: ReadoutState[]; at: (p: string) => number; frame: number }> = ({ states, at, frame }) => {
  const starts = states.map((s, i) => (s.at_phrase ? at(s.at_phrase) : i === 0 ? 10 : NaN));
  if (starts.some((f) => Number.isNaN(f))) throw new Error("Band: every readout state after the first needs an at_phrase");
  for (let i = 1; i < starts.length; i++) if (starts[i]! <= starts[i - 1]!) throw new Error("Band: readout states must come in spoken order");
  let k = -1;
  starts.forEach((f, i) => { if (frame >= f) k = i; });
  if (k < 0) return null;
  const s = states[k]!;
  const op = fadeIn(frame, starts[k]!);
  return (
    <div style={{ position: "absolute", left: X0, top: BAND.y0, width: X1 - X0, opacity: op }}>
      <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{s.text}</SafeText>
      {s.caption ? <SafeText role="body" fontSize={48} maxLines={1}>{s.caption}</SafeText> : null}
    </div>
  );
};

/** A 1050px cents.vision front, clipped to its coin, drawn so the coin is `d` px across. */
const Coin: React.FC<{ src: string; d: number; style?: React.CSSProperties }> = ({ src, d, style }) => {
  const S = d * (0.5 / 0.402);       // the fronts put the coin in a circle of radius ~0.40 of the image
  return (
    <div style={{ width: d, height: d, position: "relative", ...style }}>
      <Img src={staticFile(src)} style={{ position: "absolute", left: (d - S) / 2, top: (d - S) / 2, width: S, height: S,
                                          clipPath: "circle(40.5% at 50% 50%)",
                                          filter: `drop-shadow(0 ${d * 0.04}px ${d * 0.06}px rgba(0,0,0,0.55))` }} />
    </div>
  );
};

// ---------------------------------------------------------------------------

type Msg = { name: string; text: string; at_phrase?: string };

/**
 * Chat messages, retyped word for word on our own card (no avatars, no app
 * chrome): each name in copper as its claimed Wall renders it, the message
 * under it. Each message fades in on its cue; all are laid out from frame 0 so
 * nothing reflows.
 */
export const ChatCard: React.FC<Anchored & { title: string; subtitle?: string; messages: Msg[]; textSize?: number }> = (props) => {
  const { title, subtitle, messages, textSize = 54 } = props;
  if (!messages.length) throw new Error("ChatCard: no messages");
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  const starts = messages.map((m, i) => (m.at_phrase ? at(m.at_phrase) : 6 + i * 10));
  // The card must not stand empty: its first message enters within 0.5 s of the shot.
  // (LEDGER: a shot's start is not the moment its content appears. The first render held this card
  // empty for 1.7 s, cued on "Dopemind asked" in a shot that began on "In the Numismatists Discord".)
  if (starts[0]! > 15) throw new Error(`ChatCard: first message enters at frame ${starts[0]} of the shot; the card would stand empty`);
  const panel = useEntrance("place", 0);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <NameBand title={title} subtitle={subtitle} />
      <div style={{ position: "absolute", left: X0 - 20, top: STAGE.y0, width: X1 - X0 + 40, height: BAND.y1 - STAGE.y0,
                    display: "flex", flexDirection: "column", justifyContent: "center" }}>
        <div style={{ background: COLOR.surface, borderRadius: 28, border: `2px solid ${COLOR.rule}`, padding: "34px 20px",
                      display: "flex", flexDirection: "column", gap: 40,
                      opacity: panel.opacity, transform: `translateY(${panel.y}px) scale(${panel.scale})` }}>
          {messages.map((m, i) => {
            const op = fadeIn(frame, starts[i]!, 12);
            return (
              <div key={i} style={{ opacity: op, transform: `translateY(${(1 - op) * 14}px)` }}>
                <SafeText role="body" fontSize={48} maxLines={1} color={COLOR.accent} style={{ fontWeight: 700 }}>{m.name}</SafeText>
                <SafeText role="body" fontSize={textSize} maxLines={7} style={{ marginTop: 8, lineHeight: 1.25 }}>{m.text}</SafeText>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------

type Slot = { label: string; sub?: string; src?: string; appear_at?: string; fill_at?: string };

/**
 * Slots for what a Set or badge asks for: a filled slot is a real Cent (its
 * 1050px front), an empty one a dashed ring with its label. `appear_at` brings
 * a slot in on its cue; `fill_at` drops a Cent into an empty slot on its cue,
 * so the shot shows the gap first and then what would fill it.
 */
export const GapSlots: React.FC<Anchored & { title: string; subtitle?: string; slots: Slot[]; cols?: number; readouts?: ReadoutState[] }> = (props) => {
  const { title, subtitle, slots, readouts = [] } = props;
  if (!slots.length || slots.length > 6) throw new Error("GapSlots: 1 to 6 slots");
  const cols = props.cols ?? Math.min(slots.length, 3);
  const rows = Math.ceil(slots.length / cols);
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  const W = X1 - X0, H = STAGE.y1 - STAGE.y0;
  const labelH = 120;
  const gap = 36;
  const d = Math.floor(Math.min((W - gap * (cols - 1)) / cols, (H - rows * labelH - gap * (rows - 1)) / rows, 300));
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <NameBand title={title} subtitle={subtitle} />
      <div style={{ position: "absolute", left: X0, top: STAGE.y0, width: W, height: H,
                    display: "grid", gridTemplateColumns: `repeat(${cols}, ${d}px)`, justifyContent: "center", alignContent: "center",
                    columnGap: gap, rowGap: gap }}>
        {slots.map((s, i) => {
          const a = s.appear_at ? at(s.appear_at) : 4 + i * 4;
          const ap = fadeIn(frame, a, 10);
          const f = s.src ? (s.fill_at ? at(s.fill_at) : -1) : Infinity;
          const filled = frame >= f;
          const pop = s.fill_at && s.src ? interpolate(frame, [f, f + 10, f + 16], [0.6, 1.06, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 1;
          const ring = s.fill_at ? interpolate(frame, [f, f + 6, f + 30], [0, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 0;
          return (
            <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", opacity: ap, transform: `translateY(${(1 - ap) * 16}px)` }}>
              <div style={{ width: d, height: d, position: "relative" }}>
                {filled && s.src ? (
                  <Imagery><Coin src={s.src} d={d} style={{ transform: `scale(${pop})` }} /></Imagery>
                ) : (
                  <div style={{ position: "absolute", inset: d * 0.04, borderRadius: "50%", border: `5px dashed ${COLOR.inkDim}`, opacity: 0.8 }} />
                )}
                {ring > 0 ? <div style={{ position: "absolute", inset: -8, borderRadius: "50%", border: `6px solid ${COLOR.accent}`, opacity: ring,
                                          boxShadow: `0 0 28px ${COLOR.accent}` }} /> : null}
              </div>
              <div style={{ marginTop: 14, width: d + gap, textAlign: "center" }}>
                <SafeText role="label" fontSize={44} maxLines={1} color={filled && s.src ? COLOR.ink : COLOR.inkDim}
                          style={{ textAlign: "center", fontFamily: TYPE.mono, fontWeight: 700 }}>{s.label}</SafeText>
                {s.sub ? <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.inkDim} style={{ textAlign: "center" }}>{s.sub}</SafeText> : null}
              </div>
            </div>
          );
        })}
      </div>
      {readouts.length ? <Band states={readouts} at={at} frame={frame} /> : null}
    </div>
  );
};

// ---------------------------------------------------------------------------

/**
 * Cents per year as horizontal bars, one year lit in copper on its cue. The
 * counts are handed in (from merged-new2.json, dated) and checked for sense.
 */
export const YearBars: React.FC<Anchored & { title: string; subtitle?: string; bars: { label: string; value: number }[]; highlight: string; highlight_at: string; readouts?: ReadoutState[] }> = (props) => {
  const { title, subtitle, bars, highlight, highlight_at, readouts = [] } = props;
  if (!bars.some((b) => b.label === highlight)) throw new Error(`YearBars: no bar "${highlight}" to light`);
  if (bars.some((b) => !Number.isInteger(b.value) || b.value <= 0)) throw new Error("YearBars: every value must be a positive count");
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  const hf = at(highlight_at);
  const lit = fadeIn(frame, hf, 10);
  const max = Math.max(...bars.map((b) => b.value));
  const H = STAGE.y1 - STAGE.y0, rowH = Math.floor(H / bars.length);
  const labelW = 130, valueW = 110, barW = X1 - X0 - labelW - valueW - 20;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <NameBand title={title} subtitle={subtitle} />
      {bars.map((b, r) => {
        const grow = interpolate(frame, [3 + r * 2, 23 + r * 2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out });
        const me = b.label === highlight;
        const color = me ? (lit > 0 ? COLOR.accent : COLOR.inkDim) : COLOR.rule;
        const dim = me ? 1 : 1 - 0.45 * lit;
        return (
          <div key={b.label} style={{ position: "absolute", left: X0, top: STAGE.y0 + r * rowH, height: rowH, width: X1 - X0,
                                      display: "flex", alignItems: "center", gap: 10, opacity: dim }}>
            <div style={{ width: labelW }}>
              <SafeText role="label" fontSize={42} maxLines={1} color={me && lit > 0 ? COLOR.accent : COLOR.inkDim} style={{ fontFamily: TYPE.mono }}>{b.label}</SafeText>
            </div>
            <div style={{ width: barW, height: rowH * 0.56, position: "relative" }}>
              <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: barW * (b.value / max) * grow, background: color, borderRadius: 6,
                            boxShadow: me && lit > 0 ? `0 0 ${18 * lit}px ${COLOR.accent}` : undefined }} />
            </div>
            <div style={{ width: valueW, opacity: grow }}>
              <SafeText role="label" fontSize={42} maxLines={1} color={me && lit > 0 ? COLOR.accent : COLOR.ink} style={{ fontFamily: TYPE.mono, textAlign: "right" }}>{String(b.value)}</SafeText>
            </div>
          </div>
        );
      })}
      {readouts.length ? <Band states={readouts} at={at} frame={frame} /> : null}
    </div>
  );
};

// ---------------------------------------------------------------------------

/**
 * A quotation, credited, under its picture: a photograph or page (`src`, with
 * its caption) or a Cent (`cent`, a 1050px front). The quote comes in on its
 * cue and the picture eases up to make room, so the picture reads alone first.
 */
export const QuoteOver: React.FC<Anchored & {
  title: string; subtitle?: string;
  src?: string; img_w?: number; img_h?: number; img_caption?: string; cent?: string;
  quote: string; attribution: string; quote_at: string; quoteSize?: number;
}> = (props) => {
  const { title, subtitle, src, img_w, img_h, img_caption, cent, quote, attribution, quote_at, quoteSize = 52 } = props;
  if (!!src === !!cent) throw new Error("QuoteOver: give a picture (src) or a Cent (cent), not both or neither");
  if (src && !(img_w && img_h)) throw new Error("QuoteOver: a picture needs its img_w and img_h");
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  const q = at(quote_at);
  const t = interpolate(frame, [q, q + 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });
  const W = X1 - X0;
  // The picture reads alone first, then shrinks to make room for the quote.
  const k = 1 - 0.4 * t;
  const picW = src ? Math.round(Math.min(W, img_w!) * k) : 0;
  const picH = src ? Math.round(picW * img_h! / img_w!) : Math.round(360 * k);
  const top0 = STAGE.y0 + 120, top1 = STAGE.y0;
  const drift = interpolate(frame, [0, 300], [1, 1.04]);
  const pic = useEntrance("place", 0);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <NameBand title={title} subtitle={subtitle} />
      <div style={{ position: "absolute", left: X0, top: top0 + (top1 - top0) * t, width: W,
                    display: "flex", flexDirection: "column", alignItems: "center", opacity: pic.opacity }}>
        <Imagery>
          {src ? (
            <div style={{ width: picW, height: picH, overflow: "hidden", border: `1px solid ${COLOR.rule}` }}>
              <Img src={staticFile(src)} style={{ width: picW, height: picH, objectFit: "cover", transform: `scale(${drift})` }} />
            </div>
          ) : (
            <Coin src={cent!} d={picH} />
          )}
        </Imagery>
        {img_caption ? (
          <div style={{ marginTop: 12, width: W }}>
            <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.inkDim} style={{ textAlign: "center", fontFamily: TYPE.body }}>{img_caption}</SafeText>
          </div>
        ) : null}
        <div style={{ marginTop: 34, width: W, opacity: t, transform: `translateY(${(1 - t) * 20}px)` }}>
          <SafeText role="body" fontSize={quoteSize} maxLines={6} style={{ lineHeight: 1.22, fontWeight: 500 }}>{quote}</SafeText>
          <SafeText role="body" fontSize={46} maxLines={2} color={COLOR.accent} style={{ marginTop: 18 }}>{attribution}</SafeText>
        </div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------

type Option = { label: string; src?: string };

/**
 * The closing question to viewers, over the options the episode put forward:
 * each a real Cent (1050px front) by number, or an empty ring for an answer
 * that names a year rather than a Cent.
 */
export const AskCard: React.FC<Anchored & { question: string; options: Option[]; cols?: number; note?: string }> = (props) => {
  const { question, options, cols = 4, note } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const q = useEntrance("rise", 0);
  const W = X1 - X0;
  const gap = 22;
  const d = Math.floor(Math.min((W - gap * (cols - 1)) / cols, 170));
  // Each option is exactly d wide (label included), so `cols` really fit in a row.
  // v1 made the label d + gap wide: 4 columns no longer fitted, the options wrapped
  // to three rows and the last Cent sat on the note. Refuse that instead of drawing it.
  const GRID_TOP = 660, ROW_GAP = 30, ROW_H = d + 8 + 56;          // coin, gap, one 42px label line
  const rows = Math.ceil(options.length / cols);
  const gridBottom = GRID_TOP + rows * ROW_H + (rows - 1) * ROW_GAP;
  const NOTE_TOP = BAND.y0 + 60;
  if (note && gridBottom > NOTE_TOP) throw new Error(`AskCard: ${rows} rows end at y=${gridBottom}, under the note at ${NOTE_TOP}`);
  const pulse = 1 + 0.03 * Math.sin(Math.max(0, frame - 30) / 9);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <div style={{ position: "absolute", left: X0, top: TITLE.y0 + 10, width: W, opacity: q.opacity, transform: `translateY(${q.y}px)` }}>
        <SafeText role="display" fontSize={80} maxLines={3} style={{ fontWeight: 700, letterSpacing: -1, lineHeight: 1.1 }}>{question}</SafeText>
      </div>
      <div style={{ position: "absolute", left: X0, top: GRID_TOP, width: W,
                    display: "flex", flexWrap: "wrap", justifyContent: "center", columnGap: gap, rowGap: ROW_GAP }}>
        {options.map((o, i) => {
          const op = fadeIn(frame, 10 + i * 4, 10);
          return (
            <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", opacity: op, transform: `translateY(${(1 - op) * 14}px)` }}>
              <div style={{ width: d, height: d, position: "relative", transform: `scale(${pulse})` }}>
                {o.src ? <Imagery><Coin src={o.src} d={d} /></Imagery>
                       : <div style={{ position: "absolute", inset: d * 0.05, borderRadius: "50%", border: `5px dashed ${COLOR.accent}` }} />}
              </div>
              <div style={{ marginTop: 8, width: d }}>
                <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.ink} style={{ textAlign: "center", fontFamily: TYPE.mono }}>{o.label}</SafeText>
              </div>
            </div>
          );
        })}
      </div>
      {note ? (
        <div style={{ position: "absolute", left: X0, top: NOTE_TOP, width: W, opacity: fadeIn(frame, 24) }}>
          <SafeText role="body" fontSize={48} maxLines={2} color={COLOR.accent} style={{ textAlign: "center" }}>{note}</SafeText>
        </div>
      ) : null}
    </div>
  );
};

// ---------------------------------------------------------------------------

type Move = { at_phrase?: string; box: [number, number, number, number]; mark?: boolean };

/** Camera keys over time: hold each framing until the next cue, then ease to it over 18 frames. */
const useCamera = <K extends { k: number; cx: number; cy: number }>(keys: (K & { f: number })[], frame: number) => {
  for (let i = 1; i < keys.length; i++)
    if (keys[i]!.f < keys[i - 1]!.f) throw new Error("camera: moves are out of spoken order");
  let c = keys[0]!;
  let arrived = { i: 0, t: 1 };
  for (let i = 1; i < keys.length; i++) {
    const a = c, b = keys[i]!;
    if (frame < b.f) break;
    const t = interpolate(frame, [b.f, b.f + 18], [0, 1], { extrapolateRight: "clamp", easing: EASE.inOut });
    c = { ...b, k: a.k + (b.k - a.k) * t, cx: a.cx + (b.cx - a.cx) * t, cy: a.cy + (b.cy - a.cy) * t };
    arrived = { i, t: interpolate(frame, [b.f + 14, b.f + 26], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) };
  }
  return { c, arrived };
};

/**
 * A real screenshot (a Discord message, a cents.vision page), under a title
 * band, with the camera moving across it as the narration reaches each part,
 * so a line too long to read whole is read in zoomed sections. Boxes are in
 * the screenshot's own pixels. `start` is the opening framing (default: the
 * whole image). With `min_scale`, a move that would leave the text smaller
 * than that scale refuses: a zoom-in that cannot be read is not a zoom-in.
 */
export const ScreenCrop: React.FC<Anchored & {
  title: string; subtitle?: string; src: string; width: number; height: number;
  start?: [number, number, number, number]; moves?: Move[]; min_scale?: number;
}> = (props) => {
  const { title, subtitle, src, width, height, moves = [], min_scale } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  const AREA = { x0: 40, x1: 1040, y0: STAGE.y0, y1: BAND.y1 };
  const AW = AREA.x1 - AREA.x0, AH = AREA.y1 - AREA.y0;
  const cam = (b: [number, number, number, number], check: boolean, mark = false) => {
    const [x0, y0, x1, y1] = b;
    if (x0 < 0 || y0 < 0 || x1 > width || y1 > height || x1 <= x0 || y1 <= y0)
      throw new Error(`ScreenCrop: box ${b} is outside the ${width}x${height} image`);
    // A marked box leaves room for its ring: a box that filled the stage edge to edge drew a ring with no sides (v2 draft).
    const k = Math.min(AW / (x1 - x0), AH / (y1 - y0), 2.6) * (mark ? 0.9 : 1);
    if (check && min_scale && k < min_scale) throw new Error(`ScreenCrop: box ${b} shows the image at ${k.toFixed(2)}x, under min_scale ${min_scale}`);
    return { k, cx: (x0 + x1) / 2, cy: (y0 + y1) / 2 };
  };
  const keys = [{ f: 0, box: null as null | number[], mark: false, ...cam(props.start ?? [0, 0, width, height], false) },
                ...moves.map((m, i) => ({ f: m.at_phrase ? at(m.at_phrase) : 20 + i * 30, box: m.box as number[], mark: !!m.mark, ...cam(m.box, true, !!m.mark) }))];
  const { c, arrived } = useCamera(keys, frame);
  const mk = keys[arrived.i]!;
  const left = AW / 2 - c.cx * c.k, top = AH / 2 - c.cy * c.k;
  const enter = useEntrance("place", 0);
  // Opening the film, the screenshot is the preview frame: in from frame 0 (v2 draft opened at YMAX 11).
  const opening = React.useContext(OpeningShotCtx);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <NameBand title={title} subtitle={subtitle} />
      <Imagery>
        <div style={{ position: "absolute", left: AREA.x0, top: AREA.y0, width: AW, height: AH, overflow: "hidden", borderRadius: 18,
                      opacity: opening ? 1 : enter.opacity }}>
          <Img src={staticFile(src)} style={{ position: "absolute", left, top, width: width * c.k, height: height * c.k }} />
          {mk.mark && mk.box ? (
            <div style={{ position: "absolute", left: left + mk.box[0]! * c.k - 10, top: top + mk.box[1]! * c.k - 10,
                          width: (mk.box[2]! - mk.box[0]!) * c.k + 20, height: (mk.box[3]! - mk.box[1]!) * c.k + 20,
                          border: `5px solid ${COLOR.accent}`, borderRadius: 16, opacity: arrived.t }} />
          ) : null}
        </div>
      </Imagery>
    </div>
  );
};

export const ASKNEXT = { ChatCard, GapSlots, YearBars, QuoteOver, AskCard, ScreenCrop } as const;
for (const C of Object.values(ASKNEXT)) (C as any).wantsAlignment = true;
