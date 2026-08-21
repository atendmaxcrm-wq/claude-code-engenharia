# As 5 armadilhas que mais matam um site 3D

> Ordenadas por impacto. A skill /site-3d previne TODAS por padrao no boilerplate, nao
> como dica opcional. Cada uma vira um gate na rubrica final (SKILL.md secao 5).

## #1 - Sem gate de performance mobile/GPU (a que mais reprova entrega)

Sintoma real do cliente: "seu site trava meu celular / notebook". WebGL trava ou nem
inicializa em tier-0 / mobile fraco.

Prevencao default:
- Gate UNICO antes de montar Canvas: `useDetectGPU()` (tier 0-3 + isMobile) + reduced-motion
  numa so decisao "render fallback vs render 3D". `tier===0 || mobile-fraco || reduced-motion`
  -> serve o POSTER (mesmo asset do LCP). Reduced-motion = REDUZIR/substituir movimento
  (cortar auto-rotacao e drift de camera), nao necessariamente poster total - mas reusar a
  branch e legitimo.
- `dpr={[1,2]}` clamp (mobile cap 1.5) + `PerformanceMonitor`/`AdaptiveDpr` para downgrade dinamico.
- `frameloop="demand"` em cena estatica (+ `invalidate()` ao animar via ref). Loop continuo
  so quando ha animacao perpetua.
- Cena mobile: `<=3` luzes, sem HDR pesado nao comprimido (OOM - usar KTX2/HDR menor, ou
  fake directional+ambient), `shadowMap.autoUpdate=false` em cena estatica, `dispose()` no unmount.

## #2 - three.js no caminho critico / canvas eager

~155KB gzip so de three.js (+ drei + postpro por cima) e three NAO tree-shaka bem. Import
estatico no entry infla TBT/LCP.

Prevencao default: code-split SEMPRE via `dynamic(...,{ssr:false})` DENTRO de um Client
Component (no Next 16, ssr:false em Server Component = erro de build) + lazy-mount por
`useInView` (so baixa o chunk perto da secao 3D). Nunca import estatico no entry.

## #3 - setState / criar objetos dentro de useFrame

Animar por estado React a 60fps re-renderiza a arvore inteira = jank. Recriar
`new THREE.Vector3/Color/Material/Geometry` no loop = garbage collection e stutter
(custo de COMPILACAO de material, nao de draw call).

Prevencao default: mutar via ref dentro de `useFrame` (`ref.current.rotation.x += delta`);
ler scroll/progresso DENTRO de useFrame, nunca via setState por frame. Geometria/material
custom UMA vez via `useMemo`/escopo de modulo, reusar. `useLoader`/`useGLTF` ja cacheia por
URL. Grep: `new Vector3|new Color|new Matrix4|new Quaternion|.clone(` dentro de useFrame.

## #4 - Misturar drei ScrollControls com GSAP ScrollTrigger pin

Conflito ESPECIFICO (nao incompatibilidade geral): ScrollControls aplica damping/easing,
ScrollTrigger pin le scroll nativo -> dessincroniza (jitter, pin deslocado).

Regra de decisao:
- Cena 3D autocontida, canvas protagonista -> `ScrollControls` + `<Scroll html>`. `useScroll().offset`
  em useFrame. Casar GSAP sem ScrollTrigger: `tl.seek(offset * tl.duration())`.
- Pagina longa DOM-first com pin/horizontal/parallax -> Lenis + GSAP ScrollTrigger; o 3D le
  progresso via useFrame/gsap.ticker.
- NUNCA pin de ScrollTrigger por cima de ScrollControls no mesmo eixo.

Lenis+GSAP correto (sem `scrollerProxy`, legado):
```js
lenis.on("scroll", ScrollTrigger.update);
gsap.ticker.add((t) => lenis.raf(t * 1000));
gsap.ticker.lagSmoothing(0);
```

## #5 - Asset pesado / licenca errada

.glb cru de Sketchfab pode ter dezenas de MB. Budget: alvo 1-2MB, teto 5MB SO depois de
Draco+KTX2. Mobile <5MB, desktop ~15MB. Draco ~90-95% geometria mas decoder WASM ~100-200KB
pode anular ganho em mesh <1MB. KTX2/Basis corta VRAM ~4-8x tipico (ate ~10x com varias 4K).

Importante: Draco NAO "perde" animacao/morph - ele apenas NAO COMPRIME esses streams (ficam
intactos, nao comprimidos). Modelo animado -> Meshopt (comprime tambem animacao e decodifica
mais rapido).

Licenca: Poly Pizza NAO e 100% CC0 - catalogo MISTO (CC0 + CC-BY), tem filtro de licenca.
"Poly by Google" la e CC-BY 3.0 (exige credito). Unica fonte CC0-by-default real entre as
comuns e Quaternius. Regra: FILTRAR/checar licenca por modelo; em CC-BY incluir atribuicao
no rodape; sempre passar por `gltfjsx --transform`.

## Bonus - LCP: canvas nunca e o LCP element

Tipos elegiveis a LCP: `<img>`, `<image>` em `<svg>`, `<video>` (poster/1o frame),
background-image `url()`, e texto block-level. Canvas e `<svg>` inteiro sao excluidos.
Se o canvas cobre o hero, o LCP cai para o proximo elemento (potencialmente tardio).

Contorno (1 asset, 3 problemas): poster `<img>` real com `fetchPriority="high"` (ou
background-image `url()` com preload) vira o LCP element; o canvas monta lazy por cima. Esse
mesmo poster e o fallback de tier-0 GPU e reduced-motion.
