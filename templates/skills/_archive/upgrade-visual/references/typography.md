# Tipografia Premium — Upgrade Visual

Sistema tipografico que separa "sistema generico" de "produto premium".

---

## 1. Font Pairings Recomendados

### Para SaaS/Tech (clean, moderno)

| Headings | Body | Custo | Vibe |
|----------|------|-------|------|
| **Inter (800)** | Inter (400) | Gratis | Neutro profissional |
| Geist Sans | Inter | Gratis | Vercel-style, tech |
| General Sans | Satoshi | Gratis | Startup moderno |

### Para Saude/Clinicas (confianca + elegancia)

| Headings | Body | Custo | Vibe |
|----------|------|-------|------|
| **Playfair Display** | Inter | Gratis | Elegancia classica |
| DM Serif Display | DM Sans | Gratis | Amigavel + profissional |
| Cormorant Variable | Montserrat | Gratis | Sofisticacao editorial |

### Para Portfolio/Criativo

| Headings | Body | Custo | Vibe |
|----------|------|-------|------|
| Editorial New | Space Grotesk | Acessivel | Web3, editorial |
| Playfair Display | Karla | Gratis | Narrativo |

### Padrao Recomendado (funciona para tudo)

**Inter** (body, labels, botoes) + **Playfair Display Variable** (keywords em italico nos headings)

---

## 2. Setup Next.js (next/font/google)

```tsx
// layout.tsx
import { Inter, Playfair_Display } from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-playfair",
  display: "swap",
  style: ["normal", "italic"],
});

export default function RootLayout({ children }) {
  return (
    <html className={`${inter.variable} ${playfair.variable}`}>
      <body className={inter.className}>{children}</body>
    </html>
  );
}
```

---

## 3. Scale Tipografico (Major Third — ratio 1.25)

```css
:root {
  --text-xs: 0.75rem;    /* 12px — captions, fine print */
  --text-sm: 0.875rem;   /* 14px — body small, labels */
  --text-base: 1rem;     /* 16px — body default */
  --text-lg: 1.125rem;   /* 18px — body large */
  --text-xl: 1.25rem;    /* 20px — heading small */
  --text-2xl: 1.5rem;    /* 24px — heading medium */
  --text-3xl: 1.875rem;  /* 30px — heading large */
  --text-4xl: 2.25rem;   /* 36px — display small */
  --text-5xl: 3rem;      /* 48px — display large */
  --text-6xl: 3.75rem;   /* 60px — hero */
}
```

---

## 4. Estilos por Nivel

### Hero / Display (H1 principal)

```css
.heading-hero {
  font-family: var(--font-inter);
  font-size: clamp(28px, 6vw, 48px);
  font-weight: 300;            /* LIGHT — nao bold */
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

/* Keyword em serif italico para contraste */
.heading-hero .keyword {
  font-family: var(--font-playfair);
  font-style: italic;
  font-weight: 400;
  font-size: 1.15em;          /* Levemente maior */
  color: var(--accent-light);
}
```

**Exemplo de uso:**
```tsx
<h1 className="heading-hero">
  Transforme sua <span className="keyword">clinica</span> com dados
</h1>
```

### Section Label (uppercase com linha)

```css
.section-label-text {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: var(--text-muted);
}
```

### Subtitle / Description

```css
.subtitle {
  font-size: 13px;
  font-weight: 300;
  letter-spacing: 0.08em;
  opacity: 0.45;
  color: var(--text-secondary);
}
```

### Body Text (conteudo longo)

```css
.body-text {
  font-size: 0.875rem;        /* 14px */
  font-weight: 400;
  line-height: 1.75;          /* Generoso */
  color: var(--text-muted);
}
```

### Badge / Tag Text

```css
.badge-text {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
```

### Numeros (tabular)

```css
.number {
  font-variant-numeric: tabular-nums;
  font-feature-settings: "tnum" on;
}
```

---

## 5. OpenType Features

```css
body {
  font-feature-settings:
    "cv01" on,  /* alternate a (Inter) */
    "cv02" on,  /* alternate g (Inter) */
    "tnum" on,  /* tabular numbers */
    "salt" on;  /* stylistic alternates */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

---

## 6. O Que Faz a Diferenca

### Generico vs Premium

| Aspecto | Generico | Premium |
|---------|----------|---------|
| Heading weight | 700 (bold) | 300 (light) ou 800 com tracking -0.03em |
| Heading font | Mesma do body | Display/serif para contraste |
| Labels | fontSize 14, normal | 11px, uppercase, letter-spacing 0.2em, weight 700 |
| Body line-height | 1.5 | 1.75 (mais generoso) |
| Numeros em tabelas | Proportional (desalinhados) | Tabular (alinhados) |
| Placeholder | Mesmo tom do texto | 50% opacity, peso 300 |
| Keyword highlight | Bold ou underline | Serif italic em cor accent |

### Principio: Contraste Tipografico

O segredo e criar **tensao visual** entre dois extremos:
- Sans-serif ultra-light (300) para headings grandes
- Serif italic para a palavra-chave focal
- Uppercase com spacing largo para labels/section titles
- Body com line-height generoso (1.75)

Isso cria hierarquia visual sem precisar de cores ou decoracoes extras.
