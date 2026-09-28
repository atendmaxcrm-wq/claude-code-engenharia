// Passo de SCREENSHOT (pipeline-fiel): renderiza cada .screen do mockup em PNG (claro+escuro) pro
// lead/dono BATER O OLHO no que o gate automatico nao pega (alinhamento fino, espacamento,
// truncamento, sobreposicao). Uso: node shot.mjs <arquivo.html> [outDir] [temas=light,dark]
// PORTAVEL: resolve playwright-core e chromium por env / sibling / fallback.
import { readFileSync, mkdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const firstExisting = (c) => c.filter(Boolean).find(p => existsSync(p)) || null;
const pwCore = firstExisting([
  process.env.PLAYWRIGHT_CORE,
  resolve(here, 'node_modules/playwright-core/index.mjs'),
  resolve(here, '../capturar-logica-saas/node_modules/playwright-core/index.mjs'),
  '/root/CRMAX_2/.claude/skills/capturar-logica-saas/node_modules/playwright-core/index.mjs',
]);
if (!pwCore) { console.error('playwright-core nao encontrado. Setar env PLAYWRIGHT_CORE=/caminho/playwright-core/index.mjs'); process.exit(3); }
const chrome = firstExisting([process.env.CHROME, '/usr/bin/chromium-browser', '/snap/bin/chromium', '/usr/bin/chromium', '/usr/bin/google-chrome']) || '/usr/bin/chromium-browser';
const { chromium } = await import(pwCore);

const file = process.argv[2];
if (!file) { console.error('uso: node shot.mjs <arquivo.html> [outDir] [temas]'); process.exit(2); }
const outDir = process.argv[3] || './shots';
const themes = (process.argv[4] || 'light,dark').split(',').map(s => s.trim()).filter(Boolean);
mkdirSync(outDir, { recursive: true });

const fragment = readFileSync(file, 'utf8');
const html = `<!doctype html><html lang="pt-br"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>${fragment}</body></html>`;

const browser = await chromium.launch({ executablePath: chrome, args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'] });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.setContent(html, { waitUntil: 'load' });
await page.waitForTimeout(150);

const screenIds = await page.$$eval('.screen', els => els.map(e => e.id));
const ids = screenIds.length ? screenIds : ['__page__'];
const shots = [];
for (const theme of themes) {
  await page.evaluate(t => document.documentElement.setAttribute('data-theme', t), theme);
  for (const sid of ids) {
    if (sid !== '__page__') {
      await page.evaluate(id => {
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('on'));
        const el = document.getElementById(id); if (el) el.classList.add('on');
      }, sid);
    }
    await page.waitForTimeout(80);
    const path = `${outDir}/${sid}-${theme}.png`;
    await page.screenshot({ path, fullPage: true });
    shots.push(path);
  }
}
await browser.close();
console.log(JSON.stringify({ file, screens: ids.length, themes, count: shots.length, outDir }, null, 2));
