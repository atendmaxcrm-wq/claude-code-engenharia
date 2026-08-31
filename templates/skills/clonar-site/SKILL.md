---
name: clonar-site
description: Reconstruir um site inteiro pixel-perfect como projeto Next.js moderno. Extrai assets, CSS exato, conteudo e comportamentos secao por secao, despachando builders paralelos em worktrees. Use quando o usuario quer clonar, replicar, reconstruir ou copiar um site inteiro. Triggers: "clonar site", "copiar site", "reconstruir pagina", "clone pixel-perfect", "rebuild this site".
argument-hint: "<url1> [<url2> ...]"
user-invocable: true
---

# Clonar Site

Voce vai fazer engenharia reversa e reconstruir **$ARGUMENTS** como clone(s) pixel-perfect.

Quando multiplas URLs forem fornecidas, processe cada uma independentemente e em paralelo quando possivel, mantendo artefatos isolados em pastas dedicadas (ex: `docs/research/<hostname>/`).

Isto NAO e um processo de duas fases (inspecionar, depois construir). Voce e um **mestre de obras no canteiro** — conforme inspeciona cada secao da pagina, escreve uma especificacao detalhada em arquivo, depois entrega ao agente builder especializado com tudo que ele precisa. Extracao e construcao acontecem em paralelo, mas a extracao e meticulosa e produz artefatos auditaveis.

## Escopo Padrao

O alvo e o que `$ARGUMENTS` resolve. Clone exatamente o que esta visivel naquela URL. A menos que o usuario especifique diferente:

- **Fidelidade:** Pixel-perfect — match exato em cores, espacamentos, tipografia, animacoes
- **Incluso:** Layout visual, estrutura de componentes, interacoes, responsividade, dados mock para demo
- **Excluido:** Backend real, autenticacao, features real-time, SEO, auditoria de acessibilidade
- **Customizacao:** Nenhuma — emulacao pura

Se o usuario der instrucoes adicionais, honrar sobre os padroes.

## Pre-Flight

1. **Modo de extracao:** Este skill suporta dois modos de extracao, escolhido automaticamente:
   - **Browser MCP** (preferido se disponivel): Chrome MCP, Playwright MCP, etc. Permite interacao em tempo real (click, hover, scroll).
   - **Design Scraper** (fallback headless): Script Python em `/root/teste-aios/aios-core/apps/monitor-server/src/scripts/design-scraper.py`. Usa Playwright headless + Stealth. Funciona em VPS sem display. Extrai design tokens, animacoes, layout, screenshots e video automaticamente.
   
   **Deteccao automatica:** Verificar se ha browser MCP disponivel. Se sim, usar browser MCP. Se nao, usar design-scraper.py (confirmar que Playwright esta instalado: `python3 -c "from playwright.async_api import async_playwright; print('ok')"`).

2. Parsear `$ARGUMENTS` como uma ou mais URLs. Normalizar e validar. Se alguma invalida, pedir correcao.
3. Verificar se existe um projeto Next.js no diretorio atual. Se nao, criar scaffold com: `npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --use-npm` e instalar shadcn/ui.
4. Criar diretorios de output: `docs/research/`, `docs/research/components/`, `docs/design-references/`, `scripts/`.
5. Para multiplos sites, confirmar se roda em paralelo ou sequencial.

## Principios Fundamentais

### 1. Completude Vence Velocidade

Cada builder agent deve receber **tudo** para fazer o trabalho perfeitamente: screenshot, valores CSS exatos, assets baixados com paths locais, texto real, estrutura de componentes. Se o builder precisar ADIVINHAR qualquer coisa — uma cor, um font-size, um padding — voce falhou na extracao.

### 2. Tarefas Pequenas, Resultados Perfeitos

Quando um agente recebe "construir a secao inteira de features", ele ignora detalhes — aproxima espacamentos, chuta font-sizes. Quando recebe um unico componente focado com valores CSS exatos, ele acerta toda vez.

Avalie a complexidade de cada secao. Banner simples com heading e botao? Um agente. Secao complexa com 3 variantes de card, cada uma com hover states unicos? Um agente por variante + um para o wrapper.

**Regra de complexidade:** Se o prompt do builder exceder ~150 linhas de spec, a secao e complexa demais para um agente. Quebre em pedacos menores.

### 3. Conteudo Real, Assets Reais

Extraia texto, imagens, videos e SVGs reais do site. Isto e um clone, nao um mockup. Use `element.textContent`, baixe cada `<img>` e `<video>`, extraia `<svg>` inline como componentes React.

**Assets em camadas importam.** Uma secao que parece uma imagem e frequentemente multiplas camadas — background watercolor/gradient, PNG de foreground, icone overlay. Inspecione a arvore DOM completa de cada container e enumere TODOS os `<img>` e background-images, incluindo overlays posicionados absolutamente.

### 4. Fundacao Primeiro

Nada pode ser construido ate a fundacao existir: CSS global com design tokens do site (cores, fontes, espacamentos), tipos TypeScript para estruturas de conteudo, assets globais (fontes, favicons). Isto e sequencial e inegociavel. Tudo depois pode ser paralelo.

### 5. Extrair Como Parece E Como Se Comporta

Um website nao e um screenshot — e algo vivo. Elementos se movem, mudam, aparecem e desaparecem em resposta a scroll, hover, click, resize e tempo.

Para cada elemento, extraia sua **aparencia** (CSS exato via `getComputedStyle()`) E seu **comportamento** (o que muda, o que dispara a mudanca, e como a transicao acontece). Nao "parece 16px" — extraia o valor computado real. Nao "o nav muda no scroll" — documente o trigger exato, os estados antes/depois, e a transicao.

Comportamentos a observar (lista ilustrativa, nao exaustiva):
- Navbar que encolhe, muda background ou ganha shadow apos scroll threshold
- Elementos que animam ao entrar no viewport (fade-up, slide-in, stagger delays)
- Secoes com scroll-snap
- Parallax com velocidades diferentes
- Hover states animados (duracao e easing importam)
- Dropdowns, modais, accordions com animacoes enter/exit
- Progress indicators ou opacity transitions scroll-driven
- Carousels auto-play ou conteudo ciclico
- Transicoes dark-to-light entre secoes
- Conteudo tabbado/pill que cicla com transicoes
- Tab/accordion switching scroll-driven (IntersectionObserver, NAO click)
- Smooth scroll libraries (Lenis, Locomotive Scroll — checar `.lenis` class)
- **GSAP ScrollTrigger** — checar `data-speed`, `data-scroll`, `gsap.registerPlugin`
- **Framer Motion** — checar `motion.div`, `AnimatePresence`, `useScroll`
- **AOS (Animate On Scroll)** — checar `data-aos` attributes

### 6. Identificar Modelo de Interacao Antes de Construir

O erro mais caro em clonagem: construir UI click-based quando o original e scroll-driven, ou vice-versa.

Como determinar:
1. **Nao clique primeiro.** Scroll pela secao lentamente e observe se as coisas mudam sozinhas.
2. Se mudam, e scroll-driven. Extraia o mecanismo: `IntersectionObserver`, `scroll-snap`, `position: sticky`, `animation-timeline`, ou JS scroll listeners.
3. Se nada muda no scroll, AI SIM clique/hover para testar interatividade.
4. Documente explicitamente no component spec: "MODELO DE INTERACAO: scroll-driven com IntersectionObserver".

### 7. Extrair Todos os Estados, Nao Apenas o Default

Componentes com multiplos estados visuais: extraia TODOS.

Para conteudo tabbado/stateful:
- Clique cada tab/botao via browser MCP (ou analisando design-data.json no modo scraper)
- Extraia conteudo, imagens e dados de cards para CADA estado
- Registre qual conteudo pertence a qual estado
- Note a animacao de transicao entre estados

Para elementos scroll-dependent:
- Capture estilos no scroll position 0 (estado inicial)
- Scroll alem do trigger e capture estilos novamente (estado scrolled)
- Diff dos dois = especificacao exata do comportamento
- Registre a CSS transition e o threshold exato do trigger

### 8. Spec Files Sao a Fonte de Verdade

Cada componente recebe um arquivo de especificacao em `docs/research/components/` ANTES de qualquer builder ser despachado. Este arquivo e o contrato entre sua extracao e o builder agent.

O spec file NAO e opcional. Se despachar builder sem spec file, esta mandando instrucoes incompletas baseadas na memoria, e o builder vai chutar para preencher lacunas.

### 9. Build Deve Sempre Compilar

Cada builder agent deve verificar `npx tsc --noEmit` antes de terminar. Apos merge de worktrees, verificar `npm run build`. Build quebrado nunca e aceitavel.

## Fase 1: Reconhecimento

### Modo A: Browser MCP (se disponivel)

Navegue ate a URL alvo com browser MCP. Siga o fluxo interativo completo abaixo.

### Modo B: Design Scraper (headless, para VPS sem display)

Rode o design-scraper.py para extracao automatica:

```bash
python3 /root/teste-aios/aios-core/apps/monitor-server/src/scripts/design-scraper.py \
  --url "$ARGUMENTS" \
  --output "docs/research/scraper-output" \
  --video \
  --responsive
```

O scraper extrai automaticamente:
- **Design tokens:** cores (top 50 por frequencia), tipografia (30 estilos), espacamentos, shadows, border-radius, gradients, CSS variables
- **Animacoes:** @keyframes, CSS animations/transitions, hover rules, Web Animations API (runtime Framer Motion/GSAP)
- **Scroll behaviors:** before/after diffs (CDP mouseWheel), scroll hijack detection, scroll-snap, smooth scroll libs
- **Layout:** secoes com display/flex/grid/gap/padding/maxWidth, media queries, breakpoints, containers
- **JS Libraries:** GSAP, Framer Motion, AOS, Lenis, Locomotive Scroll, anime.js, Three.js, Barba.js
- **Interacoes avancadas:** pinned sections, parallax attrs, cursor followers, tilt cards, mouse-reactive elements, GSAP ScrollTrigger instances
- **Assets:** videos embarcados, framer configs
- **Screenshots:** full-page (3 viewports se --responsive) + por secao
- **Video:** gravacao WebM do scroll completo (se --video)

**Output:** `docs/research/scraper-output/design-data.json` (~completo) + `screenshots/` + `video/`

Apos o scraper rodar, leia `design-data.json` e use os dados para preencher os artefatos de pesquisa abaixo. O scraper faz ~80% da extracao automaticamente, mas voce ainda precisa:
1. Analisar o JSON e gerar os documentos estruturados (BEHAVIORS.md, PAGE_TOPOLOGY.md)
2. Baixar assets (imagens, favicons) que o scraper detectou mas nao baixa
3. Extrair texto verbatim de cada secao (scraper captura layout mas nao texto completo)
4. Para extracao de texto e assets complementares, use WebFetch na URL alvo

### Screenshots
- Screenshots full-page em desktop (1440px) e mobile (390px)
- Salvar em `docs/design-references/` com nomes descritivos
- No modo scraper, copiar de `docs/research/scraper-output/screenshots/` para `docs/design-references/`
- Estas sao sua referencia master

### Extracao Global
Extraia antes de qualquer outra coisa:

**Fontes** — No modo scraper: ler `design-data.json > typography` para font families e weights usados. No modo browser MCP: inspecionar `<link>` tags e computed `font-family`. Configure em `src/app/layout.tsx` usando `next/font/google` ou `next/font/local`.

**Cores** — No modo scraper: ler `design-data.json > colors` (ja ordenado por frequencia) e `cssVariables`. No modo browser MCP: extrair via getComputedStyle. Atualize `src/app/globals.css` com tokens shadcn.

**Favicons & Meta** — Baixe favicons, apple-touch-icons, OG images, webmanifest para `public/seo/`. Use WebFetch para obter o HTML da pagina e extrair `<link rel="icon">` tags. Atualize metadata do `layout.tsx`.

**Padroes globais** — No modo scraper: ler `design-data.json > animations > jsLibraries` para detectar Lenis, Locomotive, etc. Ler `keyframes` para animacoes globais. Ler `interactions` para scroll behaviors. Adicione ao `globals.css`.

### Sweep de Interacoes

**No modo browser MCP:** Passo dedicado APOS screenshots e ANTES de tudo.

**Sweep de scroll:** Scroll lento de cima a baixo via browser MCP (ou analisando design-data.json no modo scraper). Em cada secao, pause e observe:
- Header muda aparencia? Registre scroll position do trigger.
- Elementos animam ao entrar no viewport? Registre quais e tipo de animacao.
- Sidebar ou tab auto-switch ao scrollar? Registre mecanismo.
- Scroll-snap? Registre containers.
- Smooth scroll library ativa?

**Sweep de click:** Clique cada elemento interativo:
- Botoes, tabs, pills, links, cards
- Registre o que acontece: conteudo muda? Modal abre? Dropdown aparece?
- Para tabs/pills: clique CADA UM e registre conteudo por estado

**Sweep de hover:** Hover sobre cada elemento com possivel hover state:
- Botoes, cards, links, imagens, nav items
- Registre mudancas: cor, scale, shadow, underline, opacity

**Sweep responsivo:** Teste em 3 viewports (desktop 1440, tablet 768, mobile 390).

**No modo scraper:** Estas informacoes ja foram parcialmente capturadas:
- Scroll behaviors: `design-data.json > animations > scrollBeforeAfterDiffs` + `scrollCdpAnimations`
- Hover states: `design-data.json > animations > hoverDiffs` + `hoverRules`
- Responsivo: screenshots em 3 viewports + `layout > mediaQueries` + `breakpoints`
- Interacoes: `interactions` (scroll hijack, snap, pinned, parallax, tilt, cursor)
- **Limitacao do scraper:** nao consegue clicar tabs/botoes para extrair conteudo por estado. Para componentes tabbados, use WebFetch + analise do HTML para inferir estados, ou documente como "REQUER VERIFICACAO MANUAL".

Salve tudo em `docs/research/BEHAVIORS.md`.

### Topologia da Pagina
Mapeie cada secao distinta de cima a baixo. De nome a cada uma. Documente:
- Ordem visual
- Fixed/sticky overlays vs. flow content
- Layout geral (scroll container, estrutura de colunas, z-index layers)
- Dependencias entre secoes
- **Modelo de interacao** de cada secao (static, click-driven, scroll-driven, time-driven)

Salve como `docs/research/PAGE_TOPOLOGY.md`.

## Fase 2: Build da Fundacao

Isto e sequencial. Faca voce mesmo (nao delegue):

1. **Atualizar fontes** em `layout.tsx` para fontes reais do site alvo
2. **Atualizar globals.css** com color tokens, spacing, keyframes, utility classes e scroll behaviors globais
3. **Criar interfaces TypeScript** em `src/types/` para estruturas de conteudo observadas
4. **Extrair icones SVG** — encontre todos `<svg>` inline, deduplique e salve como componentes React em `src/components/icons.tsx`
5. **Baixar assets globais** — escreva e rode script Node.js (`scripts/download-assets.mjs`) que baixa todas imagens, videos e binarios para `public/`. Downloads paralelos (4 por vez).
6. Verificar: `npm run build` passa

### Script de Descoberta de Assets

Rode via browser MCP (ou analisando design-data.json no modo scraper) para enumerar todos assets:

```javascript
JSON.stringify({
  images: [...document.querySelectorAll('img')].map(img => ({
    src: img.src || img.currentSrc,
    alt: img.alt,
    width: img.naturalWidth,
    height: img.naturalHeight,
    parentClasses: img.parentElement?.className,
    siblings: img.parentElement ? [...img.parentElement.querySelectorAll('img')].length : 0,
    position: getComputedStyle(img).position,
    zIndex: getComputedStyle(img).zIndex
  })),
  videos: [...document.querySelectorAll('video')].map(v => ({
    src: v.src || v.querySelector('source')?.src,
    poster: v.poster,
    autoplay: v.autoplay,
    loop: v.loop,
    muted: v.muted
  })),
  backgroundImages: [...document.querySelectorAll('*')].filter(el => {
    const bg = getComputedStyle(el).backgroundImage;
    return bg && bg !== 'none';
  }).map(el => ({
    url: getComputedStyle(el).backgroundImage,
    element: el.tagName + '.' + el.className?.split(' ')[0]
  })),
  svgCount: document.querySelectorAll('svg').length,
  fonts: [...new Set([...document.querySelectorAll('*')].slice(0, 200).map(el => getComputedStyle(el).fontFamily))],
  favicons: [...document.querySelectorAll('link[rel*="icon"]')].map(l => ({ href: l.href, sizes: l.sizes?.toString() }))
});
```

## Fase 3: Especificacao de Componentes & Despacho

Loop principal. Para cada secao na topologia (cima para baixo), faca TRES coisas: **extrair**, **escrever spec file**, **despachar builders**.

### Passo 1: Extrair

Para cada secao, via browser MCP (ou analisando design-data.json no modo scraper):

1. **Screenshot** da secao isolada. Salvar em `docs/design-references/`.

2. **Extrair CSS** de cada elemento. Use o script abaixo — nao mexa propriedade por propriedade:

```javascript
(function(selector) {
  const el = document.querySelector(selector);
  if (!el) return JSON.stringify({ error: 'Element not found: ' + selector });
  const props = [
    'fontSize','fontWeight','fontFamily','lineHeight','letterSpacing','color',
    'textTransform','textDecoration','backgroundColor','background',
    'padding','paddingTop','paddingRight','paddingBottom','paddingLeft',
    'margin','marginTop','marginRight','marginBottom','marginLeft',
    'width','height','maxWidth','minWidth','maxHeight','minHeight',
    'display','flexDirection','justifyContent','alignItems','gap',
    'gridTemplateColumns','gridTemplateRows',
    'borderRadius','border','borderTop','borderBottom','borderLeft','borderRight',
    'boxShadow','overflow','overflowX','overflowY',
    'position','top','right','bottom','left','zIndex',
    'opacity','transform','transition','cursor',
    'objectFit','objectPosition','mixBlendMode','filter','backdropFilter',
    'whiteSpace','textOverflow','WebkitLineClamp'
  ];
  function extractStyles(element) {
    const cs = getComputedStyle(element);
    const styles = {};
    props.forEach(p => { const v = cs[p]; if (v && v !== 'none' && v !== 'normal' && v !== 'auto' && v !== '0px' && v !== 'rgba(0, 0, 0, 0)') styles[p] = v; });
    return styles;
  }
  function walk(element, depth) {
    if (depth > 4) return null;
    const children = [...element.children];
    return {
      tag: element.tagName.toLowerCase(),
      classes: element.className?.toString().split(' ').slice(0, 5).join(' '),
      text: element.childNodes.length === 1 && element.childNodes[0].nodeType === 3 ? element.textContent.trim().slice(0, 200) : null,
      styles: extractStyles(element),
      images: element.tagName === 'IMG' ? { src: element.src, alt: element.alt, naturalWidth: element.naturalWidth, naturalHeight: element.naturalHeight } : null,
      childCount: children.length,
      children: children.slice(0, 20).map(c => walk(c, depth + 1)).filter(Boolean)
    };
  }
  return JSON.stringify(walk(el, 0), null, 2);
})('SELECTOR');
```

3. **Extrair estilos multi-estado** — para elementos com multiplos estados (scroll-triggered, hover, tab ativo), capture AMBOS estados e registre o diff: "Propriedade X muda de VALOR_A para VALOR_B, trigger: TRIGGER, transicao: TRANSITION_CSS."

4. **Extrair conteudo real** — todo texto, alt attributes, aria labels, placeholders. Para conteudo tabbado, clique cada tab e extraia conteudo por estado.

5. **Identificar assets** da secao — quais imagens/videos de `public/`, quais icones de `icons.tsx`. Checar assets em camadas.

6. **Avaliar complexidade** — quantos sub-componentes distintos?

### Passo 2: Escrever Spec File

Para cada secao, criar spec em `docs/research/components/<nome>.spec.md`:

```markdown
# <NomeComponente> Especificacao

## Visao Geral
- **Arquivo alvo:** `src/components/<NomeComponente>.tsx`
- **Screenshot:** `docs/design-references/<nome-screenshot>.png`
- **Modelo de interacao:** <static | click-driven | scroll-driven | time-driven>

## Estrutura DOM
<Hierarquia de elementos>

## Estilos Computados (valores exatos de getComputedStyle)

### Container
- display: ...
- padding: ...
- maxWidth: ...

### <Elemento filho 1>
- fontSize: ...
- color: ...

## Estados & Comportamentos

### <Nome do comportamento>
- **Trigger:** <mecanismo exato>
- **Estado A (antes):** propriedades
- **Estado B (depois):** propriedades
- **Transicao:** transition CSS
- **Implementacao:** <CSS transition + scroll listener | IntersectionObserver | etc.>

### Hover states
- **<Elemento>:** <propriedade>: <antes> -> <depois>, transition: <valor>

## Conteudo por Estado (se aplicavel)

### Estado: "Tab 1"
- Titulo: "..."
- Cards: [{ titulo, descricao, imagem, link }, ...]

## Assets
- Background: `public/images/<file>.webp`
- Overlay: `public/images/<file>.png`
- Icones: <ArrowIcon>, <SearchIcon> de icons.tsx

## Texto (verbatim do site)
<Todo texto, copiado exatamente>

## Comportamento Responsivo
- **Desktop (1440px):** <descricao layout>
- **Tablet (768px):** <o que muda>
- **Mobile (390px):** <o que muda>
- **Breakpoint:** layout muda em ~<N>px
```

### Passo 3: Despachar Builders

Baseado na complexidade, despachar builder agent(s) em worktree(s) usando Agent tool com `isolation: "worktree"`:

**Secao simples** (1-2 sub-componentes): Um builder recebe a secao inteira.

**Secao complexa** (3+ sub-componentes): Quebrar. Um agente por sub-componente + um para o wrapper. Sub-componentes primeiro.

**O que cada builder recebe:**
- Conteudo completo do spec file (inline no prompt — NAO diga "leia o spec file")
- Path do screenshot em `docs/design-references/`
- Quais componentes compartilhados importar (`icons.tsx`, `cn()`, shadcn)
- Path do arquivo alvo (ex: `src/components/HeroSection.tsx`)
- Instrucao para verificar com `npx tsc --noEmit` antes de terminar
- Comportamento responsivo: breakpoints e o que muda

**Nao espere.** Assim que despachar builders de uma secao, comece a extrair a proxima. Builders trabalham em paralelo nos worktrees.

### Passo 4: Merge

Conforme builders completam:
- Merge dos worktree branches no main
- Resolver conflitos inteligentemente (voce tem contexto completo)
- Apos cada merge, verificar: `npm run build`
- Se merge introduzir erros de tipo, corrigir imediatamente

O ciclo extrair -> spec -> despachar -> merge continua ate todas secoes construidas.

## Fase 4: Montagem da Pagina

Apos todas secoes construidas e mergeadas, montar em `src/app/page.tsx`:

- Importar todos componentes de secao
- Implementar layout page-level da topologia (scroll containers, colunas, sticky, z-index)
- Conectar conteudo real aos props
- Implementar comportamentos page-level: scroll snap, animacoes scroll-driven, transicoes dark-to-light, intersection observers, smooth scroll (Lenis etc.)
- Verificar: `npm run build` limpo

## Fase 5: QA Visual

Apos montagem, NAO declare o clone completo. Compare side-by-side:

1. Abra site original e clone lado a lado (ou screenshots nos mesmos viewports)
2. Compare secao por secao, desktop (1440px)
3. Compare novamente mobile (390px)
4. Para cada discrepancia:
   - Cheque spec file — valor extraido corretamente?
   - Spec errado: re-extraia, atualize spec, corrija componente
   - Spec correto mas builder errou: corrija componente para bater com spec
5. Teste todas interacoes: scroll, clique cada botao/tab, hover
6. Verifique smooth scroll, transicoes de header, tab switching, animacoes

So apos este QA visual o clone esta completo.

## Checklist Pre-Despacho

Antes de despachar QUALQUER builder, verifique TODOS:

- [ ] Spec file escrito em `docs/research/components/<nome>.spec.md` com TODAS secoes preenchidas
- [ ] Cada valor CSS no spec e de `getComputedStyle()`, nao estimado
- [ ] Modelo de interacao identificado e documentado
- [ ] Para componentes stateful: conteudo e estilos de cada estado capturados
- [ ] Para scroll-driven: trigger threshold, estilos antes/depois, transicao registrados
- [ ] Para hover: valores antes/depois e timing registrados
- [ ] Todas imagens identificadas (incluindo overlays e composicoes em camadas)
- [ ] Comportamento responsivo documentado para desktop e mobile
- [ ] Texto verbatim do site, nao parafraseado
- [ ] Prompt do builder sob ~150 linhas de spec; se mais, secao precisa ser dividida

## O que NAO Fazer

Licoes de clones falhos — cada um custou horas de retrabalho:

- **Nao construa tabs click-based quando o original e scroll-driven (ou vice-versa).** Determine o modelo de interacao PRIMEIRO scrollando antes de clicar. Erro #1 mais caro — requer reescrita completa.
- **Nao extraia apenas o estado default.** Se tem tabs mostrando "Featured" no load, clique em cada tab e extraia tudo.
- **Nao perca imagens overlay/camadas.** Background watercolor + foreground mockup = 2 imagens. Cheque DOM tree de cada container.
- **Nao construa mockups para conteudo que e video/animacao.** Cheque se a secao usa `<video>`, Lottie ou canvas.
- **Nao aproxime classes CSS.** "Parece text-lg" esta errado se o valor computado nao bate exatamente. Extraia valores exatos.
- **Nao construa tudo num commit monolitico.** Progresso incremental com builds verificados.
- **Nao referencie docs nos prompts dos builders.** Cada builder recebe spec inline — nunca "veja DESIGN_TOKENS.md".
- **Nao pule extracao de assets.** Sem imagens, videos e fontes reais, o clone sempre parecera falso.
- **Nao de escopo demais a um builder.** Prompt ficando longo = sinal para quebrar em tarefas menores.
- **Nao junte secoes nao-relacionadas num agente.** CTA e footer sao componentes diferentes.
- **Nao pule extracao responsiva.** So inspecionar desktop = clone quebrado em tablet e mobile.
- **Nao esqueca smooth scroll libraries.** Lenis, Locomotive Scroll, etc. Scroll nativo se sente notavelmente diferente.
- **Nao despache builders sem spec file.** O spec file forca extracao exaustiva e cria artefato auditavel.

## Conclusao

Quando terminar, reporte:
- Total de secoes construidas
- Total de componentes criados
- Total de spec files escritos (deve bater com componentes)
- Total de assets baixados (imagens, videos, SVGs, fontes)
- Status do build (`npm run build`)
- Resultados do QA visual (discrepancias restantes)
- Gaps ou limitacoes conhecidos
