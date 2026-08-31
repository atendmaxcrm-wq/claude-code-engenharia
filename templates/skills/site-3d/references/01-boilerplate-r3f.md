# Boilerplate R3F - copy-paste canonico

> Os 4 arquivos-base estao em `00-briefing-tecnico.md` secao 2. Aqui ficam as DUAS
> variantes de scroll prontas + os snippets certo/errado de useFrame. Tudo ja com gate
> de performance, dpr clamp, frameloop e poster-LCP embutidos POR PADRAO.

## Setup inicial (uma vez)

```bash
# stack base
npm i three @react-three/fiber @react-three/drei @react-three/postprocessing
# scroll (escolher pela rota - pode instalar os dois)
npm i lenis gsap
# gate de performance + lazy-mount
npm i detect-gpu react-intersection-observer
# dev (asset pipeline)
npm i -D @react-three/gltfjsx @gltf-transform/cli leva
```

## Gate de performance UNICO (sempre antes de montar Canvas)

```tsx
// components/three/useQualityGate.ts
"use client";
import { useEffect, useState } from "react";
import { getGPUTier } from "detect-gpu";

export type Quality = "high" | "low" | "fallback";

export function useQualityGate(): Quality | null {
  const [q, setQ] = useState<Quality | null>(null); // null = ainda decidindo
  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) { setQ("fallback"); return; }      // reduced-motion -> poster (sem auto-rotacao/drift)
    getGPUTier().then((gpu) => {
      if (gpu.tier === 0) { setQ("fallback"); return; }   // GPU incapaz -> poster
      if (gpu.isMobile || gpu.tier === 1) { setQ("low"); return; } // mobile/fraco -> cena reduzida
      setQ("high");
    });
  }, []);
  return q;
}
```

No SceneGate: `fallback` -> nao monta Canvas (so o poster ja visivel). `low` -> monta com
dpr cap 1.5, sem postpro, <=2 luzes. `high` -> experiencia completa.

## Variante A - ScrollControls (canvas protagonista)

```tsx
// components/three/SceneScroll.tsx
"use client";
import { Canvas, useFrame } from "@react-three/fiber";
import { ScrollControls, useScroll, Scroll, AdaptiveDpr, PerformanceMonitor } from "@react-three/drei";
import { useRef, useState } from "react";
import * as THREE from "three";

function Rig() {
  const ref = useRef<THREE.Group>(null!);
  const scroll = useScroll();
  useFrame(() => {
    // LER o offset DENTRO do frame; mutar via ref. NUNCA setState aqui.
    ref.current.rotation.y = scroll.offset * Math.PI * 2;
  });
  return (
    <group ref={ref}>
      <mesh><icosahedronGeometry args={[1, 0]} /><meshStandardMaterial color="#e7540f" /></mesh>
    </group>
  );
}

export default function SceneScroll() {
  const [dpr, setDpr] = useState(1.5);
  return (
    <Canvas dpr={[1, 2]} gl={{ antialias: false, alpha: false }} camera={{ position: [0, 0, 5], fov: 45 }}>
      <PerformanceMonitor onDecline={() => setDpr((d) => Math.max(1, d - 0.25))} />
      <AdaptiveDpr pixelated />
      <ambientLight intensity={0.6} />
      <directionalLight position={[5, 5, 5]} intensity={1.2} />
      <ScrollControls pages={3} damping={0.25}>
        <Rig />
        <Scroll html>
          {/* HTML overlay sincronizado com o scroll 3D. Conteudo real do site aqui. */}
          <h1 style={{ position: "absolute", top: "20vh", left: "8vw" }}>Titulo</h1>
        </Scroll>
      </ScrollControls>
    </Canvas>
  );
}
// NUNCA combinar com GSAP ScrollTrigger pin no mesmo eixo.
```

## Variante B - Lenis + GSAP ScrollTrigger (DOM-first, 3D pontual)

```tsx
// app/providers.tsx - smooth scroll global
"use client";
import { ReactLenis } from "lenis/react";   // NAO @studio-freight/lenis
export default function Providers({ children }: { children: React.ReactNode }) {
  return <ReactLenis root options={{ autoRaf: false }}>{children}</ReactLenis>;
}
```

```tsx
// components/three/useScrollBridge.ts - casa Lenis com ScrollTrigger (sem scrollerProxy)
"use client";
import { useEffect } from "react";
import { useLenis } from "lenis/react";
import gsap from "gsap";
import ScrollTrigger from "gsap/ScrollTrigger";

export function useScrollBridge() {
  const lenis = useLenis();
  useEffect(() => {
    if (!lenis) return;
    gsap.registerPlugin(ScrollTrigger);
    lenis.on("scroll", ScrollTrigger.update);
    const tick = (t: number) => lenis.raf(t * 1000);
    gsap.ticker.add(tick);
    gsap.ticker.lagSmoothing(0);
    ScrollTrigger.refresh();
    return () => { gsap.ticker.remove(tick); };
  }, [lenis]);
}
```

O 3D le o progresso via `ScrollTrigger` -> grava num ref/objeto, e o `useFrame` consome
esse ref (nunca setState por frame). Pin/horizontal/parallax ficam no DOM via ScrollTrigger.

## useFrame: certo vs errado (a regra que mais salva fps)

```tsx
// ERRADO - re-render da arvore inteira a 60fps + GC
function Bad() {
  const [r, setR] = useState(0);
  useFrame(() => setR((v) => v + 0.01));                 // setState por frame = jank
  useFrame(() => { const v = new THREE.Vector3(1,2,3); /* ... */ }); // new no loop = GC stutter
  return <mesh rotation-y={r} />;
}

// CERTO - mutar via ref, objetos criados UMA vez
const tmp = new THREE.Vector3(); // escopo de modulo, reusado
function Good() {
  const ref = useRef<THREE.Mesh>(null!);
  useFrame((_, delta) => { ref.current.rotation.y += delta; });
  return <mesh ref={ref} />;
}
```

Checklist de grep antes de entregar:
```bash
# zero ocorrencias dentro de useFrame/render:
grep -rnE "setState|set[A-Z][a-zA-Z]*\(|new (THREE\.)?(Vector3|Color|Matrix4|Quaternion)|\.clone\(" components/three/
```
