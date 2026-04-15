# Design System — Diagnostico Interativo

Referencia completa do design system. Dark mode, accent customizavel, gradient mesh.

---

## Paleta de Cores (CSS Variables)

```css
:root {
  /* Base */
  --background: #09090b;       /* Fundo principal */
  --foreground: #fafafa;       /* Texto principal */
  --card-bg: #18181b;          /* Background de cards */
  --card-border: #27272a;      /* Borda de cards */
  --muted: #a1a1aa;            /* Texto secundario */

  /* Star Rating */
  --star-empty: #3f3f46;       /* Estrela vazia */
  --star-filled: #f59e0b;      /* Estrela preenchida (amber) */
  --star-hover: #fbbf24;       /* Estrela hover */

  /* Severidade */
  --urgent: #ef4444;           /* Notas 1-2 (vermelho) */
  --attention: #eab308;        /* Nota 3 (amarelo) */
  --good: #3b82f6;             /* Nota boa (azul) */
  --excellent: #22c55e;        /* Nota 4 (verde) */

  /* Accent (customizar por marca) */
  --accent: #E7540F;           /* Cor principal da marca */
  --accent-light: #FF7A3D;     /* Variante clara do accent */
}
```

## Tailwind v4 Theme Mapping

```css
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card-bg: var(--card-bg);
  --color-card-border: var(--card-border);
  --color-muted: var(--muted);
  --color-star-empty: var(--star-empty);
  --color-star-filled: var(--star-filled);
  --color-star-hover: var(--star-hover);
  --color-urgent: var(--urgent);
  --color-attention: var(--attention);
  --color-good: var(--good);
  --color-excellent: var(--excellent);
  --color-accent: var(--accent);
  --color-accent-light: var(--accent-light);
  --font-sans: var(--font-inter);
}
```

---

## Texturas e Backgrounds

### Gradient Mesh
Radial gradients sutis para profundidade:
```css
.gradient-mesh {
  background:
    radial-gradient(ellipse 80% 50% at 20% 40%, rgba(accent, 0.08), transparent),
    radial-gradient(ellipse 60% 40% at 80% 20%, rgba(59, 130, 246, 0.05), transparent),
    radial-gradient(ellipse 50% 50% at 50% 80%, rgba(139, 92, 246, 0.04), transparent);
}
```

---

## Tipografia

### Fontes (next/font/google)
```typescript
import { Inter, Playfair_Display } from "next/font/google";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
});

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  style: ["normal", "italic"],
});
```

**Inter** — Fonte principal para body, labels, botoes, textos gerais.
**Playfair Display Variable** — Fonte serif para palavras-chave em italico nos titulos (ex: "Arquetipo", "Clinicas"). Transmite sofisticacao e diferenciacao visual.

### Escala Tipografica
| Elemento | Tamanho | Peso | Extras |
|----------|---------|------|--------|
| H1 (header premium) | clamp(28px, 6vw, 48px) | 300 (light) | tracking-[-0.02em], leading-[1.1] |
| H1 keyword (italico) | 1.15em relativo | normal | font-family: Playfair, italic, cor accent-light |
| H1 (titulo resultado) | 2xl-3xl | bold | tracking-tight |
| H2 (secao analise) | 1.25rem | 700 | border-bottom |
| H3 (sub-secao) | 1rem | 600 | ::before accent bar |
| Body | 0.875rem | 400 | line-height 1.75 |
| Label | xs (12px) | medium | uppercase tracking-wider |
| Subtitle (header) | 13px | 300 | opacity 0.45, letterSpacing 0.08em |
| Muted | [10px]-[11px] | medium | text-muted |

---

## Componentes de UI

### Cards
```css
/* Card padrao */
rounded-2xl border border-card-border bg-card-bg/60 backdrop-blur-sm

/* Card com shadow */
shadow-xl shadow-black/20
```

### Botoes

**Primary (submit/CTA):**
```css
bg-gradient-to-r from-accent to-accent-light px-8 py-3.5 rounded-full
text-sm font-semibold text-white shadow-lg shadow-accent/20
hover:shadow-xl hover:shadow-accent/30
```

**Secondary (reset):**
```css
border border-card-border bg-card-bg rounded-full px-5 py-2.5
text-sm font-medium text-muted
hover:border-foreground/20 hover:text-foreground
```

**Nav (prev/next):**
```css
h-12 w-12 rounded-full border border-card-border bg-card-bg text-muted
hover:border-foreground/20 hover:text-foreground
disabled:opacity-30
```

### Header Premium (MakewlHeader)

Padrao visual para a tela inicial de formularios/diagnosticos:

**Logo com linhas:**
```css
/* Linha accent de cada lado do logo */
w-8 h-px bg-[var(--color-accent)] opacity-50
/* Layout: flex items-center justify-center gap-3 */
/* Logo: h-5 w-auto (20px height) */
```

**Titulo com keyword italica:**
```css
/* Container */
font-light leading-[1.1] tracking-[-0.02em]
font-size: clamp(28px, 6vw, 48px)

/* Keyword em italico */
font-family: var(--font-playfair), serif
font-style: italic
font-size: 1.15em
color: var(--color-accent-light)  /* #FF7A3D */
```

**Ornamento divisor:**
```css
/* Linhas gradiente: 60px cada */
background: linear-gradient(90deg, transparent, rgba(231,84,15,0.25), transparent)

/* Losango central: 5x5px */
bg-[var(--color-accent)] rotate-45 opacity-60
```

### Logo Asset
- **Arquivo:** `/public/logo-makewl.png`
- **Dimensoes originais:** 2528 x 490px
- **Aspect ratio:** 5.16:1
- **Tamanhos responsivos:** sm=24px, md=32px, lg=44px height (width auto)

### Status Badges
```css
/* Critico/Urgente */
border-urgent/30 bg-urgent/10 text-urgent

/* Atencao */
border-attention/30 bg-attention/10 text-attention

/* Excelente */
border-excellent/30 bg-excellent/10 text-excellent
```

### Star Glow
```css
.star-glow {
  filter: drop-shadow(0 0 6px rgba(245, 158, 11, 0.5));
}
```

---

## Analysis Content CSS

Formatacao do HTML gerado pela IA:

```css
.analysis-content { color: var(--muted); line-height: 1.75; font-size: 0.875rem; }
.analysis-content h2 { color: var(--foreground); font-size: 1.25rem; font-weight: 700; margin-top: 2.5rem; border-bottom: 1px solid var(--card-border); }
.analysis-content h3 { color: var(--foreground); font-size: 1rem; font-weight: 600; }
.analysis-content h3::before { content: ""; width: 3px; height: 1em; background: var(--accent); border-radius: 2px; }
.analysis-content strong { color: var(--foreground); font-weight: 600; }
.analysis-content ul { list-style: none; padding-left: 0; }
.analysis-content ul li::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--accent); opacity: 0.6; }
```

---

## Animacoes

### Ease Padrao
`[0.25, 0.46, 0.45, 0.94]` — usado no carousel

### Transicoes entre Estados
- AnimatePresence mode="wait"
- opacity 0→1→0, duration 0.3-0.4s

### Carousel Slides
- Enter: x ±80, opacity 0, scale 0.95
- Duration: 0.35s

### Animacoes Internas do Slide (Anti-Flash Mobile)
**REGRA CRITICA:** Elementos dentro do slide (titulo, subtitulo, opcoes) NUNCA devem comecar com `opacity: 0`. Isso causa "flash/piscar" no mobile porque a animacao do slide (AnimatePresence) ja faz fade-in do container, e animacoes internas com opacity 0 criam um momento vazio visivel.

**Padrao correto:**
- Titulo: `initial={{ opacity: 0.8, y: 6 }}`, delay 0.05s, duration 0.25s
- Subtitulo: `initial={{ opacity: 0.6, y: 4 }}`, delay 0.08s, duration 0.25s
- Opcoes/items: `initial={{ opacity: 0.7, y: 6 }}`, stagger delay curto (original * 0.4), duration 0.25s
- Icone/emoji: spring (scale 0→1, rotate) — esse pode comecar em 0 pois e pequeno e rapido

**Principio:** Opacity inicial alta (0.6-0.8) + delays minusculos (< 0.12s) + duracao curta (0.25s) = animacao perceptivel SEM flash.

### Emoji/Icon Spring
- type: "spring", stiffness: 300, damping: 15
- scale 0→1, rotate -30→0

### Pulsing Orb (Loading)
- 3 camadas: scale [1, 1.4, 1], opacity [0.3, 0.1, 0.3]
- Duration: 2s, repeat Infinity
- Delays: 0s, 0.3s, 0.5s

### Star Fill
- scale: [1, 1.4, 1], rotate: [0, -15, 15, 0]
- duration: 0.4s

### Streaming Dots
- 3 dots: opacity [0.3, 1, 0.3]
- duration: 0.8s, delay: i * 0.15

### Streaming Cursor
- opacity [1, 0], duration: 0.6s, repeat Infinity

---

## Scrollbar
```css
/* Scrollbar dark padrao */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--background); }
::-webkit-scrollbar-thumb { background: var(--card-border); border-radius: 3px; }

/* Hide scrollbar — funcional mas invisivel (para area de opcoes no mobile) */
.hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
.hide-scrollbar::-webkit-scrollbar { display: none; }
```

---

## Responsividade e Layout Mobile

### Principios
- Mobile-first com breakpoints sm (640px)
- Max width: max-w-lg (wizard), max-w-3xl (resultado)
- Texto: text-2xl sm:text-3xl
- **SEMPRE usar inline styles** para padding, margin, gap, fontSize (Tailwind spacing nao confiavel no Next.js 16 + Turbopack)

### Layout Mobile do Wizard (100dvh sem scroll na pagina)
O wizard usa `height: 100dvh` + `overflow: hidden` no container principal. A tela e dividida em:

1. **Header** (logo + subtitulo) — `flexShrink: 0`
2. **Progress ring** — `flexShrink: 0`
3. **Titulo da pergunta** (icone + texto + contexto) — `flexShrink: 0`
4. **Area de opcoes** — `flex-1` + `overflow: auto` + `minHeight: 0` + `.hide-scrollbar`
5. **Navegacao** (dots + setas + contador) — `flexShrink: 0`

A chave e `minHeight: 0` na area scrollavel — sem isso, flex-1 nao respeita overflow.

### Spacing compacto no mobile
```
Container: padding 10px 16px 6px
Ring: marginTop 6, marginBottom 6
Titulo area: paddingTop 4
Opcoes area: paddingTop 10, paddingBottom 6
Nav: gap 6, marginTop 4
Footer: paddingBottom 2
```

### ProfessionalForm compacto
```
Container: padding 16px 16px 12px
Header marginBottom: 14
Brand marginBottom: 14
Headline fontSize: clamp(26px, 5.5vw, 44px), marginBottom 8
Ornament marginBottom: 12
Card padding: 20px 20px
Field marginBottom: 14
Label marginBottom: 8
Tipo Atuacao buttons: padding 12px 10px
Divider margin: 14px 0
CTA padding: 16px 28px
Footer marginTop: 16
```
