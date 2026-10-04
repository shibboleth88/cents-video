import React, { createContext, useContext, useLayoutEffect, useRef } from "react";
import { cancelRender, useCurrentScale } from "remotion";
import { COLOR, MIN_FONT_PX, REGIONS, SAFE, TYPE, type RegionName } from "./tokens";

/**
 * "essential" renders text layers only, on black. The safe-area gate measures
 * THAT export in pixels, so the check is independent of the component that
 * claims to be laying things out correctly.
 */
export type RenderMode = "full" | "essential";
export const ModeCtx = createContext<RenderMode>("full");
export const useMode = () => useContext(ModeCtx);

/** Imagery hides itself in essential mode so the pixel gate sees text alone. */
export const Imagery: React.FC<{ children: React.ReactNode }> = ({ children }) =>
  useMode() === "essential" ? null : <>{children}</>;

const box = (r: RegionName) => {
  const { x0, y0, x1, y1 } = REGIONS[r];
  return { position: "absolute" as const, left: x0, top: y0, width: x1 - x0, height: y1 - y0 };
};

export const Region: React.FC<{
  region: RegionName;
  align?: "start" | "center" | "end";
  justify?: "start" | "center" | "end";
  children: React.ReactNode;
}> = ({ region, align = "start", justify = "start", children }) => (
  <div style={{ ...box(region), display: "flex", flexDirection: "column", alignItems: align, justifyContent: justify }}>
    {children}
  </div>
);

/**
 * Text that refuses to be illegible or out of bounds. Violations CANCEL the
 * render with a message naming the offending string — the fix is a shorter
 * label or a split sequence, never a smaller film.
 */
export const SafeText: React.FC<{
  children: string;
  role?: keyof typeof MIN_FONT_PX;
  essential?: boolean;
  fontSize?: number;
  color?: string;
  maxLines?: number;
  style?: React.CSSProperties;
  /** Per-word opacity. The full string is still laid out and measured, so the
   *  bounds gate sees the final text and nothing reflows as words appear. */
  wordOpacity?: number[];
}> = ({ children, role = "body", essential = true, fontSize, color, maxLines = 3, style, wordOpacity }) => {
  const ref = useRef<HTMLDivElement>(null);
  const scale = useCurrentScale();
  const min = MIN_FONT_PX[role];
  const size = fontSize ?? min;

  if (size < min)
    cancelRender(
      `LEGIBILITY: "${children.slice(0, 48)}" set at ${size}px, below the ${role} floor of ${min}px. Shorten the text instead of shrinking it.`
    );

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el || !essential) return;
    // Measure against the canvas root, not offsetParent: nested flex and
    // transformed wrappers make offsetParent an unreliable origin, and a wrong
    // origin makes this gate report violations that are not there (and, worse,
    // miss ones that are).
    const root = el.closest("[data-canvas-root]");
    if (!root) cancelRender("SAFE AREA: no [data-canvas-root] ancestor — the gate cannot measure.");
    const r = el.getBoundingClientRect();
    const rr = (root as HTMLElement).getBoundingClientRect();
    if (r.width === 0 || r.height === 0)
      cancelRender(`SAFE AREA: "${children.slice(0, 48)}" measured 0x0 — nothing was laid out, so a pass here would be meaningless.`);
    const x0 = (r.left - rr.left) / scale;
    const y0 = (r.top - rr.top) / scale;
    const x1 = x0 + r.width / scale;
    const y1 = y0 + r.height / scale;
    const E = SAFE.essential;
    if (x0 < E.x0 || y0 < E.y0 || x1 > E.x1 || y1 > E.y1)
      cancelRender(
        `SAFE AREA: "${children.slice(0, 48)}" occupies [${x0.toFixed(0)},${y0.toFixed(0)}-${x1.toFixed(0)},${y1.toFixed(0)}], outside [${E.x0},${E.y0}-${E.x1},${E.y1}].`
      );
    const lines = Math.round(r.height / scale / (size * 1.25));
    if (lines > maxLines)
      cancelRender(`LINE COUNT: "${children.slice(0, 48)}" wrapped to ${lines} lines, max ${maxLines}.`);
  }, [children, essential, scale, size, maxLines]);

  const fam = role === "display" ? TYPE.display : role === "label" ? TYPE.mono : TYPE.body;
  return (
    <div
      ref={ref}
      data-essential={essential ? "1" : "0"}
      style={{
        fontFamily: fam,
        fontSize: size,
        lineHeight: 1.25,
        color: color ?? COLOR.ink,
        maxWidth: "100%",
        ...style,
      }}
    >
      {wordOpacity
        ? children.split(/(\s+)/).map((tok, i) =>
            /^\s+$/.test(tok) ? (
              tok
            ) : (
              <span key={i} style={{ opacity: wordOpacity[Math.floor(i / 2)] ?? 1 }}>{tok}</span>
            )
          )
        : children}
    </div>
  );
};
