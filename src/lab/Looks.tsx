import React from "react";
import {
  AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, spring, staticFile,
  useCurrentFrame, useVideoConfig, Easing,
} from "remotion";
import { loadFonts } from "../style/fonts";

loadFonts();

/**
 * Three candidate series looks, built on the same 22.6 s excerpt: the opening
 * of One Cent #2616 v3 (its real narration, 0-14.6 s) followed by a silent
 * quote card and end card. Only the look changes between A, B and C, so the
 * three can be compared frame for frame. Assets live in public/look/ (not
 * committed; see films/../README in the PR).
 *
 *   npx remotion render src/lab/index.ts LookA out.mp4
 */

const FPS = 30;
const s = (sec: number) => Math.round(sec * FPS);

/** Cue times from one-cent-2616_v3.srt. Word times are spread evenly inside a
 *  cue: close enough to judge a caption look, not a substitute for alignment. */
const CUES: { t0: number; t1: number; text: string }[] = [
  { t0: 0.16, t1: 2.8, text: "Cent #2616." },
  { t0: 2.84, t1: 6.32, text: "A penny struck in 1912, at Philadelphia." },
  { t0: 6.4, t1: 9.2, text: "The only Cent from 1912 in the collection." },
  { t0: 9.24, t1: 11.2, text: "One of 12 1/1 Years," },
  { t0: 11.28, t1: 14.52, text: "and one of only two before 1919." },
];

const CENT = { n: 2616, inscription: "65990912", year: 1912, episode: "03" };
/** The twelve 1/1 Years, in year order (index.json, sovrn-onchain). */
const ONES: { n: number; y: number }[] = [
  { n: 9540, y: 1911 }, { n: 2616, y: 1912 }, { n: 3340, y: 1919 }, { n: 3609, y: 1926 },
  { n: 5953, y: 1928 }, { n: 5944, y: 1929 }, { n: 4784, y: 1930 }, { n: 6619, y: 1934 },
  { n: 6628, y: 1935 }, { n: 8618, y: 1939 }, { n: 6980, y: 1949 }, { n: 1004, y: 1954 },
];
const QUOTE = {
  text: "This data reveals how quickly scarcity accelerates the further back in time you go.",
  who: "Martin Lehnen",
  where: "Reflections on Mint Years",
};

const SCENES = {
  title: [0, s(6.36)],
  only: [s(6.36), s(9.22)],
  ones: [s(9.22), s(14.6)],
  quote: [s(14.6), s(18.6)],
  end: [s(18.6), s(22.6)],
} as const;
export const LOOK_FRAMES = s(22.6);

type Look = {
  bg: string; ink: string; dim: string; rule: string; hi: string; block: string;
  display: string; sans: string; mono: string;
};

const LOOKS: Record<"A" | "B" | "C", Look> = {
  /** Gallery: cents.gallery's own type and colours. */
  A: { bg: "#0e0e0e", ink: "#f2f2f0", dim: "#8e8e8e", rule: "#2c2c2c", hi: "#c99079", block: "#824C3D",
       display: "Fraunces", sans: "IBM Plex Sans", mono: "IBM Plex Mono" },
  /** Registry: a catalogue sheet; verdigris is the interface, copper is only the coin. */
  B: { bg: "#0b0c0b", ink: "#ecebe6", dim: "#8b918d", rule: "#2a2f2d", hi: "#76b7a6", block: "#233933",
       display: "IBM Plex Sans Condensed", sans: "IBM Plex Sans Condensed", mono: "IBM Plex Mono" },
  /** Rim: the coin's own geometry; rings and legends, bright copper. */
  C: { bg: "#0b0908", ink: "#f3ece6", dim: "#93877f", rule: "#33281f", hi: "#d9925c", block: "#5a3218",
       display: "Fraunces", sans: "IBM Plex Sans", mono: "IBM Plex Mono" },
};

const CUT: React.CSSProperties = { clipPath: "circle(40.5% at 50% 50%)" };

// ---------- shared motion ----------
const useIn = (delay = 0, damping = 200) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: f - delay, fps, config: { damping, mass: 0.9, stiffness: 90 } });
};
const Rise: React.FC<{ delay?: number; travel?: number; children: React.ReactNode; style?: React.CSSProperties }> =
  ({ delay = 0, travel = 30, children, style }) => {
    const p = useIn(delay);
    return <div style={{ ...style, opacity: p, transform: `translateY(${(1 - p) * travel}px)` }}>{children}</div>;
  };
/** Simple left-to-right reveal: the Registry look's only entrance. */
const Wipe: React.FC<{ delay?: number; dur?: number; children: React.ReactNode; style?: React.CSSProperties }> =
  ({ delay = 0, dur = 10, children, style }) => {
    const f = useCurrentFrame();
    const p = interpolate(f - delay, [0, dur], [0, 100], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
    return <div style={{ ...style, clipPath: `inset(0 ${100 - p}% 0 0)` }}>{children}</div>;
  };

/** The opening spin, its coin centred on (cx, cy) at diameter d. In the
 *  3DCENTS reel the coin sits at (520, 960) with a ~680 px face. */
const Spin: React.FC<{ cx: number; cy: number; d: number; bg: string }> = ({ cx, cy, d, bg }) => {
  const k = d / 680;
  return (
    <AbsoluteFill style={{ background: bg, isolation: "isolate" }}>
      <OffthreadVideo src={staticFile("look/spin-2616.mp4")} muted
        style={{ position: "absolute", width: 1080 * k, height: 1920 * k,
                 left: cx - 520 * k, top: cy - 960 * k, mixBlendMode: "lighten" }} />
    </AbsoluteFill>
  );
};

// ---------- captions: the chosen "Lead" behaviour, re-typed per look ----------
const Caption: React.FC<{ L: Look; font: string; size: number; weight: number; align: "left" | "center"; underline?: boolean }> =
  ({ L, font, size, weight, align, underline }) => {
    const f = useCurrentFrame();
    const t = f / FPS;
    const i = CUES.findIndex((c, k) => t >= c.t0 && t < (CUES[k + 1]?.t0 ?? c.t1 + 0.4));
    if (i < 0) return null;
    const c = CUES[i]!;
    const words = c.text.split(" ");
    const per = (c.t1 - c.t0) / words.length;
    const cur = Math.min(words.length - 1, Math.floor((t - c.t0) / per));
    return (
      <div style={{ position: "absolute", left: 104, width: 732, top: 1340, height: 160,
                    display: "flex", alignItems: "center", justifyContent: align === "center" ? "center" : "flex-start" }}>
        <div style={{ position: "absolute", inset: "-40px -104px", zIndex: 0,
                      background: `linear-gradient(to bottom, ${L.bg}00 0%, ${L.bg}b0 35%, ${L.bg}b0 70%, ${L.bg}00 100%)` }} />
        <div style={{ position: "relative", fontFamily: font, fontSize: size, fontWeight: weight, lineHeight: 1.22,
                      textAlign: align, textWrap: "balance", textShadow: "0 2px 10px rgba(0,0,0,0.85)" } as React.CSSProperties}>
          {words.map((w, k) => (
            <React.Fragment key={k}>
              <span style={{ color: k === cur ? L.hi : k < cur ? L.ink : L.dim,
                             textDecoration: underline && k === cur ? "underline" : "none",
                             textDecorationThickness: 4, textUnderlineOffset: 10 }}>{w}</span>
              {k < words.length - 1 ? " " : ""}
            </React.Fragment>
          ))}
        </div>
      </div>
    );
  };

// =====================================================================
// A · GALLERY
// =====================================================================
const caps = (L: Look, size = 42, color = L.dim, spacing = "0.13em"): React.CSSProperties =>
  ({ fontFamily: L.mono, fontWeight: 500, fontSize: size, letterSpacing: spacing, textTransform: "uppercase", color });

const A_Chip: React.FC<{ L: Look; a: string; b: string }> = ({ L, a, b }) => (
  <div style={{ display: "inline-flex", gap: 22, background: L.block, padding: "16px 26px", ...caps(L, 42, L.ink) }}>
    <span>{a}</span><span style={{ color: L.hi }}>{b}</span>
  </div>
);

const LookA: React.FC = () => {
  const L = LOOKS.A;
  const frac = { fontFamily: L.display, fontVariationSettings: '"opsz" 144, "SOFT" 0, "WONK" 0' } as const;
  const small = { fontFamily: L.display, fontWeight: 400, fontVariationSettings: '"opsz" 36, "SOFT" 0, "WONK" 0' } as const;
  return (
    <AbsoluteFill style={{ background: L.bg, color: L.ink }}>
      <Audio src={staticFile("look/vo-2616.m4a")} />
      <Sequence from={SCENES.title[0]} durationInFrames={SCENES.title[1] - SCENES.title[0]}>
        <Spin cx={540} cy={1010} d={560} bg={L.bg} />
        <div style={{ position: "absolute", left: 104, top: 300 }}>
          <A_Chip L={L} a="One Cent" b={`Nº ${CENT.episode}`} />
          <Rise delay={4}><div style={{ ...frac, fontWeight: 300, fontSize: 168, lineHeight: 1.0, marginTop: 34, letterSpacing: "-0.02em" }}>Cent #{CENT.n}</div></Rise>
          <Rise delay={9}><div style={{ ...small, fontStyle: "italic", fontSize: 54, color: L.dim, marginTop: 14 }}>Inscription {CENT.inscription}</div></Rise>
        </div>
      </Sequence>

      <Sequence from={SCENES.only[0]} durationInFrames={SCENES.only[1] - SCENES.only[0]}>
        <A_Only L={L} />
      </Sequence>
      <Sequence from={SCENES.ones[0]} durationInFrames={SCENES.ones[1] - SCENES.ones[0]}>
        <A_Ones L={L} />
      </Sequence>
      <Sequence from={SCENES.quote[0]} durationInFrames={SCENES.quote[1] - SCENES.quote[0]}>
        <div style={{ position: "absolute", left: 104, width: 732, top: 560 }}>
          <Rise><div style={{ ...caps(L), marginBottom: 40 }}>In the words of</div></Rise>
          <Rise delay={4}>
            <div style={{ fontFamily: L.display, fontVariationSettings: '"opsz" 72', fontStyle: "italic", fontWeight: 350, fontSize: 76, lineHeight: 1.18, }}>
              “{QUOTE.text}”
            </div>
          </Rise>
          <Rise delay={12}>
            <div style={{ borderTop: `1px solid ${L.rule}`, marginTop: 56, paddingTop: 28 }}>
              <div style={{ fontFamily: L.sans, fontSize: 48, color: L.ink }}>{QUOTE.who}</div>
              <div style={{ ...small, fontStyle: "italic", fontSize: 48, color: L.dim, marginTop: 6 }}>{QUOTE.where}</div>
            </div>
          </Rise>
        </div>
      </Sequence>
      <Sequence from={SCENES.end[0]} durationInFrames={SCENES.end[1] - SCENES.end[0]}>
        <div style={{ position: "absolute", left: 104, width: 732, top: 330 }}>
          <Rise><div style={{ ...frac, fontWeight: 300, fontSize: 150, lineHeight: 1 }}>CENTS</div></Rise>
          <Rise delay={4}><div style={{ ...small, fontStyle: "italic", fontSize: 60, color: L.dim, marginTop: 8 }}>Rutherford Chang</div></Rise>
          <div style={{ marginTop: 90 }}>
            {[["Images", "Rutherford Chang"], ["3D render", "3DCENTS by sinvalli"], ["Words", "Martin Lehnen"], ["Series", "One Cent · Nº 03"]].map(([k, v], i) => (
              <Rise key={k} delay={10 + i * 4}>
                <div style={{ borderTop: `1px solid ${L.rule}`, padding: "22px 0 24px" }}>
                  <div style={caps(L)}>{k}</div>
                  <div style={{ fontFamily: L.sans, fontSize: 48, marginTop: 6 }}>{v}</div>
                </div>
              </Rise>
            ))}
          </div>
          <Rise delay={30}><div style={{ ...caps(L, 42, L.hi), marginTop: 30 }}>cents.gallery</div></Rise>
        </div>
      </Sequence>
      <Caption L={L} font={L.sans} size={50} weight={500} align="left" />
    </AbsoluteFill>
  );
};

const A_Only: React.FC<{ L: Look }> = ({ L }) => {
  const frac = { fontFamily: L.display, fontVariationSettings: '"opsz" 144' } as const;
  const p = useIn(0);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 104, top: 300, ...caps(L) }}>Year · Philadelphia</div>
      <Rise delay={2} style={{ position: "absolute", left: 104, top: 352 }}>
        <div style={{ ...frac, fontWeight: 300, fontSize: 210, lineHeight: 1, color: L.hi }}>{CENT.year}</div>
      </Rise>
      <Rise delay={8} style={{ position: "absolute", left: 104, top: 580 }}>
        <div style={{ fontFamily: L.display, fontVariationSettings: '"opsz" 36', fontStyle: "italic", fontWeight: 400, fontSize: 56, color: L.ink }}>the only Cent of its year</div>
      </Rise>
      <Img src={staticFile("look/2616.webp")}
        style={{ ...CUT, position: "absolute", width: 760, height: 760, left: 160, top: 640, opacity: p,
                 transform: `scale(${0.96 + 0.04 * p})` }} />
    </AbsoluteFill>
  );
};

const A_Ones: React.FC<{ L: Look }> = ({ L }) => {
  const f = useCurrentFrame();
  const two = f >= s(11.28 - 9.22);
  const frac = { fontFamily: L.display, fontVariationSettings: '"opsz" 144' } as const;
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 104, top: 300, ...caps(L) }}>{two ? "1/1 Years before 1919" : "1/1 Years in CENTS"}</div>
      <div style={{ position: "absolute", left: 104, top: 352, ...frac, fontWeight: 300, fontSize: 210, lineHeight: 1 }}>
        {two ? <>2 <span style={{ fontStyle: "italic", fontSize: 120, color: L.dim }}>of</span> 12</> : <>12</>}
      </div>
      <Grid12 L={L} top={630} lit={(c) => (two ? c.y < 1919 : c.n === CENT.n)} ring={(on) => on ? `0 0 0 4px ${L.hi}` : "none"}
              label={caps(L, 42)} />
    </AbsoluteFill>
  );
};

/** Two rows of six, years beneath. `lit` decides which are at full strength. */
const Grid12: React.FC<{
  L: Look; top: number; lit: (c: { n: number; y: number }) => boolean;
  ring: (on: boolean) => string; label: React.CSSProperties; round?: boolean;
}> = ({ L, top, lit, ring, label }) => {
  const f = useCurrentFrame();
  const size = 156, gapX = 36, gapY = 26;
  return (
    <div style={{ position: "absolute", left: 104, top, width: 732, display: "grid",
                  gridTemplateColumns: `repeat(4, ${size}px)`, columnGap: gapX, rowGap: gapY }}>
      {ONES.map((c, i) => {
        const on = lit(c);
        const appear = interpolate(f - i * 2, [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return (
          <div key={c.n} style={{ opacity: appear, display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ width: size, height: size, borderRadius: "50%", boxShadow: ring(on), transition: "none" }}>
              <Img src={staticFile(`look/cents/${c.n}.webp`)}
                   style={{ ...CUT, width: size * 1.235, height: size * 1.235, margin: -size * 0.1175,
                            filter: on ? "none" : "brightness(0.42) saturate(0.6)" }} />
            </div>
            <div style={{ ...label, marginTop: 12, color: on ? L.ink : L.dim, letterSpacing: 0 }}>{c.y}</div>
          </div>
        );
      })}
    </div>
  );
};

// =====================================================================
// B · REGISTRY
// =====================================================================
const B_Frame: React.FC<{ L: Look; left: string; right: string }> = ({ L, left, right }) => {
  const tick = (x: number, y: number, dx: number, dy: number) => (
    <path d={`M${x + dx * 36} ${y} L${x} ${y} L${x} ${y + dy * 36}`} stroke={L.hi} strokeWidth={3} fill="none" />
  );
  return (
    <AbsoluteFill>
      <svg width={1080} height={1920} style={{ position: "absolute" }}>
        {tick(60, 250, 1, 1)}{tick(1020, 250, -1, 1)}{tick(60, 1560, 1, -1)}{tick(1020, 1560, -1, -1)}
        <line x1={104} x2={976} y1={356} y2={356} stroke={L.rule} strokeWidth={2} />
      </svg>
      <div style={{ position: "absolute", left: 104, top: 286, width: 732, display: "flex", justifyContent: "space-between",
                    fontFamily: L.mono, fontSize: 42, fontWeight: 500, color: L.dim }}>
        <span>{left}</span><span style={{ color: L.hi }}>{right}</span>
      </div>
    </AbsoluteFill>
  );
};

/** Digits roll up to their value: the Registry's emphasis. */
const Count: React.FC<{ to: number; pad?: number; dur?: number; delay?: number }> = ({ to, pad = 0, dur = 14, delay = 0 }) => {
  const f = useCurrentFrame();
  const v = Math.round(interpolate(f - delay, [0, dur], [0, to], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) }));
  return <>{String(v).padStart(pad, "0")}</>;
};

const B_Row: React.FC<{ L: Look; k: string; v: string; on?: boolean; delay: number }> = ({ L, k, v, on, delay }) => (
  <Wipe delay={delay}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", padding: "18px 0",
                  borderBottom: `2px solid ${L.rule}`, fontFamily: L.mono, fontSize: 44, fontWeight: 500 }}>
      <span style={{ color: on ? L.hi : L.dim, textTransform: "uppercase" }}>{k}</span>
      <span style={{ color: on ? L.hi : L.ink }}>{v}</span>
    </div>
  </Wipe>
);

const LookB: React.FC = () => {
  const L = LOOKS.B;
  const big: React.CSSProperties = { fontFamily: L.display, fontWeight: 600, textTransform: "uppercase", lineHeight: 0.9, letterSpacing: "-0.01em" };
  return (
    <AbsoluteFill style={{ background: L.bg, color: L.ink }}>
      <Audio src={staticFile("look/vo-2616.m4a")} />
      <Sequence from={SCENES.title[0]} durationInFrames={SCENES.title[1] - SCENES.title[0]}>
        <Spin cx={540} cy={1090} d={480} bg={L.bg} />
        <B_Frame L={L} left={`${CENT.n} / 10000`} right="ONE CENT 03" />
        <div style={{ position: "absolute", left: 104, top: 392, width: 732 }}>
          <Wipe><div style={{ ...big, fontSize: 176 }}>Cent {CENT.n}</div></Wipe>
          <Wipe delay={6}><div style={{ fontFamily: L.mono, fontSize: 44, color: L.dim, marginTop: 22 }}>INSCRIPTION {CENT.inscription}</div></Wipe>
        </div>
      </Sequence>
      <Sequence from={SCENES.only[0]} durationInFrames={SCENES.only[1] - SCENES.only[0]}>
        <B_Frame L={L} left={`${CENT.n} / 10000`} right="ONE CENT 03" />
        <Img src={staticFile("look/2616.webp")} style={{ ...CUT, position: "absolute", width: 640, height: 640, left: 220, top: 380 }} />
        <div style={{ position: "absolute", left: 104, top: 1000, width: 732 }}>
          <B_Row L={L} k="Year" v="1912" on delay={0} />
          <B_Row L={L} k="Mint" v="Philadelphia" delay={4} />
          <B_Row L={L} k="Cents of this year" v="1 of 1" on delay={8} />
        </div>
      </Sequence>
      <Sequence from={SCENES.ones[0]} durationInFrames={SCENES.ones[1] - SCENES.ones[0]}>
        <B_Ones L={L} big={big} />
      </Sequence>
      <Sequence from={SCENES.quote[0]} durationInFrames={SCENES.quote[1] - SCENES.quote[0]}>
        <B_Frame L={L} left="NOTE" right="LEHNEN" />
        <div style={{ position: "absolute", left: 104, top: 470, width: 732, borderLeft: `6px solid ${L.hi}`, paddingLeft: 36, boxSizing: "border-box" }}>
          <Wipe dur={16}><div style={{ fontFamily: L.sans, fontWeight: 500, fontSize: 70, lineHeight: 1.12 }}>“{QUOTE.text}”</div></Wipe>
        </div>
        <div style={{ position: "absolute", left: 104, top: 930, width: 732 }}>
          <B_Row L={L} k="Author" v={QUOTE.who} delay={14} />
          <B_Row L={L} k="Essay" v="Mint Years" delay={18} />
        </div>
      </Sequence>
      <Sequence from={SCENES.end[0]} durationInFrames={SCENES.end[1] - SCENES.end[0]}>
        <B_Frame L={L} left="CENTS" right="CREDITS" />
        <div style={{ position: "absolute", left: 104, top: 400, width: 732 }}>
          <Wipe><div style={{ ...big, fontSize: 150 }}>CENTS</div></Wipe>
          <Wipe delay={4}><div style={{ ...big, fontSize: 70, fontWeight: 500, color: L.dim, marginTop: 14 }}>Rutherford Chang</div></Wipe>
          <div style={{ marginTop: 70 }}>
            <B_Row L={L} k="Images" v="R. Chang" delay={8} />
            <B_Row L={L} k="3D render" v="3DCENTS" delay={11} />
            <B_Row L={L} k="Words" v="M. Lehnen" delay={14} />
            <B_Row L={L} k="Series" v="One Cent 03" delay={17} />
          </div>
          <Wipe delay={22}><div style={{ fontFamily: L.mono, fontSize: 42, color: L.hi, marginTop: 34 }}>cents.gallery</div></Wipe>
        </div>
      </Sequence>
      <Caption L={L} font={L.sans} size={56} weight={500} align="left" underline />
    </AbsoluteFill>
  );
};

const B_Ones: React.FC<{ L: Look; big: React.CSSProperties }> = ({ L, big }) => {
  const f = useCurrentFrame();
  const t2 = s(11.28 - 9.22);
  const two = f >= t2;
  return (
    <AbsoluteFill>
      <B_Frame L={L} left="1/1 YEARS" right={two ? "BEFORE 1919" : "ALL"} />
      <div style={{ position: "absolute", left: 104, top: 392, ...big, fontFamily: L.mono, fontWeight: 600, fontSize: 160, color: L.hi }}>
        {two ? <><Count to={2} pad={2} dur={8} delay={t2} />/12</> : <><Count to={12} pad={2} />/12</>}
      </div>
      <Grid12 L={L} top={590} lit={(c) => (two ? c.y < 1919 : c.n === CENT.n)}
              ring={(on) => on ? `0 0 0 3px ${L.bg}, 0 0 0 6px ${L.hi}` : "none"}
              label={{ fontFamily: L.mono, fontSize: 42, fontWeight: 500 }} />
    </AbsoluteFill>
  );
};

// =====================================================================
// C · RIM
// =====================================================================
/** A ring around a coin with legends set as a coin sets them: the top one
 *  reads over the rim, the bottom one reads upright under it. Drawn on, never spun. */
const Legend: React.FC<{ L: Look; cx: number; cy: number; r: number; top: string; bottom?: string; delay?: number; id: string; size?: number; drawn?: boolean }> =
  ({ L, cx, cy, r, top, bottom, delay = 0, id, size = 42, drawn }) => {
    const f = useCurrentFrame();
    const p = drawn ? 1 : interpolate(f - delay, [0, 24], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
    const C = 2 * Math.PI * r;
    const tt = r + 16, tb = r + 16 + size * 0.74;
    const txt: React.CSSProperties = { fontFamily: L.mono, fontSize: size, fontWeight: 500, letterSpacing: "0.12em", fill: L.ink, opacity: p };
    return (
      <svg width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0 }}>
        <defs>
          <path id={`${id}-t`} d={`M ${cx - tt} ${cy} A ${tt} ${tt} 0 0 1 ${cx + tt} ${cy}`} />
          <path id={`${id}-b`} d={`M ${cx - tb} ${cy} A ${tb} ${tb} 0 0 0 ${cx + tb} ${cy}`} />
        </defs>
        <circle cx={cx} cy={cy} r={r} fill="none" stroke={L.hi} strokeWidth={3}
                strokeDasharray={C} strokeDashoffset={C * (1 - p)} transform={`rotate(-90 ${cx} ${cy})`} />
        <text style={txt} textAnchor="middle"><textPath href={`#${id}-t`} startOffset="50%">{top}</textPath></text>
        {bottom ? <text style={txt} textAnchor="middle"><textPath href={`#${id}-b`} startOffset="50%">{bottom}</textPath></text> : null}
      </svg>
    );
  };

/** "Story time" (the One Cent cover line, user pick 2026-10-28) in Rim terms: the play
 *  mark sits in a small copper ring, a miniature of the coin's ring, with the words beside
 *  it in the legend face. Full strength at frame 0; the pulse is one ripple leaving the
 *  ring, as a struck coin rings; gone by `hold` seconds. */
const StoryTime: React.FC<{ L: Look; y: number; hold?: number }> = ({ L, y, hold = 3.4 }) => {
  const f = useCurrentFrame();
  const out = interpolate(f, [s(hold) - 10, s(hold)], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  if (out <= 0) return null;
  const ripple = interpolate(f, [15, 45], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const D = 104;
  return (
    <div style={{ position: "absolute", left: 104, width: 732, top: y, display: "flex", justifyContent: "center",
                  alignItems: "center", gap: 30, opacity: out }}>
      <svg width={D} height={D} viewBox={`0 0 ${D} ${D}`} style={{ overflow: "visible" }}>
        {ripple > 0 && ripple < 1 ? (
          <circle cx={D / 2} cy={D / 2} r={D / 2 - 3 + 46 * ripple} fill="none" stroke={L.hi} strokeWidth={5}
                  opacity={0.95 * (1 - ripple)} />
        ) : null}
        <circle cx={D / 2} cy={D / 2} r={D / 2 - 3} fill="none" stroke={L.hi} strokeWidth={5} />
        <path d={`M${D * 0.4} ${D * 0.3} L${D * 0.72} ${D / 2} L${D * 0.4} ${D * 0.7} Z`} fill={L.hi} />
      </svg>
      <div style={{ fontFamily: L.mono, fontWeight: 600, fontSize: 60, letterSpacing: "0.16em", color: L.ink }}>STORY TIME</div>
    </div>
  );
};

/** Scene change through a circle opening from the coin's centre. */
const Iris: React.FC<{ cx: number; cy: number; children: React.ReactNode }> = ({ cx, cy, children }) => {
  const f = useCurrentFrame();
  const r = interpolate(f, [0, 14], [0, 2300], { extrapolateRight: "clamp", easing: Easing.in(Easing.quad) });
  return <AbsoluteFill style={{ clipPath: `circle(${r}px at ${cx}px ${cy}px)` }}>{children}</AbsoluteFill>;
};

const LookC: React.FC<{ hi?: string }> = ({ hi }) => {
  const L = { ...LOOKS.C, hi: hi ?? LOOKS.C.hi };
  const fr = (soft: number, opsz = 144): React.CSSProperties =>
    ({ fontFamily: L.display, fontVariationSettings: `"opsz" ${opsz}, "SOFT" ${soft}, "WONK" 0` });
  return (
    <AbsoluteFill style={{ background: L.bg, color: L.ink }}>
      <Audio src={staticFile("look/vo-2616.m4a")} />
      <Sequence from={SCENES.title[0]} durationInFrames={SCENES.title[1] - SCENES.title[0]}>
        {/* frame 0 is the cover: everything at full strength, nothing still arriving */}
        <Spin cx={540} cy={790} d={450} bg={L.bg} />
        <StoryTime L={L} y={292} />
        <Legend L={L} cx={540} cy={790} r={262} id="lg1" drawn
                top={`ONE CENT · Nº ${CENT.episode}`} bottom={`INSCRIPTION ${CENT.inscription}`} />
        <div style={{ position: "absolute", left: 104, width: 732, top: 1112, textAlign: "center" }}>
          <div style={{ ...caps(L, 42, L.dim, "0.3em") }}>Cent</div>
          <div style={{ ...fr(100), fontWeight: 600, fontSize: 160, lineHeight: 0.95, color: L.hi }}>{CENT.n}</div>
        </div>
      </Sequence>
      <Sequence from={SCENES.only[0]} durationInFrames={SCENES.only[1] - SCENES.only[0]}>
        <Iris cx={540} cy={790}>
          <AbsoluteFill style={{ background: L.bg }}>
            <Img src={staticFile("look/2616.webp")} style={{ ...CUT, position: "absolute", width: 590, height: 590, left: 245, top: 425 }} />
            <Legend L={L} cx={540} cy={720} r={262} id="lg2" top="THE ONLY CENT OF ITS YEAR" bottom="1912 · PHILADELPHIA" />
            <div style={{ position: "absolute", left: 104, width: 732, top: 1080, textAlign: "center" }}>
              <Rise delay={6}><div style={{ ...caps(L, 42, L.dim, "0.3em") }}>Philadelphia</div></Rise>
              <Rise delay={9}><div style={{ ...fr(100), fontWeight: 600, fontSize: 176, lineHeight: 0.95, color: L.hi }}>1912</div></Rise>
            </div>
          </AbsoluteFill>
        </Iris>
      </Sequence>
      <Sequence from={SCENES.ones[0]} durationInFrames={SCENES.ones[1] - SCENES.ones[0]}>
        <Iris cx={540} cy={720}><C_Ones L={L} fr={fr} /></Iris>
      </Sequence>
      <Sequence from={SCENES.quote[0]} durationInFrames={SCENES.quote[1] - SCENES.quote[0]}>
        <Iris cx={540} cy={860}>
          <AbsoluteFill style={{ background: L.bg }}>
            <Legend L={L} cx={540} cy={860} r={318} id="lg3" top="MARTIN LEHNEN" bottom="REFLECTIONS ON MINT YEARS" />
            <div style={{ position: "absolute", left: 270, width: 540, top: 860, transform: "translateY(-50%)", textAlign: "center" }}>
              <Rise delay={8}><div style={{ ...fr(50, 72), fontStyle: "italic", fontWeight: 400, fontSize: 56, lineHeight: 1.18 }}>“{QUOTE.text}”</div></Rise>
            </div>
          </AbsoluteFill>
        </Iris>
      </Sequence>
      <Sequence from={SCENES.end[0]} durationInFrames={SCENES.end[1] - SCENES.end[0]}>
        <Iris cx={540} cy={720}>
          <AbsoluteFill style={{ background: L.bg }}>
            <Legend L={L} cx={540} cy={720} r={276} id="lg4" top="CENTS" bottom="RUTHERFORD CHANG" />
            <div style={{ position: "absolute", left: 240, width: 600, top: 720, transform: "translateY(-50%)", textAlign: "center" }}>
              <Rise delay={6}><div style={{ ...fr(100), fontWeight: 600, fontSize: 110, color: L.hi, lineHeight: 1 }}>One Cent</div></Rise>
              <Rise delay={10}><div style={{ ...fr(0, 72), fontStyle: "italic", fontWeight: 400, fontSize: 54, color: L.dim, marginTop: 10 }}>Nº {CENT.episode} · Cent #{CENT.n}</div></Rise>
            </div>
            <div style={{ position: "absolute", left: 104, width: 732, top: 1120, textAlign: "center", fontFamily: L.sans, fontSize: 46, lineHeight: 1.5 }}>
              {[["Images", "Rutherford Chang"], ["3D render", "3DCENTS by sinvalli"], ["Words", "Martin Lehnen"]].map(([k, v], i) => (
                <Rise key={k} delay={14 + i * 4}><span style={{ ...caps(L, 42, L.dim, "0.14em") }}>{k}</span>  {v}</Rise>
              ))}
            </div>
          </AbsoluteFill>
        </Iris>
      </Sequence>
      <Caption L={L} font={L.sans} size={50} weight={500} align="center" />
    </AbsoluteFill>
  );
};

const C_Ones: React.FC<{ L: Look; fr: (soft: number, opsz?: number) => React.CSSProperties }> = ({ L, fr }) => {
  const f = useCurrentFrame();
  const two = f >= s(11.28 - 9.22);
  // the twelve on a ring, oldest at 12 o'clock, clockwise
  const cx = 540, cy = 720, R = 290, d = 132;
  return (
    <AbsoluteFill style={{ background: L.bg }}>
      <svg width={1080} height={1920} style={{ position: "absolute" }}>
        <circle cx={cx} cy={cy} r={R} fill="none" stroke={L.rule} strokeWidth={2} />
      </svg>
      {ONES.map((c, i) => {
        const a = (i / 12) * Math.PI * 2 - Math.PI / 2;
        const on = two ? c.y < 1919 : c.n === CENT.n;
        const appear = interpolate(f - i * 2, [0, 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return (
          <div key={c.n} style={{ position: "absolute", left: cx + R * Math.cos(a) - d / 2, top: cy + R * Math.sin(a) - d / 2,
                                   width: d, height: d, borderRadius: "50%", opacity: appear,
                                   boxShadow: on ? `0 0 0 4px ${L.hi}, 0 0 28px ${L.hi}88` : "none" }}>
            <Img src={staticFile(`look/cents/${c.n}.webp`)}
                 style={{ ...CUT, width: d * 1.235, height: d * 1.235, margin: -d * 0.1175,
                          filter: on ? "none" : "brightness(0.42) saturate(0.6)" }} />
          </div>
        );
      })}
      <div style={{ position: "absolute", left: cx - 150, width: 300, top: cy, transform: "translateY(-50%)", textAlign: "center" }}>
        <div style={{ ...fr(100), fontWeight: 600, fontSize: 150, lineHeight: 1, color: L.hi }}>{two ? 2 : 12}</div>
      </div>
      <div style={{ position: "absolute", left: 104, width: 732, top: 1090, textAlign: "center" }}>
        <div style={{ ...caps(L, 42, L.dim, "0.3em") }}>{two ? "before 1919" : "1/1 Years"}</div>
        <div style={{ ...fr(0, 72), fontStyle: "italic", fontWeight: 400, fontSize: 54, marginTop: 12 }}>
          {two ? "1911 and 1912" : "one Cent alone in its year"}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const LOOK_COMPONENTS = { LookA, LookB, LookC };

/** Highlight candidates for look C (2026-10-28). Each is a colour CENTS already carries. */
export const C_HIGHLIGHTS: Record<string, string> = {
  Copper: "#d9925c",      // current: the Lead caption copper
  Rose: "#c99079",        // cents.gallery's light copper
  FullRed: "#e8744a",     // a Full Red Cent, bright mint copper
  Brass: "#d8b25a",       // the Gold trait, honey to pale amber
  Verdigris: "#76b7a6",   // the patina that grows on copper
  Paper: "#efe7dc",       // no colour: the highlight is weight and light alone
};
