# 04 - ffmpeg para scrub fluido em browser

Video bruto do Veo nao scruba bem em browser. Veo entrega MP4 com keyframe a cada 2-3 segundos. Quando o usuario faz scroll-scrub, o browser precisa reposicionar `currentTime` quadro a quadro, e sem keyframe por frame o decoder fica buscando o keyframe mais proximo + decodificando ate o frame alvo. Resultado: travadas visiveis, especialmente em iOS Safari.

A solucao e re-encodar com `-g 1` (keyframe a cada frame). Arquivo fica 3-5x maior, mas scrub vira frame-perfect.

Fontes:
- https://ffmpeg.org/ffmpeg.html
- https://trac.ffmpeg.org/wiki/Encode/H.264
- https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video
- https://web.dev/articles/fast-playback-with-preload (preload + faststart)

## Comando canonico

```bash
ffmpeg -i input.mp4 \
  -vf scale=1280:-2 \
  -movflags +faststart \
  -vcodec libx264 \
  -profile:v baseline \
  -level 3 \
  -pix_fmt yuv420p \
  -crf 23 \
  -g 1 \
  -an \
  output.mp4
```

## Cada flag explicada

| Flag | O que faz | Por que importa |
|------|-----------|-----------------|
| `-i input.mp4` | Arquivo de entrada | - |
| `-vf scale=1280:-2` | Resize para 1280 de largura, altura proporcional, par | Hero web 720p chega como sweet spot |
| `-movflags +faststart` | Move moov atom para o inicio do MP4 | Browser comeca a tocar antes do download completo |
| `-vcodec libx264` | H.264 (compativel com tudo) | Universal, hardware-decoded em iOS/Android |
| `-profile:v baseline` | Profile baseline | Max compat iOS, sem B-frames |
| `-level 3` | Level 3 | Garante decoder compat em devices antigos |
| `-pix_fmt yuv420p` | Subsampling 4:2:0 | iOS exige isso, sem este flag MP4 nao toca |
| `-crf 23` | Quality constant rate factor | 23 = qualidade visual transparente (18-28 e a faixa util) |
| `-g 1` | GOP = 1 (keyframe a cada frame) | SEGREDO do scrub fluido |
| `-an` | Sem audio | Hero web e muted, audio so adiciona peso |

## Por que -g 1 e o segredo

GOP (Group of Pictures) controla intervalo de keyframes. Padrao de encoder: GOP 250 (a cada 10 segundos a 25fps). Para scrub, browser precisa decodificar do keyframe mais proximo ate o frame alvo.

- Sem `-g 1` (GOP padrao): scrub salta para o keyframe, depois "alcanca" - usuario ve trancos.
- Com `-g 1`: cada frame e keyframe, scrub instantaneo, sem alcance.

Custo: arquivo 3-5x maior. Hero de 8s vira ~5-8MB em 720p (vs ~1.5MB sem -g 1). Aceitavel para hero acima da dobra.

## Variantes

### Mobile 720p (otimizado para banda)

```bash
ffmpeg -i input.mp4 \
  -vf scale=720:-2 \
  -movflags +faststart \
  -vcodec libx264 -profile:v baseline -level 3 -pix_fmt yuv420p \
  -crf 26 -g 1 -an \
  output-mobile.mp4
```

`-crf 26` (vs 23 do desktop) economiza ~30% sem perda perceptivel em tela pequena. Resultado: ~2-3MB para 8s.

### Desktop 1080p (qualidade alta)

```bash
ffmpeg -i input.mp4 \
  -vf scale=1920:-2 \
  -movflags +faststart \
  -vcodec libx264 -profile:v baseline -level 3 -pix_fmt yuv420p \
  -crf 22 -g 1 -an \
  output-desktop.mp4
```

`-crf 22` deixa um pouco mais nitido. Resultado: ~10-14MB para 8s. So usar acima de 1920x1080 viewport.

### Variante WebM (fallback bonus para Chrome/Firefox)

```bash
ffmpeg -i input.mp4 \
  -vf scale=1280:-2 \
  -c:v libvpx-vp9 \
  -crf 32 -b:v 0 \
  -g 1 -an \
  output.webm
```

VP9 com `-g 1` tambem scruba bem, ~20-30% menor que H.264. Servir via `<source>` antes do MP4 para Chrome/Firefox economizarem banda.

## Gerar poster JPEG

```bash
ffmpeg -i input.mp4 -ss 0 -vframes 1 -q:v 2 poster.jpg
```

`-ss 0` = comeca no segundo 0, `-vframes 1` = um unico frame, `-q:v 2` = qualidade JPEG alta. Usar como `poster=` no `<video>` para evitar flash branco antes do video carregar.

## Sweet spots de tamanho

| Asset | Resolucao | -crf | -g | Tamanho tipico |
|-------|-----------|------|----|-----|
| Hero acima da dobra (5-8s) | 1280x720 | 23 | 1 | 5-8 MB |
| Hero mobile (5-8s) | 720x405 | 26 | 1 | 2-3 MB |
| Section accent (3-5s, autoplay loop) | 960x540 | 24 | 1 | 1.5-2.5 MB |
| Background full-bleed (10-15s, autoplay) | 1920x1080 | 25 | 250 | 4-6 MB |

Para autoplay loop SEM scrub, voltar para `-g 250` padrao - scrub nao precisa, tamanho cai 4x.

## iOS Safari: o gotcha que mata

Sem `-g 1`, iOS Safari NAO scruba. Ele aceita o video, toca normal, mas `video.currentTime = x` em scroll-scrub trava ou pula. Testado em iPhone 13 Pro Max (iOS 17 e 18). E o unico fix confiavel.

Outros pontos de atencao para iOS:

- `playsinline` no `<video>` (sem isso, Safari mobile abre fullscreen).
- `muted` obrigatorio para autoplay.
- `preload="auto"` ou `preload="metadata"` - "none" trava o scrub na primeira interacao.
- `crossOrigin="anonymous"` se hospedar em CDN diferente, senao Safari bloqueia drawImage e Canvas.

## Quando virar canvas + image sequence

Caso extremo, raro (~5% dos projetos). Voce so precisa disso se:

- Scrub em iOS de 2017 ou anterior (iPhone 8 e inferiores).
- Scrub com taxa de frames > 60fps (animacao ultra-suave).
- Site exige zero dependencia de codec (kiosks, embarcado).

Workflow: extrair PNGs sequenciais com ffmpeg + animar via canvas + drawImage.

```bash
ffmpeg -i input.mp4 -vf "scale=1280:-2,fps=30" frames/frame-%04d.jpg
```

Em 95% dos casos, `-g 1` resolve sem precisar dessa complexidade.

## Script reutilizavel

```bash
#!/usr/bin/env bash
# scripts/encode/scrub.sh
set -euo pipefail

INPUT=${1:?usage: scrub.sh input.mp4 output.mp4 [width] [crf]}
OUTPUT=${2}
WIDTH=${3:-1280}
CRF=${4:-23}

ffmpeg -y -i "$INPUT" \
  -vf "scale=${WIDTH}:-2" \
  -movflags +faststart \
  -vcodec libx264 -profile:v baseline -level 3 -pix_fmt yuv420p \
  -crf "$CRF" -g 1 -an \
  "$OUTPUT"

echo "encoded: $OUTPUT"
ls -lh "$OUTPUT"
```

Uso: `./scrub.sh raw-from-veo.mp4 hero.mp4 1280 23`.

## Verificacao final

Sempre rodar antes de fazer commit do video:

```bash
# checar GOP
ffprobe -v error -show_entries frame=key_frame -of csv input.mp4 | head -20
# deve mostrar 1,1,1,1,1,... (todo frame e keyframe)

# checar profile/level
ffprobe -v error -show_entries stream=profile,level input.mp4
# deve mostrar Baseline / 30 (level 3.0)

# checar moov atom posicao
ffprobe -v trace input.mp4 2>&1 | grep -E "moov|mdat" | head -4
# moov deve aparecer ANTES de mdat
```

Se moov vem depois de mdat, faltou `+faststart` e o video so toca depois de download completo.
