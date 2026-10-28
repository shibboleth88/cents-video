import React from "react";
import { AbsoluteFill, Composition } from "remotion";
import { CANVAS, COLOR, REGIONS } from "../style/tokens";
import { CentGrid, CentTurn, fitGrid } from "../style/grids";
import { LOOK_COMPONENTS, LOOK_FRAMES } from "./Looks";
import poolsJson from "../../films/sets/data/pools.json";

/**
 * A bench for the shared grid pieces, separate from the film roots so it needs
 * no recording or timeline. Text-free on purpose: labels belong to SafeText in
 * a real shot. Render a still with:
 *   npx remotion still src/lab/index.ts <id> <out.png> --frame=60
 */
const pools = (poolsJson as unknown as { pools: Record<string, number[]> }).pools;
const pool = (k: string) => {
  const p = pools[k];
  if (!p || p.length === 0) throw new Error(`pool ${k} is empty or missing`);
  return p;
};

const A = REGIONS.art;

/**
 * Every Full of each base patina, one column each. Equal columns put the 71
 * Full Reds at 54px, under the trait floor, and the render stopped; columns
 * weighted by the square root of their count keep all four at 65px or more.
 */
const FullsWall: React.FC = () => {
  const cols = ["verdigris", "obsidian", "desert", "red"].map((p) => pool(`${p}:full`));
  const weights = cols.map((ns) => Math.sqrt(ns.length));
  const total = weights.reduce((a, b) => a + b, 0);
  let x = A.x0;
  return (
    <AbsoluteFill style={{ background: COLOR.bg }}>
      {cols.map((ns, i) => {
        const w = ((A.x1 - A.x0) * weights[i]!) / total;
        const left = x;
        x += w;
        return (
          <CentGrid key={i} ns={ns} layout={fitGrid(ns.length, w - 16, A.y1 - A.y0)}
                    enterFrames={40} from={i * 6}
                    style={{ position: "absolute", left: left + 8, top: A.y0 }} />
        );
      })}
    </AbsoluteFill>
  );
};

/** All 10,000 as a field with one pool lit. Texture, not evidence. */
const Field: React.FC<{ pool: string }> = ({ pool: k }) => {
  const all = Array.from({ length: 10000 }, (_, i) => i + 1);
  const lit = new Set(pool(k));
  return (
    <AbsoluteFill style={{ background: COLOR.bg, alignItems: "center", justifyContent: "center" }}>
      <CentGrid ns={all} layout={{ cols: 100, size: 10, gap: 0 }} lit={lit} dim={0.82}
                enterFrames={45} texture />
    </AbsoluteFill>
  );
};

/** One Cent turning: Full Verdigris, CENT #3981, the Fulls example on the Sets page. */
const Turn: React.FC<{ n: number }> = ({ n }) => (
  <AbsoluteFill style={{ background: COLOR.bg, alignItems: "center", justifyContent: "center" }}>
    <CentTurn n={n} size={500} />
  </AbsoluteFill>
);

const base = { width: CANVAS.width, height: CANVAS.height, fps: CANVAS.fps, durationInFrames: 120 };
export const LabRoot: React.FC = () => (
  <>
    <Composition id="FullsWall" component={FullsWall} {...base} />
    <Composition id="TurnFullVerdigris" component={Turn} {...base} durationInFrames={210} defaultProps={{ n: 3981 }} />
    <Composition id="FieldFullRed" component={Field} {...base} defaultProps={{ pool: "red:full" }} />
    {Object.entries(LOOK_COMPONENTS).map(([id, C]) => (
      <Composition key={id} id={id} component={C} width={1080} height={1920} fps={30} durationInFrames={LOOK_FRAMES} />
    ))}
  </>
);
