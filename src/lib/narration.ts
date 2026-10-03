import { useVideoConfig } from "remotion";
import { findPhrase, type Alignment } from "./timeline";

/**
 * A diagram state anchored to a phrase of the narration.
 *
 * The production notes are explicit that a diagram's states must convey the
 * intended concept rather than merely add motion. Anchoring each state to the
 * words that explain it enforces that structurally: a state cannot appear
 * before the narration reaches it, and re-recording the voiceover moves the
 * states with the voice instead of leaving them stranded on a clock.
 */
export type NarrationState<T> = { at_phrase: string } & T;

export type ResolvedState<T> = NarrationState<T> & { fromFrame: number };

export function resolveStates<T>(
  states: NarrationState<T>[],
  al: Alignment,
  fps: number,
  shotStartFrame: number
): ResolvedState<T>[] {
  if (states.length === 0) throw new Error("a diagram needs at least one state");
  const out = states.map((s) => ({
    ...s,
    fromFrame: Math.round(findPhrase(al, s.at_phrase).start * fps) - shotStartFrame,
  }));
  // Monotonic by construction of the narration; out of order means an anchor
  // points outside this shot, which would make the diagram jump backwards.
  for (let i = 1; i < out.length; i++) {
    if (out[i]!.fromFrame < out[i - 1]!.fromFrame)
      throw new Error(
        `diagram states out of order: "${out[i]!.at_phrase}" resolves before "${out[i - 1]!.at_phrase}"`
      );
  }
  if (out[0]!.fromFrame > 0)
    throw new Error(
      `first diagram state "${out[0]!.at_phrase}" starts ${out[0]!.fromFrame} frames into the shot — the diagram would be blank until then`
    );
  return out;
}

/** Index of the state the narration has currently reached. */
export function activeIndex<T>(states: ResolvedState<T>[], frame: number): number {
  let i = 0;
  for (let k = 0; k < states.length; k++) if (frame >= states[k]!.fromFrame) i = k;
  return i;
}

/** 0..1 progress into the current state's entrance, for restrained transitions. */
export function stateProgress<T>(states: ResolvedState<T>[], frame: number, fps: number, secs = 0.45): number {
  const i = activeIndex(states, frame);
  const t = (frame - states[i]!.fromFrame) / (fps * secs);
  return Math.max(0, Math.min(1, t));
}

export function useFps(): number {
  return useVideoConfig().fps;
}
