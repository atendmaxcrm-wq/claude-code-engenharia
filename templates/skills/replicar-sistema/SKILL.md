---
name: replicar-sistema
description: Pipeline completo para replicar o design de qualquer sistema a partir de foto/print OU VIDEO (screen recording) e construir um sistema real com aquela cara. Fluxo validado: extracao cirurgica do design system (video vira frames via ffmpeg + notas de movimento) -> mockup HTML canonico de alta fidelidade (aprovado pelo usuario ANTES de codar) -> tokens semanticos no Tailwind -> telas em ondas (Agent Teams se grande) -> quality gate visual + auditoria de completude (skill auditar-fidelidade: renderizar a referencia e achar features/recursos faltando, nao so o visual). Use quando o usuario manda print, foto ou video de um sistema, app ou dashboard e quer "fazer igual", "replicar esse design", "criar meu sistema com essa cara", "quero um sistema assim", "clonar esse visual pro meu app", "replica esse sistema", "replica desse video". NAO e para clonar sites de marketing por URL (isso e /clonar-site); aqui a entrada e IMAGEM/VIDEO e a saida e um SISTEMA do usuario com o design da referencia.
---

# Replicar Sistema a partir de Foto

Replicar o design do print em um sistema real: $ARGUMENTS

Filosofia (validada no build do My Zap Money): a foto NAO e o alvo final, e materia-prima.
O que separa resultado mediano de resultado perfeito e o passo intermediario:

```
FOTO -> EXTRACAO (tokens) -> STYLEGUIDE HTML (aprovar) -> MOCKUP HTML CANONICO (aprovar!) -> TOKENS NO CODIGO -> TELAS EM ONDAS -> VERIFICACAO VISUAL
```

REGRA DE OURO: nunca pular o mockup. Codar direto da foto perde as decisoes de design
que dao identidade. O mockup e barato de iterar (1 arquivo HTML); o sistema e caro.
O mockup aprovado vira o ALVO CANONICO de todo o resto do projeto.

## Fase 0 - Entender o pedido (2 perguntas no maximo)

1. Replicar o DESIGN (a cara) ou o PRODUTO (funcionalidades tambem)?
   Default: design da referencia + conteudo/funcionalidades DO PRODUTO DO USUARIO.
2. Qual e o produto do usuario e quais telas precisa? (dashboard, lista, form...)

Localizar a(s) referencia(s): caminho em $ARGUMENTS, ou a mais recente em docs/
(`ls -lt docs/*.{png,jpg,jpeg,webp,mp4,mov,webm,mkv} 2>/dev/null | head`).
Imagens: ler TODAS com a tool Read (visao).

**Mineracao de referencia (enriquecer o print unico).** Um print so deixa ambiguidades
(como esse arquetipo trata hover? estado vazio? o dark? a tabela densa?). Antes de extrair,
garimpar 2-3 shots ADICIONAIS do MESMO arquetipo visual (Dribbble/Pinterest: a estetica que
o usuario quer, ex: "fintech dark lime", "invoices premium") e ler todos juntos. Destilar de
3-4 referencias concretas de alto nivel - em vez de adivinhar do print unico - ancora o
resultado em proporcoes e relacoes JA validadas por designers e resolve os casos que uma
imagem sozinha nao mostra. Registrar a origem no eyebrow/footer do styleguide ("destilado de
X · invoices"). Nao copiar conteudo das referencias - so a gramatica visual.

### Entrada em VIDEO (screen recording da referencia)

Claude nao assiste video direto; o video vira FRAMES (que a visao le) + NOTAS DE
MOVIMENTO (o ouro que a foto nao tem). Com ffmpeg:

```bash
mkdir -p /tmp/frames-replica
# 1) Cortes de cena (telas distintas): detector de mudanca
ffmpeg -i video.mp4 -vf "select='gt(scene,0.25)'" -vsync vfr -frame_pts 1 /tmp/frames-replica/cena-%04d.png
# 2) Amostragem regular 1fps (fluxos, estados intermediarios de animacao)
ffmpeg -i video.mp4 -vf fps=1 /tmp/frames-replica/seq-%04d.png
```

Protocolo:
1. Ler primeiro as `cena-*.png` (cada uma tende a ser uma TELA distinta) e mapear:
   quais telas existem, qual e a principal, navegacao entre elas.
2. Ler as `seq-*.png` em janelas onde houve transicao (frames vizinhos ao corte)
   para extrair MOVIMENTO: tipo de transicao (fade/slide/scale), direcao, o que
   anima (modal sobe? sidebar desliza? numero conta?), estados de hover visiveis.
3. Se houver MUITOS frames, ler em lotes os mais distintos (nao precisa ler 100% -
   priorize 1 frame nitido por tela + os pares antes/depois de cada transicao).
4. Registrar uma secao extra na extracao: **"Decisoes de movimento"** (duracao
   percebida, easing aparente, o que anima e o que e instantaneo). Ela alimenta o
   mockup (transicoes CSS) e depois a implementacao (interaction-patterns/gsap).
5. Se o video tiver narracao relevante, transcrever o audio e usar como contexto de
   requisitos (`ffmpeg -i video.mp4 -vn audio.mp3` + Whisper, se disponivel).

Frames sao descartaveis: limpar /tmp/frames-replica ao final.

## Fase 1 - Extracao cirurgica do design system

Se a skill `extrair-design-imagem` existir no projeto, invocar via Skill tool.
Senao, aplicar o protocolo inline (mesmo nivel de um designer destilando tokens):

- **Cores: hex + papel + regra de uso.** Nunca "tem roxo"; sempre
  "`#7C6BE0` Mid Purple - progress bars, icones ativos". Agrupar: superficies
  (canvas/card/painel escuro), trio cromatico de identidade (e a REGRA de cada uma,
  ex: "lime so em CTA/badge/ativo, nunca fundo de card inteiro"), escala de texto
  (heading/primario/secundario/muted), borda/divisor.
- **Tipografia por papel:** Display/H1/H2/H3/Body/Caption/Badge com size, weight,
  tracking, cor e exemplo real da imagem. Identificar familia provavel (Inter, Geist,
  Syne...) e de onde vem a "agressividade" (fonte ou size/weight/tracking).
- **Tokens:** radius (sm/md/lg/pill), spacing base e escala, card-padding,
  sidebar-width, sombra (flat? elevado? glow?), borda default.
- **Combos de contraste aprovados** (ex: Lime+Dark, Purple+White).
- **Decisoes notaveis** (a parte mais valiosa): "zero sombras, separacao por contraste",
  "numeros gigantes ~72px", "radius cresce com o componente".

Salvar em `docs/design-extraido-<slug>.md`. Nao inventar o que nao da pra ver;
marcar inferencias como "(aproximado)".

## Fase 1.5 - Styleguide HTML (antes das telas)

O passo do Kainan que mais elevou o resultado: antes de qualquer tela, gerar UM
`docs/<dominio>-design-system.html` renderizado e aprova-lo lado a lado com a referencia.
O styleguide NAO e documentacao pos-fato: e o contrato que torna telas (e ate dominios)
diferentes coerentes. Forca decidir cor/tipo/raio UMA vez, em isolamento, sem a pressao de
uma tela funcionar; depois toda tela so consome tokens ja decididos e nenhuma inventa um
cinza ou um raio novo.

O arquivo tem 6 secoes numeradas (badge com numero em accent + descricao a direita):
- **01 Paleta:** swatches com hex + papel + regra de uso ("`#8FF500` accent - so CTA/nav
  ativo/progresso, nunca fundo de card").
- **02 Tipografia:** specimen da fonte real (nome + classificacao, ex: "Lufga · geometrica
  humanista") e a escala por papel com size/weight/tracking rotulados ("300 · titulos",
  "500 · nav/labels", "800 · labels pequenos").
- **03 Raios e superficies:** os 7 raios visualizados + a inversao de superficie demonstrada.
- **04 Sombras e efeitos:** elevacao (spread negativo), glow duplo do acento, glass.
- **05 Componentes:** os controles REAIS que as telas vao reusar - botoes accent/dark/ghost,
  tabs com badge de contagem, chips, pills, avatares em stack, KPI/metrica, payment cards,
  estados (hover/ativo/done/vazio). A tela depois so COMPOE pecas ja aprovadas.
- **06 Tokens CSS:** o bloco `:root` + `[data-theme]` EXATAMENTE como vai pro codigo (mesmos
  nomes `--accent/--page/--panel/--ink/--line`, escalas `--r-*`, `--speed-*`, `--ease-*`).
  Esse bloco e colado VERBATIM no topo de cada tela; telas so consomem `var(--token)`.

Obrigatorio: toggle de tema FUNCIONAL e render/print nos DOIS temas (light + dark) como
checagem - pega cedo onde um token quebra contraste (ex: texto sobre lime sempre escuro).

So depois deste arquivo aprovado parte-se pra Fase 2 (telas). Regra de revisao: `#hex`
literal dentro do markup de uma tela (fora do `:root`) e bug - trocar por `var(--token)`.
Dominio novo (clinica, logistica) com a MESMA cara: duplicar o `:root` + temas e reescrever
SO o conteudo; o sistema visual e transversal a dominios.

> Em projetos que ja tem extracao forte na Fase 1, o styleguide e leve: e a Fase 1 montada
> como HTML navegavel + bloco de tokens copiavel. Vale o passo porque renderizar > ler texto.

## Fase 2 - Mockup HTML canonico (O CORACAO desta skill)

> **Regra de ouro de beleza:** uma fonte com personalidade + headline gigante-fino +
> UM acento que so marca acao + inversao de superficie - se faltar um desses quatro, ainda
> e mockup generico.

E o passo que muda o nivel do resultado. Gerar UM arquivo HTML autocontido com a cara
da referencia aplicada ao PRODUTO DO USUARIO, e iterar ate o usuario aprovar.

Checklist de qualidade do mockup (nivel "ficou perfeito"):
- **Autocontido:** CSS em `<style>`, Google Fonts e icones (Tabler) via CDN. Abre com
  duplo clique, zero build.
- **Conteudo REAL do produto do usuario:** nada de lorem ipsum nem de copiar o conteudo
  da referencia. Numeros plausiveis, rotulos em PT-BR do dominio dele.
- **A tela mais importante COMPLETA:** shell inteiro (sidebar + topbar + conteudo),
  cards de KPI, tabela/lista com 5-8 linhas reais, chart fake (SVG ou divs), estados
  (ativo, hover, badge, vazio). Se o usuario pediu mais telas, secoes empilhadas ou
  abas no proprio HTML.
- **Aplicar as DECISOES NOTAVEIS extraidas, nao so as cores.** Hierarquia agressiva
  dos numeros, espacamento generoso, flat se a referencia for flat, regra de uso de
  cada cor de identidade respeitada.
- **Responsivo basico** (uma media query pro mobile ja basta no mockup).
- **Se a fonte foi VIDEO:** aplicar as "Decisoes de movimento" como transicoes CSS
  reais no mockup (hover, modal, sidebar) - e o que faz o mockup "parecer o video",
  nao so a foto dele.
- Salvar em `docs/<produto>-mockup-v1.html`, mostrar ao usuario (servir ou abrir),
  **ITERAR** (v2, v3...) ate aprovacao explicita. A versao aprovada e o alvo canonico:
  registrar isso na memoria do projeto.

### Assets generativos (quando o mockup/telas precisam de imagem real)

Se o produto pede imagens que nao existem (hero com foto, fundos cinematograficos,
fotos de produto, avatares nao-genericos), NAO improvisar geracao solta: rodar a
**fabrica de assets** de `.claude/skills/site-elite-cinema/references/07-fabrica-assets.md`
(lista com orcamento aprovado -> prompt tecnico por asset com negative prompt de
fotorealismo -> geracao API ou manual -> validacao com veredito PASSA/ARTEFATO por
asset). So asset aprovado entra no mockup. Placeholder cinza no mockup v1 e valido;
asset slop nao e. Se o hero pedir transformacao/video scrubado, isso e
/site-elite-cinema (ramo D, `references/08-hero-transformacao.md`).

## Excelencia visual (rubrica do mockup)

Aprovar um mockup "ok" e o que produz sistema mediano. Esta rubrica e o sarrafo do
nivel "parece desenhado por designer, nao gerado". Aplicar item a item ao mockup da
Fase 2 e re-conferir no render. Validada no redesign do nosso dashboard
(docs/prints/myzap-dashboard-redesign.html): Lufga + headline gigante-fino +
inversao de superficie + acento contido.

### Tipografia
- [ ] UMA familia geometrica-humanista pra 100% da UI (Lufga; gratis: Manrope, Onest,
      Geist). Stack com fallback que mantem o DNA: `'Lufga','Manrope','Inter',ui-sans-serif`.
      ZERO segunda familia pra titulo. Carregar pesos 300;400;500;600;700;800 de uma vez.
- [ ] Headline gigante-fino: H1 `clamp(46px,6vw,82px)`, weight `300-500` (NUNCA bold),
      `letter-spacing:-.075em`, `line-height:.88-.96`, `margin:0`. Quanto maior o titulo,
      mais negativo o tracking e mais leve o peso.
- [ ] Pesos por papel (inversao deliberada): 300 = display/metrica grande; 400 = numero
      medio; 500 = nav/labels/titulo de pagina; 600 = subtitulo/destaque; 700 = H2 secao;
      800 = label PEQUENO/badge/botao/nav/brand. Regra: texto <16px funcional = 700-800;
      texto >40px decorativo = 300-500.
- [ ] Metrica/KPI tratado como display: `font-weight:500`, `letter-spacing:-.06 a -.07em`
      (mais negativo que titulo), `line-height:.92`, `white-space:nowrap`, flex
      `align-items:baseline`. Numero hero NUNCA em bold.
- [ ] Cifrao e unidade rebaixados em span: `font-size:.46-.55em`, `color:var(--tmut)`,
      `font-weight:500-600`. Tamanho em `em` (escala com clamp), nao px. Superscript do
      simbolo via `vertical-align` positivo, nunca `<sup>`.
- [ ] Tracking por faixa: >40px `-.06 a -.075em`; 20-40px `-.03 a -.05em`; body 14-16px
      `-.01em`. Excecao: uppercase <14px (eyebrow, th de tabela, label de coluna) recebe
      tracking POSITIVO `+.04 a +.05em` + weight 800-900. Uppercase miudo com tracking 0
      e preguica.

### Cor e acento
- [ ] UM unico acento quente, e ele significa ACAO ou ESTADO ATIVO (nav ativo, CTA, item
      concluido, progresso, toggle on, card em foco). Nunca decoracao (titulo, icone solto).
- [ ] Escassez do acento: 1 a 3 pontos quentes por viewport. Contar no render; acima de 3,
      rebaixar os menos importantes pra neutro ou pra versao soft (cor a ~16% alpha).
- [ ] Base 100% neutra fria: pagina/superficies/bordas/texto so com cinzas frios (vies azul).
      No maximo UM neutro com leve matiz (steel-blue) pro painel de detalhe. Nada mais ganha
      cor exceto o acento e os 2 estados.
- [ ] Texto sobre o acento e SEMPRE ink escuro fixo (`#071006`/`#0e1a00`), hardcoded fora do
      sistema de tema, pra contraste garantido nos 2 modos (token viraria branco e sumiria).
- [ ] Danger/warning NUNCA preenchem botao nem viram bloco chapado. Trio do mesmo hex: texto
      = hex puro, fundo = hex a 13-16% alpha, borda = hex a 24-25% alpha. Preenchimento solido
      e glow sao exclusivos do acento. Sucesso pode ser o proprio acento.
- [ ] Acento com profundidade: gradiente vertical sutil (tom +claro no topo -> accent na base,
      ~4-5% de luminancia) + glow duplo na cor + `inset 0 1px 0 rgba(255,255,255,.45)`. Lime
      chapado fica plastico.

### Superficie e profundidade
- [ ] Escala de 7 raios proporcional ao tamanho: xs=12 / sm=18 / md=26 / lg=36 / xl=48 /
      xxl=58 / pill=999. Shell-hero 48-58px; card padrao 26-38px; input/botao/chip-acao = pill;
      tag/badge interna 12-18px. Nunca o mesmo raio num painel de 600px e num botao de 40px.
- [ ] Sombra de elevacao com offset Y grande + spread NEGATIVO (sombra macia, curta, "pousada"):
      light `0 18px 44px -26px rgba(40,60,90,.5)`, dark `0 24px 54px -30px rgba(0,0,0,.7)`.
      Tonalizar com a cor do fundo, NUNCA preto puro. Combinar com `inset 0 1px 0 rgba(255,255,255,.09)`.
- [ ] Glow do acento = halo DUPLO na propria cor (curto+forte e longo+fraco):
      `0 0 18px rgba(143,245,0,.34), 0 0 48px rgba(143,245,0,.16)`. So no acento. Sombra cinza
      em botao verde mata o brilho.
- [ ] Inversao de superficie (a jogada-mestra): o painel-ancora e o OPOSTO de luminancia da
      pagina. Canvas escuro -> bloco branco `#FFF`; canvas claro -> bloco `#1C2024`. Raio grande
      (44-58px) reforca o efeito "folha pousada". Texto dentro inverte junto (cor fixa).
- [ ] Glass de verdade = 4-5 camadas, nao so backdrop-filter: gradiente diagonal 135-142deg
      entre 2 superficies (~.82 e ~.92 alpha) + `backdrop-filter:blur(20-30px) saturate(1.15-1.2)`
      + borda branca 8-12% + `::after` sweep de luz 120deg + `::before` glow radial. O saturate
      reanima a cor atras (sem ele o blur deixa tudo cinza-morto).
- [ ] Ritmo de espaco: o espaco MORA dentro dos cards. Padding interno 32-54px; gap entre cards
      14-18px. Regra: padding interno >= 2x o gap do grid. Metricas dentro do card com gap maior (~40px).

### Componentes
- [ ] Estado ativo unificado (o MESMO gesto em nav/tab/method-card/switch/badge): gradiente lime
      vertical + glow duplo + texto `#071006` + `inset 0 1px 0 rgba(255,255,255,.45)`. O olho
      reconhece "selecionado" sem ler.
- [ ] Badge de contagem dentro de pill inverte quando o pai fica ativo: bg semitransparente escuro
      no normal; solido escuro `#12141C` + texto branco no ativo (pra nao sumir sobre o lime claro).
- [ ] Hachura diagonal pra tudo "nao confirmado/vazio/secundario":
      `repeating-linear-gradient(135deg, cor-fraca 0 7px, cor 7px 14px)`. Vale ate pra barra de
      progresso (dois tons do acento em bandas de 6-7px = sensacao de material).
- [ ] Pilha de avatares: `margin-left:-13px` (zerando o primeiro), border de 3px na COR DA
      SUPERFICIE (token, nao branco fixo), preenchimento `linear-gradient(135deg, corA, corA-escura)`.
- [ ] Anel de progresso sem SVG: `conic-gradient(var(--accent) var(--p), trilha-fraca 0)` num circulo
      + `::after inset:10px` com a cor EXATA da superficie do card (token por tema) abrindo o furo.
- [ ] Iconografia 100% line: `fill:none; stroke:currentColor; stroke-width:1.7-1.8;
      stroke-linecap/linejoin:round`, grid 24, renderizado 20-22px. Herdar currentColor pra seguir
      o estado. NUNCA misturar solid com stroke.
- [ ] Hover universal de micro-elevacao 1-3px com 2 easings nomeados: `--ease-smooth
      cubic-bezier(.22,1,.36,1)` pra mover/hover, `--ease-snap cubic-bezier(.16,1,.3,1)` pra
      entradas. Botao/card `translateY(-2px)`; linha de lista `translateX(3px)`. Velocidades
      160/260/520ms. Gesto grande (scale/rotate) so no toggle de tema.

### Composicao
- [ ] Grade do hero assimetrica `1.55fr / 1fr` (ou `1.58fr/.98fr`), nunca 50/50. O lado largo e o
      protagonista.
- [ ] Cards-filhos que furam a base do pai: fileira de opcoes posicionada `absolute` no bottom, cada
      item com cantos so no topo (`border-radius:34px 34px 0 0`), o selecionado 30-40px mais alto +
      glow de acento, `align-items:end`, `overflow:hidden` no pai. A ALTURA comunica selecao mesmo
      em escala de cinza.

### Anti-slop: sinais de mockup generico a evitar
- Inter (ou system-ui) em TUDO -> usar geometrica-humanista com personalidade.
- Header em bold/600 medio "tamanho de subtitulo" -> headline gigante-fino 300-500.
- Acento espalhado (titulo colorido, icones decorativos, varios botoes lime) -> 1-3 pontos quentes.
- Numero KPI em bold sem tracking, com R$ do mesmo tamanho boiando -> weight 500, tracking -.07em,
  cifrao/unidade rebaixados.
- Dark uniforme (tudo no mesmo cinza-chumbo, sem figura-fundo) -> inversao de superficie.
- Flat sem ritmo: todos os cards com mesmo raio, mesmo gap, sombra preta dura -> escala de 7 raios,
  padding interno > gap, sombra com spread negativo tonalizada.
- Tudo em weight 600/700 (cara de bootstrap) -> mapa de pesos por papel.
- Lime chapado e glow cinza -> gradiente vertical + halo duplo na cor.

## Fase 3 - Tokens semanticos no codigo

Wirar o design aprovado como tokens SEMANTICOS (Tailwind v4: bloco `@theme` no
globals.css). Nomear por papel, nunca por cor: `canvas/paper/panel/ink/ink2/tsec/
tmut/line` + trio de identidade + `pos/neg/warn` (status).

Gotchas reais (aprendidos em producao no My Zap):
1. **Texto sobre cor de identidade CLARA (lime etc) e SEMPRE fixo escuro** (`#111`),
   nunca token de tema. Se um dia houver dark mode, token de texto vira branco e some.
2. **Cores-DADO nunca tokenizar:** cor da empresa, do perfil, color-picker salvos no
   banco sao dado, nao tema.
3. **Tailwind v4 cacheia o @theme:** mexeu no bloco, limpar/mover `.next` antes do build.
4. **Telas usam SO tokens desde o dia 1** (nada de hex hardcoded em className/style).
   Isso torna dark mode quase gratis depois: so um bloco `.dark` redefinindo os
   semanticos + `@custom-variant dark (&:where(.dark, .dark *))` + cookie de tema
   aplicado no `<html>` via SSR (com `suppressHydrationWarning`).

## Fase 4 - Implementacao em ondas

- **Pequeno (1-3 telas):** implementar direto, comecando pelo shell (sidebar/topbar)
  e componentes base (tokens.ts com fieldCls/btnPrimary..., Pill, Modal).
- **Grande (4+ telas):** Agent Teams (se disponivel: ToolSearch carrega TeamCreate etc;
  apresentar plano e aguardar GO). Onda 0 = fundacao (schema/tokens/shell) pelo lead;
  Onda 1 = telas em teammates paralelos com listas de arquivos DISJUNTAS.
- Cada teammate recebe no prompt: o `design-extraido.md`, o caminho do MOCKUP CANONICO
  (mandar ler com Read), a tabela de tokens e as regras de ouro da Fase 3.
- Proibir: hex hardcoded, mudanca de layout fora do espec, dois teammates no mesmo arquivo.

## Fase 5 - Quality gate: visual + COMPLETUDE (obrigatorio antes de "pronto")

1. `tsc --noEmit` + build limpo (mover `.next` se mexeu no @theme).
2. **Renderize a REFERENCIA (rode o JS dela), nao audite so o HTML estatico.** Mockup
   monta telas/widgets/temas em runtime; capture TODAS as views (clicar `[data-view]`)
   nos DOIS temas como ground truth em /tmp/ref-render*/. (Foi o furo do My Zap v10:
   li o estatico e perdi a dashboard rica + features que so existem no JS.)
3. **Screenshots do app com sessao real** (forjar cookie JWT com o secret do .env) em
   mobile (390px) e desktop, nos DOIS temas. Overflow: meça POR ELEMENTO
   (`getBoundingClientRect().right > innerWidth`), nao so `scrollWidth-clientWidth`
   (que esconde blowout clipado). Erros de console = 0.
4. **Comparar lado a lado** cada tela do app com o render da referencia (claro E escuro).
5. **Auditoria de COMPLETUDE (nao so visual): rode a skill `auditar-fidelidade`.** Ela
   enumera funcoes/handlers/modais/settings do JS da referencia e acha RECURSOS faltando
   (galeria de tema, telas de detalhe, campos de modal, botoes mortos, simuladores
   estaticos). Fidelidade visual NAO garante que as features existem.
6. Rodar `safari-check` se a skill existir; mostrar os prints ao usuario e iterar.

## Anti-padroes (o que mata o resultado)

- Pular o mockup e codar direto da foto (resultado generico).
- Copiar o CONTEUDO da referencia em vez do design dela.
- Hex hardcoded espalhado nas telas (divida tecnica que explode no dark mode).
- Declarar "pronto" sem screenshot autenticado da tela real.
- Encher o usuario de perguntas: 2 perguntas na Fase 0, GO no plano (se Agent Teams),
  aprovacao do mockup. O resto e decisao tecnica sua.

## Notas

- PT-BR com acentuacao correta; sem travessao (em-dash).
- Caso exemplo completo: My Zap Money (print -> extracao "FLUX" -> mockup
  my-zap-money-mvp-v2.html aprovado -> @theme tokens -> 14 telas em ondas ->
  dark mode quase gratis depois, porque tudo era token).
