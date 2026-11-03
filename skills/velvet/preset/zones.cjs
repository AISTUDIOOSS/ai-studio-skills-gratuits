// Contrôle des zones sûres Instagram sur la composition : cd PROJET && node PKG/preset/zones.cjs v1 (puppeteer-core installé dans PKG/preset par install.sh)
// Chrome : CH=/chemin/chrome si Google Chrome n'est pas à sa place habituelle.
const pp = require(require.resolve('puppeteer-core', { paths: [process.cwd(), __dirname] }));
const path = require('path');
(async () => {
  const b = await pp.launch({ executablePath: process.env.CH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new', args: ['--allow-file-access-from-files'] });
  const g = await b.newPage(); await g.setViewport({ width: 1080, height: 1920 });
  await g.goto('file://' + path.resolve(process.argv[2], 'composition/index.html'), { waitUntil: 'load' }); await new Promise(r => setTimeout(r, 2500));
  const r = await g.evaluate(() => [...document.querySelectorAll('.cap')].map(c => { const p = c.querySelector('.tour') ? 45 : 0;
    return { t: c.textContent.trim(), id: c.id, x0: Math.round(c.offsetLeft - p), x1: Math.round(c.offsetLeft + c.offsetWidth + p), y0: Math.round(c.offsetTop), y1: Math.round(c.offsetTop + c.offsetHeight) }; }));
  let ko = 0;
  for (const c of r) { const dr = c.y1 >= 1150 ? 940 : 1015; if (c.x0 < 65 || c.x1 > dr || c.y0 < 270 || c.y1 > 1500) { ko++; console.log('HORS', JSON.stringify(c)); } }
  console.log(r.length, 'calques,', ko, 'hors zone'); await b.close();
})().catch(e => { console.error(e.message); process.exit(1); });
