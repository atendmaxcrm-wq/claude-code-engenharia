# Recipes — Receitas Prontas de Animacao

Copiar e adaptar. Todos os exemplos usam TypeScript + Next.js App Router.

---

## 1. Pin Section (Secao fixa com animacao interna)

```tsx
"use client";
import { useRef } from "react";
import { gsap, useGSAP, ScrollTrigger } from "@/lib/gsap-config";

export function PinSection() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: sectionRef.current,
        start: "top top",
        end: "+=100%",
        pin: true,
        scrub: 0.5,
        anticipatePin: 1,
      },
    });

    tl.from(".pin-title", { opacity: 0, y: 50 })
      .from(".pin-description", { opacity: 0, y: 30 }, "-=0.3")
      .from(".pin-image", { scale: 0.8, opacity: 0 }, "-=0.2");
  }, { scope: sectionRef });

  return (
    <section ref={sectionRef} style={{ minHeight: "100vh", position: "relative" }}>
      <h2 className="pin-title">Titulo Pinned</h2>
      <p className="pin-description">Descricao aparece no scroll</p>
      <img className="pin-image" src="/hero.jpg" alt="" />
    </section>
  );
}
```

---

## 2. Horizontal Scroll

```tsx
"use client";
import { useRef } from "react";
import { gsap, useGSAP, ScrollTrigger } from "@/lib/gsap-config";

export function HorizontalScroll() {
  const containerRef = useRef<HTMLDivElement>(null);
  const panelsRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    const panels = gsap.utils.toArray<HTMLElement>(".h-panel");
    const totalWidth = panels.length * window.innerWidth;

    gsap.to(panels, {
      xPercent: -100 * (panels.length - 1),
      ease: "none",
      scrollTrigger: {
        trigger: containerRef.current,
        pin: true,
        scrub: 0.5,
        anticipatePin: 1,
        end: () => `+=${totalWidth}`,
        snap: 1 / (panels.length - 1), // Snap entre paineis
      },
    });
  }, { scope: containerRef });

  return (
    <div ref={containerRef} style={{ overflow: "hidden" }}>
      <div ref={panelsRef} style={{ display: "flex", width: "fit-content" }}>
        <div className="h-panel" style={{ width: "100vw", height: "100vh" }}>
          Painel 1
        </div>
        <div className="h-panel" style={{ width: "100vw", height: "100vh" }}>
          Painel 2
        </div>
        <div className="h-panel" style={{ width: "100vw", height: "100vh" }}>
          Painel 3
        </div>
      </div>
    </div>
  );
}
```

---

## 3. Parallax Layers

```tsx
"use client";
import { useRef } from "react";
import { gsap, useGSAP, ScrollTrigger } from "@/lib/gsap-config";

export function ParallaxHero() {
  const heroRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    gsap.to(".parallax-bg", {
      y: -100,
      scrollTrigger: {
        trigger: heroRef.current,
        start: "top top",
        end: "bottom top",
        scrub: 0.5,
      },
    });

    gsap.to(".parallax-mid", {
      y: -50,
      scrollTrigger: {
        trigger: heroRef.current,
        start: "top top",
        end: "bottom top",
        scrub: 0.5,
      },
    });

    // Foreground: sem parallax (velocidade normal)
  }, { scope: heroRef });

  return (
    <div ref={heroRef} style={{ position: "relative", height: "100vh", overflow: "hidden" }}>
      <div className="parallax-bg" style={{ position: "absolute", inset: 0, zIndex: 0 }}>
        {/* Background image */}
      </div>
      <div className="parallax-mid" style={{ position: "absolute", inset: 0, zIndex: 1 }}>
        {/* Middle layer */}
      </div>
      <div style={{ position: "relative", zIndex: 2 }}>
        {/* Foreground content */}
      </div>
    </div>
  );
}
```

---

## 4. Text Split — Char by Char Reveal

```tsx
"use client";
import { useRef } from "react";
import { gsap, useGSAP, SplitText } from "@/lib/gsap-config";

export function TextReveal() {
  const textRef = useRef<HTMLHeadingElement>(null);

  useGSAP(() => {
    const split = new SplitText(textRef.current, {
      type: "chars,words",
    });

    gsap.from(split.chars, {
      opacity: 0,
      y: 20,
      rotateX: -90,
      stagger: 0.02,
      duration: 0.6,
      ease: "back.out(1.7)",
      scrollTrigger: {
        trigger: textRef.current,
        start: "top 80%",
      },
    });

    return () => split.revert(); // OBRIGATORIO: restaurar DOM
  }, { scope: textRef });

  return <h1 ref={textRef}>Texto que revela letra por letra</h1>;
}
```

---

## 5. Text Split — Line Clip Reveal (Mask)

```tsx
"use client";
import { useRef } from "react";
import { gsap, useGSAP, SplitText } from "@/lib/gsap-config";

export function LineClipReveal() {
  const textRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    const split = new SplitText(textRef.current, {
      type: "lines",
      mask: true, // Clip/mask cada linha
    });

    gsap.from(split.lines, {
      yPercent: 100,
      opacity: 0,
      stagger: 0.1,
      duration: 0.8,
      ease: "power3.out",
      scrollTrigger: {
        trigger: textRef.current,
        start: "top 80%",
      },
    });

    return () => split.revert();
  }, { scope: textRef });

  return (
    <div ref={textRef}>
      <p>Cada linha deste paragrafo aparece deslizando de baixo,
      com mascara que esconde o overflow. Efeito premium usado
      em sites premiados.</p>
    </div>
  );
}
```

---

## 6. Scramble/Decode Text

```tsx
"use client";
import { useRef } from "react";
import { gsap, useGSAP } from "@/lib/gsap-config";
import { ScrambleTextPlugin } from "gsap/ScrambleTextPlugin";

export function ScrambleText() {
  const textRef = useRef<HTMLSpanElement>(null);

  useGSAP(() => {
    gsap.to(textRef.current, {
      scrambleText: {
        text: "Texto Final Decodificado",
        chars: "!@#$%&*",
        speed: 0.5,
        revealDelay: 0.3,
      },
      duration: 2,
      ease: "none",
      scrollTrigger: {
        trigger: textRef.current,
        start: "top 80%",
      },
    });
  });

  return <span ref={textRef}>████████████████</span>;
}
```

---

## 7. SVG Draw (Revelar tracos)

```tsx
"use client";
import { useRef } from "react";
import { gsap, useGSAP } from "@/lib/gsap-config";

export function DrawSVGDemo() {
  const svgRef = useRef<SVGSVGElement>(null);

  useGSAP(() => {
    gsap.from(".draw-path", {
      drawSVG: "0%",
      duration: 2,
      stagger: 0.2,
      ease: "power2.inOut",
      scrollTrigger: {
        trigger: svgRef.current,
        start: "top 70%",
      },
    });
  }, { scope: svgRef });

  return (
    <svg ref={svgRef} viewBox="0 0 200 200">
      <circle className="draw-path" cx="100" cy="100" r="80"
        fill="none" stroke="currentColor" strokeWidth="2" />
      <path className="draw-path" d="M60 100 L90 130 L140 70"
        fill="none" stroke="currentColor" strokeWidth="3" />
    </svg>
  );
}
```

---

## 8. SVG Morph

```tsx
"use client";
import { useRef } from "react";
import { gsap, useGSAP } from "@/lib/gsap-config";

export function MorphSVGDemo() {
  const pathRef = useRef<SVGPathElement>(null);

  useGSAP(() => {
    gsap.to(pathRef.current, {
      morphSVG: "#target-shape", // ID do path destino
      duration: 1.5,
      ease: "power2.inOut",
      repeat: -1,
      yoyo: true,
    });
  });

  return (
    <svg viewBox="0 0 200 200">
      <path ref={pathRef} d="M100,20 C140,20 180,60 180,100 ..." fill="currentColor" />
      <path id="target-shape" d="M50,50 L150,50 L150,150 ..." style={{ visibility: "hidden" }} />
    </svg>
  );
}
```

---

## 9. Grid Stagger Wave

```tsx
"use client";
import { useRef } from "react";
import { gsap, useGSAP } from "@/lib/gsap-config";

export function GridWave() {
  const gridRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    gsap.from(".grid-item", {
      scale: 0,
      opacity: 0,
      duration: 0.5,
      ease: "back.out(1.7)",
      stagger: {
        each: 0.05,
        from: "center",
        grid: "auto",
        ease: "power2.inOut",
      },
      scrollTrigger: {
        trigger: gridRef.current,
        start: "top 70%",
      },
    });
  }, { scope: gridRef });

  return (
    <div ref={gridRef} style={{
      display: "grid",
      gridTemplateColumns: "repeat(4, 1fr)",
      gap: "16px",
    }}>
      {Array.from({ length: 16 }).map((_, i) => (
        <div key={i} className="grid-item" style={{
          aspectRatio: "1",
          background: "var(--accent, #e7540f)",
          borderRadius: "12px",
        }} />
      ))}
    </div>
  );
}
```

---

## 10. FLIP Animation (GSAP)

```tsx
"use client";
import { useRef, useState } from "react";
import { gsap, useGSAP, Flip } from "@/lib/gsap-config";

export function FlipDemo() {
  const [expanded, setExpanded] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  function handleClick() {
    // 1. Capturar estado atual
    const state = Flip.getState(cardRef.current);

    // 2. Mudar o layout (toggle class, mover elemento, etc)
    setExpanded(!expanded);

    // 3. Animar do estado antigo para o novo
    requestAnimationFrame(() => {
      Flip.from(state, {
        duration: 0.6,
        ease: "power2.inOut",
        absolute: true,
      });
    });
  }

  return (
    <div
      ref={cardRef}
      onClick={handleClick}
      style={{
        width: expanded ? "100%" : "200px",
        height: expanded ? "400px" : "200px",
        background: "var(--accent)",
        borderRadius: "12px",
        cursor: "pointer",
        transition: "none", // GSAP cuida da transicao
      }}
    />
  );
}
```

---

## 11. Page Transition (Next.js App Router)

```tsx
// components/TransitionLink.tsx
"use client";
import { useRouter } from "next/navigation";
import { gsap } from "@/lib/gsap-config";

interface TransitionLinkProps {
  href: string;
  children: React.ReactNode;
}

export function TransitionLink({ href, children }: TransitionLinkProps) {
  const router = useRouter();

  function handleClick(e: React.MouseEvent) {
    e.preventDefault();

    // Animacao de saida
    const tl = gsap.timeline({
      onComplete: () => router.push(href),
    });

    tl.to(".page-content", {
      opacity: 0,
      y: -30,
      duration: 0.4,
      ease: "power2.in",
    });
  }

  return (
    <a href={href} onClick={handleClick}>
      {children}
    </a>
  );
}

// No layout ou pagina: animacao de entrada
// components/PageWrapper.tsx
"use client";
import { useRef } from "react";
import { gsap, useGSAP } from "@/lib/gsap-config";

export function PageWrapper({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    gsap.from(ref.current, {
      opacity: 0,
      y: 30,
      duration: 0.5,
      ease: "power2.out",
    });
  }, { scope: ref });

  return (
    <div ref={ref} className="page-content">
      {children}
    </div>
  );
}
```

---

## 12. Scroll Progress Bar

```tsx
"use client";
import { useRef } from "react";
import { gsap, useGSAP, ScrollTrigger } from "@/lib/gsap-config";

export function ScrollProgress() {
  const barRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    gsap.to(barRef.current, {
      scaleX: 1,
      ease: "none",
      scrollTrigger: {
        trigger: document.body,
        start: "top top",
        end: "bottom bottom",
        scrub: 0.3,
      },
    });
  });

  return (
    <div
      ref={barRef}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        height: "3px",
        background: "var(--accent, #e7540f)",
        transformOrigin: "left",
        transform: "scaleX(0)",
        zIndex: 9999,
      }}
    />
  );
}
```

---

## 13. Number Counter (Contagem animada)

```tsx
"use client";
import { useRef } from "react";
import { gsap, useGSAP, ScrollTrigger } from "@/lib/gsap-config";

export function Counter({ value, suffix = "" }: { value: number; suffix?: string }) {
  const numRef = useRef<HTMLSpanElement>(null);
  const objRef = useRef({ val: 0 });

  useGSAP(() => {
    gsap.to(objRef.current, {
      val: value,
      duration: 2,
      ease: "power2.out",
      scrollTrigger: {
        trigger: numRef.current,
        start: "top 80%",
      },
      onUpdate: () => {
        if (numRef.current) {
          numRef.current.textContent = Math.round(objRef.current.val) + suffix;
        }
      },
    });
  });

  return <span ref={numRef}>0{suffix}</span>;
}

// Uso: <Counter value={1500} suffix="+" />
```

---

## 14. Reveal Stagger (Cards/Features)

```tsx
"use client";
import { useRef } from "react";
import { gsap, useGSAP } from "@/lib/gsap-config";

export function RevealCards({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    gsap.from(ref.current!.children, {
      y: 40,
      opacity: 0,
      duration: 0.6,
      stagger: 0.1,
      ease: "power2.out",
      scrollTrigger: {
        trigger: ref.current,
        start: "top 80%",
      },
    });
  }, { scope: ref });

  return <div ref={ref}>{children}</div>;
}
```

---

## 15. Magnetic Button (hover atrai cursor)

```tsx
"use client";
import { useRef } from "react";
import { gsap } from "@/lib/gsap-config";

export function MagneticButton({ children }: { children: React.ReactNode }) {
  const btnRef = useRef<HTMLButtonElement>(null);

  function handleMouseMove(e: React.MouseEvent) {
    const btn = btnRef.current!;
    const rect = btn.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;

    gsap.to(btn, {
      x: x * 0.3,
      y: y * 0.3,
      duration: 0.3,
      ease: "power2.out",
    });
  }

  function handleMouseLeave() {
    gsap.to(btnRef.current, {
      x: 0,
      y: 0,
      duration: 0.5,
      ease: "elastic.out(1, 0.3)",
    });
  }

  return (
    <button
      ref={btnRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {children}
    </button>
  );
}
```
