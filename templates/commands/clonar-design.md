---
description: Extrair design system completo de um site (cores, tipografia, animacoes, layout, screenshots, video)
argument-hint: "[URL do site]"
user-invocable: true
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

Garanta o Playwright primeiro (idempotente, instala so se faltar):

```bash
python3 -c "import playwright" 2>/dev/null \
  && python3 -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); p.chromium.launch(headless=True).close(); p.stop()" 2>/dev/null \
  && echo "Playwright OK" \
  || { echo "Instalando Playwright..."; pip install playwright playwright-stealth && python3 -m playwright install chromium; }
```

O script e self-contained na skill `clonar-design` (instalada junto). Monte o
comando baseado nas respostas:

```bash
python3 "$CLAUDE_PROJECT_DIR/.claude/skills/clonar-design/assets/design-scraper.py" \
  --url "URL_DO_SITE" \
  --output "$CLAUDE_PROJECT_DIR/scraping-output/NOME_DO_SITE/design" \
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

Leia o `design-data.json` completo e gere um arquivo MD estruturado e legivel:

### Estrutura do design-system.md

```markdown
# Design System — [Nome do Site]

## Paleta de Cores
| Cor | Hex | Uso | Frequencia |
(listar as cores mais usadas, agrupando: primaria, secundaria, backgrounds, texto, accent)
(converter rgb para hex)

## CSS Variables
(listar as variaveis CSS encontradas em :root, agrupando por tipo: cores, espacamentos, fontes)

## Tipografia
| Elemento | Font Family | Size | Weight | Line Height |
(agrupar por hierarquia: h1-h6, body, small, buttons, labels)
(incluir sample de texto encontrado)

## Espacamentos
(listar os valores mais recorrentes de padding/margin/gap)
(organizar como escala: xs, sm, md, lg, xl)

## Sombras
(listar box-shadows e text-shadows unicos encontrados)

## Border Radius
(listar valores unicos encontrados)

## Gradientes
(listar gradients detectados com CSS completo)

## Layout
### Breakpoints
(listar breakpoints detectados)

### Containers
(listar max-widths usados como containers)

### Secoes
(para cada secao: nome, display type, flex/grid props, dimensoes)

## Bibliotecas JS Detectadas
(listar libs encontradas com versao quando disponivel)
```

Salvar como: `design-system.md` na pasta de output.

## Passo 4: Gerar `animacoes.md`

Arquivo separado focado em **replicacao** das animacoes:

### Estrutura do animacoes.md

```markdown
# Animacoes — [Nome do Site]

## Bibliotecas Detectadas
(listar libs com versao e link para documentacao)

## @keyframes (CSS puro)
(para cada keyframe encontrado:)
### [nome-do-keyframe]
- **Onde:** elemento/classe que usa
- **Duracao:** Xs
- **Easing:** cubic-bezier(...)
- **CSS pronto para copiar:**
```css
@keyframes nome { ... }
.elemento { animation: nome Xs easing; }
```

## Transicoes CSS
(agrupar por tipo: hover, focus, scroll)
### Transicoes de Hover
- Elemento: `.classe` — propriedade Xs easing
- ...

### Transicoes de Scroll
- Elementos com data-aos="fade-up" (ou equivalente)
- ...

## Regras :hover
(CSS das regras :hover encontradas — pronto para copiar)

## Scroll Effects
(elementos com data-attributes de scroll)
(tipo de efeito: fade, slide, parallax)

## Data Attributes de Animacao
(listar data-* attributes encontrados relacionados a animacao)

## Como Replicar
(resumo pratico: quais libs instalar, quais CSS copiar, quais configs aplicar)
```

Salvar como: `animacoes.md` na pasta de output.

## Passo 5: Apresentar resultado

Mostrar ao usuario:
- Quantas cores, fontes, animacoes, secoes foram detectadas
- Quais libs JS foram encontradas (com versao)
- Quantos screenshots foram gerados (secoes + full-page)
- Se video foi gravado
- Estrutura de pastas gerada
- Resumo das animacoes mais interessantes encontradas
- Perguntar se quer ajustar algo ou gerar codigo CSS/componentes

## Notas tecnicas

- O scraper usa `playwright` + `playwright-stealth` (Python, ja instalado)
- Sites renderizados por JS (React, Next.js, Framer, etc) sao suportados
- Timeout de 30s por pagina, scroll automatico para lazy loading
- Maximo de 2000 elementos analisados (performance)
- Logs vao para stderr, dados para stdout
- Output fica em `scraping-output/NOME/design/` (relativo a raiz do projeto, `$CLAUDE_PROJECT_DIR`)
- Script (self-contained na skill): `.claude/skills/clonar-design/assets/design-scraper.py`
- Video e gravado em instancia separada do browser (contexto com recordVideo)
- Formato do video: WebM (nativo Playwright)
