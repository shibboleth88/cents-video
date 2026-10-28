import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { Alignment } from "../lib/timeline";
import { COLOR, REGIONS, TYPE } from "./tokens";
import { SafeText } from "./Safe";
import { wordProgress } from "./motion";

/**
 * Caption looks, picked per render with the `captionStyle` prop.
 *   classic  the shipped look: dim box, words brighten as spoken (CaptionLayer)
 *   lead     no box; the word being spoken is copper, said words white, the rest dim
 *   keys     the whole line at once; numbers and years in copper, like the
 *            readouts; a copper rule fills as the line is spoken
 *   phrase   two to four words at a time, large, each word lighting as it is spoken
 * The SRT is untouched by all of them: these change how a cue is drawn, never its words.
 */
export type CaptionStyle = "classic" | "lead" | "keys" | "phrase";

type Cue = { start: number; end: number; text: string };
type Word = { word: string; start: number; end: number };

/** Lighter than the palette copper so a thin glyph still reads on black (7.7:1 on bg). */
export const CAPTION_COPPER = "#d9925c";

const SMALL: Record<string, number> = {
  ten: 10, eleven: 11, twelve: 12, thirteen: 13, fourteen: 14, fifteen: 15, sixteen: 16,
  seventeen: 17, eighteen: 18, nineteen: 19,
};
const TENS: Record<string, number> = {
  twenty: 20, thirty: 30, forty: 40, fifty: 50, sixty: 60, seventy: 70, eighty: 80, ninety: 90,
};
const UNITS: Record<string, number> = {
  one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9,
};

/** "thirty-three," -> "33,". Only 10 to 99, so "one of them" and "two wallets" stay words. */
function numeral(tok: string): string {
  const m = tok.match(/^([A-Za-z-]+)([^A-Za-z]*)$/);
  if (!m) return tok;
  const [a = "", b] = m[1]!.toLowerCase().split("-");
  let n: number | undefined;
  if (b === undefined) n = SMALL[a] ?? TENS[a];
  else if (TENS[a] && UNITS[b]) n = TENS[a]! + UNITS[b]!;
  return n === undefined ? tok : `${n}${m[2]}`;
}

/** A hyphen inside a word must not become a line break ("thirty- / three"). */
const nobreak = (tok: string) => tok.replace(/(\w)-(\w)/g, "$1‑$2");
const isNumber = (tok: string) => /\d/.test(tok);

const norm = (w: string) => w.toLowerCase().replace(/[^a-z0-9']/g, "");

/**
 * The cue's words and when each is spoken. The alignment holds SPOKEN words, so a
 * written "8550" is two of them ("eighty-five fifty"). Walk both lists: a matching
 * word takes its own time; a written token that does not match takes the time of
 * the first spoken word it stands for, and swallows spoken words up to the next
 * match. A plain word that does not match, or any loose end, leaves the cue untimed (drawn whole), never half-timed.
 */
function cueWords(cue: Cue, alignment?: Alignment) {
  const words = cue.text.split(/\s+/).filter(Boolean);
  const spoken = ((alignment?.words ?? []) as Word[]).filter(
    (w) => w.start >= cue.start - 0.01 && w.start <= cue.end + 0.01
  );
  const times: number[] = [];
  let j = 0;
  for (let i = 0; i < words.length; i++) {
    // A dash or other bare punctuation is not spoken: it rides with the word before.
    if (norm(words[i]!) === "") { times.push(times[times.length - 1] ?? cue.start); continue; }
    if (j >= spoken.length) return { words, times: undefined };
    times.push(spoken[j]!.start);
    if (norm(words[i]!) === norm(spoken[j]!.word)) { j++; continue; }
    // Only a written form may stand for other spoken words: a number, "cents.vision",
    // "1/1", or a name the voice is given phonetically ("ScrappyT" said "Scrappy T",
    // "Reiss" said "Rice"). A lowercase word that does not match is a real disagreement.
    if (/^[a-z'’]+[,.;:!?]*$/.test(words[i]!)) return { words, times: undefined };
    const next = words[i + 1];
    j++;
    while (j < spoken.length && (next === undefined || norm(spoken[j]!.word) !== norm(next))) j++;
    if (next !== undefined && j >= spoken.length) return { words, times: undefined };
  }
  return { words, times: j === spoken.length ? times : undefined };
}

const Band: React.FC<{ children: React.ReactNode; align?: "center" | "flex-start" }> = ({ children, align = "center" }) => {
  const { x0, y0, x1, y1 } = REGIONS.caption;
  return (
    <div style={{ position: "absolute", left: x0, top: y0, width: x1 - x0, height: y1 - y0,
      display: "flex", alignItems: "center", justifyContent: align }}>
      {children}
    </div>
  );
};

/** A soft fall-off behind the caption band instead of a box: it darkens busy frames
 *  without drawing an edge. Decorative, so it runs full width under the interface. */
const Scrim: React.FC = () => (
  <div style={{ position: "absolute", left: 0, width: 1080, top: 1290, height: 300,
    background: "linear-gradient(to bottom, rgba(11,10,10,0) 0%, rgba(11,10,10,0.62) 35%, rgba(11,10,10,0.62) 70%, rgba(11,10,10,0) 100%)" }} />
);

const SHADOW = "0 2px 10px rgba(0,0,0,0.85), 0 0 2px rgba(0,0,0,0.9)";

const Lead: React.FC<{ cue: Cue; alignment?: Alignment }> = ({ cue, alignment }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const { words, times } = cueWords(cue, alignment);
  const shown = words.map((w) => nobreak(numeral(w)));
  let op: number[] | undefined;
  let col: (string | undefined)[] | undefined;
  if (times) {
    // The current word is the last one whose start has passed.
    let cur = -1;
    times.forEach((s, i) => { if (t >= s - 0.06) cur = i; });
    op = times.map((s) => 0.38 + 0.62 * wordProgress(f, fps, s));
    col = times.map((_, i) => (i === cur ? CAPTION_COPPER : undefined));
  }
  return (
    <>
      <Band align="flex-start">
        <SafeText role="caption" fontSize={52} maxLines={2} wordOpacity={op} wordColor={col}
          style={{ textWrap: "balance", fontWeight: 600, textShadow: SHADOW }}>
          {shown.join(" ")}
        </SafeText>
      </Band>
    </>
  );
};

const Keys: React.FC<{ cue: Cue; alignment?: Alignment }> = ({ cue, alignment }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const { words, times } = cueWords(cue, alignment);
  const shown = words.map((w) => nobreak(numeral(w)));
  const lastStart = times ? times[times.length - 1]! + 0.25 : cue.end;
  const fill = interpolate(t, [cue.start, lastStart], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const enter = interpolate(t, [cue.start - 0.05, cue.start + 0.15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <Band align="flex-start">
      <div style={{ opacity: enter, display: "flex", flexDirection: "column", alignItems: "flex-start", maxWidth: "100%" }}>
        {/* The rule spans the line's own width and fills as the line is spoken. */}
        <div style={{ width: `${fill * 100}%`, height: 3, background: CAPTION_COPPER, opacity: 0.85, marginBottom: 10 }} />
        <SafeText role="caption" fontSize={50} maxLines={2}
          wordColor={shown.map((w) => (isNumber(w) ? CAPTION_COPPER : undefined))}
          style={{ textWrap: "balance", fontWeight: 500, textShadow: SHADOW }}>
          {shown.join(" ")}
        </SafeText>
      </div>
    </Band>
  );
};

/** Break a cue into short phrases: at punctuation, or before a phrase passes 16 characters, so it holds one line. */
function phrases(words: string[]): number[][] {
  const out: number[][] = [];
  let cur: number[] = [];
  let len = 0;
  words.forEach((w, i) => {
    if (cur.length && (len + 1 + w.length > 16 || cur.length >= 4)) { out.push(cur); cur = []; len = 0; }
    cur.push(i);
    len += (len ? 1 : 0) + w.length;
    if (/[,.;:!?]$/.test(w) && i < words.length - 1) { out.push(cur); cur = []; len = 0; }
  });
  if (cur.length) out.push(cur);
  // A lone short tail reads as a stray word: fold it back when it fits.
  if (out.length > 1) {
    const last = out[out.length - 1]!;
    const prev = out[out.length - 2]!;
    const prevLen = prev.map((i) => words[i]!.length).reduce((a, b) => a + b + 1, -1);
    const joined = !/[,.;:!?]$/.test(words[prev[prev.length - 1]!]!);
    if (last.length === 1 && joined && prevLen + 1 + words[last[0]!]!.length <= 18)
      out.splice(out.length - 2, 2, [...prev, ...last]);
    // Too long to fold: lend it the previous phrase's last word ("Ghost Cents,").
    else if (last.length === 1 && joined && prev.length >= 3) last.unshift(prev.pop()!);
  }
  return out;
}

const Phrase: React.FC<{ cue: Cue; alignment?: Alignment }> = ({ cue, alignment }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const { words, times: timed } = cueWords(cue, alignment);
  const shown = words.map((w) => nobreak(numeral(w)));
  // A whole cue does not fit at this size, so an untimed cue still goes phrase by
  // phrase, its words spread over the cue by length.
  const chars = shown.map((w) => w.length + 1);
  const total = chars.reduce((a, b) => a + b, 0);
  let acc = 0;
  const times = timed ?? chars.map((c) => { const at = cue.start + ((cue.end - cue.start) * acc) / total; acc += c; return at; });
  let idx = shown.map((_, i) => i);
  let prog = shown.map(() => 1);
  {
    const groups = phrases(shown);
    let g = groups[0]!;
    for (const grp of groups) if (t >= times[grp[0]!]! - 0.08) g = grp;
    idx = g;
    prog = g.map((i) => wordProgress(f, fps, times[i]!, 0.08));
  }
  const text = idx.map((i) => shown[i]).join(" ");
  return (
    <>
      <Band>
        <SafeText role="caption" fontSize={68} maxLines={2}
          wordOpacity={prog.map((p) => 0.18 + 0.82 * p)}
          wordColor={idx.map((i) => (isNumber(shown[i]!) ? CAPTION_COPPER : undefined))}
          style={{ textWrap: "balance", textAlign: "center", fontFamily: TYPE.display, fontWeight: 700,
            letterSpacing: -0.5, textShadow: SHADOW }}>
          {text}
        </SafeText>
      </Band>
    </>
  );
};

export const StyledCaptions: React.FC<{ cues: Cue[]; alignment?: Alignment; look: Exclude<CaptionStyle, "classic"> }> = ({
  cues, alignment, look,
}) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const cue = cues.find((c) => t >= c.start && t < c.end);
  const C = look === "lead" ? Lead : look === "keys" ? Keys : Phrase;
  // The scrim stays up through the gaps between cues so it never flickers.
  return (
    <>
      {cue ? <C cue={cue} alignment={alignment} /> : null}
    </>
  );
};
