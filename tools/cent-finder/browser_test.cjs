const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('http://127.0.0.1:8765/test.html');
  await p.evaluate(() => window.centFinder.ready);
  const status = await p.textContent('#status'); const sample = await p.textContent('#centno'); const pill = await p.textContent('#pill');
  console.log('status:', status, '| sample:', sample, pill, '| CIRC', await p.evaluate(() => 0));
  await p.screenshot({ path: 'shot_desktop.png', fullPage: true });
  const root = 'jstest', variants = process.argv.slice(2);
  for (const v of variants) {
    const files = fs.readdirSync(path.join(root, v)).filter(f => f.endsWith('.png'));
    let r1 = 0, conf = 0, confWrong = 0, t0 = Date.now(); const fails = []; const scores = [];
    for (const f of files) {
      const n = parseInt(f); const b64 = fs.readFileSync(path.join(root, v, f)).toString('base64');
      const out = await p.evaluate(async (b64) => { const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0)); return await window.centFinder.identify(new Blob([bin], { type: 'image/png' })); }, b64);
      const ok = out.top[0].n === n; r1 += ok; if (!ok) fails.push([n, out.top[0].n, out.top.findIndex(t => t.n === n)]);
      if (out.verdict === 'match') { conf++; if (!ok) confWrong++; }
      scores.push(out.top[0].score);
    }
    scores.sort();
    console.log(`${v.padEnd(16)} rank1 ${r1}/${files.length}  Match shown ${conf} (wrong ${confWrong})  top score min ${scores[0].toFixed(3)}  ${((Date.now() - t0) / files.length).toFixed(0)} ms/image  fails ${JSON.stringify(fails.slice(0, 5))}`);
  }
  console.log('page errors:', errs.length ? errs.slice(0, 5) : 'none');
  await b.close();
})();
