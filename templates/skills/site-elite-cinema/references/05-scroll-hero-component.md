# 05 - Scroll-scrubbed Video Hero (Next.js 16 + GSAP)

Componente React completo para hero scroll-scrubbed: video que avanca conforme o usuario rola a pagina, pin durante o trecho, mobile e desktop com sources diferentes, fallback poster, preload condicional, cleanup em unmount. Inclui variantes (hero curto vs storytelling longo com overlays), integracao com Lenis e gotchas de iOS Safari.

Fontes oficiais:
- https://gsap.com/docs/v3/Plugins/ScrollTrigger/
- https://gsap.com/resources/React/ (useGSAP)
- https://gsap.com/docs/v3/GSAP/gsap.context()/
- https://lenis.darkroom.engineering/
- https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video

## Setup

```bash
npm install gsap @gsap/react
# opcional, scroll suave:
npm install lenis
```

GSAP virou 100% gratuito em outubro/2024 (Webflow comprou GreenSock), entao ScrollTrigger e qualquer plugin sao livres.

## Componente canonico: ScrollVideoHero.tsx

```tsx
'use client';

import { useRef } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(useGSAP, ScrollTrigger);

type Source = { src: string; type: string; media?: string };

interface Props {
  sources: Source[];
  poster: string;
  pinDistance?: string;
  scrub?: number | boolean;
  className?: string;
}

export function ScrollVideoHero({
  sources,
  poster,
  pinDistance = '+=2000',
  scrub = 0.3,
  className = '',
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useGSAP(
    () => {
      const video = videoRef.current;
      const container = containerRef.current;
      if (!video || !container) return;

      const onMeta = () => {
        const tween = gsap.to(video, {
          currentTime: video.duration || 1,
          ease: 'none',
          scrollTrigger: {
            trigger: container,
            start: 'top top',
            end: pinDistance,
            scrub,
            pin: true,
            anticipatePin: 1,
            invalidateOnRefresh: true,
          },
        });

        return () => {
          tween.scrollTrigger?.kill();
          tween.kill();
        };
      };

      if (video.readyState >= 1) {
        return onMeta();
      }
      video.addEventListener('loadedmetadata', onMeta, { once: true });
      return () => video.removeEventListener('loadedmetadata', onMeta);
    },
    { scope: containerRef }
  );

  return (
    <section ref={containerRef} className={`relative h-screen w-full overflow-hidden ${className}`}>
      <video
        ref={videoRef}
        poster={poster}
        muted
        playsInline
        preload="auto"
        crossOrigin="anonymous"
        className="absolute inset-0 h-full w-full object-cover"
      >
        {sources.map((s) => (
          <source key={s.src} src={s.src} type={s.type} media={s.media} />
        ))}
      </video>
    </section>
  );
}
```

## Pontos chave

### Esperar `loadedmetadata`

Sem `video.duration` real, `gsap.to(video, { currentTime: video.duration })` calcula `NaN` e o tween nunca acontece. O evento `loadedmetadata` dispara assim que o browser le o header do MP4. `readyState >= 1` cobre o caso de o metadata ja estar pronto antes do effect rodar.

### scrub: 0.3 (default recomendado)

| Valor | Comportamento |
|-------|---------------|
| `scrub: true` | Video gruda no scroll (frame-perfect, pode parecer "duro") |
| `scrub: 0.3` | Suavidade 300ms de catch-up (default que recomendamos) |
| `scrub: 1` | Suavidade 1s (lento demais para hero curto) |

Comecar com `0.3`, ajustar conforme o ritmo do site.

### pin + anticipatePin

`pin: true` trava o container no viewport durante o trecho. `anticipatePin: 1` pre-calcula o pin um frame antes para evitar "jump" visivel quando o scroll cruza o trigger.

### invalidateOnRefresh

Quando o usuario gira o device ou redimensiona, ScrollTrigger recalcula tudo. Sem `invalidateOnRefresh`, posicoes ficam erradas apos resize.

## Sources duplas (mobile + desktop)

```tsx
<ScrollVideoHero
  poster="/hero/poster.jpg"
  sources={[
    { src: '/hero/hero-mobile.mp4',  type: 'video/mp4', media: '(max-width: 768px)' },
    { src: '/hero/hero-desktop.mp4', type: 'video/mp4', media: '(min-width: 769px)' },
  ]}
/>
```

Browser escolhe um `<source>` baseado em `media`. Resultado: mobile baixa 2-3MB, desktop baixa 5-8MB. Sem isso, mobile baixaria o desktop inteiro.

WebM como fallback bonus para Chrome/Firefox:

```tsx
sources={[
  { src: '/hero/hero-mobile.webm',  type: 'video/webm', media: '(max-width: 768px)' },
  { src: '/hero/hero-mobile.mp4',   type: 'video/mp4',  media: '(max-width: 768px)' },
  { src: '/hero/hero-desktop.webm', type: 'video/webm', media: '(min-width: 769px)' },
  { src: '/hero/hero-desktop.mp4',  type: 'video/mp4',  media: '(min-width: 769px)' },
]}
```

## IntersectionObserver para preload condicional

Hero do topo da pagina: `preload="auto"` resolve. Section accent video la embaixo: vale preload so quando proximo do viewport.

```tsx
'use client';

import { useEffect, useRef, useState } from 'react';

export function LazyScrollVideo(props: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => entry.isIntersecting && setVisible(true),
      { rootMargin: '200% 0px' } // pre-carrega 2 viewports antes
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  return <div ref={ref}>{visible ? <ScrollVideoHero {...props} /> : null}</div>;
}
```

## Variante: storytelling longo com overlays sincronizados

Hero curto = 8s, scrub direto. Storytelling = section pinada com 3-4 text overlays aparecendo em momentos especificos.

```tsx
'use client';

import { useRef } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(useGSAP, ScrollTrigger);

export function ScrollStoryHero({ src, poster }: { src: string; poster: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useGSAP(
    () => {
      const video = videoRef.current!;
      const setup = () => {
        const tl = gsap.timeline({
          scrollTrigger: {
            trigger: containerRef.current,
            start: 'top top',
            end: '+=3000',
            scrub: 0.3,
            pin: true,
            anticipatePin: 1,
          },
        });

        tl.to(video, { currentTime: video.duration, ease: 'none' }, 0);
        tl.fromTo('[data-overlay="1"]', { opacity: 0, y: 30 }, { opacity: 1, y: 0 }, 0.1)
          .to('[data-overlay="1"]', { opacity: 0, y: -30 }, 0.3)
          .fromTo('[data-overlay="2"]', { opacity: 0, y: 30 }, { opacity: 1, y: 0 }, 0.35)
          .to('[data-overlay="2"]', { opacity: 0, y: -30 }, 0.6)
          .fromTo('[data-overlay="3"]', { opacity: 0, y: 30 }, { opacity: 1, y: 0 }, 0.65)
          .to('[data-overlay="3"]', { opacity: 0, y: -30 }, 0.9);
      };
      if (video.readyState >= 1) setup();
      else video.addEventListener('loadedmetadata', setup, { once: true });
    },
    { scope: containerRef }
  );

  return (
    <section ref={containerRef} className="relative h-screen w-full overflow-hidden">
      <video
        ref={videoRef}
        src={src}
        poster={poster}
        muted
        playsInline
        preload="auto"
        crossOrigin="anonymous"
        className="absolute inset-0 h-full w-full object-cover"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
      <div className="absolute inset-0 flex items-center justify-center">
        <h2 data-overlay="1" className="text-6xl font-serif text-white opacity-0">capitulo 1</h2>
        <h2 data-overlay="2" className="absolute text-6xl font-serif text-white opacity-0">capitulo 2</h2>
        <h2 data-overlay="3" className="absolute text-6xl font-serif text-white opacity-0">capitulo 3</h2>
      </div>
    </section>
  );
}
```

`pin: true` com `end: '+=3000'` reserva 3000px de scroll para o storytelling. Cada overlay aparece num "tempo normalizado" (0 = inicio, 1 = fim).

## Integracao com Lenis (scroll suave)

Lenis e o scroll-smoother mais comum em sites premium. Precisa sincronizar com o ticker do GSAP.

```tsx
'use client';

import { useEffect } from 'react';
import Lenis from 'lenis';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function SmoothScroll({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const lenis = new Lenis({ duration: 1.2 });
    lenis.on('scroll', ScrollTrigger.update);
    const tick = (time: number) => lenis.raf(time * 1000);
    gsap.ticker.add(tick);
    gsap.ticker.lagSmoothing(0);
    return () => {
      gsap.ticker.remove(tick);
      lenis.destroy();
    };
  }, []);

  return <>{children}</>;
}
```

Wrap o app inteiro: `<SmoothScroll>{children}</SmoothScroll>` no `app/layout.tsx`. ScrollTrigger atualiza automaticamente em cada frame do Lenis.

## iOS Safari quirks

1. `playsInline` e `muted` sao obrigatorios para autoplay.
2. `crossOrigin="anonymous"` necessario se hospedar video em CDN diferente.
3. Battery saver mode pode pausar autoplay; scrub manual (currentTime) continua funcionando.
4. Existe bug antigo onde Safari nao decodifica video apos a aba ficar idle 5+ min; setar `video.currentTime = video.currentTime` (no-op aparente) forca re-decode.
5. Video tem que ser encodado com `-g 1` (ver 04-ffmpeg-scrub.md). Sem isso, scrub em iOS trava.

## Cleanup automatico via useGSAP

`@gsap/react` faz cleanup automatico via `gsap.context()`. Em StrictMode (dev), o hook desmonta/remonta - sem `useGSAP`, scrolltriggers acumulam. Sempre usar `useGSAP({ scope })` ao inves de `useEffect`.

## Uso completo no app/page.tsx

```tsx
import { ScrollVideoHero } from '@/components/ScrollVideoHero';
import { SmoothScroll } from '@/components/SmoothScroll';

export default function HomePage() {
  return (
    <SmoothScroll>
      <ScrollVideoHero
        poster="/hero/poster.jpg"
        sources={[
          { src: '/hero/hero-mobile.mp4',  type: 'video/mp4', media: '(max-width: 768px)' },
          { src: '/hero/hero-desktop.mp4', type: 'video/mp4', media: '(min-width: 769px)' },
        ]}
        pinDistance="+=2000"
        scrub={0.3}
      />

      <section className="min-h-screen px-8 py-32">
        <h2 className="text-5xl font-serif">Conteudo abaixo do hero</h2>
      </section>
    </SmoothScroll>
  );
}
```

## Anti-pattern

```tsx
// SLOP - sem useGSAP, sem loadedmetadata, sem media query
useEffect(() => {
  gsap.to(videoRef.current, {
    currentTime: videoRef.current.duration, // NaN no primeiro render
    scrollTrigger: { trigger: ref.current, scrub: true },
  });
}, []);
```

```tsx
// SIGNAL - useGSAP, loadedmetadata, scrub: 0.3, pin
useGSAP(() => {
  const v = videoRef.current;
  const start = () => gsap.to(v, {
    currentTime: v.duration,
    ease: 'none',
    scrollTrigger: { trigger: ref.current, start: 'top top', end: '+=2000', scrub: 0.3, pin: true },
  });
  v.readyState >= 1 ? start() : v.addEventListener('loadedmetadata', start, { once: true });
}, { scope: ref });
```
