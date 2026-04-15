# Decision Matrix — Qual Lib Usar

## Regra Rapida

```
Precisa de scroll pin/scrub/parallax?     -> GSAP ScrollTrigger
Precisa de split text?                     -> GSAP SplitText
Precisa de SVG morph/draw?                 -> GSAP MorphSVG/DrawSVG
Precisa de horizontal scroll?              -> GSAP ScrollTrigger
Precisa de timeline complexa (5+ tweens)?  -> GSAP Timeline
Precisa de page transition?                -> GSAP Timeline + Next.js router
Precisa de FLIP layout animation?          -> GSAP Flip OU AnimeJS Layout
Precisa de enter/leave DOM animation?      -> AnimeJS Layout API
Precisa de hardware-accelerated simples?   -> AnimeJS WAAPI (3KB, off-thread)
Precisa de hover/tap/mount React?          -> Framer Motion (ja instalado)
Precisa de stagger simples em lista?       -> Framer Motion (whileInView + stagger)
Precisa de loop background decorativo?     -> CSS @keyframes (NUNCA JS para loops)
```

## Matriz Detalhada

| Efeito | GSAP | AnimeJS | Framer Motion | CSS |
|--------|------|---------|---------------|-----|
| Scroll pin | **Melhor** | Nao tem | Nao tem | Nao tem |
| Scroll scrub | **Melhor** | Nao tem | Limitado | scroll-driven (basico) |
| Parallax | **Melhor** (ScrollSmoother) | Nao tem | whileInView (basico) | Nao |
| Horizontal scroll | **Melhor** | Nao tem | Nao tem | Nao |
| Split text | **Melhor** (SplitText) | Nao tem | Nao tem | Nao |
| SVG morph | **Melhor** (MorphSVG) | Basico | Nao | Nao |
| SVG draw | **Melhor** (DrawSVG) | strokeDashoffset | Nao | Basico |
| Timeline complexa | **Melhor** | Bom | Limitado | Nao |
| Stagger grid | **Melhor** (grid, axis) | Bom (stagger()) | Basico | Nao |
| FLIP layout | **Bom** (Flip plugin) | **Melhor** (Layout API) | layout prop (React only) | Nao |
| Enter/Leave DOM | Basico | **Melhor** (Layout API) | **Bom** (AnimatePresence) | Nao |
| Hardware-accel | force3D | **Melhor** (WAAPI off-thread) | Nao | will-change |
| Hover/tap | Possivel | Possivel | **Melhor** (whileHover/Tap) | :hover/:active |
| Page transition | Bom (manual) | Nao | Bom (AnimatePresence) | Nao |
| Drag & drop | **Bom** (Draggable) | Bom (Draggable) | drag prop | Nao |
| Performance (bundle) | 24KB gzip | 10KB (JS) / 3KB (WAAPI) | Ja instalado (0 extra) | 0KB |

## Combinacoes Comuns

### Landing Page Premium
- GSAP ScrollTrigger (pin hero, parallax)
- GSAP SplitText (hero heading reveal)
- Framer Motion (hover cards, CTAs)
- CSS keyframes (background mesh drift)

### Dashboard/App
- Framer Motion (quase tudo: transicoes, modais, listas)
- AnimeJS Layout API (reordenar items, filtros)
- GSAP (somente se tiver onboarding animado)

### Portfolio/Showcase
- GSAP tudo (scroll-driven, horizontal, morph, draw)
- SplitText para cada heading
- GSAP Flip para filtros de portfolio

### Formulario/Quiz (diagnostico, arquetipos)
- Framer Motion (wizard steps, progress)
- GSAP SplitText (resultado reveal)
- CSS (skeleton, shimmer)
