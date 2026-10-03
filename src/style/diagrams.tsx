import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { COLOR, MIN_FONT_PX, REGIONS, TYPE } from "./tokens";
import { activeIndex, resolveStates, stateProgress, type NarrationState } from "../lib/narration";
import type { Alignment } from "../lib/timeline";

const D = REGIONS.diagram;
const W = D.x1 - D.x0;
const H = D.y1 - D.y0;

/**
 * Every diagram draws inside this frame. The SVG viewBox IS the diagram region,
 * so a label cannot escape the safe area geometrically — which matters, because
 * SVG text is not measured by SafeText and would otherwise bypass the bounds
 * gate the way a raw styled div once did.
 */
const Frame: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ position: "absolute", left: D.x0, top: D.y0, width: W, height: H }}>
    <svg viewBox={`0 0 ${W} ${H}`} width={W} height={H} style={{ overflow: "visible" }}>
      {children}
    </svg>
  </div>
);

/**
 * SVG label at or above the legibility floor, wrapped to a width.
 *
 * SVG <text> does not wrap, so a long caption runs straight out of the diagram
 * region — the same escape route the raw styled div used. Wrapping here, to the
 * width the caller has, keeps diagram text inside the frame by construction.
 */
const CHAR_W = 0.52; // mean advance per character as a fraction of font size

const Label: React.FC<{
  x: number; y: number; children: string; size?: number; fill?: string;
  anchor?: "start" | "middle" | "end"; mono?: boolean; dim?: boolean; wrap?: number;
}> = ({ x, y, children, size = MIN_FONT_PX.label, fill, anchor = "middle", mono, dim, wrap }) => {
  if (size < MIN_FONT_PX.label)
    throw new Error(`diagram label "${children}" at ${size}px is below the ${MIN_FONT_PX.label}px floor`);
  const maxChars = Math.max(8, Math.floor((wrap ?? W) / (size * CHAR_W)));
  const lines: string[] = [];
  let cur = "";
  for (const word of children.split(/\s+/)) {
    if (!cur) { cur = word; continue; }
    if ((cur + " " + word).length <= maxChars) cur += " " + word;
    else { lines.push(cur); cur = word; }
  }
  if (cur) lines.push(cur);
  if (lines.length > 3)
    throw new Error(`diagram label "${children.slice(0, 40)}" wraps to ${lines.length} lines at ${size}px — shorten it`);
  // Wrapping cannot break a single word. One too wide for its column overflows
  // into the neighbouring label instead, which reads as two labels run together.
  const longest = children.split(/\s+/).reduce((a, b) => (a.length > b.length ? a : b), "");
  if (wrap && longest.length * size * CHAR_W > wrap)
    throw new Error(
      `diagram label "${children.slice(0, 40)}": the word "${longest}" is wider than its ${Math.round(wrap)}px column — it would overlap the next label`
    );
  return (
    <text x={x} y={y} textAnchor={anchor} fontSize={size}
          fontFamily={mono ? TYPE.mono : TYPE.body}
          fill={fill ?? (dim ? COLOR.inkDim : COLOR.ink)}>
      {lines.map((l, k) => (
        <tspan key={k} x={x} dy={k === 0 ? 0 : size * 1.22}>{l}</tspan>
      ))}
    </text>
  );
};

type DiagramProps<T> = { states: NarrationState<T>[]; alignment: Alignment; shotStartFrame: number };

function useStates<T>({ states, alignment, shotStartFrame }: DiagramProps<T>) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const resolved = resolveStates(states, alignment, fps, shotStartFrame);
  return { i: activeIndex(resolved, frame), p: stateProgress(resolved, frame, fps), resolved, frame };
}

/* ------------------------------------------------------------------ chain */

export type ChainState = { active: number; caption: string };

/**
 * A sequence that PRODUCES things. Nodes light as the narration reaches them and
 * stay lit, so the finished state shows the whole chain rather than a travelling
 * highlight — the difference between explaining a process and animating one.
 */
export const ProcessChain: React.FC<DiagramProps<ChainState> & { nodes: string[] }> = (props) => {
  const { i, p } = useStates(props);
  const st = props.states[i]!;
  const n = props.nodes.length;
  const gap = H * 0.155;
  const y0 = H * 0.5 - ((n - 1) * H * 0.155) / 2 - H * 0.04;
  return (
    <Frame>
      {props.nodes.map((label, k) => {
        const y = y0 + k * gap;
        const on = k <= st.active;
        const fresh = k === st.active ? p : 1;
        return (
          <g key={label}>
            {k > 0 ? (
              <line x1={W * 0.16} y1={y - gap + 26} x2={W * 0.16} y2={y - 26}
                    stroke={k <= st.active ? COLOR.accent : COLOR.rule} strokeWidth={3} />
            ) : null}
            <circle cx={W * 0.16} cy={y} r={on ? 20 + 6 * fresh : 16}
                    fill={on ? COLOR.accent : "none"} stroke={on ? COLOR.accent : COLOR.rule} strokeWidth={3} />
            <Label x={W * 0.16 + 46} y={y + 8} anchor="start" size={44} wrap={W * 0.78}
                   fill={on ? COLOR.ink : COLOR.inkDim}>{label}</Label>
          </g>
        );
      })}
      <Label x={W / 2} y={y0 + (n - 1) * gap + 104} size={42} dim wrap={W * 0.9}>{st.caption}</Label>
    </Frame>
  );
};

/* ------------------------------------------------------------- distinction */

export type DistinctionState = { linked: boolean; caption: string; emphasise?: number };

/**
 * Two or three things the source holds APART. The link between them is the
 * drawn element, so losing it is visible rather than merely stated — built for
 * the failure mode where a film collapses a distinction the essay makes.
 */
export const Distinction: React.FC<DiagramProps<DistinctionState> & { items: string[]; vertical?: boolean }> = (props) => {
  const { i, p } = useStates(props);
  const st = props.states[i]!;
  const n = props.items.length;
  const vert = props.vertical ?? false;
  const r = vert ? 34 : Math.min(62, W / (n + 1) / 2 - 12);
  // Horizontal reads as a row of peers; vertical gives each label the full
  // width, which is the only way long phrases fit at the legibility floor.
  const cx = (k: number) => (vert ? 86 : (W / (n + 1)) * (k + 1));
  const cyV = (k: number) => H * 0.16 + k * (H * 0.2);
  const cy = H * 0.34;
  if (vert) {
    return (
      <Frame>
        {props.items.map((label, k) => (
          <g key={label}>
            {k > 0 ? (
              <line x1={86} y1={cyV(k - 1) + r} x2={86} y2={cyV(k) - r}
                    stroke={st.linked ? COLOR.accent : COLOR.rule} strokeWidth={4}
                    strokeDasharray={st.linked ? undefined : "2 16"} />
            ) : null}
            <circle cx={86} cy={cyV(k)} r={r} fill="none"
                    stroke={st.emphasise === k ? COLOR.accent : COLOR.ink}
                    strokeWidth={st.emphasise === k ? 5 : 3} />
            <Label x={86 + r + 34} y={cyV(k) + 12} anchor="start" size={48} wrap={W - 86 - r - 50}
                   fill={st.emphasise === k ? COLOR.accent : COLOR.ink}>{label}</Label>
          </g>
        ))}
        <Label x={W / 2} y={cyV(n - 1) + 215} size={44} dim wrap={W * 0.92}>{st.caption}</Label>
      </Frame>
    );
  }
  return (
    <Frame>
      {props.items.map((_, k) =>
        k === 0 ? null : (
          <line key={`l${k}`} x1={cx(k - 1) + r} y1={cy} x2={cx(k) - r} y2={cy}
                stroke={st.linked ? COLOR.accent : COLOR.rule} strokeWidth={4}
                strokeDasharray={st.linked ? undefined : "2 16"}
                strokeOpacity={st.linked ? 1 : 0.45 + 0.2 * p} />
        )
      )}
      {props.items.map((label, k) => {
        const em = st.emphasise === k;
        return (
          <g key={label}>
            <circle cx={cx(k)} cy={cy} r={r} fill="none"
                    stroke={em ? COLOR.accent : COLOR.ink} strokeWidth={em ? 5 : 3} />
            <Label x={cx(k)} y={cy + r + 52} size={42} wrap={W / (n + 1) * 1.15} fill={em ? COLOR.accent : COLOR.ink}>{label}</Label>
          </g>
        );
      })}
      <Label x={W / 2} y={cy + r + 190} size={44} dim wrap={W * 0.92}>{st.caption}</Label>
      
    </Frame>
  );
};

/* ------------------------------------------------------------------ field */

export type FieldState = { markedVisible: boolean; scanned: number; caption: string; readout: string };

/**
 * A population being scanned, with a readout. Generalises the previous film's
 * marketplace/exchange diagram: a grid of ordinary items, one of them marked,
 * and a scan that may or may not single it out. The readout is driven by the
 * same state as the grid, so it cannot drift away from what is drawn.
 */
export const FieldScan: React.FC<DiagramProps<FieldState> & { cols?: number; rows?: number; markedFraction?: number }> = (
  props
) => {
  const { i, p } = useStates(props);
  const st = props.states[i]!;
  const cols = props.cols ?? 9, rows = props.rows ?? 7;
  const markedFraction = props.markedFraction ?? 0.1;
  const padX = 40, top = 30;
  const cw = (W - padX * 2) / cols, ch = (H * 0.62) / rows;
  const scanY = top + (H * 0.62) * Math.min(1, st.scanned + (p * 0.0));
  return (
    <Frame>
      {Array.from({ length: cols * rows }).map((_, k) => {
        const c = k % cols, r = Math.floor(k / cols);
        const x = padX + cw * (c + 0.5), y = top + ch * (r + 0.5);
        // Deterministic pseudo-scatter so the marked tenth is spread through the
        // field rather than clustered, and identical on every render.
        const isMarked = ((k * 2654435761) % 997) / 997 < markedFraction;
        const passed = y <= scanY;
        const lit = isMarked && st.markedVisible && passed;
        return (
          <circle key={k} cx={x} cy={y} r={lit ? 13 : 9}
                  fill={lit ? COLOR.accent : passed ? COLOR.inkDim : COLOR.rule}
                  fillOpacity={lit ? 1 : passed ? 0.75 : 1} />
        );
      })}
      <line x1={padX - 10} y1={scanY} x2={W - padX + 10} y2={scanY}
            stroke={COLOR.ink} strokeWidth={2} strokeOpacity={0.55} />
      <Label x={padX} y={H * 0.74} anchor="start" size={42} wrap={W - padX * 2} mono
             fill={st.markedVisible ? COLOR.accent : COLOR.inkDim}>{st.readout}</Label>
      <Label x={W / 2} y={H * 0.86} size={44} dim wrap={W * 0.92}>{st.caption}</Label>
    </Frame>
  );
};

/* ----------------------------------------------------------- simultaneity */

export type SimulState = { present: boolean; caption: string };

/**
 * N things a single object IS AT ONCE. Built for a claim a sequence diagram
 * cannot carry: that something is all of these and none of them. The second
 * state withdraws the spokes without removing the labels, so "none of them"
 * reads as a retraction of the claim rather than as things disappearing.
 */
export const Simultaneity: React.FC<DiagramProps<SimulState> & { items: string[]; centre: string }> = (props) => {
  const { i, p } = useStates(props);
  const st = props.states[i]!;
  const n = props.items.length;
  const cxC = W - 86, cyC = H * 0.42;
  const top = H * 0.12, step = (H * 0.66) / Math.max(1, n - 1);
  return (
    <Frame>
      {props.items.map((label, k) => {
        const y = top + k * step;
        return (
          <g key={label}>
            <line x1={396} y1={y - 6} x2={cxC - 54} y2={cyC}
                  stroke={st.present ? COLOR.accent : COLOR.rule} strokeWidth={2}
                  strokeOpacity={st.present ? 0.85 : 0.3}
                  strokeDasharray={st.present ? undefined : "2 14"} />
            <Label x={16} y={y} anchor="start" size={42} wrap={372}
                   fill={st.present ? COLOR.ink : COLOR.inkDim}>{label}</Label>
          </g>
        );
      })}
      <circle cx={cxC} cy={cyC} r={52} fill="none"
              stroke={st.present ? COLOR.accent : COLOR.inkDim} strokeWidth={4}
              strokeOpacity={st.present ? 1 : 0.5 + 0.3 * p} />
      <Label x={cxC} y={cyC + 14} size={42} fill={st.present ? COLOR.accent : COLOR.inkDim}>{props.centre}</Label>
      <Label x={W / 2} y={H * 0.92} size={44} dim wrap={W * 0.92}>{st.caption}</Label>
    </Frame>
  );
};

export const DIAGRAMS = { ProcessChain, Distinction, FieldScan, Simultaneity } as const;
export type DiagramName = keyof typeof DIAGRAMS;
