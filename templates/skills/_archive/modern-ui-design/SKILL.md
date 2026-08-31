---
name: modern-ui-design
description: Principios universais de design moderno. Hierarquia visual, espacamento, tipografia, cores. Use ao criar interfaces.
---

# Modern UI Design

## Hierarquia Visual
- Um elemento dominante por secao (titulo, hero, CTA)
- Contraste para guiar o olho: tamanho, peso, cor
- Whitespace e mais importante que decoracao
- Menos elementos = mais impacto

## Tipografia
- Max 2 familias de fonte (1 serif + 1 sans-serif OU 2 pesos da mesma)
- Escala tipografica consistente (1.25x ou 1.333x ratio)
- Line-height: 1.5 para body, 1.2 para headings
- Largura maxima de texto: 65-75 caracteres (max-w-prose)

## Espacamento
- Sistema de 4px/8px (spacing: 4, 8, 12, 16, 24, 32, 48, 64)
- Padding interno > margin externo (consistencia)
- Secoes: py-20 a py-32
- Cards: p-6 a p-8
- Gaps: gap-4 (tight), gap-6 (normal), gap-8 (loose)

## Cores
- Paleta limitada: 1 primaria, 1 accent, neutros
- Contraste acessivel: 4.5:1 texto, 3:1 UI
- Cor so para significado (sucesso/erro/aviso) ou destaque
- Opacidade para variantes: primary/80, primary/60

## Layout
- Grid 12 colunas para flexibilidade
- Container max-width: 1280px (xl) ou 1024px (lg)
- Responsive: mobile-first (sm → md → lg → xl)
- Breakpoints: sm:640, md:768, lg:1024, xl:1280

## Cards
- Cantos arredondados: rounded-xl (12px)
- Sombra sutil: shadow-sm ou shadow-md
- Borda fina: border border-gray-100 (light) ou border-white/10 (dark)
- Hover: sombra aumenta OU scale(1.02)

## Botoes
- Tamanho minimo touch: 44x44px
- Padding horizontal > vertical (px-6 py-3)
- Estados: default, hover, active, disabled, loading
- Hierarquia: primary (filled) > secondary (outline) > ghost (text)

## Forms
- Labels acima dos inputs (nao placeholder-only)
- Validacao inline (nao so no submit)
- Estados: default, focus, error, success, disabled
- Mensagens de erro abaixo do campo em vermelho

## Anti-padroes
- Carousel automatico (usuario perde controle)
- Parallax excessivo (nausea, performance)
- Texto sobre imagem sem overlay (ilegivel)
- Botoes sem feedback visual (clicou mas nao sabe se funcionou)
- Modais dentro de modais (confusion)
