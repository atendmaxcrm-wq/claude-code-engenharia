---
name: upgrade-visual
description: "Transforma qualquer sistema com 'cara de sistema' em produto premium. Aplica design system dark mode, glassmorphism, micro-interacoes, tipografia premium e efeitos visuais. Suporta Agent Teams para upgrades Total (10+ componentes). Stack: Next.js 16 + Tailwind v4 + Framer Motion. Use sempre que o usuario disser: esta feio, cara de sistema, generico, precisa melhorar visual, upgrade visual, deixar bonito, redesign, premium look, ou qualquer pedido de melhoria estetica significativa."
---

# Upgrade Visual — De Sistema Generico a Produto Premium

Transforma interfaces com "cara de sistema" em produtos premium. Aplica design system consistente, micro-interacoes, tipografia sofisticada e efeitos visuais sutis.

## Filosofia Central

**Confianca > Complexidade.** Cada elemento visual deve construir confianca no usuario, nao impressionar com efeitos. Premium nao e "mais coisas" — e menos coisas feitas com maestria.

**O que separa generico de premium:**
- Bordas quase invisiveis em vez de linhas duras
- Sombras em 3 camadas em vez de 1
- Off-black (#09090b) em vez de preto puro
- Font pairing display+body em vez de uma fonte so
- Spacing com ritmo vertical (8px grid) em vez de padding uniforme
- Spring physics em vez de ease 300ms
- Accent como ponto focal unico em vez de cores espalhadas

## Quando Usar Esta Skill

- Usuario diz "cara de sistema", "generico", "feio", "precisa melhorar visual"
- Interface funciona mas parece template Bootstrap/Material
- Formularios, dashboards, paginas de resultado precisam de upgrade
- Qualquer sistema existente que precisa de "polish" visual

## Quando NAO Usar

- Criar projeto do zero (usar `/criacao-form` para formularios)
- Apenas trocar cor ou texto (ajuste simples, nao precisa de skill)
- Performance audit (usar `/performance-audit`)

## Stack Compativel

| Tecnologia | Versao | Papel |
|------------|--------|-------|
| Next.js | 16+ | Framework |
| Tailwind CSS | v4 | Estilizacao (@theme inline) |
| Framer Motion | 12+ | Micro-interacoes e transicoes |
| Lucide React | 0.577+ | Icones |
| Inter | - | Fonte sans-serif primaria |
| Playfair Display | Variable | Fonte serif para contraste tipografico |

## Workflow de Upgrade (7 Passos)

## Modo Agent Teams (Upgrade Total)

**Quando usar:** upgrade classificado como "Total" (10+ componentes) ou rewrite completo do design system.
Para upgrade Leve (2-3 componentes) ou Medio (5-10), executar sem Agent Teams.

### Composicao do Time

| Agente | Responsabilidade | Referencia |
|--------|-----------------|------------|
| **design-tokens-dev** | globals.css, CSS variables, keyframes, scrollbar, selection | `references/design-system.md` |
| **components-dev** | Cards, inputs, botoes, progress, loading | `assets/component-recipes.md` |
| **motion-dev** | Framer Motion, hover/active states, scroll reveal, stagger | `references/motion-system.md` |
| **effects-dev** _(opcional)_ | Gradient mesh, decorative blurs, grid decorativo, accent glow | `references/design-system.md` |

### Fluxo de Execucao

**Wave 0 — Diagnostico (Explore, read-only)**
- Agente `explore` faz diagnostico visual completo (lista componentes, estado atual, gaps)
- Classifica severidade e define escopo para cada agente

**Wave 1 — Fundacao (design-tokens-dev, obrigatorio primeiro)**
- Escreve `globals.css` completo: CSS vars, utilitarios, keyframes, scrollbar, selection
- Outros agentes dependem destas variaveis — nao paralelizar com Wave 1

**Wave 2 — Implementacao Paralela**
- `components-dev`: aplica recipes em todos os componentes identificados
- `motion-dev`: implementa sistema de micro-interacoes (spring configs, scroll reveal, stagger)
- `effects-dev` _(se solicitado)_: adiciona efeitos ambientais com blur budget controlado

**Quality Gate**
- Build sem erros (`next build`)
- Verificacao visual: dark mode, hover states, animacoes, responsivo
- Checklist anti-generico: `references/anti-generic-checklist.md`

### Passo 1: Diagnostico Visual (OBRIGATORIO)

Antes de tocar em codigo, analisar o estado atual:

```
Checklist de Diagnostico:
[ ] Qual framework CSS? (Tailwind, CSS modules, styled-components)
[ ] Tem design system/globals.css? Qual estado?
[ ] Quantos componentes precisam de upgrade?
[ ] Tem animacoes existentes? Quais?
[ ] Dark mode ou light mode?
[ ] Marca tem cor accent definida?
[ ] E mobile-first ou desktop-first?
[ ] Qual a "pior" tela visualmente?
```

Classificar severidade:
- **Leve** (2-3 componentes): Aplicar CSS utilitarios + hover effects
- **Medio** (5-10 componentes): Reescrever globals.css + componentes criticos
- **Total** (10+ componentes): Rewrite completo do design system

### Passo 2: Design System (globals.css)

Ler `references/design-system.md` e aplicar:
1. Varieaveis CSS (paleta, spacing, efeitos)
2. Classes utilitarias (card-glass, card-premium, gradient-mesh, etc)
3. Keyframes (fade-up, shimmer, pulse-glow)
4. Scrollbar customizada
5. Selection color

### Passo 3: Tipografia

Ler `references/typography.md` e aplicar:
1. Font pairing (Inter + Playfair Display ou alternativa)
2. Scale tipografico (Major Third 1.25)
3. Letter-spacing por nivel (tight para headings, wide para labels)
4. Font feature settings (tnum, cv01, cv02)

### Passo 4: Componentes Core

Ler `assets/component-recipes.md` e aplicar na ordem:
1. **Cards** — glassmorphism dark, hover com elevacao
2. **Inputs/Forms** — focus ring accent, background tint
3. **Botoes** — gradiente, glow, micro-animacao
4. **Progress** — dots/bars com spring physics
5. **Loading** — skeleton shimmer em vez de spinner

### Passo 5: Micro-Interacoes

Ler `references/motion-system.md` e aplicar:
1. Spring configs por tipo de elemento
2. Hover: y:-2px + shadow expansion
3. Active: scale(0.98)
4. Scroll reveal: fade-up 20px, ease-out
5. Stagger em listas

### Passo 6: Efeitos Ambientais (OPCIONAL)

Aplicar com moderacao:
1. Gradient mesh (3 radial-gradients, opacidade 0.04-0.08)
2. Decorative blurs (max 50px estatico, 30px animado)
3. Grid decorativo com mask radial
4. Accent glow atras de CTAs

### Passo 7: Pesquisa Complementar (OPCIONAL)

Se o contexto exigir algo especifico:
1. Usar MCP 21st Magic para buscar componentes de inspiracao
2. WebSearch para tendencias especificas do nicho
3. Aceternity UI / Magic UI para efeitos avancados

## Principios Inviolaveis

1. **NUNCA preto puro.** Background #09090b ou similar off-black
2. **UMA cor accent por tela.** Todo resto em escala de cinza
3. **Bordas quase invisiveis.** rgba(255,255,255,0.06) como padrao
4. **Sombras em 3 camadas.** Near (1-3px), medium (4-16px), far (16-48px)
5. **Hover = accent tint + border + y:-2px.** Nunca mais que 2px de elevacao
6. **Active = scale(0.98).** Feedback tatil sem exagero
7. **Border-radius consistente.** 12px cards, 10px inputs, 14px badges, 9999px pills
8. **Blur budget.** 8px cards normais, 16px glass, 50px max decorativo estatico
9. **Animacoes ambientais ultra-lentas.** 30-45 segundos para mesh drift
10. **Animacoes funcionais rapidas.** 0.2-0.4s para hover/transitions
11. **Typography contrast.** Sans light (300) para headers + serif italic para keywords
12. **Inline styles para spacing critico.** (Bug Next.js 16 + Turbopack + Tailwind v4)
13. **NUNCA noise texture sem aprovacao.** Usuario ja reprovou antes
14. **Cubic-bezier padrao.** cubic-bezier(0.25, 0.4, 0.25, 1) para tudo interativo
15. **Selection color accent.** ::selection { background: var(--accent); color: white; }

## Arquivos de Referencia

| Tarefa | Leia Primeiro |
|--------|--------------|
| Montar design system | `references/design-system.md` |
| Configurar tipografia | `references/typography.md` |
| Configurar animacoes | `references/motion-system.md` |
| Aplicar componentes | `assets/component-recipes.md` |
| CSS completo para globals | `assets/globals-css-template.md` |
| Checklist anti-generico | `references/anti-generic-checklist.md` |
