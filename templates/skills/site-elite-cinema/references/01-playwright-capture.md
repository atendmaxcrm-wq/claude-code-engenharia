# 01 - Playwright Capture (assets para Veo)

Recipes prontas para extrair screenshots, video e fluxos de interacao de um site/app rico, com o objetivo de alimentar prompts image-to-video do Veo 3.1. Inclui autoScroll para lazy-load, captura mobile+desktop em paralelo, hover/modal automatizado, login persistente e gravacao de video nativa.

Fontes oficiais:
- https://playwright.dev/docs/screenshots
- https://playwright.dev/docs/videos
- https://playwright.dev/docs/api/class-page#page-screenshot
- https://playwright.dev/docs/auth (storageState)

## Stack assumida

- `@playwright/test` >= 1.48 ou `playwright` standalone
- Node.js 18+
- `ffmpeg` no PATH (apt-get install ffmpeg)

## 1. autoScroll (resolve lazy-load)

Sem isso, imagens lazy-loaded ficam pretas no `fullPage: true`. Roda dentro do browser, scroll incremental.

```js
// scripts/capture/util-autoscroll.js
async function autoScroll(page) {
  await page.evaluate(async () => {
    await new Promise((resolve) => {
      let total = 0;
      const step = 200;
      const timer = setInterval(() => {
        window.scrollBy(0, step);
        total += step;
        if (total >= document.body.scrollHeight) {
          clearInterval(timer);
          resolve();
        }
      }, 100);
    });
  });
  await page.waitForLoadState('networkidle');
  await page.evaluate(() => window.scrollTo(0, 0));
}

module.exports = { autoScroll };
```

## 2. Fullpage screenshot canonico

```js
// scripts/capture/fullpage.js
const { chromium } = require('playwright');
const { autoScroll } = require('./util-autoscroll');

(async () => {
  const url = process.argv[2];
  const out = process.argv[3] || 'out/full.png';
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'load' });
  await autoScroll(page);
  await page.screenshot({ path: out, fullPage: true, animations: 'disabled' });
  await browser.close();
  console.log('saved', out);
})();
```

Rodar: `node fullpage.js https://linear.app out/linear-desktop.png`.

## 3. Section-by-section (iterando viewport)

Util quando o site e gigante e voce quer 1 frame por dobra (cada uma vira candidato a image-to-video).

```js
// scripts/capture/sections.js
const { chromium } = require('playwright');
const { autoScroll } = require('./util-autoscroll');
const fs = require('fs');

(async () => {
  const url = process.argv[2];
  const dir = process.argv[3] || 'out/sections';
  fs.mkdirSync(dir, { recursive: true });
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'load' });
  await autoScroll(page);
  const totalH = await page.evaluate(() => document.body.scrollHeight);
  const vh = 900;
  let i = 0;
  for (let y = 0; y < totalH; y += vh) {
    await page.evaluate((y) => window.scrollTo(0, y), y);
    await page.waitForTimeout(400);
    await page.screenshot({ path: `${dir}/sec-${String(i).padStart(2, '0')}.png`, animations: 'disabled' });
    i += 1;
  }
  await browser.close();
})();
```

## 4. Mobile + Desktop em paralelo

`devices` traz iPhone 13, iPad Pro 11, Pixel 7. Usar `Promise.all` cobra os dois em paralelo.

```js
// scripts/capture/dual-viewport.js
const { chromium, devices } = require('playwright');
const { autoScroll } = require('./util-autoscroll');

async function shot(launchCtx, url, out) {
  const browser = await chromium.launch();
  const ctx = await browser.newContext(launchCtx);
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'load' });
  await autoScroll(page);
  await page.screenshot({ path: out, fullPage: true, animations: 'disabled' });
  await browser.close();
}

(async () => {
  const url = process.argv[2];
  await Promise.all([
    shot({ viewport: { width: 1440, height: 900 } }, url, 'out/desktop.png'),
    shot({ ...devices['iPhone 13'] }, url, 'out/mobile.png'),
  ]);
})();
```

## 5. Hover / Focus / Modal

Estado interativo costuma ser o frame mais cinematografico para o Veo.

```js
// scripts/capture/hover.js
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newContext({ viewport: { width: 1440, height: 900 } }).then(c => c.newPage());
  await page.goto('https://linear.app/pricing');

  // hover em card de preco
  await page.locator('[data-card="pro"]').hover();
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'out/hover-pro.png' });

  // focus em campo de input
  await page.locator('input[name="email"]').focus();
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'out/focus-email.png' });

  // abrir modal
  await page.locator('button:has-text("Get a demo")').click();
  await page.waitForSelector('[role="dialog"]');
  await page.screenshot({ path: 'out/modal-demo.png' });

  await browser.close();
})();
```

## 6. Login persistente (storageState)

Quando o site rico (Stripe Dashboard, Vercel app) so revela conteudo logado. Captura uma vez, reusa N vezes.

```js
// scripts/capture/login-once.js
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  await page.goto('https://app.example.com/login');
  console.log('Faca login manualmente. Apertando ENTER no terminal salva o estado.');
  await new Promise((r) => process.stdin.once('data', r));
  await ctx.storageState({ path: 'auth.json' });
  await browser.close();
})();
```

```js
// scripts/capture/with-auth.js
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    storageState: 'auth.json',
    viewport: { width: 1440, height: 900 },
  });
  const page = await ctx.newPage();
  await page.goto('https://app.example.com/dashboard');
  await page.screenshot({ path: 'out/dashboard.png', fullPage: true });
  await browser.close();
})();
```

## 7. Video recording nativo + extract frames

Playwright grava webm direto. Bom para gerar B-roll real (cursor mexendo, scroll, modal abrindo) e depois extrair frames-chave como imagens base.

```js
// scripts/capture/video.js
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    recordVideo: { dir: 'out/video', size: { width: 1440, height: 900 } },
  });
  const page = await ctx.newPage();
  await page.goto('https://linear.app');
  await page.waitForTimeout(1500);
  await page.evaluate(() => window.scrollTo({ top: 800, behavior: 'smooth' }));
  await page.waitForTimeout(2000);
  await page.evaluate(() => window.scrollTo({ top: 1600, behavior: 'smooth' }));
  await page.waitForTimeout(2000);
  await ctx.close();
  await browser.close();
  console.log('webm salvo em out/video/');
})();
```

Extrair 1 frame por segundo via ffmpeg para virar pool de imagens base:

```bash
ffmpeg -i out/video/*.webm -vf fps=1 out/frames/frame-%03d.png
```

## 8. Estrutura de pasta recomendada para alimentar Veo

```
out/
  desktop/
    full.png             # hero candidato 1
    sec-00.png           # candidato 2 (above-the-fold)
    sec-01.png           # candidato 3 (segunda dobra)
    hover-pro.png        # estado interativo
    modal-demo.png       # estado modal
  mobile/
    full.png
    sec-00.png
  video/
    capture-001.webm
  frames/
    frame-001.png
    frame-002.png
```

Cada PNG nesse pool e candidato a `image.bytesBase64Encoded` no payload do Veo (ver 06-veo-api.md). Manter resolucao nativa, deixar o Veo redimensionar internamente.

## 9. Quando NAO usar Playwright

- Site bloqueia automacao (Cloudflare bot challenge agressivo, captcha em todas as rotas).
- URL nao publica e nao da para fazer login programatico.
- Conteudo so existe em app mobile nativo (sem versao web).
- Cliente mandou foto fisica de produto (mockup de embalagem, foto editorial, frame de filme).

Nesses casos, pedir imagem manual (mockuuups.studio, Figma export, foto crua) e pular para 03-compose-mockup.md.

## 10. Gotchas

- `animations: 'disabled'` no `page.screenshot()` congela animacoes CSS/JS (evita motion blur indesejada).
- `networkidle` pode travar em sites com long-poll. Usar `domcontentloaded` + timeout manual quando isso acontecer.
- iPhone 13 viewport vem com `deviceScaleFactor: 3`, PNG sai 1170x2532 - reduzir com sharp antes de mandar para Veo se quiser economizar banda.
- Headers `Accept-Language` podem ser necessarios em sites geo-aware: `ctx.setExtraHTTPHeaders({ 'Accept-Language': 'pt-BR,pt;q=0.9' })`.
