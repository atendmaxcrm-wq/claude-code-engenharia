# 02 - Veo 3.1 Prompts (formula + 10 templates)

Como escrever prompts que o Veo 3.1 entrega sem drift. Inclui vocabulario cinematografico que funciona, lista de movimentos confiaveis vs problematicos, regra de sutileza (5-10% deslocamento) e 10 templates prontos para colar.

Fontes oficiais:
- https://ai.google.dev/gemini-api/docs/video
- https://deepmind.google/technologies/veo/
- https://cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos
- Prompt guide (Google): https://ai.google.dev/gemini-api/docs/prompting-strategies

## Formula canonica

```
[Cinematography] + [Subject] + [Action] + [Context] + [Style/Ambiance]
```

Exemplo cru:

```
Slow cinematic push-in,                              <- cinematography
MacBook Pro on a walnut desk,                        <- subject
the screen content remains static,                   <- action
in a minimal studio with soft north-facing light,    <- context
shallow depth of field, anamorphic lens flare,       <- style
35mm grain, teal-orange grade.                       <- ambiance
```

A ordem importa. Cinematography primeiro porque o Veo usa essas keywords para escolher modelo interno de camera; subject depois para ancorar; action separado evita "drift" (camera mexe, sujeito fica).

## Vocabulario tecnico que funciona

### Lens lengths

- `18mm wide-angle` - ambiente, distorcao leve nas bordas
- `35mm` - editorial padrao, "look de filme"
- `50mm` - retrato, equivalente ao olho humano
- `85mm portrait lens` - retrato com bokeh
- `100mm macro lens` - close de produto/textura

### Lighting

- `golden hour` - laranja morno, sombras longas
- `blue hour` - azul, transicao crepuscular
- `north-facing studio light` - difuso, neutro, "Apple website"
- `single key light, 45 degrees` - dramatico, sombra dura
- `bounce card fill` - sombra suave no rosto
- `practical lights` - lampadas no plano (neon, abajur)
- `chiaroscuro` - alto contraste preto/branco

### Camera moves (confiaveis)

- `slow dolly in` - camera anda para frente em trilho
- `slow push-in` - sinonimo de dolly in, mais comum
- `dolly out` / `pull back` - camera anda para tras
- `orbit slow` - 360 lento ao redor do sujeito (funciona ate 180 graus, depois embaralha)
- `parallax shift` - sutil paralaxe lateral, sem rotacao
- `crane up` / `crane down` - vertical, eleva ou desce
- `static locked-off shot` - tripe, zero movimento (otimo se voce so quer animacao do sujeito)
- `handheld micro-shake` - tremor humano leve, da realismo

### Camera moves (evitar)

- `zoom + orbit` composto - Veo embaralha eixo
- `whip pan` - costuma virar smear ilegivel
- `dolly zoom (vertigo)` - quase nunca acerta o efeito Hitchcock
- `360 full rotation` - depois de 180 graus desmonta o sujeito
- `rack focus complexo` - mudar foco entre 3+ objetos costuma falhar

### Style descriptors

- `cinematic film grain 35mm`
- `anamorphic lens flare horizontal`
- `Kodak Portra 400 emulation`
- `bleach bypass grade`
- `teal-orange grade`
- `desaturated muted palette`
- `monochrome high-contrast`
- `chromatic aberration subtle`

## Regra anti-drift: sutileza (5-10%)

Veo 3.1 fast acerta MUITO mais quando o movimento descrito e PEQUENO. Prompts agressivos ("dramatic explosive zoom") produzem artefatos. Prompts sutis ("imperceptible slow push-in, less than 5% scale change") produzem video premium.

Boas frases ancora:

- `very slow, almost imperceptible`
- `subtle, restrained motion`
- `less than 5% scale change`
- `barely-moving camera, locked-off feeling`
- `gentle drift, no abrupt movement`

## Negative prompt obrigatorio

```
negativePrompt: "no text overlays, no captions, no watermarks, no logos, no UI mockup distortion, no extra fingers, no warped geometry, no abrupt zoom, no whip pan"
```

Sem isso, em ~30% dos generates aparecem captions/marca dagua acidentais.

## 10 templates prontos

### Template 1 - Dashboard de UI em mockup MacBook (push-in)

```
Very slow cinematic push-in, less than 5% scale change.
A modern MacBook Pro on a walnut desk, screen showing a minimalist SaaS dashboard
with deep navy panels and white type. The screen content remains static and crisp.
Soft north-facing studio light, shallow depth of field, anamorphic 35mm lens,
subtle film grain, teal-orange grade. Locked-off tripod feel with imperceptible
forward drift.
negativePrompt: "no text changing, no UI flickering, no extra fingers, no warped screen edges"
```

### Template 2 - App mobile em mockup iPhone (parallax)

```
Subtle parallax shift to the right, less than 8% horizontal travel.
An iPhone 15 Pro held vertically on a textured paper background, screen showing
a fintech app home screen with a vibrant gradient hero. The UI elements remain
crisp and unchanged. 85mm portrait lens, soft window light from the left,
shallow depth of field, gentle film grain.
negativePrompt: "no UI distortion, no hand entering frame, no scrolling animation, no text morph"
```

### Template 3 - Produto fisico (orbit slow)

```
Very slow orbit, 30 degrees of arc maximum, around the subject.
A premium matte-black fountain pen resting on Carrara marble, brass accents
catching highlight. Cinematic studio key light at 45 degrees, single shadow.
50mm macro lens, shallow depth of field, dust motes visible in light beam.
35mm grain, desaturated palette, editorial product photography style.
negativePrompt: "no full 360, no logo, no fingers, no text"
```

### Template 4 - Pessoa / avatar (closeup editorial)

```
Locked-off shot with subtle handheld micro-shake.
A young Brazilian creative professional in early 30s, sitting in a softly lit
studio, looking slightly off-camera. Wearing a neutral cream sweater. The subject
breathes naturally but does not speak. 85mm portrait lens, shallow depth of field,
window light from the left, bone-white background. Kodak Portra 400 emulation,
35mm grain.
negativePrompt: "no extra fingers, no warped face, no text, no logo, no abrupt expression change"
```

### Template 5 - Logo / marca (zoom-out reveal)

```
Very slow zoom-out reveal, starting at 90% scale, ending at 80%.
A minimalist wordmark logo in matte gold, embossed into a deep navy paper
texture. The reveal exposes more of the surrounding negative space as the
camera pulls back. Single key light at 30 degrees, hard shadow.
Static composition otherwise, locked-off feel.
negativePrompt: "no animation on the logo itself, no text deformation, no extra elements"
```

### Template 6 - Cena ambiente abstrata (luz pulsando)

```
Static locked-off shot, only the lighting changes subtly.
An empty raw concrete room, single shaft of golden light cutting diagonally
through dust motes. The light intensity pulses very gently, breathing-like,
over the 8 seconds. 35mm grain, monochrome with single warm highlight,
anamorphic flare. No camera movement, only ambient light variation.
negativePrompt: "no camera movement, no objects entering, no text, no people"
```

### Template 7 - Texto / headline (push-in com glow)

```
Imperceptible push-in, less than 3% scale change.
A bold serif headline in cream, set on a deep ink background. A soft cyan
rim glow pulses gently behind the type. Anamorphic lens flare horizontal
across the lower third. Subtle 35mm grain. The text characters remain
completely static and unchanged.
negativePrompt: "no text morphing, no letters changing, no extra characters, no warped type"
```

### Template 8 - Antes vs depois (cross-fade controlado)

```
Static locked-off composition. The frame slowly cross-dissolves between two
versions of the same workspace: the first cluttered with old monitors and
cables, the second minimal and clean with a single laptop. The transition
happens at the midpoint of the 8 seconds, very gradual, no hard cut.
North-facing studio light, 35mm grain.
negativePrompt: "no hard cut, no flash, no zoom, no warping during transition"
```

### Template 9 - Hero SaaS sem produto fisico (luz ambiente)

```
Very slow crane down, less than 10% vertical travel.
An empty modern workspace from above, slate desk, single brass lamp casting
warm circle of light. No people, no devices visible. The light flickers
imperceptibly like a real bulb. Cinematic 35mm grain, teal-orange grade,
anamorphic flare. Locked-off feel.
negativePrompt: "no objects appearing, no text, no logo, no people entering"
```

### Template 10 - Banner promocional (zoom-in dramatico controlado)

```
Slow zoom-in, ending at 110% scale, very controlled.
A premium product packaging box, deep navy with embossed gold foil typography,
on a softly lit pedestal. Single rim light from behind creates halo. The box
remains static and unmoving, only the camera approaches. 50mm lens, shallow
depth of field, editorial product style. 35mm grain.
negativePrompt: "no fingers, no hands, no text changing, no box opening, no flash"
```

## Tuning fino com `seed` e `negativePrompt`

- `seed`: integer estavel reproduz o mesmo video se prompt nao mudar. Util para iterar `negativePrompt` mantendo o resto identico.
- Sem `seed`, cada generate retorna variacao diferente (4 generates = 4 takes, escolher melhor).
- `negativePrompt` aceita lista separada por virgula, max ~300 chars uteis.

Workflow recomendado:

1. Gerar com seed aleatorio + prompt base.
2. Se gostou da composicao mas teve artefato, fixar `seed`, adicionar `negativePrompt` cobrindo o artefato.
3. Re-gerar. Iterar 2-3x ate limpo.

## Anti-pattern (NAO escrever assim)

```
SLOP: "epic cinematic dashboard reveal, mind-blowing camera movement, dramatic zoom, futuristic vibes"
```

```
SIGNAL: "Very slow cinematic push-in, less than 5% scale change. A MacBook Pro on a walnut desk, screen showing a minimalist SaaS dashboard. Static screen content. 35mm anamorphic lens, north-facing light, shallow depth of field, film grain."
```

A diferenca: substantivos concretos > adjetivos hype.
