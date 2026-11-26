import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { EASE, useShotFade } from "./motion";
import { Imagery, SafeText } from "./Safe";
import { findPhrase, type Alignment } from "../lib/timeline";
import { useSpokenWords } from "./onecent";
import { LOOK_C } from "./storyopen";
import { loadFonts } from "./fonts";

loadFonts();

/**
 * Look C shots for the faster One Cent cut (first used for #189, 2026-11-26, after shibboleth's note that every
 * film needs much more frequent image changes). Each is a picture made from data or from a source, never a fake
 * photograph: words as they are spoken, a grade scale, a typeset plate, a quote on black, a scroll of a trait's
 * whole pool, a dot field of all 10,000 Cents, a fast back-and-forth between two Cents, and an Atlas ladder.
 * They share StoryOpen's palette and type, so the film stays in one look.
 */

type Anchored = { alignment: Alignment; shotStartFrame: number };
type Box = [number, number, number, number];
const L = LOOK_C;
const BRIGHT = "#d9925c";   // copper as a light (dots, rings); text never sits on it
const fraunces = (soft: number, opsz = 144): React.CSSProperties =>
  ({ fontFamily: L.display, fontVariationSettings: `"opsz" ${opsz}, "SOFT" ${soft}, "WONK" 0` });
const caps = (size = 42, color: string = L.dim, spacing = "0.12em"): React.CSSProperties =>
  ({ fontFamily: L.mono, fontWeight: 500, fontSize: size, letterSpacing: spacing, textTransform: "uppercase", color });

const Chip: React.FC<{ children: string; size?: number }> = ({ children, size = 42 }) => (
  <div style={{ display: "inline-block", background: L.hi, padding: "10px 22px" }}>
    <SafeText role="label" fontSize={size} maxLines={1} color={L.ink}
              style={{ fontFamily: L.mono, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", lineHeight: 1.2 }}>{children}</SafeText>
  </div>
);

function useAt({ alignment, shotStartFrame }: Anchored, who: string) {
  const { fps } = useVideoConfig();
  return (phrase: string, plus = 0) => {
    const f = Math.round((findPhrase(alignment, phrase).start + plus) * fps) - shotStartFrame;
    if (f < 0) throw new Error(`${who}: "${phrase}" is spoken before this shot starts`);
    return f;
  };
}
const rampAt = (frame: number, from: number, len: number) =>
  interpolate(frame, [from, from + len], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });

/** A Cent photo (cents.vision, coin = 0.815 of the frame) drawn as a disc `d` across. */
const Disc: React.FC<{ src: string; d: number; style?: React.CSSProperties }> = ({ src, d, style }) => {
  const S = d / 0.815;
  return (
    <div style={{ position: "relative", width: d, height: d, borderRadius: "50%", overflow: "hidden", ...style }}>
      <Img src={staticFile(src)} style={{ position: "absolute", left: d / 2 - S / 2, top: d / 2 - S / 2, width: S, height: S,
                                          clipPath: "circle(40.5% at 50% 50%)" }} />
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/** Words set as they are spoken, stacking down the frame: the newest at full ink, the earlier ones dimmed. */
export const StoryWords: React.FC<Anchored & { words: { at_phrase: string; text: string }[]; kicker?: string }> = (props) => {
  const { words, kicker } = props;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useShotFade();
  const at = useAt(props, "StoryWords");
  const fs = words.map((w) => at(w.at_phrase));
  for (let i = 1; i < fs.length; i++) if (fs[i]! < fs[i - 1]!) throw new Error(`StoryWords: "${words[i]!.text}" comes before the word above it`);
  const gap = 210, y0 = 960 - ((words.length - 1) * gap) / 2;
  const cur = fs.filter((f) => frame >= f).length - 1;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      {kicker ? (
        <div style={{ position: "absolute", left: 104, width: 732, top: 330, textAlign: "center" }}>
          <SafeText role="label" fontSize={42} maxLines={1} style={caps(42, L.dim)}>{kicker}</SafeText>
        </div>
      ) : null}
      {words.map((w, i) => {
        if (frame < fs[i]!) return null;
        const pop = spring({ frame: frame - fs[i]!, fps, config: { damping: 11, stiffness: 170, mass: 0.6 } });
        return (
          <div key={i} style={{ position: "absolute", left: 104, width: 732, top: y0 + i * gap - 80, textAlign: "center",
                                opacity: i === cur ? 1 : 0.4, transform: `scale(${0.6 + 0.4 * pop})` }}>
            <SafeText role="display" fontSize={136} maxLines={1} color={L.ink}
                      style={{ ...fraunces(100), fontWeight: 650, lineHeight: 1.1, letterSpacing: "0.01em" }}>{w.text}</SafeText>
          </div>
        );
      })}
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/**
 * A coin-grade scale, upright: 1 at the foot, 70 at the head, with the grading terms of the source beside their
 * numbers. A copper marker climbs it on phrases. The numbers and terms are the source's (Littleton's grading terms
 * sheet), and the scale says nothing about any Cent.
 */
export const StoryScale: React.FC<Anchored & {
  kicker: string; ticks: { v: number; label: string }[]; stops: { at_phrase: string; to: number; dur?: number }[]; source: string;
}> = (props) => {
  const { kicker, ticks, stops, source } = props;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useShotFade();
  const at = useAt(props, "StoryScale");
  const Y1 = 1240, Y70 = 520, X = 300;
  const y = (v: number) => Y1 + ((v - 1) / 69) * (Y70 - Y1);
  let v = 1;
  for (const s of stops) {
    if (s.to < 1 || s.to > 70) throw new Error(`StoryScale: stop ${s.to} is off the 1-70 scale`);
    const f0 = at(s.at_phrase);
    v = v + (s.to - v) * rampAt(frame, f0, Math.round((s.dur ?? 1.2) * fps));
  }
  for (let i = 1; i < ticks.length; i++)
    if (Math.abs(y(ticks[i]!.v) - y(ticks[i - 1]!.v)) < 60) throw new Error(`StoryScale: labels ${ticks[i - 1]!.v} and ${ticks[i]!.v} would overlap`);
  const near = (t: number) => Math.max(0, 1 - Math.abs(v - t) / 6);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <div style={{ position: "absolute", left: 104, width: 732, top: 330, textAlign: "center" }}>
        <SafeText role="label" fontSize={42} maxLines={1} style={caps(42, L.ink)}>{kicker}</SafeText>
        <div style={{ width: 120, height: 6, background: L.hi, margin: "22px auto 0" }} />
      </div>
      <Imagery>
        <svg width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0 }}>
          <line x1={X} x2={X} y1={Y1} y2={Y70} stroke={L.dim} strokeWidth={6} strokeLinecap="round" />
          <line x1={X} x2={X} y1={Y1} y2={y(v)} stroke={BRIGHT} strokeWidth={14} strokeLinecap="round" />
          {ticks.map((t) => <line key={t.v} x1={X - 26} x2={X + 26} y1={y(t.v)} y2={y(t.v)} stroke={L.ink} strokeOpacity={0.7} strokeWidth={4} />)}
          <circle cx={X} cy={y(v)} r={30} fill={BRIGHT} stroke={L.ink} strokeWidth={5} />
        </svg>
      </Imagery>
      {ticks.map((t) => (
        <div key={t.v} style={{ position: "absolute", left: X - 200, width: 150, top: y(t.v) - 30, textAlign: "right" }}>
          <SafeText role="label" fontSize={48} maxLines={1} color={L.ink}
                    style={{ fontFamily: L.mono, fontWeight: 600, opacity: 0.55 + 0.45 * near(t.v) }}>{String(t.v)}</SafeText>
        </div>
      ))}
      {ticks.map((t) => (
        <div key={`l${t.v}`} style={{ position: "absolute", left: X + 60, width: 836 - X - 60, top: y(t.v) - 32 }}>
          <SafeText role="body" fontSize={48} maxLines={1} color={L.ink}
                    style={{ ...fraunces(50, 48), fontStyle: "italic", opacity: 0.45 + 0.55 * near(t.v) }}>{t.label}</SafeText>
        </div>
      ))}
      <div style={{ position: "absolute", left: 104, width: 732, top: 1330, textAlign: "center" }}>
        <SafeText role="label" fontSize={42} maxLines={2} style={caps(42, L.dim, "0.06em")}>{source}</SafeText>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/** A typeset plate: a copper chip, a title, lines that may arrive on phrases, and optional two-column rows. */
type TLine = { text: string; at_phrase?: string; look?: "sub" | "note" | "quote" };
export const StoryText: React.FC<Anchored & {
  chip?: string; title: string; titleSize?: number; italic?: boolean; lines?: TLine[]; rows?: [string, string][]; rows_at?: string; rows_head?: [string, string]; rows_top?: number;
}> = (props) => {
  const { chip, title, titleSize = 120, italic, lines = [], rows, rows_at, rows_head, rows_top = 760 } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props, "StoryText");
  const tIn = rampAt(frame, 0, 12);
  const r0 = rows_at ? at(rows_at) : 4;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <div style={{ position: "absolute", left: 104, width: 732, top: rows ? 330 : 520, textAlign: "center",
                    opacity: tIn, transform: `translateY(${(1 - tIn) * 16}px)` }}>
        {chip ? <div style={{ display: "flex", justifyContent: "center", marginBottom: 28 }}><Chip>{chip}</Chip></div> : null}
        <SafeText role="display" fontSize={titleSize} maxLines={2} color={L.ink}
                  style={{ ...fraunces(italic ? 50 : 100, 144), fontStyle: italic ? "italic" : "normal", fontWeight: italic ? 400 : 600, lineHeight: 1.05 }}>{title}</SafeText>
        <div style={{ width: 120, height: 6, background: L.hi, margin: "30px auto 26px" }} />
        {lines.map((l, i) => {
          const o = l.at_phrase ? rampAt(frame, at(l.at_phrase), 8) : 1;
          const look = l.look ?? "sub";
          return (
            <div key={i} style={{ opacity: o, transform: `translateY(${(1 - o) * 10}px)`, marginTop: i ? 18 : 0 }}>
              {look === "note" ? <SafeText role="label" fontSize={42} maxLines={2} style={caps(42, L.dim, "0.08em")}>{l.text}</SafeText>
                : <SafeText role="body" fontSize={look === "quote" ? 50 : 58} maxLines={3} color={look === "quote" ? L.dim : L.ink}
                            style={{ ...fraunces(0, 48), fontStyle: "italic", fontWeight: 400, lineHeight: 1.2 }}>{l.text}</SafeText>}
            </div>
          );
        })}
      </div>
      {rows ? (
        <div style={{ position: "absolute", left: 104, width: 732, top: rows_top }}>
          {rows_head ? (
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 14 }}>
              <SafeText role="label" fontSize={42} maxLines={1} style={caps(42, L.dim)}>{rows_head[0]}</SafeText>
              <SafeText role="label" fontSize={42} maxLines={1} style={caps(42, L.dim)}>{rows_head[1]}</SafeText>
            </div>
          ) : null}
          {rows.map(([a, b], i) => {
            const o = interpolate(frame, [r0 + i * 1.5, r0 + i * 1.5 + 4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return (
              <div key={i} style={{ display: "flex", justifyContent: "space-between", opacity: o, borderTop: `2px solid rgba(147,135,127,0.35)`, padding: "6px 0" }}>
                <SafeText role="label" fontSize={42} maxLines={1} color={L.ink} style={{ fontFamily: L.mono, fontWeight: 500 }}>{a}</SafeText>
                <SafeText role="label" fontSize={42} maxLines={1} color={L.dim} style={{ fontFamily: L.mono, fontWeight: 500 }}>{b}</SafeText>
              </div>
            );
          })}
        </div>
      ) : null}
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/** A quote alone on black, each word lit as it is spoken; the speaker in caps and the source in italic below. */
export const StoryQuote: React.FC<Anchored & { quote: { at_phrase: string; text: string; spoken?: Record<string, string> }; who: string; where: string; size?: number }> = (props) => {
  const { quote, who, where, size = 84 } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const spoken = useSpokenWords(props, quote);
  const tIn = rampAt(frame, 2, 12);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <div style={{ position: "absolute", left: 104, width: 732, top: 560, opacity: tIn, transform: `translateY(${(1 - tIn) * 20}px)`,
                    borderLeft: `8px solid ${L.hi}`, paddingLeft: 44, boxSizing: "border-box" }}>
        <SafeText role="display" fontSize={size} maxLines={6} color={L.ink}
                  style={{ ...fraunces(50, 72), fontStyle: "italic", fontWeight: 400, lineHeight: 1.16, textWrap: "pretty" }}
                  wordOpacity={spoken.map((f) => (frame >= f ? 1 : 0.32))}>{`“${quote.text}”`}</SafeText>
        <div style={{ marginTop: 48 }}>
          <SafeText role="label" fontSize={42} maxLines={1} style={caps(42, L.ink)}>{who}</SafeText>
          <SafeText role="body" fontSize={46} maxLines={3} color={L.dim}
                    style={{ ...fraunces(0, 36), fontStyle: "italic", fontWeight: 400, marginTop: 8, lineHeight: 1.2 }}>{where}</SafeText>
        </div>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/**
 * A trait's (or a year's) whole pool, scrolling up fast in rows of `cols`, every Cent large enough to see. The
 * list is shown in full: `count`, when given, must equal the list. With `mark`, the scroll settles on the last
 * row before `until`, the others dim and the marked Cent is ringed outside its rim (the #8820 spotlight).
 */
export const StoryScroll: React.FC<Anchored & {
  ns: number[]; dir: string; label: string; count?: string; cols?: number; mark?: number; until: string;
}> = (props) => {
  const { ns, dir, label, count, cols = 6, mark, until } = props;
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const fade = useShotFade();
  const at = useAt(props, "StoryScroll");
  if (new Set(ns).size !== ns.length) throw new Error("StoryScroll: a Cent is listed twice");
  if (count !== undefined && count !== ns.length.toLocaleString("en-US")) throw new Error(`StoryScroll: count ${count} is not the ${ns.length} listed`);
  if (mark !== undefined && ns[ns.length - 1] !== mark) throw new Error("StoryScroll: the marked Cent goes last, where the scroll settles");
  const W = 732, cell = W / cols, d = cell - 14, TOPY = 470, VIEW = 1300 - TOPY;
  const rows = Math.ceil(ns.length / cols), H = rows * cell;
  const end = Math.min(durationInFrames, at(until)) - (mark !== undefined ? Math.round(0.8 * fps) : 0);
  const travel = Math.max(0, H - VIEW);
  const p = interpolate(frame, [4, Math.max(5, end)], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });
  const off = -travel * p;
  const spot = mark !== undefined ? rampAt(frame, end, 10) : 0;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <div style={{ position: "absolute", left: 104, width: 732, top: 300, textAlign: "center" }}>
        {count ? <SafeText role="display" fontSize={84} maxLines={1} color={L.ink} style={{ ...fraunces(100), fontWeight: 600, lineHeight: 1 }}>{count}</SafeText> : null}
        <div style={{ display: "flex", justifyContent: "center", marginTop: count ? 14 : 40 }}><Chip>{label}</Chip></div>
      </div>
      <Imagery>
        <div style={{ position: "absolute", left: 104, top: TOPY, width: W, height: VIEW, overflow: "hidden",
                      maskImage: "linear-gradient(to bottom, transparent 0, black 40px, black calc(100% - 40px), transparent 100%)" }}>
          {ns.map((n, i) => {
            const x = (i % cols) * cell + 7, y = Math.floor(i / cols) * cell + 7 + off;
            if (y < -cell || y > VIEW) return null;
            const isMark = n === mark;
            return (
              <div key={n} style={{ position: "absolute", left: x, top: y, opacity: isMark ? 1 : 1 - 0.72 * spot }}>
                <Disc src={`${dir}/${n}.webp`} d={d} />
                {isMark && spot > 0 ? (
                  <div style={{ position: "absolute", left: -9, top: -9, width: d + 18, height: d + 18, borderRadius: "50%",
                                border: `6px solid ${L.ink}`, opacity: spot, boxSizing: "border-box" }} />
                ) : null}
              </div>
            );
          })}
        </div>
      </Imagery>
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/** All 10,000 Cents as a 100 x 100 field of squares in number order, a pool lit in copper and one Cent ringed. */
export const StoryDots: React.FC<Anchored & { lit: number[]; mark: number; count: string; label: string; total?: number }> = (props) => {
  const { lit, mark, count, label, total = 10000 } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  if (count !== lit.length.toLocaleString("en-US")) throw new Error(`StoryDots: count ${count} is not the ${lit.length} lit`);
  if (!lit.includes(mark)) throw new Error("StoryDots: the ringed Cent is not in the lit pool");
  const N = 100, W = 732, c = W / N, X0 = 104, Y0 = 640;
  const pos = (n: number) => ({ x: X0 + ((n - 1) % N) * c, y: Y0 + Math.floor((n - 1) / N) * c });
  const sorted = [...lit].sort((a, b) => a - b);
  const m = pos(mark);
  const ring = rampAt(frame, 22, 10);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <div style={{ position: "absolute", left: 104, width: 732, top: 330, textAlign: "center" }}>
        <SafeText role="display" fontSize={150} maxLines={1} color={L.ink} style={{ ...fraunces(100), fontWeight: 600, lineHeight: 1 }}>{count}</SafeText>
        <div style={{ display: "flex", justifyContent: "center", marginTop: 18 }}><Chip>{label}</Chip></div>
      </div>
      <Imagery>
        <svg width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0 }}>
          <rect x={X0} y={Y0} width={W} height={c * Math.ceil(total / N)} fill="#241d1a" />
          {sorted.map((n, i) => {
            const p = pos(n), o = interpolate(frame, [2 + i * 0.2, 6 + i * 0.2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return <rect key={n} x={p.x - 1.5} y={p.y - 1.5} width={c + 3} height={c + 3} fill={BRIGHT} opacity={o} />;
          })}
          {ring > 0 ? <circle cx={m.x + c / 2} cy={m.y + c / 2} r={30 - 8 * ring} fill="none" stroke={L.ink} strokeWidth={5} opacity={ring} /> : null}
        </svg>
      </Imagery>
      <div style={{ position: "absolute", left: 104, width: 732, top: Y0 + W + 30, textAlign: "center" }}>
        <SafeText role="label" fontSize={42} maxLines={1} style={caps(42, L.dim)}>{`All ${total.toLocaleString("en-US")} Cents`}</SafeText>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/**
 * The fast back-and-forth (shibboleth, 2026-11-26: "go back and forth between the two with a higher frequency").
 * Two Cents at the same size and place swap every `period` seconds with a few-frame dissolve, the name and the
 * inscription line swapping with the coin, so the name on screen always belongs to the coin on screen. The camera
 * moves on both coins at once (the same box on both photos). After `settle` it stays on `a`.
 */
type Face = { n: number; inscription: number; front: string; chip?: string };
export const StoryFlip: React.FC<Anchored & {
  a: Face; b: Face; period?: number; settle: string; moves?: { at_phrase: string; box: Box | null; dur?: number }[]; chips_at?: string;
}> = (props) => {
  const { a, b, period = 0.6, settle, moves = [], chips_at } = props;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useShotFade();
  const at = useAt(props, "StoryFlip");
  const P = Math.round(period * fps), X = 3;
  const fs = at(settle);
  const nSwaps = Math.floor(fs / P);
  if (nSwaps < 6) throw new Error(`StoryFlip: only ${nSwaps} swaps before "${settle}"; the brief asks for at least six`);
  // b on odd periods, a on even ones; each swap dissolves over X frames from the period boundary. From the first
  // even boundary at or after `settle` on, a stays.
  const kEnd = (() => { const k = Math.ceil(fs / P); return k % 2 ? k + 1 : k; })();
  const side = (k: number) => (k >= kEnd ? 0 : k % 2);
  const kNow = Math.floor(frame / P), into = frame - kNow * P;
  const prevSide = kNow > 0 ? side(kNow - 1) : side(0);
  const wB = prevSide + (side(kNow) - prevSide) * interpolate(into, [0, X], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const D = 520, CX = 540, CY = 760, S0 = D / 0.815;
  let cam = { cx: 0.5, cy: 0.5, k: 1 };
  for (const m of moves) {
    const t = rampAt(frame, at(m.at_phrase), Math.round((m.dur ?? 0.6) * fps));
    if (t <= 0) break;
    let to = { cx: 0.5, cy: 0.5, k: 1 };
    if (m.box) {
      const [x0, y0, x1, y1] = m.box;
      if (!(0 <= x0 && x0 < x1 && x1 <= 1 && 0 <= y0 && y0 < y1 && y1 <= 1)) throw new Error(`StoryFlip: box ${m.box} is not inside the image`);
      to = { cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, k: Math.min((0.78 * D) / Math.hypot((x1 - x0) * S0, (y1 - y0) * S0), 3.2) };
    }
    cam = { cx: cam.cx + (to.cx - cam.cx) * t, cy: cam.cy + (to.cy - cam.cy) * t, k: cam.k + (to.k - cam.k) * t };
  }
  const S = S0 * cam.k, ox = D / 2 - cam.cx * S, oy = D / 2 - cam.cy * S;
  const rim = Math.min(1, Math.max(0, (cam.k - 1) / 0.4));
  const chipsOn = chips_at ? frame >= at(chips_at) : false;
  const face = (c: Face, o: number) => o <= 0.002 ? null : (
    <div key={c.n} style={{ position: "absolute", left: CX - D / 2, top: CY - D / 2, width: D, height: D, borderRadius: "50%", overflow: "hidden", opacity: o }}>
      <Img src={staticFile(c.front)} style={{ position: "absolute", left: ox, top: oy, width: S, height: S, clipPath: "circle(40.5% at 50% 50%)" }} />
    </div>
  );
  const textFace = wB >= 0.5 ? b : a;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <Imagery>
        {face(a, 1 - wB)}
        {face(b, wB)}
        {rim > 0 ? (
          <div style={{ position: "absolute", left: CX - D / 2 - 9, top: CY - D / 2 - 9, width: D + 18, height: D + 18,
                        borderRadius: "50%", border: `9px solid ${L.hi}`, opacity: rim, boxSizing: "border-box" }} />
        ) : null}
      </Imagery>
      <div style={{ position: "absolute", left: 104, width: 732, top: 1062, textAlign: "center" }}>
        <SafeText role="display" fontSize={140} maxLines={1} color={L.ink} style={{ ...fraunces(100), fontWeight: 600, lineHeight: 1 }}>{`Cent #${textFace.n}`}</SafeText>
        <div style={{ width: 120, height: 6, background: L.hi, margin: "26px auto 22px" }} />
        <div style={{ height: 72 }}>
          {chipsOn && textFace.chip ? <Chip>{textFace.chip}</Chip>
            : <SafeText role="label" fontSize={42} maxLines={1} style={caps(42, L.dim)}>{`Inscription ${textFace.inscription}`}</SafeText>}
        </div>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/** The Atlas's own three examples of a trait's scale (notable, significant, full), lighting row by row. */
export const StoryLadder: React.FC<Anchored & {
  title: string; rows: { n: number; front: string; level: string; range: string; at_phrase?: string; plus?: number; lit?: boolean }[]; credit: string;
}> = (props) => {
  const { title, rows, credit } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props, "StoryLadder");
  const d = 250, ys = [470, 770, 1070];
  if (rows.length !== 3) throw new Error("StoryLadder: the Atlas scale has three levels");
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <div style={{ position: "absolute", left: 104, width: 732, top: 320, textAlign: "center" }}>
        <SafeText role="label" fontSize={42} maxLines={1} style={caps(42, L.ink)}>{title}</SafeText>
      </div>
      {rows.map((r, i) => {
        const f0 = r.at_phrase ? at(r.at_phrase, r.plus ?? 0) : i * 8;
        const o = r.lit === false ? 0.25 : 0.25 + 0.75 * rampAt(frame, f0, 8);
        return (
          <div key={r.n} style={{ position: "absolute", left: 120, top: ys[i], width: 716, height: d, display: "flex", alignItems: "center", gap: 40, opacity: o }}>
            <Imagery><Disc src={r.front} d={d} /></Imagery>
            <div style={{ flex: 1 }}>
              <SafeText role="display" fontSize={72} maxLines={1} color={L.ink} style={{ ...fraunces(100, 72), fontWeight: 600, lineHeight: 1.05 }}>{r.level}</SafeText>
              <SafeText role="body" fontSize={46} maxLines={3} color={L.ink} style={{ ...fraunces(0, 48), fontStyle: "italic", lineHeight: 1.12, marginTop: 6 }}>{r.range}</SafeText>
              <SafeText role="label" fontSize={42} maxLines={1} style={{ ...caps(42, L.dim), marginTop: 8 }}>{`Cent #${r.n}`}</SafeText>
            </div>
          </div>
        );
      })}
      <div style={{ position: "absolute", left: 104, width: 732, top: 1380, textAlign: "center" }}>
        <SafeText role="label" fontSize={42} maxLines={2} style={caps(42, L.dim, "0.06em")}>{credit}</SafeText>
      </div>
    </div>
  );
};

export const STORYKIT = { StoryWords, StoryScale, StoryText, StoryQuote, StoryScroll, StoryDots, StoryFlip, StoryLadder } as const;
for (const C of Object.values(STORYKIT)) (C as any).wantsAlignment = true;
