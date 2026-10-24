import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { CANVAS, COLOR, TYPE } from "../style/tokens";
import { CentGrid, CentImage, fitGrid } from "../style/grids";
import { findPhrase, type Alignment } from "../lib/timeline";
import alignmentJson from "../../films/secret-history/script/alignment.json";
import chartJson from "../../films/secret-history/build/year_chart.json";
import picksJson from "../../films/secret-history/build/picks.json";

/**
 * Rough animatic for Secret History of a Penny. Every cut is a phrase of the
 * narration, so a different take re-times it with no edits here. Boxes marked
 * PLACEHOLDER stand for footage that lives on the user's Mac or still has to be
 * sourced; nothing in them is offered as evidence.
 */

const al = alignmentJson as unknown as Alignment;
const chart = chartJson as unknown as {
  cell: number; base: number; x0: number;
  columns: Record<string, { x: number; w: number; count: number; top: number }>;
};
const picks = picksJson as unknown as { zoom: Record<string, number[]>; field: number[]; heroes: Record<string, number> };
const FPS = CANVAS.fps;

const at = (p: string) => Math.round(findPhrase(al, p).start * FPS);
export const DURATION = Math.ceil(al.duration * FPS) + FPS;

const SCENES: { id: string; from: string | null; to: string | null }[] = [
  { id: "open", from: null, to: "Each date marks" },
  { id: "thesis", from: "Each date marks", to: "1943 is missing" },
  { id: "y1943", from: "1943 is missing", to: "1944 At Bretton" },
  { id: "y1944", from: "1944 At Bretton", to: "1964 The silver" },
  { id: "y1964", from: "1964 The silver", to: "1971 The dollar" },
  { id: "y1971", from: "1971 The dollar", to: "1979 Inflation" },
  { id: "y1979", from: "1979 Inflation", to: "1982 Copper has" },
  { id: "y1982", from: "1982 Copper has", to: "In the Block" },
  { id: "block", from: "In the Block", to: "As inscriptions" },
  { id: "close", from: "As inscriptions", to: null },
];

const Label: React.FC<{ y: number; size?: number; color?: string; children: React.ReactNode; weight?: number }> =
  ({ y, size = 46, color = COLOR.ink, children, weight = 500 }) => (
    <div style={{ position: "absolute", left: 104, right: 220, top: y, fontFamily: TYPE.body, fontSize: size,
                  fontWeight: weight, color, lineHeight: 1.15 }}>{children}</div>
  );

const Placeholder: React.FC<{ y: number; h: number; text: string }> = ({ y, h, text }) => (
  <div style={{ position: "absolute", left: 104, width: 732, top: y, height: h, border: `3px dashed ${COLOR.inkDim}`,
                display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", padding: 24,
                fontFamily: TYPE.mono, fontSize: 42, color: COLOR.inkDim, boxSizing: "border-box" }}>
    PLACEHOLDER<br />{text}
  </div>
);

/** The whole collection as a chart, one cell per Cent. `reveal` 0..1 sweeps it in by year. */
const Chart: React.FC<{ reveal?: number; lit?: number[]; dim?: number; squash?: number }> =
  ({ reveal = 1, lit, dim = 0.8, squash = 0 }) => {
    const x1 = chart.x0 + 73 * 12;
    const clipX = chart.x0 + (x1 - chart.x0) * reveal;
    return (
      <AbsoluteFill>
        <div style={{ position: "absolute", inset: 0, clipPath: `inset(0 ${1080 - clipX}px 0 0)`,
                      opacity: lit ? 1 - dim : 1, transform: `scaleY(${1 - squash})`, transformOrigin: `50% ${chart.base}px` }}>
          <Img src={staticFile("secret-history/year_chart.png")} style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 1920 }} />
        </div>
        {lit?.map((y) => {
          const c = chart.columns[String(y)]!;
          return (
            <div key={y} style={{ position: "absolute", left: c.x, top: Math.min(c.top, chart.base - 4), width: c.w,
                                  height: chart.base - Math.min(c.top, chart.base - 4), overflow: "hidden" }}>
              <Img src={staticFile("secret-history/year_chart.png")}
                   style={{ position: "absolute", left: -c.x, top: -Math.min(c.top, chart.base - 4), width: 1080, height: 1920 }} />
            </div>
          );
        })}
        <div style={{ position: "absolute", left: chart.x0, top: chart.base + 14, fontFamily: TYPE.mono, fontSize: 42, color: COLOR.inkDim }}>1910</div>
        <div style={{ position: "absolute", left: x1 - 100, top: chart.base + 14, fontFamily: TYPE.mono, fontSize: 42, color: COLOR.inkDim }}>1982</div>
      </AbsoluteFill>
    );
  };

const Hero: React.FC<{ year: string; story: string; extra?: string }> = ({ year, story, extra }) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  const n = picks.heroes[year]!;
  const c = chart.columns[year]!;
  return (
    <AbsoluteFill>
      <Chart lit={[Number(year)]} dim={0.82} />
      <Label y={300} size={96} weight={700} color={COLOR.accent}>{year}</Label>
      <Label y={410} size={42} color={COLOR.inkDim}>{`${c.count} Cents · CENT #${n}${extra ? " · " + extra : ""}`}</Label>
      <div style={{ position: "absolute", left: 540 - 210, top: 500, opacity: t, transform: `scale(${0.92 + 0.08 * t})` }}>
        <CentImage n={n} size={420} />
      </div>
      <Placeholder y={950} h={200} text={story} />
    </AbsoluteFill>
  );
};

const Scene: React.FC<{ id: string }> = ({ id }) => {
  const f = useCurrentFrame();
  switch (id) {
    case "open":
      return (<AbsoluteFill>
        <Chart reveal={interpolate(f, [10, 130], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} />
        <Label y={300} size={72} weight={700}>The mint years<br />in CENTS</Label>
      </AbsoluteFill>);
    case "thesis":
      return (<AbsoluteFill><Chart /><Label y={300} size={46} color={COLOR.inkDim}>10,000 Cents, one cell each, by year</Label></AbsoluteFill>);
    case "y1943": {
      const years = ["1940", "1941", "1942", "1943", "1944", "1945", "1946"];
      return (<AbsoluteFill>
        <Chart lit={years.map(Number)} dim={0.85} />
        <Label y={290} size={46} color={COLOR.inkDim}>1940 to 1946, every Cent</Label>
        <div style={{ position: "absolute", left: 104, top: 370, width: 872, display: "flex", gap: 10 }}>
          {years.map((y) => {
            const ns = picks.zoom[y]!;
            return (
              <div key={y} style={{ width: 116, display: "flex", flexDirection: "column", alignItems: "center" }}>
                <div style={{ height: 560, width: 116, display: "flex", alignItems: "flex-end", justifyContent: "center",
                              border: ns.length ? "none" : `3px dashed ${COLOR.accent}`, boxSizing: "border-box" }}>
                  {ns.length ? <CentGrid ns={ns} layout={fitGrid(ns.length, 112, 560)} enterFrames={20} texture={fitGrid(ns.length, 112, 560).size < 60} /> : null}
                </div>
                <div style={{ fontFamily: TYPE.mono, fontSize: 42, color: y === "1943" ? COLOR.accent : COLOR.inkDim, marginTop: 8 }}>{y.slice(2)}</div>
              </div>
            );
          })}
        </div>
        <Placeholder y={1000} h={170} text="1943 steel cent, archival (not in CENTS)" />
      </AbsoluteFill>);
    }
    case "y1944": return <Hero year="1944" story="Bretton Woods conference, July 1944 (archival)" />;
    case "y1964": return <Hero year="1964" story="1964 coin shortage; silver dime beside a clad dime" extra={`1965: ${chart.columns["1965"]!.count}`} />;
    case "y1971": return <Hero year="1971" story="Nixon address, 15 August 1971 (your clip)" />;
    case "y1979": return <Hero year="1979" story="no archival image; the line stays quiet" />;
    case "y1982": return <Hero year="1982" story="1982: copper to copper-plated zinc" />;
    case "block":
      return (<AbsoluteFill>
        <Chart squash={interpolate(f, [0, 60], [0, 0.94], { extrapolateRight: "clamp" })} />
        <Placeholder y={420} h={520} text="copper pour, then CENTS Block Copper (footage on your Mac)" />
      </AbsoluteFill>);
    case "close": {
      const lay = { cols: 8, size: 104, gap: 8 };
      const drift = interpolate(f, [0, 300], [0, -240]);
      return (<AbsoluteFill>
        <div style={{ position: "absolute", left: 92, top: 300 + drift }}>
          <CentGrid ns={picks.field} layout={lay} enterFrames={60} />
        </div>
      </AbsoluteFill>);
    }
  }
  return null;
};

export const Animatic: React.FC = () => {
  const end = Math.ceil(al.duration * FPS);
  return (
    <AbsoluteFill style={{ background: COLOR.bg }}>
      <Audio src={staticFile("secret-history/vo_take_a.mp3")} />
      {SCENES.map((s) => {
        const from = s.from ? at(s.from) : 0;
        const to = s.to ? at(s.to) : end + FPS;
        return <Sequence key={s.id} from={from} durationInFrames={Math.max(1, to - from)} name={s.id}><Scene id={s.id} /></Sequence>;
      })}
    </AbsoluteFill>
  );
};
