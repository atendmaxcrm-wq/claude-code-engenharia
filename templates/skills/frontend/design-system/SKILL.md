---
name: design-system
description: Padroes visuais do projeto. Use ao criar ou modificar componentes UI.
---

# Design System

## Cores
- Primary: #E7540F (laranja Makewl)
- Background: #0A0A0A (dark mode)
- Text: #F4F3F2 (claro)
- Gold/Accent: #C4A35A
- Neutro: #09090b

## Cards
- rounded-xl, border border-white/10, bg-white/5 backdrop-blur
- Padding: p-6
- Glassmorphism dark: bg-white/5 border-white/10

## Botoes
- Primary: bg-[#E7540F] text-white rounded-lg px-4 py-2
- Secondary: bg-white/10 text-white/80
- Hover: opacity-90 ou brightness

## Modais
- rounded-2xl, shadow-xl
- Overlay: bg-black/60 backdrop-blur-sm

## Inputs
- rounded-lg, border border-white/20, bg-white/5
- Focus: ring-2 ring-[#E7540F]/30

## Tipografia
- Body: Inter (sans-serif)
- Titulos: Playfair Display Variable (serif) quando aplicavel
- Hierarquia: text-4xl/3xl/2xl/xl/lg/base

## Espacamento
- Sections: py-20 a py-32
- Cards gap: gap-6 a gap-8
- Padding interno: p-6 a p-8

## Animacoes
- Shapes decorativos: div estatico (NUNCA motion.div animate Infinity)
- blur CSS: max 30px animado, 50px estatico
- Transicoes: duration-300 ease-out
- ScrollReveal: so opacity + translate (sem blur, sem perspective)

## Dark Mode
- Site 100% dark mode (cores hardcoded, sem toggle)
- Fundo principal: #0A0A0A ou #09090b
- Texto principal: #F4F3F2
- Bordas sutis: white/10
