---
name: capturar-efeitos
description: Engenharia reversa de efeitos visuais e animacoes de sites. Identifica a tecnologia por tras de WebGL shaders, parallax, hyperspace, scroll animations, cursor effects. Descobre libs usadas (UnicornStudio, Spline, Rive, three.js, GSAP, Lenis, Framer Motion) e extrai o code path minimo para replicar. Use quando o usuario quer "capturar esse efeito", "como esse site faz essa animacao", "que lib esse cara usa", "descobrir como ele fez isso", ou quando ver uma referencia e quiser saber o que tem por tras.
---

# Capturar Efeitos

Skill que faz engenharia reversa cirurgica de **efeitos visuais** em sites. Nao clona o site (isso e `/clonar-site`). Aqui a entrega e:

1. **O que e o efeito** (shader custom / cena Spline / UnicornStudio / canvas 2D / SVG / CSS puro / lib X)
2. **A origem real do codigo** (bundle minificado, CDN, Supabase, iframe, srcdoc, scene URL)
3. **Como replicar** no projeto do usuario (snippet minimo + deps + IDs ou shader extraido)

## Quando disparar

Ativa automaticamente quando o usuario:

- "Como ele fez essa animacao?"
- "Que lib esse cara esta usando?"
- "Capturar esse efeito"
- "Quero esse mesmo negocio no meu site"
- "Copiar essa parte que pulsa/brilha/ondula"
- "Descobrir como ele esta fazendo isso"
- "O que tem por tras desse site?"
- Manda URL + pergunta tecnica sobre UM elemento especifico (nao o site inteiro)

**Nao disparar quando**:
- Usuario quer clonar o site inteiro (→ `/clonar-site`)
- Usuario quer scraping de conteudo (→ `/scraping`)
- Usuario quer design tokens (cores/fontes) sem efeitos (→ `/clonar-design`)

## Pipeline de 7 fases

Cada fase tem ferramentas e condicoes de parada. Se a fase N resolver, pula as proximas.

---

### Fase 1 — Inspecao visual (1 min)

**Objetivo**: entender o que o usuario esta chamando de "efeito". Pode ser:

- Background animado (feixe, estrada, partículas, orb, blobs)
- Scroll-linked (parallax, reveal, pin, horizontal scroll)
- Cursor interaction (magnetic, trail, distortion)
- Hover (tilt, glow, morph)
- Text (scramble, split, decrypt)
- 3D scene (camera, lighting, geometry)
- Transicao de pagina

**Acao**: Pedir clareza se ambiguo. **Nunca assumir**. Pergunta curta tipo: "E o fundo que pulsa no hero, ou o card que flutua, ou as letras que aparecem?".

Se o usuario mandar video/print da referencia, usar `ffmpeg` pra extrair frames:

```bash
ffmpeg -i video.mp4 -vf "fps=1,scale=960:-1" -q:v 3 "frames/f%03d.jpg"
```

Ler frames estrategicos (inicio, meio, fim) + qualquer screenshot/print disponivel.

---

### Fase 2 — Abrir o site via Playwright MCP (2 min)

**Objetivo**: carregar o site real pra inspecionar DOM, network, libs carregadas.

```
mcp__playwright__browser_navigate → URL
mcp__playwright__browser_wait_for → 3s
mcp__playwright__browser_evaluate → inspecao
```

**Sempre checar iframe**: Se o site e template hospedado (aura.build, framer preview, etc), o efeito fica dentro de um `<iframe>`. Passar pelo `iframe.contentDocument` ou `contentWindow`.

**Script de inspecao padrao** (executar via `browser_evaluate`):

```javascript
() => {
  // Busca iframe se houver
  const iframe = document.querySelector('iframe');
  const doc = iframe ? iframe.contentDocument : document;
  const win = iframe ? iframe.contentWindow : window;

  // Libs conhecidas (flags globais)
  const techs = [];
  if (win.gsap) techs.push('GSAP');
  if (win.ScrollTrigger) techs.push('ScrollTrigger');
  if (win.SplitText) techs.push('SplitText');
  if (win.Lenis) techs.push('Lenis');
  if (win.THREE) techs.push('Three.js');
  if (win.anime) techs.push('AnimeJS');
  if (win.Matter) techs.push('Matter.js');
  if (win.UnicornStudio) techs.push('UnicornStudio');
  if (doc.querySelector('spline-viewer') || doc.querySelector('[data-spline]')) techs.push('Spline');
  if (doc.querySelector('[data-rive]') || win.rive) techs.push('Rive');
  if (doc.querySelector('[data-framer-motion]')) techs.push('Framer Motion');
  if (doc.querySelector('[data-us-project]')) techs.push('UnicornStudio (embed)');
  if (doc.querySelector('[data-locomotive-scroll]')) techs.push('Locomotive Scroll');

  // Canvas (WebGL indica shader/three/spline)
  const canvases = [...doc.querySelectorAll('canvas')].map(c => ({
    w: c.width, h: c.height,
    parent: c.parentElement?.tagName,
    hasWebGL: !!(c.getContext('webgl2') || c.getContext('webgl')),
  }));

  // Network (URLs de scenes, shaders, etc)
  const res = performance.getEntriesByType('resource').map(r => r.name);
  const suspicious = res.filter(n =>
    /spline\.design|splinecode|rive\.app|\.riv$|unicornstudio|lottie|\.glb$|\.gltf$|\.splat$/i.test(n)
  );

  // Scripts externos carregados
  const scripts = [...doc.querySelectorAll('script[src]')].map(s => s.src)
    .filter(s => /gsap|three|spline|rive|unicorn|lottie|locomotive|lenis|motion/i.test(s));

  return { techs, canvases, suspicious, scripts };
}
```

**Resultado esperado**: Lista de techs detectadas + URLs interessantes (scene files, riv, lottie).

---

### Fase 3 — Identificar tipo de efeito pela combinacao (2 min)

Com base na Fase 2, classificar:

| Combinacao | Provavel tecnica |
|---|---|
| `UnicornStudio` + `[data-us-project]` + canvas WebGL | **Cena UnicornStudio** (no-code WebGL) |
| `spline-viewer` ou URL `.splinecode` | **Cena Spline** (design 3D no-code) |
| `[data-rive]` ou arquivo `.riv` | **Animacao Rive** |
| `THREE` + canvas + `.glb/.gltf` | **Three.js custom** com modelo 3D |
| `THREE` + canvas **sem** modelo 3D | **Shader custom GLSL** (mais provavel fullscreen quad) |
| `GSAP` + `ScrollTrigger` sem canvas | **Animacao DOM scroll-linked** |
| `Lottie` + JSON | **Animacao Lottie** (After Effects export) |
| Canvas **sem** WebGL (so 2D) | **Canvas 2D custom** (raf + partículas) |
| Apenas CSS/Tailwind, sem canvas | **CSS puro** (animation + gradients + filter) |

**Taxa de ocorrencia real (2026):** 70% dos "efeitos sofisticados" em landings de SaaS sao **UnicornStudio, Spline ou Rive** (libs black-box no-code). 20% sao shader custom com three.js ou ogl. 10% canvas 2D ou CSS puro.

---

### Fase 4 — Extrair o identificador/artefato (5-15 min)

Objetivo: conseguir o **pedaco minimo reproduzivel** do efeito. Depende da tecnica:

#### Caso A — UnicornStudio

Basta o `data-us-project="ID"`. No HTML (ou iframe):

```bash
# Inspeciona o DOM
document.querySelectorAll('[data-us-project]')
```

Snippet minimo pra replicar:

```html
<div data-us-project="ID_COPIADO"></div>
<script>
!function(){if(!window.UnicornStudio){window.UnicornStudio={isInitialized:!1};var i=document.createElement("script");i.src="https://cdn.jsdelivr.net/gh/hiunicornstudio/unicornstudio.js@v1.4.34/dist/unicornStudio.umd.js",i.onload=function(){window.UnicornStudio.isInitialized||(UnicornStudio.init(),window.UnicornStudio.isInitialized=!0)},(document.head||document.body).appendChild(i)}}();
</script>
```

**Fim.** A cena e publica no CDN do Unicorn Studio, funciona direto.

#### Caso B — Spline

Pegar URL `.splinecode`:

```javascript
document.querySelector('spline-viewer').getAttribute('url')
```

Snippet React:

```tsx
'use client';
import Spline from '@splinetool/react-spline';
<Spline scene="https://prod.spline.design/XXXX/scene.splinecode" />
```

#### Caso C — Rive

Pegar URL do `.riv`:

```javascript
performance.getEntriesByType('resource').filter(r => r.name.endsWith('.riv'))
```

Snippet React (usa `@rive-app/react-canvas`).

#### Caso D — Shader custom (three.js / ogl)

Preciso **capturar o GLSL** em tempo de execucao. Hook em `WebGLRenderingContext.prototype.shaderSource`:

```javascript
() => {
  const iframe = document.querySelector('iframe');
  const win = iframe ? iframe.contentWindow : window;
  if (!win.__shaderCapture) {
    win.__shaderCapture = [];
    [win.WebGLRenderingContext, win.WebGL2RenderingContext].forEach(Ctx => {
      if (!Ctx) return;
      const orig = Ctx.prototype.shaderSource;
      Ctx.prototype.shaderSource = function(sh, src) {
        win.__shaderCapture.push(src);
        return orig.call(this, sh, src);
      };
    });
  }
  return win.__shaderCapture.length;
}
```

**Importante**: O hook precisa ser instalado **antes** do canvas ser criado. Se ja carregou, forcar `location.reload()` no iframe depois do hook.

Depois:

```javascript
window.__shaderCapture // array de strings GLSL
```

Filtrar por `void main()` pra pegar fragment vs vertex.

#### Caso E — Site e template no-code (aura.build, framer, v0, lovable)

**Descoberta importante (caso real CRMax)**: muitos builders guardam o codigo fonte em **tabelas publicas Supabase/Firebase**. Seguir o modulo `references/full-source-recovery.md`.

Resumido:
1. Inspecionar `performance.getEntriesByType('resource')` procurando chamadas a Supabase (`supabase.co/rest/v1/`)
2. Achar o slug do projeto na URL da API
3. Pegar a anon key do bundle JS: `grep -oE 'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}'`
4. Curl direto: `curl "https://SUPABASE/rest/v1/TABELA?select=code&slug=ilike.SLUG" -H "apikey: JWT" -H "Authorization: Bearer JWT"`

Resultado: codigo-fonte HTML/CSS completo. Ai volta pra Fase 3 agora com visao total.

---

### Fase 5 — Validar replicacao (3 min)

Criar arquivo de teste minimo no projeto:

```bash
# Next.js
echo "export default function TestEffect() { return <div>EFEITO AQUI</div>; }" > src/app/teste-efeito/page.tsx
```

Aplicar snippet da Fase 4. Acessar a rota, conferir via Playwright:

```javascript
// Existe canvas? Lib carregou? Script injetou?
() => {
  return {
    canvas: !!document.querySelector('canvas'),
    libLoaded: !!window.UnicornStudio || !!window.THREE || !!window.Spline,
  };
}
```

Se passou → pronto. Se falhou → debug:
- CORS no CDN?
- SSR quebrou? (envolver em `dynamic(() => ..., { ssr: false })`)
- Lib conflitou com bundler? (Next.js 16 + Turbopack e sensivel a GLSL em template literals — mover shader pra arquivo `.glsl` separado ou usar string simples)

---

### Fase 6 — Documentar a captura (2 min)

Criar em `/root/SEU_PROJETO/.refs/NOME/` um markdown com:

- URL da referencia
- Tecnica identificada
- Artefato capturado (ID, URL, shader, etc)
- Snippet de replicacao
- Adaptacoes feitas (se houver)
- Gotchas durante a replicacao

Isso vira memoria do projeto pra quando quiser ajustar depois.

---

### Fase 7 — Oferecer proximo passo

Depois de replicar, perguntar ao usuario se quer:

- **Personalizar** (trocar cores, ID, URL) — ex: criar cena propria no UnicornStudio / Spline / Rive
- **Aplicar** em outra secao
- **Capturar mais efeitos** do mesmo site
- **Atualizar** se o site de origem mudar

## Armadilhas conhecidas

### Tailwind v4 JIT quebra em bundle de terceiro

Se voce baixar o bundle JS/CSS da referencia pra analise, **nao salve dentro de `src/`** do seu projeto Next.js. O Tailwind v4 escaneia esses arquivos e interpreta pedacos de JS minificado como classes CSS, quebrando o build. Salvar em `/root/projeto-NOME-refs/` (fora do src).

### Hook `shaderSource` perde os shaders ja compilados

WebGL compila shaders no carregamento. Se o hook foi instalado depois, `__shaderCapture` fica vazio. Solucao: injetar o hook no iframe **antes** do srcdoc ser avaliado OU forcar `iframe.contentWindow.location.reload()` depois do hook.

### SSR do Next.js 16 quebra libs WebGL client-only

UnicornStudio, Spline viewer, three.js: todos precisam `window`. Envolver em:

```tsx
const Scene = dynamic(() => import('./Scene'), { ssr: false });
```

### Video do YouTube nao abre em VPS headless

"Sign in to confirm you're not a bot". Para analisar video de referencia, usar Instagram, TikTok via Playwright direto, ou pedir o usuario gravar tela e salvar em pasta local + extrair frames via `ffmpeg`.

### CORS bloqueia fetch direto

Se tentar `fetch` no browser pra Supabase/CDN de terceiro, CORS bloqueia. Usar `curl` no terminal (sem restricao de origem).

### Performance resource API so mostra URLs JA carregadas

Se o asset e lazy-loaded (scroll), precisa scrollar antes de inspecionar.

## Referencias

- `references/full-source-recovery.md` — Tecnica de extracao de code fonte de templates Supabase/Firebase
- `references/lib-signatures.md` — Como identificar cada lib pelo DOM/network (UnicornStudio, Spline, Rive, three.js, GSAP, Lenis, Lottie)
- `references/shader-capture.md` — Detalhes do hook `shaderSource` e como re-executar o render

## Caso real resolvido

**Problema**: efeito "hyperspace pulsante" do site `social-automation-template.aura.build` (template da aura.build chamado "Luminous") precisava ser replicado no CRMax.

**Caminho**:
1. Canvas 2D nosso ficou "cartoon" (feedback direto do usuario)
2. Ogl WebGL shader (tentativa 2) chegou perto mas sem mouse interaction
3. Descobri que o site e srcdoc vindo do Supabase da aura
4. Anon key no bundle JS da aura → curl direto → HTML completo (116kb)
5. Grep no HTML → `data-us-project="AhqzKk9mZE0EnlENMQDi"` + script UnicornStudio
6. Aplicacao: div + script no Hero do CRMax → efeito identico

**Tempo total**: 15 minutos (vs horas tentando recriar shader manualmente).
