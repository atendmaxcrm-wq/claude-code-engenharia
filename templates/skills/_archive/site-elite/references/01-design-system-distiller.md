# 01 — Design System Distiller

## Workflow Vibe Design Asimov

Antes de escrever uma linha de codigo, **destilar** um Design System em markdown. Isso forca decisoes upstream e cria contrato verificavel downstream.

Fluxo:

```
URL/screenshot/Dribbble link
        |
        v
Playwright capture (screenshot + DOM + computed styles)
        |
        v
DESIGN-{marca}.md (9 secoes, formato styleseed)
        |
        v
Implementacao Tailwind/CSS (verificavel contra o doc)
```

## Output: DESIGN-{marca}.md

Estrutura obrigatoria, 9 secoes:

### 1. Identity & Voice
- 1 frase: o que essa marca faz
- 3 adjetivos de tom (escolhidos de extremos, nao do centro)
- Anti-tom: 3 adjetivos que NAO sao essa marca
- Audience: quem ve, em que estado mental, em que dispositivo

### 2. Color System
- Dominante (1 cor que ocupa 70% da tela)
- Cortante (1 accent unico, alta saturacao, ocupa <5%)
- Neutros (3 tons: BG, surface, border)
- Texto (foreground + muted)
- Banido: paletas equilibradas com 5 cores de peso similar

Formato:
```
--bg: #050505
--surface: #0F0F0F
--border: #1F1F1F
--fg: #FAFAFA
--muted: #A0A0A0
--accent: #EA580C  (orange-600, ocupa <5%)
```

### 3. Typography
- Display: 1 fonte, weight, range (clamp min/preferred/max)
- Body: 1 fonte, weight 400, line-height
- Mono: 1 fonte, uso especifico (codigo, numeros, captions)
- Tracking: letter-spacing por escala
- Anti-pattern: 3+ fontes display

Formato:
```
--font-display: "Bricolage Grotesque", weight 700-900, clamp(2.5rem, 8vw, 6rem)
--font-body: "Inter", weight 400, line-height 1.6
--font-mono: "JetBrains Mono", weight 400
```

### 4. Spacing & Layout
- Escala (multiplos de 4px ou 8px)
- Container max-width
- Grid: numero de colunas, gutter
- Breakpoints
- Rules de quebra (quando virar mobile)

### 5. Border Radius & Shadows
- Radius: 0, 2px, 4px (brutalist) OU 8px, 12px (moderno) — escolher 1 escala
- Shadows: maximo 3 niveis OU zero (brutalist)
- Banido: shadow `0 1px 3px rgba(0,0,0,0.1)` generico

### 6. Motion Principles
- Easing curves padrao (`cubic-bezier`)
- Duracao: rapida 150ms, media 350ms, lenta 700ms
- 1 motion signature (a coisa que so essa marca faz)
- prefers-reduced-motion: comportamento alternativo

### 7. Imagery Style
- Fotografia (cinematografica? editorial? snapshot?)
- Ilustracao (vetor? watercolor? 3D render?)
- Render WebGL (shader? particles? mesh?)
- Iconografia: 1 set so (Lucide OU Iconify, nao mistura)

### 8. Components Tone
- Buttons: shape, hover behavior, disabled state
- Cards: borda? shadow? glassmorphism?
- Inputs: floating label? minimal underline? bordered?
- Nav: pill fixa? sidebar? hamburger?

### 9. Anti-patterns
- O que essa marca NUNCA faz visualmente
- Lista 5-10 itens especificos com exemplo

## Capturar referencia ao vivo (Playwright)

```js
browser_navigate("https://emilkowal.ski")
browser_snapshot()
browser_take_screenshot({ fullPage: true })
browser_evaluate(`
  const stylesUsed = new Set();
  document.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    stylesUsed.add(JSON.stringify({
      font: cs.fontFamily,
      size: cs.fontSize,
      color: cs.color,
      bg: cs.backgroundColor,
      radius: cs.borderRadius
    }));
  });
  return [...stylesUsed].slice(0, 50);
`)
```

Resultado alimenta as 9 secoes do `DESIGN-{marca}.md`.

## Como usar downstream

Toda decisao de Tailwind/CSS no projeto deve ter justificativa rastreavel ao `DESIGN-{marca}.md`. Se nao tem, adicione ao doc OU mude a implementacao. Doc e contrato vivo.

## Exemplo de invocacao

"Destila o design system de basement.studio em DESIGN-basement.md seguindo as 9 secoes. Captura via Playwright. Foco no que e ESPECIFICO da marca, nao generico."
