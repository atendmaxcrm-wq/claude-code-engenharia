# Motion System — Upgrade Visual

Biblioteca de animacoes e micro-interacoes com Framer Motion. Spring physics, variants reutilizaveis, e receitas prontas.

---

## 1. Spring Configs (Presets)

```tsx
// lib/motion-presets.ts
export const springs = {
  // Elementos pequenos (botoes, toggles, badges)
  snappy: { type: "spring" as const, stiffness: 400, damping: 25 },

  // Elementos medios (cards, menus, dropdowns)
  smooth: { type: "spring" as const, stiffness: 300, damping: 30 },

  // Elementos grandes (modais, paineis, overlays)
  gentle: { type: "spring" as const, stiffness: 200, damping: 25 },

  // Feedback tatil (tap, press)
  bouncy: { type: "spring" as const, stiffness: 400, damping: 10 },

  // Micro-feedback (checkmarks, icons)
  micro: { type: "spring" as const, stiffness: 500, damping: 30 },
} as const;

// Easing padrao para CSS/duration-based
export const easings = {
  default: [0.25, 0.4, 0.25, 1],       // cubic-bezier padrao premium
  easeOut: [0, 0, 0.2, 1],              // saida suave
  easeInOut: [0.4, 0, 0.2, 1],          // entrada e saida
  springCSS: [0.175, 0.885, 0.32, 1.275], // overshoot sutil
} as const;
```

---

## 2. Variants Reutilizaveis

```tsx
// lib/motion-variants.ts
export const fadeInUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export const fadeIn = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
};

export const scaleIn = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1 },
};

export const slideInLeft = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0 },
};

export const slideInRight = {
  hidden: { opacity: 0, x: 20 },
  visible: { opacity: 1, x: 0 },
};

// Container com stagger para listas
export const staggerContainer = (delay = 0.1) => ({
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: delay },
  },
});

// Wizard slide direction-aware
export const slideVariants = {
  enter: (direction: number) => ({
    x: direction > 0 ? 60 : -60,
    opacity: 0,
  }),
  center: {
    x: 0,
    opacity: 1,
  },
  exit: (direction: number) => ({
    x: direction > 0 ? -60 : 60,
    opacity: 0,
  }),
};

// Modal com backdrop
export const modalVariants = {
  hidden: { opacity: 0, scale: 0.95, y: 20 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { type: "spring", damping: 25, stiffness: 300 },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 20,
    transition: { duration: 0.2 },
  },
};

export const backdropVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 },
};
```

---

## 3. Componentes de Animacao Reutilizaveis

### ScrollReveal

```tsx
import { useRef } from "react";
import { motion, useInView } from "framer-motion";

interface ScrollRevealProps {
  children: React.ReactNode;
  delay?: number;
  y?: number;
  duration?: number;
}

export const ScrollReveal = ({
  children,
  delay = 0,
  y = 20,
  duration = 0.5,
}: ScrollRevealProps) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y }}
      transition={{ duration, delay, ease: [0, 0, 0.2, 1] }}
    >
      {children}
    </motion.div>
  );
};
```

**Regra:** NUNCA usar translateY acima de 20px. NUNCA usar blur no reveal. So opacity + translate.

### StaggerList

```tsx
import { motion } from "framer-motion";

interface StaggerListProps {
  children: React.ReactNode;
  delay?: number;
}

export const StaggerList = ({ children, delay = 0.08 }: StaggerListProps) => (
  <motion.div
    initial="hidden"
    whileInView="visible"
    viewport={{ once: true, margin: "-60px" }}
    variants={{
      hidden: { opacity: 0 },
      visible: { opacity: 1, transition: { staggerChildren: delay } },
    }}
  >
    {children}
  </motion.div>
);

export const StaggerItem = ({ children }: { children: React.ReactNode }) => (
  <motion.div
    variants={{
      hidden: { opacity: 0, y: 12 },
      visible: { opacity: 1, y: 0 },
    }}
    transition={{ duration: 0.4, ease: [0, 0, 0.2, 1] }}
  >
    {children}
  </motion.div>
);
```

---

## 4. Padroes de Interacao

### Hover Premium (card)

```tsx
<motion.div
  whileHover={{ y: -2 }}
  transition={{ type: "spring", stiffness: 400, damping: 25 }}
  style={{
    // card styles...
    transition: "box-shadow 0.4s cubic-bezier(0.25, 0.4, 0.25, 1)",
  }}
  onHoverStart={(e) => {
    e.currentTarget.style.boxShadow =
      "0 8px 30px rgba(0,0,0,0.4), 0 0 40px rgba(231,84,15,0.08)";
  }}
  onHoverEnd={(e) => {
    e.currentTarget.style.boxShadow =
      "0 1px 2px rgba(0,0,0,0.2), 0 4px 16px rgba(0,0,0,0.15)";
  }}
>
```

### Tap/Press Feedback

```tsx
<motion.button
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
>
  Click me
</motion.button>
```

### Celebration (completar tarefa)

```tsx
<motion.div
  initial={{ scale: 0, rotate: -180 }}
  animate={{ scale: 1, rotate: 0 }}
  transition={{ type: "spring", stiffness: 300, damping: 15 }}
>
  <CheckCircleIcon />
</motion.div>
```

### AnimatePresence para Wizard Steps

```tsx
import { AnimatePresence, motion } from "framer-motion";

<AnimatePresence mode="wait" custom={direction}>
  <motion.div
    key={currentStep}
    custom={direction}
    variants={slideVariants}
    initial="enter"
    animate="center"
    exit="exit"
    transition={{ type: "spring", stiffness: 300, damping: 30 }}
  >
    {/* step content */}
  </motion.div>
</AnimatePresence>
```

---

## 5. Regras de Performance

1. **NUNCA animar layout properties** (width, height, top, left). Apenas `transform` e `opacity`
2. **will-change: transform** nos elementos atras de backdrop-filter
3. **Animacoes ambientais (mesh-drift, pulse) = CSS keyframes** (nao Framer Motion)
4. **Animacoes interativas (hover, tap, reveal) = Framer Motion** (spring physics)
5. **Max 30px blur em animados, 50px em estaticos**
6. **Stagger delay max 0.1s** para listas (mais que isso parece lento)
7. **ScrollReveal: 20px translateY, 0.35-0.5s duration** (NUNCA 150px)
8. **NUNCA animate Infinity** em motion.div (GPU thrashing). Usar CSS @keyframes para loops

---

## 6. CSS Scroll-Driven Animations (Alternativa sem JS)

Para reveals simples sem JS (melhor performance, compositor thread):

```css
/* Reveal ao entrar no viewport */
.reveal-scroll {
  animation: fade-up 0.5s ease-out;
  animation-timeline: view();
  animation-range: entry 0% cover 30%;
}

/* Progress bar no scroll da pagina */
.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: var(--accent);
  transform-origin: left;
  animation: grow-x linear;
  animation-timeline: scroll();
}

@keyframes grow-x {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}
```

**Nota:** Scroll-driven animations rodam na compositor thread = 60fps garantido. Preferir para reveals simples. Usar Framer Motion para animacoes interativas complexas.
