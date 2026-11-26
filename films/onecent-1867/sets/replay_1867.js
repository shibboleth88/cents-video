// Replays collectors.html offline against the saved raw files, then reads the
// page's own computed collector objects and rendered badges for claimed walls.
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const RAW = process.argv[2]; const OUT = process.argv[3];
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const served = new Set(); const blocked = [];
  page.on('console', m => { if (m.type() === 'error') console.error('page:', m.text()); });
  await page.route('**/*', route => {
    const u = new URL(route.request().url());
    if (u.hostname !== 'cents.vision') { blocked.push(u.href); return route.abort(); }
    const name = u.pathname.replace(/^\//, '') || 'collectors.html';
    if (name === 'wallets-names.json') { served.add(name + ' (stubbed {}; Council-only, not fetched)'); return route.fulfill({ status: 200, contentType: 'application/json', body: '{}' }); }
    const f = path.join(RAW, name);
    if (fs.existsSync(f) && !name.includes('/')) { served.add(name); return route.fulfill({ status: 200, body: fs.readFileSync(f), contentType: name.endsWith('.json') ? 'application/json' : 'text/html' }); }
    blocked.push(u.href); return route.fulfill({ status: 404, body: '' });
  });
  await page.goto('https://cents.vision/collectors.html');
  await page.waitForFunction(() => state.collectors.length > 0, null, { timeout: 60000 });
  const result = await page.evaluate(() => {
    const C = state.collectors;
    const c = C.find(x => x.centIds.includes(1867));
    if (!c) return { error: 'no collector holds 1867' };
    const n = f => C.filter(f).length;
    return {
      totalCollectors: C.length,
      holder: { count: c.count, club: clubName(c.count), claimed: Boolean(c.publicProfile.name), years: [c.minYear, c.maxYear],
        sets: { patina_level: c.patinaSet, spectrum: c.spectrumSet, full_spectrum: c.grandPatinaSet, chronicle: c.chronicleSet,
                full_mint: c.fullMintSet, contamination_types: c.contaminationTypes, decade_sets: c.decadeSets,
                three_decades: c.threeDecadesSet, full_decades: c.fullDecadeSet, all_decades: c.allDecadesSet },
        top_traits: c.topTraits, diamond_hands: c.diamondHands },
      aggregate: { patina: n(x => x.patinaSet !== null), sig: n(x => x.patinaSet === 'significant' || x.patinaSet === 'full'),
        fulls: n(x => x.patinaSet === 'full'), contaminationSet: n(x => x.contaminationTypes >= 3), contaminationHoard: n(x => x.contaminationTypes >= 6),
        decade1960: n(x => x.decadeSets.includes(1960)), threeDecades: n(x => x.threeDecadesSet), allDecades: n(x => x.allDecadesSet) }
    };
  });
  fs.writeFileSync(OUT, JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 1)); console.log('blocked', blocked.length);
  await browser.close();
})();
