# Templates de Componentes

Estrutura base de cada componente. Adaptar nomes, categorias e textos por projeto.

---

## page.tsx (Orquestrador)

```tsx
"use client";

import { useState, useRef, useCallback } from "react";
import { AnimatePresence, motion } from "framer-motion";
import DiagnosticWizard from "../components/DiagnosticWizard";
import LoadingAnalysis from "../components/LoadingAnalysis";
import ResultView from "../components/ResultView";

type AppState = "form" | "loading" | "streaming" | "result";

export default function Home() {
  const [state, setState] = useState<AppState>("form");
  const [ratings, setRatings] = useState<Record<string, number>>({});
  const [analysis, setAnalysis] = useState("");
  const abortRef = useRef<AbortController | null>(null);

  function handleRatingChange(id: string, value: number) {
    setRatings((prev) => ({ ...prev, [id]: value }));
  }

  const handleSubmit = useCallback(async () => {
    setState("loading");
    setAnalysis("");
    const loadingStart = Date.now();

    try {
      abortRef.current = new AbortController();
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ratings }),
        signal: abortRef.current.signal,
      });

      if (!res.ok) throw new Error("Falha na analise");

      // Garantir pelo menos 2s de loading
      const elapsed = Date.now() - loadingStart;
      if (elapsed < 2000) {
        await new Promise((r) => setTimeout(r, 2000 - elapsed));
      }

      setState("streaming");

      const reader = res.body?.getReader();
      if (!reader) throw new Error("Stream nao disponivel");
      const decoder = new TextDecoder();
      let accumulated = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        accumulated += decoder.decode(value, { stream: true });
        setAnalysis(accumulated);
      }

      setState("result");
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") return;
      alert("Erro ao gerar diagnostico. Tente novamente.");
      setState("form");
    }
  }, [ratings]);

  function handleReset() {
    if (abortRef.current) abortRef.current.abort();
    setRatings({});
    setAnalysis("");
    setState("form");
  }

  return (
    <AnimatePresence mode="wait">
      {state === "form" && (
        <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}>
          <DiagnosticWizard ratings={ratings} onRatingChange={handleRatingChange} onSubmit={handleSubmit} />
        </motion.div>
      )}
      {state === "loading" && (
        <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}>
          <LoadingAnalysis />
        </motion.div>
      )}
      {(state === "streaming" || state === "result") && (
        <motion.div key="result" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.4 }}>
          <ResultView analysis={analysis} ratings={ratings} onReset={handleReset} isStreaming={state === "streaming"} />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

---

## layout.tsx

```tsx
import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
});

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  style: ["normal", "italic"],
});

export const metadata: Metadata = {
  title: "TITULO | Makewl",
  description: "DESCRICAO",
  icons: { icon: "/favicon.ico", apple: "/apple-touch-icon.png" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body className={`${inter.variable} ${playfair.variable} antialiased`}>{children}</body>
    </html>
  );
}
```

---

## MakewlLogo.tsx

Componente de logo responsivo. Usa `/logo-makewl.png` (2528x490px, aspect ratio 5.16:1).

```tsx
"use client";

import { motion } from "framer-motion";
import Image from "next/image";

const ASPECT_RATIO = 5.16; // 2528 / 490
const HEIGHTS = { sm: 24, md: 32, lg: 44 };

interface MakewlLogoProps {
  size?: "sm" | "md" | "lg";
}

export default function MakewlLogo({ size = "md" }: MakewlLogoProps) {
  const h = HEIGHTS[size];
  const w = Math.round(h * ASPECT_RATIO);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <Image
        src="/logo-makewl.png"
        alt="Makewl"
        width={w}
        height={h}
        className="w-auto"
        style={{ height: h }}
        priority
      />
    </motion.div>
  );
}
```

---

## MakewlHeader.tsx

Header premium padrao Makewl. Usado na primeira tela de formularios/diagnosticos.
Baseado no design de producao de arquetipo.assessoriamakewl.com.br.

**Elementos:**
1. Logo com linhas accent de cada lado
2. Titulo com palavra-chave em italico serif (Playfair Display) e cor accent-light
3. Subtitulo muted
4. Ornamento divisor (linhas gradiente + losango accent)

```tsx
"use client";

import { motion } from "framer-motion";
import Image from "next/image";

interface MakewlHeaderProps {
  /** Texto antes da palavra-chave. Ex: "Descubra seu" */
  titlePrefix: string;
  /** Palavra em italico serif com cor accent. Ex: "Arquetipo" */
  titleKeyword: string;
  /** Subtitulo muted abaixo do titulo. Ex: "15 perguntas · resultado com IA" */
  subtitle: string;
}

const ease = [0.25, 0.46, 0.45, 0.94];

export default function MakewlHeader({ titlePrefix, titleKeyword, subtitle }: MakewlHeaderProps) {
  return (
    <div className="text-center" style={{ marginBottom: 20 }}>
      {/* Logo com linhas accent */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.5 }}
        className="flex items-center justify-center gap-3"
        style={{ marginBottom: 20 }}
      >
        <div className="w-8 h-px bg-[var(--color-accent)] opacity-50" />
        <Image
          src="/logo-makewl.png"
          alt="Makewl"
          width={130}
          height={25}
          className="h-5 w-auto"
          priority
        />
        <div className="w-8 h-px bg-[var(--color-accent)] opacity-50" />
      </motion.div>

      {/* Titulo com palavra-chave em italico serif */}
      <motion.h1
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, duration: 0.5, ease }}
        className="font-light text-[var(--color-text-primary)] leading-[1.1] tracking-[-0.02em]"
        style={{ fontSize: "clamp(28px, 6vw, 48px)", marginBottom: 12 }}
      >
        {titlePrefix}{" "}
        <em
          className="font-normal"
          style={{
            fontFamily: "var(--font-playfair), serif",
            fontStyle: "italic",
            fontSize: "1.15em",
            color: "var(--color-accent-light)",
          }}
        >
          {titleKeyword}
        </em>
      </motion.h1>

      {/* Subtitulo */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.25, duration: 0.4 }}
        style={{
          fontSize: 13,
          color: "var(--color-text-muted)",
          opacity: 0.45,
          letterSpacing: "0.08em",
          fontWeight: 300,
        }}
      >
        {subtitle}
      </motion.p>

      {/* Ornamento divisor */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.5 }}
        className="flex items-center justify-center gap-2.5"
        style={{ marginTop: 18 }}
      >
        <span
          className="block h-px w-[60px]"
          style={{ background: "linear-gradient(90deg, transparent, rgba(231,84,15,0.25), transparent)" }}
        />
        <i
          className="block w-[5px] h-[5px] bg-[var(--color-accent)] rotate-45 opacity-60 flex-shrink-0"
        />
        <span
          className="block h-px w-[60px]"
          style={{ background: "linear-gradient(90deg, transparent, rgba(231,84,15,0.25), transparent)" }}
        />
      </motion.div>
    </div>
  );
}
```

**Uso:**
```tsx
<MakewlHeader
  titlePrefix="Descubra seu"
  titleKeyword="Arquetipo"
  subtitle="15 perguntas &middot; resultado personalizado com IA"
/>

<MakewlHeader
  titlePrefix="Diagnostico para"
  titleKeyword="Clinicas"
  subtitle="13 categorias &middot; analise estrategica com IA"
/>
```

---

## StarRating.tsx

```tsx
"use client";

import { motion } from "framer-motion";
import { Star } from "lucide-react";

interface StarRatingProps {
  value: number;
  onChange: (value: number) => void;
  max?: number;
}

export default function StarRating({ value, onChange, max = 4 }: StarRatingProps) {
  return (
    <div className="flex items-center gap-3">
      {Array.from({ length: max }, (_, i) => {
        const starValue = i + 1;
        const isFilled = starValue <= value;
        return (
          <motion.button key={i} type="button"
            onClick={() => onChange(starValue === value ? 0 : starValue)}
            whileTap={{ scale: 0.8 }}
            className="relative cursor-pointer p-1 focus:outline-none"
            aria-label={`${starValue} estrela${starValue > 1 ? "s" : ""}`}
          >
            <motion.div
              animate={isFilled ? { scale: [1, 1.4, 1], rotate: [0, -15, 15, 0] } : { scale: 1, rotate: 0 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              whileHover={{ scale: 1.2 }}
            >
              <Star size={40} strokeWidth={1.5}
                className={`transition-all duration-300 ${
                  isFilled ? "fill-star-filled text-star-filled star-glow" : "fill-transparent text-star-empty hover:text-star-hover"
                }`}
              />
            </motion.div>
            <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 + i * 0.05 }}
              className="mt-1 block text-center text-[10px] font-medium text-muted"
            >
              {starValue}
            </motion.span>
          </motion.button>
        );
      })}
    </div>
  );
}
```

---

## LoadingAnalysis.tsx

```tsx
"use client";

import { motion } from "framer-motion";

const STEPS = [
  "Analisando suas avaliacoes",
  "Identificando areas criticas",
  "Mapeando interdependencias",
  "Elaborando recomendacoes",
  "Gerando diagnostico personalizado",
];

export default function LoadingAnalysis() {
  return (
    <div className="gradient-mesh flex min-h-screen flex-col items-center justify-center px-4">
      {/* Logo Makewl */}
      <div style={{ marginBottom: 40 }}>
        <MakewlLogo size="sm" />
      </div>

      {/* Pulsing orb */}
      <div className="relative mb-10">
        <motion.div className="h-20 w-20 rounded-full bg-accent/20"
          animate={{ scale: [1, 1.4, 1], opacity: [0.3, 0.1, 0.3] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div className="absolute inset-2 rounded-full bg-accent/30"
          animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.2, 0.5] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.3 }}
        />
        <motion.div className="absolute inset-4 rounded-full bg-accent/60"
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
        />
      </div>

      {/* Steps cycling */}
      <div className="relative h-6 w-64 overflow-hidden">
        {STEPS.map((step, i) => (
          <motion.p key={step} className="absolute inset-0 text-center text-sm text-muted"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: [0, 1, 1, 0], y: [20, 0, 0, -20] }}
            transition={{ duration: 2.5, delay: i * 2.5, repeat: Infinity, repeatDelay: (STEPS.length - 1) * 2.5, ease: "easeInOut" }}
          >
            {step}...
          </motion.p>
        ))}
      </div>

      {/* Dots loader */}
      <div className="mt-8 flex gap-1.5">
        {[0, 1, 2].map((i) => (
          <motion.div key={i} className="h-1.5 w-1.5 rounded-full bg-muted"
            animate={{ opacity: [0.2, 1, 0.2] }}
            transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
          />
        ))}
      </div>
    </div>
  );
}
```

---

## API Route Template (api/analyze/route.ts)

```typescript
import { NextResponse } from "next/server";
import OpenAI from "openai";
import { readFileSync } from "fs";
import { join } from "path";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const promptsDir = join(process.cwd(), "prompts");
const systemPrompt = readFileSync(join(promptsDir, "prompt-TEMA.md"), "utf-8");
const knowledgeBase = readFileSync(join(promptsDir, "kb-TEMA.md"), "utf-8");

const CATEGORY_NAMES: Record<string, string> = {
  // PREENCHER com id → nome display
};

function classifyRating(value: number) {
  if (value === 1) return { label: "CRITICO", severity: "critico" };
  if (value === 2) return { label: "URGENTE", severity: "urgente" };
  if (value === 3) return { label: "ATENCAO", severity: "atencao" };
  return { label: "EXCELENTE", severity: "excelente" };
}

export async function POST(request: Request) {
  try {
    const { ratings } = await request.json();

    if (!ratings || typeof ratings !== "object") {
      return NextResponse.json({ error: "Ratings sao obrigatorios" }, { status: 400 });
    }

    const entries = Object.entries(ratings) as [string, number][];
    const totalCategories = Object.keys(CATEGORY_NAMES).length;

    if (entries.length !== totalCategories) {
      return NextResponse.json({ error: `Todas as ${totalCategories} categorias devem ser avaliadas` }, { status: 400 });
    }

    const avg = entries.reduce((sum, [, v]) => sum + v, 0) / entries.length;

    const ratingsText = entries
      .sort(([, a], [, b]) => a - b)
      .map(([id, value]) => {
        const { label } = classifyRating(value);
        return `- ${CATEGORY_NAMES[id] || id}: ${value}/4 (${label})`;
      })
      .join("\n");

    const urgent = entries.filter(([, v]) => v <= 2).map(([id]) => CATEGORY_NAMES[id]).join(", ");
    const attention = entries.filter(([, v]) => v === 3).map(([id]) => CATEGORY_NAMES[id]).join(", ");
    const excellent = entries.filter(([, v]) => v === 4).map(([id]) => CATEGORY_NAMES[id]).join(", ");

    const fullSystemPrompt = `${systemPrompt}\n\n---\n\n# Base de Conhecimento\n\n${knowledgeBase}`;

    const userPrompt = `Analise o seguinte diagnostico.

AVALIACOES (escala 1-4, ordenadas por criticidade):
${ratingsText}

RESUMO ESTATISTICO:
- Media geral: ${avg.toFixed(1)}/4.0
- Areas criticas/urgentes (nota 1-2): ${urgent || "Nenhuma"}
- Areas de atencao (nota 3): ${attention || "Nenhuma"}
- Areas excelentes (nota 4): ${excellent || "Nenhuma"}

Pense passo a passo. Analise o quadro geral primeiro, depois detalhe cada area prioritaria.`;

    const stream = await openai.chat.completions.create({
      model: "gpt-5.2",
      messages: [
        { role: "system", content: fullSystemPrompt },
        { role: "user", content: userPrompt },
      ],
      max_completion_tokens: 3000,
      temperature: 0.7,
      stream: true,
    });

    const encoder = new TextEncoder();

    const readable = new ReadableStream({
      async start(controller) {
        try {
          for await (const chunk of stream) {
            const content = chunk.choices[0]?.delta?.content;
            if (content) controller.enqueue(encoder.encode(content));
          }
          controller.close();
        } catch (err) {
          controller.error(err);
        }
      },
    });

    return new Response(readable, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Transfer-Encoding": "chunked",
        "Cache-Control": "no-cache",
      },
    });
  } catch (error) {
    console.error("[Diagnostico] Erro:", error);
    return NextResponse.json({ error: "Falha ao gerar analise." }, { status: 500 });
  }
}
```

---

## next.config.ts

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: [
    "DOMINIO.COM.BR",
    "IP.DA.VPS",
  ],
};

export default nextConfig;
```

---

## .env.local

```
OPENAI_API_KEY=sk-...
```
