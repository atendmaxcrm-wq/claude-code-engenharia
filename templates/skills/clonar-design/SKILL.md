---
name: clonar-design
description: Extrair design system completo de um site (cores, tipografia, animacoes, layout, screenshots, video). Use ao clonar visual de sites.
---

Extraia o design system completo do seguinte site: $ARGUMENTS

## Passo 1: Perguntar ao usuario o que deseja

ANTES de qualquer acao, use AskUserQuestion para perguntar:

1. **O que capturar?**
   - Tudo (design tokens + animacoes + layout + screenshots + video)
   - Design tokens + layout (cores, fontes, espacamentos, estrutura)
   - Animacoes + movimentos (transitions, keyframes, scroll effects)
   - Screenshots/video apenas

2. **Capturar responsividade?**
   - Sim (3 viewports: desktop 1920px, tablet 768px, mobile 375px)
   - Nao (so desktop)

3. **Gravar video do scroll?**
   - Sim (video WebM do scroll completo da pagina)
   - Nao

## Passo 2: Executar o design scraper

Monte o comando baseado nas respostas:

```bash
python3 /root/teste-aios/aios-core/apps/monitor-server/src/scripts/design-scraper.py \
  --url "URL_DO_SITE" \
  --output "/root/teste-aios/scraping-output/NOME_DO_SITE/design" \
  --video \
  --responsive
```

Flags opcionais:
- `--video`: so inclua se o usuario pediu video
- `--responsive`: so inclua se o usuario pediu responsividade

O script:
- Usa Playwright + Stealth (headless Chromium) para renderizar JS completamente
- Extrai TODOS os estilos computados (cores, fontes, espacamentos, shadows, gradients)
- Extrai @keyframes, CSS animations, CSS transitions de todas stylesheets
- Detecta libs JS: Framer Motion, GSAP, AOS, Lenis, ScrollTrigger, Locomotive Scroll, anime.js, Three.js, Barba.js
- Mapeia elementos com data-attributes de scroll/animacao
- Captura :hover rules das stylesheets
- Detecta media queries e breakpoints
- Mapeia layout de cada secao (flex/grid, gap, padding, max-width)
- Tira screenshot de cada secao individual
- Tira screenshot full-page em cada viewport
- Grava video WebM do scroll completo (se --video)
- Salva tudo em `design-data.json`

## Passo 3: Gerar `design-system.md`

Leia o `design-data.json` completo e gere um arquivo MD estruturado:

```markdown
# Design System — [Nome do Site]

## Paleta de Cores
| Cor | Hex | Uso | Frequencia |
(listar as cores mais usadas, agrupando: primaria, secundaria, backgrounds, texto, accent)

## CSS Variables
(listar as variaveis CSS encontradas em :root)

## Tipografia
| Elemento | Font Family | Size | Weight | Line Height |

## Espacamentos
(valores mais recorrentes de padding/margin/gap)

## Sombras, Border Radius, Gradientes

## Layout (Breakpoints, Containers, Secoes)

## Bibliotecas JS Detectadas
```

## Passo 4: Gerar `animacoes.md`

Arquivo separado focado em replicacao das animacoes com CSS pronto para copiar.

## Passo 5: Apresentar resultado

Mostrar quantas cores, fontes, animacoes, secoes foram detectadas. Perguntar se quer gerar codigo CSS/componentes.

## Notas tecnicas

- Script: `/root/teste-aios/aios-core/apps/monitor-server/src/scripts/design-scraper.py`
- Output: `/root/teste-aios/scraping-output/NOME/design/`
- Video em WebM (nativo Playwright)
