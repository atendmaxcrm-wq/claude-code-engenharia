# 06 — gpt-image-2 Prompts

gpt-image-2 lancado 21/04/2026. Substitui gpt-image-1 para a maioria dos casos. Para hero/background editorial, e o melhor caminho.

## Limitacao critica

**gpt-image-2 NAO suporta PNG transparente nativo.** Workarounds:

1. Usar gpt-image-1 com `background: "transparent"` (qualidade pior, mas funciona)
2. Gerar fundo solido conhecido (`#FF00FF` magenta) e fazer chroma key downstream com sharp/canvas
3. Mascarar via SVG clip-path no frontend

```js
// Fallback gpt-image-1 transparente
const img = await openai.images.generate({
  model: 'gpt-image-1',
  prompt: '...',
  size: '1024x1024',
  background: 'transparent'
})
```

## Thinking mode (signature gpt-image-2)

Adicionar literalmente "Use thinking mode to plan layout mathematically" no prompt aumenta acerto de texto PT-BR em ~20pp e melhora composicao.

```
Use thinking mode to plan layout mathematically. Then generate:
[prompt principal]
```

Funciona especialmente para:
- Texto em PT-BR dentro da imagem (banners, posters)
- Composicao com regra dos tercos
- Tipografia integrada ao cenario

## Receitas para hero/background

### Cinematografico (premium SaaS, fintech)

```
Use thinking mode to plan layout mathematically.
Photographed on Hasselblad H6D-100c, 50mm f/1.4 lens, golden hour, shallow depth of field.
Subject: [tema], placed in lower-left third.
Background: soft gradient sky, cinematic teal-orange grade.
Mood: contemplative, confident.
No text, no logo, no UI elements.
Aspect ratio: 16:9.
```

### Editorial (revista, livro, ensaios)

```
Use thinking mode to plan layout mathematically.
Magazine spread aesthetic, A24 film still inspired.
Anamorphic lens flare, 35mm grain, muted palette: bone white, ink black, ochre accent.
Composition: rule of thirds, negative space dominant left.
Subject: [tema], cropped at edge.
No text overlay, no captions.
Aspect ratio: 4:3.
```

### Solarpunk (sustentabilidade, futuro otimista)

```
Use thinking mode to plan layout mathematically.
Lush biodome interior, soft sunset light filtering through glass.
Biophilic architecture: wood, brass, climbing plants integrated structurally.
Watercolor texture overlay, soft pastel grade.
Subject: [tema] as ambient detail, not centered.
No text, no people unless specified.
Aspect ratio: 16:9.
```

### Brutalist concrete (bold, austero, autoritativo)

```
Use thinking mode to plan layout mathematically.
Raw concrete monolith architecture, tadao ando reference.
Hard directional shadows, sun at 30 degrees, monochrome grayscale.
35mm grain, slight overexposure on highlights.
Composition: heavy negative space top, mass concentrated bottom.
No text, no signage, no ornamentation.
Aspect ratio: 21:9 ultrawide.
```

### Retro-futurista (cyberpunk, neon, anos 80-90)

```
Use thinking mode to plan layout mathematically.
Tokyo street circa 1987, neon signs reflected in wet asphalt.
Anamorphic lens, magenta and cyan dominant, Blade Runner grade.
Steam, rain, atmospheric haze depth layers.
Composition: leading lines into vanishing point.
No readable text on signs (illegible kanji).
Aspect ratio: 21:9.
```

## O que NAO gerar com gpt-image-2

| Asset | Use ao inves |
|-------|--------------|
| Icones de UI | Lucide React, Iconify (SVG, escalavel, leve) |
| Logos | SVG vetor desenhado a mao ou Figma |
| Mockups de tela de app | Figma + screenshot |
| Diagramas tecnicos | Mermaid, Excalidraw, mao |
| Avatares de pessoas reais | Foto real (direitos!) ou ilustracao vetor |
| Texturas tilable | Materiais ja existentes (Poly Haven, Substance) |
| Imagens com texto longo PT-BR | Componente HTML com fonte real |

Regra: gpt-image-2 e para **atmosfera fotografica** ou **editorial unico**, nao para asset funcional.

## Workflow recomendado

```
1. Vibe questionnaire (02-vibe-questionnaire.md) -> tom escolhido
2. Escrever prompt seguindo receita do tom
3. Gerar 4 candidatos (n=4 na API)
4. Pick humano (nunca o primeiro automaticamente)
5. Upscale (DALL-E upscaler ou ESRGAN local)
6. Integrar como next/image priority
   - quality={90}, sizes correto, blurDataURL placeholder
7. Loading shift: NUNCA, reservar dimensoes via aspectRatio CSS
```

## Codigo de geracao (Node.js)

```js
import OpenAI from 'openai'
const client = new OpenAI()

async function generateHero(prompt) {
  const result = await client.images.generate({
    model: 'gpt-image-2',
    prompt: `Use thinking mode to plan layout mathematically.\n${prompt}`,
    size: '1792x1024',
    quality: 'hd',
    n: 4
  })
  return result.data.map(d => d.url)
}
```

## Integrar no Next.js

```jsx
import Image from 'next/image'
import hero from '@/assets/hero-cinematic.jpg'

export function Hero() {
  return (
    <div className="relative aspect-[16/9] w-full overflow-hidden">
      <Image
        src={hero}
        alt=""
        fill
        priority
        quality={90}
        sizes="100vw"
        placeholder="blur"
        className="object-cover"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent" />
      {/* texto sobre a imagem aqui */}
    </div>
  )
}
```

## Anti-pattern

```
// SLOP — gerar com gpt-image qualquer coisa
prompt: "modern hero image for SaaS dashboard, blue and purple gradient, 3D render"
```

```
// SIGNAL — receita especifica + thinking mode + tom forcado
prompt: "Use thinking mode to plan layout mathematically. Tadao Ando concrete chapel interior, single shaft of golden hour light cutting diagonal across raw cement floor. 35mm grain, monochrome with single warm highlight. Aspect ratio 21:9."
```
