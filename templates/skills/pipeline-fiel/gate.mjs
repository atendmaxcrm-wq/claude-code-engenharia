// Gate visual (pipeline-fiel): renderiza cada .screen em claro+escuro (desktop 1440), detecta
// overflow horizontal por elemento e erros de console. Uso: node gate.mjs <arquivo.html>
// PORTAVEL: resolve playwright-core e chromium por env / sibling (capturar-logica-saas) / fallback.
import { readFileSync, existsSync } from 'node:fs';
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
if (!file) { console.error('uso: node gate.mjs <arquivo.html>'); process.exit(2); }
const fragment = readFileSync(file, 'utf8');
const html = `<!doctype html><html lang="pt-br"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>${fragment}</body></html>`;

const consoleErrors = [];
const browser = await chromium.launch({ executablePath: chrome, args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'] });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
page.on('pageerror', e => consoleErrors.push('PAGEERROR: ' + e.message));
await page.setContent(html, { waitUntil: 'load' });
await page.waitForTimeout(150);

const screenIds = await page.$$eval('.screen', els => els.map(e => e.id));
const results = [];
for (const theme of ['light', 'dark']) {
  await page.evaluate(t => document.documentElement.setAttribute('data-theme', t), theme);
  for (const sid of (screenIds.length ? screenIds : ['__page__'])) {
    if (sid !== '__page__') {
      await page.evaluate(id => {
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('on'));
        const el = document.getElementById(id); if (el) el.classList.add('on');
      }, sid);
    }
    await page.waitForTimeout(50);
    const m = await page.evaluate(() => {
      const docW = document.documentElement.clientWidth;
      const offenders = [];
      const scrollable = (el) => { const ox = getComputedStyle(el).overflowX; return ox === 'auto' || ox === 'scroll' || ox === 'hidden'; };
      document.querySelectorAll('body *').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.width > 0 && r.height > 0 && r.right > docW + 1) {
          // ignora conteudo largo DENTRO de um container rolavel/clipante (ex.: tabela em overflow-x:auto);
          // isso e desejado (rola no container, o body nao rola) e nao e gap.
          let p = el.parentElement, contained = false;
          while (p && p !== document.body) { if (scrollable(p)) { contained = true; break; } p = p.parentElement; }
          if (contained) return;
          const cls = (typeof el.className === 'string' && el.className) ? '.' + el.className.split(/\s+/)[0] : el.tagName.toLowerCase();
          offenders.push(cls + ' right=' + Math.round(r.right));
        }
      });
      return { docW, bodyScrollW: document.body.scrollWidth, hScroll: document.body.scrollWidth > docW + 1, offCount: offenders.length, off: offenders.slice(0, 6) };
    });
    results.push({ theme, screen: sid, ...m });
  }
}
await browser.close();
const bad = results.filter(r => r.hScroll || r.offCount > 0);
console.log(JSON.stringify({ file, screens: screenIds.length, themesTested: ['light', 'dark'], consoleErrorCount: consoleErrors.length, consoleErrors: consoleErrors.slice(0, 10), overflowBadCount: bad.length, overflowBad: bad, verdict: (consoleErrors.length === 0 && bad.length === 0) ? 'PASSA' : 'AJUSTAR' }, null, 2));
