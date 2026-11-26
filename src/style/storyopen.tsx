import React from "react";
import { Easing, Freeze, Img, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { EASE, useShotFade } from "./motion";
import { Imagery, SafeText } from "./Safe";
import { findPhrase, type Alignment } from "../lib/timeline";
import { useSpokenWords } from "./onecent";
import { loadFonts } from "./fonts";

loadFonts();

/**
 * The One Cent opening in Look C (series-look work, PR #25, v3.1; shibboleth called it "quite good",
 * 28 Oct 2026), first used for #1867 so that viewers who know the series see a new episode from frame 0.
 *
 * Frame 0 is the cover: the Cent dimmed under a copper play button marked CENTS STORY TIME, its name set
 * below it in Fraunces ("title below", arrangement 1 of the look work). The button is pressed (~0.5 s), a
 * ripple leaves it, and the Cent makes one 3DCENTS turn. The turn hands over to the 1050 px photo at the
 * same size, and the camera then looks inside the coin's outline, which becomes a lens with a copper rim.
 * Reads replace the inscription line as copper chips.
 *
 * Copper #824C3D is cents.gallery's; on black it is 2.9:1, too dark for text, so it is only ever a FILL
 * behind light text, a rule or a rim (look v3 notes).
 */

type Anchored = { alignment: Alignment; shotStartFrame: number };
type Box = [number, number, number, number];
type Clip = { src: string; width: number; height: number; frames: number; coin: { cx: number; cy: number; d: number }; credit: string; credit_at_end?: boolean };
type Move = { at_phrase: string; plus?: number; dur?: number; box: Box | null; mark?: boolean; max?: number; zoom?: number };
type Read = { at_phrase: string; chip: string };

export const LOOK_C = {
  bg: "#0b0908", ink: "#f3ece6", dim: "#93877f", hi: "#824C3D",
  display: "Fraunces", sans: "IBM Plex Sans", mono: "IBM Plex Mono",
} as const;
const L = LOOK_C;
const fraunces = (soft: number, opsz = 144): React.CSSProperties =>
  ({ fontFamily: L.display, fontVariationSettings: `"opsz" ${opsz}, "SOFT" ${soft}, "WONK" 0` });
const caps = (size = 42, color: string = L.dim, spacing = "0.12em"): React.CSSProperties =>
  ({ fontFamily: L.mono, fontWeight: 500, fontSize: size, letterSpacing: spacing, textTransform: "uppercase", color });

const CX = 540, CY = 760, D = 520;      // the coin on the title card ("title below")
const S0 = D / 0.815;                   // photo size at which its coin is D across (coin = 0.815 of the 1050 px photo)
const PRESS_END = 34;                   // the Cent starts to turn once play is pressed

/** Copper chip: light text on the copper fill, as on cents.gallery. */
const Chip: React.FC<{ children: string; size?: number }> = ({ children, size = 42 }) => (
  <div style={{ display: "inline-block", background: L.hi, padding: "10px 22px" }}>
    <SafeText role="label" fontSize={size} maxLines={1} color={L.ink}
              style={{ fontFamily: L.mono, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", lineHeight: 1.2 }}>{children}</SafeText>
  </div>
);

/** The cover: the Cent dimmed under a copper play button and CENTS STORY TIME. At rest on frame 0;
 *  pressed at ~0.5 s; gone by ~1.3 s. Ported from src/lab/Looks.tsx (PlayPoster). */
const PlayPoster: React.FC = () => {
  const f = useCurrentFrame();
  if (f >= 42) return null;
  const press = interpolate(f, [12, 17, 24], [1, 0.8, 1.06], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const out = interpolate(f, [27, 40], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.quad) });
  const grow = interpolate(f, [27, 40], [1, 1.2], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const ripple = interpolate(f, [17, 34], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const down = f >= 12 && f < 22;
  const B = 150;
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <Imagery>
        <div style={{ position: "absolute", left: CX - D / 2, top: CY - D / 2, width: D, height: D, borderRadius: "50%",
                      background: "rgba(0,0,0,0.5)", opacity: out }} />
        <svg width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0 }}>
          {ripple > 0 && ripple < 1 ? (
            <circle cx={CX} cy={CY - 30} r={B / 2 + 110 * ripple} fill="none" stroke={L.ink} strokeWidth={6} opacity={0.9 * (1 - ripple)} />
          ) : null}
          <g transform={`translate(${CX} ${CY - 30}) scale(${press * grow})`} opacity={out}>
            <circle r={B / 2} fill={L.hi} style={{ filter: down ? "brightness(0.7)" : "none" }} />
            <circle r={B / 2} fill="none" stroke={L.ink} strokeOpacity={0.85} strokeWidth={4} />
            <path d={`M${-B * 0.13} ${-B * 0.2} L${B * 0.22} 0 L${-B * 0.13} ${B * 0.2} Z`} fill={L.ink} />
          </g>
        </svg>
      </Imagery>
      <div style={{ position: "absolute", left: CX - D / 2, width: D, top: CY + 70, opacity: out, textAlign: "center" }}>
        <SafeText role="label" fontSize={42} maxLines={1} color={L.ink}
                  style={{ fontFamily: L.mono, fontWeight: 600, letterSpacing: "0.06em", textShadow: "0 2px 10px rgba(0,0,0,0.9)" }}>CENTS STORY TIME</SafeText>
      </div>
    </div>
  );
};

/**
 * A playful die-cut sticker for the opening (shibboleth, 2026-11-25: "a kind of emoji or sticker thing ... like
 * one might see on tiktok ... something playful"). Drawn here, not an emoji font, so it looks the same on every
 * machine (the fonts.ts rule). Cartoon eyes and a short line on a cream sticker with a white die-cut edge. It pops
 * on once play is pressed, the eyes glance down at the coin and blink, it bobs while the Cent turns, and it pops
 * off just before the camera moves in, so "look closer" is answered by the camera.
 */
const Eyes: React.FC<{ f: number }> = ({ f }) => {
  // pupils: at the viewer, then down and to the right at the coin, then back up
  const gx = interpolate(f, [14, 22, 92, 100], [0, 7, 7, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const gy = interpolate(f, [14, 22, 92, 100], [0, 9, 9, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const lid = f >= 58 && f < 64 ? 0.12 : 1;   // one blink
  const eye = (cx: number) => (
    <g transform={`translate(${cx} 34) scale(1 ${lid}) translate(${-cx} -34)`}>
      <ellipse cx={cx} cy={34} rx={20} ry={27} fill="#ffffff" stroke={L.bg} strokeWidth={5} />
      <circle cx={cx + gx} cy={36 + gy} r={10} fill={L.bg} />
      <circle cx={cx + gx + 4} cy={32 + gy} r={3.4} fill="#ffffff" />
    </g>
  );
  return <svg width={128} height={93} viewBox="0 0 96 70" style={{ display: "block" }}>{eye(25)}{eye(71)}</svg>;
};

const Sticker: React.FC<{ text: string; from: number; to: number }> = ({ text, from, to }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (frame < from || frame >= to) return null;
  const f = frame - from;
  const pop = spring({ frame: f, fps, config: { damping: 9, stiffness: 160, mass: 0.7 } });
  const off = interpolate(frame, [to - 9, to], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.back(2)) });
  const k = 0.04 + 0.96 * pop * off;   // never 0: the safe-area gate measures every frame
  const rot = -7 + (1 - pop) * -16 + Math.sin(f / 11) * 1.6 + (1 - off) * 25;
  const bob = Math.sin(f / 9) * 4;
  // little copper sparks that fly out as it lands
  const spark = interpolate(f, [2, 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return (
    <div style={{ position: "absolute", left: 470 - 330, width: 660, top: 336 + bob, display: "flex", justifyContent: "center",
                  transform: `rotate(${rot}deg) scale(${k})`, transformOrigin: "50% 60%" }}>
      {spark > 0 && spark < 1 ? (
        <Imagery>
          <svg width={720} height={300} style={{ position: "absolute", left: -30, top: -70, overflow: "visible" }}>
            {[[-1, -0.6], [-0.9, 0.5], [1, -0.7], [0.95, 0.45], [0.1, -1]].map(([dx, dy], i) => {
              const x = 360 + dx! * (250 + 100 * spark), y = 150 + dy! * (85 + 60 * spark);
              return <path key={i} transform={`translate(${x} ${y}) scale(${2.2 * (1 - spark)})`}
                           d="M0 -16 L4 -4 L16 0 L4 4 L0 16 L-4 4 L-16 0 L-4 -4 Z" fill={i % 2 ? L.ink : L.hi} />;
            })}
          </svg>
        </Imagery>
      ) : null}
      <div style={{ display: "flex", alignItems: "center", gap: 14, padding: "14px 38px 18px 24px", borderRadius: 999,
                    background: L.ink, border: "11px solid #ffffff",
                    boxShadow: "0 10px 24px rgba(0,0,0,0.55), 0 2px 0 rgba(0,0,0,0.25)" }}>
        <Eyes f={f} />
        <SafeText role="label" fontSize={72} maxLines={2} color={L.bg}
                  style={{ ...fraunces(100, 72), fontVariationSettings: '"opsz" 72, "SOFT" 100, "WONK" 1', fontStyle: "italic",
                           fontWeight: 700, lineHeight: 1.1, whiteSpace: "nowrap" }}>{text}</SafeText>
      </div>
    </div>
  );
};

/**
 * `mode` (added for #1867 v1, so the whole film stays in Look C):
 *  - "open" (default): the cover, the play button, the sticker, one turn, then the lens.
 *  - "lens": the same card later in the film, already settled on the photo; no cover, no turn, no sticker.
 *    The camera may move from the first frame. A move with no box may set `zoom` (a slow push-in).
 *  - "close": the closing card; one turn from the first frame, no cover and no sticker, then the photo.
 */
export const StoryOpen: React.FC<Anchored & {
  n: number; inscription: number; front: string; spin?: Clip; moves?: Move[]; reads?: Read[]; sticker?: string;
  mode?: "open" | "lens" | "close";
}> = (props) => {
  const { n, inscription, front, spin, moves = [], reads = [], sticker, mode = "open", alignment, shotStartFrame } = props;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useShotFade();
  const at = (phrase: string) => {
    const f = Math.round(findPhrase(alignment, phrase).start * fps) - shotStartFrame;
    if (f < 0) throw new Error(`"${phrase}" is spoken before this shot starts`);
    return f;
  };
  if (mode !== "lens" && !spin) throw new Error(`StoryOpen #${n}: mode "${mode}" turns the coin and needs a 3DCENTS clip`);
  if (spin && !spin.credit) throw new Error(`StoryOpen #${n}: a 3DCENTS clip must carry its credit`);
  if (mode !== "open" && sticker) throw new Error(`StoryOpen #${n}: the sticker belongs to the opening only`);
  if (mode === "close" && moves.length) throw new Error(`StoryOpen #${n}: the closing card does not move the camera`);
  const press = mode === "open" ? PRESS_END : 0;
  const turned = mode === "lens" ? 0 : press + spin!.frames;
  if (moves.length && at(moves[0]!.at_phrase) < turned)
    throw new Error(`StoryOpen #${n}: the camera moves before the turn has settled on the front (frame ${turned})`);
  if (reads.length && at(reads[0]!.at_phrase) < press)
    throw new Error(`StoryOpen #${n}: a read arrives while the play button is still up`);
  for (const m of moves) {
    if (!m.box) continue;
    const [x0, y0, x1, y1] = m.box;
    if (!(0 <= x0 && x0 < x1 && x1 <= 1 && 0 <= y0 && y0 < y1 && y1 <= 1)) throw new Error(`StoryOpen #${n}: box ${m.box} is not inside the image`);
    if (m.max && m.max > 4.5) throw new Error(`StoryOpen #${n}: ${m.max}x is past what the 1050px photo holds`);
  }

  // Camera inside the lens: the point of the photo at the lens centre, and the scale.
  const ramp = (from: number, len: number) =>
    interpolate(frame, [from, from + len], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });
  const state = (b: Box | null, max = 3.2, zoom = 1) => {
    if (!b) return { cx: 0.5, cy: 0.5, k: zoom };
    const [x0, y0, x1, y1] = b;
    // the box's diagonal must sit inside the round lens, with a margin for the mark
    const diag = Math.hypot((x1 - x0) * S0, (y1 - y0) * S0);
    return { cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, k: Math.min((0.78 * D) / diag, max) };
  };
  let cam = state(null);
  let mark: Box | null = null, markT = 0, prev = -Infinity;
  for (const m of moves) {
    const f0 = at(m.at_phrase) + Math.round((m.plus ?? 0) * fps);
    if (f0 < prev) throw new Error(`StoryOpen #${n}: move "${m.at_phrase}" starts before the move before it`);
    prev = f0;
    const len = Math.max(1, Math.round((m.dur ?? 0.8) * fps));
    const t = ramp(f0, len);
    if (t <= 0) break;
    if (m.zoom !== undefined && (m.box || m.zoom < 1 || m.zoom > 1.5)) throw new Error(`StoryOpen #${n}: zoom is a push-in on the whole coin (no box, 1 to 1.5)`);
    const to = state(m.box, m.max, m.zoom);
    cam = { cx: cam.cx + (to.cx - cam.cx) * t, cy: cam.cy + (to.cy - cam.cy) * t, k: cam.k + (to.k - cam.k) * t };
    mark = m.mark && m.box ? m.box : null;
    markT = mark ? ramp(f0 + len - 4, 10) : 0;
  }
  const S = S0 * cam.k;
  const ox = D / 2 - cam.cx * S, oy = D / 2 - cam.cy * S;
  const settle = mode === "lens" ? 1 : interpolate(frame, [turned - 10, turned], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const rim = Math.min(1, Math.max(0, (cam.k - 1) / 0.4));   // the lens rim shows once the camera is inside the coin

  // The spin: its face-on coin (spin.coin) drawn D across at (CX, CY); black drops onto the stage by lighten.
  const sk = spin ? D / spin.coin.d : 1;
  const spinStyle: React.CSSProperties = spin ? { position: "absolute", width: spin.width * sk, height: spin.height * sk,
    left: CX - spin.coin.cx * sk, top: CY - spin.coin.cy * sk, mixBlendMode: "lighten" } : {};

  let cur: Read | undefined, last: Read | undefined, curFrom = 0;
  for (const r of reads) { const f = at(r.at_phrase); if (frame >= f) { last = cur; cur = r; curFrom = f; } }
  const rT = cur ? ramp(curFrom, 8) : 0;

  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <Imagery>
        {spin && settle < 1 ? (
          <div style={{ position: "absolute", inset: 0, isolation: "isolate", background: L.bg }}>
            {press > 0 ? (
              <Sequence durationInFrames={press} layout="none">
                <Freeze frame={0}><OffthreadVideo src={staticFile(spin.src)} muted style={spinStyle} /></Freeze>
              </Sequence>
            ) : null}
            <Sequence from={press} layout="none">
              <OffthreadVideo src={staticFile(spin.src)} muted style={spinStyle} />
            </Sequence>
          </div>
        ) : null}
        <div style={{ position: "absolute", left: CX - D / 2, top: CY - D / 2, width: D, height: D, borderRadius: "50%",
                      overflow: "hidden", opacity: settle, background: L.bg }}>
          <Img src={staticFile(front)} style={{ position: "absolute", left: ox, top: oy, width: S, height: S,
                                                clipPath: "circle(40.5% at 50% 50%)" }} />
          {mark && markT > 0 ? (
            <div style={{ position: "absolute", left: ox + mark[0] * S - 12, top: oy + mark[1] * S - 12,
                          width: (mark[2] - mark[0]) * S + 24, height: (mark[3] - mark[1]) * S + 24,
                          border: `5px solid ${L.ink}`, borderRadius: 16, opacity: markT,
                          boxShadow: "0 0 0 2px rgba(0,0,0,0.5), inset 0 0 0 2px rgba(0,0,0,0.5)" }} />
          ) : null}
        </div>
        {rim > 0 ? (
          <div style={{ position: "absolute", left: CX - D / 2 - 9, top: CY - D / 2 - 9, width: D + 18, height: D + 18,
                        borderRadius: "50%", border: `9px solid ${L.hi}`, opacity: rim, boxSizing: "border-box" }} />
        ) : null}
      </Imagery>
      {mode === "open" ? <PlayPoster /> : null}
      {sticker ? <Sticker text={sticker} from={PRESS_END + 8} to={turned - 6} /> : null}

      {/* name below the coin, a copper rule, then the inscription line, which the reads replace */}
      <div style={{ position: "absolute", left: 104, width: 732, top: 1062, textAlign: "center" }}>
        <SafeText role="display" fontSize={140} maxLines={1} color={L.ink} style={{ ...fraunces(100), fontWeight: 600, lineHeight: 1 }}>
          {`Cent #${n}`}
        </SafeText>
        <div style={{ width: 120, height: 6, background: L.hi, margin: "26px auto 22px" }} />
        <div style={{ position: "relative", height: 72 }}>
          <div style={{ position: "absolute", inset: 0, opacity: 1 - rT }}>
            {last ? <Chip>{last.chip}</Chip>
                  : <SafeText role="label" fontSize={42} maxLines={1} style={caps(42, L.dim)}>{`Inscription ${inscription}`}</SafeText>}
          </div>
          {cur ? (
            <div style={{ position: "absolute", inset: 0, opacity: rT, transform: `translateY(${(1 - rT) * 12}px)` }}>
              <Chip>{cur.chip}</Chip>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};


/**
 * The concept card and the lit quote cards in Look C, so that the new format runs on from the opening
 * through the concept and both quotes (shibboleth, 2026-11-25: quotes earlier, a new-looking start).
 * The coin is the one the opening ends on. With a concept, it stays where the opening left it and the
 * concept takes the name's place below it. With a quote, it rises and shrinks to the top and the quote
 * is set below in Fraunces italic on a copper rule, each word lit as it is spoken (the card must match
 * the recording word for word, as in CentLook). The credit is the speaker in caps and the source in italic.
 */
type Concept = { at_phrase: string; label: string };
type QuoteC = { at_phrase: string; text: string; who: string; where: string; spoken?: Record<string, string>; size?: number };
const TOP = { cy: 440, d: 260 };
export const StoryCard: React.FC<Anchored & { n: number; front: string; concept?: Concept; quote?: QuoteC; from_top?: boolean }> = (props) => {
  const { n, front, concept, quote, from_top } = props;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useShotFade();
  if (!!concept === !!quote) throw new Error(`StoryCard #${n}: give a concept or a quote, not both or neither`);
  const spoken = useSpokenWords(props, quote ? { at_phrase: quote.at_phrase, text: quote.text, spoken: quote.spoken } : undefined);
  const ramp = (from: number, len: number) =>
    interpolate(frame, [from, from + len], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });
  // the coin: centre and size, eased from where the shot before left it
  const up = quote ? (from_top ? 1 : ramp(0, 18)) : 0;
  const cy = CY + (TOP.cy - CY) * up, d = D + (TOP.d - D) * up;
  const S = d / 0.815;
  const tIn = ramp(quote ? 8 : 0, 14);
  const lit = (i: number) => (frame >= spoken[i]! ? 1 : 0.36);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <Imagery>
        <div style={{ position: "absolute", left: CX - d / 2, top: cy - d / 2, width: d, height: d, borderRadius: "50%", overflow: "hidden" }}>
          <Img src={staticFile(front)} style={{ position: "absolute", left: d / 2 - S / 2, top: d / 2 - S / 2, width: S, height: S,
                                                clipPath: "circle(40.5% at 50% 50%)" }} />
        </div>
      </Imagery>
      {concept ? (
        <div style={{ position: "absolute", left: 104, width: 732, top: 1050, textAlign: "center", opacity: tIn,
                      transform: `translateY(${(1 - tIn) * 16}px)` }}>
          <div style={{ display: "flex", justifyContent: "center", marginBottom: 18 }}><Chip>Concept</Chip></div>
          <SafeText role="display" fontSize={92} maxLines={2} color={L.ink}
                    style={{ ...fraunces(50, 72), fontStyle: "italic", fontWeight: 400, lineHeight: 1.08 }}>{concept.label}</SafeText>
        </div>
      ) : null}
      {quote ? (
        <div style={{ position: "absolute", left: 104, width: 732, top: 640, opacity: tIn, transform: `translateY(${(1 - tIn) * 20}px)`,
                      borderLeft: `8px solid ${L.hi}`, paddingLeft: 40, boxSizing: "border-box" }}>
          <SafeText role="display" fontSize={quote.size ?? 64} maxLines={7} color={L.ink}
                    style={{ ...fraunces(50, 72), fontStyle: "italic", fontWeight: 400, lineHeight: 1.18, textWrap: "pretty" }}
                    wordOpacity={spoken.map((_, i) => lit(i))}>{`\u201c${quote.text}\u201d`}</SafeText>
          <div style={{ marginTop: 40 }}>
            <SafeText role="label" fontSize={42} maxLines={1} style={caps(42, L.ink)}>{quote.who}</SafeText>
            <SafeText role="body" fontSize={46} maxLines={2} color={L.dim}
                      style={{ ...fraunces(0, 36), fontStyle: "italic", fontWeight: 400, marginTop: 6, lineHeight: 1.2 }}>{quote.where}</SafeText>
          </div>
        </div>
      ) : null}
    </div>
  );
};

/**
 * Two Cents in the title card's place, dissolving into each other on phrases (Look C's CentDissolve; first
 * used for #1867 against its template #4421). Each card is a whole state, name and chip with the coin, so the
 * name on screen always belongs to the coin on screen. Cards that share a coin or a name are summed, so a
 * swap between two cards of the same Cent changes only what differs (the chip), with no dip.
 */
type Face = { n: number; inscription: number; front: string; chip?: string };
export const StoryDissolve: React.FC<Anchored & { cards: Record<string, Face>; first: string; swaps: { at_phrase: string; to: string }[] }> = (props) => {
  const { cards, first, swaps, alignment, shotStartFrame } = props;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useShotFade();
  const at = (phrase: string) => {
    const f = Math.round(findPhrase(alignment, phrase).start * fps) - shotStartFrame;
    if (f < 0) throw new Error(`"${phrase}" is spoken before this shot starts`);
    return f;
  };
  const keys = Object.keys(cards);
  if (!cards[first]) throw new Error(`StoryDissolve: no card "${first}"`);
  const w: Record<string, number> = Object.fromEntries(keys.map((k) => [k, k === first ? 1 : 0]));
  let last = first, prev = -Infinity;
  for (const sw of swaps) {
    if (!cards[sw.to]) throw new Error(`StoryDissolve: no card "${sw.to}"`);
    if (sw.to === last) throw new Error(`StoryDissolve: "${sw.at_phrase}" dissolves to the card already shown`);
    const f0 = at(sw.at_phrase);
    if (f0 < prev) throw new Error(`StoryDissolve: "${sw.at_phrase}" comes before the swap before it`);
    prev = f0; last = sw.to;
    const t = interpolate(frame, [f0, f0 + 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });
    for (const k of keys) w[k] = w[k]! * (1 - t) + (k === sw.to ? t : 0);
  }
  // `text`: names and chips do not cross-dissolve (two names over each other read as a smudge); the old one is
  // gone by the middle of the swap and the new one comes up after it. The coins do cross-dissolve.
  const sum = (key: (c: Face) => string, text = false) => {
    const m = new Map<string, number>();
    for (const k of keys) m.set(key(cards[k]!), (m.get(key(cards[k]!)) ?? 0) + w[k]!);
    return [...m.entries()].map(([k, o]) => [k, text ? Math.max(0, Math.min(1, 2 * o - 1)) : o] as [string, number])
      .filter(([, o]) => o > 0.002);
  };
  const S = D / 0.815;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <Imagery>
        {sum((c) => c.front).map(([front, o]) => (
          <div key={front} style={{ position: "absolute", left: CX - D / 2, top: CY - D / 2, width: D, height: D, borderRadius: "50%",
                                    overflow: "hidden", opacity: o }}>
            <Img src={staticFile(front)} style={{ position: "absolute", left: D / 2 - S / 2, top: D / 2 - S / 2, width: S, height: S,
                                                  clipPath: "circle(40.5% at 50% 50%)" }} />
          </div>
        ))}
      </Imagery>
      <div style={{ position: "absolute", left: 104, width: 732, top: 1062, textAlign: "center" }}>
        <div style={{ position: "relative", height: 140 }}>
          {sum((c) => `Cent #${c.n}`, true).map(([name, o]) => (
            <div key={name} style={{ position: "absolute", inset: 0, opacity: o }}>
              <SafeText role="display" fontSize={140} maxLines={1} color={L.ink} style={{ ...fraunces(100), fontWeight: 600, lineHeight: 1 }}>{name}</SafeText>
            </div>
          ))}
        </div>
        <div style={{ width: 120, height: 6, background: L.hi, margin: "26px auto 22px" }} />
        <div style={{ position: "relative", height: 72 }}>
          {sum((c) => c.chip ? `chip:${c.chip}` : `line:Inscription ${c.inscription}`, true).map(([line, o]) => (
            <div key={line} style={{ position: "absolute", inset: 0, opacity: o }}>
              {line.startsWith("chip:") ? <Chip>{line.slice(5)}</Chip>
                : <SafeText role="label" fontSize={42} maxLines={1} style={caps(42, L.dim)}>{line.slice(5)}</SafeText>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

/**
 * Two pictures side by side, each under its half of a two-part quote, lit word by word as it is spoken
 * (first used for #1867: Groys's "the object without an aura" under CENTS Block Copper and "the aura without
 * an object" under the Cent's image). A panel is dim until its half is spoken, so the pairing of picture and
 * words is made by the voice, one half at a time. The credit (speaker in caps, source in italic) sits above.
 */
type Panel = { img: string; shape: "square" | "circle"; zoom?: number; quote: { at_phrase: string; text: string } };
export const StoryPair: React.FC<Anchored & { left: Panel; right: Panel; who: string; where: string }> = (props) => {
  const { left, right, who, where } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const ramp = (from: number, len: number) =>
    interpolate(frame, [from, from + len], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });
  const sl = useSpokenWords(props, { at_phrase: left.quote.at_phrase, text: left.quote.text });
  const sr = useSpokenWords(props, { at_phrase: right.quote.at_phrase, text: right.quote.text });
  if (sl[0]! >= sr[0]!) throw new Error("StoryPair: the left half must be spoken first");
  const P = 340, TOPP = 540, X = [104, 496];
  const tIn = ramp(4, 14);
  const panel = (pn: Panel, i: number, spoken: number[]) => {
    const on = 0.38 + 0.62 * ramp(spoken[0]! - 6, 10);
    const z = pn.zoom ?? 1, W = pn.shape === "circle" ? P / 0.815 : P * z;
    return (
      <React.Fragment key={i}>
        <Imagery>
          <div style={{ position: "absolute", left: X[i], top: TOPP, width: P, height: P, overflow: "hidden", opacity: on * tIn,
                        borderRadius: pn.shape === "circle" ? "50%" : 4 }}>
            <Img src={staticFile(pn.img)} style={{ position: "absolute", left: P / 2 - W / 2, top: P / 2 - W / 2, width: W, height: W,
                                                  objectFit: "cover", ...(pn.shape === "circle" ? { clipPath: "circle(40.5% at 50% 50%)" } : {}) }} />
          </div>
        </Imagery>
        <div style={{ position: "absolute", left: X[i], width: P, top: TOPP + P + 40, opacity: tIn }}>
          <SafeText role="display" fontSize={64} maxLines={4} color={L.ink}
                    style={{ ...fraunces(50, 72), fontStyle: "italic", fontWeight: 400, lineHeight: 1.12, textAlign: "center" }}
                    wordOpacity={spoken.map((f) => (frame >= f ? 1 : 0.36))}>{`“${pn.quote.text}”`}</SafeText>
        </div>
      </React.Fragment>
    );
  };
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <div style={{ position: "absolute", left: 104, width: 732, top: 330, textAlign: "center", opacity: tIn }}>
        <SafeText role="label" fontSize={42} maxLines={1} style={caps(42, L.ink)}>{who}</SafeText>
        <SafeText role="body" fontSize={46} maxLines={1} color={L.dim}
                  style={{ ...fraunces(0, 36), fontStyle: "italic", fontWeight: 400, marginTop: 6, lineHeight: 1.2 }}>{where}</SafeText>
        <div style={{ width: 120, height: 6, background: L.hi, margin: "26px auto 0" }} />
      </div>
      {panel(left, 0, sl)}
      {panel(right, 1, sr)}
    </div>
  );
};

export const STORYOPEN = { StoryOpen, StoryCard, StoryDissolve, StoryPair } as const;
for (const C of [StoryOpen, StoryCard, StoryDissolve, StoryPair]) (C as any).wantsAlignment = true;
