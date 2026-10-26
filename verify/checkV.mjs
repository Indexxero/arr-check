// Drives site-verify/verify.html with real files and reads the verdict and every row.
//   FIX=<folder of clean files> CHANGED=<folder with one changed file> PILOT=<pilot.py> node checkV.mjs
import { chromium, firefox, webkit } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(process.env.SITE || 'site-verify');
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, {'Content-Type': 'text/html'}); fs.createReadStream(p).pipe(res);
});
await new Promise(r => server.listen(8098, r));
const browser = await ({chromium, firefox, webkit})[process.env.BROWSER || 'chromium'].launch();
console.log('BROWSER', process.env.BROWSER || 'chromium');
const files = (dir, drop = []) => fs.readdirSync(dir).filter(f => !drop.includes(f)).map(f => path.join(dir, f));
const cases = [
  ['untouched pack, no pilot.py', files(process.env.FIX)],
  ['untouched pack, with pilot.py', [...files(process.env.FIX), process.env.PILOT]],
  ['one cell changed in accounts.csv', files(process.env.CHANGED)],
  ['invoices.csv not chosen', files(process.env.FIX, ['invoices.csv'])],
  ['DROP: one cell changed in accounts.csv', files(process.env.CHANGED)],
];
let reqsAfter = 0;
for (const [label, list] of cases) {
  const page = await browser.newPage();
  const reqs = [];
  page.on('request', r => reqs.push({t: Date.now(), url: r.url()}));
  await page.goto(process.env.BASE || 'http://127.0.0.1:8098/verify.html');
  await page.waitForLoadState('networkidle');
  const chosenAt = Date.now();
  if (label.startsWith('DROP')) {
    // A drop event carrying the files in a DataTransfer, as a drag from Finder delivers them.
    const payload = list.map(f => ({name: path.basename(f), b64: fs.readFileSync(f).toString('base64')}));
    const dt = await page.evaluateHandle(ps => { const d = new DataTransfer();
      for (const p of ps) d.items.add(new File([Uint8Array.from(atob(p.b64), c => c.charCodeAt(0))], p.name)); return d; }, payload);
    await page.dispatchEvent('#drop', 'drop', {dataTransfer: dt});
  } else await page.setInputFiles('#files', list);
  await page.waitForFunction(() => /^(PACK|FILES)/.test(document.getElementById('verdict').textContent), null, {timeout: 60000});
  await page.waitForTimeout(1500);       // anything the page might fetch late would land here
  const rows = await page.$$eval('#rows tbody tr', trs => trs.map(t => [t.dataset.state, t.dataset.file]));
  const counts = {}; for (const [s] of rows) counts[s] = (counts[s] || 0) + 1;
  // blob: is the browser reading a chosen File from memory (WebKit reports each read as a
  // request); it never leaves the machine. Everything else after the choice is network.
  const all = reqs.filter(r => r.t >= chosenAt);
  const after = all.filter(r => !r.url.startsWith('blob:'));
  const blobs = all.length - after.length;
  reqsAfter += after.length;
  console.log(`CASE ${label}`);
  console.log(`  VERDICT ${await page.textContent('#verdict')}`);
  console.log(`  COUNTS ${JSON.stringify(counts)}  NOT_OK ${JSON.stringify(rows.filter(([s]) => s !== 'ok'))}`);
  console.log(`  REQUESTS_TOTAL ${reqs.length} REQUESTS_AFTER_FILES_CHOSEN ${after.length} BLOB_READS ${blobs}`);
  for (const r of after) console.log('    AFTER:', r.url);
  await page.close();
}
console.log('ALL_CASES_REQUESTS_AFTER_FILES_CHOSEN', reqsAfter);
await browser.close(); server.close();
