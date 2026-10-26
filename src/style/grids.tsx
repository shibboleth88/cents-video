import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { EASE } from "./motion";

/**
 * Real Cents, drawn from the on-chain images. Shared by every film in the
 * series: the Sets film builds its pools and walls here, Secret History builds
 * its year chart on CentImage.
 *
 * Images are staged by pipeline/stage_cents.py into public/cents/<n>.webp as
 * circular cutouts with a transparent outside. Nothing here generates or
 * retouches a coin: a Cent on screen is always the Cent its number names.
 */

/**
 * Below this a Cent reads as a plain brown disc and its trait disappears
 * (measured on test frames, 2026-10-24). A grid used as EVIDENCE of a trait
 * must stay at or above it. A grid used as texture or scale — the whole
 * collection as a field — says so with `texture`, and then nothing in it may be
 * offered as showing a trait.
 */
export const MIN_TRAIT_PX = 60;

/**
 * The source images are 300px with the coin about 246px across. Upscaled past
 * this the detail goes soft; a hero Cent stays at or under it.
 */
export const MAX_CENT_PX = 520;

const checkNumber = (n: number) => {
  if (!Number.isInteger(n) || n < 1 || n > 10000)
    throw new Error(`CentImage: ${n} is not a Cent number (1-10000)`);
};

export const CentImage: React.FC<{
  n: number;
  size: number;
  /** Declares that this Cent is shown as texture, not as evidence of a trait. */
  texture?: boolean;
  style?: React.CSSProperties;
}> = ({ n, size, texture, style }) => {
  checkNumber(n);
  if (!texture && size < MIN_TRAIT_PX)
    throw new Error(`CENT #${n} at ${size}px is below the ${MIN_TRAIT_PX}px trait floor; pass texture if it is only texture`);
  if (size > MAX_CENT_PX)
    throw new Error(`CENT #${n} at ${size}px is past the ${MAX_CENT_PX}px the 300px source holds`);
  return <Img src={staticFile(`cents/${n}.webp`)} width={size} height={size}
              style={{ display: "block", width: size, height: size, ...style }} />;
};

export type GridLayout = {
  cols: number;
  size: number;
  gap: number;
};

/** Fit `count` Cents into a box, as large as they will go. */
export function fitGrid(count: number, width: number, height: number, gapRatio = 0.08): GridLayout {
  if (count < 1) throw new Error("fitGrid: nothing to fit");
  let best: GridLayout = { cols: 1, size: 0, gap: 0 };
  for (let cols = 1; cols <= count; cols++) {
    const rows = Math.ceil(count / cols);
    const cell = Math.min(width / cols, height / rows);
    const size = Math.floor(cell / (1 + gapRatio));
    if (size > best.size) best = { cols, size, gap: Math.floor(cell - size) };
  }
  return best;
}

/**
 * A grid of real Cents.
 *
 * `lit` picks out a pool inside the grid: everything else fades towards the
 * background by `dim`. Entrances run in reading order over `enterFrames`, which
 * holds a 10,000-Cent field to the same duration as a wall of fifteen, and costs
 * one interpolate per Cent rather than a spring.
 */
export const CentGrid: React.FC<{
  ns: number[];
  layout: GridLayout;
  lit?: ReadonlySet<number>;
  /** 0..1, how far unlit Cents fade. */
  dim?: number;
  /** Frame the first Cent starts entering. */
  from?: number;
  /** Frames from the first Cent's entrance to the last's. 0 = all at once. */
  enterFrames?: number;
  texture?: boolean;
  style?: React.CSSProperties;
}> = ({ ns, layout, lit, dim = 0.85, from = 0, enterFrames = 30, texture, style }) => {
  const frame = useCurrentFrame();
  if (ns.length === 0) throw new Error("CentGrid: an empty pool renders as an empty wall; refusing");
  const { cols, size, gap } = layout;
  const step = size + gap;
  const rows = Math.ceil(ns.length / cols);
  const last = Math.max(1, ns.length - 1);
  return (
    <div style={{ position: "relative", width: cols * step - gap, height: rows * step - gap, ...style }}>
      {ns.map((n, i) => {
        const start = from + (enterFrames * i) / last;
        const t = interpolate(frame, [start, start + 10], [0, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out });
        const off = lit && !lit.has(n);
        return (
          <div key={n} style={{
            position: "absolute",
            left: (i % cols) * step,
            top: Math.floor(i / cols) * step,
            opacity: t * (off ? 1 - dim : 1),
            transform: `scale(${0.6 + 0.4 * t})`,
          }}>
            <CentImage n={n} size={size} texture={texture} />
          </div>
        );
      })}
    </div>
  );
};

/**
 * One Cent, turning slowly, for showing what a trait looks like.
 *
 * The turn is a rotation in the plane plus a small tilt in depth. It never
 * turns past ±maxTilt degrees, because only the obverse was photographed and
 * inscribed: a turn that reached the back would have to invent one. No light
 * or colour is laid over the coin, so the patina on screen is the photograph's.
 */
export const CentTurn: React.FC<{
  n: number;
  size: number;
  /** Degrees of in-plane rotation per second. */
  spin?: number;
  /** Largest tilt in depth, degrees. Kept well short of edge-on. */
  maxTilt?: number;
  /** Seconds per tilt cycle. */
  tiltPeriod?: number;
  from?: number;
  style?: React.CSSProperties;
}> = ({ n, size, spin = 9, maxTilt = 16, tiltPeriod = 7, from = 0, style }) => {
  const frame = useCurrentFrame();
  if (maxTilt > 35) throw new Error(`CentTurn: a ${maxTilt}° tilt foreshortens the face too far; keep it at 35° or under`);
  const t = (frame - from) / 30;
  const enter = interpolate(frame, [from, from + 18], [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out });
  const tiltX = maxTilt * Math.sin((2 * Math.PI * t) / tiltPeriod);
  const tiltY = maxTilt * 0.6 * Math.cos((2 * Math.PI * t) / (tiltPeriod * 1.3));
  return (
    <div style={{ width: size, height: size, perspective: size * 3, ...style }}>
      <div style={{
        width: size, height: size, opacity: enter,
        transform: `scale(${0.85 + 0.15 * enter}) rotateX(${tiltX}deg) rotateY(${tiltY}deg) rotateZ(${spin * t}deg)`,
        filter: `drop-shadow(0 ${size * 0.04}px ${size * 0.06}px rgba(0,0,0,0.55))`,
      }}>
        <CentImage n={n} size={size} />
      </div>
    </div>
  );
};
