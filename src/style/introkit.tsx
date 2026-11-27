import React from "react";
import { Img, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { EASE, useShotFade } from "./motion";
import { Imagery, SafeText } from "./Safe";
import { findPhrase, type Alignment } from "../lib/timeline";
import { useSpokenWords } from "./onecent";
import { LOOK_C } from "./storyopen";
import { loadFonts } from "./fonts";

loadFonts();

/**
 * Shots for the CENTS introduction film (2026-11-27), in Look C. Pictures are shown large, with a slow camera move,
 * and every label names what the picture is. Nothing here fakes a photograph: the type plates and the network are
 * drawings, and they say so by being drawings.
 */

type Anchored = { alignment: Alignment; shotStartFrame: number };
const L = LOOK_C;
const BRIGHT = "#d9925c";
const WEB_RED = "#68170e";        // the web introduction's red (shibboleth, 2026-11-26)
const fraunces = (soft: number, opsz = 144): React.CSSProperties =>
  ({ fontFamily: L.display, fontVariationSettings: `"opsz" ${opsz}, "SOFT" ${soft}, "WONK" 0` });
const caps = (size = 42, color: string = L.dim, spacing = "0.12em"): React.CSSProperties =>
  ({ fontFamily: L.mono, fontWeight: 500, fontSize: size, letterSpacing: spacing, textTransform: "uppercase", color });

function useAt({ alignment, shotStartFrame }: Anchored, who: string) {
  const { fps } = useVideoConfig();
  return (phrase: string, plus = 0) => {
    const f = Math.round((findPhrase(alignment, phrase).start + plus) * fps) - shotStartFrame;
    if (f < 0) throw new Error(`${who}: "${phrase}" is spoken before this shot starts`);
    return f;
  };
}
const ramp = (frame: number, from: number, len: number) =>
  interpolate(frame, [from, from + len], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });

/** The picture area: full width, from just under the top interface to above the label band. */
const PIC = { x0: 0, y0: 300, x1: 1080, y1: 1150 };
const LABEL_Y = 1176;

const Label: React.FC<{ text?: string; kicker?: string; o?: number }> = ({ text, kicker, o = 1 }) => !text && !kicker ? null : (
  <div style={{ position: "absolute", left: 104, width: 732, top: LABEL_Y, opacity: o }}>
    {kicker ? <SafeText role="label" fontSize={42} maxLines={2} style={caps(42, BRIGHT)}>{kicker}</SafeText> : null}
    {text ? <SafeText role="label" fontSize={42} maxLines={2} color={L.dim} style={{ fontFamily: L.sans, lineHeight: 1.25, marginTop: kicker ? 8 : 0 }}>{text}</SafeText> : null}
  </div>
);

/** A camera move over an image: scale and centre (fractions of the image) from `a` to `b` across the shot. */
type Cam = { k: number; x: number; y: number };
function useCam(a: Cam, b: Cam) {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const t = interpolate(frame, [0, Math.max(1, durationInFrames)], [0, 1], { extrapolateRight: "clamp", easing: EASE.inOut });
  return { k: a.k + (b.k - a.k) * t, x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t };
}

/**
 * Draws an image (or clip) of size w x h into the box so that, at k = 1, it covers the box (`cover`) or fits inside
 * it (`contain`), then applies the camera (k, centre x/y). A cover crop never zooms out past covering, so no edge shows.
 */
const Framed: React.FC<{ src: string; w: number; h: number; box: typeof PIC; fit: "cover" | "contain"; cam: Cam; video?: boolean; startFrom?: number }> =
  ({ src, w, h, box, fit, cam, video, startFrom }) => {
  const bw = box.x1 - box.x0, bh = box.y1 - box.y0;
  const base = fit === "cover" ? Math.max(bw / w, bh / h) : Math.min(bw / w, bh / h);
  const s = base * Math.max(fit === "cover" ? 1 : 0.2, cam.k);
  const W = w * s, H = h * s;
  let left = bw / 2 - cam.x * W, top = bh / 2 - cam.y * H;
  if (fit === "cover") { left = Math.min(0, Math.max(bw - W, left)); top = Math.min(0, Math.max(bh - H, top)); }
  const style: React.CSSProperties = { position: "absolute", left, top, width: W, height: H };
  return (
    <div style={{ position: "absolute", left: box.x0, top: box.y0, width: bw, height: bh, overflow: "hidden" }}>
      {video ? <OffthreadVideo src={staticFile(src)} style={style} muted startFrom={startFrom} /> : <Img src={staticFile(src)} style={style} />}
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/** The opening: the web introduction's cent sign melts into nothing, and the title rises where it was. */
export const IntroTitle: React.FC<Anchored & { melt: string; titleAt: number }> = (props) => {
  const { melt, titleAt } = props;
  const frame = useCurrentFrame();
  const t = ramp(frame, titleAt, 18);
  const by = ramp(frame, titleAt + 10, 16);
  return (
    <div style={{ position: "absolute", inset: 0, background: L.bg }}>
      <Imagery>
        <OffthreadVideo src={staticFile(melt)} muted style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 1920 }} />
      </Imagery>
      <div style={{ position: "absolute", left: 104, width: 732, top: 700, textAlign: "center", opacity: t, transform: `translateY(${(1 - t) * 24}px)` }}>
        <SafeText role="display" fontSize={190} maxLines={1} color={L.ink}
                  style={{ ...fraunces(0, 144), fontWeight: 200, letterSpacing: "0.06em", lineHeight: 1 }}>CENTS</SafeText>
      </div>
      <div style={{ position: "absolute", left: 104, width: 732, top: 920, textAlign: "center", opacity: by }}>
        <SafeText role="body" fontSize={64} maxLines={1} color={L.dim}
                  style={{ ...fraunces(50, 72), fontStyle: "italic", fontWeight: 300 }}>by Rutherford Chang</SafeText>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/** One picture, large, with a slow camera move and a label that names it. */
export const IntroPhoto: React.FC<Anchored & {
  src: string; w: number; h: number; label?: string; kicker?: string; fit?: "cover" | "contain";
  from?: Cam; to?: Cam; video?: boolean; startFrom?: number;
}> = (props) => {
  const { src, w, h, label, kicker, fit = "cover", from = { k: 1.0, x: 0.5, y: 0.5 }, to = { k: 1.08, x: 0.5, y: 0.5 }, video, startFrom } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const cam = useCam(from, to);
  const lab = ramp(frame, 4, 10);
  return (
    <div style={{ position: "absolute", inset: 0, background: L.bg, opacity: fade }}>
      <Imagery><Framed src={src} w={w} h={h} box={PIC} fit={fit} cam={cam} video={video} startFrom={startFrom} /></Imagery>
      <Label text={label} kicker={kicker} o={lab} />
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/** Several pictures in quick succession, each on its own phrase, under one label line that follows them. */
export const IntroSeq: React.FC<Anchored & {
  items: { at_phrase?: string; plus?: number; src: string; w: number; h: number; label?: string; fit?: "cover" | "contain"; from?: Cam; to?: Cam }[];
  kicker?: string;
}> = (props) => {
  const { items, kicker } = props;
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const fade = useShotFade();
  const at = useAt(props, "IntroSeq");
  const fs = items.map((it, i) => (i === 0 && !it.at_phrase ? 0 : at(it.at_phrase!, it.plus ?? 0)));
  for (let i = 1; i < fs.length; i++) if (fs[i]! <= fs[i - 1]!) throw new Error(`IntroSeq: item ${i + 1} does not come after item ${i}`);
  const cur = Math.max(0, fs.filter((f) => frame >= f).length - 1);
  const it = items[cur]!;
  const end = cur + 1 < fs.length ? fs[cur + 1]! : durationInFrames;
  const t = interpolate(frame, [fs[cur]!, end], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });
  const a = it.from ?? { k: 1, x: 0.5, y: 0.5 }, b = it.to ?? { k: 1.07, x: 0.5, y: 0.5 };
  const cam = { k: a.k + (b.k - a.k) * t, x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t };
  const pop = ramp(frame, fs[cur]!, 4);
  return (
    <div style={{ position: "absolute", inset: 0, background: L.bg, opacity: fade }}>
      <Imagery><div style={{ opacity: 0.35 + 0.65 * pop }}><Framed src={it.src} w={it.w} h={it.h} box={PIC} fit={it.fit ?? "cover"} cam={cam} /></div></Imagery>
      <Label text={it.label} kicker={kicker} />
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/** A quote lit word by word as it is spoken, over black or over a dimmed picture that moves slowly. */
export const IntroQuote: React.FC<Anchored & {
  quote: { at_phrase: string; text: string; spoken?: Record<string, string> }; who: string; where?: string; size?: number;
  figure?: { text: string; at_phrase: string; size?: number }; maxLines?: number; bg?: { src: string; w: number; h: number; from?: Cam; to?: Cam; dim?: number }; top?: number;
}> = (props) => {
  const { quote, who, where, size = 80, figure, bg, top = 560, maxLines = 7 } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props, "IntroQuote");
  const spoken = useSpokenWords(props, quote);
  const cam = useCam(bg?.from ?? { k: 1.0, x: 0.5, y: 0.5 }, bg?.to ?? { k: 1.1, x: 0.5, y: 0.5 });
  const tIn = ramp(frame, 2, 12);
  const fig = figure ? spring({ frame: frame - at(figure.at_phrase), fps: 30, config: { damping: 12, stiffness: 160, mass: 0.6 } }) : 0;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      {bg ? (
        <Imagery>
          <Framed src={bg.src} w={bg.w} h={bg.h} box={{ x0: 0, y0: 0, x1: 1080, y1: 1920 }} fit="cover" cam={cam} />
          <div style={{ position: "absolute", inset: 0, background: L.bg, opacity: bg.dim ?? 0.78 }} />
        </Imagery>
      ) : null}
      {figure ? (
        <div style={{ position: "absolute", left: 104, width: 732, top: top - 300, textAlign: "left", opacity: Math.min(1, fig), transform: `scale(${0.7 + 0.3 * fig})`, transformOrigin: "left center" }}>
          <SafeText role="display" fontSize={figure.size ?? 150} maxLines={1} color={BRIGHT} style={{ ...fraunces(100), fontWeight: 600, lineHeight: 1 }}>{figure.text}</SafeText>
        </div>
      ) : null}
      <div style={{ position: "absolute", left: 104, width: 732, top, opacity: tIn, transform: `translateY(${(1 - tIn) * 20}px)`,
                    borderLeft: `8px solid ${L.hi}`, paddingLeft: 44, boxSizing: "border-box" }}>
        <SafeText role="display" fontSize={size} maxLines={maxLines} color={L.ink}
                  style={{ ...fraunces(50, 72), fontStyle: "italic", fontWeight: 400, lineHeight: 1.16, textWrap: "pretty" }}
                  wordOpacity={spoken.map((f) => (frame >= f ? 1 : 0.32))}>{`“${quote.text}”`}</SafeText>
        <div style={{ marginTop: 44 }}>
          <SafeText role="label" fontSize={42} maxLines={1} style={caps(42, L.ink)}>{who}</SafeText>
          {where ? <SafeText role="body" fontSize={46} maxLines={2} color={L.dim}
                    style={{ ...fraunces(0, 36), fontStyle: "italic", fontWeight: 400, marginTop: 8, lineHeight: 1.2 }}>{where}</SafeText> : null}
        </div>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/** Large figures set as type, each arriving on its phrase; the earlier ones dim. A drawing, not a picture. */
export const IntroFigure: React.FC<Anchored & { kicker?: string; items: { at_phrase: string; big: string; small?: string; size?: number }[]; note?: string }> = (props) => {
  const { kicker, items, note } = props;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useShotFade();
  const at = useAt(props, "IntroFigure");
  const fs = items.map((it) => at(it.at_phrase));
  const cur = fs.filter((f) => frame >= f).length - 1;
  const gap = 330, y0 = 900 - ((items.length - 1) * gap) / 2 - 120;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      {kicker ? <div style={{ position: "absolute", left: 104, width: 732, top: 340, textAlign: "center" }}>
        <SafeText role="label" fontSize={42} maxLines={1} style={caps(42, L.dim)}>{kicker}</SafeText></div> : null}
      {items.map((it, i) => {
        if (frame < fs[i]!) return null;
        const pop = spring({ frame: frame - fs[i]!, fps, config: { damping: 12, stiffness: 170, mass: 0.6 } });
        return (
          <div key={i} style={{ position: "absolute", left: 104, width: 732, top: y0 + i * gap, textAlign: "center",
                                opacity: i === cur ? 1 : 0.38, transform: `scale(${0.65 + 0.35 * pop})` }}>
            <SafeText role="display" fontSize={it.size ?? 170} maxLines={1} color={i === cur ? BRIGHT : L.ink}
                      style={{ ...fraunces(100), fontWeight: 600, lineHeight: 1.05 }}>{it.big}</SafeText>
            {it.small ? <SafeText role="label" fontSize={44} maxLines={2} style={{ ...caps(44, L.ink, "0.1em"), marginTop: 10 }}>{it.small}</SafeText> : null}
          </div>
        );
      })}
      {note ? <div style={{ position: "absolute", left: 104, width: 732, top: 1240, textAlign: "center" }}>
        <SafeText role="label" fontSize={42} maxLines={2} color={L.dim} style={{ fontFamily: L.sans }}>{note}</SafeText></div> : null}
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/** Cents in quick succession, each a disc, under an optional quote lit as it is spoken. */
export const IntroFlash: React.FC<Anchored & {
  fronts: string[]; every?: number; label?: string;
  quote?: { at_phrase: string; text: string; spoken?: Record<string, string> }; who?: string;
}> = (props) => {
  const { fronts, every = 6, label, quote, who } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const spoken = useSpokenWords(props, quote);
  const i = Math.floor(frame / every) % fronts.length;
  const D = 640, S = D / 0.815;
  const dim = quote ? 0.38 : 1;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <Imagery>
        <div style={{ position: "absolute", left: 540 - D / 2, top: quote ? 330 : 420, width: D, height: D, borderRadius: "50%", overflow: "hidden", opacity: dim }}>
          <Img src={staticFile(fronts[i]!)} style={{ position: "absolute", left: D / 2 - S / 2, top: D / 2 - S / 2, width: S, height: S, clipPath: "circle(40.5% at 50% 50%)" }} />
        </div>
      </Imagery>
      {quote ? (
        <div style={{ position: "absolute", left: 104, width: 732, top: 760, borderLeft: `8px solid ${L.hi}`, paddingLeft: 44, boxSizing: "border-box" }}>
          <SafeText role="display" fontSize={78} maxLines={6} color={L.ink}
                    style={{ ...fraunces(50, 72), fontStyle: "italic", fontWeight: 400, lineHeight: 1.16, textWrap: "pretty" }}
                    wordOpacity={spoken.map((f) => (frame >= f ? 1 : 0.32))}>{`“${quote.text}”`}</SafeText>
          {who ? <div style={{ marginTop: 36 }}><SafeText role="label" fontSize={42} maxLines={1} style={caps(42, L.ink)}>{who}</SafeText></div> : null}
        </div>
      ) : null}
      {!quote ? <Label text={label} /> : null}
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/** Three Cents, one after another on phrases, each zoomed onto what its chip names. */
export const IntroTriple: React.FC<Anchored & { cents: { at_phrase: string; front: string; chip: string; n: number; trait: string; box: [number, number, number, number] }[] }> = (props) => {
  const { cents } = props;
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const fade = useShotFade();
  const at = useAt(props, "IntroTriple");
  const fs = cents.map((c, i) => (i === 0 ? 0 : at(c.at_phrase)));
  const cur = Math.max(0, fs.filter((f) => frame >= f).length - 1);
  const c = cents[cur]!;
  const end = cur + 1 < fs.length ? fs[cur + 1]! : durationInFrames;
  const t = interpolate(frame, [fs[cur]!, end], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });
  const D = 700, S0 = D / 0.815;
  const [x0, y0, x1, y1] = c.box;
  const kT = Math.min(2.6, (0.8 * D) / (Math.max(x1 - x0, y1 - y0) * S0));
  const k = 1 + (kT - 1) * t, cx = 0.5 + ((x0 + x1) / 2 - 0.5) * t, cy = 0.5 + ((y0 + y1) / 2 - 0.5) * t;
  const S = S0 * k;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <Imagery>
        <div style={{ position: "absolute", left: 540 - D / 2, top: 380, width: D, height: D, borderRadius: "50%", overflow: "hidden" }}>
          <Img src={staticFile(c.front)} style={{ position: "absolute", left: D / 2 - cx * S, top: D / 2 - cy * S, width: S, height: S, clipPath: k < 1.02 ? "circle(40.5% at 50% 50%)" : undefined }} />
        </div>
      </Imagery>
      <div style={{ position: "absolute", left: 104, width: 732, top: 1140, textAlign: "center" }}>
        <div style={{ display: "inline-block", background: L.hi, padding: "10px 22px" }}>
          <SafeText role="label" fontSize={46} maxLines={1} color={L.ink} style={{ fontFamily: L.mono, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase" }}>{c.chip}</SafeText>
        </div>
        <SafeText role="label" fontSize={42} maxLines={1} color={L.dim} style={{ fontFamily: L.mono, marginTop: 16 }}>{`Cent #${c.n} · ${c.trait}`}</SafeText>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/** The five forms, one tile per phrase, then all five together under a chip. */
type Tile = { at_phrase: string; label: string; src?: string; w?: number; h?: number; disc?: boolean; text?: [string, string] };
export const IntroForms: React.FC<Anchored & { tiles: Tile[]; all_at: string; chip: string }> = (props) => {
  const { tiles, all_at, chip } = props;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useShotFade();
  const at = useAt(props, "IntroForms");
  const fs = tiles.map((t) => at(t.at_phrase));
  const fAll = at(all_at);
  const all = ramp(frame, fAll, 14);
  const cur = fs.filter((f) => frame >= f).length - 1;
  // Solo: one tile large in the middle. All: a 2-3 grid.
  const solo = { x: 540, y: 760, s: 640 };
  const grid = (i: number) => { const row = i < 2 ? 0 : 1, col = i < 2 ? i : i - 2, n = i < 2 ? 2 : 3, s = n === 2 ? 330 : 230;
    return { x: 540 + (col - (n - 1) / 2) * (s + 24), y: row === 0 ? 560 : 920, s }; };
  const draw = (t: Tile, s: number) => t.text ? (
    <div style={{ width: s, height: s, background: "#16110f", border: `2px solid ${L.hi}`, boxSizing: "border-box", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", gap: s * 0.05 }}>
      <div style={{ ...caps(Math.max(16, s * 0.07), L.dim), fontSize: Math.max(16, s * 0.07) }}>{t.text[0]}</div>
      <div style={{ fontFamily: L.mono, fontSize: s * 0.11, color: BRIGHT, fontWeight: 500 }}>{t.text[1]}</div>
    </div>
  ) : t.disc ? (
    <div style={{ width: s, height: s, borderRadius: "50%", overflow: "hidden", position: "relative" }}>
      <Img src={staticFile(t.src!)} style={{ position: "absolute", left: s / 2 - s / 0.815 / 2, top: s / 2 - s / 0.815 / 2, width: s / 0.815, height: s / 0.815, clipPath: "circle(40.5% at 50% 50%)" }} />
    </div>
  ) : (
    <div style={{ width: s, height: s, overflow: "hidden", position: "relative" }}>
      <Img src={staticFile(t.src!)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    </div>
  );
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <Imagery>
        {tiles.map((t, i) => {
          if (frame < fs[i]!) return null;
          const g = grid(i);
          const isCur = i === cur && all === 0;
          const pop = spring({ frame: frame - fs[i]!, fps, config: { damping: 13, stiffness: 180, mass: 0.6 } });
          const vis = all > 0 ? 1 : isCur ? 1 : 0;
          const x = isCur ? solo.x : g.x + (solo.x - g.x) * (1 - all) * (i === cur ? 1 : 0);
          const s = all > 0 ? solo.s + (g.s - solo.s) * all : solo.s;
          const xx = all > 0 ? solo.x + (g.x - solo.x) * all : x, yy = all > 0 ? solo.y + (g.y - solo.y) * all : solo.y;
          const ss = all > 0 ? (i === cur ? s : g.s) : s;
          const ox = all > 0 && i !== cur ? g.x : xx, oy = all > 0 && i !== cur ? g.y : yy;
          return vis ? (
            <div key={i} style={{ position: "absolute", left: ox - ss / 2, top: oy - ss / 2, opacity: all > 0 && i !== cur ? all : 1, transform: `scale(${isCur ? 0.85 + 0.15 * pop : 1})` }}>
              {draw(t, ss)}
            </div>
          ) : null;
        })}
      </Imagery>
      {all === 0 && cur >= 0 ? (
        <div style={{ position: "absolute", left: 104, width: 732, top: 1140, textAlign: "center" }}>
          <SafeText role="display" fontSize={84} maxLines={1} color={L.ink} style={{ ...fraunces(50, 72), fontStyle: "italic", fontWeight: 400 }}>{tiles[cur]!.label}</SafeText>
        </div>
      ) : null}
      {all > 0 ? (
        <div style={{ position: "absolute", left: 104, width: 732, top: 1170, textAlign: "center", opacity: all }}>
          <div style={{ display: "inline-block", background: L.hi, padding: "10px 22px" }}>
            <SafeText role="label" fontSize={46} maxLines={1} color={L.ink} style={{ fontFamily: L.mono, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase" }}>{chip}</SafeText>
          </div>
        </div>
      ) : null}
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/** A post set as type (not a screenshot): name, handle and date, the words lit as they are read. */
export const IntroPost: React.FC<Anchored & { name: string; handle: string; date: string; quote: { at_phrase: string; text: string; spoken?: Record<string, string> }; context?: string }> = (props) => {
  const { name, handle, date, quote, context } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const spoken = useSpokenWords(props, quote);
  const tIn = ramp(frame, 0, 10);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <div style={{ position: "absolute", left: 104, width: 732, top: 480, opacity: tIn, transform: `translateY(${(1 - tIn) * 16}px)`,
                    background: "#15110f", border: "2px solid #2a221e", borderRadius: 28, padding: "44px 44px 40px", boxSizing: "border-box" }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 18, flexWrap: "wrap" }}>
          <SafeText role="body" fontSize={50} maxLines={1} color={L.ink} style={{ fontFamily: L.sans, fontWeight: 600 }}>{name}</SafeText>
          <SafeText role="label" fontSize={42} maxLines={1} color={L.dim} style={{ fontFamily: L.mono }}>{handle}</SafeText>
        </div>
        {context ? <SafeText role="body" fontSize={48} maxLines={3} color={L.dim} style={{ fontFamily: L.sans, lineHeight: 1.3, marginTop: 26 }}>{context}</SafeText> : null}
        <SafeText role="body" fontSize={58} maxLines={6} color={L.ink} style={{ fontFamily: L.sans, lineHeight: 1.3, marginTop: context ? 10 : 26 }}
                  wordOpacity={spoken.map((f) => (frame >= f ? 1 : 0.3))}>{quote.text}</SafeText>
        <SafeText role="label" fontSize={42} maxLines={1} color={L.dim} style={{ fontFamily: L.mono, marginTop: 30 }}>{date}</SafeText>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/**
 * From a state to a public network, drawn: one node holding the record, then the record copied to many nodes that
 * link to each other. A diagram of the idea, not a map of Bitcoin's real nodes.
 */
export const IntroNetwork: React.FC<Anchored & { net_at: string; lines: { at_phrase: string; text: string }[]; one: string }> = (props) => {
  const { net_at, lines, one } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const at = useAt(props, "IntroNetwork");
  const fNet = at(net_at);
  const grow = ramp(frame, fNet, 30);
  // Seeded nodes in a disc.
  const N = 46; const nodes: { x: number; y: number; d: number }[] = [];
  let h = 7;
  const rnd = () => ((h = (h * 1103515245 + 12345) % 2147483648) / 2147483648);
  for (let i = 0; i < N; i++) { const a = rnd() * Math.PI * 2, r = Math.sqrt(rnd()) * 330; nodes.push({ x: 540 + Math.cos(a) * r, y: 760 + Math.sin(a) * r * 0.95, d: 0 }); }
  nodes.forEach((n) => (n.d = Math.hypot(n.x - 540, n.y - 760)));
  const edges: [number, number][] = [];
  nodes.forEach((a, i) => { const near = nodes.map((b, j) => [j, Math.hypot(a.x - b.x, a.y - b.y)] as [number, number]).filter(([j]) => j !== i).sort((p, q) => p[1] - q[1]).slice(0, 3);
    near.forEach(([j]) => { if (i < j) edges.push([i, j]); }); });
  const pulse = (frame % 45) / 45;
  const ls = lines.map((l) => at(l.at_phrase));
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <Imagery>
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          {edges.map(([i, j], k) => {
            const a = nodes[i]!, b = nodes[j]!; const vis = grow > Math.max(a.d, b.d) / 340 ? 1 : 0;
            return <line key={k} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={L.hi} strokeWidth={3} opacity={0.75 * vis} />;
          })}
          {nodes.map((n, i) => { const vis = grow > n.d / 340 ? 1 : 0; const lit = Math.abs(n.d / 340 - pulse) < 0.08;
            return <circle key={i} cx={n.x} cy={n.y} r={lit ? 15 : 11} fill={lit ? BRIGHT : "#5a3a30"} opacity={vis} />; })}
          <circle cx={540} cy={760} r={46 + 0 * grow} fill={grow > 0 ? BRIGHT : L.hi} opacity={1 - 0.6 * grow} />
        </svg>
      </Imagery>
      <div style={{ position: "absolute", left: 104, width: 732, top: 1160, textAlign: "center" }}>
        {grow === 0 ? <SafeText role="label" fontSize={46} maxLines={1} style={caps(46, L.ink)}>{one}</SafeText>
          : lines.map((l, i) => frame >= ls[i]! ? (
            <SafeText key={i} role="label" fontSize={46} maxLines={1} style={{ ...caps(46, i === ls.filter((f) => frame >= f).length - 1 ? L.ink : L.dim), marginTop: i ? 10 : 0 }}>{l.text}</SafeText>) : null)}
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------------------------------------ */
/** The end card: the title again, and where to look next. */
export const IntroEnd: React.FC<Anchored & { sites: string[] }> = (props) => {
  const { sites } = props;
  const frame = useCurrentFrame();
  const fade = useShotFade();
  const t = ramp(frame, 0, 16), s = ramp(frame, 12, 14);
  return (
    <div style={{ position: "absolute", inset: 0, opacity: fade, background: L.bg }}>
      <div style={{ position: "absolute", left: 104, width: 732, top: 640, textAlign: "center", opacity: t }}>
        <SafeText role="display" fontSize={170} maxLines={1} color={L.ink} style={{ ...fraunces(0, 144), fontWeight: 200, letterSpacing: "0.06em", lineHeight: 1 }}>CENTS</SafeText>
        <SafeText role="body" fontSize={60} maxLines={1} color={L.dim} style={{ ...fraunces(50, 72), fontStyle: "italic", fontWeight: 300, marginTop: 30 }}>by Rutherford Chang</SafeText>
      </div>
      <div style={{ position: "absolute", left: 104, width: 732, top: 1000, textAlign: "center", opacity: s }}>
        <div style={{ width: 120, height: 6, background: WEB_RED, margin: "0 auto 40px" }} />
        {sites.map((u, i) => <SafeText key={i} role="body" fontSize={58} maxLines={1} color={BRIGHT} style={{ fontFamily: L.mono, marginTop: i ? 16 : 0 }}>{u}</SafeText>)}
      </div>
    </div>
  );
};

/** These read the recording (phrases), so the shot runner hands them the alignment. */
for (const C of [IntroTitle, IntroPhoto, IntroSeq, IntroQuote, IntroFigure, IntroFlash, IntroTriple, IntroForms, IntroPost, IntroNetwork, IntroEnd])
  (C as any).wantsAlignment = true;

export const INTROKIT = { IntroTitle, IntroPhoto, IntroSeq, IntroQuote, IntroFigure, IntroFlash, IntroTriple, IntroForms, IntroPost, IntroNetwork, IntroEnd } as const;
