---
name: interaction-patterns
description: Como as coisas se movem. Padroes de animacao, transicao e interacao. Use ao implementar animacoes, scroll effects ou drag&drop.
---

# Interaction Patterns

## Principios
- Performance first: budget definido ANTES de implementar
- Smooth 60fps: evitar layout thrashing, repaints desnecessarios
- Minimal motion: preferir opacity + translate sobre transform complexo
- GPU-friendly: max blur 30px animado, 50px estatico

## GSAP (Animacoes Avancadas)
- ScrollTrigger para scroll-based animations
- Pin + scrub para sections fixas
- Stagger para listas/cards (0.1-0.2s entre itens)
- scrub: 0.5 (nao 1, mais responsivo)
- scroll distance: 100% (nao 200%, evita fadiga)

## Framer Motion (Componentes React)
- whileInView para reveal on scroll
- AnimatePresence para mount/unmount
- layout prop para transicoes de layout
- NUNCA usar animate com repeat: Infinity (GPU thrashing)

## ScrollReveal
- So opacity (0→1) + translateY (20px→0)
- SEM blur, SEM perspective, SEM scale
- Stagger: 0.05-0.1s entre itens
- threshold: 0.1 (nao 0.5, usuario nao espera)

## Transicoes
- duration: 300ms (padrao), 200ms (micro), 500ms (page)
- easing: ease-out (padrao), spring (bouncy)
- hover: scale(1.02) ou brightness, NUNCA scale > 1.05

## Shapes Decorativos
- SEMPRE div estatico (position absolute, opacity baixa)
- NUNCA motion.div com animate Infinity
- blur: max 50px, opacity: max 0.3
- Cores: gradients do design system com opacity

## Loading States
- Skeleton com pulse animation (CSS, nao JS)
- Spinner minimalista para acoes
- Progress bar para uploads/processos longos

## Drag & Drop
- Feedback visual imediato (shadow, scale)
- Ghost element com opacity 0.7
- Drop zone highlight
- Snap to grid se aplicavel
