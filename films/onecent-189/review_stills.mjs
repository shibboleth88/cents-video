// Quick stills for the #189 rehearsal (copied from #1867, itself from #10000) (copy of pipeline/stills.mjs that reports a failed frame and goes on).
//   node pipeline/stills.mjs <outdir> <comp> t1 t2 ...
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
  try { await renderStill({ serveUrl, composition, frame, output, browserExecutable, scale: 0.5 }); console.log("OK", output); }
  catch (e) { console.log("FAIL", frame, String(e.message || e).split("\n")[0]); }
}
