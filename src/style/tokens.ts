/**
 * The single source of visual truth. Change the series' look here, not in shots.
 * Lengths are in canvas px (1080x1920). See SAFE for interface exclusions.
 */
export const CANVAS = { width: 1080, height: 1920, fps: 30 } as const;

/**
 * Instagram interface exclusions, measured from the previous organic Reel.
 * NOT an official spec: device, app version, post text and expanded captions
 * all change coverage. Treated as a starting guide that must be re-verified
 * against the real upload preview. Ads need more bottom clearance.
 */
export const SAFE = {
  top: 270,
  bottom: 1535,
  right: 900,
  left: 80,
  /** Essential text must fit strictly inside this box. */
  essential: { x0: 80, y0: 270, x1: 860, y1: 1510 },
} as const;

/** Named layout regions. Shots place content into these, never at raw coords. */
/**
 * Regions are INSET from SAFE.essential by GUTTER so that nothing essential
 * sits on the gate's boundary. Text antialiasing bleeds a pixel or two past a
 * glyph box; a label flush to the line reads as a violation (and, flush to the
 * real interface, reads as clipped). Breathing room, not boundary-hugging.
 */
const GUTTER = 24;
export const REGIONS = {
  title:   { x0: 104, y0: 320,  x1: 836, y1: 1180 },
  /** Full-bleed. For PHOTOGRAPHY only - it deliberately extends under the
   *  interface. Anything informational belongs in a bounded region below. */
  art:     { x0: 0,  y0: 270,  x1: 1080, y1: 1330 },
  quote:   { x0: 104, y0: 520,  x1: 836, y1: 1280 },
  stat:    { x0: 104, y0: 480,  x1: 836, y1: 1280 },
  /** Diagrams are INFORMATION, so they are bounded like text, never full-bleed.
   *  The SVG viewBox is this box exactly, so nothing drawn can escape it. */
  diagram: { x0: 104, y0: 400,  x1: 836, y1: 1300 },
  labels:  { x0: 104, y0: 1130, x1: 836, y1: 1330 },
  caption: { x0: 104, y0: 1340, x1: 836, y1: 1500 },
  credits: { x0: 104, y0: 700,  x1: 836, y1: 1200 },
} as const;
export type RegionName = keyof typeof REGIONS;

export const COLOR = {
  bg: "#0b0b0c",
  ink: "#f4f1ea",
  inkDim: "#a9a49a",
  accent: "#d98324",
  rule: "#2a2a2d",
  captionBack: "rgba(0,0,0,0.42)",
} as const;

export const TYPE = {
  display: '"Inter Tight", "Helvetica Neue", Helvetica, Arial, sans-serif',
  body: '"Inter", "Helvetica Neue", Helvetica, Arial, sans-serif',
  mono: '"IBM Plex Mono", ui-monospace, Menlo, monospace',
} as const;

/**
 * Legibility floor. A phone shows this 1080px-wide canvas at roughly 400 CSS px,
 * so canvas px scale by ~0.37 on screen. 38 canvas px is the smallest cap-height
 * that survives that. The renderer FAILS rather than shrinking past it.
 */
export const MIN_FONT_PX = { caption: 46, label: 42, body: 46, display: 64 } as const;

export const MOTION = { enterFrames: 8, exitFrames: 6, holdMinFrames: 60 } as const;
