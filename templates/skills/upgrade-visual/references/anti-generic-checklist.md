# Checklist Anti-Generico — Upgrade Visual

Use este checklist para auditar e transformar qualquer interface de "sistema" em "produto premium".

---

## Auditoria Rapida (Marcar todos que se aplicam)

### Background
- [ ] Background e preto puro (#000) ou branco puro (#fff) → Trocar para off-black (#09090b)
- [ ] Background e flat (cor solida) → Adicionar gradient mesh sutil (3 radial-gradients, 0.04-0.08 opacity)
- [ ] Sem profundidade entre camadas → Adicionar escala de elevacao por luminosidade (#121212 → #1a1a1a → #262626)

### Borders
- [ ] Bordas visiveis demais (1px solid #333) → Trocar para rgba(255,255,255,0.06)
- [ ] Bordas uniformes em tudo → Variar: 0.06 para sutis, 0.10 para visiveis, accent para focus

### Cards
- [ ] Box-shadow unica → Trocar por 3 camadas (near, medium, far)
- [ ] Sem hover effect → Adicionar y:-2px + shadow expansion + accent tint
- [ ] Border-radius 4px ou 8px → Padronizar para 12-16px
- [ ] Sem backdrop-filter → Adicionar blur(8px) com background semi-transparente

### Tipografia
- [ ] Uma unica fonte → Adicionar font pairing (display + body)
- [ ] Headings em bold (700) → Experimentar light (300) com tracking -0.02em
- [ ] Labels sem tratamento → Uppercase, 11px, letter-spacing 0.2em, weight 700
- [ ] Numeros desalinhados em listas → Ativar tabular-nums (font-feature-settings: "tnum")
- [ ] Line-height apertado no body → Aumentar para 1.75

### Cores
- [ ] Multiplas cores de destaque → Reduzir a UMA cor accent
- [ ] Accent aparece so em botoes → Espalhar sutilmente (focus rings, bullets, barras, tints)
- [ ] Cores semanticas sem hierarquia → Badges coloridos com background 10% + border 20%

### Inputs / Forms
- [ ] Input com background branco/cinza claro → Trocar para rgba(255,255,255,0.03)
- [ ] Focus ring azul default → Focus ring com cor accent + background tint
- [ ] Border-radius pequeno → Padronizar 10-12px
- [ ] Placeholder igual ao texto → Opacity 0.5, peso 300

### Botoes
- [ ] Botao flat com cor solida → Gradiente 135deg (accent → accent-light)
- [ ] Sem hover effect → Adicionar y:-2px + glow shadow com cor accent
- [ ] Sem active effect → Adicionar scale(0.98)
- [ ] Sem sheen/shimmer → Pseudo-element ::before com gradiente branco no hover

### Loading
- [ ] Spinner circular generico → Substituir por skeleton com shimmer
- [ ] Texto "Carregando..." → Shimmer text animado ou loading dots
- [ ] Layout pula ao carregar → Skeleton preserva layout (mesmas dimensoes)

### Animacoes
- [ ] Sem animacoes → Adicionar fade-up (20px, 0.5s) nos elementos
- [ ] Transition ease 300ms → Spring physics (stiffness: 300-400, damping: 25-30)
- [ ] Tudo aparece de uma vez → Stagger (0.08-0.1s delay entre items)
- [ ] Hover muda so cor → Hover com y:-2px + shadow + accent tint

### Detalhes Premium
- [ ] Scrollbar default do browser → Customizar (6px, cor do border)
- [ ] Selection azul → Selection com cor accent
- [ ] Sem ::before/::after decorativos → Adicionar accent line, sheen, glow ring
- [ ] Empty state = "Sem dados" → Texto guia + ilustracao + CTA

---

## Tabela Comparativa Detalhada

| Aspecto | Generico | Premium |
|---------|----------|---------|
| **Background** | `#000` ou `#fff` flat | `#09090b` + gradient mesh sutil |
| **Borders** | `1px solid #333` opaco | `1px solid rgba(255,255,255,0.06)` |
| **Shadows** | `box-shadow` unica | 3 camadas (near, medium, far) |
| **Cards bg** | Cor solida | `rgba(24,24,27,0.6)` + backdrop-blur |
| **Card hover** | Nenhum ou color change | y:-2px + shadow expansion + accent tint |
| **Card radius** | 4px ou 8px | 12-16px |
| **Typography** | Uma fonte, pesos padrao | Font pairing display+body |
| **Headings** | Bold (700) | Light (300) ou Extra Bold (800) -0.03em |
| **Labels** | 14px normal | 11px uppercase 0.2em weight 700 |
| **Body lineheight** | 1.5 | 1.75 |
| **Accent** | Varias cores | UMA cor accent unica |
| **Focus ring** | Azul default browser | Accent color + ring offset |
| **Input bg** | Branco ou cinza claro | rgba(255,255,255,0.03) |
| **Input focus** | Borda azul | Border accent + bg tint + glow ring |
| **Button** | Cor solida flat | Gradiente 135deg + glow + sheen ::before |
| **Button hover** | Darken | y:-2px + colored shadow |
| **Button active** | Nenhum | scale(0.98) |
| **Loading** | Spinner | Skeleton shimmer |
| **Transitions** | ease 300ms | Spring (stiffness 300, damping 30) |
| **Reveal** | Tudo aparece junto | Stagger 0.08s + fade-up 20px |
| **Hover global** | Color change | y:-2px + shadow + tint |
| **Scrollbar** | Default browser | 6px, cor do border |
| **Selection** | Azul default | Accent color |
| **Empty state** | "Nenhum dado" | Ilustracao + guia + CTA |
| **Whitespace** | Minimo | Generoso, funcional |
| **Data** | Tabela padrao | Cards com hierarquia + badges |
| **Numbers** | Proportional | Tabular-nums |
| **Icons** | Size padrao, cor default | Proporcionais, cor muted |

---

## Ordem de Prioridade de Upgrade

Se o tempo for limitado, aplicar nesta ordem (maior impacto primeiro):

1. **globals.css** — Variaveis, classes utilitarias, keyframes
2. **Cards** — glassmorphism + hover + shadows em camadas
3. **Tipografia** — Font pairing + scale + features
4. **Inputs/Botoes** — Focus ring accent, gradiente, micro-animacoes
5. **Scroll reveal** — Fade-up com stagger
6. **Background** — Gradient mesh + decorative blurs
7. **Detalhes** — Scrollbar, selection, badges, empty states

---

## Pesquisa Complementar (Quando Usar)

Ativar pesquisa dinamica quando:
- O contexto exige algo especifico do nicho (ex: fintech tem padroes diferentes de saude)
- O usuario menciona referencia especifica ("quero parecido com Linear", "estilo Stripe")
- Precisa de componente que nao esta nos recipes (ex: drag-and-drop, chart, timeline)

Ferramentas disponiveis:
- **MCP 21st Magic** — Buscar componentes UI de inspiracao (searchQuery: "dark dashboard", "wizard form", etc)
- **WebSearch** — Tendencias especificas, exemplos de sites
- **Aceternity UI** — Efeitos avancados (spotlight, tracing beam, wavy background)
- **Magic UI** — Border beam, shimmer button, number ticker, marquee
