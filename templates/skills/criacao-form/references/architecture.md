# Arquitetura — Diagnostico Interativo com IA

Referencia completa da arquitetura do projeto. Baseado no `makewl-diagnostico` em producao.

---

## State Machine Central (page.tsx)

O `page.tsx` e um componente `"use client"` que orquestra todo o fluxo com 4 estados:

```typescript
type AppState = "form" | "loading" | "streaming" | "result";
```

### Fluxo:

```
form ─→ loading ─→ streaming ─→ result
                                   │
                                   └─→ reset() ─→ form
```

### Estado:
```typescript
const [state, setState] = useState<AppState>("form");
const [ratings, setRatings] = useState<Record<string, number>>({});
const [analysis, setAnalysis] = useState("");
const abortRef = useRef<AbortController | null>(null);
```

### Logica de Submit:
```typescript
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

    // Garantir pelo menos 2s de loading (UX)
    const elapsed = Date.now() - loadingStart;
    if (elapsed < 2000) {
      await new Promise(r => setTimeout(r, 2000 - elapsed));
    }

    setState("streaming");

    const reader = res.body?.getReader();
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
```

### Logica de Reset:
```typescript
function handleReset() {
  if (abortRef.current) abortRef.current.abort();
  setRatings({});
  setAnalysis("");
  setState("form");
}
```

### Renderizacao com AnimatePresence:
```tsx
<AnimatePresence mode="wait">
  {state === "form" && (
    <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <DiagnosticWizard ratings={ratings} onRatingChange={handleRatingChange} onSubmit={handleSubmit} />
    </motion.div>
  )}
  {state === "loading" && (
    <motion.div key="loading" ...>
      <LoadingAnalysis />
    </motion.div>
  )}
  {(state === "streaming" || state === "result") && (
    <motion.div key="result" ...>
      <ResultView analysis={analysis} ratings={ratings} onReset={handleReset} isStreaming={state === "streaming"} />
    </motion.div>
  )}
</AnimatePresence>
```

---

## Wizard Carousel (DiagnosticWizard.tsx)

### Dados das Categorias:
```typescript
const CATEGORIES = [
  { id: "financeiro", title: "Financeiro", description: "Como voce avalia...?", icon: "💰" },
  { id: "processos", title: "Processos", description: "...", icon: "⚙️" },
  // ... N categorias
];
```

### Scale Labels:
```typescript
const SCALE_LABELS = [
  { value: 1, label: "Urgente", color: "bg-urgent" },
  { value: 2, label: "Urgente", color: "bg-urgent" },
  { value: 3, label: "Atencao", color: "bg-attention" },
  { value: 4, label: "Excelente", color: "bg-excellent" },
];
```

### Props:
```typescript
interface DiagnosticWizardProps {
  ratings: Record<string, number>;
  onRatingChange: (id: string, value: number) => void;
  onSubmit: () => void;
}
```

### Estado Interno:
```typescript
const [currentStep, setCurrentStep] = useState(0);
const [direction, setDirection] = useState(1); // 1=next, -1=prev
```

### Auto-Advance:
```typescript
function handleRate(value: number) {
  onRatingChange(category.id, value);
  if (value > 0 && !isLast) {
    setTimeout(() => {
      setDirection(1);
      setCurrentStep(s => Math.min(s + 1, total - 1));
    }, 500);
  }
}
```

### Progress Ring SVG:
```typescript
const ringRadius = 45;
const ringCircumference = 2 * Math.PI * ringRadius;
const ringOffset = ringCircumference - (progress / 100) * ringCircumference;

<svg width="110" height="110" className="-rotate-90">
  <circle cx="55" cy="55" r={ringRadius} fill="none" stroke="var(--card-border)" strokeWidth="3" />
  <motion.circle cx="55" cy="55" r={ringRadius} fill="none" stroke="var(--accent)"
    strokeWidth="3" strokeLinecap="round" strokeDasharray={ringCircumference}
    animate={{ strokeDashoffset: ringOffset }}
    transition={{ duration: 0.5, ease: "easeOut" }}
  />
</svg>
```

### Slide Variants (direction-aware):
```typescript
const slideVariants = {
  enter: (dir: number) => ({ x: dir > 0 ? 80 : -80, opacity: 0, scale: 0.95 }),
  center: { x: 0, opacity: 1, scale: 1 },
  exit: (dir: number) => ({ x: dir > 0 ? -80 : 80, opacity: 0, scale: 0.95 }),
};
```

### Animacoes Internas do Slide (Anti-Flash Mobile):
**NUNCA** usar `opacity: 0` em elementos dentro do slide (titulo, subtitulo, opcoes/items).
O slide do AnimatePresence ja faz fade-in do container. Animacoes internas com opacity 0 causam "flash/piscar" no mobile — o elemento some e reaparece visivelmente.

**Padrao correto:**
```typescript
// Titulo — quase visivel, fade sutil
<motion.h2
  initial={{ opacity: 0.8, y: 6 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ delay: 0.05, duration: 0.25, ease: "easeOut" }}
>

// Subtitulo — um pouco mais sutil
<motion.p
  initial={{ opacity: 0.6, y: 4 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ delay: 0.08, duration: 0.25, ease: "easeOut" }}
>

// Opcoes/Items — stagger com delay reduzido (original * 0.4)
<motion.button
  initial={{ opacity: 0.7, y: 6 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.25, delay: staggerDelay * 0.4, ease: "easeOut" }}
>

// Icone/Emoji — spring normal (pode comecar em 0, e pequeno e rapido)
<motion.div
  initial={{ scale: 0, rotate: -30 }}
  animate={{ scale: 1, rotate: 0 }}
  transition={{ type: "spring", stiffness: 300, damping: 15 }}
>
```

**Principio:** opacity inicial alta (0.6-0.8) + delays < 0.12s + duracao 0.25s = animacao perceptivel SEM flash.

### Layout Mobile — Areas Fixas + Scroll nas Opcoes (CRITICO)

No mobile, 5-6 opcoes de resposta nao cabem na viewport junto com header, ring, titulo e nav. A solucao e dividir o layout em areas fixas e uma area scrollavel.

**Estrutura:**
```
┌─────────────────────────┐
│  Logo + subtitulo       │  ← fixo (flexShrink: 0)
│  Progress ring          │  ← fixo (flexShrink: 0)
│  Icone + titulo + ctx   │  ← fixo (flexShrink: 0)
├─────────────────────────┤
│  Opcao A                │
│  Opcao B                │  ← scrollavel (flex-1, overflow auto)
│  Opcao C                │     hide-scrollbar
│  Opcao D                │
│  Opcao E (scroll)       │
├─────────────────────────┤
│  ◄ · · · · · · · · · ► │  ← fixo (flexShrink: 0)
│  3 de 15 respondidas    │
└─────────────────────────┘
```

**Container principal:**
```tsx
<div
  className="relative flex flex-col items-center"
  style={{ height: "100dvh", overflow: "hidden", padding: "10px 16px 6px" }}
>
  {/* Header — fixo */}
  <div style={{ flexShrink: 0 }}>...</div>

  {/* Progress ring — fixo */}
  <div style={{ flexShrink: 0 }}>...</div>

  {blockMessage ? (
    /* Block message — centralizado no espaco restante */
    <div className="flex-1 flex items-center justify-center" style={{ minHeight: 0 }}>
      ...mensagem de transicao...
    </div>
  ) : (
    <>
      {/* Titulo da pergunta — fixo */}
      <div style={{ flexShrink: 0 }}>
        <AnimatePresence mode="wait" custom={direction}>
          <motion.div key={`header-${question.id}`} variants={slideVariants} ...>
            <QuestionHeader question={question} />
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Opcoes — scrollavel */}
      <div
        className="flex-1 hide-scrollbar"
        style={{ overflow: "auto", minHeight: 0, WebkitOverflowScrolling: "touch" }}
      >
        <AnimatePresence mode="wait" custom={direction}>
          <motion.div key={`options-${question.id}`} variants={slideVariants} ...>
            <QuestionOptions ... />
          </motion.div>
        </AnimatePresence>
      </div>
    </>
  )}

  {/* Nav — fixo */}
  <div style={{ flexShrink: 0 }}>...</div>
</div>
```

**Pontos criticos:**
- `minHeight: 0` na area scrollavel e OBRIGATORIO para flex-1 funcionar com overflow
- `-webkit-overflow-scrolling: touch` para scroll suave no iOS
- Header e opcoes animam com os mesmos slideVariants (sincronizados)
- Block messages ocupam todo o espaco central (flex-1 + items-center + justify-center)

**CSS para hide-scrollbar:**
```css
.hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
.hide-scrollbar::-webkit-scrollbar { display: none; }
```

### Separacao do QuestionCard em Partes

Para o layout funcionar, o QuestionCard deve exportar componentes separados:

```typescript
// QuestionHeader — renderizado fora da area scroll
export function QuestionHeader({ question }: { question: Question }) {
  return (
    <div className="flex flex-col items-center">
      {/* Icone */}
      <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} ...>
        <Icon ... />
      </motion.div>
      {/* Titulo */}
      <motion.h2 initial={{ opacity: 0.8, y: 6 }} animate={{ opacity: 1, y: 0 }} ...>
        {question.texto}
      </motion.h2>
      {/* Contexto */}
      {question.contexto && <motion.p ...>{question.contexto}</motion.p>}
    </div>
  );
}

// QuestionOptions — renderizado dentro da area scroll
export function QuestionOptions({ question, onAnswer, disabled, selectedAnswer }) {
  return (
    <div style={{ gap: 8 }}>
      {question.opcoes.map((opcao, idx) => (
        <AnswerOption key={opcao.id} opcao={opcao} index={idx} ... />
      ))}
    </div>
  );
}

// QuestionCard original mantido para compatibilidade
export default function QuestionCard(props) { ... }
```

### ProfessionalForm — Compacto no Mobile

O formulario inicial tambem deve caber no mobile sem scroll excessivo:

```typescript
// Container
style={{ minHeight: "100dvh", padding: "16px 16px 12px", overflowY: "auto", overflowX: "hidden" }}

// Card
style={{ padding: "20px 20px" }}

// Fields — marginBottom reduzido
style={{ marginBottom: 14 }}  // cada campo

// Labels — marginBottom reduzido
style={{ fontSize: 11, letterSpacing: "0.18em", marginBottom: 8 }}

// Tipo Atuacao buttons
style={{ padding: "12px 10px" }}

// Divider
style={{ height: 1, margin: "14px 0" }}

// CTA button
style={{ padding: "16px 28px" }}

// Footer
style={{ marginTop: 16 }}
```

**IMPORTANTE:** Usar SEMPRE inline styles para padding, margin, gap, fontSize. Classes Tailwind de spacing nao refletem visualmente no Next.js 16 + Turbopack.

### Step Dots:
```tsx
{CATEGORIES.map((cat, i) => {
  const filled = (ratings[cat.id] || 0) > 0;
  const active = i === currentStep;
  return (
    <button key={cat.id}
      onClick={() => { setDirection(i > currentStep ? 1 : -1); setCurrentStep(i); }}
      className={`h-2 rounded-full transition-all duration-300 cursor-pointer ${
        active ? "w-6 bg-accent" : filled ? "w-2 bg-foreground/40" : "w-2 bg-card-border"
      }`}
    />
  );
})}
```

---

## Star Rating (StarRating.tsx)

### Props:
```typescript
interface StarRatingProps {
  value: number;
  onChange: (value: number) => void;
  max?: number; // default 4
}
```

### Comportamento:
- Click na estrela preenchida = deseleciona (value 0)
- Click na vazia = seleciona ate ali
- Animacao ao preencher: `scale: [1, 1.4, 1], rotate: [0, -15, 15, 0]`
- Hover: scale 1.2
- Label numerica abaixo de cada estrela

### Classes:
- Preenchida: `fill-star-filled text-star-filled star-glow`
- Vazia: `fill-transparent text-star-empty hover:text-star-hover`

---

## API Route (api/analyze/route.ts)

### Fluxo:
1. **Valida** input (ratings objeto, 13 categorias)
2. **Classifica** cada rating: 1=CRITICO, 2=URGENTE, 3=ATENCAO, 4=EXCELENTE
3. **Identifica clusters** de areas correlacionadas em risco
4. **Carrega** prompt + KB dos arquivos `prompts/`
5. **Monta** fullSystemPrompt = prompt + KB
6. **Monta** userPrompt com: avaliacoes ordenadas, resumo estatistico, clusters
7. **Chama** OpenAI stream
8. **Retorna** ReadableStream

### Streaming Response:
```typescript
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
    for await (const chunk of stream) {
      const content = chunk.choices[0]?.delta?.content;
      if (content) controller.enqueue(encoder.encode(content));
    }
    controller.close();
  },
});

return new Response(readable, {
  headers: {
    "Content-Type": "text/plain; charset=utf-8",
    "Transfer-Encoding": "chunked",
    "Cache-Control": "no-cache",
  },
});
```

---

## Result View (ResultView.tsx)

### Score Card:
- Media geral: `avg.toFixed(1) + "/4.0"`
- Status: avg < 2.0="Em Crise", < 2.5="Em Risco", < 3.2="Atencao", else="Saudavel"
- Contadores: N urgentes, N excelentes

### Rating Bars:
- Categorias ordenadas por nota (ascendente)
- Barra horizontal: `width: (value/4)*100%`
- Cor por severidade: urgent/orange/attention/excellent

### Analysis Content:
- `dangerouslySetInnerHTML={{ __html: analysis }}`
- CSS class `analysis-content` para formatacao de h2/h3/p/ul/li

### Streaming Indicators:
- 3 dots pulsantes com delay escalonado
- Cursor piscante (`opacity: [1, 0]`, repeat Infinity)

### Streaming (SEM auto-scroll):
O conteudo HTML aparece em tempo real via `dangerouslySetInnerHTML`, mas a pagina **NAO rola automaticamente**. O usuario le no proprio ritmo.

**NUNCA** implementar `scrollTo`, `scrollIntoView` ou qualquer scroll programatico vinculado ao streaming. Isso atrapalha a leitura e e uma experiencia ruim.

### Copy Button:
- `navigator.clipboard.writeText(text)` com fallback textarea
- Estado: "Copiar Analise" → "Copiado!" (2s timeout)

---

## Loading Analysis (LoadingAnalysis.tsx)

### Pulsing Orb:
- 3 circulos concentricos com scale/opacity animados
- Delays escalonados: 0s, 0.3s, 0.5s
- Duration: 2s, repeat Infinity

### Steps Cycling:
- Array de 5 textos descritivos
- Cada um aparece por 2.5s
- Animacao: opacity [0,1,1,0] + y [20,0,0,-20]
- RepeatDelay: (STEPS.length - 1) * 2.5

### Dots Loader:
- 3 dots com opacity [0.2, 1, 0.2]
- Duration: 1s, delay: i * 0.2

---

## Logo Component (MakewlLogo.tsx)

### Tamanhos:
```typescript
const ASPECT_RATIO = 5.16; // 2528 / 490 (logo-makewl.png original)
const HEIGHTS = { sm: 24, md: 32, lg: 44 };
const w = Math.round(h * ASPECT_RATIO);
```

### Uso de next/image com priority flag. Arquivo: `/public/logo-makewl.png`

---

## Header Premium (MakewlHeader.tsx)

Componente padrao de branding para todas as telas iniciais de formularios/diagnosticos Makewl.

### Elementos:
1. **Logo com linhas accent** — Logo `/logo-makewl.png` centralizado, com 2 linhas horizontais de 32px (h-px, accent, opacity 50%) de cada lado, gap-3
2. **Titulo com palavra-chave italica** — Texto light (300) + palavra-chave em `<em>` com font-family serif (Playfair Display Variable), italic, font-size 1.15em, cor accent-light
3. **Subtitulo muted** — fontSize 13px, opacity 0.45, letterSpacing 0.08em, fontWeight 300
4. **Ornamento divisor** — 2 linhas gradiente (60px cada, transparent→accent→transparent) + losango 5x5px accent rotacionado 45 graus no centro, opacity 60%

### Props:
```typescript
interface MakewlHeaderProps {
  titlePrefix: string;    // "Descubra seu", "Diagnostico para"
  titleKeyword: string;   // "Arquetipo", "Clinicas" (em italico serif)
  subtitle: string;       // "15 perguntas · resultado personalizado com IA"
}
```

### Animacoes (Framer Motion):
- Logo: opacity 0→1, y:-10→0, delay 0.1s
- Titulo: opacity 0→1, y:12→0, delay 0.15s
- Subtitulo: opacity 0→1, delay 0.25s
- Ornamento: opacity 0→1, delay 0.3s

### Fontes requeridas no layout.tsx:
```typescript
import { Inter, Playfair_Display } from "next/font/google";
const playfair = Playfair_Display({ variable: "--font-playfair", subsets: ["latin"], style: ["normal", "italic"] });
// body: className={`${inter.variable} ${playfair.variable} antialiased`}
```

### Uso em paginas:
- **Wizard (DiagnosticWizard)**: Usar logo simples (MakewlLogo) + subtitulo uppercase no header do quiz
- **ProfessionalForm / Tela Inicial**: Usar MakewlHeader completo com titulo, keyword, subtitulo e ornamento
- **LoadingAnalysis**: Usar MakewlLogo centralizado acima do pulsing orb
- **ResultView**: Usar MakewlLogo tamanho "sm" no header
