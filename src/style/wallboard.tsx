import React from "react";
import { continueRender, delayRender, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { useShotFade, EASE } from "./motion";
import { COLOR, SAFE, TYPE } from "./tokens";
import { Imagery, SafeText } from "./Safe";
import { findPhrase, type Alignment } from "../lib/timeline";

/**
 * WallBoard: a claimed Collector Wall rebuilt from its data, so the camera can
 * scroll it and land on any Cent or badge at full sharpness. A screenshot goes
 * soft past ~1.5x, can only show what fit on one screen, and needs every zoom
 * box measured by hand; here every element is placed by layoutWall(), so a
 * target is named ({cent: 3640}, {badge: "Wheat"}) and its box is known exactly.
 *
 * It draws the card as cents.vision/collectors.html does (signature, name,
 * count, mosaic, trait tags, Set badges, full patinas held, meta badges) with
 * the "View collection" grid of every Cent opened beneath it. Badge text is the
 * card's own rendered text; the wallet line is never drawn.
 *
 * Data: public/walls/<slug>.json, written by pipeline/wall_board.py.
 */

export type Board = {
  name: string; signature: number; count: number; as_of: string;
  mosaic: number[]; cents: number[];
  badges: { tags: string[]; sets: string[]; fulls: string[]; meta: string[] };
  groups: Record<string, number[] | Record<string, number[]>>;
};

type Box = [number, number, number, number];
type Item =
  | { kind: "cent"; where: "signature" | "mosaic" | "grid"; n: number; box: Box }
  | { kind: "badge"; row: "tags" | "sets" | "fulls" | "meta"; text: string; box: Box }
  | { kind: "text"; text: string; box: Box; size: number; weight?: number; color?: string; align?: "left" | "right" | "center"; underline?: boolean };

export type Target =
  | { top: true }                 // the card at 1:1, top edge in view
  | { card: true }                // the whole card (name to meta badges)
  | { cent: number; in?: "signature" | "mosaic" | "grid" }
  | { badge: string }             // the one badge whose text starts with this
  | { grid_start: true } | { grid_end: true }   // the collection grid at 1:1, first or last row in view
  | { box: Box };

export type Move = { at_phrase?: string; target: Target; until_phrase?: string; mark?: boolean; zoom?: number };
export type Highlight = { at_phrase: string; until_phrase?: string; cents?: number[]; group?: string };
export type Show = "all" | "card" | "grid";
export type Readout = { at_phrase: string; text?: string; count?: { from: number; to: number; until_phrase: string; suffix?: string } };

// ---------- layout (board units; the board is 1000 wide) ----------

const BW = 1000, PAD = 24;
const MAIN_X = 250, MAIN_W = BW - PAD - MAIN_X;
const FONT = "Helvetica, Arial, sans-serif";
const CHAR = 0.56;          // average glyph width / font size, Helvetica; chips get slack on top

const chipW = (text: string, size: number, upper = false) => Math.ceil(text.length * size * (upper ? CHAR * 1.18 : CHAR) + 26);

const SET_STYLE: [RegExp, { color: string; border: string; bg: string; upper?: boolean; weight?: number }][] = [
  [/^Full Spectrum/, { color: "#7a4a00", border: "#c8860a", bg: "#fef3d8", upper: true }],
  [/^Spectrum Set/, { color: "#6a5200", border: "#b89020", bg: "#faf0c0", upper: true }],
  [/^Patina Fulls/, { color: "#0f450f", border: "#2e722e", bg: "#ceebce", upper: true }],
  [/^Patina Sig/, { color: "#1f5a1f", border: "#4e8c4e", bg: "#deeede", upper: true }],
  [/^Patina Set/, { color: "#3d6e3d", border: "#7aaa7a", bg: "#edf5ed", upper: true }],
  [/^Chronicle/, { color: "#3a2b52", border: "#7c5fae", bg: "#efe9f8", weight: 700 }],
  [/^Full Mint/, { color: "#5a3a12", border: "#b8863b", bg: "#f6ecd6", weight: 700 }],
  [/^Full Contamination/, { color: "#2e2208", border: "#5a4410", bg: "#ddcd9f", weight: 700 }],
  [/^Contamination Hoard/, { color: "#423417", border: "#7d6526", bg: "#e8ddc0", weight: 700 }],
  [/^Contamination Set/, { color: "#50432a", border: "#998445", bg: "#efe9d6", weight: 600 }],
  [/^Three Decades/, { color: "#2d2d5e", border: "#6868b0", bg: "#e6e6f5", weight: 600 }],
  [/^All Decades/, { color: "#1f1f4e", border: "#4e4e9c", bg: "#f2f2fb", weight: 700 }],
  [/Decade/, { color: "#1f1f4e", border: "#4e4e9c", bg: "#dcdcf2", weight: 700 }],
];
const setStyle = (t: string) => SET_STYLE.find(([re]) => re.test(t))?.[1] ?? { color: "#333", border: "#999", bg: "#f4f4f4" };
const META_STYLE = (t: string) =>
  t.startsWith("1/1") ? { color: "#b8860b", border: "#b8860b", bg: "white", weight: 700 }
  : t.startsWith("Diamond Hands") ? { color: "#0f5e6e", border: "#4fb8cf", bg: "#eafbfd", weight: 700 }
  : t.startsWith("Mint Keeper") ? { color: "#155a3a", border: "#4caa7a", bg: "#e9f9f0", weight: 700 }
  : null;                     // club, years, patina, 1971, 1969, wheat: plain grey text on the card

const SIZE = { tags: 24, sets: 22, fulls: 24, meta: 26 };

export function layoutWall(b: Board) {
  const items: Item[] = [];
  // Header: signature left, name and count right.
  const sig = 190;
  items.push({ kind: "cent", where: "signature", n: b.signature, box: [PAD + 6, PAD + 10, PAD + 6 + sig, PAD + 10 + sig] });
  items.push({ kind: "text", text: `Signature #${b.signature}`, box: [PAD, PAD + 210, PAD + 202, PAD + 240], size: 26, color: "#777", align: "center" });
  items.push({ kind: "text", text: b.name, box: [MAIN_X, PAD, MAIN_X + MAIN_W - 200, PAD + 54], size: 44, weight: 700, underline: true });
  items.push({ kind: "text", text: `${b.count.toLocaleString("en-US")} ${b.count === 1 ? "CENT" : "CENTS"}`,
               box: [MAIN_X + MAIN_W - 200, PAD + 8, MAIN_X + MAIN_W, PAD + 40], size: 26, weight: 700, align: "right" });
  // Mosaic: 6 across, as the card.
  let y = PAD + 76;
  const mg = 8, ms = Math.floor((MAIN_W - 5 * mg) / 6);
  b.mosaic.forEach((n, i) => {
    const x = MAIN_X + (i % 6) * (ms + mg), yy = y + Math.floor(i / 6) * (ms + mg);
    items.push({ kind: "cent", where: "mosaic", n, box: [x, yy, x + ms, yy + ms] });
  });
  y += Math.ceil(b.mosaic.length / 6) * (ms + mg) + 12;
  // Chip rows flow left to right and wrap inside the main column.
  const flow = (row: "tags" | "sets" | "fulls" | "meta", texts: string[], size: number, upper: (t: string) => boolean, lead?: string) => {
    if (!texts.length) return;
    let x = MAIN_X;
    const h = size + 20, gap = 10;
    if (lead) {
      const w = chipW(lead, size * 0.85, true) - 16;
      items.push({ kind: "text", text: lead, box: [x, y, x + w, y + h], size: size * 0.85, color: "#777" });
      x += w + gap;
    }
    for (const t of texts) {
      const w = chipW(t, size, upper(t));
      if (x + w > MAIN_X + MAIN_W && x > MAIN_X) { x = MAIN_X; y += h + gap; }
      items.push({ kind: "badge", row, text: t, box: [x, y, x + w, y + h] });
      x += w + gap;
    }
    y += h + gap + 4;
  };
  flow("tags", b.badges.tags, SIZE.tags, () => false);
  flow("sets", b.badges.sets, SIZE.sets, (t) => !!setStyle(t).upper);
  flow("fulls", b.badges.fulls, SIZE.fulls, () => false, "FULL PATINAS HELD:");
  flow("meta", b.badges.meta, SIZE.meta, () => false);
  const cardEnd = Math.max(y, PAD + 250) + 8;
  // The opened "View collection" grid: every Cent with its number.
  let gy = cardEnd + 30;
  items.push({ kind: "text", text: `${b.count.toLocaleString("en-US")} ${b.count === 1 ? "CENT" : "CENTS"} in this wall`,
               box: [PAD, gy, BW - PAD, gy + 34], size: 26, color: "#777" });
  gy += 50;
  const cols = 6, gg = 14, gs = Math.floor((BW - 2 * PAD - (cols - 1) * gg) / cols), rowH = gs + 40;
  const gridTop = gy;
  b.cents.forEach((n, i) => {
    const x = PAD + (i % cols) * (gs + gg), yy = gy + Math.floor(i / cols) * rowH;
    items.push({ kind: "cent", where: "grid", n, box: [x, yy, x + gs, yy + gs] });
    items.push({ kind: "text", text: `#${n}`, box: [x, yy + gs + 4, x + gs, yy + gs + 34], size: 24, color: "#777", align: "center" });
  });
  const gridEnd = gy + Math.ceil(b.cents.length / cols) * rowH;
  return { items, cardEnd, gridTop, gridEnd, height: gridEnd + PAD };
}

// ---------- data ----------

const cache = new Map<string, Board>();
function useBoard(slug: string): Board | null {
  const [b, setB] = React.useState<Board | null>(cache.get(slug) ?? null);
  const [handle] = React.useState(() => (cache.has(slug) ? null : delayRender(`wall board ${slug}`)));
  React.useEffect(() => {
    if (b) return;
    fetch(staticFile(`walls/${slug}.json`))
      .then((r) => { if (!r.ok) throw new Error(`walls/${slug}.json: HTTP ${r.status}; run pipeline/wall_board.py`); return r.json(); })
      .then((j: Board) => { cache.set(slug, j); setB(j); if (handle !== null) continueRender(handle); })
      .catch((e) => { throw e; });
  }, [slug]);
  return b;
}

// ---------- the shot ----------

type Anchored = { alignment: Alignment; shotStartFrame: number };

export const WallBoard: React.FC<Anchored & {
  wall: string; moves?: Move[]; highlights?: Highlight[]; readout?: Readout;
  /** "card": the Wall card alone, as collectors.html shows it closed. "grid": only the opened
   *  "View collection" rows, for singling out Cents. Default "all" draws both. */
  show?: Show;
}> = (props) => {
  const b = useBoard(props.wall);
  if (!b) return null;
  return <WallBoardInner {...props} board={b} />;
};

const WallBoardInner: React.FC<Anchored & { board: Board; moves?: Move[]; highlights?: Highlight[]; readout?: Readout; show?: Show }> = (props) => {
  const { board: b, moves = [], highlights = [], readout, alignment, shotStartFrame, show = "all" } = props;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useShotFade();
  const at = (phrase: string) => {
    const f = Math.round(findPhrase(alignment, phrase).start * fps) - shotStartFrame;
    if (f < 0) throw new Error(`WallBoard: "${phrase}" is spoken before this shot starts`);
    return f;
  };
  const L = React.useMemo(() => layoutWall(b), [b]);
  const VIEW = { x0: 40, x1: 1040, y0: SAFE.essential.y0, y1: readout ? 1130 : 1330 };
  const VW = VIEW.x1 - VIEW.x0, VH = VIEW.y1 - VIEW.y0;

  const resolve = (t: Target): { box: Box; fit: boolean } => {
    if ("top" in t) return { box: [0, 0, BW, VH], fit: true };
    if ("card" in t) return { box: [0, 0, BW, L.cardEnd], fit: true };
    if ("grid_start" in t) return { box: [0, L.gridTop - 60, BW, L.gridTop - 60 + VH], fit: true };
    if ("grid_end" in t) return { box: [0, L.gridEnd - VH + 20, BW, L.gridEnd + 20], fit: true };
    if ("box" in t) return { box: t.box, fit: true };
    if ("cent" in t) {
      const where = t.in ?? "grid";
      const hit = L.items.filter((i) => i.kind === "cent" && i.n === t.cent && i.where === where);
      if (hit.length !== 1) throw new Error(`WallBoard: Cent #${t.cent} is not in the ${where} of ${b.name}'s Wall`);
      const [x0, y0, x1, y1] = hit[0]!.box, p = (x1 - x0) * 0.35;
      return { box: [x0 - p, y0 - p, x1 + p, y1 + p], fit: true };
    }
    const hits = L.items.filter((i) => i.kind === "badge" && i.text.startsWith(t.badge));
    if (hits.length !== 1)
      throw new Error(`WallBoard: badge "${t.badge}" matches ${hits.length} badges on ${b.name}'s Wall`);
    const [x0, y0, x1, y1] = hits[0]!.box;
    return { box: [x0 - 40, y0 - 60, x1 + 40, y1 + 60], fit: true };
  };
  const cam = (box: Box, maxK: number) => {
    const [x0, y0, x1, y1] = box;
    const k = Math.min(VW / (x1 - x0), VH / (y1 - y0), maxK);
    return { k, cx: (x0 + x1) / 2, cy: (y0 + y1) / 2 };
  };

  // Camera: hold the top of the card (or of the rows), then each move eases (or, with until_phrase, pans linearly) to its target.
  let c = show === "grid" ? cam(resolve({ grid_start: true }).box, 1) : cam([0, 0, BW, VH], 1);
  let mark: { box: Box; t: number } | null = null;
  let last = -1;
  for (const [i, m] of moves.entries()) {
    const f0 = m.at_phrase ? at(m.at_phrase) : 0;
    if (f0 < last) throw new Error(`WallBoard: move ${i} is out of spoken order`);
    last = f0;
    if (frame < f0) break;
    const f1 = m.until_phrase ? at(m.until_phrase) : f0 + 18;
    if (f1 <= f0) throw new Error(`WallBoard: move ${i} ends before it starts`);
    const r = resolve(m.target), to = cam(r.box, m.zoom ?? 2.6);
    const t = interpolate(frame, [f0, f1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp",
                                                    easing: m.until_phrase ? EASE.linear : EASE.inOut });
    c = { k: c.k + (to.k - c.k) * t, cx: c.cx + (to.cx - c.cx) * t, cy: c.cy + (to.cy - c.cy) * t };
    const tb = "badge" in m.target ? L.items.find((i) => i.kind === "badge" && i.text.startsWith((m.target as any).badge))!.box
             : "cent" in m.target ? (() => { const [x0, y0, x1, y1] = r.box, p = (x1 - x0) * 0.35 / 1.7; return [x0 + p, y0 + p, x1 - p, y1 - p] as Box; })()
             : r.box;
    mark = m.mark ? { box: tb, t: interpolate(frame, [f1 - 4, f1 + 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) } : null;
  }
  const ox = VW / 2 - c.cx * c.k, oy = VH / 2 - c.cy * c.k;
  const S = (v: number) => v * c.k;

  // Highlights: everything else on the board dims; the chosen Cents get a copper ring.
  let lit: Set<number> | null = null, litT = 0;
  for (const h of highlights) {
    const f0 = at(h.at_phrase), f1 = h.until_phrase ? at(h.until_phrase) : Infinity;
    if (frame < f0 || frame >= f1) continue;
    const g = h.group ? b.groups[h.group] : undefined;
    if (h.group && !Array.isArray(g)) throw new Error(`WallBoard: no Cent group "${h.group}" (have ${Object.keys(b.groups).join(", ")})`);
    const ns = h.cents ?? (g as number[]);
    for (const n of ns) if (!b.cents.includes(n)) throw new Error(`WallBoard: highlight Cent #${n} is not on ${b.name}'s Wall`);
    lit = new Set(ns);
    litT = Math.min(interpolate(frame, [f0, f0 + 12], [0, 1], { extrapolateRight: "clamp" }),
                    f1 === Infinity ? 1 : interpolate(frame, [f1 - 8, f1], [1, 0], { extrapolateLeft: "clamp" }));
  }

  // The card ends at cardEnd; the opened collection rows sit below it.
  const sheetY0 = show === "grid" ? L.cardEnd : 0, sheetY1 = show === "card" ? L.cardEnd : L.height;
  const inPart = (bx: Box) => show === "all" || (show === "card" ? bx[1] < L.cardEnd : bx[1] >= L.cardEnd);
  const vis = (bx: Box) => {          // cull what the camera cannot see
    const x0 = ox + S(bx[0]), y0 = oy + S(bx[1]), x1 = ox + S(bx[2]), y1 = oy + S(bx[3]);
    return x1 > -50 && x0 < VW + 50 && y1 > -50 && y0 < VH + 50;
  };

  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade }}>
      <Imagery>
        <div style={{ position: "absolute", left: VIEW.x0, top: VIEW.y0, width: VW, height: VH, overflow: "hidden", borderRadius: 18, background: "#ececec" }}>
          <div style={{ position: "absolute", left: ox, top: oy + S(sheetY0), width: S(BW), height: S(sheetY1 - sheetY0), background: "white",
                        border: `${Math.max(1, S(1.5))}px solid #d7d7d7`, boxSizing: "border-box" }} />
          {L.items.map((it, i) => {
            if (!vis(it.box) || !inPart(it.box)) return null;
            const [x0, y0, x1, y1] = it.box;
            const st: React.CSSProperties = { position: "absolute", left: ox + S(x0), top: oy + S(y0), width: S(x1 - x0), height: S(y1 - y0) };
            if (it.kind === "cent") {
              const on = lit?.has(it.n);
              const dim = lit && !on && it.where !== "signature" ? 1 - 0.75 * litT : 1;
              return (
                <div key={i} style={{ ...st, opacity: dim }}>
                  <Img src={staticFile(`cents/${it.n}.webp`)} style={{ width: "100%", height: "100%" }} />
                  {on ? <div style={{ position: "absolute", inset: -S(5), borderRadius: "50%", border: `${S(5)}px solid ${COLOR.accent}`, opacity: litT }} /> : null}
                </div>
              );
            }
            if (it.kind === "text") {
              return (
                <div key={i} style={{ ...st, fontFamily: FONT, fontSize: S(it.size), fontWeight: it.weight ?? 400, color: it.color ?? "#111",
                                      textAlign: it.align ?? "left", whiteSpace: "nowrap", lineHeight: `${S(y1 - y0)}px`,
                                      textDecoration: it.underline ? "underline" : "none", opacity: lit ? 1 - 0.6 * litT : 1 }}>{it.text}</div>
              );
            }
            const size = SIZE[it.row];
            const s = it.row === "sets" ? setStyle(it.text)
                    : it.row === "fulls" || (it.row === "tags" && it.text.startsWith("Full x")) ? { color: "#1f5e3a", border: "#1f5e3a", bg: "#eaf5ee", weight: 600 }
                    : it.row === "meta" ? META_STYLE(it.text)
                    : { color: "#111", border: "#d7d7d7", bg: "white" };
            return (
              <div key={i} style={{ ...st, fontFamily: FONT, fontSize: S(size), display: "flex", alignItems: "center",
                                    justifyContent: s ? "center" : "flex-start", whiteSpace: "nowrap",
                                    color: s ? s.color : "#777", background: s ? s.bg : "transparent",
                                    border: s ? `${Math.max(1, S(1.5))}px solid ${s.border}` : "none", boxSizing: "border-box",
                                    fontWeight: (s as any)?.weight ?? (it.row === "sets" ? 600 : 400),
                                    textTransform: it.row === "sets" && (s as any).upper ? "uppercase" : "none",
                                    letterSpacing: it.row === "sets" && (s as any).upper ? S(1) : 0,
                                    opacity: lit ? 1 - 0.6 * litT : 1 }}>{it.text}</div>
            );
          })}
          {mark && mark.t > 0 ? (
            <div style={{ position: "absolute", left: ox + S(mark.box[0]) - 12, top: oy + S(mark.box[1]) - 12,
                          width: S(mark.box[2] - mark.box[0]) + 24, height: S(mark.box[3] - mark.box[1]) + 24,
                          border: `5px solid ${COLOR.accent}`, borderRadius: 14, opacity: mark.t }} />
          ) : null}
        </div>
      </Imagery>
      {readout ? <ReadoutBand r={readout} at={at} frame={frame} /> : null}
    </div>
  );
};

const ReadoutBand: React.FC<{ r: Readout; at: (p: string) => number; frame: number }> = ({ r, at, frame }) => {
  const f0 = at(r.at_phrase);
  const op = interpolate(frame, [f0, f0 + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  let text = r.text ?? "";
  if (r.count) {
    const f1 = at(r.count.until_phrase);
    const v = Math.round(interpolate(frame, [f0, f1], [r.count.from, r.count.to], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
    text = `${v.toLocaleString("en-US")}${r.count.suffix ?? ""}`;
  }
  return (
    <div style={{ position: "absolute", left: SAFE.essential.x0 + 24, top: 1150, width: SAFE.essential.x1 - SAFE.essential.x0 - 48, opacity: op }}>
      <SafeText role="display" fontSize={84} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{text}</SafeText>
    </div>
  );
};

(WallBoard as any).wantsAlignment = true;
