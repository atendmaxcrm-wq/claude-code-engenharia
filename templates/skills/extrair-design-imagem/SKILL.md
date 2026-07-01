---
name: extrair-design-imagem
description: Extrai um design system completo (cores com hex + papel, tipografia hierarquica, tokens, combos de contraste, decisoes notaveis) a partir de uma IMAGEM de referencia (screenshot, mockup, print de UI). Usa a visao do Claude, sem scraper. Use quando o usuario compartilha uma imagem/print de um app ou site e quer destilar o esquema visual, paleta, tipografia ou design tokens dela. Triggers: extrair design de imagem, design system de um print, paleta dessa imagem, tipografia dessa referencia, tokens dessa tela, analisar referencia visual, "faz que nem o GPT fez", "esse nivel de extracao".
---

Extraia um design system completo a partir de uma imagem de referencia: $ARGUMENTS

Esta skill NAO usa Playwright nem scraper. A entrada e uma imagem estatica e a
extracao e 100% feita pela visao do Claude (ler a imagem com a tool Read).

## Passo 0: Localizar a imagem

- Se `$ARGUMENTS` traz um caminho de imagem, use-o.
- Se nao, procure a imagem mais recente em `docs/` (png/jpg/jpeg/webp):
  `ls -lt docs/*.{png,jpg,jpeg,webp} 2>/dev/null | head`
- Se houver varias imagens recentes (ex: o print + um board de cores), leia TODAS:
  o print da UI mostra os usos reais, o board (se existir) confirma os hex exatos.
- Confirme com o usuario qual imagem usar SO se houver ambiguidade real. Nao encha
  de perguntas.

Leia a(s) imagem(ns) com a tool **Read** (visao). Olhe de verdade: pixels, contraste,
pesos de fonte, espacamentos, cantos.

## Passo 1: Protocolo de extracao (o coracao da skill)

Seja CIRURGICO. A meta e o nivel de um designer destilando tokens, nao "tem roxo e verde".
Regras:

1. **Cores: sempre hex + papel + onde aparece.** Nunca diga "roxo"; diga
   "`#7C6BE0` Mid Purple - progress bars, icones ativos". Estime o hex pelo pixel.
   Agrupe por funcao:
   - Backgrounds / superficies (fundo de pagina, card, painel escuro, modal)
   - Trio/quarteto cromatico (as cores de marca/identidade e seus papeis)
   - Escala de texto (titulo forte, primario, secundario, muted)
   - Borda / divisor
   Para cada cor cromatica, diga a REGRA DE USO observada (ex: "lime so aparece em
   CTA, badge positivo e estado ativo, nunca como fundo de card inteiro").

2. **Tipografia: hierarquia por papel, nao lista de tamanhos.** Para cada nivel
   (Display, H1, H2, H3, Body/Label, Caption, Badge) extraia: faixa de size, weight,
   letter-spacing (tracking), cor, e um EXEMPLO de texto tirado da imagem. Identifique
   a familia provavel (compare glyphs: Inter, Geist, General Sans, Clash Display,
   Poppins, etc) e diga se a "agressividade" vem da fonte ou do size/weight/tracking.

3. **Tokens: deduza os valores reais.** border-radius (escala sm/md/lg/pill),
   spacing base e a escala (4/8/16/24/32...), card-padding, sidebar-width,
   abordagem de SOMBRA (flat sem sombra? elevado? glow colorido?), borda default.

4. **Combos de cor com contraste.** Liste pares aprovados (ex: Lime + Dark,
   Purple + White) que a referencia usa e que passam em contraste.

5. **Decisoes de design notaveis.** A parte opinativa e mais valiosa: as escolhas
   que dao identidade. Ex: "Zero sombras, separacao por contraste de fundo",
   "Lime nunca em fundo de card", "radius cresce conforme o componente",
   "hierarquia agressiva nos numeros (~72px) cria sensacao de dado em destaque".

NAO invente o que nao da pra ver. Se um valor for inferencia, marque como
"(aproximado)". Prefira hex consistentes (se a mesma cor aparece em varios lugares,
use um unico hex).

## Passo 2: Gerar o markdown da extracao

Salve em `docs/design-extraido-<slug>.md` (slug = nome curto da referencia, ex:
`flux`, `linear`, `meuassessor`). Siga EXATAMENTE este formato (ver tambem o exemplo-ouro
em `.claude/skills/extrair-design-imagem/assets/exemplo-color-system.md`):

```markdown
# Color System - <Nome da referencia>

## Backgrounds e superficies
| Papel | Hex |
|-------|-----|
| Sidebar / fundo escuro | #1A1A1A |
| Canvas principal | #F2F2EF |
| Card / modal | #FFFFFF |
| Card escuro (destaque) | #262626 |

## Trio cromatico (identidade)
| Cor | Hex | Papel / regra de uso |
|-----|-----|----------------------|
| Lime | #C5F74F | CTA, badge +%, ativo. Nunca fundo de card inteiro. |
| Soft Purple | #B7A4F0 | charts, bubble, secundario |
| Mid Purple | #7C6BE0 | progress bars, icones ativos |

## Escala de texto
| Papel | Hex |
|-------|-----|
| Headings bold | #111111 |
| Texto primario | #1A1A1A |
| Texto secundario | #6B6B66 |
| Texto muted | #AEAEA6 |
| Borda / divisor | #E8E8E2 |

## Tipografia
| Papel | Size | Weight | Tracking | Cor | Exemplo |
|-------|------|--------|----------|-----|---------|
| Display | 72-80px | 700 | -0.03em | #111 | 4,3k |
| H1 / titulo | 36-40px | 700 | -0.02em | #111 | Health Overview |
| H2 / card | 18px | 600 | -0.01em | #1A1A1A | Energy Used |
| H3 / label | 14px | 600 | 0 | #1A1A1A | Sleep Analysis |
| Body | 14px | 400 | 0 | #6B6B66 | Take control... |
| Caption | 12px | 400 | 0 | #AEAEA6 | kcal today |
| Badge | 11px | 700 | +0.02em | dark/lime | +5% |

Familia: <Inter / Geist / etc> - <de onde vem a agressividade>.

## Design tokens (referencia rapida)
| Token | Valor |
|-------|-------|
| radius sm / md / lg / pill | 8 / 14 / 20 / 999px |
| spacing base | 8px (4/8/16/24/32) |
| card-padding | 24px |
| sidebar-width | 220px |
| shadow | none (flat) / elevado / glow |
| border default | 0.5px solid #E8E8E2 |

## Combos aprovados
Lime + Dark · Dark + Lime · Purple + White · Light BG + Dark Text

## Decisoes notaveis
- ...
- ...
```

## Passo 3: Gerar o board visual de cores (opcional mas recomendado)

Clone `.claude/skills/extrair-design-imagem/assets/color-board-template.html` para
`docs/design-extraido-<slug>-board.html` e preencha com os swatches extraidos
(igual a segunda imagem da referencia flux: cada cor um retangulo com hex + papel).
Avise que da pra abrir no navegador. (Nao precisa screenshot; sem Playwright aqui.)

## Passo 4: Oferecer ponte para implementacao

Pergunte se o usuario quer:
1. Wirar os tokens no projeto (ex: bloco `@theme` do Tailwind v4 em `app/globals.css`)
2. Aplicar em uma tela como preview antes de propagar
3. So a extracao (parar aqui)

## Passo 5: Apresentar resultado

Mostre um resumo (quantas cores, niveis tipograficos, decisoes), o caminho dos
arquivos gerados, e a pergunta do Passo 4.

## Notas
- Prompt-only: nenhuma dependencia externa, nenhum script. So Read (visao) + Write.
- Se a imagem for so um board/paleta (sem UI), extraia so cores e pule a parte de
  layout/uso que dependeria de ver componentes.
- PT-BR sem travessao (em-dash).
