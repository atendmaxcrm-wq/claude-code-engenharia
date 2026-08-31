# 07 — Quality Gates

Nenhum site sai sem passar por todos os gates abaixo. Gate falhando = nao deploya. Inclui automacao por comando.

## Pre-deploy checklist

```
[ ] 1.  Vibe questionnaire respondido e arquivado em docs/VIBE-{slug}.md
[ ] 2.  DESIGN-{marca}.md gerado (9 secoes) e seguido
[ ] 3.  Anti-slop scan: zero Inter como display
[ ] 4.  Anti-slop scan: zero copy banido ("Build the future", etc)
[ ] 5.  Anti-slop scan: zero gradiente roxo->azul
[ ] 6.  Lighthouse Performance >= 90
[ ] 7.  Lighthouse Accessibility >= 95
[ ] 8.  Lighthouse SEO >= 95
[ ] 9.  WCAG 2.1 AA: contrast 4.5:1 (3:1 para texto >24px)
[ ] 10. WCAG 2.1 AA: keyboard nav completa, focus visible
[ ] 11. WCAG 2.1 AA: alt text em todas <img>, aria-label em buttons sem texto
[ ] 12. Dark mode funciona
[ ] 13. Light mode funciona (nao so dark)
[ ] 14. Responsivo: 320px, 768px, 1280px, 1920px
[ ] 15. prefers-reduced-motion respeitado
[ ] 16. LCP < 2.5s (real device, nao throttled CPU desktop)
[ ] 17. INP < 200ms
[ ] 18. CLS < 0.1
[ ] 19. Bundle hero critico < 200KB
[ ] 20. Bundle total page < 1MB
[ ] 21. Imagens otimizadas (next/image, AVIF/WebP)
[ ] 22. Fontes via next/font (sem FOUT visivel)
[ ] 23. Build passa sem warnings
[ ] 24. TypeScript sem erros (sem any escondido)
[ ] 25. Tested em Chrome, Safari iOS, Firefox
```

## Comandos automaticos

### Lighthouse CI

```bash
npx lighthouse https://your-site.com \
  --output=json \
  --output-path=./reports/lighthouse.json \
  --chrome-flags="--headless" \
  --only-categories=performance,accessibility,seo,best-practices

# Falha se < threshold
node -e "
const r = require('./reports/lighthouse.json');
const cats = r.categories;
const fail = [];
if (cats.performance.score < 0.9) fail.push('perf');
if (cats.accessibility.score < 0.95) fail.push('a11y');
if (cats.seo.score < 0.95) fail.push('seo');
if (fail.length) { console.error('FAIL:', fail); process.exit(1); }
console.log('OK');
"
```

### axe (a11y deep)

```bash
npx @axe-core/cli https://your-site.com --exit
```

### Playwright visual diff

```js
// tests/visual.spec.js
import { test, expect } from '@playwright/test'

const viewports = [
  { width: 320, height: 568 },
  { width: 768, height: 1024 },
  { width: 1280, height: 800 },
  { width: 1920, height: 1080 }
]

for (const vp of viewports) {
  test(`home @ ${vp.width}x${vp.height}`, async ({ page }) => {
    await page.setViewportSize(vp)
    await page.goto('/')
    await expect(page).toHaveScreenshot(`home-${vp.width}.png`, {
      maxDiffPixelRatio: 0.01
    })
  })
}
```

```bash
npx playwright test --update-snapshots  # primeira vez
npx playwright test                     # CI subsequente
```

## Anti-slop scan automatizado

Script `scripts/anti-slop.sh`:

```bash
#!/usr/bin/env bash
set -e

FAIL=0

# 1. Inter como display (procura font-inter junto com text-Xxl)
if grep -rE "font-inter.*text-(4|5|6|7|8|9)xl|text-(4|5|6|7|8|9)xl.*font-inter" src/; then
  echo "FAIL: Inter usada como display"
  FAIL=1
fi

# 2. Copy banido
if grep -rEi "Build the future|Empowering|Reimagine|Seamlessly integrate|Cutting.edge|Unlock the power" src/; then
  echo "FAIL: copy banido detectado"
  FAIL=1
fi

# 3. Gradiente roxo->azul
if grep -rE "from-purple-[0-9]+ to-(blue|indigo)-[0-9]+|from-violet-[0-9]+ to-blue-[0-9]+" src/; then
  echo "FAIL: gradiente roxo->azul slop"
  FAIL=1
fi

# 4. Cards default Lovable
if grep -rE "rounded-(xl|2xl) shadow-(md|lg) bg-white" src/ | grep -i card; then
  echo "WARN: cards padrao Lovable"
fi

# 5. Hero centralizado padrao
if grep -rE "flex.*items-center.*justify-center.*min-h-screen.*text-center" src/app/page; then
  echo "WARN: hero centralizado generico"
fi

if [ "$FAIL" -eq 1 ]; then
  echo "Anti-slop scan FAILED"
  exit 1
fi
echo "Anti-slop scan: PASS"
```

## Core Web Vitals — medicao real

Nao confiar em Lighthouse local. Usar:

1. **CrUX (Chrome User Experience Report)** — dados reais agregados do Chrome
2. **Vercel Speed Insights** ou **Cloudflare Web Analytics** — RUM
3. **PageSpeed Insights** — combinacao Lighthouse + CrUX

Threshold:
- LCP < 2.5s (verde)
- INP < 200ms (verde) — substituiu FID em 2024
- CLS < 0.1 (verde)

## Bundle audit

```bash
# Next.js 16
npx @next/bundle-analyzer

# ou via build output
ANALYZE=true pnpm build
```

Suspeitos pesados (verificar se realmente precisa):
- `framer-motion` (~50KB) — so se usar
- `three` (~600KB) — tree-shake agressivo
- `gsap` (~70KB core + plugins) — OK se realmente usa
- `lodash` completo — substituir por imports especificos

## A11y manual obrigatorio

- [ ] Tab por todos elementos interativos (foco visivel sempre)
- [ ] Esc fecha modais
- [ ] Enter/Space ativa botoes
- [ ] Arrow keys em menus/tabs
- [ ] Screen reader (VoiceOver no Mac, NVDA no Windows): le ordem logica
- [ ] Zoom 200% nao quebra layout
- [ ] Sem conteudo so acessivel via hover (mobile/teclado)

## Regra dura

Se algum gate falha, voce **NAO deploya**. Voce volta, corrige, roda de novo. Sem "deploya e arruma depois". A culpa de slop em producao e organizacional, nao tecnica — comece reforcando os gates.
