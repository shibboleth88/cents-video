import React from "react";
import { Img, OffthreadVideo, Loop, staticFile, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { COLOR, MIN_FONT_PX, REGIONS, SAFE, TYPE } from "./tokens";
import { Imagery, SafeText } from "./Safe";
import { useDrift, useEntrance, useShotFade } from "./motion";

export type Asset = {
  path: string; motion: boolean; subject: string;
  width?: number; height?: number; low_res?: boolean; max_display_width?: number | null;
  staged_as?: string; staged_width?: number; staged_height?: number; frames?: number; duration?: number;
};

/** Always the staged copy: crops are applied at staging, so the original's
 *  excluded regions do not exist in what the renderer can reach. */
const file = (a: Asset) => staticFile("assets/" + (a.staged_as ?? a.path.split("/").pop()));
const dims = (a: Asset) => ({ w: a.staged_width ?? a.width ?? 4, h: a.staged_height ?? a.height ?? 3 });

/**
 * layout="none" is load-bearing. By default <Loop> wraps its child in a
 * <Sequence>, which is an absolute fill: the Block animation escaped its plate,
 * covered the whole canvas and painted over the plate's own caption — and the
 * render reported no error, so only measuring the text-only export found it.
 */
/**
 * Looping is only right for a short cycle like the Block animation. A generated
 * clip is usually longer than the shot that holds it, and looping it would snap
 * back to the first frame mid-shot; played straight, the shot simply ends before
 * the clip does.
 */
const Media: React.FC<{ asset: Asset; style?: React.CSSProperties }> = ({ asset, style }) => {
  const { durationInFrames, fps } = useVideoConfig();
  if (!asset.motion) return <Img src={file(asset)} style={style} />;
  const clipFrames = Math.round((asset.duration ?? 0) * fps) || Math.round(asset.frames ?? 0);
  if (clipFrames >= durationInFrames - 1)
    return <OffthreadVideo src={file(asset)} style={style} muted />;
  return (
    <Loop durationInFrames={Math.max(2, clipFrames || 111)} layout="none">
      <OffthreadVideo src={file(asset)} style={style} muted />
    </Loop>
  );
};

/**
 * Photography behind a shot. Full-bleed is allowed here because this is a
 * picture, not information — and a scrim keeps the text above it legible.
 * `focus` is the object-position, which is how a crop restriction gets honoured
 * (a01 carries burned-in text in its lower third and must sit high in frame).
 */
export const Backdrop: React.FC<{ asset: Asset; focus?: string; dim?: number; seed?: string }> = ({
  asset, focus = "50% 50%", dim = 0.62, seed = "backdrop",
}) => {
  const o = useShotFade();
  // A still gets a camera move; a clip that already moves does not. Drifting
  // generated motion stacks two camera moves on one shot and reads as a mistake.
  const drift = useDrift(seed, asset.motion ? 0 : undefined);
  return (
    <Imagery>
      <div style={{ position: "absolute", inset: 0, opacity: o, overflow: "hidden" }}>
        <div style={{ position: "absolute", inset: 0, ...drift }}>
          <Media asset={asset} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: focus }} />
        </div>
        <div style={{ position: "absolute", inset: 0, background: COLOR.bg, opacity: dim }} />
      </div>
    </Imagery>
  );
};

/**
 * One asset presented at its own size, with a caption. Refuses to display a
 * low-resolution asset wider than it can carry: the Block animation is 385px
 * across, and stretching it over a 1080 canvas is how real material is made to
 * look cheap.
 */
export const Plate: React.FC<{ asset: Asset; caption: string; maxWidth?: number }> = ({
  asset, caption, maxWidth,
}) => {
  const o = useShotFade();
  const e = useEntrance("place", 0);
  const cap0 = useEntrance("rise", 2);
  const R = REGIONS.diagram;
  const boxW = R.x1 - R.x0, boxH = R.y1 - R.y0;
  const cap = asset.max_display_width ?? 1080;
  const want = Math.min(maxWidth ?? boxW, boxW, cap);
  if (asset.low_res && want > cap)
    throw new Error(`asset ${asset.path} is ${asset.width}px wide; ${want}px would soften it`);
  const d = dims(asset);
  const ar = d.w / d.h;
  let w = want, h = w / ar;
  if (h > boxH - 130) { h = boxH - 130; w = h * ar; }
  return (
    <div style={{ position: "absolute", left: R.x0, top: R.y0, width: boxW, height: boxH,
                  display: "flex", flexDirection: "column", alignItems: "center",
                  justifyContent: "center", gap: 34, opacity: o }}>
      <Imagery>
        <div style={{ width: w, height: h, overflow: "hidden", borderRadius: 2,
                      border: `1px solid ${COLOR.rule}`,
                      opacity: e.opacity, transform: `translateY(${e.y}px) scale(${e.scale})` }}>
          <Media asset={asset} style={{ width: "100%", height: "100%", objectFit: "contain",
                                        background: "#0f0f10" }} />
        </div>
      </Imagery>
      <div style={{ width: boxW - 60, display: "flex", justifyContent: "center", opacity: cap0.opacity, transform: `translateY(${cap0.y}px)` }}>
        <SafeText role="label" fontSize={MIN_FONT_PX.label} color={COLOR.inkDim} maxLines={3}
                  style={{ textAlign: "center", fontFamily: TYPE.body }}>
          {caption}
        </SafeText>
      </div>
    </div>
  );
};
