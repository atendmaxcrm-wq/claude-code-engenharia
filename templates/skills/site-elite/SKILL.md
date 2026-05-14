---
name: site-elite
description: Criar sites premium nivel Asimov/Linear/Vercel/Aura.build. Aplica metodologia Vibe Design - destila Design System de referencia ANTES de codar, em camadas (estrutura -> tokens -> motion -> background). Anti-slop manifesto carregado por padrao. Use quando o usuario pedir criar site novo nivel premium, landing page elite, site nao-generico, replicar estetica X, "site bonito" tipo Asimov/Aura/Linear, sair do template Lovable. Stack Next.js 16 + Tailwind v4 + GSAP + UnicornStudio + gpt-image-2.
---

# /site-elite — Sites Premium Nivel Asimov/Aura.build

> Skill mestre para construir sites que NAO tem cara de IA. Substitui o reflexo "hero centralizado + Inter + roxo" pelo workflow Vibe Design da Asimov Academy combinado com guidelines oficiais da Anthropic.

---

## STOP: Gate de aderencia

**LEIA ANTES DE COMECAR. Pular qualquer fase = slop garantido.**

Esta skill existe porque sites criados em one-shot prompting com LLMs convergem para a media estatistica do training data. O resultado e sempre o mesmo: tipografia Inter, paleta roxo-azul gradiente, hero centralizado, cards com radius 12px, copy "Build the future of X". Reconhecivel a 1km de distancia como IA.

A solucao NAO e dar mais liberdade pro modelo. E o oposto: **constraint > permission**. Esta skill bane explicitamente o que voce nao pode usar e forca um workflow em camadas que extrai o Design System ANTES de escrever uma linha de codigo.

**Se voce vai pular Fase 0 (Vibe Questionnaire) ou Fase 1 (Destilar DS), pare e me avise. Nao prossiga.**

---

## Filosofia

### Por que sites com LLM saem genericos

Distributional convergence. O modelo nao tem preferencia estetica - ele tem distribuicao de probabilidade. Quando voce pede "crie um site moderno", a saida mais provavel e a media do que ele viu no training data. E essa media e:

- Inter como display
- Roxo (#8B5CF6) com gradiente para azul (#3B82F6)
- border-radius 12-16px universal
- Hero `flex items-center justify-center text-center`
- Copy Lovable: "Build", "Empower", "Reimagine", "Future"
- Micro-interactions Framer Motion espalhadas em todo hover

Isso nao e ruim por estetica. E ruim por ser **previsivel**. Nao tem assinatura, nao tem alma, nao tem decisao.

### Constraint > Permission

A virada de chave da Asimov Academy ("Vibe Design") e: nao diga ao modelo o que fazer. Diga o que NAO fazer e force um workflow que destila criterio antes de gerar.

### Vibe Design (Asimov) + Frontend-Design (Anthropic) = este skill

| Vibe Design (Asimov) | Frontend-Design (Anthropic) |
|---|---|
| Extrair DS antes do codigo | 4 perguntas de Vibe (Purpose/Tone/Constraints/Differentiation) |
| Contexto progressivo (multi-prompt) | 11 tones extremos (escolher 1) |
| Camadas separadas | Editorial restraint (1 coisa memoravel, nao 10) |
| Iteracao com URL/screenshot | Anti-slop manifesto |

Esta skill funde os dois. Workflow em 5 fases obrigatorias.

---

## Quando usar

Triggers explicitos:

- "Cria uma landing premium pra X"
- "Quero um site nivel Asimov / Aura / Linear / Vercel"
- "Site novo pra [marca/produto], sem cara de IA"
- "Replica essa estetica" + URL de referencia
- "Redesign do site X em nivel premium"
- "Sair do template Lovable"
- "Site bonito, com personalidade"
- "Hero com WebGL / shader / motion serio"

Sinais implicitos: usuario reclama que o site anterior "tem cara de IA", "ta generico", "qualquer um faz igual", "parece template", "Lovable de novo".

---

## Quando NAO usar

- **Formularios, wizards, diagnosticos, quiz**: usar `/criacao-form`. Fluxo diferente, estetica diferente.
- **Clone pixel-perfect de site existente**: usar `/clonar-site`. Engenharia reversa de assets/CSS exato, nao destilacao de DS.
- **Componente isolado (botao, card, modal)**: usar `/component-builder` ou `/upgrade-visual`.
- **Animacao especifica isolada (text reveal, scroll pin)**: usar `/gsap-animations`.
- **Sites simples sem ambicao visual** (admin, dashboard interno, MVP rapido): nao gaste o orcamento de complexidade aqui. `/component-builder` resolve.

---

## Workflow 5 fases

```
[Fase 0] Vibe Questionnaire ----+
                                |
[Fase 1] Destilar DS de ref ----+--> DESIGN-{marca}.md
                                |
[Fase 2] Estrutura + Tokens ----+--> tailwind.config + tokens.css + componentes base
                                |
[Fase 3] Motion (GSAP) ---------+--> page-load timeline + scroll triggers
                                |
[Fase 4] Background assinatura -+--> UnicornStudio / WebGL / gpt-image-2 / canvas
                                |
[Fase 5] Quality gates ---------+--> anti-slop checklist + Lighthouse + WCAG
```

**Cada fase tem entregavel concreto. Nao avance sem o entregavel da anterior.**

---

### Fase 0 — Vibe Questionnaire (OBRIGATORIO antes de codar)

Pergunte ao usuario as 4 perguntas Vibe antes de qualquer outra acao. Se o usuario nao souber responder, pare e ajude a destrinchar - nao chute.

#### As 4 perguntas

**1. Purpose**
- O que e este site/pagina? (produto SaaS, landing de captura, portfolio, agencia, educacional, evento)
- Para quem? (1 persona especifica, nao "todos")
- Qual a UMA acao principal que voce quer que o visitante faca?

**2. Tone (escolher 1 dos 11 extremos)**

Nao aceite "moderno e clean". Forca o usuario a escolher UM:

| # | Tone | Referencias canonicas |
|---|------|----------------------|
| 1 | **Brutalist** | bratus.studio, koto.studio |
| 2 | **Editorial Magazine** | thecreativeindependent.com, are.na |
| 3 | **Retro-futurista (Y2K/CRT)** | paper.design, antinode.studio |
| 4 | **Swiss/Helvetica minimal** | rauno.me, emilkowal.ski |
| 5 | **Dark technical premium** | linear.app, vercel.com/design |
| 6 | **WebGL maximalist** | aura.build, basement.studio, active.theory |
| 7 | **Soft pastel humano** | maven.com, posthog.com |
| 8 | **Terminal/CLI nerd** | charm.sh, mitchellh.com |
| 9 | **Editorial luxury** | hermes.com, off---white.com |
| 10 | **Playful illustrated** | stripe.com (press), notion.so |
| 11 | **Industrial/blueprint** | rivian.com, supreme.com |

**3. Constraints**
- Marca existente? (cores fixas, fonte fixa, logo fixo - se sim, anexar /docs/makewl/ ou equivalente)
- Performance target? (Lighthouse 90+? Hero <2.5s LCP?)
- A11y? (WCAG AA obrigatorio? screen reader friendly?)
- Browser support? (Safari iOS conta? IE nunca - mas Safari sim)
- SEO/SSR critico?

**4. Differentiation (a UMA coisa memoravel)**

Pergunta-chave da Anthropic: **se o usuario lembrar de UMA coisa do site, qual e?**

NAO aceite lista de 10 features memoraveis. UMA. Pode ser:
- Um background WebGL especifico
- Uma transicao de pagina
- Uma tipografia de display unica
- Um sistema de cor inesperado
- Um copy contrarian
- Um momento de scroll especifico

Se o usuario lista 10 coisas, retorne: "Escolhe UMA. As outras sao tempero, nao prato principal."

#### Entregavel da Fase 0

Documento curto (markdown, ~30 linhas) com as 4 respostas. Salvar em `/root/teste-aios/aios-core/apps/{projeto}/VIBE.md` ou onde fizer sentido. Esse doc alimenta Fase 1.

---

### Fase 1 — Destilar Design System de referencia

**Sem referencia visual real, voce vai gerar a media do training data. Pegue URL ou screenshot.**

#### Input aceito

- URL ao vivo (preferido - permite scraping de CSS computado)
- Screenshot (PNG/JPG)
- Multiplas refs (max 3 - mais que isso vira franken-design)

#### Processo

Use o reference `01-design-system-distiller.md` (escrito separadamente) como prompt. O distiller gera um `DESIGN-{marca}.md` em **9 secoes obrigatorias**:

1. **Identidade & posicionamento** (1 frase)
2. **Paleta de cores** (background, foreground, accent, neutros - hex + uso)
3. **Tipografia** (display + body + mono - familia, peso, escala modular, tracking)
4. **Espacamento & ritmo** (escala 4/8 ou custom, gutters, content widths)
5. **Layout & grid** (12-col? assimetrico? hero pattern especifico?)
6. **Componentes-chave** (botoes, cards, inputs - shape language)
7. **Motion language** (easing curves, duracao, principios - calmo? snappy? heavy?)
8. **Background/atmosfera** (cor solida? gradient? WebGL? noise? grain?)
9. **Anti-padroes** (o que esse site EVITA - ajuda a calibrar)

**Se nao tem referencia, NAO PROSSIGA.** Volta na Fase 0 e force o usuario a apontar 1-3 sites que ele admira.

#### Entregavel da Fase 1

`DESIGN-{marca}.md` com 9 secoes preenchidas. Esse arquivo e a fonte de verdade unica para Fases 2-4. Se algo nao esta nele, NAO existe no site.

---

### Fase 2 — Estrutura + Tokens

Agora voce pode codar. Mas em camadas.

#### Ordem rigida

1. **tokens.css** (CSS variables) - cores, espacamento, radius, shadows, fonts
2. **tailwind.config.ts** - mapeia tokens.css para classes Tailwind v4 (`@theme inline`)
3. **app/layout.tsx** - import de fonts (next/font), variaveis globais
4. **Componentes atomicos** - Button, Link, Heading, Badge (3-5 max)
5. **Componentes compostos** - Card, Section, Hero (so depois dos atomicos)
6. **Pagina** - so depois dos compostos

#### Regras teste-aios (criticas)

- **USAR INLINE STYLE pra spacing/sizing** em Next.js 16 + Turbopack. Classes Tailwind tipo `mt-12 px-6 text-2xl` nao refletem confiavelmente. `style={{ marginTop: 48, paddingInline: 24, fontSize: 24 }}` reflete.
- Classes genericas (`flex grid items-center gap-4`) funcionam normal.
- next/font para tudo que nao e display custom. Para display custom (variable font de marca), `<link>` no head.

#### Tipografia

Consultar `03-typography-arsenal.md`. Nunca default Inter. Display options canonicos por tone:

| Tone | Display | Body |
|------|---------|------|
| Editorial | Tiempos / GT Sectra / PP Editorial | Inter Tight / Söhne |
| Brutalist | PP Neue Bit / NB International Mono | NB International Pro |
| Swiss | NB Akademie / GT America | NB Akademie |
| Retro | VT323 / Press Start 2P / Departure Mono | JetBrains Mono |
| Dark technical | Berkeley Mono / Geist Mono | Geist |
| WebGL maximalist | Migra / PP Editorial Old | PP Neue Montreal |

Free alternatives quando licenca aperta: **PP Neue Montreal (free trial)**, **Inter Tight** (nao Inter), **Geist** (Vercel, free), **JetBrains Mono**, **Space Grotesk**.

#### Entregavel da Fase 2

- `tokens.css` com todas variaveis derivadas do DS
- `tailwind.config.ts` mapeando tokens
- 3-5 componentes atomicos funcionando
- Pagina rascunho SEM motion e SEM background ainda

**Build deve passar e visualmente o site ja deve ter cara propria.** Se ainda parece template, voltar.

---

### Fase 3 — Motion (GSAP)

GSAP e 100% gratis desde Outubro/2024 (Webflow comprou e abriu). Usar GSAP por padrao para sites elite. Framer Motion fica para componentes isolados (modais, micro-hovers).

Consultar `04-motion-recipes-gsap.md` para receitas completas.

#### Principios de motion para site elite

1. **Page-load timeline orquestrada** - tudo entra em sequencia coreografada nos primeiros 2s, nao "fade-in espalhado".
2. **ScrollTrigger com pin sections** para momentos-chave (1 ou 2 no site, nao 10).
3. **SplitText para revelar headlines** - char-by-char ou word-by-word com stagger.
4. **Easing curves do DS** - definidas na Fase 1, secao 7. Nunca `ease-in-out` default.
5. **Lenis para smooth scroll** se o tone pede (WebGL, editorial). Nunca em sites tecnicos secos.

#### Anti-padroes de motion

- Hover scale 1.05 em tudo que se mexe
- Fade-in `whileInView` em cada secao identico
- Bounce/spring em itens serios
- Animacao de loader fake quando nao tem nada carregando

#### Entregavel da Fase 3

- Page-load timeline funcionando
- 1-2 scroll moments
- Hover/focus states intencionais nos atomicos
- Performance: motion nao trava em scroll (60fps em scroll)

---

### Fase 4 — Background (assinatura)

Aqui mora a `differentiation` da Fase 0. **Esta e a UMA coisa memoravel** na maioria dos casos.

#### Opcoes em ordem de preferencia

1. **UnicornStudio** (preferido, ja integrado no projeto)
   - Shader ID exemplo: `AhqzKk9mZE0EnlENMQDi` (crmax-site)
   - Lightweight, configuravel sem codigo, performance otima
   - Consultar `05-webgl-backgrounds.md` para integrar

2. **WebGL custom** (three.js / OGL / shaders)
   - Quando UnicornStudio nao cobre
   - Mantem peso baixo: prefer OGL sobre three.js para shaders 2D
   - Consultar `05-webgl-backgrounds.md` secao "WebGL custom"

3. **gpt-image-2 hero** (lancado 21/04/2026)
   - Para heros com imagem de fundo unica e estatica
   - **Sem PNG transparente nativo** - gerar fundo solido e mascarar via CSS
   - Suporta thinking mode para texto PT-BR (logo placards, etc)
   - Consultar `06-gpt-image-2-prompts.md` para prompts canonicos

4. **Canvas matrix / particles / noise**
   - Fallback leve para tones tecnicos/retro
   - 200 linhas de canvas 2D, sem libs

5. **Solid + grain CSS** (fallback minimo)
   - Quando background nao e o foco
   - `background-image: url(noise.png); background-blend-mode: overlay;`

#### Aura.build arsenal

Refs canonicas premium para inspiracao de background:

- emilkowal.ski (motion + WebGL sutil)
- rauno.me (Swiss minimal + scroll)
- basement.studio (WebGL maximalist)
- paper.design (retro-futurista premium)
- vercel.com/design (dark technical)
- linear.app (gradients sutis + grain)
- aura.build (templates premium WebGL - referencia visual real)

Consultar `09-aura-build-arsenal.md` para shaders mapeados por tone.

#### Entregavel da Fase 4

- 1 background-assinatura no hero (ou em 1 secao especifica)
- Performance: nao quebra LCP (lazy load se necessario, fallback estatico para mobile)
- Acessivel: prefers-reduced-motion respeitado

---

### Fase 5 — Quality gates

Consultar `07-quality-gates.md` para checklist completo. Resumo:

#### Anti-slop checklist (obrigatorio)

- [ ] Display NAO e Inter, Roboto, Arial, Helvetica
- [ ] Paleta NAO e roxo-azul gradiente generico
- [ ] Hero NAO e centralizado padrao Lovable (a menos que o tone justifique)
- [ ] border-radius NAO e 12px universal
- [ ] Copy NAO contem "Build the future", "Empower", "Reimagine"
- [ ] Motion tem proposito (nao hover scale 1.05 em tudo)
- [ ] Background tem assinatura (nao gradient CSS chao)
- [ ] Site reconhecivel se voce remover o logo? (teste do logo)
- [ ] Site se distingue de 10 sites Lovable lado a lado?

#### Lighthouse target

- Performance: 90+
- Accessibility: 95+
- Best Practices: 95+
- SEO: 95+

#### WCAG AA

- Contraste 4.5:1 (texto), 3:1 (UI)
- Foco visivel em tudo navegavel
- prefers-reduced-motion respeitado
- Semantic HTML (nao `<div>` tudo)

#### Validacao final teste-aios

```bash
# Build de producao
cd /root/teste-aios/aios-core/apps/{projeto}
npm run build
npm run start  # NUNCA next dev pra acesso externo

# Lighthouse via Playwright
# (ver /safari-check para auditoria Safari iOS)
```

---

## Anti-slop quick reference

### BANLIST (nao usar sem justificativa explicita do DS)

**Tipografia**
- Inter (use Inter Tight se precisar de geometric sans free)
- Roboto, Arial, Helvetica como display
- System fonts default

**Paleta**
- `from-purple-500 to-blue-500` (gradiente Lovable)
- `from-pink-500 via-purple-500 to-indigo-500` (vibrant gradient)
- Roxo (#8B5CF6) sem justificativa de marca
- Azul (#3B82F6) sem justificativa
- "Vibrant gradient hero"

**Layout**
- Hero `flex items-center justify-center text-center` default
- Cards `border-radius: 12px` + `shadow-md` universal
- Grid 3 colunas de features com icones
- "Trusted by" com 6 logos cinza

**Copy**
- "Build the future of X"
- "Empowering Y to Z"
- "Reimagine your W"
- "The next generation of"
- "AI-powered" como diferencial unico
- "Seamlessly integrate"

**Motion**
- `whileInView opacity 0 -> 1 y: 20` em toda secao
- Hover scale 1.05 em todo card
- Spring bounce em CTA serio
- Loading skeleton fake

### USELIST (preferir)

**Tipografia**: PP Neue Montreal, Inter Tight, Geist, Tiempos, GT Sectra, PP Editorial, NB Akademie, Berkeley Mono, Departure Mono.

**Paleta**: derivada da referencia, nao do default. Considerar duotone (2 cores forte + neutros), monocromatico com 1 accent, ou paleta inesperada (verde militar, mostarda, lavanda fria).

**Layout**: hero assimetrico, grid editorial, magazine sidebars, full-bleed media.

**Copy**: especifica, contrariana, com voz. Curta. Numeros concretos. Citacoes.

**Motion**: page-load orquestrado, SplitText reveals, scroll pin com proposito, easing custom do DS.

---

## Decision tree: qual reference consultar quando

```
Estou na Fase 1, pegando URL/screenshot de referencia
  -> 01-design-system-distiller.md

Estou escolhendo tipografia (Fase 2)
  -> 03-typography-arsenal.md
  -> 02-color-palettes.md (se duvida de paleta)

Estou implementando motion (Fase 3)
  -> 04-motion-recipes-gsap.md
  -> /gsap-animations skill (deep dive)

Estou definindo background (Fase 4)
  -> UnicornStudio: 05-webgl-backgrounds.md secao 1
  -> WebGL custom: 05-webgl-backgrounds.md secao 2-3
  -> gpt-image-2: 06-gpt-image-2-prompts.md
  -> Aura.build inspiration: 09-aura-build-arsenal.md

Estou no quality gate (Fase 5)
  -> 07-quality-gates.md
  -> /safari-check skill (compatibilidade Safari)

Cliente pediu copy
  -> 08-copy-anti-slop.md
  -> /text-humanizer skill (humanizar tom IA)

Estou clonando 1:1 um site existente
  -> NAO usar este skill, ir pra /clonar-site

Preciso de animacao isolada complexa
  -> /gsap-animations skill

Estou criando wizard/diagnostico/quiz
  -> /criacao-form skill (NAO esta skill)
```

---

## Skills auxiliares relacionadas

- `/gsap-animations` — deep dive em motion (ScrollTrigger, SplitText, Flip, MorphSVG)
- `/clonar-site` — engenharia reversa pixel-perfect (NAO usar para sites novos)
- `/clonar-design` — extrair design system de site existente (input para Fase 1)
- `/capturar-efeitos` — descobrir lib/tech por tras de efeito visual
- `/criacao-form` — wizards/diagnosticos/quiz (workflow diferente)
- `/upgrade-visual` — upgrade de sistema existente (1+ componentes)
- `/component-builder` — componente isolado
- `/safari-check` — validacao Safari iOS/macOS
- `/frontend-design` — guidelines oficiais Anthropic (referencia base)
- `/text-humanizer` — humanizar copy gerado por IA

---

## Particularidades teste-aios

### Stack confirmada

- Next.js 16 + Tailwind v4 + Turbopack
- Framer Motion + GSAP (GSAP 100% gratis desde Out/2024)
- gpt-image-2 (lancado 21/04/2026)
- UnicornStudio (shader ID `AhqzKk9mZE0EnlENMQDi` ja integrado no crmax-site)

### Regras criticas (CLAUDE.md)

- **USAR INLINE STYLE pra spacing/sizing**: classes Tailwind v4 + Turbopack nao refletem mudancas visuais confiavelmente. `style={{ marginTop: 48 }}` em vez de `mt-12`. Classes genericas (flex, grid, items-center) funcionam normal.
- **next dev NAO hidrata via IP externo**: sempre `next build` + `next start` para acesso via IP/dominio. next dev so via localhost.
- **Heredocs em Bash**: NUNCA `cat <<EOF` via Bash tool. Sempre Write tool.
- **gpt-image-2 sem PNG transparente nativo**: gerar fundo solido + mascarar via CSS.

### Portas livres para dev

3107-3199. Verificar `ss -tlnp` antes de subir servidor. Faixa ja ocupada:

| Projeto | Porta |
|---------|-------|
| Site Makewl (dev) | 3100 |
| Diagnostico | 3101 |
| Quiz Arquetipos | 3102 |
| Legacy Advisor | 3103 |
| Disrupty Vagas | 3104 |
| NPS Legacy | 3105 |
| Financa Pessoal | 3106 |
| GSAP Showcase | 3108 |

### Identidade Makewl (quando aplicavel)

Se o site e da Makewl, consultar `/docs/makewl/` (8 arquivos: marca, cores, tipografia, logo, voz, publico, design system, conteudo). Esses tokens sobrescrevem o que viria da Fase 1.

---

## Exemplos de uso

### Exemplo 1: Landing premium pra produto novo

**Usuario**: "Cria uma landing pra um SaaS B2B chamado Drift. Quero nivel Linear/Vercel."

**Fluxo**:
1. Fase 0: pergunto Purpose (qual o produto exatamente?), Tone (Linear = "Dark technical premium" #5), Constraints (perf Lighthouse 95+? marca existente?), Differentiation (UMA coisa memoravel).
2. Fase 1: pego linear.app + vercel.com/design como ref, gero `DESIGN-drift.md` em 9 secoes.
3. Fase 2: Geist como font, paleta neutra fria + 1 accent, tokens, atomicos, pagina rascunho.
4. Fase 3: GSAP page-load com SplitText no headline, ScrollTrigger pin numa secao de feature.
5. Fase 4: UnicornStudio shader sutil de gradient mesh no hero (assinatura). Backgound: solid + grain nas demais secoes.
6. Fase 5: anti-slop checklist + Lighthouse + Safari iOS.

### Exemplo 2: Replicar estetica Aura.build

**Usuario**: "Quero um site nivel aura.build pra minha agencia."

**Fluxo**:
1. Fase 0: Purpose (agencia, captar leads), Tone (#6 WebGL maximalist), Differentiation (background WebGL tipo aura).
2. Fase 1: aura.build + basement.studio + active.theory como refs, gera DS focado em motion-heavy.
3. Fase 2: PP Neue Montreal + Migra display, paleta dark + 1 vibrant accent.
4. Fase 3: Lenis smooth scroll + GSAP timeline pesada + page transitions.
5. Fase 4: WebGL custom (OGL) com shader assinatura. Consultar `09-aura-build-arsenal.md`.
6. Fase 5: gates + perf especial em mobile (WebGL pesa).

### Exemplo 3: Redesign do site Makewl

**Usuario**: "Refaz o site da Makewl, ta com cara de IA."

**Fluxo**:
1. Fase 0: Purpose (Makewl = consultoria/agencia), Constraints (anexar `/docs/makewl/` - marca fixa). Tone: voce e o usuario decidem juntos, nao chute.
2. Fase 1: pular destilacao de ref externa - usar `/docs/makewl/` como DS pronto. Validar 9 secoes.
3. Fase 2: tokens vem do `/docs/makewl/cores.md` + `tipografia.md`. Logo de `logo.md`.
4. Fase 3: motion alinhado a `voz.md` (tom da marca define ritmo da animacao).
5. Fase 4: background derivado da identidade visual Makewl, nao default WebGL roxo.
6. Fase 5: gates + voz humanizada (passar copy por `/text-humanizer`).

### Exemplo 4: "Site bonito" tipo Asimov

**Usuario**: "Olha o site da asimov.academy, quero algo nesse nivel pra meu curso."

**Fluxo**:
1. Fase 0: Purpose (curso/educacao), Tone (Asimov tem tom proprio - "Editorial premium dark com acento tecnico"), Differentiation.
2. Fase 1: scrape asimov.academy + 1-2 refs adjacentes (maven.com, posthog.com), gera DS.
3. Fase 2-5: igual.

---

## Final note

Este skill NAO entrega um site em 1 prompt. Entrega um workflow em 5 fases que produz um site memoravel. Se o usuario pedir "rapido, em 1 shot", explique que o resultado vai ser slop e oferece o trade-off. Se ele insistir, use `/component-builder` ou `/upgrade-visual` em vez deste skill.

Constraint > permission. Camada por camada. Referencia antes de codigo. UMA coisa memoravel.
