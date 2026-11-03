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
 * The Gap, a year on. v2: one picture per beat (~27 shots), from many sources.
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

/** A still, slowly pushed in or panned (Ken Burns). `box` is where it sits; full-bleed when omitted. */
const Photo: React.FC<{ src: string; x?: number; y?: number; w?: number; h?: number; zoom?: number; pan?: [number, number];
  origin?: string; fit?: "cover" | "contain"; opacity?: number }> =
  ({ src, x = 0, y = 0, w = 1080, h = 1920, zoom = 0.08, pan = [0, 0], origin = "50% 50%", fit = "cover", opacity = 1 }) => {
    const f = useCurrentFrame();
    const k = ease(f, 0, 300);
    return (
      <div style={{ position: "absolute", left: x, top: y, width: w, height: h, overflow: "hidden", opacity }}>
        <Img src={staticFile(`the-gap/ftg/${src}`)} style={{ width: "100%", height: "100%", objectFit: fit, transformOrigin: origin,
          transform: `translate(${pan[0] * k}px, ${pan[1] * k}px) scale(${1 + zoom * k})` }} />
      </div>
    );
  };

/** Label at the top of the frame, over a shade so it reads on any picture. */
const Label: React.FC<{ children: string; sub?: string; on?: number }> = ({ children, sub, on = 1 }) => (
  <div style={{ opacity: on }}>
    <TopShade />
    <Text y={290} size={46}>{children}</Text>
    {sub ? <Text y={350} size={42} color={COLOR.inkDim}>{sub}</Text> : null}
  </div>
);

const BottomShade: React.FC = () => (
  <div style={{ position: "absolute", left: 0, right: 0, top: 1240, height: 420,
                background: "linear-gradient(rgba(11,10,10,0), rgba(11,10,10,0.82) 30%, rgba(11,10,10,0.82) 75%, rgba(11,10,10,0))" }} />
);

// ------------------------------------------------------------------ scenes (v2: one picture per beat)

const TRAITS: Record<string, [string, string]> = {
  t_verdigris: ["verdigris", "Verdigris"], t_obsidian: ["obsidian", "Obsidian"],
  t_fingerprints: ["fingerprints", "Fingerprints"], t_ghost: ["ghost", "Ghost"],
};

const Scene: React.FC<{ id: string }> = ({ id }) => {
  const f = useCurrentFrame();
  const L = (p: string) => local(id, p);
  const hero = picks.heroes.copper!;
  if (TRAITS[id]) {
    const [k, name] = TRAITS[id]!;
    const n = picks.heroes[k]!;
    return (<AbsoluteFill>
      <HiCent n={n} size={640} x={220} y={400} scale={1.04 + 0.06 * ease(f, 0, 45)} />
      <Text y={290} size={42} color={COLOR.inkDim}>Named by the Trait Council</Text>
      <Text y={1110} size={64} weight={700} color={COLOR.accent}>{name}</Text>
      <Text y={1195} size={42} mono color={COLOR.inkDim}>{`CENT #${n} · ${picks.years[String(n)]}`}</Text>
    </AbsoluteFill>);
  }
  switch (id) {
    case "open":
      // Frame 0 is the 10,000-Cent mosaic and the date: never black.
      return (<AbsoluteFill>
        <Photo src="mosaic_crop.jpg" zoom={0.06} />
        <AbsoluteFill style={{ background: COLOR.bg, opacity: 0.5 }} />
        <Text y={300} size={42} color={COLOR.ink}>Philadelphia</Text>
        <Text y={360} size={96} weight={700} color={COLOR.accent}>{"12 November\n2025"}</Text>
      </AbsoluteFill>);
    case "press": {
      const s = L("struck its last");
      return (<AbsoluteFill>
        <Photo src="press.jpg" x={130} y={420} w={820} h={740} zoom={0.1} origin="40% 45%" />
        <Text y={290} size={42} color={COLOR.inkDim}>{"Coining presses, Philadelphia Mint,\nabout 1916 (Library of Congress)"}</Text>
        <Text y={1190} size={46} opacity={ease(f, s, s + 10)}>{"The last cent struck\nfor circulation"}</Text>
      </AbsoluteFill>);
    }
    case "tender":
      return (<AbsoluteFill>
        <div style={{ position: "absolute", inset: 0, transformOrigin: "50% 75%", transform: `scale(${1 + 0.25 * ease(f, 0, 100)})` }}>
          <HiCent n={hero} size={660} x={210} y={500} back scale={1} />
        </div>
        <Label sub={`CENT #${hero}, back`}>1¢: still legal tender</Label>
      </AbsoluteFill>);
    case "till": {
      const r = L("round a cash"), st = L("twenty states");
      const rounded = f >= r + 8;
      return (<AbsoluteFill>
        <Field dim={0.82} drift={-0.5 * f} size={150} top={-40} />
        <div style={{ position: "absolute", left: 104, top: 420, width: 732, height: 330, background: COLOR.surface, borderRadius: 16,
                      border: `3px solid ${COLOR.rule}`, boxSizing: "border-box" }} />
        <Text x={144} y={450} w={652} size={42} color={COLOR.inkDim}>Cash total</Text>
        <Text x={144} y={530} w={652} size={150} mono weight={600} color={rounded ? COLOR.accent : COLOR.ink}>{rounded ? "$4.95" : "$4.97"}</Text>
        <Text x={144} y={690} w={652} size={42} color={COLOR.inkDim} opacity={ease(f, r + 8, r + 18)}>rounded to the nearest 5¢</Text>
        <Text y={300} size={120} weight={700} color={COLOR.accent} opacity={ease(f, st, st + 10)}>20</Text>
        <Text x={260} y={318} w={576} size={46} opacity={ease(f, st + 4, st + 14)}>{"states with cash-rounding\nlaws, by July 2026"}</Text>
      </AbsoluteFill>);
    }
    case "capitol":
      return (<AbsoluteFill>
        <Photo src="capitol.jpg" x={0} y={420} w={1080} h={875} zoom={0.1} origin="50% 30%" />
        <Text y={290} size={46}>{"Common Cents Act: passed\nby Congress, September 2026"}</Text>
      </AbsoluteFill>);
    case "away": {
      const a = L("rounded away");
      return (<AbsoluteFill>
        <Field dim={0.85} drift={0.5 * f} size={150} top={-300} />
        <Text y={300} size={42} color={COLOR.inkDim}>Face value</Text>
        <div style={{ opacity: 1 - 0.7 * ease(f, a + 6, a + 30) }}>
          <Text y={420} size={360} mono weight={600} color={COLOR.accent} align="center">1¢</Text>
        </div>
        <div style={{ position: "absolute", left: 140, top: 640, height: 10, background: COLOR.ink, width: 660 * ease(f, a, a + 16), transform: "rotate(-12deg)" }} />
      </AbsoluteFill>);
    }
    case "ingots":
      return (<AbsoluteFill>
        <Photo src="ingots.jpg" x={200} y={560} w={680} h={677} zoom={0.1} />
        <Text y={290} size={42} color={COLOR.inkDim}>Copper, London Metal Exchange</Text>
        <Text y={340} size={110} mono weight={600} color={COLOR.accent}>$14,875</Text>
        <Text y={470} size={42}>{"a tonne: record high, 10 Sep 2026"}</Text>
        <Text y={1250} size={42} color={COLOR.inkDim}>{"Casting copper ingots, 1942"}</Text>
      </AbsoluteFill>);
    case "hero":
      return (<AbsoluteFill>
        <HiCent n={hero} size={620} x={230} y={380} />
        <Text y={1050} size={46}>{`CENT #${hero} · ${picks.years[String(hero)]}`}</Text>
        <Text y={1112} size={46} color={COLOR.accent} opacity={ease(f, L("ninety-five percent"), L("ninety-five percent") + 10)}>{"Pre-1983 cent: 95% copper,\n3.11 g"}</Text>
      </AbsoluteFill>);
    case "melt":
      return (<AbsoluteFill>
        <div style={{ position: "absolute", inset: 0, transformOrigin: "50% 40%", transform: `scale(${1.5 + 0.15 * ease(f, 0, 140)})` }}>
          <HiCent n={hero} size={620} x={230} y={380} scale={1} opacity={0.5} />
        </div>
        <Text y={300} size={42} color={COLOR.inkDim}>Copper in one cent, at the record</Text>
        <Text y={560} size={240} mono weight={700} color={COLOR.accent} align="center" opacity={ease(f, L("worth more"), L("worth more") + 10)}>{`${MELT_CENTS.toFixed(1)}¢`}</Text>
        <Text y={880} size={42} align="center" color={COLOR.ink} opacity={ease(f, L("worth more"), L("worth more") + 10)}>{"3.11 g × 95% × $14,875 a tonne"}</Text>
      </AbsoluteFill>);
    case "bars": {
      const x0 = 104 + 732 / SCALE_MAX, x1 = 104 + 732 * MELT_CENTS / SCALE_MAX;
      const m = L("its copper has said");
      return (<AbsoluteFill>
        <Field dim={0.88} drift={-0.5 * f} size={150} top={-40} />
        <Text y={420} size={64} weight={700}>The coin says 1¢.</Text>
        <Text y={520} size={64} weight={700} color={COLOR.accent} opacity={ease(f, m, m + 10)}>Its copper says more.</Text>
        <Bars grow={ease(f, 0, 30)} />
        <div style={{ position: "absolute", left: x0, top: BAR1, width: (x1 - x0) * ease(f, m, m + 20), height: 56,
                      border: `3px dashed ${COLOR.accent}`, borderLeft: "none", boxSizing: "border-box", borderRadius: "0 8px 8px 0" }} />
        <Text x={x1 - 300} y={BAR1 - 60} w={300} align="right" size={42} color={COLOR.accent} opacity={ease(f, m + 10, m + 22)}>the gap</Text>
      </AbsoluteFill>);
    }
    case "split": {
      const d = L("what the state decrees"), h = L("what the metal holds");
      return (<AbsoluteFill>
        <Photo src="capitol.jpg" x={0} y={360} w={538} h={800} zoom={0.06} origin="50% 30%" opacity={0.3 + 0.7 * ease(f, d - 6, d + 4)} />
        <Photo src="ingots.jpg" x={542} y={360} w={538} h={800} zoom={0.06} opacity={0.3 + 0.7 * ease(f, h - 6, h + 4)} />
        <Text x={104} y={1180} w={380} size={42} opacity={ease(f, d, d + 10)}>what the state decrees</Text>
        <Text x={570} y={1180} w={290} size={42} color={COLOR.accent} opacity={ease(f, h, h + 10)}>what the metal holds</Text>
        <Text y={290} size={42} color={COLOR.inkDim}>the gap</Text>
      </AbsoluteFill>);
    }
    case "mosaic": {
      const s = 2.6 - 1.6 * ease(f, 0, 80);
      return (<AbsoluteFill>
        <div style={{ position: "absolute", left: 120, top: 400, width: 840, height: 840, overflow: "hidden" }}>
          <Img src={staticFile("the-gap/ftg/mosaic_full.jpg")} style={{ width: 840, height: 840, transform: `scale(${s})` }} />
        </div>
        <Text y={290} size={46} opacity={ease(f, 10, 22)}>CENTS · 10,000 Cents</Text>
      </AbsoluteFill>);
    }
    case "desk":
      return (<AbsoluteFill>
        <Photo src="desk_cents.jpg" x={0} y={410} w={1080} h={900} zoom={0.12} origin="45% 70%" />
        <Label>{"Rutherford Chang's desk"}</Label>
      </AbsoluteFill>);
    case "arm":
      return (<AbsoluteFill>
        <Photo src="desk_arm.jpg" x={0} y={410} w={1080} h={900} zoom={0.1} origin="70% 50%" />
        <Label>{"His camera stand and laptop"}</Label>
      </AbsoluteFill>);
    case "frontback": {
      const b = 12;
      const n = 19;
      return (<AbsoluteFill>
        <HiCent n={n} size={420} x={80} y={560} />
        <HiCent n={n} size={420} x={580} y={560} back opacity={ease(f, b, b + 8)} />
        <Text y={290} size={46}>{`CENT #${n}, front and back`}</Text>
        <Text x={80} y={1010} w={420} size={46} align="center">front</Text>
        <Text x={456} y={1010} w={380} size={46} align="center" opacity={ease(f, b, b + 8)}>back</Text>
      </AbsoluteFill>);
    }
    case "pour":
      return (<AbsoluteFill>
        <Footage src="the-gap/ftg/pour.mp4" start={0.5} zoom={0.05} />
        <BottomShade />
        <Label>Casting CENTS Block Copper</Label>
      </AbsoluteFill>);
    case "block":
      return (<AbsoluteFill>
        <Photo src="block_still.jpg" x={0} y={400} w={1080} h={1080} zoom={0.08} />
        <Label sub="31 kg · 68.56 lb">CENTS Block Copper</Label>
      </AbsoluteFill>);
    case "grid": {
      const lay = { cols: 7, size: 120, gap: 10 };
      const drift = interpolate(f, [0, 300], [0, -260], clamp);
      const step = Math.floor(Math.max(0, f - 20) / 22);
      const row = 2 + Math.floor(-drift / 130) + (step % 3);
      const col = (step * 3 + 1) % 7;
      const n = picks.field[row * 7 + col];
      const left = (1080 - (7 * 130 - 10)) / 2;
      return (<AbsoluteFill>
        <div style={{ position: "absolute", left, top: 420 + drift }}>
          <CentGrid ns={picks.field.slice(0, 140)} layout={lay} from={-20} enterFrames={0} />
          {f > 20 && n ? <div style={{ position: "absolute", left: col * 130 - 5, top: row * 130 - 5, width: 130, height: 130,
                                        border: `4px solid ${COLOR.accent}`, borderRadius: "50%", boxSizing: "border-box" }} /> : null}
        </div>
        <div style={{ position: "absolute", left: 0, right: 0, top: 240, height: 180, background: COLOR.bg }} />
        <Text y={290} size={46}>{"Each front on its own satoshi,\nMarch 2024"}</Text>
        <div style={{ position: "absolute", left: 0, right: 0, top: 1160, bottom: 0, background: COLOR.bg }} />
        {f > 20 && n ? <Text y={1180} size={46} mono color={COLOR.accent}>{`CENT #${n}`}</Text> : null}
        {f > 20 && n ? <Text y={1240} size={42} mono color={COLOR.inkDim}>{`inscription ${Number(picks.inscription_numbers[String(n)]).toLocaleString("en-US")}`}</Text> : null}
      </AbsoluteFill>);
    }
    case "natures":
      return (<AbsoluteFill>
        <Photo src="natures.jpg" x={90} y={400} w={900} h={900} zoom={0.05} />
        <Text y={290} size={46}>The five natures of a Cent</Text>
      </AbsoluteFill>);
    case "ucca":
      return (<AbsoluteFill>
        <Photo src="ucca.jpg" x={0} y={420} w={1080} h={860} zoom={0.12} origin="60% 50%" />
        <Text y={290} size={42} color={COLOR.ink}>{"Hundreds and Thousands, UCCA\nBeijing, 17 Jan – 12 Apr 2026"}</Text>
      </AbsoluteFill>);
    case "lab":
      return (<AbsoluteFill>
        <Photo src="traitslab.jpg" x={0} y={420} w={1080} h={860} zoom={0.25} origin="20% 15%" />
        <Text y={290} size={42}>{"Traits named by the Trait Council,\nover two years of voting"}</Text>
      </AbsoluteFill>);
    case "rolls":
      return (<AbsoluteFill>
        <Photo src="rolls.jpg" x={0} y={410} w={1080} h={900} zoom={0.1} />
        <Label>Penny rolls, Chang's desk</Label>
      </AbsoluteFill>);
    case "close": {
      const out = f + sceneStart["close"]! >= TAIL_FROM ? ease(f + sceneStart["close"]! - TAIL_FROM, 0, 18) : 0;
      return (<AbsoluteFill>
        <div style={{ opacity: 1 - out }}>
          <Photo src="mosaic_crop.jpg" zoom={-0.06} pan={[0, -120]} />
          <AbsoluteFill style={{ background: COLOR.bg, opacity: 0.25 }} />
        </div>
        <div style={{ opacity: out }}>
          <Text y={540} size={110} weight={700} align="center">CENTS</Text>
          <Text y={690} size={52} align="center" color={COLOR.inkDim}>by Rutherford Chang</Text>
          <Text y={790} size={46} align="center" color={COLOR.accent}>cents.gallery</Text>
          <Text y={880} size={42} align="center" color={COLOR.inkDim}>{"Sources: US Mint, 12 Nov 2025;\nReuters (LME), Sep 2026"}</Text>
          <Text y={990} size={42} align="center" color={COLOR.inkDim}>{"State laws as of July 2026;\nCommon Cents Act, Sep 2026"}</Text>
          <Text y={1100} size={42} align="center" color={COLOR.inkDim}>{"Archival: Library of Congress\n(Keystone; FSA/OWI; Highsmith)"}</Text>
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
