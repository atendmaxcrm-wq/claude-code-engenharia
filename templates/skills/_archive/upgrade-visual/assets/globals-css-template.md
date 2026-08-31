# globals.css Template — Upgrade Visual Premium

Template completo para copiar e adaptar. Trocar `--accent` e `--accent-light` pela cor da marca.

---

```css
@import "tailwindcss";

/* ========================================
   DESIGN TOKENS
   ======================================== */

:root {
  /* Backgrounds — escala de elevacao */
  --background: #09090b;
  --surface: #121212;
  --surface-elevated: #1a1a1a;
  --surface-hover: #262626;

  /* Borders */
  --border: rgba(255, 255, 255, 0.06);
  --border-visible: rgba(255, 255, 255, 0.10);
  --border-focus: rgba(255, 255, 255, 0.20);

  /* Texto */
  --text-primary: #fafafa;
  --text-secondary: #d4d4d8;
  --text-muted: #a1a1aa;
  --text-faint: #71717a;

  /* Accent — TROCAR POR COR DA MARCA */
  --accent: #E7540F;
  --accent-light: #FF7A3D;
  --accent-soft: rgba(231, 84, 15, 0.12);
  --accent-glow: rgba(231, 84, 15, 0.08);

  /* Semanticas */
  --success: #22c55e;
  --warning: #eab308;
  --error: #ef4444;
  --info: #3b82f6;

  /* Stars */
  --star-empty: #3f3f46;
  --star-filled: #f59e0b;
  --star-hover: #fbbf24;
}

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

/* ========================================
   BASE
   ======================================== */

body {
  background: var(--background);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-feature-settings: "cv01" on, "cv02" on, "tnum" on, "salt" on;
}

::selection {
  background-color: var(--accent);
  color: white;
}

/* ========================================
   SCROLLBAR
   ======================================== */

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--background); }
::-webkit-scrollbar-thumb { background: var(--border-visible); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-faint); }

.hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
.hide-scrollbar::-webkit-scrollbar { display: none; }

/* ========================================
   CARDS
   ======================================== */

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

/* ========================================
   BACKGROUNDS DECORATIVOS
   ======================================== */

.gradient-mesh {
  background:
    radial-gradient(ellipse 80% 50% at 20% 40%, var(--accent-glow), transparent),
    radial-gradient(ellipse 60% 40% at 80% 20%, rgba(59, 130, 246, 0.05), transparent),
    radial-gradient(ellipse 50% 50% at 50% 80%, rgba(139, 92, 246, 0.04), transparent);
}

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

.deco-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(40px);
  pointer-events: none;
  z-index: 0;
}

/* ========================================
   INPUTS
   ======================================== */

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

/* ========================================
   BOTOES
   ======================================== */

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

.btn-secondary {
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-primary);
  font-weight: 500;
  border: 1px solid var(--border-visible);
  border-radius: 12px;
  padding: 12px 24px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.4, 0.25, 1);
}

.btn-secondary:hover {
  border-color: var(--accent);
  color: var(--accent-light);
  background: var(--accent-glow);
}

/* ========================================
   OPTIONS / CHIPS
   ======================================== */

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

.option-card:active { transform: scale(0.985); }
.option-card.selected { border-color: var(--accent); background: var(--accent-soft); }

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

.chip:hover { border-color: var(--accent); color: var(--accent-light); background: var(--accent-glow); }
.chip.active { border-color: var(--accent); color: var(--accent-light); background: var(--accent-soft); font-weight: 600; }

/* ========================================
   LABELS / BADGES
   ======================================== */

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

.badge-accent { background: var(--accent-soft); color: var(--accent-light); border: 1px solid rgba(231,84,15,0.2); }
.badge-success { background: rgba(34,197,94,0.1); color: #4ade80; border: 1px solid rgba(34,197,94,0.2); }
.badge-warning { background: rgba(234,179,8,0.1); color: #fbbf24; border: 1px solid rgba(234,179,8,0.2); }
.badge-error { background: rgba(239,68,68,0.1); color: #f87171; border: 1px solid rgba(239,68,68,0.2); }

/* ========================================
   PROGRESS
   ======================================== */

.rating-bar-track {
  height: 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.rating-bar-fill {
  height: 100%;
  border-radius: 4px;
}

/* ========================================
   ANALYSIS CONTENT (HTML gerado por IA)
   ======================================== */

.analysis-content {
  color: var(--text-muted);
  line-height: 1.75;
  font-size: 0.875rem;
}

.analysis-content h2 {
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin-top: 2.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-visible);
}

.analysis-content h3 {
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 600;
  margin-top: 2rem;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.analysis-content h3::before {
  content: "";
  display: inline-block;
  width: 3px;
  height: 1em;
  border-radius: 2px;
  background: var(--accent);
  flex-shrink: 0;
}

.analysis-content ul { list-style: none; padding-left: 0; }

.analysis-content ul li {
  position: relative;
  padding-left: 1.25rem;
  margin-bottom: 0.5rem;
}

.analysis-content ul li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0.6em;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  opacity: 0.6;
}

.analysis-content ul ul li::before {
  width: 4px;
  height: 4px;
  background: var(--text-muted);
  opacity: 0.4;
}

.analysis-content strong {
  color: var(--text-primary);
  font-weight: 600;
}

/* ========================================
   KEYFRAMES
   ======================================== */

@keyframes fade-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@keyframes pulse-glow {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.05); }
}

@keyframes mesh-drift {
  0%, 100% { background-position: 20% 40%, 80% 20%, 50% 80%; }
  33% { background-position: 50% 60%, 50% 50%, 20% 30%; }
  66% { background-position: 80% 20%, 20% 70%, 80% 60%; }
}

@keyframes border-shimmer {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes reveal-in {
  from { clip-path: inset(100% 0 0 0); }
  to { clip-path: inset(0 0 0 0); }
}

@keyframes spin { to { transform: rotate(360deg); } }
```
