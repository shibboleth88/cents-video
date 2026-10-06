import { spring, interpolate, Easing, useCurrentFrame, useVideoConfig } from "remotion";

/**
 * Motion tokens. Every animated thing in the film picks a ROLE here rather than
 * inventing its own curve, so the whole film moves with one character and a new
 * shot inherits it without anyone tuning numbers.
 *
 * The production notes forbid slow zooms used as the only source of motion, so
 * `drift` is deliberately small and always accompanies something else; it is
 * atmosphere, never the reason a shot is alive.
 */
export const MOTION_ROLE = {
  /** Text and titles: rises into place and settles. */
  rise:   { damping: 200, mass: 0.9,  stiffness: 90,  travel: 34, scale: 0 },
  /** Diagram nodes arriving: a little overshoot so the state change is felt. */
  settle: { damping: 14,  mass: 0.55, stiffness: 120, travel: 0,  scale: 0.14 },
  /** Emphasis on an element already present. */
  bloom:  { damping: 12,  mass: 0.4,  stiffness: 160, travel: 0,  scale: 0.09 },
  /** Plates and images entering. */
  place:  { damping: 26,  mass: 1.1,  stiffness: 70,  travel: 22, scale: 0.03 },
} as const;
export type MotionRole = keyof typeof MOTION_ROLE;

export const TIMING = {
  /** Gap between successive members of a group, in frames. */
  stagger: 4,
  /** Entrance and exit of a whole shot. */
  shotIn: 10,
  shotOut: 8,
  /** Camera drift across a full shot, as a fraction of the frame. */
  driftAmount: 0.045,
} as const;

export const EASE = {
  out: Easing.bezier(0.16, 1, 0.3, 1),
  inOut: Easing.bezier(0.65, 0, 0.35, 1),
  linear: Easing.linear,
} as const;

export type Entrance = { opacity: number; y: number; scale: number };

/** Entrance for one element, optionally delayed by its position in a group. */
export function useEntrance(role: MotionRole = "rise", index = 0, from = 0): Entrance {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const r = MOTION_ROLE[role];
  const f = frame - from - index * TIMING.stagger;
  const s = spring({ frame: f, fps, config: { damping: r.damping, mass: r.mass, stiffness: r.stiffness } });
  return {
    opacity: interpolate(f, [0, 7], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
    y: (1 - s) * r.travel,
    scale: 1 + (1 - s) * r.scale,
  };
}

/** Opacity for a whole shot: in at the start, out at the end. */
export function useShotFade(): number {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return interpolate(
    frame,
    [0, TIMING.shotIn, durationInFrames - TIMING.shotOut, durationInFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.out }
  );
}

/**
 * A slow, deterministic camera move for a still. The direction comes from the
 * shot id, so every shot differs without anyone choosing, and the same shot
 * always moves the same way.
 */
export function useDrift(seed: string, amount: number = TIMING.driftAmount): { transform: string } {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  const angle = ((h % 360) * Math.PI) / 180;
  const t = interpolate(frame, [0, Math.max(1, durationInFrames)], [0, 1], {
    extrapolateRight: "clamp", easing: EASE.inOut,
  });
  const d = amount * 100;
  const x = Math.cos(angle) * d * (t - 0.5);
  const y = Math.sin(angle) * d * (t - 0.5);
  const z = 1.08 + 0.03 * t;
  return { transform: `scale(${z}) translate(${x}%, ${y}%)` };
}

/** 0..1 for a word, given when it is spoken. Used for word-level reveals. */
export function wordProgress(frame: number, fps: number, start: number, lead = 0.06): number {
  return interpolate(frame / fps, [start - lead, start + 0.1], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
}
