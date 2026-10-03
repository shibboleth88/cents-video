import type { RegionName } from "../style/tokens";

export type VisualKind = "code" | "real" | "stock" | "generated";

/**
 * A shot's position in time is expressed as a phrase of the narration, never as
 * a number of seconds. Re-record the voiceover and the edit follows the words.
 */
export type Anchor =
  | { at_phrase: string }      // cut on the first word of this phrase
  | { after_phrase: string }   // cut on the end of this phrase
  | { at_start: true }
  | { at_end: true };

export type TextBlock = {
  text: string;
  region: RegionName;
  /** Essential content participates in the safe-area and legibility gates. */
  essential: boolean;
  role?: "display" | "body" | "label" | "mono";
};

export type Shot = {
  shot_id: string;
  start: Anchor;
  end: Anchor;
  /** Why this shot exists. A shot that cannot state a purpose is decoration. */
  purpose: string;
  visual_kind: VisualKind;
  /** Component name in src/style for visual_kind "code". */
  component?: string;
  /** asset_id from timeline/assets.json for real/stock/generated. */
  asset_id?: string;
  props?: Record<string, unknown>;
  text?: TextBlock[];
};

export type Timeline = {
  essay: { title: string; author: string; subtitle?: string; source: string; version: string };
  shots: Shot[];
  credits: { lines: string[]; url?: string };
};

export type Word = { word: string; start: number; end: number };
export type Alignment = { words: Word[]; duration: number };

/** Apostrophes vanish rather than becoming word breaks: Chang's -> changs. */
const norm = (s: string) =>
  s.toLowerCase().replace(/['\u2019]/g, "").replace(/[^a-z0-9\s]/g, " ").replace(/\s+/g, " ").trim();

/** Flatten words to tokens, remembering which word each token came from, so a
 *  hyphenated or compound token still matches a plainly written anchor. */
function tokenize(al: Alignment): { tok: string; wi: number }[] {
  const out: { tok: string; wi: number }[] = [];
  al.words.forEach((w, wi) => {
    for (const tok of norm(w.word).split(" ")) if (tok) out.push({ tok, wi });
  });
  return out;
}

/** Character-level similarity, 0..1. Enough to survive a transcription slip. */
function ratio(a: string, b: string): number {
  if (a === b) return 1;
  const m = a.length, n = b.length;
  if (m === 0 || n === 0) return 0;
  let prev = new Array<number>(n + 1);
  let cur = new Array<number>(n + 1);
  for (let j = 0; j <= n; j++) prev[j] = j;
  for (let i = 1; i <= m; i++) {
    cur[0] = i;
    for (let j = 1; j <= n; j++) {
      cur[j] = Math.min(prev[j]! + 1, cur[j - 1]! + 1, prev[j - 1]! + (a[i - 1] === b[j - 1] ? 0 : 1));
    }
    [prev, cur] = [cur, prev];
  }
  return 1 - prev[n]! / Math.max(m, n);
}

/**
 * Locate a phrase in the aligned transcript.
 *
 * Deliberately FUZZY. A real aligner emits noise — it produced the token
 * ".opherRutherford" on a scratch pass here — and exact token matching made one
 * corrupted word break every cut in the film. Matching is on character
 * similarity over a sliding window.
 *
 * The ambiguity guard survives: a match is only accepted when it is clearly
 * better than the next non-overlapping candidate, so a phrase occurring twice
 * still fails loudly rather than cutting on the wrong one.
 */
const MATCH_MIN = 0.80;    // below this, the phrase is not in the recording
const MATCH_MARGIN = 0.06; // best must beat the runner-up by at least this

export function findPhrase(al: Alignment, phrase: string): { start: number; end: number } {
  const needle = norm(phrase).split(" ").filter(Boolean);
  if (needle.length === 0) throw new Error("empty anchor phrase");
  const toks = tokenize(al);
  if (toks.length === 0) throw new Error("alignment contains no tokens — nothing to anchor to");
  const target = needle.join(" ");

  type Cand = { i: number; len: number; score: number };
  const cands: Cand[] = [];
  for (const len of [needle.length - 1, needle.length, needle.length + 1]) {
    if (len < 1) continue;
    for (let i = 0; i + len <= toks.length; i++) {
      const window = toks.slice(i, i + len).map((t) => t.tok).join(" ");
      const score = ratio(window, target);
      if (score >= MATCH_MIN) cands.push({ i, len, score });
    }
  }
  if (cands.length === 0)
    throw new Error(`anchor phrase not found in recording: "${phrase}" (best match below ${MATCH_MIN})`);

  cands.sort((a, b) => b.score - a.score);
  const best = cands[0]!;
  const rival = cands.find((c) => c.i + c.len <= best.i || c.i >= best.i + best.len);
  if (rival && best.score - rival.score < MATCH_MARGIN)
    throw new Error(
      `anchor phrase is ambiguous: "${phrase}" matches at two places (${best.score.toFixed(2)} vs ${rival.score.toFixed(2)}) \u2014 lengthen it`
    );

  return {
    start: al.words[toks[best.i]!.wi]!.start,
    end: al.words[toks[best.i + best.len - 1]!.wi]!.end,
  };
}

export function resolveAnchor(al: Alignment, a: Anchor): number {
  if ("at_start" in a) return 0;
  if ("at_end" in a) return al.duration;
  if ("at_phrase" in a) return findPhrase(al, a.at_phrase).start;
  return findPhrase(al, a.after_phrase).end;
}

export type ResolvedShot = Shot & { fromFrame: number; durationInFrames: number };

/**
 * Resolve every shot to frame boundaries on one timebase, then assert the
 * result is a gapless, non-overlapping cover of the recording. These are the
 * errors that produce a frozen tail or a black hole mid-film.
 */
export function resolveShots(tl: Timeline, al: Alignment, fps: number): ResolvedShot[] {
  if (tl.shots.length === 0) throw new Error("timeline has no shots");

  // One timebase, one rounding. Each BOUNDARY is converted to a frame exactly
  // once and durations are derived as frame differences. Rounding each shot's
  // duration independently drifts boundaries by a frame and desynchronises the
  // film from the recording.
  const bounds = tl.shots.map((s) => {
    const t0 = resolveAnchor(al, s.start);
    const t1 = resolveAnchor(al, s.end);
    if (!(t1 > t0)) throw new Error(`${s.shot_id}: end (${t1}s) is not after start (${t0}s)`);
    return { s, f0: Math.round(t0 * fps), f1: Math.round(t1 * fps) };
  });
  bounds.sort((a, b) => a.f0 - b.f0);

  const out = bounds.map(({ s, f0, f1 }) => {
    if (f1 - f0 < 1) throw new Error(`${s.shot_id}: rounds to zero frames — passage too short to be a shot`);
    return { ...s, fromFrame: f0, durationInFrames: f1 - f0 };
  });

  if (out[0]!.fromFrame !== 0)
    throw new Error(`first shot starts at frame ${out[0]!.fromFrame}, not 0 \u2014 film would open black`);
  for (let i = 1; i < out.length; i++) {
    const prevEnd = out[i - 1]!.fromFrame + out[i - 1]!.durationInFrames;
    if (out[i]!.fromFrame !== prevEnd)
      throw new Error(
        `gap/overlap of ${out[i]!.fromFrame - prevEnd} frames between ${out[i - 1]!.shot_id} and ${out[i]!.shot_id}`
      );
  }
  const end = out[out.length - 1]!;
  const tail = Math.round(al.duration * fps) - (end.fromFrame + end.durationInFrames);
  if (tail > 1)
    throw new Error(`last shot ends ${tail} frames before the recording does \u2014 the film would freeze or go black on the tail`);
  return out;
}

export function totalFrames(shots: ResolvedShot[]): number {
  const last = shots[shots.length - 1]!;
  return last.fromFrame + last.durationInFrames;
}
