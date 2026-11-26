// export_3dcents.cjs: export one Cent's 3DCENTS turn (3dcents.vercel.app, by sinvalli) with the site's
// own MP4 button, in the container's headless Chromium. Same settings and file name as the user's exports:
// View "IG Reel 1080x1920", 1080p, 25 fps, backdrop Black -> cent-<n>-360-1080x1920-25fps-reel.mp4
// (150 frames, 6 s, one full turn). About 17 minutes a Cent: WebGL runs in software (swiftshader).
// Tested 2026-11-21 on #10000 (Studio and Black backdrops), compared with the user's #478 export.
// Credit: "3D render: 3DCENTS by sinvalli". Then retime for the films: ffmpeg -i <in> -vf setpts=N/30/TB -r 30 <out>
// usage: node pipeline/export_3dcents.cjs <n> <outdir> [backdrop: Studio|None|White|Black, default Black]
const { chromium } = require('playwright');
(async () => {
  const [n, out, backdrop = 'Black'] = process.argv.slice(2);
  const t0 = Date.now(); const log = (...a) => console.log(((Date.now()-t0)/1000).toFixed(1)+'s', ...a);
  const b = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 }, acceptDownloads: true });
  const p = await ctx.newPage();
  p.on('console', m => { if (['error','warning'].includes(m.type())) log('console.'+m.type()+':', m.text().slice(0,200)); });
  await p.goto('https://3dcents.vercel.app/', { waitUntil: 'networkidle', timeout: 90000 });
  const box = p.locator('input[placeholder^="Search"]').first();
  await box.fill(String(n)); await box.press('Enter');
  await p.waitForTimeout(10000);
  log('title in viewer:', await p.locator('text=#' + n).first().innerText().catch(()=>'?'));
  if (backdrop !== 'Studio') {
    await p.locator('button').filter({ hasText: /^\s*Studio\s*$/ }).first().click();
    await p.waitForTimeout(800);
    await p.locator('[role=menuitem],[role=menuitemradio],[role=option]').filter({ hasText: new RegExp('^\\s*' + backdrop + '\\s*$') }).first().click();
    await p.waitForTimeout(1500);
    log('backdrop set:', backdrop);
  }
  await p.locator('button').filter({ hasText: /^\s*View\s*$/ }).first().click();
  await p.waitForTimeout(800);
  await p.locator('[role=menuitem],[role=menuitemradio],[role=option],button,li').filter({ hasText: /IG Reel/ }).last().click();
  await p.waitForTimeout(1500);
  const btns = await p.evaluate(() => [...document.querySelectorAll('button')].map(e => (e.innerText||'').trim().replace(/\n/g,' ')).filter(t => /MP4|PNG|fps|1080p|GIF/.test(t)));
  log('export buttons:', JSON.stringify(btns));
  await p.screenshot({ path: out + '/before_export.png', timeout: 200000 });
  const mp4 = p.locator('button').filter({ hasText: /MP4\s*1080×1920/ }).first();
  const dlP = p.waitForEvent('download', { timeout: 1500000 });
  await mp4.click();
  log('export clicked');
  const tick = setInterval(async () => { try { log('progress:', (await p.evaluate(() => [...document.querySelectorAll('button,[role=progressbar],div')].map(e=>e.innerText||'').find(t=>/\d+\s*%|Rendering|Encoding|Exporting/i.test(t) && t.length<60)||'')) ); } catch(e){} }, 30000);
  const dl = await dlP; clearInterval(tick);
  const name = dl.suggestedFilename(); await dl.saveAs(out + '/' + name);
  log('saved', name);
  await b.close();
})().catch(e => { console.error('FAILED', e.message.slice(0,500)); process.exit(1); });
