import React from "react";
import { staticFile, useCurrentFrame } from "remotion";
import { COLOR } from "./tokens";
import { Imagery } from "./Safe";

/**
 * Film grain and a vignette over the whole film.
 *
 * A tiled noise bitmap shifted per frame, not an SVG turbulence filter: the
 * filter is recomputed every frame at 1080x1920 and makes a two-minute render
 * crawl, while a 256px tile costs nothing and reads the same.
 *
 * Inside <Imagery>, so the text-only export the safe-area gate measures stays
 * clean — a grain layer over it would raise the luma of every band and make the
 * gate report violations that are not there.
 */
export const Atmosphere: React.FC<{ grain?: number; vignette?: number }> = ({
  grain = 0.055, vignette = 0.5,
}) => {
  const f = useCurrentFrame();
  // Shift the tile on a cycle that is not a multiple of the tile size, so the
  // grain never visibly repeats its position.
  const x = (f * 37) % 256;
  const y = (f * 53) % 256;
  return (
    <Imagery>
      <div style={{ position: "absolute", inset: 0, pointerEvents: "none",
                    background: `radial-gradient(130% 92% at 50% 44%, transparent 38%, ${COLOR.bg} 100%)`,
                    opacity: vignette }} />
      <div style={{ position: "absolute", inset: -256, pointerEvents: "none",
                    backgroundImage: `url(${staticFile("grain.png")})`,
                    backgroundRepeat: "repeat",
                    transform: `translate(${-x}px, ${-y}px)`,
                    opacity: grain, mixBlendMode: "overlay" }} />
    </Imagery>
  );
};
