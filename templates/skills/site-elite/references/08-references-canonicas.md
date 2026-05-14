# 08 — Referencias Canonicas

Sites para estudar (nao copiar). Cada um resolve UM problema especifico de design moderno premium. Capture, audite, destile, depois adapte ao seu contexto.

## Lista anotada

### emilkowal.ski
- URL: https://emilkowal.ski
- O que estudar: motion craft em React. Autor de `sonner` (toasts) e `vaul` (drawer). Trabalha no Linear web team
- Foco: micro-interacoes com proposito, fisica natural (spring), performance impecavel
- Aprendizado especifico: timing de spring, mass/damping, when to use Framer Motion `layout`

### rauno.me
- URL: https://rauno.me
- O que estudar: UI craft Linear/Vercel-adjacent. Detalhes obsessivos em radius, shadow, transicao
- Foco: sistema visual coerente sem ostentacao. Tipografia + space + cor em equilibrio
- Aprendizado especifico: como construir hierarquia sem virar barulhento

### basement.studio
- URL: https://basement.studio
- O que estudar: maximalismo cinematografico. Agencia que mistura WebGL, video, tipografia 3D
- Foco: ousadia controlada. Tudo grita mas converge num tom
- Aprendizado especifico: pacing narrativo de scroll, transicoes entre secoes

### paper.design
- URL: https://paper.design
- O que estudar: editorial layouts modernos. Tom magazine traduzido para web
- Foco: tipografia editorial, drop caps, proporcoes long-form
- Aprendizado especifico: como fazer leitura web parecer com leitura impressa

### vercel.com/design
- URL: https://vercel.com/design
- O que estudar: sistema corporate premium. Geist como display, Geist Mono em captions
- Foco: design system documentado em uso real. Tokens, primitivas, padroes
- Aprendizado especifico: como escalar coerencia em produto grande

### linear.app
- URL: https://linear.app
- O que estudar: gold standard B2B SaaS. Provavelmente o site B2B mais influente de 2022-2025
- Foco: copy precisa, motion controlada, tema dark sofisticado
- Aprendizado especifico: hierarquia de info densa sem clutter

### anti-work.studio
- URL: https://anti-work.studio
- O que estudar: agencia ousada. Tipografia gigante, tom irreverente, animacoes nao-genericas
- Foco: como ter personalidade sem ser tryhard
- Aprendizado especifico: confianca tipografica

### aura.build
- URL: https://aura.build
- O que estudar: templates WebGL prontos para landing. Fonte de IDs UnicornStudio reutilizaveis
- Foco: padrao hero shader + glassmorphism + Bricolage/Oswald
- Aprendizado especifico: ver `09-aura-build-arsenal.md`

### Ethan Mollick
- URL: https://www.oneusefulthing.org
- O que estudar: analises sobre Anthropic skills, distributional convergence, constraint vs permission
- Foco: framework conceitual para entender por que slop acontece
- Aprendizado especifico: ler "On the Generally Mediocre" e "AI Skills" posts

### Bonus — outras vale visita

- **stripe.com** — technical-doc tom, pareamento Sohne (custom)
- **arc.net** — ja descontinuado mas archive vale: motion narrativo
- **monogram.io** — agencia, tipografia experimental
- **resend.com** — Geist em uso real, dark mode bem feito
- **railway.app** — dev tool, estetica command-line moderna
- **clerk.com** — auth provider, sistema de cor consistente
- **anthropic.com** — claro: o paper "Building Effective Agents" e referencia

## Workflow Playwright para capturar

```js
// 1. Snapshot completo
await browser_navigate("https://emilkowal.ski")
await browser_snapshot()
await browser_take_screenshot({ fullPage: true, filename: "emil-full.png" })

// 2. Computed styles relevantes
const styleSummary = await browser_evaluate(`
  const sample = document.querySelectorAll('h1, h2, button, a, [class*="card"]')
  return [...sample].slice(0, 30).map(el => {
    const cs = getComputedStyle(el)
    return {
      tag: el.tagName,
      cls: el.className,
      font: cs.fontFamily,
      size: cs.fontSize,
      weight: cs.fontWeight,
      color: cs.color,
      bg: cs.backgroundColor,
      radius: cs.borderRadius,
      shadow: cs.boxShadow
    }
  })
`)

// 3. Cores dominantes
const colors = await browser_evaluate(`
  const counts = new Map()
  document.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el)
    ;[cs.color, cs.backgroundColor, cs.borderColor].forEach(c => {
      if (c && c !== 'rgba(0, 0, 0, 0)') counts.set(c, (counts.get(c) || 0) + 1)
    })
  })
  return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 15)
`)

// 4. Fontes carregadas
const fonts = await browser_evaluate(`
  return [...document.fonts].map(f => ({
    family: f.family, weight: f.weight, status: f.status
  }))
`)
```

Output alimenta `DESIGN-{marca}.md` (ver `01-design-system-distiller.md`).

## Comando de invocacao tipo

"Captura o hero do basement.studio com Playwright. Destila tipografia, cores, motion. Implementa estetica similar para [contexto], adaptando A UMA coisa diferenciadora (`02-vibe-questionnaire.md` Q4)."

## Anti-pattern de uso

Errado: "copia o linear.app exatamente"
- Resultado: imitacao detectavel, voce parece linear-clone

Certo: "estuda como linear.app organiza hierarquia de info densa em dark mode. Aplica esse PRINCIPIO ao nosso B2B com NOSSO tom (`02-vibe-questionnaire.md`) e NOSSA paleta"
- Resultado: site competente que aprendeu de fonte certa, sem ser cosplay

## Frequencia de revisita

Reabra essa lista mensalmente. Sites como linear/vercel/emilkowalski atualizam. Aura.build adiciona templates novos. Capture o que mudou.
