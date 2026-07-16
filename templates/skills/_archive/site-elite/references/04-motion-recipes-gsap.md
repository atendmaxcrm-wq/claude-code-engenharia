# 04 — Motion Recipes (GSAP)

GSAP virou 100% gratuito em Outubro/2024 (Webflow comprou GreenSock). Inclui ScrollTrigger, SplitText, MorphSVG, Flip, DrawSVG. Zero motivo para nao usar.

## Decision tree: GSAP vs Framer Motion

| Cenario | Lib |
|---------|-----|
| Page-load orchestration coreografada (timeline com 10+ steps) | GSAP |
| Scroll-driven (pin, parallax, scrub) | GSAP ScrollTrigger |
| Text reveal stagger por palavra/letra | GSAP SplitText |
| SVG morph entre 2 paths | GSAP MorphSVG |
| Layout transition (lista reordenando) | GSAP Flip OU Framer Motion layout |
| Component-level enter/exit | Framer Motion (mais ergonomico em React) |
| Drag & drop interativo | Framer Motion |
| Gesture (swipe, pinch) | Framer Motion |

Regra: GSAP para coreografia narrativa pesada. Framer Motion para interacoes componente-locais.

## Receita 1: ScrollTrigger pin section (estilo Aura)

```jsx
'use client'
import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import ScrollTrigger from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export function PinSection() {
  const ref = useRef(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.to('.pin-content', {
        scrollTrigger: {
          trigger: ref.current,
          start: 'top top',
          end: '+=2000',
          pin: true,
          scrub: 1,
          anticipatePin: 1
        },
        xPercent: -100,
        ease: 'none'
      })
    }, ref)
    return () => ctx.revert()
  }, [])

  return (
    <section ref={ref} className="h-screen overflow-hidden">
      <div className="pin-content flex w-[300vw]">
        <div className="w-screen">slide 1</div>
        <div className="w-screen">slide 2</div>
        <div className="w-screen">slide 3</div>
      </div>
    </section>
  )
}
```

## Receita 2: SplitText reveal stagger

```jsx
'use client'
import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { SplitText } from 'gsap/SplitText'

gsap.registerPlugin(SplitText)

export function HeroTitle({ text }) {
  const ref = useRef(null)

  useEffect(() => {
    const split = new SplitText(ref.current, { type: 'words,chars' })
    gsap.from(split.chars, {
      yPercent: 120,
      opacity: 0,
      stagger: 0.02,
      duration: 0.8,
      ease: 'power3.out'
    })
    return () => split.revert()
  }, [text])

  return (
    <h1 ref={ref} className="font-display text-[clamp(3rem,10vw,9rem)] uppercase">
      {text}
    </h1>
  )
}
```

## Receita 3: Page-load orchestration

Uma timeline coreografada > 50 micro-interactions desconectadas.

```jsx
useEffect(() => {
  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })

  tl.from('[data-anim="logo"]', { yPercent: -100, duration: 0.6 })
    .from('[data-anim="nav-item"]', {
      yPercent: -50, opacity: 0, stagger: 0.08, duration: 0.4
    }, '-=0.3')
    .from('[data-anim="hero-title"]', {
      yPercent: 30, opacity: 0, duration: 1
    }, '-=0.2')
    .from('[data-anim="hero-sub"]', {
      yPercent: 20, opacity: 0, duration: 0.7
    }, '-=0.6')
    .from('[data-anim="hero-cta"]', {
      scale: 0.8, opacity: 0, duration: 0.5
    }, '-=0.4')

  return () => tl.kill()
}, [])
```

## Receita 4: Parallax background

```jsx
useEffect(() => {
  gsap.to('[data-parallax]', {
    yPercent: -30,
    ease: 'none',
    scrollTrigger: {
      trigger: '[data-parallax]',
      start: 'top bottom',
      end: 'bottom top',
      scrub: true
    }
  })
}, [])
```

## Receita 5: Horizontal scroll

```jsx
useEffect(() => {
  const sections = gsap.utils.toArray('.h-panel')
  gsap.to(sections, {
    xPercent: -100 * (sections.length - 1),
    ease: 'none',
    scrollTrigger: {
      trigger: '.h-container',
      pin: true,
      scrub: 1,
      end: () => `+=${document.querySelector('.h-container').offsetWidth}`
    }
  })
}, [])
```

## Receita 6: Cursor follow lerp

```jsx
'use client'
import { useEffect, useRef } from 'react'

export function Cursor() {
  const ref = useRef(null)

  useEffect(() => {
    const cursor = ref.current
    const pos = { x: 0, y: 0 }
    const target = { x: 0, y: 0 }
    const speed = 0.15

    const onMove = (e) => {
      target.x = e.clientX
      target.y = e.clientY
    }
    window.addEventListener('mousemove', onMove)

    let raf
    const animate = () => {
      pos.x += (target.x - pos.x) * speed
      pos.y += (target.y - pos.y) * speed
      cursor.style.transform = `translate3d(${pos.x}px, ${pos.y}px, 0)`
      raf = requestAnimationFrame(animate)
    }
    animate()

    return () => {
      window.removeEventListener('mousemove', onMove)
      cancelAnimationFrame(raf)
    }
  }, [])

  return (
    <div
      ref={ref}
      className="pointer-events-none fixed left-0 top-0 z-50 h-4 w-4 rounded-full bg-white mix-blend-difference"
    />
  )
}
```

## Performance

- Sempre `prefers-reduced-motion`:
  ```js
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  ```
- `will-change: transform` so durante a animacao, remover apos
- Usar `transform` e `opacity` (GPU). Evitar animar `width`, `height`, `top`, `left`
- ScrollTrigger.config({ ignoreMobileResize: true }) para evitar re-trigger no scroll mobile (URL bar resize)
- Cleanup obrigatorio com `gsap.context()` + `ctx.revert()` em React StrictMode
