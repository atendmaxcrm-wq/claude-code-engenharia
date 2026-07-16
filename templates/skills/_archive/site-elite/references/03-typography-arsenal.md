# 03 — Typography Arsenal

Inter como display e o sintoma #1 de slop. Esta lista existe para forcar escolhas tipograficas com identidade.

## Display fonts (headlines, hero, h1-h2)

### Bricolage Grotesque
- Quando: tom editorial-tecnico, signature do Aura.build
- Range: weight 200-800, ideal 700-800 para display
- Tamanho: clamp(3rem, 8vw, 7rem)
- Vibes: contemporaneo, expressivo, sem ser hostil

```js
import { Bricolage_Grotesque } from 'next/font/google'
const display = Bricolage_Grotesque({
  subsets: ['latin'],
  weight: ['700', '800'],
  display: 'swap',
  variable: '--font-display'
})
```

### Clash Display
- Quando: B2B SaaS premium, fintech moderna
- Range: weight 200-700
- Tamanho: clamp(2.5rem, 7vw, 6rem)
- Vibes: confianca, estabilidade, sem ser corporate-chato
- Fonte: Fontshare (gratuita)

### Satoshi
- Quando: produto digital, dashboard, marca jovem
- Range: weight 300-900
- Tamanho: clamp(2rem, 6vw, 5rem)
- Vibes: friendly mas profissional, alternativa real ao Inter
- Fonte: Fontshare (gratuita)

### Fraunces
- Quando: editorial, livro, publicacao long-form
- Range: weight 100-900, optical size 9-144
- Tamanho: clamp(2.5rem, 8vw, 6.5rem)
- Vibes: serif moderna com personalidade, drop caps lindos
- Anti-uso: B2B SaaS (vai parecer livraria)

### Newsreader
- Quando: blog, jornalismo, conteudo denso
- Range: weight 200-800, optical size 6-72
- Tamanho: clamp(2rem, 6vw, 5rem) display, 18px body
- Vibes: legivel em qualquer tamanho, ar editorial moderno

### IBM Plex Sans
- Quando: technical-doc, empresa de infra/dev tools
- Range: weight 100-700
- Tamanho: clamp(2rem, 6vw, 5rem)
- Vibes: corporate-tech credivel, sem ser frio

### Geist
- Quando: dev tool, Vercel-adjacent, cli-friendly
- Range: weight 100-900
- Tamanho: clamp(2rem, 6vw, 5rem)
- Vibes: neutro premium, gold standard atual para SaaS dev

### Space Grotesk
- Quando: tech indie, startup early-stage com personalidade
- Range: weight 300-700
- Tamanho: clamp(2.5rem, 7vw, 6rem)
- Vibes: geometrico mas humano

### Oswald
- Quando: brutalist, poster, sports, magazine cover
- Range: weight 200-700, ideal 600-700
- Tamanho: clamp(3.5rem, 12vw, 10rem)
- Vibes: poster impacto, condensed bold, signature do Aura

## Body fonts

### Inter (so body, NUNCA display)
- Range: weight 400 e 500
- Tamanho: 16-18px desktop, 15-16px mobile
- Line-height: 1.6
- Pareamento: vai com qualquer display acima

### IBM Plex Sans (body)
- Quando: pareada com IBM Plex display, ou com Geist
- Range: weight 400, 500
- Tamanho: 16-17px

### Geist (body)
- Quando: pareada com Geist Mono em dev tools
- Range: weight 400
- Tamanho: 16px

## Mono fonts

### JetBrains Mono
- Quando: codigo em landing, captions tecnicas, numeros tabulares
- Tamanho: 14-15px
- Features: ligaduras (=>) opcionais

### IBM Plex Mono
- Quando: pareada com IBM Plex Sans, doc tecnica
- Tamanho: 14px

### Geist Mono
- Quando: pareada com Geist Sans, dev tool
- Tamanho: 14px

## Tabela: tom -> fonte

| Tom | Display | Body | Mono |
|-----|---------|------|------|
| brutalist | Oswald 700 | Inter 400 | JetBrains 400 |
| editorial-magazine | Fraunces 600 | Newsreader 400 | — |
| retro-futurista | Space Grotesk 700 | Inter 400 | JetBrains 400 |
| solarpunk | Fraunces 500 | Newsreader 400 | — |
| technical-doc | IBM Plex Sans 600 | IBM Plex Sans 400 | IBM Plex Mono |
| art-deco | Bricolage 700 italic | Inter 400 | — |
| swiss-poster | Bricolage 800 | Inter 400 | — |
| terminal-cyberpunk | JetBrains 700 | JetBrains 400 | JetBrains 400 |
| organic-handcrafted | Fraunces 400 | Newsreader 300 | — |
| maximalist-collage | Bricolage 800 + Fraunces 700 (mistura) | Inter 400 | — |
| minimalist-japanese | Bricolage 300 | Inter 300 | — |

## Anti-pattern explicito

```jsx
// PROIBIDO
<h1 className="font-inter text-7xl font-bold">Build the Future</h1>

// CERTO
<h1 className="font-display text-7xl font-bold tracking-tight">
  {/* font-display = Bricolage Grotesque via next/font */}
</h1>
```

## Pareamentos comprovados

- Bricolage 800 display + Inter 400 body
- Oswald 700 display uppercase + Inter 400 body
- Fraunces 600 display italic + Newsreader 400 body
- Geist 700 display + Geist 400 body + Geist Mono captions
- Clash 600 display + Inter 400 body
