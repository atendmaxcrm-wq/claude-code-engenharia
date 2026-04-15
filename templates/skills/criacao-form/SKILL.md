---
name: criacao-form
description: "Cria formulario/diagnostico interativo com wizard carousel, rating por estrelas, analise por IA com streaming e pagina de resultado rica. Stack: Next.js 16 + Tailwind v4 + Framer Motion + OpenAI streaming. Suporta Agent Teams para projetos grandes (multiplas categorias, customizacao pesada). Baseado no projeto diagnostico.assessoriamakewl.com.br em producao. Use sempre que o usuario pedir: diagnostico, assessment, avaliacao, formulario interativo com IA, wizard multi-step com analise, pesquisa com resultado gerado por IA, ou qualquer fluxo de categorias com rating e feedback inteligente."
---

# Criacao de Formulario/Diagnostico Interativo com IA

Cria projetos completos de diagnostico interativo com wizard carousel, rating por estrelas, loading cinematografico, streaming de resposta IA e pagina de resultado rica. Baseado no projeto em producao: diagnostico.assessoriamakewl.com.br.

## Filosofia Central

**Diagnostico premium = wizard simples + analise profunda por IA + streaming real-time + resultado acionavel.**

O usuario avalia N categorias com estrelas (1-4), a IA recebe os dados estruturados + prompt especializado + knowledge base, e gera uma analise personalizada em streaming. O resultado deve ser util, nao generico.

## Stack Obrigatoria

| Tecnologia | Versao | Papel |
|------------|--------|-------|
| Next.js | 16+ | Framework, App Router, API Routes |
| React | 19+ | UI |
| TypeScript | 5+ | Tipagem |
| Tailwind CSS | v4 | Estilizacao (@theme inline) |
| Framer Motion | 12+ | Animacoes de transicao e UI |
| OpenAI SDK | 6+ | Streaming de analise por IA |
| Lucide React | 0.577+ | Icones |
| Inter | - | Fonte via next/font/google |

## Quando Ler os Arquivos de Referencia

Antes de iniciar qualquer trabalho, leia os arquivos apropriados:

| Tarefa | Leia Primeiro |
|--------|--------------|
| Criar diagnostico novo do zero | `references/architecture.md` depois `references/design-system.md` |
| Ajustar prompt/KB da IA | `references/prompt-engineering.md` |
| Copiar estrutura de componentes | `assets/component-templates.md` |
| Gerar CSS base | `assets/globals-css-template.md` |

## Workflow Completo

## Modo Agent Teams (Tarefas Grandes)

### Quando Usar Agent Teams

Use Agent Teams quando o projeto envolver **pelo menos um** dos fatores abaixo:
- 8 ou mais categorias no wizard
- Customização pesada de design (cores, fontes, branding fora do padrão Makewl)
- Projeto criado do zero (sem base existente para copiar)
- Cliente com requisitos de resultado muito específicos (PDF, múltiplos idiomas, etc.)

Para projetos simples (menos de 8 categorias, sem customização pesada), executar sem Agent Teams — fazer direto sequencialmente.

### Composição do Time

| Agente | Responsabilidade |
|--------|-----------------|
| **scaffold-dev** | Estrutura do projeto, `layout.tsx`, `globals.css`, `next.config.ts`, `.env.local` |
| **api-dev** | Rota da API (`route.ts`), lógica de streaming, arquivos `prompt-*.md` e `kb-*.md` |
| **wizard-dev** | `DiagnosticWizard.tsx`, `StarRating.tsx`, `CategoryCard.tsx`, state machine em `page.tsx` |
| **design-dev** | `MakewlHeader.tsx`, `LoadingAnalysis.tsx`, `ResultView.tsx`, polish visual |

### Fluxo de Execução

```
Wave 1 (paralelo — independentes entre si):
  scaffold-dev  →  estrutura base do projeto
  api-dev       →  rota API + prompts + KB

Wave 2 (paralelo — após Wave 1 concluir):
  wizard-dev    →  carousel + state machine (precisa do scaffold)
  design-dev    →  header + loading + resultado (precisa do scaffold)

Quality Gate:
  npm run build → deve compilar sem erros
  Teste fluxo completo: wizard → loading → streaming → resultado
```

### Padrão de Criação do Time

```
TeamCreate: { team_name: "criacao-form", description: "[tema] diagnostic form" }

Wave 1 (parallel):
- Agent: scaffold-dev (general-purpose, sonnet) → project setup
- Agent: api-dev (general-purpose, sonnet) → API route + prompts

Wave 2 (after Wave 1):
- Agent: wizard-dev (general-purpose, sonnet) → wizard carousel + state machine  
- Agent: design-dev (general-purpose, sonnet) → header + loading + result view

Quality Gate: npm run build + test full flow
TeamDelete
```

### 1. Briefing (Levantar com o Usuario)

Antes de codar qualquer coisa, defina:

- **Tema do diagnostico**: Qual area? (ex: empresarial, saude, marketing, financeiro)
- **Marca/identidade**: Nome, logo, cores accent
- **Categorias**: Quais areas avaliar? (recomendado: 8-15 categorias)
- **Escala de rating**: 1-4 estrelas (padrao) ou customizada
- **Labels por nota**: Ex: 1-2=Urgente, 3=Atencao, 4=Excelente
- **Persona da IA**: Quem e o consultor? (ex: consultor senior, medico, mentor)
- **Knowledge base**: Que frameworks/dados a IA deve usar por categoria?
- **Porta dev**: Usar faixa 3100-3199 (verificar disponibilidade)
- **Dominio final**: Para configurar allowedDevOrigins

### 2. Scaffold do Projeto

```bash
npx create-next-app@latest [nome-projeto] --typescript --tailwind --app --src-dir
cd [nome-projeto]
npm install framer-motion lucide-react openai
```

### 3. Estrutura de Arquivos (Padrao)

```
[projeto]/
├── src/
│   ├── app/
│   │   ├── layout.tsx           # Root layout (Inter font + Playfair Display, metadata)
│   │   ├── favicon.ico          # Favicon Makewl (copiar de makewl-diagnostico/src/app/favicon.ico)
│   │   ├── page.tsx             # State machine: form → loading → streaming → result
│   │   ├── globals.css          # Dark theme + analysis-content formatting
│   │   └── api/
│   │       └── analyze/
│   │           └── route.ts     # POST: valida → monta prompt → OpenAI stream
│   └── components/
│       ├── MakewlHeader.tsx     # Header premium: logo + linhas accent + titulo italico
│       ├── DiagnosticWizard.tsx  # Carousel com progress ring + star rating
│       ├── StarRating.tsx       # N estrelas clicaveis com animacao
│       ├── CategoryCard.tsx     # Card de categoria (alternativa grid)
│       ├── LoadingAnalysis.tsx   # Pulsing orb + steps cycling
│       ├── ResultView.tsx       # Score card + bars + analysis + copy + reset
│       └── MakewlLogo.tsx       # Logo responsivo (sm/md/lg) com next/image
├── prompts/
│   ├── prompt-[tema].md         # System prompt da IA
│   └── kb-[tema].md             # Knowledge base por categoria
├── public/
│   └── logo-makewl.png          # Logo Makewl (2528x490px, aspect ratio 5.16:1)
├── .env.local                   # OPENAI_API_KEY
└── next.config.ts               # allowedDevOrigins
```

### 4. Implementacao — State Machine (CRITICO)

O page.tsx e o orquestrador central com 4 estados:

```
"form" → "loading" (min 2s) → "streaming" → "result"
```

**Regras:**
- `form`: Mostra DiagnosticWizard. Ratings em `Record<string, number>`
- `loading`: Mostra LoadingAnalysis. Minimo 2s de delay (UX)
- `streaming`: Mostra ResultView com `isStreaming=true`. SEM auto-scroll (o usuario le no seu ritmo)
- `result`: Mostra ResultView final. Botoes de copiar e refazer

**AbortController**: Sempre usar para cancelar stream ao resetar.

### 5. Implementacao — Header Premium Makewl (CRITICO)

O MakewlHeader e o componente padrao de branding para todos os formularios/diagnosticos.

**Elementos obrigatorios:**
- **Logo Makewl** (`/logo-makewl.png`) centralizado, com linhas accent de cada lado
- **Titulo principal**: Texto light (peso 300) com a palavra-chave em **italico serif** e **cor accent-light**
- **Subtitulo**: Texto muted, uppercase, letter-spacing 0.08em
- **Ornamento divisor**: Duas linhas gradiente com losango accent rotacionado 45 graus no centro

**Exemplo de titulo:**
```
Descubra seu Arquetipo    → "Arquetipo" em italic serif, cor accent-light
Diagnostico para Clinicas → "Clinicas" em italic serif, cor accent-light
```

**Fontes:** Usar `Playfair Display Variable` (serif) para as palavras em italico. Importar no layout.tsx via `next/font/google`.

**Linhas accent ao lado do logo:**
- Largura: 32px (w-8)
- Altura: 1px (h-px)
- Cor: `var(--color-accent)` com opacity 50%
- Gap: 12px entre logo e linhas

Ver template completo em `assets/component-templates.md`.

### 6. Implementacao — Wizard Carousel (CRITICO)

O DiagnosticWizard e um carousel com:

- **Layout mobile-first com areas fixas/scrollaveis**: O container principal usa `height: 100dvh` + `overflow: hidden`. Header (logo), progress ring e titulo da pergunta ficam **fixos** (flexShrink: 0). Somente a area de opcoes/respostas faz scroll (`flex-1` + `overflow: auto` + `minHeight: 0`). Nav (dots + setas) fica fixo no fundo. Isso garante que o usuario sempre ve a pergunta e so scrolla as opcoes se nao couberem
- **Hide scrollbar visual**: Adicionar classe `.hide-scrollbar` na area scrollavel para esconder a barra sem perder funcionalidade: `scrollbar-width: none; -ms-overflow-style: none; ::-webkit-scrollbar { display: none }`
- **Progress ring SVG**: Circulo com stroke-dashoffset animado
- **Step counter**: "N de M" centralizado no ring
- **Category card**: Emoji + titulo + descricao + StarRating
- **Auto-advance**: 500ms delay apos selecionar estrela
- **Direction-aware slides**: x:±80 baseado em direcao (next/prev). Header da pergunta e opcoes animam em paralelo com os mesmos slideVariants
- **Animacoes anti-flash**: Elementos internos do slide NUNCA comecam com opacity 0 (causa piscar no mobile). Usar opacity inicial 0.6-0.8 + delays < 0.12s + duracao 0.25s
- **Block messages centralizados**: Mensagens de transicao entre blocos ("Otimo! Agora vamos aprofundar...") devem ocupar o espaco central inteiro (flex-1 + justify-center), nao ficam presas no header
- **Step dots**: N dots clicaveis (active=wider, filled=color)
- **Nav buttons**: ChevronLeft/Right
- **Submit button**: Aparece so quando todas categorias preenchidas

### 7. Implementacao — API Route (CRITICO)

O endpoint POST /api/analyze:

1. Recebe `{ ratings }` (Record<string, number>)
2. Valida todas as categorias presentes
3. Classifica cada rating (critico/urgente/atencao/excelente)
4. Identifica clusters de areas correlacionadas
5. Carrega prompt + KB dos arquivos em `prompts/`
6. Monta userPrompt com dados estruturados
7. Chama OpenAI com `stream: true`
8. Retorna ReadableStream com chunks

**Modelo**: gpt-5.2 (ou gpt-4o para custo menor)
**max_completion_tokens**: 3000
**temperature**: 0.7

### 8. Implementacao — Result View (CRITICO)

A pagina de resultado mostra:

- **Score card**: Media geral + status (Saudavel/Atencao/Em Risco/Em Crise)
- **Rating bars**: Todas categorias ordenadas por nota, com barras coloridas
- **Analysis content**: HTML renderizado com `dangerouslySetInnerHTML`
- **Streaming cursor**: Barra piscante durante streaming
- **Streaming dots**: 3 dots pulsantes + "Gerando analise..."
- **Copy button**: Copia texto da analise para clipboard
- **Reset button**: Volta ao formulario
- **Disclaimer**: "Diagnostico gerado por IA..."

### 9. Implementacao — Prompts (CRITICO)

Dois arquivos em `prompts/`:

**prompt-[tema].md** — System prompt:
- Identidade e personalidade do consultor
- Tom de voz (direto, sem jargoes)
- Regras criticas (so usar dados fornecidos, analisar interdependencias)
- Fluxo de analise: Diagnosticar → Priorizar → Recomendar → Planejar
- Mapa de interdependencias entre categorias
- Calibracao de severidade por nota
- Estrutura da saida HTML (h2, h3, p, ul, li)

**kb-[tema].md** — Knowledge base:
- Framework por categoria (sinais por nota, recomendacoes acionaveis, interdependencias)
- Analise de clusters (grupos de categorias correlacionadas)
- Escala de avaliacao

### 10. Validacao

Antes de considerar pronto:
1. `npm run build` — deve compilar sem erros
2. Testar fluxo completo: wizard → loading → streaming → resultado
3. Verificar auto-advance das estrelas
4. Verificar streaming real-time (nao batch)
5. Verificar copy-to-clipboard funciona
6. Verificar responsivo (mobile + desktop)
7. Verificar `.env.local` tem OPENAI_API_KEY

## Principios Rigidos

1. **Dark mode** — fundo #09090b, cards #18181b, texto #fafafa
2. **Cor accent customizavel** — padrao #E7540F (laranja Makewl)
3. **CSS custom properties** via :root + @theme inline (Tailwind v4)
4. **Gradient mesh** com radial-gradients coloridos (opacity 0.04-0.08)
6. **Fontes**: Inter (body, 300-800) + Playfair Display Variable (titulos italicos serif) via next/font/google
7. **4 estrelas** (padrao) — nao 5. Escala de 1-4 sem neutro
8. **Streaming real** via ReadableStream — nao polling nem batch
9. **Analysis content** formatado com CSS class (h2/h3/p/ul/li com estilos proprios)
10. **"use client"** em todo componente com hooks/interatividade
11. **Proibido travessao (em-dash —) em QUALQUER texto visivel** — perguntas, opcoes de resposta, titulos, subtitulos, labels, placeholders, mensagens de transicao, analise da IA, PDF, TUDO. O travessao e marca registrada de texto gerado por IA e compromete a credibilidade. Usar virgula, ponto, ponto e virgula, ou reescrever a frase. Exemplos: "Como voce avalia a gestao financeira da sua clinica?" (correto) vs "Como voce avalia — de forma geral — a gestao?" (ERRADO). Isso vale tambem para o conteudo dos prompts e KB da IA
12. **Acentuação correta OBRIGATÓRIA** em TODO texto visível ao usuário — títulos, labels, placeholders, mensagens de erro, opções de select, tooltips, botões, descriptions, scarcityMessages, e qualquer string que apareça na interface. Exemplos: "Gestão" (não "Gestao"), "Clínica" (não "Clinica"), "Você" (não "Voce"), "à vista" (não "a vista"), "Cartão" (não "Cartao"), "único" (não "unico"), "mês" (não "mes"), "Opção" (não "Opcao"), "Diagnóstico" (não "Diagnostico"), "Não" (não "Nao"). IDs e slugs (ex: `gestao-processos`, `precificacao`) podem ficar sem acento. **NUNCA** entregar código com texto PT-BR sem acentos.
13. **Portas dev**: usar faixa 3100-3199 (NUNCA 3000-3005, 4001, 5432, 6379, 8080)
14. **Prompt + KB separados** — nunca misturar comportamento com dados
15. **min 2s loading** — garantir UX cinematografica antes do streaming
16. **SEM auto-scroll durante streaming** — o conteudo aparece em tempo real mas a pagina NAO rola automaticamente. O usuario le no proprio ritmo. NUNCA usar `scrollTo` ou `scrollIntoView` vinculado ao streaming
17. **Animacoes anti-flash em carousel** — elementos dentro do slide (titulo, subtitulo, opcoes) NUNCA comecam com `opacity: 0`. Usar `opacity: 0.6-0.8` inicial + delays < 0.12s + duracao 0.25s. Icones/emojis podem usar spring normal (scale 0→1). Opacity 0 dentro de AnimatePresence causa "piscar" no mobile
18. **Layout mobile: areas fixas + scroll so nas opcoes** — o container usa `height: 100dvh` + `overflow: hidden`. Header, progress ring e titulo da pergunta ficam fixos. Somente as opcoes/respostas fazem scroll (flex-1 + overflow auto + minHeight 0). Nav fica fixo embaixo. Esconder scrollbar com `.hide-scrollbar` (scrollbar-width: none)
19. **Inline styles para spacing no Next.js 16** — classes Tailwind de spacing (padding, margin, gap, fontSize) NAO refletem visualmente de forma confiavel no Next.js 16 + Turbopack + Tailwind v4. SEMPRE usar `style={{}}` para padding, margin, gap, fontSize e propriedades visuais criticas. Classes genericas (flex, grid, items-center, rounded) funcionam normalmente
20. **Block messages centralizados** — mensagens de transicao entre blocos de perguntas devem ocupar o espaco central completo (flex-1 + justify-center), nao ficar presas no header. Renderizar condicionalmente: se blockMessage, mostra mensagem centralizada; senao, mostra header + opcoes
21. **ProfessionalForm compacto no mobile** — padding do container max 16px, card padding max 20px, field marginBottom max 14px, label marginBottom max 8px, CTA padding max 16x28. overflow-y via inline style (nao Tailwind class)
22. **Favicon Makewl padrao** — ao fazer deploy em dominio, SEMPRE copiar o favicon oficial da Makewl de `/root/teste-aios/makewl-diagnostico/src/app/favicon.ico` para `src/app/favicon.ico` (e opcionalmente `public/favicon.ico`). Esse e o favicon padrao para todos os projetos Makewl em producao. NUNCA usar o favicon default do Next.js

## Formato de Saida

Ao criar um diagnostico, entregue:
1. Projeto Next.js completo com todos os componentes
2. Prompt do consultor IA (`prompts/prompt-[tema].md`)
3. Knowledge base por categoria (`prompts/kb-[tema].md`)
4. `.env.local` template com OPENAI_API_KEY placeholder
