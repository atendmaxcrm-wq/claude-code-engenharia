# Component Recipes — Upgrade Visual

Receitas prontas de componentes React premium. Copiar e adaptar.

---

## 1. GlassCard (Card Premium Reutilizavel)

```tsx
import { motion } from "framer-motion";

interface GlassCardProps {
  children: React.ReactNode;
  hover?: boolean;
  className?: string;
}

export const GlassCard = ({ children, hover = true, className = "" }: GlassCardProps) => (
  <motion.div
    whileHover={hover ? { y: -2 } : undefined}
    transition={{ type: "spring", stiffness: 400, damping: 25 }}
    style={{
      background: "rgba(24, 24, 27, 0.7)",
      backdropFilter: "blur(16px) saturate(120%)",
      WebkitBackdropFilter: "blur(16px) saturate(120%)",
      border: "1px solid rgba(255, 255, 255, 0.06)",
      borderRadius: 16,
      padding: 24,
      boxShadow: [
        "0 1px 2px rgba(0,0,0,0.2)",
        "0 4px 16px rgba(0,0,0,0.15)",
        "0 16px 48px rgba(0,0,0,0.1)",
        "inset 0 1px 0 rgba(255,255,255,0.03)",
      ].join(", "),
      transition: "box-shadow 0.4s cubic-bezier(0.25, 0.4, 0.25, 1)",
    }}
    className={className}
  >
    {children}
  </motion.div>
);
```

---

## 2. PremiumButton (CTA com Glow)

```tsx
import { motion } from "framer-motion";

interface PremiumButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "ghost";
  fullWidth?: boolean;
}

export const PremiumButton = ({
  children,
  onClick,
  variant = "primary",
  fullWidth = false,
}: PremiumButtonProps) => {
  const styles = {
    primary: {
      background: "linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%)",
      color: "#fff",
      border: "none",
    },
    secondary: {
      background: "rgba(255,255,255,0.03)",
      color: "var(--text-primary)",
      border: "1px solid rgba(255,255,255,0.10)",
    },
    ghost: {
      background: "transparent",
      color: "var(--text-secondary)",
      border: "1px solid transparent",
    },
  };

  return (
    <motion.button
      whileHover={{ scale: 1.02, y: -1 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
      onClick={onClick}
      style={{
        ...styles[variant],
        borderRadius: 12,
        padding: "12px 24px",
        fontSize: 15,
        fontWeight: 600,
        cursor: "pointer",
        width: fullWidth ? "100%" : "auto",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {children}
    </motion.button>
  );
};
```

---

## 3. PremiumInput (Input com Focus Ring Accent)

```tsx
"use client";
import { useState } from "react";

interface PremiumInputProps {
  label: string;
  placeholder?: string;
  type?: string;
  value: string;
  onChange: (v: string) => void;
}

export const PremiumInput = ({
  label,
  placeholder,
  type = "text",
  value,
  onChange,
}: PremiumInputProps) => {
  const [focused, setFocused] = useState(false);

  return (
    <div>
      <label
        style={{
          display: "block",
          fontSize: 13,
          fontWeight: 500,
          color: focused ? "var(--accent-light)" : "var(--text-secondary)",
          marginBottom: 6,
          letterSpacing: "0.02em",
          transition: "color 0.2s ease",
        }}
      >
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        style={{
          width: "100%",
          padding: "14px 18px",
          fontSize: 15,
          color: "var(--text-primary)",
          background: focused ? "var(--accent-glow)" : "rgba(255,255,255,0.03)",
          border: `1px solid ${focused ? "var(--accent)" : "rgba(255,255,255,0.10)"}`,
          borderRadius: 12,
          outline: "none",
          boxShadow: focused ? "0 0 0 3px rgba(231,84,15,0.1)" : "none",
          transition: "all 0.25s cubic-bezier(0.25, 0.4, 0.25, 1)",
        }}
      />
    </div>
  );
};
```

---

## 4. SkeletonLoader (Shimmer Premium)

```tsx
export const SkeletonLine = ({
  width = "100%",
  height = 16,
  delay = 0,
}: {
  width?: string | number;
  height?: number;
  delay?: number;
}) => (
  <div
    style={{
      width,
      height,
      borderRadius: 8,
      background: "linear-gradient(90deg, #1a1a1a 25%, #262626 50%, #1a1a1a 75%)",
      backgroundSize: "200% 100%",
      animation: `shimmer 1.5s infinite ${delay}s`,
    }}
  />
);

export const SkeletonCard = () => (
  <div
    style={{
      background: "rgba(24,24,27,0.6)",
      border: "1px solid rgba(255,255,255,0.06)",
      borderRadius: 16,
      padding: 24,
      display: "flex",
      flexDirection: "column",
      gap: 12,
    }}
  >
    <SkeletonLine width="60%" height={20} />
    <SkeletonLine width="100%" delay={0.1} />
    <SkeletonLine width="80%" delay={0.2} />
    <SkeletonLine width="40%" height={12} delay={0.3} />
  </div>
);
```

---

## 5. ScrollReveal (Fade-Up no Scroll)

```tsx
"use client";
import { useRef } from "react";
import { motion, useInView } from "framer-motion";

interface ScrollRevealProps {
  children: React.ReactNode;
  delay?: number;
  y?: number;
}

export const ScrollReveal = ({ children, delay = 0, y = 20 }: ScrollRevealProps) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y }}
      transition={{ duration: 0.5, delay, ease: [0, 0, 0.2, 1] }}
    >
      {children}
    </motion.div>
  );
};
```

---

## 6. SectionLabel (Titulo de Secao com Linha)

```tsx
interface SectionLabelProps {
  children: React.ReactNode;
  icon?: React.ReactNode;
}

export const SectionLabel = ({ children, icon }: SectionLabelProps) => (
  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
    {icon && (
      <div style={{ color: "var(--accent)", fontSize: 16 }}>{icon}</div>
    )}
    <span
      style={{
        fontSize: 11,
        fontWeight: 700,
        textTransform: "uppercase",
        letterSpacing: "0.2em",
        color: "var(--text-muted)",
        whiteSpace: "nowrap",
      }}
    >
      {children}
    </span>
    <div
      style={{
        flex: 1,
        height: 1,
        background: "linear-gradient(90deg, rgba(255,255,255,0.10), transparent)",
      }}
    />
  </div>
);
```

---

## 7. Badge (Variantes Semanticas)

```tsx
interface BadgeProps {
  children: React.ReactNode;
  variant?: "accent" | "success" | "warning" | "error" | "neutral";
}

const badgeColors = {
  accent: { bg: "rgba(231,84,15,0.1)", color: "#FF7A3D", border: "rgba(231,84,15,0.2)" },
  success: { bg: "rgba(34,197,94,0.1)", color: "#4ade80", border: "rgba(34,197,94,0.2)" },
  warning: { bg: "rgba(234,179,8,0.1)", color: "#fbbf24", border: "rgba(234,179,8,0.2)" },
  error: { bg: "rgba(239,68,68,0.1)", color: "#f87171", border: "rgba(239,68,68,0.2)" },
  neutral: { bg: "rgba(255,255,255,0.05)", color: "#a1a1aa", border: "rgba(255,255,255,0.10)" },
};

export const Badge = ({ children, variant = "neutral" }: BadgeProps) => {
  const c = badgeColors[variant];
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        padding: "5px 14px",
        borderRadius: 9999,
        fontSize: 11,
        fontWeight: 700,
        textTransform: "uppercase",
        letterSpacing: "0.1em",
        background: c.bg,
        color: c.color,
        border: `1px solid ${c.border}`,
      }}
    >
      {children}
    </span>
  );
};
```

---

## 8. CircularProgress (SVG Ring)

```tsx
"use client";
import { motion } from "framer-motion";

interface CircularProgressProps {
  value: number;       // 0-100
  size?: number;
  strokeWidth?: number;
  color?: string;
  label?: string;
}

export const CircularProgress = ({
  value,
  size = 120,
  strokeWidth = 8,
  color = "var(--accent)",
  label,
}: CircularProgressProps) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div style={{ position: "relative", width: size, height: size }}>
      <svg
        width={size}
        height={size}
        style={{ transform: "rotate(-90deg)" }}
      >
        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth={strokeWidth}
        />
        {/* Progress */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: [0.4, 0, 0.2, 1] }}
        />
      </svg>
      {label && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: size * 0.22,
            fontWeight: 700,
            color: "var(--text-primary)",
          }}
        >
          {label}
        </div>
      )}
    </div>
  );
};
```

---

## 9. GradientMeshBg (Background Decorativo)

```tsx
export const GradientMeshBg = ({
  accentColor = "rgba(231, 84, 15, 0.08)",
  animated = false,
}: {
  accentColor?: string;
  animated?: boolean;
}) => (
  <div
    style={{
      position: "fixed",
      inset: 0,
      zIndex: 0,
      pointerEvents: "none",
      background: [
        `radial-gradient(ellipse 80% 50% at 20% 40%, ${accentColor}, transparent)`,
        "radial-gradient(ellipse 60% 40% at 80% 20%, rgba(59, 130, 246, 0.05), transparent)",
        "radial-gradient(ellipse 50% 50% at 50% 80%, rgba(139, 92, 246, 0.04), transparent)",
      ].join(", "),
      backgroundSize: animated ? "200% 200%, 200% 200%, 200% 200%" : undefined,
      animation: animated ? "mesh-drift 45s ease-in-out infinite" : undefined,
    }}
  />
);
```

---

## 10. DecorativeBlur (Blob Shape)

```tsx
interface DecorativeBlurProps {
  color?: string;
  size?: number;
  top?: string;
  left?: string;
  right?: string;
  bottom?: string;
}

export const DecorativeBlur = ({
  color = "rgba(231, 84, 15, 0.12)",
  size = 300,
  top,
  left,
  right,
  bottom,
}: DecorativeBlurProps) => (
  <div
    aria-hidden="true"
    style={{
      position: "absolute",
      width: size,
      height: size,
      background: color,
      filter: "blur(50px)",
      borderRadius: "50%",
      pointerEvents: "none",
      zIndex: 0,
      top,
      left,
      right,
      bottom,
    }}
  />
);
```

---

## 11. NavButton (Botao Circular de Navegacao)

```tsx
import { motion } from "framer-motion";

interface NavButtonProps {
  onClick: () => void;
  disabled?: boolean;
  children: React.ReactNode;
}

export const NavButton = ({ onClick, disabled, children }: NavButtonProps) => (
  <motion.button
    whileHover={disabled ? undefined : { scale: 1.05 }}
    whileTap={disabled ? undefined : { scale: 0.95 }}
    onClick={onClick}
    disabled={disabled}
    style={{
      width: 40,
      height: 40,
      borderRadius: "50%",
      border: "1.5px solid rgba(255,255,255,0.10)",
      background: "var(--surface)",
      color: disabled ? "rgba(255,255,255,0.15)" : "var(--text-muted)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      cursor: disabled ? "not-allowed" : "pointer",
      opacity: disabled ? 0.25 : 1,
      transition: "all 0.3s cubic-bezier(0.25, 0.4, 0.25, 1)",
    }}
  >
    {children}
  </motion.button>
);
```

---

## 12. RatingBar (Barra de Score Colorida)

```tsx
import { motion } from "framer-motion";

interface RatingBarProps {
  value: number;     // 0-100
  color: string;
  label: string;
  delay?: number;
}

export const RatingBar = ({ value, color, label, delay = 0 }: RatingBarProps) => (
  <div>
    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
      <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>{label}</span>
      <span style={{ fontSize: 13, fontWeight: 600, color, fontVariantNumeric: "tabular-nums" }}>
        {value}%
      </span>
    </div>
    <div
      style={{
        height: 8,
        borderRadius: 4,
        background: "rgba(255,255,255,0.05)",
        overflow: "hidden",
      }}
    >
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${value}%` }}
        transition={{ duration: 0.8, delay, ease: [0.4, 0, 0.2, 1] }}
        style={{ height: "100%", borderRadius: 4, background: color }}
      />
    </div>
  </div>
);
```
