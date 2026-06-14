---
name: replicar-sistema
description: Pipeline completo para replicar o design de qualquer sistema a partir de foto/print OU VIDEO (screen recording) e construir um sistema real com aquela cara. Fluxo validado: extracao cirurgica do design system (video vira frames via ffmpeg + notas de movimento) -> mockup HTML canonico de alta fidelidade (aprovado pelo usuario ANTES de codar) -> tokens semanticos no Tailwind -> telas em ondas (Agent Teams se grande) -> quality gate visual + auditoria de completude (skill auditar-fidelidade: renderizar a referencia e achar features/recursos faltando, nao so o visual). Use quando o usuario manda print, foto ou video de um sistema, app ou dashboard e quer "fazer igual", "replicar esse design", "criar meu sistema com essa cara", "quero um sistema assim", "clonar esse visual pro meu app", "replica esse sistema", "replica desse video". NAO e para clonar sites de marketing por URL (isso e /clonar-site); aqui a entrada e IMAGEM/VIDEO e a saida e um SISTEMA do usuario com o design da referencia.
---

# Replicar Sistema a partir de Foto

Replicar o design do print em um sistema real: $ARGUMENTS

Filosofia (validada no build do My Zap Money): a foto NAO e o alvo final, e materia-prima.
O que separa resultado mediano de resultado perfeito e o passo intermediario:

```
FOTO -> EXTRACAO (tokens) -> MOCKUP HTML CANONICO (aprovar!) -> TOKENS NO CODIGO -> TELAS EM ONDAS -> VERIFICACAO VISUAL
```

REGRA DE OURO: nunca pular o mockup. Codar direto da foto perde as decisoes de design
que dao identidade. O mockup e barato de iterar (1 arquivo HTML); o sistema e caro.
O mockup aprovado vira o ALVO CANONICO de todo o resto do projeto.

## Fase 0 — Entender o pedido (2 perguntas no maximo)

1. Replicar o DESIGN (a cara) ou o PRODUTO (funcionalidades tambem)?
   Default: design da referencia + conteudo/funcionalidades DO PRODUTO DO USUARIO.
2. Qual e o produto do usuario e quais telas precisa? (dashboard, lista, form...)

Localizar a(s) referencia(s): caminho em $ARGUMENTS, ou a mais recente em docs/
(`ls -lt docs/*.{png,jpg,jpeg,webp,mp4,mov,webm,mkv} 2>/dev/null | head`).
Imagens: ler TODAS com a tool Read (visao).

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

## Fase 1 — Extracao cirurgica do design system

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

## Fase 2 — Mockup HTML canonico (O CORACAO desta skill)

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

## Fase 3 — Tokens semanticos no codigo

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

## Fase 4 — Implementacao em ondas

- **Pequeno (1-3 telas):** implementar direto, comecando pelo shell (sidebar/topbar)
  e componentes base (tokens.ts com fieldCls/btnPrimary..., Pill, Modal).
- **Grande (4+ telas):** Agent Teams (se disponivel: ToolSearch carrega TeamCreate etc;
  apresentar plano e aguardar GO). Onda 0 = fundacao (schema/tokens/shell) pelo lead;
  Onda 1 = telas em teammates paralelos com listas de arquivos DISJUNTAS.
- Cada teammate recebe no prompt: o `design-extraido.md`, o caminho do MOCKUP CANONICO
  (mandar ler com Read), a tabela de tokens e as regras de ouro da Fase 3.
- Proibir: hex hardcoded, mudanca de layout fora do espec, dois teammates no mesmo arquivo.

## Fase 5 — Quality gate: visual + COMPLETUDE (obrigatorio antes de "pronto")

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
