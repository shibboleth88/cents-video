import React from "react";
import {
  AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame,
} from "remotion";
import { CANVAS, COLOR, TYPE } from "../style/tokens";
import { CentGrid, CentImage, fitGrid } from "../style/grids";
import { CaptionLayer } from "../style/components";
import { SafeText } from "../style/Safe";
import { findPhrase, type Alignment } from "../lib/timeline";
import alignmentJson from "../../films/secret-history/script/alignment.json";
import chartJson from "../../films/secret-history/build/year_chart.json";
import picksJson from "../../films/secret-history/build/picks.json";
import cuesJson from "../../films/secret-history/captions/cues.json";
import scenesJson from "../../films/secret-history/build/scenes.json";

/**
 * Secret History of a Penny, visual pass 1.
 *
 * Every cut and every in-scene beat is a phrase of the narration (findPhrase),
 * so a re-recorded take re-times the film with no edits here. Footage is the
 * user's own (pour, Block, the 1971 Cent on the Block) plus the Nixon address of
 * 15 August 1971. Where no rights-cleared archival image exists here, the beat is
 * carried by a diagram drawn from the sources of record, never by stock or
 * generated imagery.
 */

const al = alignmentJson as unknown as Alignment;
const cues = cuesJson as unknown as { start: number; end: number; text: string }[];
const chart = chartJson as unknown as {
  cell: number; base: number; x0: number;
  columns: Record<string, { x: number; w: number; count: number; top: number }>;
};
const picks = picksJson as unknown as { zoom: Record<string, number[]>; field: number[]; heroes: Record<string, number>;
  years: Record<string, number[]>; inscription_numbers: Record<string, string> };
const FPS = CANVAS.fps;
const TAIL = 4 * FPS; // end card after the last word

const sec = (p: string) => findPhrase(al, p).start;
const at = (p: string) => Math.round(sec(p) * FPS);
const END = Math.ceil(al.duration * FPS);
export const DURATION = END + TAIL;

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = (f: number, a: number, b: number) => interpolate(f, [a, b], [0, 1], clamp);

const SCENES = (scenesJson as unknown as { scenes: { id: string; from: string | null; to: string | null }[] }).scenes;
const sceneStart: Record<string, number> = Object.fromEntries(SCENES.map((s) => [s.id, s.from ? at(s.from) : 0]));
/** Frame of a phrase, relative to the start of the scene it falls in. */
const local = (scene: string, phrase: string) => at(phrase) - sceneStart[scene]!;

// ------------------------------------------------------------------ pieces

/** Positioned text through SafeText, so the safe-area, legibility and line-count
 *  gates measure every word on screen. "\n" breaks a line. */
const Text: React.FC<{ x?: number; y: number; w?: number; size?: number; color?: string; weight?: number;
  mono?: boolean; align?: "left" | "right"; opacity?: number; children: string }> =
  ({ x = 104, y, w = 732, size = 46, color = COLOR.ink, weight = 500, mono, align = "left", opacity = 1, children }) => (
    <div style={{ position: "absolute", left: x, top: y, width: w, opacity }}>
      <SafeText role={size >= 64 ? "display" : size >= 46 ? "body" : "label"} fontSize={size} color={color} maxLines={3}
        style={{ fontFamily: mono ? TYPE.mono : size >= 64 ? TYPE.display : TYPE.body, fontWeight: weight, textAlign: align,
                 whiteSpace: "pre-line", lineHeight: 1.15 }}>{children}</SafeText>
    </div>
  );

const YEARS = Object.keys(chart.columns).map(Number);
const X1 = chart.x0 + YEARS.length * chart.columns[String(YEARS[0])]!.w;

/** All 10,000 Cents, one 3 px cell each, by year. */
const Chart: React.FC<{ reveal?: number; lit?: number[]; dim?: number; litGlow?: number }> =
  ({ reveal = 1, lit, dim = 0.8, litGlow = 1 }) => {
    const clipX = chart.x0 + (X1 - chart.x0) * reveal;
    const src = staticFile("secret-history/year_chart.png");
    return (
      <AbsoluteFill>
        <div style={{ position: "absolute", inset: 0, clipPath: `inset(0 ${1080 - clipX}px 0 0)`, opacity: lit ? 1 - dim : 1 }}>
          <Img src={src} style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 1920 }} />
        </div>
        {lit?.map((y) => {
          const c = chart.columns[String(y)]!;
          const top = Math.min(c.top, chart.base - 3);
          return (
            <div key={y} style={{ position: "absolute", left: c.x, top, width: c.w, height: chart.base - top, overflow: "hidden", opacity: litGlow }}>
              <Img src={src} style={{ position: "absolute", left: -c.x, top: -top, width: 1080, height: 1920 }} />
            </div>
          );
        })}
        <div style={{ position: "absolute", left: chart.x0, width: X1 - chart.x0, top: chart.base + 2, height: 2, background: COLOR.rule, opacity: reveal > 0 ? 1 : 0 }} />
        <Text x={chart.x0} y={chart.base + 12} w={200} size={42} mono color={COLOR.inkDim}>1910</Text>
        <Text x={X1 - 200} y={chart.base + 12} w={200} size={42} mono color={COLOR.inkDim} align="right" opacity={reveal >= 1 ? 1 : 0}>1982</Text>
      </AbsoluteFill>
    );
  };

/** A column marker under the axis, pointing at one year. */
const Tick: React.FC<{ year: number; opacity?: number }> = ({ year, opacity = 1 }) => {
  const c = chart.columns[String(year)]!;
  return <div style={{ position: "absolute", left: c.x + c.w / 2 - 2, top: chart.base + 4, width: 4, height: 6, background: COLOR.accent, opacity }} />;
};

const Hero: React.FC<{ year: string; size?: number; top?: number; enter?: number }> = ({ year, size = 400, top = 330, enter = 0 }) => {
  const f = useCurrentFrame();
  const t = ease(f, enter, enter + 15);
  return (
    <div style={{ position: "absolute", left: 540 - size / 2, top, opacity: t, transform: `scale(${0.94 + 0.06 * t})` }}>
      <CentImage n={picks.heroes[year]!} size={size} />
    </div>
  );
};

const YearHead: React.FC<{ year: string; sub: string }> = ({ year, sub }) => (
  <>
    <Text y={290} size={64} weight={700} color={COLOR.accent}>{year}</Text>
    <Text x={420} y={300} w={416} size={42} color={COLOR.inkDim} align="right">{sub}</Text>
  </>
);

const Box: React.FC<{ x: number; y: number; w: number; h: number; label: string; on: number; accent?: boolean }> =
  ({ x, y, w, h, label, on, accent }) => (
    <div style={{ position: "absolute", left: x, top: y, width: w, height: h, opacity: on,
                  border: `3px solid ${accent ? COLOR.accent : COLOR.inkDim}`, borderRadius: 12, display: "flex",
                  alignItems: "center", justifyContent: "center", textAlign: "center", fontFamily: TYPE.body,
                  fontSize: 44, color: accent ? COLOR.accent : COLOR.ink, boxSizing: "border-box", padding: 10 }}>{label}</div>
  );

const Arrow: React.FC<{ x: number; y: number; w: number; on: number }> = ({ x, y, w, on }) => (
  <div style={{ position: "absolute", left: x, top: y - 2, width: w * on, height: 4, background: COLOR.inkDim }}>
    <div style={{ position: "absolute", right: -2, top: -8, width: 0, height: 0, borderTop: "10px solid transparent",
                  borderBottom: "10px solid transparent", borderLeft: `16px solid ${COLOR.inkDim}`, opacity: on >= 0.98 ? 1 : 0 }} />
  </div>
);

/** A horizontal gauge against face value: 0..1 filled. */
const Gauge: React.FC<{ y: number; fill: number; color: string; label: string; value: string }> = ({ y, fill, color, label, value }) => (
  <>
    <Text y={y - 62} size={42} color={COLOR.inkDim}>{label}</Text>
    <div style={{ position: "absolute", left: 104, top: y, width: 732, height: 64, border: `3px solid ${COLOR.inkDim}`, borderRadius: 8, boxSizing: "border-box" }}>
      <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${fill * 100}%`, background: color, borderRadius: 4 }} />
    </div>
    <Text y={y + 76} size={42} mono color={COLOR.ink}>{value}</Text>
    <Text x={636} y={y + 76} w={200} size={42} mono color={COLOR.inkDim} align="right">face</Text>
  </>
);

const Footage: React.FC<{ src: string; x: number; y: number; w: number; h: number; start?: number; fit?: "cover" | "contain"; zoom?: number }> =
  ({ src, x, y, w, h, start = 0, fit = "cover", zoom = 0 }) => {
    const f = useCurrentFrame();
    const s = 1 + zoom * ease(f, 0, 240);
    return (
      <div style={{ position: "absolute", left: x, top: y, width: w, height: h, overflow: "hidden" }}>
        <OffthreadVideo src={staticFile(src)} muted startFrom={Math.round(start * FPS)}
          style={{ width: "100%", height: "100%", objectFit: fit, transform: `scale(${s})` }} />
      </div>
    );
  };

// ------------------------------------------------------------------ scenes

const Scene: React.FC<{ id: string }> = ({ id }) => {
  const f = useCurrentFrame();
  switch (id) {
    case "open": {
      const r = ease(f, 6, 140);
      const year = 1910 + Math.min(72, Math.floor(r * 73));
      return (<AbsoluteFill>
        <Chart reveal={r} />
        <Text y={300} size={64} weight={700} opacity={ease(f, 0, 20)}>{"The mint years\nin CENTS"}</Text>
        <Text y={470} size={120} weight={700} mono color={COLOR.accent} opacity={r > 0 ? 1 : 0}>{String(year)}</Text>
      </AbsoluteFill>);
    }
    case "thesis": {
      const marks = [1944, 1964, 1971, 1979, 1982];
      return (<AbsoluteFill>
        <Chart lit={marks} dim={interpolate(f, [0, 40], [0, 0.55], clamp)} />
        {marks.map((y, i) => <Tick key={y} year={y} opacity={ease(f, 20 + i * 12, 30 + i * 12)} />)}
        <Text y={300} size={46} color={COLOR.inkDim}>{"10,000 Cents, one cell each,\nstacked by the year on their face"}</Text>
      </AbsoluteFill>);
    }
    case "y1943": {
      const years = ["1940", "1941", "1942", "1943", "1944", "1945", "1946"];
      return (<AbsoluteFill>
        <Chart lit={years.map(Number)} dim={0.85} />
        <Text y={290} size={46} color={COLOR.inkDim}>1940 to 1946, every Cent</Text>
        <div style={{ position: "absolute", left: 104, top: 380, width: 736, display: "flex", gap: 6 }}>
          {years.map((y, i) => {
            const ns = picks.zoom[y]!;
            const lay = ns.length ? fitGrid(ns.length, 94, 560) : null;
            return (
              <div key={y} style={{ width: 100, display: "flex", flexDirection: "column", alignItems: "center", opacity: ease(f, i * 4, i * 4 + 12) }}>
                <div style={{ height: 560, width: 100, display: "flex", alignItems: "flex-end", justifyContent: "center",
                              border: ns.length ? "none" : `3px dashed ${COLOR.accent}`, boxSizing: "border-box", borderRadius: 8 }}>
                  {lay ? <CentGrid ns={ns} layout={lay} enterFrames={20} from={i * 4} texture={lay.size < 60} /> : null}
                </div>
                <div style={{ fontFamily: TYPE.mono, fontSize: 42, color: y === "1943" ? COLOR.accent : COLOR.inkDim, marginTop: 8 }}>{y.slice(2)}</div>
              </div>
            );
          })}
        </div>
        <Text x={384} y={1040} w={452} size={46} color={COLOR.accent} opacity={ease(f, local("y1943", "That year copper"), local("y1943", "That year copper") + 12)}>
          1943: no Cents
        </Text>
        {/* The coin CENTS does not hold: a 1943 steel cent, NNC (public domain). */}
        <div style={{ position: "absolute", left: 104, top: 1030, opacity: ease(f, local("y1943", "struck in steel"), local("y1943", "struck in steel") + 12) }}>
          <Img src={staticFile("secret-history/ftg/steel1943.png")} style={{ width: 250, height: 250 }} />
        </div>
        <Text x={384} y={1110} w={452} size={42} color={COLOR.inkDim} opacity={ease(f, local("y1943", "struck in steel"), local("y1943", "struck in steel") + 12)}>
          {"Steel cent, 1943\nNational Numismatic\nCollection"}
        </Text>
      </AbsoluteFill>);
    }
    case "y1944": {
      const a = local("y1944", "tie their currencies"), b = local("y1944", "and the dollar to gold"), c = local("y1944", "thirty-five dollars");
      return (<AbsoluteFill>
        <Chart lit={[1944]} dim={0.9} />
        <YearHead year="1944" sub={`${chart.columns["1944"]!.count} Cents\nCENT #${picks.heroes["1944"]}`} />
        {/* Archival first, then the mechanism. Photo: OWI via NARA RG 208, public domain. */}
        <div style={{ position: "absolute", left: 104, top: 400, width: 732, height: 593, overflow: "hidden", opacity: 1 - ease(f, a - 12, a - 2) }}>
          <Img src={staticFile("secret-history/ftg/bw_morgenthau.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover",
            transform: `scale(${1.0 + 0.06 * ease(f, 0, a)})` }} />
        </div>
        <Text y={1010} size={42} color={COLOR.inkDim} opacity={1 - ease(f, a - 12, a - 2)}>
          {"Henry Morgenthau Jr. opens the\nconference, July 1944"}
        </Text>
        <div style={{ opacity: ease(f, a - 8, a + 4) }}><Hero year="1944" size={360} top={390} /></div>
        <Box x={104} y={820} w={240} h={130} label="44 currencies" on={ease(f, a - 6, a + 6)} />
        <Arrow x={350} y={885} w={60} on={ease(f, a + 4, a + 16)} />
        <Box x={416} y={820} w={110} h={130} label="$" on={ease(f, a + 10, a + 20)} accent />
        <Arrow x={532} y={885} w={88} on={ease(f, b, b + 12)} />
        <Box x={626} y={820} w={210} h={130} label="gold" on={ease(f, b + 6, b + 16)} />
        <Text y={970} size={46} mono color={COLOR.accent} opacity={ease(f, c, c + 10)}>$35 = 1 troy ounce</Text>
        <Text y={1036} size={42} color={COLOR.inkDim} opacity={ease(f, a, a + 15)}>Bretton Woods, July 1944</Text>
      </AbsoluteFill>);
    }
    case "y1964": {
      const hoard = local("y1964", "People hoard change"), lose = local("y1964", "Then dimes and quarters");
      const yrs = ["1963", "1964", "1965"];
      const phaseA = f < hoard, phaseC = f >= lose;
      const drain = phaseC ? 0.934 * (1 - ease(f, lose + 4, lose + 30)) : 0.934 * ease(f, 8, 40);
      return (<AbsoluteFill>
        <Chart lit={[1963, 1964, 1965]} dim={0.9} />
        <YearHead year="1964" sub={`${chart.columns["1964"]!.count} Cents\nCENT #${picks.heroes["1964"]}`} />
        {phaseA || phaseC ? (<>
          <Hero year="1964" size={340} top={390} />
          <Gauge y={860} fill={drain} color="#c9ccd1"
                 label={phaseC ? "Silver in a 1965 dime" : "Silver value of a 1964 dime"}
                 value={phaseC ? "none (clad)" : "≈ 93% of face"} />
        </>) : (
          <div style={{ position: "absolute", left: 104, top: 400, width: 872, display: "flex", gap: 30, alignItems: "flex-end", height: 640 }}>
            {yrs.map((y, i) => {
              const ns = picks.years[y];
              const count = chart.columns[y]!.count;
              return (
                <div key={y} style={{ width: 232, display: "flex", flexDirection: "column", alignItems: "center", opacity: ease(f, hoard + i * 6, hoard + i * 6 + 12) }}>
                  {ns ? <CentGrid ns={ns} layout={{ cols: 12, size: 17, gap: 2 }} texture enterFrames={24} from={hoard + i * 6} /> : null}
                  <div style={{ fontFamily: TYPE.mono, fontSize: 42, color: y === "1964" ? COLOR.accent : COLOR.inkDim, marginTop: 10 }}>{y}</div>
                  <div style={{ fontFamily: TYPE.mono, fontSize: 42, color: COLOR.ink }}>{count}</div>
                </div>
              );
            })}
          </div>
        )}
      </AbsoluteFill>);
    }
    case "y1971":
      return (<AbsoluteFill>
        <Chart lit={[1971]} dim={0.9} />
        <YearHead year="1971" sub={`${chart.columns["1971"]!.count} Cents\nCENT #${picks.heroes["1971"]}`} />
        {/* The clean head of the user's own Nixon edit runs 3.9 s; after it, the front page. */}
        <Sequence durationInFrames={Math.round(3.9 * FPS)}>
          <Footage src="secret-history/ftg/nixon_hd.mp4" x={104} y={390} w={732} h={549} fit="cover" />
          <Text y={950} w={520} size={42} color={COLOR.inkDim}>Televised address, 15 August 1971</Text>
        </Sequence>
        <Sequence from={Math.round(3.9 * FPS)}>
          <div style={{ position: "absolute", left: 104, top: 470, width: 732, height: 396, overflow: "hidden" }}>
            <Img src={staticFile("secret-history/ftg/nyt1971.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover",
              transform: `scale(${1.02 + 0.08 * ease(f - Math.round(3.9 * FPS), 0, 150)})` }} />
          </div>
          <Text y={890} w={520} size={42} color={COLOR.inkDim}>{"The New York Times,\n16 August 1971"}</Text>
        </Sequence>
      </AbsoluteFill>);
    case "y1971b":
      return (<AbsoluteFill>
        <Footage src="secret-history/ftg/face1971.mp4" x={0} y={420} w={1080} h={1080} zoom={0.06} />
        <Text y={300} size={42} color={COLOR.inkDim} opacity={ease(f, 0, 15)}>{`CENT #${picks.heroes["1971"]} over CENTS Block 839969`}</Text>
      </AbsoluteFill>);
    case "y1979":
      return (<AbsoluteFill>
        <Chart lit={[1979]} dim={0.88} />
        <YearHead year="1979" sub={`${chart.columns["1979"]!.count} Cents\nCENT #${picks.heroes["1979"]}`} />
        <Hero year="1979" size={460} top={420} />
      </AbsoluteFill>);
    case "y1982": {
      const stop = local("y1982", "The collection stops there");
      const pre = f < stop;
      const disc = (x: number, label: string, core: string, ring: string, on: number) => (
        <div style={{ position: "absolute", left: x, top: 820, width: 340, opacity: on, textAlign: "center" }}>
          <div style={{ width: 200, height: 200, margin: "0 auto", borderRadius: "50%", background: core, border: `10px solid ${ring}`, boxSizing: "border-box" }} />
          <div style={{ fontFamily: TYPE.body, fontSize: 42, color: COLOR.ink, marginTop: 14, lineHeight: 1.15 }}>{label}</div>
        </div>
      );
      const z = local("y1982", "the Mint switches to zinc");
      return (<AbsoluteFill>
        <Chart lit={pre ? [1982] : YEARS} dim={pre ? 0.9 : 0} />
        <YearHead year="1982" sub={`${chart.columns["1982"]!.count} Cents\nCENT #${picks.heroes["1982"]}`} />
        {pre ? (<>
          <Hero year="1982" size={330} top={400} />
          {disc(104, "95% copper", COLOR.accent, COLOR.accent, ease(f, 10, 25))}
          {disc(496, "97.5% zinc, copper-plated", "#9aa0a6", COLOR.accent, ease(f, z, z + 12))}
        </>) : (
          <>
            <div style={{ position: "absolute", left: X1 + 4, top: 560, width: 4, height: chart.base - 560, background: COLOR.accent, opacity: ease(f, stop, stop + 10) }} />
            <Text y={430} size={46} color={COLOR.ink} opacity={ease(f, stop, stop + 10)}>{"No Cent is dated\nlater than 1982"}</Text>
          </>
        )}
      </AbsoluteFill>);
    }
    case "block": {
      const turn = Math.round(0.5 * (at("As inscriptions") - sceneStart["block"]!));
      return (<AbsoluteFill>
        <Sequence durationInFrames={turn}>
          <Footage src="secret-history/ftg/pour.mp4" x={0} y={0} w={1080} h={1920} start={3} />
          <div style={{ position: "absolute", left: 0, right: 0, top: 260, height: 90, background: "linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0))" }} />
          <Text y={290} size={42} color={COLOR.ink}>Casting CENTS Block Copper</Text>
        </Sequence>
        <Sequence from={turn}>
          {/* The rotating model, white keyed to the film's ground (build: block_dark.mp4). */}
          <Footage src="secret-history/ftg/block_dark.mp4" x={0} y={260} w={1080} h={1080} start={3} zoom={0.04} />
          <Text y={290} size={42} color={COLOR.inkDim}>CENTS Block 839969</Text>
        </Sequence>
      </AbsoluteFill>);
    }
    case "close": {
      const lay = { cols: 8, size: 104, gap: 8 };
      const drift = interpolate(f, [0, 400], [0, -420]);
      // One Cent at a time is named by its inscription: the same object, read as a record.
      const step = Math.floor(Math.max(0, f - 50) / 24);
      const row = 2 + Math.floor(-drift / 112) + (step % 3);
      const col = (step * 3 + 1) % 6;
      const k = row * 8 + col;
      const n = picks.field[k];
      const out = 1 - ease(f, END - sceneStart["close"]! - 10, END - sceneStart["close"]! + 10);
      return (<AbsoluteFill style={{ opacity: out }}>
        <div style={{ position: "absolute", left: 92, top: 300 + drift }}>
          <CentGrid ns={picks.field} layout={lay} enterFrames={60} />
          {f > 50 && n ? <div style={{ position: "absolute", left: col * 112 - 4, top: row * 112 - 4, width: 112, height: 112,
                                        border: `4px solid ${COLOR.accent}`, borderRadius: "50%", boxSizing: "border-box" }} /> : null}
        </div>
        {f > 50 && n ? <div style={{ position: "absolute", left: 80, top: 1190, width: 780, height: 140, background: COLOR.bg }} /> : null}
        {f > 50 && n ? <Text y={1196} size={46} mono color={COLOR.accent}>{`CENT #${n}`}</Text> : null}
        {f > 50 && n ? <Text y={1252} size={46} mono color={COLOR.inkDim}>{`inscription ${Number(picks.inscription_numbers[String(n)]).toLocaleString("en-US")}`}</Text> : null}
      </AbsoluteFill>);
    }
  }
  return null;
};

const EndCard: React.FC = () => {
  const f = useCurrentFrame();
  const o = ease(f, 0, 15);
  return (<AbsoluteFill>
    <Text y={700} size={64} weight={700} opacity={o}>CENTS</Text>
    <Text y={790} size={46} color={COLOR.inkDim} opacity={o}>by Rutherford Chang</Text>
    <Text y={930} size={42} color={COLOR.inkDim} opacity={o}>Written and narrated by shibboleth</Text>
    <Text y={1000} size={42} color={COLOR.inkDim} opacity={o}>cents.gallery</Text>
    <Text y={1120} size={42} color={COLOR.inkDim} opacity={o}>{"Archival: US National Archives;\nNational Numismatic Collection,\nSmithsonian"}</Text>
  </AbsoluteFill>);
};

export const Film: React.FC<{ captions: boolean }> = ({ captions }) => (
  <AbsoluteFill data-canvas-root="1" style={{ background: COLOR.bg }}>
    <Audio src={staticFile("secret-history/vo.mp3")} />
    {SCENES.map((s) => {
      const from = s.from ? at(s.from) : 0;
      const to = s.to ? at(s.to) : END;
      return <Sequence key={s.id} from={from} durationInFrames={Math.max(1, to - from)} name={s.id}><Scene id={s.id} /></Sequence>;
    })}
    <Sequence from={END} durationInFrames={TAIL} name="endcard"><EndCard /></Sequence>
    {captions ? <CaptionLayer cues={cues} alignment={al} /> : null}
  </AbsoluteFill>
);

export const FilmClean: React.FC = () => <Film captions={false} />;
export const FilmCaptioned: React.FC = () => <Film captions />;
