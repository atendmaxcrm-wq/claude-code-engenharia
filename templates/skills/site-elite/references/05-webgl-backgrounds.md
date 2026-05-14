# 05 — WebGL Backgrounds

Hierarquia de complexidade: UnicornStudio (ready-to-use) -> Three.js (custom shader) -> Spline (3D scene) -> Canvas 2D (lightweight). Escolher o **menor peso possivel** para o efeito desejado.

## UnicornStudio (preferido)

Plataforma que hospeda shaders WebGL prontos. Voce pega um ID publico ou cria o seu, embeda via div + script.

### Loader

```html
<script src="https://cdn.jsdelivr.net/gh/hiunicornstudio/unicornstudio.js@v1.4.34/dist/unicornStudio.umd.js"></script>
```

Em Next.js 16:

```jsx
'use client'
import Script from 'next/script'

export function UnicornBg({ projectId }) {
  return (
    <>
      <div
        data-us-project={projectId}
        data-us-scale="1"
        data-us-dpi="1.5"
        className="absolute inset-0 -z-10"
      />
      <Script
        src="https://cdn.jsdelivr.net/gh/hiunicornstudio/unicornstudio.js@v1.4.34/dist/unicornStudio.umd.js"
        strategy="afterInteractive"
        onLoad={() => window.UnicornStudio?.init()}
      />
    </>
  )
}
```

### IDs publicos catalogados (Aura.build)

| ID | Efeito | Vibe |
|----|--------|------|
| `AhqzKk9mZE0EnlENMQDi` | Orange burn | Fogo lento, accent laranja, BG escuro |
| `zNLwDraPwdiE0ELhd8Z4` | Gradient mesh predictive | Mesh roxo-azul fluido (cuidado: slop, customizar) |

Catalogados via Playwright em aura.build (ver `09-aura-build-arsenal.md`).

### Como capturar IDs novos

```js
browser_navigate("https://aura.build/templates/[slug]")
browser_evaluate(`
  const iframe = document.querySelector('iframe')
  const doc = iframe.contentDocument || iframe.contentWindow.document
  return [...doc.querySelectorAll('[data-us-project]')]
    .map(el => el.getAttribute('data-us-project'))
`)
```

## Three.js custom shader

Quando precisa controle (cor da marca exata, parametro reativo a scroll/cursor).

```jsx
'use client'
import { useEffect, useRef } from 'react'
import * as THREE from 'three'

const fragmentShader = `
  uniform float u_time;
  uniform vec2 u_resolution;
  uniform vec3 u_color;

  float noise(vec2 p) {
    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
  }

  void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    float n = noise(uv * 8.0 + u_time * 0.1);
    vec3 col = mix(vec3(0.02), u_color, smoothstep(0.4, 0.8, n));
    gl_FragColor = vec4(col, 1.0);
  }
`

const vertexShader = `
  void main() {
    gl_Position = vec4(position, 1.0);
  }
`

export function ShaderBg({ accent = [0.92, 0.34, 0.05] }) {
  const ref = useRef(null)

  useEffect(() => {
    const renderer = new THREE.WebGLRenderer({
      canvas: ref.current,
      antialias: false,
      alpha: false
    })
    const scene = new THREE.Scene()
    const camera = new THREE.Camera()

    const uniforms = {
      u_time: { value: 0 },
      u_resolution: { value: new THREE.Vector2() },
      u_color: { value: new THREE.Vector3(...accent) }
    }
    const mat = new THREE.ShaderMaterial({ uniforms, vertexShader, fragmentShader })
    const geom = new THREE.PlaneGeometry(2, 2)
    scene.add(new THREE.Mesh(geom, mat))

    const resize = () => {
      const w = window.innerWidth
      const h = window.innerHeight
      renderer.setSize(w, h, false)
      uniforms.u_resolution.value.set(w, h)
    }
    resize()
    window.addEventListener('resize', resize)

    const start = performance.now()
    let raf
    const loop = () => {
      uniforms.u_time.value = (performance.now() - start) / 1000
      renderer.render(scene, camera)
      raf = requestAnimationFrame(loop)
    }
    loop()

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(raf)
      renderer.dispose()
      mat.dispose()
      geom.dispose()
    }
  }, [accent])

  return <canvas ref={ref} className="absolute inset-0 -z-10" />
}
```

## Canvas 2D matrix rain (lightweight ~30KB)

Quando o tom e terminal-cyberpunk e voce quer zero deps WebGL.

```jsx
'use client'
import { useEffect, useRef } from 'react'

export function MatrixRain({ color = '#00FF41', density = 1.0 }) {
  const ref = useRef(null)

  useEffect(() => {
    const canvas = ref.current
    const ctx = canvas.getContext('2d')
    let w = canvas.width = window.innerWidth
    let h = canvas.height = window.innerHeight

    const fontSize = 14
    const cols = Math.floor(w / fontSize)
    const drops = Array(cols).fill(1)
    const chars = 'アイウエオカキクケコサシスセソ0123456789'

    const draw = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'
      ctx.fillRect(0, 0, w, h)
      ctx.fillStyle = color
      ctx.font = `${fontSize}px monospace`

      for (let i = 0; i < cols; i++) {
        const ch = chars[Math.floor(Math.random() * chars.length)]
        ctx.fillText(ch, i * fontSize, drops[i] * fontSize)
        if (drops[i] * fontSize > h && Math.random() > 0.975) drops[i] = 0
        drops[i] += density
      }
    }

    const id = setInterval(draw, 50)
    const onResize = () => {
      w = canvas.width = window.innerWidth
      h = canvas.height = window.innerHeight
    }
    window.addEventListener('resize', onResize)

    return () => {
      clearInterval(id)
      window.removeEventListener('resize', onResize)
    }
  }, [color, density])

  return <canvas ref={ref} className="absolute inset-0 -z-10 bg-black" />
}
```

## Spline (3D scenes ready)

Quando precisa de cena 3D ja modelada (objeto interativo). Pesado: bundle 200KB+ runtime, terrivel em mobile baixo-end.

```jsx
'use client'
import Spline from '@splinetool/react-spline'

export function HeroScene() {
  return (
    <Spline
      scene="https://prod.spline.design/[your-scene-id]/scene.splinecode"
      className="absolute inset-0 -z-10"
    />
  )
}
```

Regras:
- So no hero, NUNCA em pagina inteira
- Mobile: substituir por imagem estatica (next/image priority)
- Lazy: dynamic import com `ssr: false`

## Decision matrix: peso vs efeito vs mobile

| Solucao | Bundle | Mobile | Customizacao | Quando |
|---------|--------|--------|--------------|--------|
| UnicornStudio + ID publico | ~150KB | OK | Baixa (ID fixo) | MVP, hero rapido |
| UnicornStudio custom | ~150KB | OK | Alta (editor visual) | Marca propria |
| Three.js custom shader | ~600KB (tree-shake) | OK c/ DPI 1.5 | Total | Quando UnicornStudio nao basta |
| Spline | ~200KB + cena | Pesado | Visual editor | So hero, so desktop |
| Canvas 2D | ~5KB | Otimo | Total | Tom terminal/retro, lightweight |
| CSS gradient layered | 0KB | Perfeito | Limitada | Fallback / paginas internas |

## Regra final

Nao colocar WebGL em todas paginas. **Hero da home: pesado. Resto: CSS gradient.** Bundle inteiro do Aura.build e 13MB — eles servem 1 bundle pra tudo. Voce nao precisa.
