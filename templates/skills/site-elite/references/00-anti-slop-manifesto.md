# 00 — Anti-Slop Manifesto

## Diagnostico: distributional convergence

LLM converge para a media estatistica do training data. Quando voce pede "make it modern", o modelo devolve o centroide visual do que a internet rotulou como "modern" entre 2021-2024: Lovable hero, gradiente roxo, Inter como display, cards 12px radius com shadow leve, "Build the future of X".

A solucao nao e dar mais permissao ("seja criativo"). E dar **constraint**: tom forcado, fonte forcada, paleta forcada, anti-patterns explicitos. Constraint > permission.

## Banlist absoluta

### Tipografia display proibida
- Inter (use SO em body, nunca em headline)
- Roboto
- Arial / Helvetica
- Lato
- Open Sans
- Montserrat

Display obrigatorio: Bricolage Grotesque, Clash Display, Satoshi, Fraunces, Newsreader, Geist, Space Grotesk, Oswald (ver `03-typography-arsenal.md`).

### Paleta proibida
- Gradiente roxo -> azul (`from-purple-500 to-blue-500`)
- Adjetivos: "vibrant", "vivid", "bold colorful"
- Purple `#8B5CF6` solitario
- Paletas equilibradas com 5 cores de mesmo peso (sempre 1 dominante + 1 cortante)

### Layout proibido
- Hero centralizado com botao gigante no meio (Lovable default)
- Cards com `rounded-xl shadow-md` empilhados em grid 3 colunas
- Navbar pill fixa no topo com 7 links e botao "Get Started" CTA roxo
- Hero split 50/50 texto-esquerda imagem-direita generico

### Copy proibido
- "Build the future of X"
- "Empowering Y"
- "Reimagine Z"
- "We help businesses to..."
- "Unlock the power of..."
- "Transform your workflow"
- "Seamlessly integrate"
- "Cutting-edge"

### Motion proibido
- Hover scale 1.05 espalhado em todo elemento clicavel
- Fade-in-up generico em scroll para cada secao
- Micro-interactions sem proposito narrativo
- Parallax gratuito (deve servir a hierarquia)

## Por que constraint > permission

Permissao gera media. Constraint gera identidade.

Exemplo concreto:

**Permissao** (slop): "Crie um hero moderno e clean para SaaS de produtividade"
-> Resultado: Inter 64px, bg `#FAFAFA`, gradiente sutil, "Build productivity that scales", botao roxo `#8B5CF6`.

**Constraint** (signal): "Hero brutalist editorial. Display: Oswald uppercase 800 clamp(4rem, 12vw, 9rem). BG `#0A0A0A`. Accent UNICO: `#FF4500` orange burn. Proibido: gradiente, shadow, radius > 4px. Copy: 6 palavras max, frase incompleta. Motion: SplitText reveal 1 vez no load, depois pagina estatica."
-> Resultado: identidade.

## Regra operacional

Antes de escrever qualquer linha de Tailwind, responda o `02-vibe-questionnaire.md`. Se o tom escolhido nao foi forcado a um dos 11 extremos, voce vai cair no centroide. Nao existe "moderno e clean" — isso e a media.

## Anti-slop scan automatizado

```bash
grep -rE "from-purple-[0-9]+ to-blue-[0-9]+" src/
grep -rE "Build the future|Empowering|Reimagine|Seamlessly" src/
grep -rE "font-(inter|roboto|arial|helvetica|montserrat).*text-(5|6|7|8|9)xl" src/
```

Se algum match: refatorar antes de deploy.
