// Stills that report per timestamp instead of dying on the first refusal (pipeline/stills.mjs stops at
// the first SafeText error). Prints OK <t> <file> or FAIL <t> <first line of the error>.
//   node pipeline/stills_safe.mjs <outdir> <comp> t1 t2 ...   (run from the repo root)
// A pass is a pass for that frame only (LEDGER): sample each shot around its cues, and render a
// whole shot with `remotion render --frames=a-b` to cover entrances.
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
const [outdir, comp, ...ts] = process.argv.slice(2);
const browserExecutable = "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell";
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id: comp, browserExecutable });
for (const t of ts) {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(Number(t) * 30));
  const output = path.join(outdir, `${comp}_${String(frame).padStart(4, "0")}.png`);
  try { await renderStill({ serveUrl, composition, frame, output, browserExecutable, scale: 0.5, logLevel: "error" }); console.log("OK", t, output); }
  catch (e) { console.log("FAIL", t, String(e.message).split("\n")[0]); }
}
