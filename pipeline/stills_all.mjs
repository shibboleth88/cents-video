// Like pipeline/stills.mjs, but reports each failing frame and carries on (SCALE env, default 0.5).
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
const [outdir, comp, ...ts] = process.argv.slice(2);
const browserExecutable = "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell";
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
let composition;
try { composition = await selectComposition({ serveUrl, id: comp, browserExecutable }); }
catch (e) { console.log("COMPOSITION FAILED:", String(e.message).split("\n")[0]); process.exit(1); }
for (const t of ts) {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(Number(t) * 30));
  const output = path.join(outdir, `${comp}_${String(frame).padStart(4, "0")}.png`);
  try { await renderStill({ serveUrl, composition, frame, output, browserExecutable, scale: Number(process.env.SCALE ?? 0.5) }); console.log("OK", t, output); }
  catch (e) { console.log("FAIL", t, String(e.message).split("\n")[0]); }
}
