# 03 - Compose Mockup (UI dentro de device PNG)

Screenshot chapado de UI nao funciona bem no Veo: o modelo ve "interface 2D" e tende a tentar animar elementos, gerar artefatos de UI ou distorcer texto. Compor a screenshot DENTRO de um mockup fotografico de device (MacBook, iPhone, iPad) muda tudo: o Veo passa a tratar a cena como objeto fisico em estudio e a animacao fica cinematica.

Fontes:
- https://sharp.pixelplumbing.com/api-composite
- https://mockuuups.studio
- https://www.ramotion.com/agency/mockups/
- https://www.ls.graphics/free

## Por que mockup importa

| Input para Veo | Resultado tipico |
|----------------|------------------|
| PNG cru de dashboard SaaS | Veo tenta animar a UI, texto vira borrao, scroll fake aparece |
| PNG do mesmo dashboard COMPOSTO num mockup de MacBook | Veo trata como produto, da push-in/orbit/parallax limpo |

Regra: sempre compor antes de enviar como `image.bytesBase64Encoded`.

## Workflow completo

1. Capturar screenshot da UI (ver 01-playwright-capture.md).
2. Pegar um mockup PNG com area transparente onde a tela do device fica.
3. Calcular as coordenadas da area da tela (uma vez por mockup).
4. Compor screenshot dentro da area com `sharp.composite()`.
5. Salvar resultado como imagem final para Veo.

## Codigo Node com sharp (canonico)

```js
// scripts/compose/mockup.js
const sharp = require('sharp');

async function composeMockup({ screenshot, mockup, screen, output }) {
  // screen = { left, top, width, height } em pixels do mockup
  const resized = await sharp(screenshot)
    .resize(screen.width, screen.height, { fit: 'cover' })
    .toBuffer();

  await sharp(mockup)
    .composite([
      {
        input: resized,
        left: screen.left,
        top: screen.top,
      },
    ])
    .toFile(output);

  console.log('composed', output);
}

module.exports = { composeMockup };
```

### Uso

```js
// scripts/compose/run.js
const { composeMockup } = require('./mockup');

(async () => {
  // MacBook Pro 16" mockup 1920x1080, area de tela:
  await composeMockup({
    screenshot: 'out/desktop.png',
    mockup: 'mockups/macbook-16-walnut-desk.png',
    screen: { left: 280, top: 120, width: 1360, height: 850 },
    output: 'out/hero-macbook.png',
  });

  // iPhone 13 mockup 1080x1920, area de tela:
  await composeMockup({
    screenshot: 'out/mobile.png',
    mockup: 'mockups/iphone-13-marble.png',
    screen: { left: 240, top: 280, width: 600, height: 1300 },
    output: 'out/hero-iphone.png',
  });
})();
```

## Como descobrir as coordenadas da area de tela do mockup

Uma vez por mockup. Abre no Figma/Photoshop, mede em pixels. Ou usa este script de inspecao:

```js
// scripts/compose/inspect-mockup.js
const sharp = require('sharp');

(async () => {
  const meta = await sharp(process.argv[2]).metadata();
  console.log('mockup size:', meta.width, 'x', meta.height);
  // abrir no preview e medir manualmente onde a tela transparente comeca/termina
})();
```

Documentar num JSON do projeto:

```json
{
  "macbook-16-walnut": { "left": 280, "top": 120, "width": 1360, "height": 850 },
  "iphone-13-marble":  { "left": 240, "top": 280, "width": 600,  "height": 1300 },
  "ipad-pro-11-cafe":  { "left": 180, "top": 200, "width": 800,  "height": 1100 }
}
```

## Mockups recomendados (gratuitos)

- https://www.ls.graphics/free - MacBook Pro 16, iPhone 15 Pro, iPad Pro 11, todos com PSD/PNG transparente
- https://www.ramotion.com/agency/mockups/ - cenas de estudio com luz cinematografica ja embutida
- https://www.mockuuups.studio - colecao gigante, alguns gratis, todos com PNG transparente na area da tela
- https://uimaker.io/mockups/ - cenas mobile in-context (mao segurando iPhone, pessoa usando MacBook)

Baixar em PNG (nao PSD) com transparencia. Salvar em `mockups/` do projeto.

## Resize final para Veo

Veo aceita ate ~2048px no lado maior. Para 16:9 cinema, padronizar em 1920x1080 ou 1280x720.

```js
// scripts/compose/resize-for-veo.js
const sharp = require('sharp');

async function resizeForVeo(input, output, target = 1920) {
  await sharp(input)
    .resize(target, null, { fit: 'inside' })
    .jpeg({ quality: 92 })
    .toFile(output);
}

module.exports = { resizeForVeo };
```

## Casos de uso por tipo de site

| Site | Mockup recomendado |
|------|--------------------|
| Dashboard SaaS (Linear, Notion, Vercel) | MacBook Pro 16" em desk de walnut |
| App fintech mobile | iPhone 15 Pro em superficie de marmore |
| Landing page corporativa | iPad Pro 11" inclinado em mesa de cafe |
| Site editorial (revista, blog) | MacBook + caderno + caneta (cena editorial) |
| Comparison antes/depois | Dois MacBooks lado a lado, mesma cena |
| Produto fisico com app | iPhone + objeto fisico em composicao |

## Alternativa: gpt-image-2 quando nao tem PNG transparente

Quando voce nao acha o mockup certo, gerar a cena inteira via gpt-image-2 com a UI ja "embutida". Funciona, mas perde fidelidade da UI real.

```js
const OpenAI = require('openai');
const client = new OpenAI();

async function generateMockupScene() {
  const r = await client.images.generate({
    model: 'gpt-image-2',
    prompt: `Use thinking mode to plan layout mathematically.
Photorealistic MacBook Pro 16" on a walnut wood desk in a minimal studio.
The screen shows a clean dashboard UI with deep navy panels, white serif headings,
and a single cyan accent bar. Soft north-facing window light from the left,
shallow depth of field, 35mm grain, editorial product photography style.
No text legible, no logos.
Aspect ratio: 16:9.`,
    size: '1792x1024',
    quality: 'hd',
    n: 1,
  });
  return r.data[0].url;
}
```

Trade-off: gerar a cena via gpt-image-2 e mais rapido (1 chamada vs Playwright+sharp), mas a UI nao e a UI real do produto. Para hero de cliente real, sempre prefira compor com Playwright + sharp.

## Anti-pattern

```
SLOP: mandar screenshot.png cru para o Veo
```

```
SIGNAL: mandar hero-macbook-composed-on-walnut-desk.jpg para o Veo
```

A diferenca em qualidade do video final e enorme: o primeiro vira animacao de "interface mexendo", o segundo vira plano de produto cinematografico.

## Gotchas

- `fit: 'cover'` no resize da screenshot pode cortar topo/base. Se a UI tem header importante, usar `fit: 'contain'` + `background: { r,g,b }` matching.
- Mockups com sombra/reflexo sobre a tela: NAO acontece automatico, vem dentro do PNG do mockup.
- Salvar como JPEG quality 92 economiza ~70% do tamanho vs PNG, sem perda visivel em hero.
- Veo aceita JPEG e PNG no `bytesBase64Encoded`. PNG so se voce precisa de transparencia (raro neste fluxo).
