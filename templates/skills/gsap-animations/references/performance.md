# Performance — Regras de Animacao

## Propriedades GPU-Accelerated (USAR)

Estas rodam na compositor thread, sem layout recalculation:
- `transform` (translate, scale, rotate, skew)
- `opacity`
- `filter` (com moderacao, max 30px blur animado)

GSAP ativa automaticamente `translate3d()` (force3D: true) para GPU acceleration.

## Propriedades que TRIGAM Layout (EVITAR)

Nunca animar estas — causam layout recalculation em TODOS os elementos:
- `width`, `height`
- `margin`, `padding`
- `top`, `left`, `right`, `bottom` (non-absolute)
- `border`
- `font-size`

## Propriedades que TRIGAM Paint (CUIDADO)

Causam repaint mas nao relayout:
- `color`, `background-color`
- `box-shadow`, `text-shadow`
- `filter` (blur, brightness)
- `border-radius` (quando anima)

## Regras de Performance GSAP

### 1. Cache DOM References
```tsx
// BOM — cache uma vez
const boxes = gsap.utils.toArray(".box");
gsap.to(boxes, { y: 100 });

// RUIM — query a cada frame
gsap.to(".box", { y: 100 }); // ok para tweens simples
// Mas em onUpdate/callbacks, SEMPRE usar cache
```

### 2. ScrollTrigger
```tsx
// BOM
ScrollTrigger.create({
  trigger: ".section",
  start: "top center",
  end: "+=100%",        // NAO 200% (scroll longo = fadiga)
  scrub: 0.5,           // NAO 1 (1s delay = parece lento)
  anticipatePin: 1,     // SEMPRE (previne pulo visual)
});

// RUIM
ScrollTrigger.create({
  scrub: true,           // true = sem smoothing, janky
  end: "+=300%",         // Scroll infinito = fadiga
  // sem anticipatePin   // Pin pula no Safari
});
```

### 3. Stagger
```tsx
// BOM — stagger sutil
gsap.from(".item", {
  opacity: 0,
  y: 20,
  stagger: 0.08,  // 80ms entre items (rapido, organico)
});

// RUIM — stagger lento
gsap.from(".item", {
  opacity: 0,
  y: 100,          // Muito deslocamento
  stagger: 0.3,    // 300ms = parece quebrado
});
```

### 4. Kill & Cleanup
```tsx
// Matar animacao quando nao precisa mais
animation.kill();

// Para animacoes que vai reusar, PAUSE (nao kill)
animation.pause();

// ScrollTrigger: kill com cleanup
ScrollTrigger.getAll().forEach(st => st.kill());
```

### 5. Mobile Optimization
```tsx
// SEMPRE: matchMedia para mobile
ScrollTrigger.matchMedia({
  "(min-width: 768px)": function() {
    // Animacoes completas desktop
    gsap.timeline({
      scrollTrigger: { pin: true, scrub: 0.5 }
    })
    .to(".hero", { scale: 1.2 })
    .to(".text", { y: -50 });
  },
  "(max-width: 767px)": function() {
    // Mobile: sem pin, sem scrub, so reveal basico
    gsap.from(".hero", { opacity: 0, y: 20 });
  },
});
```

### 6. Quantidade de Elementos
- **< 50 elementos**: Qualquer animacao funciona
- **50-200 elementos**: Preferir transform + opacity only
- **200-500 elementos**: Usar GSAP (melhor que AnimeJS para volume)
- **500+ elementos**: Considerar Canvas/WebGL, nao DOM animations

### 7. Timelines
```tsx
// BOM — timeline reutilizavel
const tl = gsap.timeline({ paused: true });
tl.to(".a", { x: 100 })
  .to(".b", { y: 50 }, "-=0.3")  // Overlap: mais fluido
  .to(".c", { opacity: 1 }, "<"); // Mesmo tempo que anterior

// Disparar quando quiser
tl.play();

// RUIM — tweens soltos com delays manuais
gsap.to(".a", { x: 100, delay: 0 });
gsap.to(".b", { y: 50, delay: 0.7 });   // Fragil, dificil de manter
gsap.to(".c", { opacity: 1, delay: 0.7 });
```

## Regras de Performance AnimeJS

### WAAPI (Hardware-Accelerated)
```tsx
// WAAPI roda off-thread — melhor para CPU load
// Mas SO funciona com transform e opacity
// Custom easings DESABILITAM hardware acceleration
waapi.animate(".el", {
  transform: ["translateX(0)", "translateX(100px)"],
  opacity: [0, 1],
}, {
  duration: 500,
  easing: "ease-out", // Easing nativo = hardware accelerated
  // easing: "out(3)" // RUIM: custom easing = main thread
});
```

### Layout API
```tsx
// Layout API faz FLIP automatico
// Custo: mede getBoundingClientRect antes e depois
// Para listas < 50 items: excelente
// Para grids > 100 items: pode ter jank no measure
```

## Checklist Pre-Deploy

```
[ ] Todas animacoes usam transform/opacity (nao width/height)
[ ] ScrollTrigger tem scrub: 0.5 (nao 1 ou true)
[ ] ScrollTrigger tem anticipatePin: 1
[ ] Mobile tem animacoes simplificadas (matchMedia)
[ ] SplitText tem revert() no cleanup
[ ] Nenhum animate com repeat: Infinity via JS (usar CSS keyframes)
[ ] useGSAP usado em vez de useEffect para GSAP
[ ] Stagger < 0.15s entre items
[ ] Nenhuma animacao em propriedade de layout
[ ] kill() chamado no unmount para animacoes manuais
```
