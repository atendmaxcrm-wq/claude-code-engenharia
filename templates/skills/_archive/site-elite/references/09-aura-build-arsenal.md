# 09 — Aura.build Arsenal

Aura.build e plataforma de templates WebGL para landing. Audita-se 3 templates em 2026-04-29. Captura completa em `/tmp/aura-arsenal.md` (ler primeiro).

## Stack confirmada

| Lib | Uso | URL |
|-----|-----|-----|
| Tailwind CSS (CDN) | utility classes | `cdn.tailwindcss.com` |
| UnicornStudio | shaders WebGL | `cdn.jsdelivr.net/gh/hiunicornstudio/unicornstudio.js@v1.4.34` |
| Iconify | icone library expandida | `code.iconify.design/iconify-icon` |
| Lucide | icones SVG default | `unpkg.com/lucide@latest` |
| FxFilter.js | efeitos de filtro proprietarios | (interno aura) |

## Tipografias canonicas

1. **Bricolage Grotesque** — display headlines (template social-automation)
2. **Oswald** — poster ultra-bold (template ai-predictive)
3. **Inter** — body universal

## Paleta cinema escuro (signature)

```
--bg-primary: #000          OU #050505
--surface: rgba(255,255,255,0.05)   /* glassmorphism cards */
--text-primary: #FFFFFF
--text-muted: gray-400
```

## Orange burn signature (template social-automation)

```
--accent: rgb(234, 88, 12)              /* tailwind orange-600 */
--accent-shadow: rgba(249, 115, 22, 0.2) /* orange-500/20 */
```

Aplicacao tipica:
```css
.cta-orange {
  background: rgb(234, 88, 12);
  box-shadow: 0 0 60px rgba(249, 115, 22, 0.2);
}
```

## Padrao hero replicado em 3 templates

```
1. BG #000 ou #050505 full-bleed
2. UnicornStudio shader absolute inset-0 -z-10
3. Glassmorphism navbar fixed top
   - background: rgba(255,255,255,0.05)
   - backdrop-filter: blur(20px)
   - border-bottom: 1px solid rgba(255,255,255,0.1)
4. Title em Oswald OU Bricolage uppercase
   - font-size: clamp(3rem, 8vw, 7rem)
   - line-height: 0.95
   - letter-spacing: -0.02em
5. Subtitle Inter regular
   - font-size: 1.125rem (18px)
   - color: gray-400
   - max-width: 42rem
6. CTA gradient com box-shadow accent
   - padding: 1rem 2rem
   - rounded-full
   - box-shadow: signature accent
```

## Templates auditados

| Template | UnicornStudio ID | Tipografia | BG | Accent |
|----------|------------------|------------|-----|--------|
| ai-predictive | `zNLwDraPwdiE0ELhd8Z4` | Oswald + Inter | `#000` | white/gray |
| social-automation | `AhqzKk9mZE0EnlENMQDi` | Bricolage Grotesque + Inter | `#050505` | `rgb(234,88,12)` orange + `rgba(249,115,22,0.2)` |
| yuna | (nao carregou em tempo) | — | — | — |

`AhqzKk9mZE0EnlENMQDi` ja replicado em **crmax-site Hero** (referencia interna funcional).

## Workaround tecnico — iframe sandbox

Templates aura sao servidos em `<iframe srcdoc>`. Acesso direto ao DOM:

```js
// Dentro de Playwright/DevTools console
const iframe = document.querySelector('iframe')
const doc = iframe.contentDocument || iframe.contentWindow.document

// Capturar IDs UnicornStudio
const ids = [...doc.querySelectorAll('[data-us-project]')]
  .map(el => el.getAttribute('data-us-project'))

// Capturar fontes carregadas no iframe
const fonts = [...iframe.contentWindow.document.fonts]
  .map(f => ({ family: f.family, weight: f.weight }))

// Capturar cores principais
const colors = [...doc.querySelectorAll('*')].slice(0, 200).flatMap(el => {
  const cs = iframe.contentWindow.getComputedStyle(el)
  return [cs.color, cs.backgroundColor]
}).filter(c => c && c !== 'rgba(0, 0, 0, 0)')
```

Em screenshot direto do Playwright: o snapshot ignora iframe srcdoc. Use `browser_evaluate` com o trecho acima.

## Decision tree — qual lib WebGL usar

| Cenario | Solucao |
|---------|---------|
| Background WebGL premium ready-to-use | UnicornStudio + ID publico catalogado |
| Customizacao de paleta UnicornStudio | UnicornStudio editor visual + ID novo |
| 3D scene interativa (objeto rotacionavel) | Spline (mas pesado, ruim mobile) |
| Animacao vetorial state-driven | Rive |
| Matrix rain / particulas custom leve | Canvas 2D proprio (~30KB) |
| Gradient mesh estatico | CSS gradient em camadas (zero KB) |
| Shader custom marca-especifico | Three.js + ShaderMaterial |

## Performance — bundle Aura completo

Aura.build serve **13MB de bundle config-driven** (1 bundle pra qualquer template). Eles podem porque vendem template pronto, nao um produto que precisa converter.

**Voce nao precisa.**

Estrategia recomendada:
- Hero da home: UnicornStudio carregado (justificavel, e a primeira impressao)
- Demais paginas: CSS gradient layered como fallback
- Mobile baixo-end: detectar via `navigator.connection.effectiveType` e servir gradient estatico se 3G

```jsx
'use client'
import { useEffect, useState } from 'react'

export function HeroBg() {
  const [useShader, setUseShader] = useState(false)

  useEffect(() => {
    const conn = navigator.connection
    const slow = conn?.effectiveType === '2g' || conn?.effectiveType === '3g'
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    setUseShader(!slow && !reducedMotion)
  }, [])

  if (!useShader) {
    return (
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_#1a0a05_0%,_#000_60%)]" />
    )
  }
  return <UnicornBg projectId="AhqzKk9mZE0EnlENMQDi" />
}
```

## Replicacao recomendada

Para landing nova B2B, ponto de partida competente:

```
- BG: #050505
- Display: Bricolage Grotesque 800 uppercase clamp(3rem, 8vw, 7rem) tracking -0.02em
- Body: Inter 400 18px line-height 1.6 color gray-400
- Accent: rgb(234,88,12) (Tailwind orange-600) — UM accent, sem segundo
- Hero shader: UnicornStudio AhqzKk9mZE0EnlENMQDi OU CSS gradient layered
- Navbar: glass fixed top com backdrop-blur-xl bg-white/5 border-b border-white/10
- CTA: rounded-full px-8 py-4 com shadow accent rgba(249,115,22,0.2)
- Motion: GSAP timeline page-load (logo + nav + hero stagger), Framer Motion zero
```

## Anti-pattern: copiar template inteiro

Errado: "pega o ai-predictive e troca os textos"
- Resultado: cliente percebe (ou outro dev percebe). Voce nao construiu nada.

Certo: "destila o padrao hero (4 elementos: BG escuro + shader + glass nav + tipografia bold uppercase). Aplica com A NOSSA tipografia (`02-vibe-questionnaire.md` Q2), A NOSSA UMA cor accent (`02` Q3) e A NOSSA differentiation (`02` Q4)"
- Resultado: site competente com identidade.

## Atualizacao da captura

Ultima auditoria: 2026-04-29 (`/tmp/aura-arsenal.md`).
Reauditar quando: aura.build lancar templates novos OU UnicornStudio mudar de versao major.
