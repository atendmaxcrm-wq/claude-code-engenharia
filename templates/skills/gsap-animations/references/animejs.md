# AnimeJS — Quando e Como Usar

## Visao Geral

AnimeJS v4 e uma lib leve (~10KB gzip) com 3 diferenciais unicos:

1. **Layout API** (v4.3+) — FLIP animations automaticas para DOM reorder
2. **WAAPI Mode** (3KB gzip) — Animacoes hardware-accelerated off-thread
3. **Sintaxe simples** — API minimalista para animacoes rapidas

## Quando Preferir AnimeJS sobre GSAP

| Cenario | Porque AnimeJS |
|---------|----------------|
| Reordenar lista/grid com animacao | Layout API faz FLIP automatico |
| Enter/Leave DOM elements | Layout API com display: flex/grid/none |
| Animacao off-thread (CPU ocupada) | WAAPI roda na compositor thread |
| Bundle ultra-leve (3KB) | WAAPI mode sem core pesado |
| Filtro de portfolio (show/hide items) | Layout API + enter/leave |

## Quando Preferir GSAP

| Cenario | Porque GSAP |
|---------|------------|
| Scroll pin/scrub | ScrollTrigger (AnimeJS nao tem) |
| Split text | SplitText (AnimeJS nao tem) |
| SVG morph | MorphSVG (AnimeJS basico) |
| Timeline complexa (10+ tweens) | GSAP Timeline e mais robusto |
| 500+ elementos | GSAP otimizado para volume |

## Layout API (Exclusivo AnimeJS v4.3+)

### Conceito
O Layout API monitora um container e anima automaticamente quando:
- Elementos sao reordenados
- Elementos sao adicionados/removidos
- Display muda (flex, grid, none)

### Uso Basico
```tsx
import { createLayout } from "animejs";

// Criar layout observer
const layout = createLayout(".container", {
  duration: 400,
  ease: "outQuad",
});

// Qualquer mudanca no DOM do container e animada automaticamente
// Exemplo: reordenar filhos
container.prepend(container.lastChild); // AnimeJS anima a transicao
layout.update(); // Trigger animation

// Cleanup
layout.destroy();
```

### Enter/Leave
```tsx
const layout = createLayout(".list", {
  enter: { opacity: [0, 1], scale: [0.8, 1] },
  leave: { opacity: [1, 0], scale: [1, 0.8] },
  duration: 300,
});

// Adicionar item — entra com animacao
list.appendChild(newItem);
layout.update();

// Remover item — sai com animacao
item.remove();
layout.update();
```

### Portfolio Filter
```tsx
const layout = createLayout(".portfolio-grid", {
  duration: 500,
  ease: "outExpo",
  enter: { opacity: [0, 1] },
  leave: { opacity: [1, 0] },
});

function filterByCategory(category) {
  const items = document.querySelectorAll(".portfolio-item");
  items.forEach(item => {
    item.style.display = item.dataset.category === category ? "block" : "none";
  });
  layout.update();
}
```

## WAAPI Mode (3KB)

### Conceito
Web Animation API roda animacoes na compositor thread do browser.
Significa: animacoes smooth mesmo com JavaScript pesado rodando.

### Limitacoes
- So funciona com propriedades compositable: `transform`, `opacity`
- Custom easings (power, spring) desabilitam hardware acceleration
- Safari tem bugs com `linear()` easing

### Uso
```tsx
import { waapi } from "animejs";

// Hardware-accelerated (off-thread)
waapi.animate(".card", {
  transform: ["translateY(20px)", "translateY(0)"],
  opacity: [0, 1],
}, {
  duration: 500,
  easing: "ease-out", // Nativo = hardware accelerated
});

// Com stagger
waapi.animate(".item", {
  transform: ["scale(0.9)", "scale(1)"],
  opacity: [0, 1],
}, {
  duration: 400,
  delay: waapi.stagger(50),
});
```

### Quando usar WAAPI vs animate()
| Criterio | waapi.animate() | animate() |
|----------|----------------|-----------|
| Bundle | 3KB | 10KB |
| Thread | Off-thread (compositor) | Main thread |
| Properties | Somente CSS compositable | Qualquer (JS, SVG, DOM) |
| Easings | Nativos do browser | Custom (spring, power) |
| Targets max | Sem limite pratico | 500+ pode ter jank |
| Timeline | Nao | Sim (createTimeline) |

## Animacao Basica (animate)

```tsx
import anime from "animejs";

// Basico
anime({
  targets: ".box",
  translateX: 250,
  rotate: "1turn",
  duration: 800,
  easing: "easeInOutQuad",
});

// Com stagger
anime({
  targets: ".grid-item",
  scale: [0, 1],
  opacity: [0, 1],
  delay: anime.stagger(100, { grid: [5, 4], from: "center" }),
  easing: "easeOutElastic(1, .5)",
});

// Timeline
const tl = anime.timeline({
  easing: "easeOutExpo",
  duration: 750,
});

tl.add({ targets: ".title", translateY: [-50, 0], opacity: [0, 1] })
  .add({ targets: ".subtitle", translateY: [-30, 0], opacity: [0, 1] }, "-=500")
  .add({ targets: ".cta", scale: [0.8, 1], opacity: [0, 1] }, "-=400");
```

## Draggable (AnimeJS v4)

```tsx
import { Draggable } from "animejs";

const draggable = new Draggable(".card", {
  container: ".board",
  snap: { x: 100, y: 100 }, // Snap to grid
  onDrag: (e) => { /* feedback visual */ },
  onRelease: (e) => { /* animar para posicao final */ },
});
```

## Integracao com React

AnimeJS NAO tem hook oficial para React. Usar useEffect + useRef:

```tsx
"use client";
import { useRef, useEffect } from "react";
import anime from "animejs";

export function AnimatedComponent() {
  const ref = useRef(null);

  useEffect(() => {
    if (!ref.current) return;

    const anim = anime({
      targets: ref.current.querySelectorAll(".item"),
      translateY: [20, 0],
      opacity: [0, 1],
      delay: anime.stagger(80),
      easing: "easeOutCubic",
      duration: 600,
    });

    return () => {
      anim.pause();
    };
  }, []);

  return (
    <div ref={ref}>
      <div className="item">A</div>
      <div className="item">B</div>
      <div className="item">C</div>
    </div>
  );
}
```
