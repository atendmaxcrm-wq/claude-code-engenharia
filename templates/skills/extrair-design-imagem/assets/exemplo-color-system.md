# Color System - Flux Health Dashboard (EXEMPLO-OURO)

> Este arquivo e a referencia de QUALIDADE e FORMATO que uma extracao deve atingir.
> Foi destilado de um print do dashboard "flux". Note a precisao: hex + papel + regra
> de uso em cada cor, e a secao de decisoes notaveis (a parte opinativa).

## Backgrounds e superficies
| Papel | Hex |
|-------|-----|
| Sidebar / fundo escuro | #1A1A1A |
| Canvas principal | #F2F2EF (off-white quente) |
| Card / modal | #FFFFFF |
| Card escuro (sleep / paineis noturnos) | #262626 |

## Trio cromatico (identidade)
| Cor | Hex | Papel / regra de uso |
|-----|-----|----------------------|
| Lime | #C5F74F | CTA primario, badge +%, highlight ativo, barra de chart selecionada. Nunca como fundo de card inteiro. |
| Soft Purple | #B7A4F0 | graficos de area, bubble chart, indicadores secundarios |
| Mid Purple | #7C6BE0 | progress bars passivas, icones ativos |

## Escala de texto
| Papel | Hex |
|-------|-----|
| Headings bold | #111111 |
| Texto primario (dark) | #1A1A1A |
| Texto secundario | #6B6B66 |
| Texto muted | #AEAEA6 |
| Borda / divisor | #E8E8E2 |

## Tipografia
| Papel | Size | Weight | Tracking | Cor | Exemplo |
|-------|------|--------|----------|-----|---------|
| Display | 72-80px | 700 | -0.03em | #111111 | 4,3k |
| H1 / page title | 36-40px | 700 | -0.02em | #111111 | Health Overview |
| H2 / card title | 18px | 600 | -0.01em | #1A1A1A | Energy Used |
| H3 / section label | 14px | 600 | 0 | #1A1A1A | Sleep Analysis |
| Body / label | 14px | 400 | 0 | #6B6B66 | Take control of your health today! |
| Caption / muted | 12px | 400 | 0 | #AEAEA6 | kcal today |
| Badge / tag | 11px | 700 | +0.02em | fundo lime | +5% |

Familia: Inter / Geist Sans (open source). A agressividade NAO vem de fonte exotica,
e sim do size/weight/tracking (Display ~72px / 700 / -0.03em cria a sensacao de
"dado em destaque").

## Design tokens (referencia rapida)
| Token | Valor |
|-------|-------|
| radius sm / md / lg / pill | 8 / 14 / 20 / 999px |
| spacing base | 8px (escala 4/8/16/24/32) |
| card-padding | 24px |
| sidebar-width | 220px |
| shadow | none (design flat) |
| border default | 0.5px solid #E8E8E2 |

## Combos aprovados (contraste)
Lime + Dark · Dark + Lime · Purple + White · Soft Purple + Navy · Light BG + Dark Text

## Decisoes notaveis
- Dois mundos simultaneos: sidebar/paineis escuros (#1A1A1A) + conteudo off-white (#F2F2EF).
- Zero sombras. Toda separacao e por contraste de fundo (off-white vs branco vs near-black).
- O Lime so aparece como CTA, badge positivo e highlight ativo. Nunca fundo de card inteiro.
- Progress bars: Mid Purple #7C6BE0 passivo, Lime como active state.
- Border radius cresce conforme o componente: badge = pill, input = 8px, card = 14-20px.
- Hierarquia agressiva nos numeros (Display ~72px) = sensacao de dado em destaque.
