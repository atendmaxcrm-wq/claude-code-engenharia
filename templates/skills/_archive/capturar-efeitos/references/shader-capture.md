# Captura de Shader GLSL em Tempo de Execucao

Tecnica para extrair fragment shader e vertex shader de qualquer site WebGL em tempo de runtime, mesmo com bundle minificado.

## Por que funciona

Todo site WebGL chama `gl.shaderSource(shaderObj, "...GLSL...")` para passar o codigo GLSL pro GPU. Se a gente monkey-patch o prototype **antes** desse call, capturamos o GLSL como string.

## O hook

```javascript
(function installShaderHook(win) {
  if (win.__shaderHookInstalled) return { already: true, captured: win.__shaderCapture.length };
  win.__shaderHookInstalled = true;
  win.__shaderCapture = [];
  [win.WebGLRenderingContext, win.WebGL2RenderingContext].forEach(function(Ctx) {
    if (!Ctx) return;
    var orig = Ctx.prototype.shaderSource;
    Ctx.prototype.shaderSource = function(shader, source) {
      win.__shaderCapture.push({
        ts: Date.now(),
        length: source.length,
        type: source.includes('gl_FragColor') || source.includes('out vec4') ? 'fragment' : 'vertex',
        source: source,
      });
      return orig.call(this, shader, source);
    };
  });
  return { installed: true };
})(window)
```

Executar via `mcp__playwright__browser_evaluate`. Se o site tem iframe, usar `iframe.contentWindow` no lugar de `window`.

## Timing — o problema do WebGL ja carregado

Se o canvas WebGL ja foi criado, os shaders ja foram compilados e o hook chegou atrasado. Solucoes:

### A) Reload com hook via `beforeParse`

Nao funciona com `page.goto` puro (o hook e instalado depois do script do site). Mas funciona se instrumentar via `addInitScript` antes do navigate:

No Playwright MCP, apos o navigate inicial, **forcar reload do iframe** programaticamente:

```javascript
() => {
  var iframe = document.querySelector('iframe');
  var win = iframe.contentWindow;
  // Install hook
  // ... codigo acima ...
  // Force reload
  iframe.src = iframe.src;
  return { reloadTriggered: true };
}
```

Esperar 3-5s, depois ler `win.__shaderCapture`.

### B) Force redraw via API

Se o site usa three.js:

```javascript
() => {
  var win = iframe.contentWindow;
  if (win.THREE && win.__renderer) {
    // forca compilar shader de novo (so captura se recompilar)
    win.__renderer.compile(win.__scene, win.__camera);
  }
}
```

Funciona so se o site expoe globals (raro em builds minificados).

### C) Recriar o efeito num tab novo

Abrir `new Tab` limpo, injetar hook primeiro, depois navegar. Feito no Playwright:

```
browser_tabs new
browser_evaluate (install hook on about:blank)
browser_navigate (URL alvo)
```

## Lendo os shaders capturados

```javascript
() => {
  var win = document.querySelector('iframe')?.contentWindow || window;
  return win.__shaderCapture.map(function(s) {
    return {
      type: s.type,
      length: s.length,
      preview: s.source.slice(0, 200),
    };
  });
}
```

Depois, pegar um por vez:

```javascript
() => {
  var win = document.querySelector('iframe')?.contentWindow || window;
  return win.__shaderCapture[0].source; // fragment shader completo
}
```

Salvar em `.glsl`:

```bash
# Pegar o retorno e salvar
echo "<GLSL_COPIADO>" > fragment.glsl
```

## Estrutura tipica de shaders capturados

### Vertex (geralmente curto, sem logica custom)

```glsl
attribute vec2 position;
attribute vec2 uv;
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = vec4(position, 0.0, 1.0);
}
```

Geralmente identico em todos os sites. Pode copiar direto.

### Fragment (onde esta a magica)

```glsl
precision highp float;
uniform float uTime;
uniform vec2 uResolution;
uniform vec2 uMouse;
varying vec2 vUv;

// ... funcoes auxiliares: noise, smoothstep, mix ...

void main() {
  vec2 uv = vUv;
  // ... logica do efeito ...
  gl_FragColor = vec4(color, 1.0);
}
```

Esse e o codigo que vale capturar.

## Replicar em projeto novo

Opcao 1 — **ogl** (lib leve, 8kb):

```tsx
import { Renderer, Program, Mesh, Triangle } from 'ogl';

const renderer = new Renderer({ dpr: 2 });
const gl = renderer.gl;
canvas.appendChild(gl.canvas);

const geometry = new Triangle(gl);
const program = new Program(gl, {
  vertex: `attribute vec2 position; void main() { gl_Position = vec4(position, 0, 1); }`,
  fragment: FRAGMENT_CAPTURADO,
  uniforms: {
    uTime: { value: 0 },
    uResolution: { value: [innerWidth, innerHeight] },
    uMouse: { value: [0.5, 0.5] },
  },
});
const mesh = new Mesh(gl, { geometry, program });

function raf(t) {
  program.uniforms.uTime.value = t * 0.001;
  renderer.render({ scene: mesh });
  requestAnimationFrame(raf);
}
requestAnimationFrame(raf);
```

Opcao 2 — **three.js** (se precisa de mais features):

```tsx
import * as THREE from 'three';

const scene = new THREE.Scene();
const geom = new THREE.PlaneGeometry(2, 2);
const mat = new THREE.ShaderMaterial({
  vertexShader, fragmentShader,
  uniforms: { uTime: { value: 0 }, uResolution: { value: new THREE.Vector2() }, uMouse: { value: new THREE.Vector2() } },
});
```

Opcao 3 — **@react-three/fiber** (se o projeto ja usa):

```tsx
import { shaderMaterial } from '@react-three/drei';
const MyMaterial = shaderMaterial({ uTime: 0 }, vertex, fragment);
extend({ MyMaterial });
```

## Gotchas no Next.js 16 + Turbopack

1. **Tailwind v4 escaneia TUDO no `src/`**. Se voce salvar um `.glsl` ou bundle de terceiro em `src/`, o Tailwind interpreta fragmentos como classes CSS e quebra o build. Salvar fora do `src` (ex: `public/shaders/`).

2. **SSR quebra**. Envolver em `dynamic(() => ..., { ssr: false })`.

3. **Template literal de shader pode disparar scan**. Se voce colocar GLSL inline como `const FRAG = \`void main() { ... }\``, Tailwind pode ler substrings como classes. Solucao: mover pra arquivo `.ts` com `export const FRAG = String.raw\`...\``.

## Checklist de captura

- [ ] Hook instalado antes do canvas renderizar
- [ ] Iframe recarregado apos hook (se necessario)
- [ ] `__shaderCapture` tem pelo menos 1 shader vertex + 1 fragment
- [ ] Fragment tem `gl_FragColor` ou `out vec4`
- [ ] Uniforms reconhecidos (uTime, uResolution, uMouse sao tipicos)
- [ ] Copia salva em `.glsl`
- [ ] Teste de replicacao: rodar em projeto limpo antes de integrar
