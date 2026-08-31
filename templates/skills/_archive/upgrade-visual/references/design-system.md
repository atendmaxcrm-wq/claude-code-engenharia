# Design System — Upgrade Visual Premium

Sistema completo de tokens, variaveis e classes CSS para transformar interfaces genericas em produtos premium.

---

## 1. Paleta de Cores (CSS Variables)

### Base Dark Mode (obrigatorio)

```css
:root {
  /* Backgrounds — escala de elevacao por luminosidade */
  --background: #09090b;          /* Fundo principal (off-black, NUNCA #000) */
  --surface: #121212;             /* Cards nivel 1 */
  --surface-elevated: #1a1a1a;    /* Cards nivel 2, hover states */
  --surface-hover: #262626;       /* Active states, menus abertos */

  /* Borders — quase invisiveis */
  --border: rgba(255, 255, 255, 0.06);          /* Padrao (sutil) */
  --border-visible: rgba(255, 255, 255, 0.10);  /* Quando precisa ser visto */
  --border-focus: rgba(255, 255, 255, 0.20);    /* Focus states */

  /* Texto — 3 niveis */
  --text-primary: #fafafa;     /* Texto principal */
  --text-secondary: #d4d4d8;   /* Texto auxiliar (zinc-300) */
  --text-muted: #a1a1aa;       /* Labels, placeholders (zinc-400) */
  --text-faint: #71717a;       /* Texto muito sutil (zinc-500) */

  /* Accent — customizar por marca */
  --accent: #E7540F;              /* Cor principal */
  --accent-light: #FF7A3D;        /* Variante clara (gradientes) */
  --accent-soft: rgba(231, 84, 15, 0.12);  /* Background tint */
  --accent-glow: rgba(231, 84, 15, 0.08);  /* Glow sutil */

  /* Semanticas */
  --success: #22c55e;
  --warning: #eab308;
  --error: #ef4444;
  --info: #3b82f6;

  /* Star Rating */
  --star-empty: #3f3f46;
  --star-filled: #f59e0b;
  --star-hover: #fbbf24;
}
```

### Tailwind v4 @theme Mapping

```css
@theme inline {
  --color-background: var(--background);
  --color-surface: var(--surface);
  --color-surface-elevated: var(--surface-elevated);
  --color-border: var(--border);
  --color-text-primary: var(--text-primary);
  --color-text-secondary: var(--text-secondary);
  --color-text-muted: var(--text-muted);
  --color-accent: var(--accent);
  --color-accent-light: var(--accent-light);
}
```

### Como Customizar por Marca

Trocar apenas `--accent` e `--accent-light`. Todo o resto se adapta:

| Marca | --accent | --accent-light |
|-------|----------|----------------|
| Makewl (laranja) | #E7540F | #FF7A3D |
| Saude (teal) | #1A6B5A | #2D9B7C |
| Tech (azul) | #3B82F6 | #60A5FA |
| Luxo (dourado) | #C4A35A | #D4B96A |
| Energia (verde) | #22C55E | #4ADE80 |

---

## 2. Spacing (Ritmo de 8px)

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;
  --space-9: 96px;
}
```

**Regra:** Usar inline `style={{}}` para spacing critico (bug Tailwind v4 + Next.js 16 + Turbopack).

---

## 3. Classes CSS Utilitarias

### Cards (3 niveis)

```css
/* Nivel 1 — Card elevado basico */
.card-elevated {
  background: rgba(24, 24, 27, 0.6);
  border: 1px solid var(--border);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-radius: 16px;
  box-shadow:
    0 1px 3px rgba(0,0,0,0.2),
    0 4px 12px rgba(0,0,0,0.15);
}

/* Nivel 2 — Card glassmorphism */
.card-glass {
  background: rgba(24, 24, 27, 0.7);
  backdrop-filter: blur(16px) saturate(120%);
  -webkit-backdrop-filter: blur(16px) saturate(120%);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  box-shadow:
    0 2px 8px rgba(0,0,0,0.2),
    0 8px 32px rgba(0,0,0,0.15),
    inset 0 1px 0 rgba(255,255,255,0.03);
}

/* Nivel 3 — Card premium interativo */
.card-premium {
  background: rgba(24, 24, 27, 0.6);
  border: 1px solid var(--border);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-radius: 16px;
  box-shadow:
    0 1px 2px rgba(0,0,0,0.2),
    0 4px 16px rgba(0,0,0,0.15),
    0 16px 48px rgba(0,0,0,0.1);
  transition: all 0.4s cubic-bezier(0.25, 0.4, 0.25, 1);
}

.card-premium:hover {
  box-shadow:
    0 2px 4px rgba(0,0,0,0.25),
    0 8px 24px rgba(0,0,0,0.2),
    0 24px 64px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}
```

### Backgrounds Decorativos

```css
/* Gradient mesh — 3 radial-gradients com opacidade extremamente baixa */
.gradient-mesh {
  background:
    radial-gradient(ellipse 80% 50% at 20% 40%, var(--accent-glow), transparent),
    radial-gradient(ellipse 60% 40% at 80% 20%, rgba(59, 130, 246, 0.05), transparent),
    radial-gradient(ellipse 50% 50% at 50% 80%, rgba(139, 92, 246, 0.04), transparent);
}

/* Grid decorativo com fade radial */
.deco-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
  background-size: 60px 60px;
  opacity: 0.3;
  pointer-events: none;
  mask-image: radial-gradient(ellipse at center, black 0%, transparent 70%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 0%, transparent 70%);
}

/* Blob decorativo */
.deco-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(40px);
  pointer-events: none;
  z-index: 0;
}
```

### Inputs

```css
/* Input premium dark */
.input-premium {
  width: 100%;
  padding: 14px 18px;
  border-radius: 12px;
  border: 1px solid var(--border-visible);
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-primary);
  font-size: 15px;
  outline: none;
  transition: all 0.25s cubic-bezier(0.25, 0.4, 0.25, 1);
}

.input-premium::placeholder {
  color: var(--text-muted);
  opacity: 0.5;
}

.input-premium:focus {
  border-color: var(--accent);
  background: var(--accent-glow);
  box-shadow: 0 0 0 3px rgba(231, 84, 15, 0.1);
}
```

### Botoes

```css
/* CTA primario com gradiente + glow */
.btn-primary {
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%);
  color: white;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.35s cubic-bezier(0.25, 0.4, 0.25, 1);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow:
    0 4px 16px rgba(231, 84, 15, 0.3),
    0 8px 32px rgba(231, 84, 15, 0.15);
}

.btn-primary:active {
  transform: translateY(0) scale(0.98);
}

/* Sheen effect no hover */
.btn-primary::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(255,255,255,0.1) 50%, transparent 100%);
  opacity: 0;
  transition: opacity 0.35s ease;
}

.btn-primary:hover::before {
  opacity: 1;
}
```

### Option Cards (Seletores)

```css
.option-card {
  background: var(--surface);
  border: 1.5px solid var(--border-visible);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.4, 0.25, 1);
}

.option-card:hover {
  border-color: var(--accent);
  background: var(--accent-glow);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(231, 84, 15, 0.1);
}

.option-card:active {
  transform: scale(0.985);
}

.option-card.selected {
  border-color: var(--accent);
  background: var(--accent-soft);
}
```

### Chips / Pills

```css
.chip {
  padding: 10px 20px;
  border-radius: 9999px;
  font-size: 13px;
  font-weight: 500;
  border: 1.5px solid var(--border-visible);
  background: var(--surface);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.4, 0.25, 1);
}

.chip:hover {
  border-color: var(--accent);
  color: var(--accent-light);
  background: var(--accent-glow);
}

.chip.active {
  border-color: var(--accent);
  color: var(--accent-light);
  background: var(--accent-soft);
  font-weight: 600;
}
```

### Section Label

```css
.section-label {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.section-label span {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: var(--text-muted);
  font-weight: 700;
  white-space: nowrap;
}

.section-label::after {
  content: "";
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, var(--border-visible), transparent);
}
```

### Badges

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.badge-accent {
  background: var(--accent-soft);
  color: var(--accent-light);
  border: 1px solid rgba(231, 84, 15, 0.2);
}

.badge-success {
  background: rgba(34, 197, 94, 0.1);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.badge-warning {
  background: rgba(234, 179, 8, 0.1);
  color: #fbbf24;
  border: 1px solid rgba(234, 179, 8, 0.2);
}

.badge-error {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.2);
}
```

### Number Badge

```css
.number-badge {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 16px;
  color: white;
  position: relative;
  overflow: hidden;
}

/* Highlight superior (efeito 3D sutil) */
.number-badge::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 50%;
  background: linear-gradient(to bottom, rgba(255,255,255,0.2), transparent);
  border-radius: 14px 14px 0 0;
}
```

---

## 4. Keyframes

```css
/* Entrada padrao */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Shimmer para loading/skeleton */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Pulse sutil para blobs decorativos */
@keyframes pulse-glow {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.05); }
}

/* Mesh drift ultra-lento (45s) */
@keyframes mesh-drift {
  0%, 100% { background-position: 20% 40%, 80% 20%, 50% 80%; }
  33% { background-position: 50% 60%, 50% 50%, 20% 30%; }
  66% { background-position: 80% 20%, 20% 70%, 80% 60%; }
}

/* Border shimmer rotativo */
@keyframes border-shimmer {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Spin padrao */
@keyframes spin { to { transform: rotate(360deg); } }

/* Reveal via clip-path */
@keyframes reveal-in {
  from { clip-path: inset(100% 0 0 0); }
  to { clip-path: inset(0 0 0 0); }
}
```

---

## 5. Utilitarios Globais

```css
/* Scrollbar customizada */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--background); }
::-webkit-scrollbar-thumb { background: var(--border-visible); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-faint); }

/* Esconder scrollbar mantendo funcionalidade */
.hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
.hide-scrollbar::-webkit-scrollbar { display: none; }

/* Selection com accent */
::selection {
  background-color: var(--accent);
  color: white;
}

/* Font smoothing */
body {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```
