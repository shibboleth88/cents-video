import { continueRender, delayRender, staticFile } from "remotion";

/**
 * Typefaces are VENDORED in public/fonts, never left to the machine. Until
 * 2026-10-28 TYPE named "Inter Tight" and "IBM Plex Mono" but loaded neither,
 * so the cloud rendered Inter and DejaVu Sans Mono and a Mac would have
 * rendered Helvetica Neue and Menlo: the same film looked different by where
 * it was made. All faces here are SIL Open Font License 1.1 (licences beside
 * the files), which allows use in video and redistribution with the licence.
 */
const FACES: { family: string; file: string; weight: string; style?: string }[] = [
  { family: "Fraunces", file: "fraunces-latin-full-normal.woff2", weight: "100 900" },
  { family: "Fraunces", file: "fraunces-latin-full-italic.woff2", weight: "100 900", style: "italic" },
  { family: "IBM Plex Sans", file: "ibm-plex-sans-latin-400-normal.woff2", weight: "400" },
  { family: "IBM Plex Sans", file: "ibm-plex-sans-latin-400-italic.woff2", weight: "400", style: "italic" },
  { family: "IBM Plex Sans", file: "ibm-plex-sans-latin-500-normal.woff2", weight: "500" },
  { family: "IBM Plex Sans", file: "ibm-plex-sans-latin-600-normal.woff2", weight: "600" },
  { family: "IBM Plex Sans Condensed", file: "ibm-plex-sans-condensed-latin-400-normal.woff2", weight: "400" },
  { family: "IBM Plex Sans Condensed", file: "ibm-plex-sans-condensed-latin-500-normal.woff2", weight: "500" },
  { family: "IBM Plex Sans Condensed", file: "ibm-plex-sans-condensed-latin-600-normal.woff2", weight: "600" },
  { family: "IBM Plex Mono", file: "ibm-plex-mono-latin-400-normal.woff2", weight: "400" },
  { family: "IBM Plex Mono", file: "ibm-plex-mono-latin-500-normal.woff2", weight: "500" },
  { family: "IBM Plex Mono", file: "ibm-plex-mono-latin-600-normal.woff2", weight: "600" },
];

let loaded = false;

/** Call once at module level in a root. Holds the render until every face is in. */
export const loadFonts = () => {
  if (loaded || typeof document === "undefined") return;
  loaded = true;
  const handle = delayRender("vendored fonts");
  Promise.all(
    FACES.map((f) =>
      new FontFace(f.family, `url(${staticFile(`fonts/${f.file}`)}) format("woff2")`, {
        weight: f.weight, style: f.style ?? "normal",
      }).load().then((face) => document.fonts.add(face)),
    ),
  ).then(() => continueRender(handle), (err) => { throw err; });
};
