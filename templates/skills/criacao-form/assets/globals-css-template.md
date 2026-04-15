# Template: globals.css

Copie e customize as cores accent para cada projeto.

```css
@import "tailwindcss";

:root {
  --background: #09090b;
  --foreground: #fafafa;
  --card-bg: #18181b;
  --card-border: #27272a;
  --muted: #a1a1aa;
  --star-empty: #3f3f46;
  --star-filled: #f59e0b;
  --star-hover: #fbbf24;
  --urgent: #ef4444;
  --attention: #eab308;
  --good: #3b82f6;
  --excellent: #22c55e;
  /* CUSTOMIZAR POR MARCA */
  --accent: #E7540F;
  --accent-light: #FF7A3D;
}

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

* {
  box-sizing: border-box;
}

body {
  background: var(--background);
  color: var(--foreground);
  font-family: var(--font-sans), system-ui, sans-serif;
  overflow-x: hidden;
}

/* Gradient mesh background */
.gradient-mesh {
  background:
    radial-gradient(ellipse 80% 50% at 20% 40%, rgba(231, 84, 15, 0.08), transparent),
    radial-gradient(ellipse 60% 40% at 80% 20%, rgba(59, 130, 246, 0.05), transparent),
    radial-gradient(ellipse 50% 50% at 50% 80%, rgba(139, 92, 246, 0.04), transparent);
}

/* Star glow when filled */
.star-glow {
  filter: drop-shadow(0 0 6px rgba(245, 158, 11, 0.5));
}

/* Smooth scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--background); }
::-webkit-scrollbar-thumb { background: var(--card-border); border-radius: 3px; }

/* Progress ring animation */
@keyframes progress-ring {
  from { stroke-dashoffset: 283; }
}

/* ============================
   Analysis content formatting
   ============================ */
.analysis-content {
  color: var(--muted);
  line-height: 1.75;
  font-size: 0.875rem;
}

.analysis-content h2 {
  color: var(--foreground);
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin-top: 2.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--card-border);
}

.analysis-content h2:first-child {
  margin-top: 0;
}

.analysis-content h3 {
  color: var(--foreground);
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

.analysis-content p {
  margin-top: 0.5rem;
  margin-bottom: 0.75rem;
}

.analysis-content strong {
  color: var(--foreground);
  font-weight: 600;
}

.analysis-content em {
  color: var(--foreground);
  opacity: 0.85;
  font-style: italic;
}

.analysis-content ul {
  margin-top: 0.5rem;
  margin-bottom: 1rem;
  padding-left: 0;
  list-style: none;
}

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

/* Nested lists */
.analysis-content ul ul {
  margin-top: 0.375rem;
  margin-bottom: 0.375rem;
}

.analysis-content ul ul li::before {
  width: 4px;
  height: 4px;
  background: var(--muted);
  opacity: 0.4;
}
```
