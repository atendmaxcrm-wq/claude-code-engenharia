---
name: site-3d
description: Criar sites 3D premium nivel Awwwards (cena/objeto 3D protagonista que reage a scroll e mouse), com React Three Fiber + drei + GSAP/Lenis em Next.js 16. Stack default R3F (gratis, MIT, sem watermark), fallback Spline so para prazo curto. Espelha o metodo da /replicar-sistema: referencia visual real -> boilerplate canonico -> rubrica cirurgica com 9 gates (performance mobile no topo). Use quando o usuario pedir: site 3D, hero 3D, objeto 3D interativo, cena WebGL, "site nivel Awwwards", "site tipo Bruno Simon/Atmos/Lusion", scroll cinematografico 3D, produto 3D girando, three.js/react-three-fiber, ou "fazer sites tao bons quanto esses" mostrando referencia 3D. NAO e para background WebGL sutil de marketing (isso e camada de /replicar-sistema ou um shader simples), nem para video scroll-scrub (isso e /site-elite-cinema).
---

# /site-3d - Sites 3D Premium (React Three Fiber)

> O degrau acima de um site bonito: a cena 3D E o site. Objeto/produto que reage a scroll
> e mouse, scroll cinematografico, fisica. Nivel Awwwards Site of the Day.
>
> Filosofia herdada da /replicar-sistema (o que de fato faz site bom): **referencia visual
> real + boilerplate canonico + rubrica cirurgica com gates**. Nao destilar 3D no abstrato.

## Verdade de base (leia antes de prometer)

As "ferramentas magicas" de site 3D (Emergent, Spline AI) sao, por baixo, React + Tailwind +
um runtime 3D + um agente de IA. Voce JA tem React/Next/Tailwind/GSAP. O 3D e `npm install`
gratis (R3F/three, MIT). O agente de IA e voce. Nao precisa de ferramenta paga. O que separa
slop de Awwwards e METODO: ancorar numa referencia real e respeitar a rubrica de performance.

Detalhe tecnico completo e verificado: `references/00-briefing-tecnico.md`.

## Quando usar / quando NAO usar

USAR: cena/objeto 3D protagonista, hero 3D interativo, produto girando, scroll cinematografico
3D, "nivel Awwwards/Bruno Simon/Atmos/Lusion", configurador 3D de produto.

NAO usar:
- Background WebGL sutil de marketing (gradient mesh atras do hero) -> shader simples ou
  camada de fundo na /replicar-sistema. Nao monte three.js so pra isso.
- Video hero com scroll-scrub (frame de filme) -> `/site-elite-cinema`.
- Clone pixel-perfect de site por URL -> `/clonar-site`.
- Replicar a CARA (acabamento 2D premium) de uma referencia, sem 3D -> `/replicar-sistema`.

Combinacao comum: a referencia do usuario tem 3D E acabamento premium 2D. Entao /site-3d
(o 3D + performance) trabalha JUNTO com /replicar-sistema (o mockup canonico + rubrica de
acabamento das secoes 2D) e /clonar-design (extrair o design system da referencia).

## Workflow (6 fases, espelhando a /replicar-sistema)

```
[0] Roteamento de decisao -> stack (R3F default | Spline fallback | hibrido) + rota de scroll
[1] Referencia real ancorada -> qual tecnica de qual site replicar (cardapio + anti-slop)
[2] Boilerplate canonico -> os 4 arquivos com performance embutida POR PADRAO
[3] Asset pipeline -> gltfjsx --transform -> Draco/Meshopt -> KTX2 -> budget
[4] Construir a cena -> useFrame por ref, scroll pela rota certa, postpro se "high"
[5] Rubrica cirurgica (9 gates) -> quality gate binario antes de "pronto"
```

### Fase 0 - Roteamento de decisao

Arvore (2 perguntas no maximo ao usuario, o resto e decisao tecnica sua):

1. **Objetivo do 3D?**
   - Experiencia imersiva / cena narrativa -> R3F + rota de scroll A ou B.
   - Configurador de produto (gira, troca cor/material) -> R3F + controls + PBR.
   - Fundo 3D decorativo simples, prazo curto, cliente que muda toda semana -> Spline fallback.

2. **O site e canvas-first ou DOM-first?**
   - Canvas protagonista, HTML acompanha -> **Rota A: drei ScrollControls** (`<Scroll html>`).
   - Pagina longa com secoes, pin/horizontal/parallax classico Awwwards, 3D pontual ->
     **Rota B: Lenis + GSAP ScrollTrigger** (conecta com `/gsap-animations`).

Stack default = **R3F** (MIT, sem watermark, e o que SOTD real usa). Spline so como atalho
controlado (ver `00-briefing-tecnico.md` secao 5: tem watermark no free, runtime ~491KB,
CPU drain, export GLB perde luz/material). NUNCA misturar ScrollControls com ScrollTrigger
pin no mesmo eixo.

### Fase 1 - Referencia real ancorada (o que faz NAO ser slop)

Como na /replicar-sistema: sem referencia visual real, a saida converge pra media do training
data. Pegar a referencia do usuario (video/print) OU escolher do cardapio e mapear a TECNICA.

Cardapio (detalhe em `00-briefing-tecnico.md` secao 4): Bruno Simon (objeto dirigivel,
fisica, codigo MIT aberto), Atmos (camera em curva por scroll, tutorial Wawa Sensei),
Monolith (cena = curta-metragem), basement.studio (planos 3D + Rapier, otimo pra portfolio),
Lusion (simular offline e tocar como buffer), Codrops (receitas por tecnica), Apple/Stripe/Nike
(tier comercial sobrio).

**Principio anti-slop (regra Equinox):** a cena 3D serve a uma narrativa/objetivo. 3D tecnico
sem proposito e esquecivel. Antes de codar, responda: o que a cena COMUNICA? Se a resposta e
"que sei fazer 3D", para e repensa.

Para extrair o design system 2D da referencia (cores, tipo, motion das secoes nao-3D):
invocar `/clonar-design` (tem o design-scraper.py). Para o acabamento das secoes 2D:
`/replicar-sistema` (mockup canonico + rubrica).

### Fase 2 - Boilerplate canonico

Copiar a cadeia de 4 arquivos de `references/01-boilerplate-r3f.md` (ou `00` secao 2). Eles
JA vem com: gate de performance unico, `dpr={[1,2]}` clamp, `frameloop="demand"`, poster-LCP,
lazy-mount por `useInView`, e `dynamic ssr:false` DENTRO de Client Component (no Next 16,
ssr:false em Server Component = erro de build). Nao reescrever do zero; partir do boilerplate.

Cadeia: `page.tsx` (server, poster + gate) -> `SceneGate.tsx` (client, dynamic ssr:false +
lazy-mount) -> `Scene.tsx` (client, `<Canvas>`) -> `Model.tsx` (`useGLTF`).

### Fase 3 - Asset pipeline (obrigatorio)

1. Fonte do `.glb` - CHECAR LICENCA por modelo (Poly Pizza e MISTO CC0+CC-BY; Quaternius e
   CC0; em CC-BY creditar no rodape).
2. `npx gltfjsx model.glb --transform --types` (gera componente + glb 70-90% menor).
3. Estatico -> Draco; animado/morph -> Meshopt (`@gltf-transform/cli`). Draco nao "perde"
   animacao, so nao a comprime.
4. Textura -> KTX2/Basis. Self-host do decoder Draco em `/public`.
5. Budget: alvo 1-2MB, teto 5MB pos-compressao. Mobile <5MB, desktop ~15MB.

### Fase 4 - Construir a cena

- Animacao SEMPRE por ref dentro de `useFrame` (`ref.current.rotation.y += delta`). NUNCA
  `setState` nem `new THREE.*` no loop (ver `02-armadilhas-performance.md` #3).
- Scroll pela rota escolhida na Fase 0 (A ou B, nunca as duas no mesmo eixo).
- Postprocessing (Bloom + emissivos >1.0 = look premium) SO no tier "high"; desligar no mobile.
- Mouse: `useThree(state => state.pointer)` lido em useFrame, com lerp suave (nao snap).
- Mobile (tier "low"): <=2-3 luzes, sem postpro, sem HDR pesado, dpr cap 1.5.

### Fase 5 - Rubrica cirurgica (9 gates binarios - quality gate antes de "pronto")

Cada item e testavel. Reprovou um -> nao esta pronto. Esta e a diferenca entre "premium" e
"demo de three.js".

- [ ] **LCP:** poster `<img>`/background-image url() e o LCP element (canvas NUNCA e). LCP
      <=2.5s medido com web-vitals.
- [ ] **Gate de degradacao:** tier-0 GPU / mobile fraco / `prefers-reduced-motion` servem o
      fallback (poster), testado em DEVICE real ou emulacao 390px - nao so desktop.
- [ ] **dpr clamp:** `dpr={[1,2]}` presente (mobile cap 1.5).
- [ ] **frameloop:** `"demand"` se a cena e estatica/scroll-driven (nao RAF perpetuo a toa).
- [ ] **useFrame limpo:** grep zero `setState|new THREE.(Vector3|Color|Matrix4|Quaternion)|.clone(`
      dentro de useFrame/render.
- [ ] **Orcamento de cena:** draw calls <100 (teto duro 500), <=3 luzes no mobile, instancing
      em qualquer repeticao. Conferir `renderer.info`.
- [ ] **Asset:** `.glb` passou por `gltfjsx --transform`, dentro do budget, licenca conferida
      (atribuicao se CC-BY).
- [ ] **SSR:** `dynamic ssr:false` dentro de Client Component (nunca Server Component);
      lazy-mount via `useInView`. Build de producao passa.
- [ ] **Scroll:** nao mistura ScrollControls com ScrollTrigger pin no mesmo eixo. `dispose()`
      no unmount; `renderer.info.memory` sem vazamento crescente.

Validacao no teste-aios: `next build` + `next start` (NUNCA `next dev` para acesso externo -
regra do projeto). Screenshot desktop + mobile via Playwright, console sem erro, objeto
reagindo a scroll/mouse. Rodar `/safari-check` se for entregar pra cliente.

## Fase 6 (opcional) - Tier vanguarda WebGPU

`WebGPURenderer` + TSL com fallback WebGL OBRIGATORIO (progressive enhancement). 2-10x em
cenas draw-call-heavy. Chunk separado. Marcar como tier ponta, nao default - so quando a cena
realmente satura draw calls e o publico tem hardware recente.

## Regras teste-aios (criticas)

- **Next.js 16 + Tailwind v4 + Turbopack.** Para spacing/sizing usar inline `style={{}}`
  (classes Tailwind nao refletem confiavelmente). Classes genericas (flex/grid) ok.
- **next build + next start** para acesso via IP/dominio. `next dev` so localhost.
- **Heredoc proibido** via Bash - usar Write tool.
- **Portas livres:** 3113-3115 (verificar `ss -tlnp` antes de subir).
- **Sem em-dash** em conteudo PT-BR.

## Skills relacionadas

- `/replicar-sistema` - acabamento premium das secoes 2D + mockup canonico + rubrica. Par natural.
- `/clonar-design` - extrai design system (cores/tipo/animacoes/video) da referencia real.
- `/auditar-fidelidade` - quality gate de completude vs a referencia.
- `/gsap-animations` - deep-dive de scroll/pin/parallax (rota B DOM-first).
- `/site-elite-cinema` - quando o "3D" e na verdade video scroll-scrub.
- `/safari-check` - compatibilidade Safari iOS/macOS antes de entregar.

## Referencias internas

- `references/00-briefing-tecnico.md` - stack pins, arquitetura Next 16, asset, Spline vs R3F, scroll. Verificado adversarialmente.
- `references/01-boilerplate-r3f.md` - setup + 2 variantes de scroll (ScrollControls / Lenis+GSAP) + useFrame certo vs errado.
- `references/02-armadilhas-performance.md` - as 5 armadilhas + LCP, com prevencao por padrao.
