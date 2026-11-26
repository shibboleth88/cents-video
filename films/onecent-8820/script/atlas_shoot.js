// Screenshot the Traits Atlas Red entry on cents.vision at a 240 px viewport, 3x (the #1328 method),
// with the quoted sentence marked by a translucent copper highlight drawn from its measured client rects.
const { chromium } = require('playwright');
(async () => {
  const SENT = process.argv[2], OUT = process.argv[3], URL = process.argv[4];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 240, height: 900 }, deviceScaleFactor: 3 });
  await p.goto(URL, { waitUntil: 'networkidle' });
  const r = await p.evaluate((sent) => {
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let n; while ((n = w.nextNode())) {
      const t = n.textContent.replace(/\s+/g, ' '); const i = t.indexOf(sent);
      if (i < 0) continue;
      // map index in collapsed text back to the raw node offsets
      const raw = n.textContent; let ci = -1, ri = 0, start = -1, end = -1, prevSpace = false;
      for (ri = 0; ri < raw.length; ri++) {
        const sp = /\s/.test(raw[ri]); if (sp && prevSpace) continue; ci++; prevSpace = sp;
        if (ci === i && start < 0) start = ri; if (ci === i + sent.length - 1) { end = ri + 1; break; }
      }
      const range = document.createRange(); range.setStart(n, start); range.setEnd(n, end);
      const rects = [...range.getClientRects()].map(q => ({ x: q.x + scrollX, y: q.y + scrollY, w: q.width, h: q.height }));
      for (const q of rects) { const d = document.createElement('div'); Object.assign(d.style, { position: 'absolute', left: q.x - 1 + 'px', top: q.y + 'px', width: q.w + 2 + 'px', height: q.h + 'px', background: 'rgba(217,146,92,0.38)', pointerEvents: 'none', zIndex: 9999 }); document.body.appendChild(d); }
      return rects;
    }
    return null;
  }, SENT);
  if (!r) { console.error('SENTENCE NOT FOUND'); process.exit(2); }
  const y0 = Math.max(0, Math.min(...r.map(q => q.y)) - 40), y1 = Math.max(...r.map(q => q.y + q.h)) + 40;
  await p.screenshot({ path: OUT, clip: { x: 0, y: y0, width: 240, height: y1 - y0 }, fullPage: true });
  await p.screenshot({ path: OUT.replace('.png', '_page.png'), fullPage: true });
  console.log(JSON.stringify({ rects: r.length, y0, y1 }));
  await b.close();
})();
