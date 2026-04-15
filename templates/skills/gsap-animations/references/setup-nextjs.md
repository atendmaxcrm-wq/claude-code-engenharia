# Setup GSAP + AnimeJS no Next.js 16

## Instalacao

```bash
# GSAP + React hook
npm install gsap @gsap/react

# AnimeJS
npm install animejs
```

**Nota:** Desde GSAP 3.13+, TODOS os plugins estao incluidos no pacote `gsap`.
Nao precisa instalar separadamente. Basta importar.

## Registro de Plugins (OBRIGATORIO - uma vez)

Criar arquivo `lib/gsap-config.ts` (ou .js):

```tsx
"use client";

import { gsap } from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ScrollSmoother } from "gsap/ScrollSmoother";
import { SplitText } from "gsap/SplitText";
import { Flip } from "gsap/Flip";
import { Observer } from "gsap/Observer";
import { Draggable } from "gsap/Draggable";
import { MotionPathPlugin } from "gsap/MotionPathPlugin";
import { TextPlugin } from "gsap/TextPlugin";
import { MorphSVGPlugin } from "gsap/MorphSVGPlugin";
import { DrawSVGPlugin } from "gsap/DrawSVGPlugin";
import { ScrambleTextPlugin } from "gsap/ScrambleTextPlugin";
import { InertiaPlugin } from "gsap/InertiaPlugin";

// Registrar TODOS os plugins que o projeto pode usar
gsap.registerPlugin(
  ScrollTrigger,
  ScrollSmoother,
  SplitText,
  Flip,
  Observer,
  Draggable,
  MotionPathPlugin,
  TextPlugin,
  MorphSVGPlugin,
  DrawSVGPlugin,
  ScrambleTextPlugin,
  InertiaPlugin,
  useGSAP
);

export {
  gsap,
  useGSAP,
  ScrollTrigger,
  ScrollSmoother,
  SplitText,
  Flip,
  Observer,
  Draggable,
  MotionPathPlugin,
  TextPlugin,
  MorphSVGPlugin,
  DrawSVGPlugin,
  ScrambleTextPlugin,
  InertiaPlugin,
};
```

**IMPORTANTE:** Registrar SOMENTE os que vai usar no projeto. Exemplo minimo:

```tsx
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
gsap.registerPlugin(ScrollTrigger, SplitText);
```

## Import no Layout (Next.js App Router)

```tsx
// app/layout.tsx
import "./globals.css";
// Importar config para registrar plugins globalmente
import "@/lib/gsap-config";

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
```

## Uso em Componentes (useGSAP)

```tsx
"use client";

import { useRef } from "react";
import { gsap, useGSAP, ScrollTrigger } from "@/lib/gsap-config";

export function HeroSection() {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    // Tudo dentro deste callback tem cleanup automatico
    gsap.from(".hero-title", {
      y: 100,
      opacity: 0,
      duration: 1,
      ease: "power3.out",
    });

    gsap.from(".hero-subtitle", {
      y: 50,
      opacity: 0,
      duration: 0.8,
      delay: 0.3,
      ease: "power2.out",
    });
  }, { scope: containerRef }); // scope limita queries ao container

  return (
    <div ref={containerRef}>
      <h1 className="hero-title">Titulo</h1>
      <p className="hero-subtitle">Subtitulo</p>
    </div>
  );
}
```

## SSR Safety

GSAP manipula DOM. Em Next.js (SSR), usar:

1. **`"use client"`** em todo componente com GSAP
2. **`useGSAP`** (nao useEffect) — ja cuida do timing certo
3. **ScrollTrigger.refresh()** apos conteudo dinamico carregar
4. **matchMedia** para responsividade:

```tsx
useGSAP(() => {
  ScrollTrigger.matchMedia({
    // Desktop
    "(min-width: 768px)": function() {
      gsap.to(".box", { x: 200, scrollTrigger: { ... } });
    },
    // Mobile — animacoes mais simples
    "(max-width: 767px)": function() {
      gsap.to(".box", { opacity: 1 });
    },
  });
});
```

## AnimeJS no Next.js

```tsx
"use client";

import { useRef, useEffect } from "react";
import anime from "animejs";

export function AnimatedList() {
  const listRef = useRef<HTMLUListElement>(null);

  useEffect(() => {
    if (!listRef.current) return;

    anime({
      targets: listRef.current.children,
      translateY: [20, 0],
      opacity: [0, 1],
      delay: anime.stagger(80),
      easing: "easeOutCubic",
      duration: 600,
    });
  }, []);

  return (
    <ul ref={listRef}>
      <li>Item 1</li>
      <li>Item 2</li>
      <li>Item 3</li>
    </ul>
  );
}
```

### AnimeJS Layout API

```tsx
"use client";

import { useRef, useEffect } from "react";
import { createLayout } from "animejs";

export function FlipList({ items }) {
  const containerRef = useRef(null);
  const layoutRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;
    layoutRef.current = createLayout(containerRef.current);
  }, []);

  // Quando items mudam, layout anima automaticamente
  useEffect(() => {
    if (layoutRef.current) {
      layoutRef.current.update();
    }
  }, [items]);

  return (
    <div ref={containerRef}>
      {items.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </div>
  );
}
```

### AnimeJS WAAPI (Hardware-Accelerated, 3KB)

```tsx
import { waapi } from "animejs";

// Off-thread animation — roda mesmo com CPU ocupada
waapi.animate(".element", {
  transform: ["translateY(20px)", "translateY(0)"],
  opacity: [0, 1],
}, {
  duration: 500,
  easing: "ease-out",
});
```

**Quando usar WAAPI:** Animacoes simples de transform/opacity que precisam rodar smooth
mesmo durante load pesado. Bundle: apenas 3KB gzip.

## Cleanup Patterns

### GSAP (automatico com useGSAP)
```tsx
useGSAP(() => {
  // Tudo criado aqui e limpo automaticamente
  const tl = gsap.timeline();
  tl.to(".box", { x: 100 });
  // NAO precisa de return cleanup!
}, { scope: containerRef });
```

### SplitText (precisa revert manual)
```tsx
useGSAP(() => {
  const split = new SplitText(".text", { type: "chars,words" });
  gsap.from(split.chars, { opacity: 0, stagger: 0.02 });

  return () => {
    split.revert(); // OBRIGATORIO: restaura DOM original
  };
}, { scope: containerRef });
```

### AnimeJS (manual)
```tsx
useEffect(() => {
  const anim = anime({ targets: ".box", translateX: 250 });
  return () => {
    anim.pause(); // Parar animacao
    // Se usou Layout: layoutRef.current?.destroy();
  };
}, []);
```
