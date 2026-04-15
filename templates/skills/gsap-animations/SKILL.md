---
name: gsap-animations
description: "Implementa animacoes avancadas com GSAP (100% gratuito) e AnimeJS. ScrollTrigger, SplitText, MorphSVG, Flip, parallax, horizontal scroll, page transitions, text reveals, pin sections. Entende o contexto do projeto e recomenda as animacoes certas. Use sempre que o usuario quiser: animacao avancada, scroll animation, text animation, parallax, pin section, horizontal scroll, page transition, SVG animation, stagger, timeline, ou qualquer efeito visual que Framer Motion nao cobre bem."
---

# GSAP Animations — Arsenal Completo de Animacoes Avancadas

Skill para implementar animacoes de nivel showcase usando GSAP (GreenSock) e AnimeJS.
Sabe recomendar a ferramenta certa para cada contexto e implementar com boas praticas.

## Novidade: GSAP 100% Gratuito (2025+)

Webflow adquiriu GSAP e **liberou TODOS os plugins gratuitamente**, incluindo os que eram pagos:
- SplitText, MorphSVG, DrawSVG, ScrollSmoother, ScrambleText, GSDevTools, Inertia
- Licenca: gratuito para uso comercial, inclusive via npm

## Filosofia

**A animacao certa no momento certo.** Cada efeito deve ter proposito: guiar atencao,
comunicar hierarquia, criar fluidez. Nunca animar por animar.

**3 libs, 3 papeis:**

| Lib | Quando usar |
|-----|-------------|
| **GSAP** | Scroll animations, pin, timelines complexas, text split, SVG morph, horizontal scroll, page transitions |
| **AnimeJS** | Layout FLIP animations, WAAPI hardware-accelerated (off-thread), animacoes leves (<3KB) |
| **Framer Motion** | Micro-interacoes React (hover, tap, mount/unmount, layout), ja instalado nos projetos |

## Quando Usar Esta Skill

- Usuario quer scroll animations (pin, parallax, scrub)
- Text reveal / split text animations
- Horizontal scroll sections
- Page transitions entre rotas
- SVG morphing / drawing
- Stagger complexo em grids
- Timeline sequenciada com multiplos elementos
- Qualquer efeito tipo "showcase" / "award-winning site"

## Quando NAO Usar

- Hover simples, tap feedback, mount/unmount -> Framer Motion (ja tem)
- Animacao de loading/skeleton -> CSS keyframes (melhor performance)
- Ajuste de timing em animacao existente -> editar direto

## Stack

| Pacote | Tamanho | Papel |
|--------|---------|-------|
| `gsap` | ~24KB gzip | Core (tweens, timelines, easing) |
| `@gsap/react` | ~2KB | Hook useGSAP para React |
| `animejs` | ~10KB gzip | Animacoes + Layout API + WAAPI (3KB) |

### Plugins GSAP (todos gratuitos, importar conforme necessidade)

| Plugin | O que faz |
|--------|-----------|
| `ScrollTrigger` | Pin, scrub, scroll-linked animations |
| `ScrollSmoother` | Smooth scroll + parallax nativo |
| `SplitText` | Split por chars/words/lines + mask/clip |
| `Flip` | Animate layout changes (FLIP technique) |
| `MorphSVGPlugin` | Morph entre SVG paths diferentes |
| `DrawSVGPlugin` | Desenhar/revelar SVG strokes |
| `MotionPathPlugin` | Animar ao longo de path SVG |
| `Draggable` | Drag & drop com momentum |
| `InertiaPlugin` | Fisica de inercia (throw, snap) |
| `Observer` | Detecta scroll/touch/pointer normalizados |
| `TextPlugin` | Typewriter / replace text animado |
| `ScrambleTextPlugin` | Scramble/decode text effect |
| `GSDevTools` | Debug visual de timelines (dev only) |

## Workflow de Implementacao (5 Passos)

### Passo 1: Diagnostico do Contexto

Antes de implementar, analisar:
```
[ ] Qual projeto? (makewl-site, diagnostico, arquetipo, legacy, disrupty, financa)
[ ] O projeto ja tem GSAP/AnimeJS instalado?
[ ] Quais animacoes ja existem? (Framer Motion, CSS)
[ ] O efeito desejado e scroll-based ou interaction-based?
[ ] Mobile-first ou desktop-first?
[ ] Performance budget: quantos elementos animados simultaneamente?
```

### Passo 2: Escolher a Ferramenta

Consultar `references/decision-matrix.md` para escolher entre GSAP, AnimeJS ou Framer Motion.

### Passo 3: Setup (se necessario)

Consultar `references/setup-nextjs.md` para configurar no projeto.

### Passo 4: Implementar

Consultar `assets/recipes.md` para receitas prontas de cada tipo de animacao.

### Passo 5: Performance Check

Consultar `references/performance.md` para validar.

## Catalogo de Efeitos (Tipo Showcase)

### Scroll-Based
1. **Pin Section** — Secao fixa enquanto conteudo anima (GSAP ScrollTrigger)
2. **Horizontal Scroll** — Scroll vertical move conteudo horizontalmente (GSAP ScrollTrigger)
3. **Parallax Layers** — Camadas movem em velocidades diferentes (GSAP ScrollSmoother)
4. **Scroll-Linked Progress** — Animacao vinculada ao % do scroll (GSAP scrub)
5. **Reveal on Scroll** — Elementos aparecem ao entrar no viewport (GSAP/Framer)
6. **SVG Mask Transition** — Mascara SVG revela conteudo no scroll (GSAP + SVG)

### Text
7. **Char-by-Char Reveal** — Cada letra aparece sequencialmente (GSAP SplitText)
8. **Word Stagger** — Palavras aparecem com delay (GSAP SplitText)
9. **Line Clip Reveal** — Linhas revelam com mask/clip (GSAP SplitText + mask)
10. **Scramble/Decode** — Texto decodifica como hacker (GSAP ScrambleText)
11. **Typewriter** — Digita letra por letra (GSAP TextPlugin)

### SVG
12. **Draw SVG** — Linha desenha progressivamente (GSAP DrawSVG)
13. **Morph SVG** — Forma transforma em outra (GSAP MorphSVG)
14. **Path Animation** — Objeto segue caminho SVG (GSAP MotionPath)

### Layout
15. **Flip Animation** — Elemento muda posicao/tamanho suavemente (GSAP Flip / AnimeJS Layout)
16. **List Reorder** — Items reordenam com transicao (AnimeJS Layout API)
17. **Enter/Leave** — Elementos entram/saem com animacao (AnimeJS Layout)

### Stagger
18. **Grid Wave** — Onda se propaga por grid (GSAP stagger grid)
19. **Center Ripple** — Animacao parte do centro (GSAP stagger from:"center")
20. **Edge Burst** — Animacao parte das bordas (GSAP stagger from:"edges")
21. **Random Pop** — Elementos aparecem aleatoriamente (GSAP stagger from:"random")

### Page Transitions
22. **Fade Crossfade** — Pagina fade out, nova fade in (GSAP + Next.js)
23. **Slide Direction** — Pagina desliza baseado na direcao (GSAP timeline)
24. **Wipe/Reveal** — Cortina revela nova pagina (GSAP + clip-path)

## Arquivos de Referencia

| Tarefa | Leia Primeiro |
|--------|--------------|
| Escolher lib certa | `references/decision-matrix.md` |
| Setup no Next.js | `references/setup-nextjs.md` |
| Regras de performance | `references/performance.md` |
| Receitas prontas | `assets/recipes.md` |
| AnimeJS specifics | `references/animejs.md` |

## Principios Inviolaveis

1. **GSAP para scroll, Framer para micro-interacoes.** Nunca misturar responsabilidades
2. **Registrar plugins uma unica vez** (no layout.tsx ou _app.tsx)
3. **useGSAP hook OBRIGATORIO em React** — garante cleanup automatico
4. **scrub: 0.5** (nao 1) — mais responsivo ao scroll
5. **scroll distance: end:"+=100%"** (nao 200%) — evita fadiga
6. **anticipatePin: 1** — sempre, previne pulo visual
7. **NUNCA animar width/height/top/left** — so transform e opacity (GPU)
8. **force3D: true** para ativar GPU acceleration
9. **Kill animations no cleanup** — previne memory leaks
10. **Mobile: desabilitar ou simplificar** animacoes pesadas (ScrollTrigger.matchMedia)
11. **SplitText: revert() no cleanup** — restaura DOM original
12. **Stagger max 0.15s entre itens** — mais que isso parece lento
13. **Pin: snap opcional** para UX de "parada" em cada secao
