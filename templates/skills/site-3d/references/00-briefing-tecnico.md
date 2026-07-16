# Briefing Tecnico - Sites 3D Premium (R3F em Next.js 16)

> Fonte: pesquisa multi-agente (29 agentes, 24 claims tecnicos passados por verificacao
> adversarial, 14 corrigidos). Junho/2026. Este e o documento-base da skill /site-3d.
> Onde a pesquisa bruta errou, a correcao verificada ja esta aplicada aqui.

## 1. Stack definitivo (pins reais, junho/2026)

```jsonc
// package.json
{
  "dependencies": {
    "three": "^0.184.0",                      // engine WebGL base. SEMPRE code-split. (corrigido: NAO 0.16x, aquilo e so o piso minimo)
    "@react-three/fiber": "^9.6.1",           // reconciler React->three (Canvas, useFrame, useThree). peer react ">=19 <19.3"
    "@react-three/drei": "^10.7.7",           // helpers (peer fiber ^9): ScrollControls, useGLTF, Environment, useDetectGPU, PerformanceMonitor, AdaptiveDpr, Float
    "@react-three/postprocessing": "^3.0.4",  // wrapper postpro. TRAZ postprocessing como dependency normal (^6.36.6), NAO peer. Nao instalar postprocessing a mao.
    "lenis": "^1",                            // smooth scroll. Import React: "lenis/react" -> { ReactLenis, useLenis }. NAO @studio-freight/lenis (morto)
    "gsap": "^3"                              // + ScrollTrigger. Para sites DOM-first com pin/horizontal/parallax
  },
  "devDependencies": {
    "@react-three/gltfjsx": "latest",         // npx gltfjsx model.glb --transform --types
    "@gltf-transform/cli": "latest",          // pipeline fino draco/meshopt/ktx2/resize
    "leva": "latest"                          // GUI debug de params em dev (opcional)
  }
}
```

Condicionais (instalar so quando o caso pede):
- `detect-gpu` + `react-intersection-observer` - gate de degradacao + lazy-mount (ver armadilha #1).
- `@react-three/rapier` - fisica (objeto dirigivel, inercia de scroll estilo basement.studio).
- `troika-three-text` - texto 3D nitido em cena (estilo Atmos).
- `three-mesh-bvh` - colisao/raycast leve para mundo exploravel.
- `@splinetool/react-spline` - SO no fallback Spline (ver secao 5).

Compatibilidade: `fiber@9` pareia com `react@19` (Next.js 16 ja roda React 19).
`fiber@8` e a ultima linha para react@18 - NAO usar aqui. `drei@10` pede `three >=0.159`,
`fiber@9` pede `three >=0.156` - ambos sao PISO, o pin correto e o latest (~0.184).

`@react-three/postprocessing@3` exporta (verificado no tarball): EffectComposer, Bloom,
SelectiveBloom, ChromaticAberration, DepthOfField, N8AO, Noise, SMAA, ToneMapping, Vignette.
Autor da lib base e Raoul van Ruschen (handle npm `vanruesc`), org pmndrs.

## 2. Arquitetura Next.js 16 (App Router) - a cadeia de 4 arquivos

**Correcao critica:** `dynamic(..., { ssr:false })` NAO pode ficar direto num Server
Component no Next 16 - gera ERRO DE BUILD ("ssr: false is not allowed with next/dynamic
in Server Components"). O `dynamic ssr:false` mora DENTRO de um Client Component wrapper.

```tsx
// app/page.tsx - SERVER component (default). So renderiza o wrapper + poster.
import SceneGate from "@/components/three/SceneGate";

export default function Page() {
  return (
    <section className="relative h-screen">
      {/* POSTER = LCP element real. <img>/background-image url() SAO elegiveis; canvas NAO e.
          fetchPriority high + preload garante LCP <=2.5s independente do three.js.
          Este mesmo asset e o fallback de tier-0/reduced-motion (1 asset, 3 problemas). */}
      <img src="/hero-poster.webp" alt="" fetchPriority="high"
           className="absolute inset-0 h-full w-full object-cover" />
      <SceneGate /> {/* Canvas monta lazy por cima do poster */}
    </section>
  );
}
```

```tsx
// components/three/SceneGate.tsx - CLIENT. Aqui (e so aqui) vive o dynamic ssr:false.
"use client";
import dynamic from "next/dynamic";
import { useInView } from "react-intersection-observer";

const Scene = dynamic(() => import("./Scene"), { ssr: false }); // chunk three.js so no cliente

export default function SceneGate() {
  const { ref, inView } = useInView({ triggerOnce: true, rootMargin: "200px" });
  return <div ref={ref} className="absolute inset-0">{inView && <Scene />}</div>;
}
```

```tsx
// components/three/Scene.tsx - CLIENT. O Canvas.
"use client";
import { Canvas } from "@react-three/fiber";          // Canvas vem do FIBER, nunca do drei
import { AdaptiveDpr, PerformanceMonitor } from "@react-three/drei";
import { useState } from "react";
import Model from "./Model";

export default function Scene() {
  const [dpr, setDpr] = useState(1.5);
  return (
    <Canvas
      frameloop="demand"                       // cena estatica: nao roda RAF a 60fps. invalidate() ao animar.
      dpr={[1, 2]}                             // clamp OBRIGATORIO (Retina dpr3 = 9x pixels = morte mobile)
      gl={{ antialias: false, alpha: false, stencil: false, depth: true }} // antialias off se usar postpro
      camera={{ position: [0, 0, 5], fov: 45 }}
    >
      <PerformanceMonitor onDecline={() => setDpr((d) => Math.max(1, d - 0.25))} />
      <AdaptiveDpr pixelated />
      <ambientLight intensity={0.6} />
      <directionalLight position={[5, 5, 5]} intensity={1.2} />
      <Model />
    </Canvas>
  );
}
```

```tsx
// components/three/Model.tsx - saida do gltfjsx --transform --types
"use client";
import { useGLTF } from "@react-three/drei";
export default function Model() {
  const { nodes, materials } = useGLTF("/model-transformed.glb");
  return <mesh geometry={(nodes.Foo as any).geometry} material={materials.bar} />;
}
useGLTF.preload("/model-transformed.glb");
```

```ts
// next.config.ts - transpilePackages e fix CONDICIONAL (add-ons nao transpilados
// do ecossistema three, tipo examples/jsm). NAO e sempre obrigatorio com Turbopack.
// Adicionar SO se der erro de transpile:
// const config = { transpilePackages: ["three"] };
export default {};
```

## 3. Pipeline de asset (sempre, antes de producao)

1. Baixar `.glb` - CHECAR LICENCA (ver secao 5).
2. `npx gltfjsx model.glb --transform --types` -> gera `Model.tsx` + `model-transformed.glb`
   (70-90% menor: draco, prune, dedup, resize textura 1024, webp).
3. Modelo ESTATICO -> Draco. Modelo ANIMADO/morph -> Meshopt via `@gltf-transform/cli`
   (gltfjsx so expoe `--draco`, NAO existe `--meshopt`; meshopt sai do gltf-transform).
   Correcao: Draco NAO "perde" animacao - ele apenas NAO COMPRIME esses streams (ficam
   intactos, nao comprimidos). Por isso animado -> Meshopt (comprime tambem animacao/morph).
4. Textura -> KTX2/Basis (corta VRAM ~4-8x tipico; ate ~10x em cenarios com varias 4K).
5. Self-host do decoder Draco em `/public` + `useGLTF.setDecoderPath(...)` - nao depender
   de CDN externo em producao.

Budget: alvo 1-2MB / teto 5MB SO depois de Draco+KTX2. Mobile <5MB, desktop ~15MB (nao 20).
Draco ~90-95% geometria, MAS decoder WASM ~100-200KB pode anular ganho em mesh <1MB
(nao aplicar Draco cegamente em asset pequeno).

## 4. Cardapio de referencias (o que replicar de cada)

| Site | Categoria | O que mandar replicar |
|------|-----------|------------------------|
| Bruno Simon (bruno-simon.com) | Objeto interativo com fisica | Carro/personagem dirigivel, fisica por naming, instancing massivo, presets de qualidade mobile (desliga DOF no mobile). Codigo MIT aberto = blueprint direto. |
| ATMOS (atmos.earth) | Viagem por scroll narrativa | CatmullRomCurve3 + camera ao longo da curva via useScroll, sky sphere com shader Perlin, nuvens instanciadas, DOF -> radial blur 2D barato, texto via Troika, GSAP. Tutorial Wawa Sensei = receita pronta. |
| The Monolith Project (themonolithproject.net) | Site = curta-metragem (13 cenas) | R3F + GSAP + postpro. Scene transitions como protagonista, GPU particles, transition shaders modularizados. |
| Equinox (equinox.space) | Anti-slop / direcao | PRINCIPIO, nao tecnica: ganhou SOTD com atmosfera + som + timing, nao com poligono. A cena serve a narrativa, nao o inverso. |
| basement.studio | Portfolio low-cost alto-impacto | Planos 3D com texturas (imagens reais) + Rapier para fisica/inercia no scroll. Molde otimo para agencia/portfolio. |
| Lusion (lusion.co) | Tier estudio (aspiracional) | Truque-chave: simular pesado OFFLINE (Houdini/cloth) e tocar resultado como ArrayBuffer (~220KB) + distorcao leve em runtime. Nunca simular cloth/fluid real-time no browser. |
| Codrops (tympanus.net/codrops) | Biblioteca de receitas | Referenciar artigo por tecnica em vez de reinventar GLSL: "Reactive Depth" (tube 3D scroll), GPGPU particles, RGB-shift no hover. |
| Apple / Stripe / Nike | Tier comercial sobrio | Stripe = fragment shader de gradiente (superficie, nao objeto); Apple = scroll-reveal via IntersectionObserver + lightmaps baked; Nike = configurador PBR. |

Cursos-fonte: Three.js Journey (Bruno Simon: basics->shaders->postpro->Blender+bake->R3F)
e Wawa Sensei (lado R3F/Drei/Rapier + clone Atmos passo-a-passo).

## 5. Spline vs R3F - recomendacao

**DEFAULT: R3F.**
- Awwwards SOTD reais (Monolith, Equinox) sao R3F/Three.js + GSAP + shaders. Spline embed
  aparece em hero simples, nao em SOTD interativo.
- Custo: R3F e MIT (gratis, zero watermark). Spline free poe WATERMARK; remover exige
  Starter (~$12/seat/mes); API/video so no Professional (~$20/seat/mes).
- Performance: runtime Spline ~491KB fixo nao-tree-shakeavel + CPU drain cronico
  (issue conhecida: 99-100% CPU mesmo idle; reduzir poligono NAO resolve).
- Export GLB do Spline traz SO geometria (luzes e materiais somem). "Exportar e usar"
  entrega modelo cinza.

**FALLBACK Spline (atalho controlado, nao default):** prazo curto + cliente nao-tecnico
que muda direcao toda semana + 3D decorativo/simples. Entrega em horas o que R3F leva dias.
Condicoes obrigatorias: lazy-load + placeholder/poster (NUNCA acima da dobra eager - caso
real: LCP 5.7s -> 0.6s e Lighthouse 30 -> 90 com lazy-load), self-host do `.splinecode`,
plano pago para tirar watermark, testar em maquina fraca antes de entregar.

**Ponte hibrida:** modelar forma rapido no Spline (cliente mexe) -> export GLB so-geometria
-> gltfjsx -> RECRIAR luz/material no R3F (MeshStandardMaterial/MeshPhysical, ou `lamina`
para materiais em camadas estilo Spline). Velocidade de Spline + controle/perf de R3F.

## 6. Scroll-driven 3D - duas rotas que nao se misturam

- **Rota A (canvas protagonista):** drei `ScrollControls pages={n} damping={0.25}` +
  `<Scroll html>` overlay. `useScroll().offset` lido em useFrame. Casar timeline GSAP sem
  ScrollTrigger: `tl.seek(offset * tl.duration())` em useFrame.
- **Rota B (DOM-first, 3D pontual):** Lenis + GSAP ScrollTrigger; o 3D le progresso via
  useFrame/gsap.ticker. Esta e a rota Awwwards classica (pin, horizontal, parallax).

**NUNCA** pin de ScrollTrigger por cima de ScrollControls no mesmo eixo: o ScrollControls
aplica damping/easing e o ScrollTrigger pin le scroll nativo -> dessincroniza (jitter, pin
deslocado). Conflito ESPECIFICO (damping vs leitura nativa), nao incompatibilidade geral.

Integracao Lenis+GSAP CORRETA (sem `scrollerProxy`, que e legado e fonte de bug - Lenis
moderno roda sobre native scroll):
```js
lenis.on("scroll", ScrollTrigger.update);
gsap.ticker.add((t) => lenis.raf(t * 1000));
gsap.ticker.lagSmoothing(0);
// Lenis com autoRaf:false (loop RAF unico) + ScrollTrigger.refresh() apos mount
```
Ressalva honesta: GSAP oficialmente NAO suporta Lenis (recomenda o proprio ScrollSmoother).
O padrao Lenis+ScrollTrigger e norma de comunidade, solido na pratica.

## 7. Incertezas honestas (o que NAO esta 100% confirmado)

- `prefers-reduced-motion` unificado com detect-gpu numa branch unica: boa engenharia, mas
  NAO ha doc R3F oficial unindo os dois. Inferencia razoavel, nao padrao documentado.
- VRAM "10x" / "300MB->30MB" do KTX2: cenario OTIMISTA de venda; evidencia primaria Khronos
  mostra 4-8x tipico (~4.5-5.4x em exemplos reais). Comunicar como "ate ~10x, 4-8x tipico".
- Environment/HDR no mobile: o custo de memoria existe (OOM de EXR/PMREM nao comprimido),
  mas env map prefiltrado pode ser MAIS BARATO que varias luzes com sombra. A regra "fake
  lights no mobile" e defensavel por OOM, mas o problema real e HDR pesado nao comprimido
  (usar KTX2/resolucao menor), nao "env map e ruim".
