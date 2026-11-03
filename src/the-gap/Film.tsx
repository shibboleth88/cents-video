import React from "react";
import { AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { CANVAS, COLOR, TYPE } from "../style/tokens";
import { CentGrid, CentImage } from "../style/grids";
import { SafeText } from "../style/Safe";
import { StyledCaptions } from "../style/captions";
import { findPhrase, type Alignment } from "../lib/timeline";
import alignmentJson from "../../films/the-gap/script/alignment.json";
import picksJson from "../../films/the-gap/build/picks.json";
import cuesJson from "../../films/the-gap/captions/cues.json";
import scenesJson from "../../films/the-gap/build/scenes.json";

/**
 * The Gap, a year on. v1.
 *
 * Every cut and in-scene beat is a phrase of the narration (findPhrase), so a new
 * take re-times the film with no edits here. Imagery is real: CENTS Cents (300px
 * on-chain images as cutouts; 1050px cents.vision fronts for heroes), Chang's
 * cent rolls, and the casting of CENTS Block Copper, all from the user's own
 * collection. Every figure on screen carries its date (epoch rule).
 */

const al = alignmentJson as unknown as Alignment;
const cues = cuesJson as unknown as { start: number; end: number; text: string }[];
const picks = picksJson as unknown as { field: number[]; heroes: Record<string, number>;
  inscription_numbers: Record<string, number>; years: Record<string, number> };
const FPS = CANVAS.fps;
const at = (p: string) => Math.round(findPhrase(al, p).start * FPS);
const END = Math.ceil(al.duration * FPS);
export const DURATION = END;
const TAIL_FROM = Math.round((al.words[al.words.length - 1]!.end + 1.2) * FPS); // end card

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = (f: number, a: number, b: number) => interpolate(f, [a, b], [0, 1], clamp);

const SCENES = (scenesJson as unknown as { scenes: { id: string; from: string | null; to: string | null }[] }).scenes;
const sceneStart: Record<string, number> = Object.fromEntries(SCENES.map((s) => [s.id, s.from ? at(s.from) : 0]));
const local = (scene: string, phrase: string) => at(phrase) - sceneStart[scene]!;

// ------------------------------------------------------------------ pieces

const Text: React.FC<{ x?: number; y: number; w?: number; size?: number; color?: string; weight?: number;
  mono?: boolean; align?: "left" | "right" | "center"; opacity?: number; children: string }> =
  ({ x = 104, y, w = 732, size = 46, color = COLOR.ink, weight = 500, mono, align = "left", opacity = 1, children }) => (
    <div style={{ position: "absolute", left: x, top: y, width: w, opacity }}>
      <SafeText role={size >= 64 ? "display" : size >= 46 ? "body" : "label"} fontSize={size} color={color} maxLines={3}
        style={{ fontFamily: mono ? TYPE.mono : size >= 64 ? TYPE.display : TYPE.body, fontWeight: weight, textAlign: align,
                 whiteSpace: "pre-line", lineHeight: 1.15 }}>{children}</SafeText>
    </div>
  );

/** A 1050px cents.vision front, cut out on black. The coin fills ~81.5% of the photo. */
const HiCent: React.FC<{ n: number; size: number; x: number; y: number; back?: boolean; opacity?: number; scale?: number }> =
  ({ n, size, x, y, back, opacity = 1, scale }) => {
    // A slow push-in by default, so a held Cent never reads as a frozen frame.
    const f = useCurrentFrame();
    if (scale === undefined) scale = 1 + 0.06 * ease(f, 0, 360);
    const box = size / 0.815;
    return (
      <div style={{ position: "absolute", left: x - (box - size) / 2, top: y - (box - size) / 2, width: box, height: box,
                    opacity, transform: `scale(${scale})` }}>
        <Img src={staticFile(`the-gap/hi/${n}${back ? "_back" : ""}.webp`)}
             style={{ width: box, height: box, clipPath: "circle(40.5% at 50% 50%)" }} />
      </div>
    );
  };

/** The field: a random sample of Cents, shown as texture only (never as trait evidence). */
const Field: React.FC<{ dim?: number; drift?: number; size?: number; top?: number }> = ({ dim = 0.5, drift = 0, size = 104, top = 120 }) => {
  const gap = 8, cols = 10;
  const left = (1080 - (cols * (size + gap) - gap)) / 2;
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left, top: top + drift }}>
        <CentGrid ns={picks.field} layout={{ cols, size, gap }} texture from={-20} enterFrames={0} />
      </div>
      <AbsoluteFill style={{ background: COLOR.bg, opacity: dim }} />
    </AbsoluteFill>
  );
};

const Bar: React.FC<{ y: number; fill: number; color: string; label: string; value: string; on?: number }> =
  ({ y, fill, color, label, value, on = 1 }) => (
    <div style={{ opacity: on }}>
      <Text y={y - 60} size={42} color={COLOR.inkDim}>{label}</Text>
      <div style={{ position: "absolute", left: 104, top: y, width: 732, height: 56, border: `3px solid ${COLOR.rule}`, borderRadius: 8, boxSizing: "border-box" }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${fill * 100}%`, background: color, borderRadius: 4 }} />
      </div>
      <Text x={104} y={y + 66} size={46} mono>{value}</Text>
    </div>
  );

/** Copper in a pre-1983 cent at the LME record: 3.11 g x 95% x $14,875/t = 4.395 cents. */
const MELT_CENTS = (3.11 * 0.95 * 14875) / 1e6 * 100;
const SCALE_MAX = 5; // cents across the full bar
const BAR1 = 960, BAR2 = 1150;
const Bars: React.FC<{ grow: number; on?: number }> = ({ grow, on = 1 }) => (
  <>
    <Bar y={BAR1} fill={1 / SCALE_MAX} color={COLOR.inkDim} label="Face value" value="1¢" on={on} />
    <Bar y={BAR2} fill={(MELT_CENTS / SCALE_MAX) * grow} color={COLOR.accent}
         label="Its copper, 10 Sep 2026" value={`≈ ${MELT_CENTS.toFixed(1)}¢`} on={on} />
  </>
);

const Footage: React.FC<{ src: string; start?: number; zoom?: number }> = ({ src, start = 0, zoom = 0 }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <OffthreadVideo src={staticFile(src)} muted startFrom={Math.round(start * FPS)}
        style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${1 + zoom * ease(f, 0, 300)})` }} />
    </AbsoluteFill>
  );
};

const TopShade: React.FC = () => (
  <div style={{ position: "absolute", left: 0, right: 0, top: 240, height: 200, background: "linear-gradient(rgba(11,10,10,0.75), rgba(11,10,10,0))" }} />
);

// ------------------------------------------------------------------ scenes

const Scene: React.FC<{ id: string }> = ({ id }) => {
  const f = useCurrentFrame();
  const L = (p: string) => local(id, p);
  switch (id) {
    case "open": {
      // Frame 0 is the field and the date, never black.
      return (<AbsoluteFill>
        <Field dim={0.62} drift={-f * 0.5} />
        <Text y={300} size={42} color={COLOR.inkDim}>Philadelphia</Text>
        <Text y={360} size={96} weight={700} color={COLOR.accent}>{"12 November\n2025"}</Text>
        <Text y={620} size={52} opacity={ease(f, L("struck its last"), L("struck its last") + 10)}>{"The last cent struck\nfor circulation"}</Text>
      </AbsoluteFill>);
    }
    case "round": {
      const r = L("round a cash"), act = L("Common Cents Act"), away = L("rounded away");
      const rounded = f >= r + 8;
      return (<AbsoluteFill>
        <Field dim={0.85} drift={-140 - f * 0.4} />
        <div style={{ position: "absolute", left: 104, top: 330, width: 732, height: 330, background: COLOR.surface, borderRadius: 16,
                      border: `3px solid ${COLOR.rule}`, boxSizing: "border-box" }} />
        <Text x={144} y={360} w={652} size={42} color={COLOR.inkDim}>Cash total</Text>
        <Text x={144} y={440} w={652} size={150} mono weight={600} color={rounded ? COLOR.accent : COLOR.ink}>{rounded ? "$4.95" : "$4.97"}</Text>
        <Text x={144} y={600} w={652} size={42} color={COLOR.inkDim} opacity={ease(f, r + 8, r + 18)}>rounded to the nearest 5¢</Text>
        <Text y={720} size={46} opacity={ease(f, 0, 12) * (1 - 0.65 * ease(f, away, away + 20))}>1¢: still legal tender</Text>
        <Text y={800} size={46} opacity={ease(f, L("twenty states"), L("twenty states") + 12)}>{"20 states: cash-rounding laws,\nby July 2026"}</Text>
        <Text y={940} size={46} opacity={ease(f, act, act + 12)}>{"Common Cents Act: passed\nby Congress, September 2026"}</Text>
        <div style={{ position: "absolute", left: 104, top: 748, height: 4, width: 330 * ease(f, away + 6, away + 26), background: COLOR.accent }} />
      </AbsoluteFill>);
    }
    case "copper": {
      const s = L("A cent struck before"), w = L("At that peak");
      return (<AbsoluteFill>
        {f < s ? (<>
          <Field dim={0.88} drift={-300 - f * 0.4} />
          <Text y={360} size={46} color={COLOR.inkDim} opacity={ease(f, 0, 10)}>Copper, London Metal Exchange</Text>
          <Text y={440} size={120} mono weight={600} color={COLOR.accent} opacity={ease(f, 6, 18)}>$14,875</Text>
          <Text y={600} size={46} opacity={ease(f, 10, 22)}>{"per tonne: the record high,\n10 September 2026"}</Text>
        </>) : (<>
          <HiCent n={picks.heroes.copper!} size={400} x={340} y={330} opacity={ease(f, s, s + 12)} />
          <Text y={760} size={46} opacity={ease(f, s + 6, s + 18)}>{`CENT #${picks.heroes.copper} · ${picks.years[String(picks.heroes.copper)]}`}</Text>
          <Text y={820} size={42} color={COLOR.inkDim} opacity={ease(f, L("ninety-five percent"), L("ninety-five percent") + 10)}>Pre-1983 cent: 95% copper, 3.11 g</Text>
          <Bars grow={ease(f, w + 10, w + 50)} on={ease(f, w, w + 12)} />
        </>)}
      </AbsoluteFill>);
    }
    case "gap": {
      const g = L("That gap"), c = L("where CENTS begins");
      const x0 = 104 + 732 / SCALE_MAX, x1 = 104 + 732 * MELT_CENTS / SCALE_MAX;
      if (f >= c) {
        const k = f - c;
        return (<AbsoluteFill>
          <Field dim={0.5 - 0.15 * ease(k, 0, 40)} drift={-k * 0.6} />
          <Text y={560} size={110} weight={700} align="center" opacity={ease(k, 0, 14)}>CENTS</Text>
          <Text y={710} size={52} align="center" color={COLOR.inkDim} opacity={ease(k, 6, 20)}>Rutherford Chang</Text>
        </AbsoluteFill>);
      }
      return (<AbsoluteFill>
        <HiCent n={picks.heroes.copper!} size={400} x={340} y={330} />
        <Text y={740} size={46} opacity={ease(f, 0, 10)}>The coin says 1¢.</Text>
        <Text y={796} size={46} color={COLOR.accent} opacity={ease(f, L("its copper has said"), L("its copper has said") + 10)}>Its copper says more.</Text>
        <Bars grow={1} />
        {/* The gap drawn on the face-value bar: from where face value ends to where the copper ends. */}
        <div style={{ position: "absolute", left: x0, top: BAR1, width: (x1 - x0) * ease(f, g, g + 20), height: 56,
                      border: `3px dashed ${COLOR.accent}`, borderLeft: "none", boxSizing: "border-box", borderRadius: "0 8px 8px 0" }} />
        <Text x={x1 - 300} y={BAR1 - 60} w={300} align="right" size={42} color={COLOR.accent} opacity={ease(f, g + 10, g + 22)}>the gap</Text>
      </AbsoluteFill>);
    }
    case "removed": {
      const p = L("photographed each one");
      return (<AbsoluteFill>
        {f < p ? (<>
          <div style={{ position: "absolute", left: 0, top: 330, width: 1080, height: 810, overflow: "hidden" }}>
            <Img src={staticFile("the-gap/ftg/rolls.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover",
              transform: `scale(${1.02 + 0.06 * ease(f, 0, p)})` }} />
          </div>
          <Text y={1170} size={42} color={COLOR.inkDim}>{"Penny rolls on Rutherford Chang's desk"}</Text>
        </>) : (<>
          <HiCent n={picks.heroes.copper!} size={380} x={104 + 0} y={460} opacity={ease(f, p, p + 10)} />
          <HiCent n={picks.heroes.copper!} size={380} x={836 - 380} y={460} back opacity={ease(f, L("front and back"), L("front and back") + 10)} />
          <Text y={380} size={42} color={COLOR.inkDim} opacity={ease(f, p, p + 10)}>{`CENT #${picks.heroes.copper}, photographed`}</Text>
          <Text x={104} y={870} w={380} size={46} align="center" opacity={ease(f, p + 6, p + 16)}>front</Text>
          <Text x={456} y={870} w={380} size={46} align="center" opacity={ease(f, L("front and back") + 6, L("front and back") + 16)}>back</Text>
        </>)}
      </AbsoluteFill>);
    }
    case "melted": {
      const k = L("thirty-one kilograms");
      return (<AbsoluteFill>
        <Footage src="the-gap/ftg/pour.mp4" start={0.5} zoom={0.05} />
        <TopShade />
        <div style={{ position: "absolute", left: 0, right: 0, top: 1240, height: 400, background: "linear-gradient(rgba(11,10,10,0), rgba(11,10,10,0.8) 30%, rgba(11,10,10,0.8) 75%, rgba(11,10,10,0))" }} />
        <Text y={300} size={46}>Casting CENTS Block Copper</Text>
        <Text y={364} size={46} mono color={COLOR.accent} opacity={ease(f, k, k + 10)}>31 kg · 68.56 lb</Text>
      </AbsoluteFill>);
    }
    case "inscribed": {
      const lay = { cols: 7, size: 120, gap: 10 };
      const drift = interpolate(f, [0, 300], [0, -260], clamp);
      const step = Math.floor(Math.max(0, f - 24) / 26);
      const row = 2 + Math.floor(-drift / 130) + (step % 3);
      const col = (step * 3 + 1) % 7;
      const n = picks.field[row * 7 + col];
      const left = (1080 - (7 * 130 - 10)) / 2;
      return (<AbsoluteFill>
        <div style={{ position: "absolute", left, top: 420 + drift }}>
          <CentGrid ns={picks.field.slice(0, 140)} layout={lay} enterFrames={30} />
          {f > 24 && n ? <div style={{ position: "absolute", left: col * 130 - 5, top: row * 130 - 5, width: 130, height: 130,
                                        border: `4px solid ${COLOR.accent}`, borderRadius: "50%", boxSizing: "border-box" }} /> : null}
        </div>
        <div style={{ position: "absolute", left: 0, right: 0, top: 240, height: 180, background: COLOR.bg }} />
        <Text y={290} size={46}>{"Each front on its own satoshi,\nMarch 2024"}</Text>
        <div style={{ position: "absolute", left: 0, right: 0, top: 1160, bottom: 0, background: COLOR.bg }} />
        {f > 24 && n ? <Text y={1180} size={46} mono color={COLOR.accent}>{`CENT #${n}`}</Text> : null}
        {f > 24 && n ? <Text y={1240} size={42} mono color={COLOR.inkDim}>{`inscription ${Number(picks.inscription_numbers[String(n)]).toLocaleString("en-US")}`}</Text> : null}
      </AbsoluteFill>);
    }
    case "natures": {
      const items: [string, string][] = [["unit of currency", "a unit of currency"], ["quantity of copper", "a quantity of copper"],
        ["part of a sculpture", "part of a sculpture"], ["a photograph", "a photograph"], ["Bitcoin inscription", "a Bitcoin inscription"]];
      return (<AbsoluteFill>
        <HiCent n={picks.heroes.copper!} size={420} x={330} y={330} scale={1 + 0.03 * ease(f, 0, 240)} />
        {items.map(([ph, label], i) => (
          <Text key={ph} y={830 + i * 76} size={52} color={i === 4 ? COLOR.accent : COLOR.ink} opacity={ease(f, L(ph), L(ph) + 10)}>{label}</Text>
        ))}
      </AbsoluteFill>);
    }
    case "traits": {
      const cells: [string, string, number, number][] = [["verdigris", "Verdigris", 140, 405], ["obsidian", "Obsidian", 520, 405],
        ["fingerprints", "Fingerprints", 140, 840], ["ghost", "Ghost", 520, 840]];
      const v = L("Over two years");
      return (<AbsoluteFill>
        <Text y={290} size={42} color={COLOR.inkDim} opacity={ease(f, v, v + 12)}>{"Traits, named by the Trait Council\nover two years of voting"}</Text>
        {cells.map(([k, label, x, y]) => {
          const t = L(k);
          const n = picks.heroes[k]!;
          return (<React.Fragment key={k}>
            <HiCent n={n} size={310} x={x} y={y} opacity={0.22 + 0.78 * ease(f, t - 4, t + 8)} />
            <Text x={x - 10} y={y + 318} w={330} size={42} align="center" color={COLOR.accent} opacity={ease(f, t, t + 10)}>{`${label}\n#${n}`}</Text>
          </React.Fragment>);
        })}
      </AbsoluteFill>);
    }
    case "close": {
      const out = f + sceneStart["close"]! >= TAIL_FROM ? ease(f + sceneStart["close"]! - TAIL_FROM, 0, 18) : 0;
      return (<AbsoluteFill>
        <div style={{ opacity: 1 - out }}><Field dim={0.3} drift={-f * 0.7} size={96} /></div>
        <div style={{ opacity: out }}>
          <Text y={600} size={110} weight={700} align="center">CENTS</Text>
          <Text y={750} size={52} align="center" color={COLOR.inkDim}>by Rutherford Chang</Text>
          <Text y={860} size={46} align="center" color={COLOR.accent}>cents.gallery</Text>
          <Text y={960} size={42} align="center" color={COLOR.inkDim}>{"Sources: US Mint, 12 Nov 2025;\nReuters (LME), Sep 2026"}</Text>
          <Text y={1070} size={42} align="center" color={COLOR.inkDim}>{"State laws as of July 2026;\nCommon Cents Act, Sep 2026"}</Text>
        </div>
      </AbsoluteFill>);
    }
  }
  return null;
};

export const Film: React.FC<{ captions: boolean }> = ({ captions }) => (
  <AbsoluteFill data-canvas-root="1" style={{ background: COLOR.bg }}>
    <Audio src={staticFile("the-gap/vo.wav")} />
    {SCENES.map((s) => {
      const from = s.from ? at(s.from) : 0;
      const to = s.to ? at(s.to) : END;
      return <Sequence key={s.id} from={from} durationInFrames={Math.max(1, to - from)} name={s.id}><Scene id={s.id} /></Sequence>;
    })}
    {captions ? <StyledCaptions cues={cues} alignment={al} look="lead" /> : null}
  </AbsoluteFill>
);

export const FilmClean: React.FC = () => <Film captions={false} />;
export const FilmCaptioned: React.FC = () => <Film captions />;
