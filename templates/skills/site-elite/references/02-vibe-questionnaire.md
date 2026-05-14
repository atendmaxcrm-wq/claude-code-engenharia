# 02 — Vibe Questionnaire

Anthropic guideline: 4 perguntas obrigatorias antes de qualquer prompt de UI. Se voce pula, vai cair no centroide.

## As 4 perguntas

### 1. Purpose
- O que e esse site/pagina?
- Para quem (estado mental, dispositivo, contexto)?
- Qual A UNICA acao que o visitante deve tomar?

Errado: "site institucional para mostrar nossos servicos"
Certo: "landing page que converte CTOs em B2B SaaS de logistica para agendar demo de 30min, mobile-first porque eles abrem o link no celular durante reuniao"

### 2. Tone
Escolher exatamente 1 dos 11 extremos. Sem misturar. Sem "moderno e clean".

| # | Tom | Marcas referencia |
|---|-----|-------------------|
| 1 | brutalist | Balenciaga, Bloomberg Terminal, Are.na |
| 2 | editorial-magazine | The New Yorker, Apple Books, paper.design |
| 3 | retro-futurista | Cyberpunk 2077, Tron, Nothing Phone |
| 4 | solarpunk | Studio Ghibli, biophilic design, futuro otimista |
| 5 | technical-doc | Stripe docs, Linear, Vercel |
| 6 | art-deco | Great Gatsby, Chrysler Building, lineas geometricas douradas |
| 7 | swiss-poster | Helvetica era, Massimo Vignelli, grid puro |
| 8 | terminal-cyberpunk | Matrix, hackers IRL, monospace verde fosforo |
| 9 | organic-handcrafted | Aesop, brand de ceramica, texturas naturais |
| 10 | maximalist-collage | Acne Studios, revista i-D, sobreposicao caotica controlada |
| 11 | minimalist-japanese | Muji, Kenya Hara, ma (espaco negativo) |

Errado: "moderno e clean"
Certo: "swiss-poster mas com 1 elemento brutalist (header tipografia 200px clamp)"

### 3. Constraints
- Marca: cores fixas, logo, fonte obrigatoria
- Performance: budget de KB, LCP target, mobile target
- A11y: WCAG nivel (A, AA, AAA), suporte teclado, screen reader
- Tech: stack obrigado, libs proibidas
- Prazo

### 4. Differentiation
A UMA coisa memoravel que diferencia. **Proibido lista de 10**. Lista de 10 = nada e memoravel.

Errado: "queremos que seja rapido, bonito, acessivel, responsivo, com animacoes legais e copy forte"
Certo: "a UMA coisa: hero que pin scroll com tipografia 200px que se desmonta em particulas no scroll"

## Template para usuario responder

```markdown
## 1. Purpose
- O que: [1 frase]
- Para quem: [persona, dispositivo, estado mental]
- Acao unica: [1 verbo]

## 2. Tone
- Escolhido: [1 dos 11]
- Por que: [1 frase]
- Anti-tom: [3 adjetivos que nunca]

## 3. Constraints
- Marca: [...]
- Performance: [LCP, KB]
- A11y: [nivel WCAG]
- Tech: [stack]
- Prazo: [data]

## 4. Differentiation
- A UMA coisa: [1 elemento especifico]
```

## Exemplo preenchido — brutalist

```markdown
## 1. Purpose
- O que: portfolio de fotografo editorial brasileiro
- Para quem: art director de revista/agencia, desktop, avaliando contratacao
- Acao unica: agendar reuniao via formulario direto

## 2. Tone
- Escolhido: brutalist
- Por que: o trabalho dele e cru, retratos sem retoque, precisa que site espelhe isso
- Anti-tom: clean, friendly, accessible-feeling

## 3. Constraints
- Marca: monograma "RG" preto sobre branco, sem cor adicional
- Performance: LCP <2s, hero <150KB
- A11y: WCAG AA (mas focus visible com border 4px solid amarelo)
- Tech: Next.js 16, sem libs de animacao
- Prazo: 14 dias

## 4. Differentiation
- A UMA coisa: tipografia 240px Bodoni que se sobrepoe as fotos com mix-blend-mode difference
```

## Exemplo preenchido — editorial-magazine

```markdown
## 1. Purpose
- O que: landing de lancamento de livro de ensaios sobre IA e trabalho
- Para quem: leitor de The Atlantic, mobile (LinkedIn click), curioso
- Acao unica: pre-encomendar fisico (R$89)

## 2. Tone
- Escolhido: editorial-magazine
- Por que: livro e long-form ensaistico, visual deve antecipar o ritmo de leitura
- Anti-tom: techy, startup-y, gradiente

## 3. Constraints
- Marca: capa do livro como unica imagem (sem fotos extras)
- Performance: LCP <2.5s, total <600KB
- A11y: WCAG AAA (audiencia inclui idosos)
- Tech: Astro (estatico)
- Prazo: 21 dias

## 4. Differentiation
- A UMA coisa: drop cap gigante (200px Fraunces) que abre cada paragrafo do excerto, scroll-driven
```

## Regra final

Se o usuario nao consegue responder a 4 — especialmente o "differentiation" — pare. Nao existe site bom sem essa decisao. Insista ate ter resposta. "Nao sei" significa que o site vai ser slop.
