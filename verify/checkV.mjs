// Drives site-verify/verify.html with real files and reads the verdict and every row.
//   FIX=<folder of clean files> CHANGED=<folder with one changed file> PILOT=<pilot.py> node checkV.mjs
import { chromium } from 'playwright';
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
const browser = await chromium.launch();
const files = (dir, drop = []) => fs.readdirSync(dir).filter(f => !drop.includes(f)).map(f => path.join(dir, f));
const cases = [
  ['untouched pack, no pilot.py', files(process.env.FIX)],
  ['untouched pack, with pilot.py', [...files(process.env.FIX), process.env.PILOT]],
  ['one cell changed in accounts.csv', files(process.env.CHANGED)],
  ['invoices.csv not chosen', files(process.env.FIX, ['invoices.csv'])],
];
let reqsAfter = 0;
for (const [label, list] of cases) {
  const page = await browser.newPage();
  const reqs = [];
  page.on('request', r => reqs.push({t: Date.now(), url: r.url()}));
  await page.goto(process.env.BASE || 'http://127.0.0.1:8098/verify.html');
  await page.waitForLoadState('networkidle');
  const chosenAt = Date.now();
  await page.setInputFiles('#files', list);
  await page.waitForFunction(() => /^(PACK|FILES)/.test(document.getElementById('verdict').textContent), null, {timeout: 60000});
  await page.waitForTimeout(1500);       // anything the page might fetch late would land here
  const rows = await page.$$eval('#rows tbody tr', trs => trs.map(t => [t.dataset.state, t.dataset.file]));
  const counts = {}; for (const [s] of rows) counts[s] = (counts[s] || 0) + 1;
  const after = reqs.filter(r => r.t >= chosenAt);
  reqsAfter += after.length;
  console.log(`CASE ${label}`);
  console.log(`  VERDICT ${await page.textContent('#verdict')}`);
  console.log(`  COUNTS ${JSON.stringify(counts)}  NOT_OK ${JSON.stringify(rows.filter(([s]) => s !== 'ok'))}`);
  console.log(`  REQUESTS_TOTAL ${reqs.length} REQUESTS_AFTER_FILES_CHOSEN ${after.length}`);
  for (const r of after) console.log('    AFTER:', r.url);
  await page.close();
}
console.log('ALL_CASES_REQUESTS_AFTER_FILES_CHOSEN', reqsAfter);
await browser.close(); server.close();
