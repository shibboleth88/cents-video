import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { CentGrid, CentImage, CentTurn, MAX_CENT_PX, fitGrid } from "./grids";
import { useEntrance, useShotFade, EASE } from "./motion";
import { COLOR, SAFE, TYPE } from "./tokens";
import { Imagery, SafeText } from "./Safe";
import { findPhrase, type Alignment } from "../lib/timeline";
import poolsJson from "../../films/sets/data/pools.json";

/**
 * Shots for the Sets films. Every coin on screen is a real Cent named by its
 * number (see grids.tsx); nothing here draws a coin.
 *
 * Text goes through SafeText and uses the prop names fidelity.py walks (title,
 * subtitle, caption, readout), so every string a viewer reads is ledgered.
 */

const pools = (poolsJson as unknown as { pools: Record<string, number[]> }).pools;
const pool = (k: string) => {
  const p = pools[k];
  if (!p || p.length === 0) throw new Error(`pool "${k}" is empty or missing`);
  return p;
};

type Anchored = { alignment: Alignment; shotStartFrame: number };

/** Frame within the shot at which a phrase is spoken. Before the shot is an error. */
const useAt = ({ alignment, shotStartFrame }: Anchored) => {
  const { fps } = useVideoConfig();
  return (phrase: string) => {
    const f = Math.round(findPhrase(alignment, phrase).start * fps) - shotStartFrame;
    if (f < 0) throw new Error(`"${phrase}" is spoken before this shot starts`);
    return f;
  };
};

/** The working area for coins: the essential box, under a title band and above a readout band. */
const E = SAFE.essential;
const TITLE = { y0: E.y0 + 30, y1: E.y0 + 180 };
const READOUT = { y0: 1150, y1: 1330 };
const STAGE = { x0: E.x0 + 24, x1: E.x1 - 24, y0: TITLE.y1 + 20, y1: READOUT.y0 - 20 };

const Title: React.FC<{ title?: string; subtitle?: string }> = ({ title, subtitle }) => {
  const e = useEntrance("rise", 0);
  if (!title) return null;
  return (
    <div style={{ position: "absolute", left: STAGE.x0, top: TITLE.y0, width: STAGE.x1 - STAGE.x0,
                  opacity: e.opacity, transform: `translateY(${e.y}px)` }}>
      <SafeText role="display" fontSize={68} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
      {subtitle ? <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim}>{subtitle}</SafeText> : null}
    </div>
  );
};

const Readout: React.FC<{ readout?: string; caption?: string; from?: number; k?: string | number }> = ({ readout, caption, from = 0, k }) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [from, from + 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out });
  if (!readout && !caption) return null;
  return (
    <div key={k} style={{ position: "absolute", left: STAGE.x0, top: READOUT.y0, width: STAGE.x1 - STAGE.x0,
                          height: READOUT.y1 - READOUT.y0, display: "flex", flexDirection: "column",
                          justifyContent: "center", opacity: t, transform: `translateY(${(1 - t) * 14}px)` }}>
      {readout ? (
        <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent}
                  style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{readout}</SafeText>
      ) : null}
      {caption ? <SafeText role="body" fontSize={48} maxLines={2}>{caption}</SafeText> : null}
    </div>
  );
};

/**
 * Patina dot colours, sampled from the media-library Set diagrams
 * (patina_sets_diagram.png in the user's cents-graphics folder), so the films
 * use the same key the community already reads.
 */
export const PATINA_DOT = {
  verdigris: "rgb(124,179,66)",
  obsidian: "rgb(66,66,66)",
  desert: "rgb(224,224,224)",
  red: "rgb(244,67,54)",
  gold: "rgb(255,204,50)",
  orange: "rgb(255,152,0)",
} as const;
export type Patina = keyof typeof PATINA_DOT;

type Hero = { n: number; caption?: string; at_phrase?: string; patina?: Patina; src?: string };

/** The key dot under a Cent. Obsidian gets a light rim, or it vanishes into the background. */
const Dot: React.FC<{ patina: Patina; d: number }> = ({ patina, d }) => {
  const c = PATINA_DOT[patina];
  if (!c) throw new Error(`no dot colour for patina "${patina}"`);
  return (
    <div style={{ width: d, height: d, borderRadius: "50%", background: c,
                  boxShadow: `inset 0 -${d * 0.12}px ${d * 0.2}px rgba(0,0,0,0.25), 0 0 0 2px rgba(255,255,255,${patina === "obsidian" ? 0.35 : 0.08})` }} />
  );
};

/**
 * A handful of named Cents: the example Cents of a Set, or one per type as the
 * narration names it. A Cent with `at_phrase` arrives when that phrase is
 * spoken and its caption takes the readout; the rest arrive together at the cut.
 * `labelsUnder` puts each caption under its own coin instead (short labels only,
 * like years).
 * `solo_until` shows each anchored Cent on its own, large, as it is named, and
 * then gathers them all into the row at that phrase.
 */
export const CentRow: React.FC<Anchored & {
  title?: string; subtitle?: string; cents: Hero[]; labelsUnder?: boolean; cols?: number;
  readout?: string; caption?: string; readout_at?: string; solo_until?: string;
}> = (props) => {
  const { title, subtitle, cents, labelsUnder, cols, readout, caption, readout_at, solo_until } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  if (cents.length === 0) throw new Error("CentRow: no Cents");
  const W = STAGE.x1 - STAGE.x0, H = STAGE.y1 - STAGE.y0;
  const dots = cents.some((c) => c.patina);
  const labelH = labelsUnder ? 64 : dots ? 52 : 0;
  // Fit cells that include the label band, then take the coin out of the cell.
  // `cols` fixes the arrangement (three in a row reads as a set of three).
  const lay = cols
    ? (() => { const cell = Math.min(W / cols, H / Math.ceil(cents.length / cols));
               const size = Math.floor(cell / 1.12); return { cols, size, gap: Math.floor(cell - size) }; })()
    : fitGrid(cents.length, W, H, 0.12);
  const size = Math.min(MAX_CENT_PX, Math.floor(lay.size - labelH * (lay.size / (lay.size + labelH))));
  const cellW = lay.size + lay.gap, cellH = size + labelH + lay.gap;
  const rows = Math.ceil(cents.length / lay.cols);
  const ox = STAGE.x0 + (W - lay.cols * cellW + lay.gap) / 2;
  const oy = STAGE.y0 + (H - rows * cellH + lay.gap) / 2;
  const spoken = cents.map((c, i) => (c.at_phrase ? at(c.at_phrase) : i * 3));
  for (let i = 1; i < spoken.length; i++)
    if (cents[i]!.at_phrase && cents[i - 1]!.at_phrase && spoken[i]! < spoken[i - 1]!)
      throw new Error(`CentRow: "${cents[i]!.at_phrase}" is spoken before "${cents[i - 1]!.at_phrase}"`);
  // The readout follows the most recently arrived anchored Cent.
  let cur = -1;
  cents.forEach((c, i) => { if (c.at_phrase && frame >= spoken[i]!) cur = i; });
  const rFrom = readout_at ? at(readout_at) : 0;
  const soloEnd = solo_until ? at(solo_until) : -1;
  if (solo_until && soloEnd <= Math.max(...spoken)) throw new Error(`CentRow: "${solo_until}" comes before the last Cent is named`);
  if (solo_until && frame < soloEnd) {
    // One Cent at a time, as large as the stage allows: the full stage height,
    // centred on the frame. A high-res front (src) keeps it sharp at that size.
    const c = cur >= 0 ? cents[cur]! : null;
    const big = c?.src ? Math.floor(H) : Math.min(MAX_CENT_PX, Math.floor(Math.min(W, H) * 0.86));
    const S = big * (0.5 / 0.402);      // cents.vision fronts: the coin is a circle of radius 0.40 on white
    const t = c ? interpolate(frame, [spoken[cur]!, spoken[cur]! + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out }) : 0;
    return (
      <div style={{ position: "absolute", inset: 0, opacity: fade }}>
        <Title title={title} subtitle={subtitle} />
        {c ? (
          <Imagery>
            {c.src ? (
              <div key={c.n} style={{ position: "absolute", left: 540 - S / 2, top: STAGE.y0 + H / 2 - S / 2, width: S, height: S,
                                      opacity: t, transform: `scale(${0.9 + 0.1 * t})`, filter: "drop-shadow(0 14px 24px rgba(0,0,0,0.55))" }}>
                <Img src={staticFile(c.src)} style={{ width: S, height: S, clipPath: "circle(40.5% at 50% 50%)" }} />
              </div>
            ) : (
              <div key={c.n} style={{ position: "absolute", left: STAGE.x0 + (W - big) / 2, top: STAGE.y0 + (H - big) / 2,
                                      opacity: t, transform: `scale(${0.85 + 0.15 * t})`, filter: "drop-shadow(0 14px 24px rgba(0,0,0,0.55))" }}>
                <CentImage n={c.n} size={big} />
              </div>
            )}
          </Imagery>
        ) : null}
        {c && c.caption ? <Readout key={cur} k={cur} caption={c.caption} from={spoken[cur]} /> : null}
      </div>
    );
  }
  // Gathered: after a solo run the Cents assemble in quick order at solo_until.
  const starts = solo_until ? cents.map((_, i) => soloEnd + i * 2) : spoken;
  if (solo_until) cur = -1;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Title title={title} subtitle={subtitle} />
      <Imagery>
        {cents.map((c, i) => {
          const f0 = starts[i]!;
          const t = interpolate(frame, [f0, f0 + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out });
          const lit = cur === -1 || !cents.some((x) => x.at_phrase) || i === cur ? 1 : 0.55;
          const col = i % lay.cols, row = Math.floor(i / lay.cols);
          return (
            <div key={c.n} style={{ position: "absolute", left: ox + col * cellW + (lay.size - size) / 2, top: oy + row * cellH,
                                    opacity: t * lit, transform: `scale(${0.7 + 0.3 * t})`,
                                    filter: "drop-shadow(0 10px 18px rgba(0,0,0,0.5))" }}>
              <CentImage n={c.n} size={size} />
              {c.patina ? (
                <div style={{ display: "flex", justifyContent: "center", marginTop: 14 }}>
                  <Dot patina={c.patina} d={Math.round(Math.max(24, Math.min(40, size * 0.14)))} />
                </div>
              ) : null}
            </div>
          );
        })}
      </Imagery>
      {labelsUnder ? cents.map((c, i) => {
        const col = i % lay.cols, row = Math.floor(i / lay.cols);
        const t = interpolate(frame, [starts[i]! + 4, starts[i]! + 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return c.caption ? (
          <div key={`l${c.n}`} style={{ position: "absolute", left: ox + col * cellW, top: oy + row * cellH + size + 8,
                                        width: lay.size, display: "flex", justifyContent: "center", opacity: t }}>
            <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.inkDim}>{c.caption}</SafeText>
          </div>
        ) : null;
      }) : null}
      {!labelsUnder && cur >= 0 && cents[cur]!.caption ? (
        <Readout key={cur} k={cur} caption={cents[cur]!.caption} from={starts[cur]} />
      ) : null}
      {readout || caption ? <Readout readout={readout} caption={caption} from={rFrom} /> : null}
    </div>
  );
};

/**
 * Every Cent in a pool, as large as the stage allows. The count is declared in
 * the timeline as `readout`, so the ledger sees it, and checked here against
 * the pool's own length, so the number on screen cannot disagree with the wall.
 */
export const PoolWall: React.FC<Anchored & {
  pool: string; readout: string; title?: string; caption?: string; readout_at?: string;
}> = (props) => {
  const { title, caption, readout, readout_at } = props;
  const fade = useShotFade();
  const at = useAt(props);
  const ns = pool(props.pool);
  if (readout !== ns.length.toLocaleString("en-US"))
    throw new Error(`PoolWall ${props.pool}: readout says ${readout} but the pool holds ${ns.length}`);
  const W = STAGE.x1 - STAGE.x0, H = STAGE.y1 - STAGE.y0;
  const lay = fitGrid(ns.length, W, H, 0.1);
  const size = Math.min(lay.size, 300);
  const layout = { ...lay, size };
  const step = size + lay.gap;
  const rows = Math.ceil(ns.length / lay.cols);
  const left = STAGE.x0 + (W - (lay.cols * step - lay.gap)) / 2;
  const top = STAGE.y0 + (H - (rows * step - lay.gap)) / 2;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Title title={title} />
      <Imagery>
        <CentGrid ns={ns} layout={layout} enterFrames={Math.min(36, ns.length * 2)}
                  style={{ position: "absolute", left, top }} />
      </Imagery>
      <Readout readout={readout} caption={caption}
               from={readout_at ? at(readout_at) : 6} />
    </div>
  );
};

/** One Cent, turning. For what a trait looks like, close. */
export const CentHero: React.FC<Anchored & { n: number; title?: string; caption?: string }> = ({ n, title, caption }) => {
  const fade = useShotFade();
  const size = 500;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Title title={title} />
      <Imagery>
        <CentTurn n={n} size={size} style={{ position: "absolute", left: (1080 - size) / 2,
                                               top: STAGE.y0 + (STAGE.y1 - STAGE.y0 - size) / 2 }} />
      </Imagery>
      <Readout caption={caption} from={10} />
    </div>
  );
};

/**
 * All 10,000 as a field behind a title, in number order. Texture, never
 * evidence: at this size no trait is visible. It is one baked image of the same
 * cutouts (pipeline/field_mosaic.py), because 10,000 live images time out the
 * renderer.
 */
export const FieldTitle: React.FC<Anchored & { title: string; subtitle?: string }> = ({ title, subtitle }) => {
  const fade = useShotFade();
  const frame = useCurrentFrame();
  const e0 = useEntrance("rise", 0, 10), e1 = useEntrance("rise", 1, 10);
  const enter = interpolate(frame, [0, 24], [0, 1], { extrapolateRight: "clamp", easing: EASE.out });
  const drift = interpolate(frame, [0, 300], [1.0, 1.06], { extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Imagery>
        <Img src={staticFile("cents_field.webp")}
             style={{ position: "absolute", left: 40, top: 520, width: 1000, height: 1000,
                      opacity: 0.5 * enter, transform: `scale(${drift})` }} />
        <div style={{ position: "absolute", inset: 0,
                      background: "linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.1) 40%, rgba(0,0,0,0.5))" }} />
      </Imagery>
      <div style={{ position: "absolute", left: STAGE.x0, top: E.y0 + 40, width: STAGE.x1 - STAGE.x0 }}>
        <div style={{ opacity: e0.opacity, transform: `translateY(${e0.y}px)` }}>
          <SafeText role="display" fontSize={104} maxLines={2} style={{ fontWeight: 700, letterSpacing: -2 }}>{title}</SafeText>
        </div>
        {subtitle ? (
          <div style={{ opacity: e1.opacity, transform: `translateY(${e1.y}px)`, marginTop: 12 }}>
            <SafeText role="body" fontSize={52} maxLines={2} color={COLOR.inkDim}>{subtitle}</SafeText>
          </div>
        ) : null}
      </div>
    </div>
  );
};

/**
 * Higher-resolution photographs (pipeline/stage_cents.py --hi): ten from the
 * user's folder and the rest from cents.vision's own pics/frontswebp/<n>.webp
 * (1050px), each identity-checked against the on-chain image. About 860px of
 * coin against the on-chain 246. Only these may be zoomed into:
 * a zoom on the 300px image would enlarge pixels, not the trait.
 */
export const HI_RES = new Set([
  25, 70, 91, 111, 121, 215, 312, 322, 337, 412, 608, 794, 809, 990, 1079, 1170, 1264, 1510, 1771, 2332, 2359, 2568, 2583, 2735, 2785, 2881, 2900, 2956, 3398, 3861, 3950, 3981, 4273, 4554, 4668, 4679, 4788, 4825, 4884, 5144, 5346, 5581, 6055, 6059, 6078, 6107, 6223, 6492, 6495, 6980, 7799, 7823, 7926, 8185, 8353, 8382, 9172, 9533, 9786, 9992,
]);
const HI_MAX_PX = 1150;

type Segment = {
  /** Optional on the first segment only: absent, it starts with the shot. */
  at_phrase?: string;
  /** Pool key(s) from films/sets/data/pools.json, or "*" for the whole collection. */
  pool: string | string[];
  /** How many Cents flash past before the hero. 0 = straight to the hero. */
  count?: number;
  hero?: number;
  /** Where the trait is on the hero, as fractions of its width and height. */
  focus?: [number, number];
  /** How far to push in on the focus. Only on a high-resolution hero. */
  zoom?: number;
  caption?: string;
  patina?: Patina;
  /** A count shown with the caption; checked against the pool's size. */
  readout?: string;
};

/** Deterministic sample, so a re-render shows the same Cents. */
const sample = (ns: number[], k: number, seed: string, avoid?: number): number[] => {
  let h = 2166136261;
  for (let i = 0; i < seed.length; i++) h = Math.imul(h ^ seed.charCodeAt(i), 16777619) >>> 0;
  const pool = ns.filter((n) => n !== avoid);
  if (k >= pool.length) return pool;
  const out: number[] = [];
  const used = new Set<number>();
  while (out.length < k) {
    h = Math.imul(h ^ (h >>> 13), 0x5bd1e995) >>> 0;
    const n = pool[h % pool.length]!;
    if (!used.has(n)) { used.add(n); out.push(n); }
  }
  return out;
};

const ALL = Array.from({ length: 10000 }, (_, i) => i + 1);
const poolOf = (p: string | string[]): number[] => {
  if (p === "*") return ALL;
  const keys = Array.isArray(p) ? p : [p];
  return Array.from(new Set(keys.flatMap((k) => pool(k)))).sort((a, b) => a - b);
};

/**
 * Many Cents for one trait, in quick succession, then one held large. Each
 * segment starts on the phrase that names its trait. Where the hero exists in
 * high resolution the hold pushes in on the part of the coin that bears the
 * trait (`focus`); otherwise it turns slowly at the size its source allows.
 */
export const TraitBurst: React.FC<Anchored & { title?: string; segments: Segment[]; flash?: number }> = (props) => {
  const { title, segments, flash = 4 } = props;
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const fade = useShotFade();
  const at = useAt(props);
  if (segments.length === 0) throw new Error("TraitBurst: no segments");
  segments.forEach((s, k) => { if (k > 0 && !s.at_phrase) throw new Error(`TraitBurst: segment ${k + 1} has no at_phrase`); });
  const starts = segments.map((s) => (s.at_phrase ? at(s.at_phrase) : 0));
  if (starts[0] !== 0 && starts[0]! > 2) throw new Error(`TraitBurst: first segment starts ${starts[0]} frames in; the shot would open empty`);
  for (let i = 1; i < starts.length; i++)
    if (starts[i]! <= starts[i - 1]!) throw new Error(`TraitBurst: "${segments[i]!.at_phrase}" is not after "${segments[i - 1]!.at_phrase}"`);
  let i = 0;
  for (let k = 0; k < starts.length; k++) if (frame >= starts[k]!) i = k;
  const seg = segments[i]!;
  const s0 = Math.max(0, starts[i]!);
  const s1 = i + 1 < starts.length ? starts[i + 1]! : durationInFrames;
  const ns = poolOf(seg.pool);
  if (seg.readout !== undefined && seg.readout !== ns.length.toLocaleString("en-US"))
    throw new Error(`TraitBurst ${JSON.stringify(seg.pool)}: readout says ${seg.readout} but the pool holds ${ns.length}`);
  if (seg.hero !== undefined && !ns.includes(seg.hero))
    throw new Error(`TraitBurst: hero #${seg.hero} is not in pool ${JSON.stringify(seg.pool)}`);
  if (seg.zoom && seg.zoom > 1 && (seg.hero === undefined || !HI_RES.has(seg.hero)))
    throw new Error(`TraitBurst: zoom on #${seg.hero} needs a high-resolution photograph; the 300px image cannot hold it`);
  const len = s1 - s0;
  // The flashes may take at most 60% of the segment, so the hero always lands.
  const wanted = seg.count ?? 6;
  const step = Math.max(2, Math.min(flash, Math.floor((len * (seg.hero ? 0.6 : 1)) / Math.max(1, wanted))));
  const flashes = sample(ns, Math.min(wanted, Math.floor((len * (seg.hero ? 0.6 : 1)) / step)), `${seg.at_phrase ?? "shot start"}`, seg.hero);
  const local = frame - s0;
  const inFlash = local < flashes.length * step;
  const hi = seg.hero !== undefined && HI_RES.has(seg.hero);

  // A round window the size of the held coin: at rest it is the coin's own
  // edge, and a push-in fills it with the trait instead of spilling past it.
  const BOX = 640;
  const cx = 540, cy = STAGE.y0 + (STAGE.y1 - STAGE.y0) / 2;
  const left = cx - BOX / 2, top = cy - BOX / 2;
  let coin: React.ReactNode = null;
  if (inFlash || seg.hero === undefined) {
    const n = flashes[Math.min(flashes.length - 1, Math.floor(local / step))];
    const size = MAX_CENT_PX;
    if (n !== undefined)
      coin = (
        <div style={{ position: "absolute", left: (BOX - size) / 2, top: (BOX - size) / 2 }}>
          <CentImage n={n} size={size} />
        </div>
      );
  } else {
    const hold = local - flashes.length * step;
    const holdLen = Math.max(1, len - flashes.length * step);
    const t = interpolate(hold, [0, holdLen], [0, 1], { extrapolateRight: "clamp", easing: EASE.inOut });
    const enter = interpolate(hold, [0, 8], [0.92, 1], { extrapolateRight: "clamp", easing: EASE.out });
    if (hi) {
      const size = BOX;
      const z = 1 + ((seg.zoom ?? 1) - 1) * t;
      if (size * z > HI_MAX_PX) throw new Error(`TraitBurst: #${seg.hero} at ${Math.round(size * z)}px is past the ${HI_MAX_PX}px its photograph holds`);
      const [fx, fy] = seg.focus ?? [0.5, 0.5];
      // Move the focus toward the window's centre as the zoom grows, but never
      // so far that the coin's own rim enters the window: the photograph is
      // cropped to the coin, so its centre may sit at most (z-1)*size/2 off.
      const wantX = (0.5 - fx) * size * (z - 1 + t), wantY = (0.5 - fy) * size * (z - 1 + t);
      const off = Math.hypot(wantX, wantY), lim = (z - 1) * size / 2 * 0.97;
      const k = off > lim ? lim / off : 1;
      const dx = wantX * k - (0.5 - fx) * size * (z - 1);
      const dy = wantY * k - (0.5 - fy) * size * (z - 1);
      coin = (
        <div style={{ position: "absolute", left: (BOX - size) / 2, top: (BOX - size) / 2, width: size, height: size,
                      transform: `translate(${dx}px, ${dy}px) scale(${z * enter})`, transformOrigin: `${fx * 100}% ${fy * 100}%` }}>
          <Img src={staticFile(`cents_hi/${seg.hero}.webp`)} style={{ width: size, height: size, display: "block" }} />
        </div>
      );
    } else {
      const size = MAX_CENT_PX;
      coin = (
        <div style={{ position: "absolute", left: (BOX - size) / 2, top: (BOX - size) / 2, transform: `scale(${enter})` }}>
          <CentTurn n={seg.hero!} size={size} from={s0 + flashes.length * step} spin={4} maxTilt={10} />
        </div>
      );
    }
  }
  const capT = interpolate(local, [0, 6], [0, 1], { extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Title title={title} />
      <Imagery>
        <div style={{ position: "absolute", left, top, width: BOX, height: BOX, overflow: "hidden", borderRadius: "50%",
                      filter: "drop-shadow(0 14px 26px rgba(0,0,0,0.55))" }}>
          {coin}
        </div>
      </Imagery>
      {seg.caption || seg.readout ? (
        <div key={i} style={{ position: "absolute", left: STAGE.x0, top: READOUT.y0, width: STAGE.x1 - STAGE.x0,
                              height: READOUT.y1 - READOUT.y0, display: "flex", flexDirection: "column", justifyContent: "center", opacity: capT }}>
          {seg.readout ? (
            <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent}
                      style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{seg.readout}</SafeText>
          ) : null}
          {seg.caption ? (
            <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
              {seg.patina ? <Imagery><Dot patina={seg.patina} d={34} /></Imagery> : null}
              <SafeText role="body" fontSize={52} maxLines={2}>{seg.caption}</SafeText>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
};

// Video.tsx passes {alignment, shotStartFrame} to components that ask for it.

/**
 * Screens from cents.vision, as captured (see pipeline/stage_vision.py). Each
 * segment pans a window across one capture, from one crop to another, so the
 * page can be read rather than shown as a thumbnail. Crops are [x, y, width]
 * in the capture's own pixels; the height follows the window's shape.
 */
type Screen = {
  /** Starts when this phrase starts, or (after_phrase) when it ends; plus `delay` seconds. */
  at_phrase?: string; after_phrase?: string; delay?: number;
  src: string; caption?: string;
  /** Crops [x, y, width]; or `fit` for a landscape capture shown whole, pushing in slightly. */
  from?: [number, number, number]; to?: [number, number, number]; fit?: boolean;
  /** Window height as a fraction of its width, for landscape captures; default fills the stage. */
  aspect?: number;
  /** How far a `fit` capture pushes in over its time (default 0.06); 0 keeps a signed chart's edges whole. */
  push?: number;
};
export const ScreenTour: React.FC<Anchored & { title?: string; subtitle?: string; screens: Screen[] }> = (props) => {
  const { title, subtitle, screens } = props;
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const fade = useShotFade();
  const at = useAt(props);
  if (screens.length === 0) throw new Error("ScreenTour: no screens");
  const { fps } = useVideoConfig();
  screens.forEach((s, k) => { if (k > 0 && !s.at_phrase && !s.after_phrase) throw new Error(`ScreenTour: screen ${k + 1} has no anchor`); });
  const starts = screens.map((s) => {
    const base = s.after_phrase ? Math.round(findPhrase(props.alignment, s.after_phrase).end * fps) - props.shotStartFrame
      : s.at_phrase ? at(s.at_phrase) : 0;
    if (base < 0) throw new Error(`ScreenTour: "${s.after_phrase}" ends before this shot starts`);
    return base + Math.round((s.delay ?? 0) * fps);
  });
  if (starts[0]! > 2) throw new Error("ScreenTour: the first screen starts late; the shot would open empty");
  for (let k = 1; k < starts.length; k++)
    if (starts[k]! <= starts[k - 1]!) throw new Error(`ScreenTour: "${screens[k]!.at_phrase}" is not after the screen before it`);
  let i = 0;
  for (let k = 0; k < starts.length; k++) if (frame >= starts[k]!) i = k;
  const sc = screens[i]!;
  const s0 = starts[i]!, s1 = i + 1 < starts.length ? starts[i + 1]! : durationInFrames;
  const W = STAGE.x1 - STAGE.x0, H = sc.aspect ? Math.round(W * sc.aspect) : STAGE.y1 - STAGE.y0;
  const top = STAGE.y0 + (STAGE.y1 - STAGE.y0 - H) / 2;
  const t = interpolate(frame, [s0, s1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });
  if (!sc.fit && !sc.from) throw new Error(`ScreenTour ${sc.src}: needs a crop or fit`);
  const from = sc.from ?? [0, 0, 1080];
  const to = sc.to ?? from;
  const [x, y, w] = [0, 1, 2].map((k) => from[k]! + (to[k]! - from[k]!) * t) as [number, number, number];
  if (w > 1080 || x < 0 || x + w > 1080) throw new Error(`ScreenTour ${sc.src}: crop leaves the 1080 px capture`);
  const k = W / w;
  const push = 1 + (sc.push ?? 0.06) * t;
  const cut = interpolate(frame, [s0, s0 + 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Title title={title} subtitle={subtitle} />
      <Imagery>
        <div style={{ position: "absolute", left: STAGE.x0, top, width: W, height: H, overflow: "hidden",
                      borderRadius: 28, background: "#fff", opacity: i === 0 ? 1 : cut,
                      boxShadow: "0 18px 40px rgba(0,0,0,0.55)" }}>
          {sc.fit ? (
            <Img src={staticFile(`vision/${sc.src}`)}
                 style={{ position: "absolute", left: 0, top: "50%", width: W, display: "block",
                          transform: `translateY(-50%) scale(${push})` }} />
          ) : (
            <Img src={staticFile(`vision/${sc.src}`)}
                 style={{ position: "absolute", left: -x * k, top: -y * k, width: 1080 * k, display: "block" }} />
          )}
        </div>
      </Imagery>
      <Readout caption={sc.caption} from={s0} k={i} />
    </div>
  );
};

/**
 * The last shot: credits in the silence after the narration, then a wall of
 * Cents filling the frame. A deterministic sample, so every render is the same
 * wall; ordered by number, as the collection is.
 */
export const EndWall: React.FC<Anchored & { lines: string[]; url?: string; text_after: number; cols?: number }> = (props) => {
  const { lines, url, text_after, cols = 9 } = props;
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const fade = useShotFade();
  const t0 = Math.round(text_after * fps);
  if (t0 <= 0 || t0 >= durationInFrames - 2 * fps) throw new Error(`EndWall: text at ${text_after}s leaves under 2 s to read it`);
  const gap = 10, size = Math.floor((1080 - gap * (cols + 1)) / cols);
  const rows = Math.ceil((1920 - gap) / (size + gap));
  const ns = sample(poolOf("*"), cols * rows, "end wall").sort((a, b) => a - b);
  const text = interpolate(frame, [t0, t0 + 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out });
  const drift = interpolate(frame, [0, durationInFrames], [1.0, 1.05], { extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
        <div style={{ position: "absolute", inset: 0, transform: `scale(${drift})` }}>
          <CentGrid ns={ns} layout={{ cols, size, gap }} from={0} enterFrames={Math.min(45, t0 - 6)}
                    style={{ position: "absolute", left: gap, top: gap }} />
        </div>
        {/* A scrim under the text only: the wall stays the picture, the words stay readable. */}
        <div style={{ position: "absolute", inset: 0, opacity: text,
                      background: "radial-gradient(ellipse 80% 34% at 50% 47%, rgba(10,10,10,0.94), rgba(10,10,10,0.82) 60%, rgba(10,10,10,0.45))" }} />
      </div>
      <div style={{ position: "absolute", left: STAGE.x0, width: STAGE.x1 - STAGE.x0, top: STAGE.y0, height: READOUT.y1 - STAGE.y0,
                    display: "flex", flexDirection: "column", justifyContent: "center", gap: 18, opacity: text,
                    transform: `translateY(${(1 - text) * 14}px)` }}>
        {lines.map((l, i) => <SafeText key={i} role="body" fontSize={48} maxLines={2}>{l}</SafeText>)}
        {url ? <SafeText role="body" fontSize={48} maxLines={1} color={COLOR.accent}>{url}</SafeText> : null}
      </div>
    </div>
  );
};

for (const C of [CentRow, PoolWall, CentHero, FieldTitle, TraitBurst, ScreenTour, EndWall]) (C as any).wantsAlignment = true;

export const SETS = { CentRow, PoolWall, CentHero, FieldTitle, TraitBurst, ScreenTour, EndWall } as const;
