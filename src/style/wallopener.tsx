import React from "react";
import { Img, interpolate, Loop, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { EASE } from "./motion";
import { COLOR, SAFE, TYPE } from "./tokens";
import { Imagery, SafeText } from "./Safe";
import { WallBoard, layoutWall, useBoard, type Board, type Move, type Show, type Sweep } from "./wallboard";
import { findPhrase, type Alignment } from "../lib/timeline";

/**
 * WallOpener: the first seconds of a Collector Wall episode, made to read as a
 * video, not a still, to someone scrolling past. The Wall card (WallBoard)
 * runs underneath from frame 0; an intro plays over it and hands over to it.
 * Frame 0 is never black and is already moving.
 *
 * Variants (proposed 2026-10-27, ScrappyT thread; the user picks one for the series):
 *  - "live":  the card itself, already in motion: the camera pulls back from
 *             the mosaic while a copper ring runs across the mosaic Cents.
 *  - "rush":  every Cent on the Wall, scrolling fast on black under the name and
 *             a running count, then the whole thing folds down into the card.
 *  - "turn":  the signature Cent turning (the 3DCENTS render) under the name,
 *             then it shrinks into its place on the card.
 *  - "showcase": the card at frame 0 with the signature Cent turning in its
 *             slot (3DCENTS) while the badges, and the mosaic Cents, light up
 *             one after another. The user's direction, 2026-10-27 16:55Z.
 * `progress` adds a thin bar across the top that fills over the whole film,
 * the way Stories show there is more to come.
 */

type Anchored = { alignment: Alignment; shotStartFrame: number };
type Clip = { src: string; width: number; height: number; frames: number; coin: { cx: number; cy: number; d: number }; credit: string; note?: string };

const VIEW = { x0: 40, y0: SAFE.essential.y0 };   // where WallBoard puts board unit (0,0) at its top view, k = 1

export const WallOpener: React.FC<Anchored & {
  variant: "live" | "rush" | "turn" | "showcase";
  wall: string; moves?: Move[]; show?: Show;
  /** The intro hands over to the card when this phrase starts. */
  until_phrase: string;
  /** Total film length in frames, for the progress bar. */
  progress?: { total_frames: number };
  clip?: Clip;
  /** showcase: the light-up chases; defaults to the mosaic and, at the same time, every badge in reading order. */
  sweep?: Sweep[];
}> = (props) => {
  const { variant, wall, moves = [], show = "card", until_phrase, progress, clip, alignment, shotStartFrame } = props;
  const showcase = variant === "showcase";
  if (showcase && !clip) throw new Error("WallOpener showcase: needs the signature Cent's 3DCENTS clip");
  const sweep = props.sweep ?? [{ rows: ["mosaic"], stagger: 5, hold: 14 }, { rows: ["tags", "sets", "fulls", "meta"], stagger: 3, hold: 14 }];
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const end = Math.round(findPhrase(alignment, until_phrase).start * fps) - shotStartFrame;
  if (end < 20) throw new Error(`WallOpener: "${until_phrase}" leaves the intro under 20 frames`);
  const b = useBoard(wall);
  const out = interpolate(frame, [end - 14, end], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });

  // The card underneath, at full opacity from frame 0 (WallBoard fades in only when it is not the opening shot).
  let under: React.CSSProperties = {};
  if (variant === "live") {
    // Pull back from 1.35x on the mosaic to 1:1 over the intro.
    const t = interpolate(frame, [0, end], [0, 1], { extrapolateRight: "clamp", easing: EASE.out });
    const k = 1.35 + (1 - 1.35) * t;
    under = { transform: `scale(${k})`, transformOrigin: "62% 30%" };
  }
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div style={{ position: "absolute", inset: 0,
                    opacity: variant === "live" || showcase ? 1 : interpolate(frame, [end - 16, end - 2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
        {/* The pull-back stays inside the board's own view, so nothing spills over the stage. */}
        <div style={{ position: "absolute", left: VIEW.x0, top: VIEW.y0, width: 1000, height: 1330 - VIEW.y0, overflow: "hidden", borderRadius: 18 }}>
          <div style={{ position: "absolute", left: -VIEW.x0, top: -VIEW.y0, width: 1080, height: 1920, ...under }}>
            <WallBoard wall={wall} moves={moves} show={show} alignment={alignment} shotStartFrame={shotStartFrame}
                       signature_clip={showcase ? clip : undefined} sweep={showcase ? sweep : undefined} />
            {variant === "live" && b ? <MosaicSweep board={b} frame={frame} end={end} /> : null}
          </div>
        </div>
      </div>
      {variant === "rush" && b && frame < end ? <Rush board={b} frame={frame} end={end} out={out} /> : null}
      {variant === "turn" && b && frame < end + 2 ? <Turn board={b} frame={frame} end={end} clip={clip} /> : null}
      {showcase && clip ? (
        // Gone once the card zooms in: the zoomed card fills this band, and the credit would sit on it.
        <div style={{ position: "absolute", left: SAFE.essential.x0 + 24, top: 1262, width: SAFE.essential.x1 - SAFE.essential.x0 - 48,
                      opacity: 1 - interpolate(frame, [end, end + 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
          <SafeText role="label" fontSize={42} maxLines={1} color="#555" style={{ fontFamily: TYPE.body, textAlign: "center" }}>{clip.credit}</SafeText>
        </div>
      ) : null}
      {progress ? <ProgressBar total={progress.total_frames} frame={frame + shotStartFrame} /> : null}
    </div>
  );
};

/** A copper ring that runs across the mosaic Cents, one after another. */
const MosaicSweep: React.FC<{ board: Board; frame: number; end: number }> = ({ board, frame, end }) => {
  const L = React.useMemo(() => layoutWall(board), [board]);
  const ms = L.items.filter((i) => i.kind === "cent" && i.where === "mosaic");
  const step = Math.max(2, Math.floor((end - 6) / ms.length));
  return (
    <>
      {ms.map((it, i) => {
        const f0 = i * step, a = interpolate(frame, [f0, f0 + 4, f0 + step + 8], [0, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        if (a <= 0) return null;
        const [x0, y0, x1, y1] = it.box;
        return <div key={i} style={{ position: "absolute", left: VIEW.x0 + x0 - 5, top: VIEW.y0 + y0 - 5, width: x1 - x0 + 10, height: y1 - y0 + 10,
                                     borderRadius: "50%", border: `5px solid ${COLOR.accent}`, opacity: a,
                                     transform: `scale(${1 + 0.12 * a})` }} />;
      })}
    </>
  );
};

const Title: React.FC<{ name: string; frame: number; y?: number; count?: string }> = ({ name, frame, y = SAFE.essential.y0 + 30, count }) => {
  const rise = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp", easing: EASE.out });
  return (
    <div style={{ position: "absolute", left: SAFE.essential.x0 + 24, top: y, width: SAFE.essential.x1 - SAFE.essential.x0 - 48 }}>
      {/* Frame 0 shows the title fully legible; the rise only adds motion. */}
      <div style={{ transform: `translateY(${(1 - rise) * 18}px)` }}>
        <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, letterSpacing: 4 }}>COLLECTOR WALL</SafeText>
        <SafeText role="display" fontSize={104} maxLines={1} style={{ fontWeight: 700, letterSpacing: -2 }}>{name}</SafeText>
        {count ? <SafeText role="display" fontSize={72} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, fontWeight: 700 }}>{count}</SafeText> : null}
      </div>
    </div>
  );
};

/** Every Cent on the Wall, scrolling fast on black, with a running count; then it folds into the card. */
const Rush: React.FC<{ board: Board; frame: number; end: number; out: number }> = ({ board, frame, end, out }) => {
  const cols = 5, size = 196, gap = 12, pitch = size + gap;
  // One endless sheet: cell k shows the Wall's Cent k mod count, so the scroll never shows an edge or a gap.
  const speed = 14;                                   // px per frame
  const scroll = frame * speed, r0 = Math.floor(scroll / pitch);
  const n = Math.round(interpolate(frame, [0, end - 16], [1, board.count], { extrapolateRight: "clamp" }));
  const sc = 1 - 0.35 * out;
  const cells: React.ReactNode[] = [];
  for (let r = r0; r < r0 + Math.ceil(1920 / pitch) + 1; r++)
    for (let c = 0; c < cols; c++) {
      const id = board.cents[(r * cols + c) % board.cents.length]!;
      cells.push(<Img key={`${r}-${c}`} src={staticFile(`cents/${id}.webp`)}
                      style={{ position: "absolute", left: c * pitch, top: r * pitch - scroll, width: size, height: size }} />);
    }
  return (
    <div style={{ position: "absolute", inset: 0, background: COLOR.bg, opacity: 1 - out, transform: `scale(${sc})` }}>
      <Imagery>
        <div style={{ position: "absolute", left: (1080 - (cols * pitch - gap)) / 2, top: 0, width: cols * pitch, height: 1920, overflow: "hidden" }}>
          {cells}
        </div>
        {/* Darken behind the title so it reads over the Cents. */}
        <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 760,
                      background: `linear-gradient(${COLOR.bg} 0%, ${COLOR.bg} 62%, transparent 100%)` }} />
      </Imagery>
      <Title name={board.name} frame={frame} count={`${n} ${n === 1 ? "CENT" : "CENTS"}`} />
    </div>
  );
};

/** The signature Cent turning (3DCENTS), then flying into its place on the card. */
const Turn: React.FC<{ board: Board; frame: number; end: number; clip?: Clip }> = ({ board, frame, end, clip }) => {
  if (!clip) throw new Error("WallOpener turn: needs the signature Cent's 3DCENTS clip");
  if (!clip.credit) throw new Error("WallOpener turn: the 3DCENTS clip must carry its credit");
  const L = React.useMemo(() => layoutWall(board), [board]);
  const sig = L.items.find((i) => i.kind === "cent" && i.where === "signature")!.box;
  const t = interpolate(frame, [end - 18, end], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE.inOut });
  const big = 560, small = sig[2] - sig[0];
  const d = big + (small - big) * t;
  const cx = 540 + ((VIEW.x0 + (sig[0] + sig[2]) / 2) - 540) * t;
  const cy = 940 + ((VIEW.y0 + (sig[1] + sig[3]) / 2) - 1010) * t;
  const k = d / clip.coin.d;
  const bgA = 1 - t;
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div style={{ position: "absolute", inset: 0, background: COLOR.bg, opacity: bgA }} />
      <Imagery>
        <div style={{ position: "absolute", left: cx - d / 2, top: cy - d / 2, width: d, height: d, borderRadius: "50%", overflow: "hidden",
                      background: COLOR.bg, isolation: "isolate" }}>
          <Loop durationInFrames={clip.frames} layout="none">
            <OffthreadVideo src={staticFile(clip.src)} muted
              style={{ position: "absolute", left: d / 2 - clip.coin.cx * k, top: d / 2 - clip.coin.cy * k,
                       width: clip.width * k, height: clip.height * k, mixBlendMode: "lighten" }} />
          </Loop>
        </div>
      </Imagery>
      <div style={{ opacity: 1 - t }}>
        <Title name={board.name} frame={frame} />
        <div style={{ position: "absolute", left: SAFE.essential.x0 + 24, top: 1236, width: SAFE.essential.x1 - SAFE.essential.x0 - 48, opacity: 0.8 }}>
          <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.inkDim} style={{ fontFamily: TYPE.body, textAlign: "center" }}>{clip.credit}</SafeText>
          {clip.note ? <SafeText role="label" fontSize={42} maxLines={1} color={COLOR.accent} style={{ fontFamily: TYPE.mono, textAlign: "center" }}>{clip.note}</SafeText> : null}
        </div>
      </div>
    </div>
  );
};

/** A thin copper bar under the top interface band, filling over the whole film. */
export const ProgressBar: React.FC<{ total: number; frame: number }> = ({ total, frame }) => {
  const p = Math.min(1, frame / Math.max(1, total));
  return (
    <div style={{ position: "absolute", left: SAFE.essential.x0, top: SAFE.essential.y0 - 22, width: SAFE.essential.x1 - SAFE.essential.x0, height: 8,
                  borderRadius: 4, background: "rgba(255,255,255,0.18)" }}>
      <div style={{ width: `${Math.max(1.5, p * 100)}%`, height: "100%", borderRadius: 4, background: COLOR.accent }} />
    </div>
  );
};

(WallOpener as any).wantsAlignment = true;
