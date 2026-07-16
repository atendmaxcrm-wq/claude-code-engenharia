# Lib Signatures — Como identificar cada lib de efeito visual

Tabela de referencia para identificar rapidamente qual lib um site esta usando para efeitos.

## UnicornStudio

**Signature DOM**: `<div data-us-project="ID">`
**Signature network**: `cdn.jsdelivr.net/gh/hiunicornstudio/unicornstudio.js`
**Signature global**: `window.UnicornStudio`
**Signature canvas**: Canvas WebGL fullscreen, geralmente parent com `-z-10` ou `pointer-events-none`

**Como capturar**: Pegar o valor de `data-us-project` e replicar com o mesmo ID (cena e publica no CDN).

**Replicar** (Next.js/React):

```tsx
'use client';
import { useEffect, useRef } from 'react';

export function UnicornScene({ projectId }: { projectId: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (document.querySelector('script[data-us-loader]')) return;
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/gh/hiunicornstudio/unicornstudio.js@v1.4.34/dist/unicornStudio.umd.js';
    script.async = true;
    script.setAttribute('data-us-loader', 'true');
    script.onload = () => {
      const w = window as any;
      if (w.UnicornStudio && !w.UnicornStudio.isInitialized) {
        w.UnicornStudio.init?.();
        w.UnicornStudio.isInitialized = true;
      }
    };
    document.body.appendChild(script);
  }, []);
  return <div ref={ref} data-us-project={projectId} className="absolute inset-0" />;
}
```

**Custo**: gratuito (free tier com limite mensal de visualizacoes). Tem mouse interaction, pulse, noise built-in.

---

## Spline

**Signature DOM**: `<spline-viewer url="...splinecode">` ou `<canvas>` dentro de `.spline-container`
**Signature network**: `prod.spline.design/XXX/scene.splinecode`
**Signature global**: `window.Spline` ou modulo `@splinetool/runtime`
**Signature canvas**: Canvas WebGL com objetos 3D (geometry, lighting)

**Como capturar**: Pegar a URL `.splinecode`.

**Replicar** (React):

```tsx
'use client';
import Spline from '@splinetool/react-spline';

<Spline scene="https://prod.spline.design/XXX/scene.splinecode" />
```

**Custo**: plano free tem watermark pequeno; plano pago remove. Exporta cenas 3D interativas.

---

## Rive

**Signature DOM**: `<canvas data-rive>` ou canvas dentro de `.rive-container`
**Signature network**: Arquivos `.riv` (ex: `/animation.riv`)
**Signature global**: `window.rive` ou `@rive-app/canvas`
**Signature canvas**: Canvas 2D OU WebGL (Rive tem ambos backends)

**Como capturar**: baixar o `.riv` e importar no projeto.

**Replicar**:

```tsx
'use client';
import { useRive } from '@rive-app/react-canvas';

export function Animation() {
  const { RiveComponent } = useRive({ src: '/animation.riv', autoplay: true });
  return <RiveComponent />;
}
```

**Custo**: gratuito pra animacoes, plano pago para features avancadas. Super leve (~30-80kb por arquivo `.riv`).

---

## three.js (custom shader ou cena)

**Signature DOM**: Canvas WebGL sem `data-*` específico
**Signature global**: `window.THREE`
**Signature network**: Sem CDN obrigatório (geralmente importado via bundler)
**Pistas adicionais**: Arquivos `.glb`/`.gltf`/`.hdr`/`.exr` na network

**Como capturar**:
- Se for modelo 3D: baixar `.glb` e importar
- Se for shader fullscreen (plasma, noise, warp): capturar GLSL via hook `shaderSource` (ver `shader-capture.md`)

**Replicar com React Three Fiber**:

```tsx
'use client';
import { Canvas } from '@react-three/fiber';
// ...
```

**Custo**: gratuito. Curva de aprendizado media.

---

## @react-three/fiber + drei

**Signature**: Mesmos sinais de three.js + scripts do react-three-fiber/drei no bundle.
**Caracteristica**: Cenas 3D declarativas em JSX.

---

## Lottie

**Signature DOM**: Canvas ou SVG dentro de `.lottie-container` ou `[data-lottie]`
**Signature network**: Arquivos `.json` com estrutura `{"v":"5.X","fr":60,"ip":0,...}` (formato Bodymovin)
**Signature global**: `window.lottie` ou `lottie-web`

**Como capturar**: baixar o JSON da animacao.

**Replicar**:

```tsx
import Lottie from 'lottie-react';
import animation from './animation.json';

<Lottie animationData={animation} loop />
```

**Custo**: gratuito. Export do After Effects.

---

## GSAP + ScrollTrigger

**Signature DOM**: Sem marcador especifico, mas elementos com `transform` mudando no scroll
**Signature global**: `window.gsap`, `window.ScrollTrigger`
**Signature network**: `cdn.jsdelivr.net/npm/gsap` ou bundle local

**Como capturar**: Olhar no console o que esta registrado:

```javascript
window.ScrollTrigger?.getAll()?.map(t => ({
  trigger: t.trigger?.tagName,
  animation: t.animation?.vars,
}))
```

Dá pra ver cada configuracao de trigger (start, end, scrub, pin, onUpdate). Reconstruir manualmente.

**Replicar**:

```tsx
'use client';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

useGSAP(() => {
  gsap.to('.box', { x: 100, scrollTrigger: { trigger: '.box', start: 'top center', scrub: true } });
});
```

**Custo**: gratuito pra uso comercial desde 2024. Plugins premium (SplitText, MorphSVG, etc) tambem liberados.

---

## Lenis (smooth scroll)

**Signature DOM**: `html` com `overscroll-behavior`, elemento `<div class="lenis">` wrappando tudo
**Signature global**: `window.Lenis`
**Signature comportamento**: Scroll suave, anti-nativo, com easing visivel

**Como capturar**: so ver se esta. Replicar e trivial.

**Replicar**:

```tsx
'use client';
import Lenis from 'lenis';
import { useEffect } from 'react';

useEffect(() => {
  const lenis = new Lenis();
  function raf(t) { lenis.raf(t); requestAnimationFrame(raf); }
  requestAnimationFrame(raf);
}, []);
```

**Custo**: gratuito. ~2kb gzip.

---

## Framer Motion

**Signature DOM**: Elementos com `data-framer-motion` em versoes antigas, ou atributos `style` com `transform3d` mudando
**Signature global**: Sem global explicito, detectar via bundle
**Signature comportamento**: Animacoes com easing suave, spring, layout transitions

**Como capturar**: usar nosso proprio motion pra recriar. Animacoes sao simples de replicar visualmente.

---

## Locomotive Scroll (legado, sendo substituido por Lenis)

**Signature DOM**: `data-scroll`, `data-scroll-container`, `[data-scroll-speed]`
**Signature global**: `window.LocomotiveScroll`

---

## Matter.js (fisica 2D)

**Signature global**: `window.Matter`
**Signature canvas**: Canvas 2D com bodies caindo, colidindo, com fisica

**Uso tipico**: Cartas espalhadas com fisica, textos que caem, confetti.

---

## Swiper / Embla / Keen Slider

**Signature DOM**:
- Swiper: `.swiper`, `.swiper-slide`, `.swiper-wrapper`
- Embla: `.embla`, `.embla__slide`
- Keen: `.keen-slider`

Trivial de identificar. Todos gratuitos.

---

## Detecao automatica (script completo)

Para colar no `browser_evaluate` e pegar tudo de uma vez:

```javascript
() => {
  var iframe = document.querySelector('iframe');
  var doc = iframe ? iframe.contentDocument : document;
  var win = iframe ? iframe.contentWindow : window;
  var t = [];
  if (win.gsap) t.push('GSAP ' + (win.gsap.version || ''));
  if (win.ScrollTrigger) t.push('ScrollTrigger');
  if (win.SplitText) t.push('SplitText');
  if (win.Lenis) t.push('Lenis');
  if (win.THREE) t.push('Three.js r' + (win.THREE.REVISION || ''));
  if (win.anime) t.push('AnimeJS');
  if (win.Matter) t.push('Matter.js');
  if (win.UnicornStudio) t.push('UnicornStudio');
  if (win.lottie) t.push('Lottie');
  if (win.rive) t.push('Rive');
  if (doc.querySelector('[data-us-project]')) t.push('UnicornStudio-embed');
  if (doc.querySelector('spline-viewer')) t.push('Spline-embed');
  if (doc.querySelector('[data-rive]')) t.push('Rive-embed');
  if (doc.querySelector('[data-framer-motion]')) t.push('Framer-Motion');
  if (doc.querySelector('[data-scroll-container]')) t.push('Locomotive');
  if (doc.querySelector('.swiper')) t.push('Swiper');
  if (doc.querySelector('.embla')) t.push('Embla');
  var resNames = performance.getEntriesByType('resource').map(function(r){return r.name;});
  var hits = resNames.filter(function(n){return /splinecode|\.riv$|unicornstudio|\.glb$|\.gltf$|lottie|rive/i.test(n);});
  var canvases = doc.querySelectorAll('canvas').length;
  var webglCount = 0;
  Array.prototype.forEach.call(doc.querySelectorAll('canvas'), function(c){ if (c.getContext('webgl2') || c.getContext('webgl')) webglCount++; });
  return { techs: t, assetHits: hits, canvases: canvases, webgl: webglCount };
}
```

## Arvore de decisao rapida

```
Tem canvas?
  SIM → WebGL?
    SIM →
      [data-us-project]? → UnicornStudio
      spline-viewer ou URL .splinecode? → Spline
      data-rive ou .riv? → Rive
      window.THREE? → three.js custom
      Nenhum dos acima? → shader custom (ogl / @webgpu)
    NAO →
      data-rive? → Rive backend 2D
      window.Matter? → Matter.js
      Sem lib conhecida? → canvas 2D manual (raf + particulas)

  NAO → Tem SVG animado?
    SIM → pode ser GSAP/Anime + SVG, ou Lottie transformado
    NAO → CSS puro (animation + gradient + filter + transform)
```
