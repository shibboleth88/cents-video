import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { EASE, useShotFade } from "./motion";
import { COLOR, SAFE, TYPE } from "./tokens";
import { Imagery, SafeText } from "./Safe";
import { findPhrase, type Alignment } from "../lib/timeline";
import { PATINA_DOT, type Patina } from "./sets";

/**
 * Shots for a Collector Wall episode about the character of a whole Wall
 * (blacktongue, 2026-11-14): what the collection holds taken together, rather
 * than Cent by Cent.
 *
 * `PatinaLadder`: the Wall's own Cents laid out as a grid of patina (rows) by
 * grade (columns): notable, significant, full. Each row arrives as its patina is
 * named; a column lights as its grade is explained. A cell is a real Cent by
 * number (1050px cents.vision front, cut out on black) or null where the grade
 * does not exist for that patina (gold has no significant grade), drawn as a
 * dash, never as an empty slot that reads like a gap in the Wall.
 * Which Cent stands in which cell is checked against the dated snapshot by the
 * film's data script (films/wall-blacktongue-character/data/character.py), not here.
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
const ease = (frame: number, from: number, len: number) =>
  interpolate(frame, [from, from + len], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out });

/** A 1050px front clipped to its coin, `d` px across (the fronts put the coin in a circle of radius ~0.40). */
const Coin: React.FC<{ n: number; d: number }> = ({ n, d }) => {
  const S = d * (0.5 / 0.402);
  return (
    <div style={{ width: d, height: d, position: "relative" }}>
      <Img src={staticFile(`hires/${n}.webp`)} style={{ position: "absolute", left: (d - S) / 2, top: (d - S) / 2, width: S, height: S,
                                                      clipPath: "circle(40.5% at 50% 50%)",
                                                      filter: `drop-shadow(0 ${d * 0.04}px ${d * 0.06}px rgba(0,0,0,0.55))` }} />
    </div>
  );
};

type LadderRow = { label: string; at_phrase: string; cells: (number | null)[];
  /** A patina with no grades (orange): one Cent, drawn across every grade column on a rule, and lit only when no single grade is. */
  ungraded?: boolean };
type ColumnLight = { at_phrase: string; column: number | null };

export const PatinaLadder: React.FC<Anchored & {
  columns: string[]; rows: LadderRow[];
  /** Light one column (dimming the others) from each phrase on; column null lights them all again. */
  lights?: ColumnLight[];
}> = (props) => {
  const { columns, rows, lights = [] } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  if (rows.length === 0) throw new Error("PatinaLadder: no rows");
  rows.forEach((r) => {
    if (r.ungraded) { if (r.cells.length !== 1 || r.cells[0] === null) throw new Error(`PatinaLadder: ungraded row "${r.label}" takes exactly one Cent`); return; }
    if (r.cells.length !== columns.length) throw new Error(`PatinaLadder: row "${r.label}" has ${r.cells.length} cells for ${columns.length} columns`);
  });
  const seen = new Set<number>();
  rows.forEach((r) => r.cells.forEach((n) => {
    if (n === null) return;
    if (seen.has(n)) throw new Error(`PatinaLadder: #${n} stands in two cells; each cell shows a different Cent`);
    seen.add(n);
  }));
  const rowAt = rows.map((r) => at(r.at_phrase));
  for (let i = 1; i < rowAt.length; i++) if (rowAt[i]! < rowAt[i - 1]!) throw new Error(`PatinaLadder: "${rows[i]!.at_phrase}" is spoken before "${rows[i - 1]!.at_phrase}"`);
  // The grid is laid out from frame 0 (headers and labels), but the first row must not keep it empty for long.
  if (rowAt[0]! > 15) throw new Error(`PatinaLadder: the first row arrives ${rowAt[0]} frames into the shot; the grid would stand empty (LEDGER: a shot's start is not the moment its content appears)`);
  const lightAt = lights.map((l) => at(l.at_phrase));
  for (let i = 1; i < lightAt.length; i++) if (lightAt[i]! <= lightAt[i - 1]!) throw new Error("PatinaLadder: column lights must come in spoken order");
  lights.forEach((l) => { if (l.column !== null && (l.column < 0 || l.column >= columns.length)) throw new Error(`PatinaLadder: no column ${l.column}`); });

  // Layout: labels on the left inside the essential box, coins in columns to the right.
  const labelX0 = E.x0 + 12, labelW = 180;
  const pitch = 206;
  const cx0 = labelX0 + labelW + pitch / 2 - 8;
  const headY = E.y0 + 36, headH = 64;
  const gridY0 = headY + headH + 18, gridY1 = 1320;
  const rowH = (gridY1 - gridY0) / rows.length;
  const d = Math.floor(Math.min(pitch - 18, rowH - 14));

  // Which column is lit now, and how far into its light we are (for a soft crossfade).
  let li = -1;
  lightAt.forEach((f, i) => { if (frame >= f) li = i; });
  const lit = li >= 0 ? lights[li]!.column : null;
  const litT = li >= 0 ? ease(frame, lightAt[li]!, 10) : 1;
  const prevLit = li > 0 ? lights[li - 1]!.column : null;
  const colAlpha = (c: number) => {
    const now = lit === null || lit === c ? 1 : 0.32;
    const before = li <= 0 ? 1 : prevLit === null || prevLit === c ? 1 : 0.32;
    return before + (now - before) * litT;
  };
  // An ungraded row belongs to no single column: full while nothing is lit, dimmed while any one column is.
  const spanAlpha = () => {
    const now = lit === null ? 1 : 0.32;
    const before = li <= 0 ? 1 : prevLit === null ? 1 : 0.32;
    return before + (now - before) * litT;
  };
  const drift = interpolate(frame, [0, 600], [1, 1.035], { extrapolateRight: "clamp" });

  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      {columns.map((c, i) => {
        const on = lit === i && li >= 0;
        return (
          <div key={c} style={{ position: "absolute", left: cx0 + i * pitch - 120, top: headY, width: 240, display: "flex", justifyContent: "center",
                                opacity: colAlpha(i) }}>
            <SafeText role="label" fontSize={42} maxLines={1} color={on ? COLOR.accent : COLOR.ink}
                      style={{ fontFamily: TYPE.body, fontWeight: 500, letterSpacing: -0.5, textAlign: "center", whiteSpace: "nowrap" }}>{c}</SafeText>
          </div>
        );
      })}
      {rows.map((r, ri) => {
        const y = gridY0 + ri * rowH + rowH / 2;
        const t0 = rowAt[ri]!;
        const labelT = ease(frame, t0, 10);
        return (
          <React.Fragment key={r.label}>
            <div style={{ position: "absolute", left: labelX0, top: y - 30, width: labelW, opacity: labelT, transform: `translateX(${(1 - labelT) * 14}px)` }}>
              <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.ink} style={{ fontFamily: TYPE.body, whiteSpace: "nowrap" }}>{r.label}</SafeText>
            </div>
            {r.ungraded ? (() => {
              const t = ease(frame, t0 + 3, 12);
              const xL = cx0 - d / 2, xR = cx0 + (columns.length - 1) * pitch + d / 2;
              return (
                <>
                  <div style={{ position: "absolute", left: xL, top: y - 1.5, width: (xR - xL) * t, height: 3, borderRadius: 2,
                                background: COLOR.inkDim, opacity: 0.45 * spanAlpha() }} />
                  <Imagery>
                    <div style={{ position: "absolute", left: cx0 + pitch * (columns.length - 1) / 2 - d / 2, top: y - d / 2, opacity: t * spanAlpha(),
                                  transform: `scale(${(0.82 + 0.18 * t) * drift})` }}>
                      <div style={{ background: COLOR.bg, borderRadius: "50%" }}><Coin n={r.cells[0]!} d={d} /></div>
                    </div>
                  </Imagery>
                </>
              );
            })() : null}
            {r.ungraded ? null : <Imagery>
              {r.cells.map((n, ci) => {
                const t = ease(frame, t0 + 3 + ci * 4, 12);
                const x = cx0 + ci * pitch;
                if (n === null) {
                  return <div key={ci} style={{ position: "absolute", left: x - 28, top: y - 2, width: 56, height: 4, borderRadius: 2,
                                                background: COLOR.inkDim, opacity: 0.6 * t * colAlpha(ci) }} />;
                }
                return (
                  <div key={ci} style={{ position: "absolute", left: x - d / 2, top: y - d / 2, opacity: t * colAlpha(ci),
                                         transform: `scale(${(0.82 + 0.18 * t) * drift})` }}>
                    <Coin n={n} d={d} />
                  </div>
                );
              })}
            </Imagery>}
          </React.Fragment>
        );
      })}
    </div>
  );
};

/**
 * `GradeStrips`: which of the counted patina values each named Wall holds, one strip
 * of dots per Wall, in the ladder's order (verdigris, obsidian, desert and red at
 * notable, significant and full; gold at notable and full; then orange, which has no
 * grades: fifteen in the blacktongue episode's draft 3, 2026-11-14). Above
 * the strips, the Wall's own full-grade Cents stand as the key for each patina group.
 * A held grade is a filled dot; a missing one an empty ring, which can be marked
 * (copper) when its absence is spoken. Each row's count is computed from its dots;
 * the timeline also declares it, and a disagreement stops the render. A row can be
 * set apart under a rule (the artist wallet, which is never a collector).
 */
type StripRow = { name: string; cents: number; held: boolean[]; count: number; at_phrase: string; apart?: boolean };
export const GradeStrips: React.FC<Anchored & {
  title: string; subtitle?: string;
  /** Sizes of the patina groups along a strip, e.g. [3, 3, 3, 3, 2]; they must sum to each strip's length. */
  groups: number[];
  /** One key Cent per group (shown above it), by number. */
  keys: number[];
  /** The patina of each group: held dots take the series' patina key colour (as under the Full Spectrum Cents). */
  patinas: Patina[];
  rows: StripRow[];
  /** From this phrase, the empty rings of every row are marked in copper. */
  mark_missing_at?: string;
}> = (props) => {
  const { title, subtitle, groups, keys, patinas, rows, mark_missing_at } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  const len = groups.reduce((a, b) => a + b, 0);
  if (keys.length !== groups.length) throw new Error(`GradeStrips: ${keys.length} key Cents for ${groups.length} groups`);
  if (patinas.length !== groups.length) throw new Error(`GradeStrips: ${patinas.length} patinas for ${groups.length} groups`);
  patinas.forEach((p) => { if (!PATINA_DOT[p]) throw new Error(`GradeStrips: no key colour for "${p}"`); });
  const dotPatina = groups.flatMap((g, gi) => Array.from({ length: g }, () => patinas[gi]!));
  rows.forEach((r) => {
    if (r.held.length !== len) throw new Error(`GradeStrips: "${r.name}" has ${r.held.length} dots for ${len} grades`);
    const n = r.held.filter(Boolean).length;
    if (n !== r.count) throw new Error(`GradeStrips: "${r.name}" fills ${n} dots but the timeline says ${r.count}`);
  });
  const rowAt = rows.map((r) => at(r.at_phrase));
  for (let i = 1; i < rowAt.length; i++) if (rowAt[i]! < rowAt[i - 1]!) throw new Error(`GradeStrips: "${rows[i]!.at_phrase}" is spoken before "${rows[i - 1]!.at_phrase}"`);
  if (rowAt[0]! > 15) throw new Error(`GradeStrips: the first strip arrives ${rowAt[0]} frames into the shot; the chart would stand empty`);
  const markAt = mark_missing_at ? at(mark_missing_at) : Infinity;
  const mT = ease(frame, markAt, 12);
  const head = ease(frame, 0, 10);

  const X0 = E.x0 + 24, X1 = E.x1 - 24, W = X1 - X0;
  const countW = 72;                                           // the row's count, right of its strip
  // Gaps between patina groups, in dot pitches. A one-dot group (orange) gets a wider gap on
  // each side, or its key Cent overlaps its neighbour's (seen on the first draft-3 still).
  const gaps = groups.slice(0, -1).map((g, gi) => 0.42 + (g === 1 || groups[gi + 1] === 1 ? 0.6 : 0));
  const pitch = (W - countW - 12) / (len + gaps.reduce((a, b) => a + b, 0));
  const d = Math.floor(pitch * 0.8);
  const dotX: number[] = [];                                   // centre of each dot along a strip
  let gx = X0;
  groups.forEach((g, gi) => { for (let j = 0; j < g; j++) dotX.push(gx + pitch * (j + 0.5)); gx += pitch * (g + (gaps[gi] ?? 0)); });
  const groupCx = groups.map((g, gi) => { const first = groups.slice(0, gi).reduce((a, b) => a + b, 0); return (dotX[first]! + dotX[first + g - 1]!) / 2; });
  const minKeyGap = Math.min(...groupCx.slice(1).map((x, i) => x - groupCx[i]!));
  const titleY = E.y0 + 30;
  const keyY = titleY + (subtitle ? 150 : 96) + 14, keyD = Math.min(104, Math.floor(minKeyGap - 10));
  const rowsY0 = keyY + keyD + 34, rowsY1 = 1320;
  const rowH = (rowsY1 - rowsY0) / rows.length;

  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <div style={{ position: "absolute", left: X0, top: titleY, width: W, opacity: head, transform: `translateY(${(1 - head) * 10}px)` }}>
        <SafeText role="display" fontSize={68} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
        {subtitle ? <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim}>{subtitle}</SafeText> : null}
      </div>
      <Imagery>
        {keys.map((n, gi) => (
          <div key={n} style={{ position: "absolute", left: groupCx[gi]! - keyD / 2, top: keyY, opacity: ease(frame, 2 + gi * 3, 10) }}>
            <Coin n={n} d={keyD} />
          </div>
        ))}
      </Imagery>
      {rows.map((r, ri) => {
        const y0 = rowsY0 + ri * rowH;
        const t0 = rowAt[ri]!;
        const lt = ease(frame, t0, 10);
        const stripY = y0 + 66 + d / 2;
        const shown = Math.min(len, Math.max(0, Math.floor((frame - t0) / 1.5)));
        const countT = ease(frame, t0 + len * 1.5, 8);
        return (
          <React.Fragment key={r.name}>
            {r.apart ? <div style={{ position: "absolute", left: X0, top: y0 - 14, width: W, height: 2, background: COLOR.rule, opacity: lt }} /> : null}
            <div style={{ position: "absolute", left: X0, top: y0, width: W, opacity: lt, display: "flex", alignItems: "baseline", gap: 18 }}>
              <SafeText role="label" fontSize={44} maxLines={1} color={r.apart ? COLOR.inkDim : COLOR.ink} style={{ fontFamily: TYPE.body, fontWeight: 700, whiteSpace: "nowrap" }}>{r.name}</SafeText>
              <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.inkDim} style={{ fontFamily: TYPE.body, whiteSpace: "nowrap" }}>{`${r.cents.toLocaleString("en-US")} Cents`}</SafeText>
            </div>
            {r.held.map((h, i) => {
              const t = i < shown ? 1 : 0;
              const ringMark = !h && mT > 0;
              return (
                <div key={i} style={{ position: "absolute", left: dotX[i]! - d / 2, top: stripY - d / 2, width: d, height: d, borderRadius: "50%",
                                      boxSizing: "border-box", opacity: t * (r.apart ? 0.75 : 1),
                                      background: h ? PATINA_DOT[dotPatina[i]!] : "transparent",
                                      border: h ? (dotPatina[i] === "obsidian" ? `2px solid ${COLOR.inkDim}` : "none")
                                                : `${3 + 2 * mT}px solid ${ringMark ? mixToAccent(mT) : COLOR.inkDim}`,
                                      boxShadow: ringMark ? `0 0 ${22 * mT}px ${COLOR.accent}` : "none" }} />
              );
            })}
            <div style={{ position: "absolute", left: X1 - countW, top: stripY - 30, width: countW, textAlign: "right", opacity: countT }}>
              <SafeText role="label" fontSize={48} maxLines={1} color={r.count === len ? COLOR.accent : COLOR.ink}
                        style={{ fontFamily: TYPE.mono, fontWeight: 700, textAlign: "right" }}>{String(r.count)}</SafeText>
            </div>
          </React.Fragment>
        );
      })}
    </div>
  );
};

/**
 * `CentTiers`: the Wall's Cents sorted into rows by a measured count (here, visual
 * traits per Cent), most at the top, each row a line of real Cents: a histogram
 * made of the collection itself. Rows arrive top-down at the start of the shot.
 * The readout band carries the figures, each on its phrase. The timeline declares
 * the total; a Cent placed twice, or a total that disagrees, stops the render.
 */
type Tier = { label: string; cents: number[] };
type TierRead = { at_phrase: string; readout: string; caption: string };
export const CentTiers: React.FC<Anchored & { title: string; subtitle?: string; tiers: Tier[]; total: number; reads: TierRead[] }> = (props) => {
  const { title, subtitle, tiers, total, reads } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props);
  const all = tiers.flatMap((t) => t.cents);
  if (all.length !== total) throw new Error(`CentTiers: the tiers hold ${all.length} Cents but the timeline declares ${total}`);
  if (new Set(all).size !== all.length) throw new Error("CentTiers: a Cent stands in two tiers");
  const readAt = reads.map((r) => at(r.at_phrase));
  for (let i = 1; i < readAt.length; i++) if (readAt[i]! <= readAt[i - 1]!) throw new Error("CentTiers: readouts must come in spoken order");
  let cur = -1;
  readAt.forEach((f, i) => { if (frame >= f) cur = i; });
  const X0 = E.x0 + 24, X1 = E.x1 - 24, W = X1 - X0;
  const titleY = E.y0 + 30;
  const band = { y0: 1150, y1: 1330 };
  const y0 = titleY + (subtitle ? 150 : 96) + 30, y1 = band.y0 - 24;
  const labelW = 64;
  const maxN = Math.max(...tiers.map((t) => t.cents.length));
  const rowH = (y1 - y0) / tiers.length;
  const pitch = Math.min((W - labelW - 12) / maxN, rowH);
  const d = Math.floor(pitch * 0.9);
  const head = ease(frame, 0, 10);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <div style={{ position: "absolute", left: X0, top: titleY, width: W, opacity: head, transform: `translateY(${(1 - head) * 10}px)` }}>
        <SafeText role="display" fontSize={68} maxLines={1} style={{ fontWeight: 700, letterSpacing: -1 }}>{title}</SafeText>
        {subtitle ? <SafeText role="body" fontSize={46} maxLines={1} color={COLOR.inkDim}>{subtitle}</SafeText> : null}
      </div>
      {tiers.map((t, ri) => {
        const cy = y0 + rowH * (ri + 0.5);
        const lt = ease(frame, 2 + ri * 4, 10);
        return (
          <React.Fragment key={t.label}>
            <div style={{ position: "absolute", left: X0, top: cy - 30, width: labelW, opacity: lt }}>
              <SafeText role="label" fontSize={48} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{t.label}</SafeText>
            </div>
            <Imagery>
              {t.cents.map((n, i) => {
                const ct = ease(frame, 4 + ri * 4 + i * 2, 10);
                return (
                  <div key={n} style={{ position: "absolute", left: X0 + labelW + 12 + pitch * i + (pitch - d) / 2, top: cy - d / 2,
                                        opacity: ct, transform: `scale(${0.8 + 0.2 * ct})` }}>
                    <Coin n={n} d={d} />
                  </div>
                );
              })}
            </Imagery>
          </React.Fragment>
        );
      })}
      {cur >= 0 ? (
        <div key={cur} style={{ position: "absolute", left: X0, top: band.y0, width: W, opacity: ease(frame, readAt[cur]!, 8) }}>
          <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{reads[cur]!.readout}</SafeText>
          <SafeText role="body" fontSize={48} maxLines={1}>{reads[cur]!.caption}</SafeText>
        </div>
      ) : null}
    </div>
  );
};

const mixToAccent = (t: number) => {
  const hex = (c: string) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16));
  const a = hex(COLOR.inkDim), b = hex(COLOR.accent);
  return `rgb(${a.map((v, i) => Math.round(v + (b[i]! - v) * t)).join(",")})`;
};

export const CHARACTER = { PatinaLadder, GradeStrips, CentTiers } as const;
for (const C of Object.values(CHARACTER)) (C as any).wantsAlignment = true;
