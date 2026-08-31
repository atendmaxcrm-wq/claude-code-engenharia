---
name: replicar-operador-trade
description: Pipeline validado para replicar o METODO de um operador de mercado (trader/day trade/opcoes) que ensina em video/Instagram, transformando em um AGENTE DE IA que analisa o mercado e emite sinais, rodando no n8n com Gemini + KB vetorial (pgvector) + Evolution WhatsApp. Fluxo: descobrir e destilar o metodo do perfil (Apify/transcricao + Gemini) -> fundamentar com deep-research (a metodologia real por tras de cada regra) -> construir a KB (documento-fonte com marcadores de fidelidade -> KB destilada com tags) -> definir a API de dados de mercado (candles gratis) -> escrever o prompt do agente analista (padrao Gemini, funil de decisao, honestidade embutida) -> montar o encanamento n8n (gatilho -> busca dados -> Code calcula indicadores -> agente + info_trader -> WhatsApp). Use quando o usuario quiser "replicar o metodo desse trader", "criar um robo que opera igual fulano", "transformar a estrategia desse canal/perfil num agente", "quero um agente de sinais baseado em X", ou mandar link de YouTube/Instagram de alguem que ensina a operar e pedir pra automatizar. NAO e conselho financeiro nem promessa de lucro: a saida e um sistema de ANALISE com human-in-the-loop e honestidade estatistica embutida (sem edge = FICAR FORA). Validado no build do agente illumi.ai (NQ/Nasdaq).
---

# Replicar Operador de Trade em Agente de IA

Transformar o metodo de um operador que ensina publicamente em um agente de IA que analisa o mercado e emite sinais disciplinados. Alvo: $ARGUMENTS

Filosofia (validada no build do agente illumi.ai para NQ/Nasdaq): o video/post do operador
NAO e a fonte de conteudo, e o INDICE. Ele diz QUAIS tecnicas usa; a substancia real vem da
pesquisa profunda de cada tecnica. E o agente nunca "adivinha" o metodo: ele consulta uma KB
vetorial. A honestidade e parte do produto: onde nao ha edge comprovado, o agente diz e fica
de fora. Isso e o que separa um agente util de mais um papagaio de indicador.

```
PERFIL (video/IG) -> DESTILAR o que ele faz -> FUNDAMENTAR (deep-research) ->
KB (doc-fonte -> destilada com tags) -> API DE DADOS -> PROMPT (Gemini) -> n8n (encanamento)
```

REGRA DE OURO: separar sempre o que o operador REALMENTE faz (ancorado no material dele) do
que e fundamentacao de pesquisa (refino opcional). Marcadores [FONTE]/[FUND]/[MATE] na KB
impedem o agente de inflar o metodo com coisa que o operador nunca disse. Sem isso, a KB vira
ICT/indicador generico de YouTube e o agente perde fidelidade.

## Fase 0 - Escopo (poucas perguntas, com defaults)

1. **Qual o perfil/referencia?** URL de YouTube, Instagram, ou nome do operador. Se so o nome,
   pesquisar o canal/perfil principal.
2. **Qual mercado e instrumento?** (indice/futuro tipo NQ, forex, cripto, acoes, opcoes binarias).
   Isso decide a API de dados e o formato do sinal.
3. **Qual plataforma de execucao?** (so pra colocar o link no sinal e checar se demo existe).
   Default: comecar em conta DEMO, human-in-the-loop (a IA analisa, o humano clica).

Perguntar so o que muda o pipeline. O resto assume default e informa.

## Fase 1 - Descobrir e destilar o metodo do perfil

O objetivo e catalogar EXAUSTIVAMENTE o que o operador faz, ancorado no material dele.

### Instagram
Usar o pipeline de [[project-pipeline-replicacao-perfis-ig]]: Apify `apify~instagram-scraper`
(directUrls dos POSTS, resultsType posts, addParentData true), baixar assets, extrair audio
(ffmpeg mp3 16k) e frames, e o Gemini transcreve + analisa cada post em JSON estruturado.
GOTCHA de chave: usar a `GOOGLE_API_KEY` (formato AIza) do monitor-server .env; a
`GEMINI_API_KEY` (formato AQ. OAuth) FALHA no endpoint REST `?key=`. Ver
[[gotcha-gemini-shim-max-completion-tokens]].

### YouTube
Nao e "scraping", e TRANSCRICAO (o que ele fala = o metodo). Ordem de tentativa:
1. `oembed` para titulo/autor sem bloqueio:
   `curl -s "https://www.youtube.com/oembed?url=VIDEO_URL&format=json"`
2. Transcricao: a VPS costuma tomar bloqueio anti-bot no yt-dlp e no timedtext direto (IP
   flagado, ver memoria). Alternativas: servicos web de transcricao (WebFetch em
   youtubetotranscript.com, tactiq.io, notegpt.io passando a URL), ou a skill `yt-search` do
   projeto, ou pedir a legenda por um proxy/MCP. Se nada funcionar, cair para fontes
   secundarias (resumos, resenhas, descricao, comentarios) e ser explicito sobre a lacuna.

### Saida da Fase 1
Um catalogo (extracao) marcando cada item [DITO] (ele fala) vs [TELA] (visto em print/grafico),
ancorado no video/post: vies/direcao, gatilho de entrada, ponto de entrada, stop/saida, alvo,
gestao de risco, instrumentos, horarios, e as LACUNAS (o que ele diz que faz mas nao detalha,
que a Fase 2 vai fundamentar).

## Fase 2 - Fundamentar com deep-research

Para cada tecnica que o operador usa, uma pesquisa profunda da metodologia REAL por tras.
Rodar via Workflow com deep-research por tema (ancorado no que ELE faz, nao no vacuo), depois
consolidar. Cada relatorio deve:
- Fundamentar cada regra dele com fontes confiaveis (consenso, nao um blog so).
- Ser escrito para um AGENTE aplicar: regras objetivas checaveis em dados de candle (OHLC, EMA,
  RSI, niveis calculados), valores concretos.
- Ser HONESTO sobre edge: onde nao ha comprovacao estatistica publica, dizer. O agente nao pode
  vender certeza que a fonte nao suporta. (No build illumi: Faber tem edge no 200MA diario;
  ICT/RSI intraday nao tem backtest publico robusto. Isso virou o nucleo de honestidade da KB.)

## Fase 3 - Construir a KB (dois estagios)

**Estagio A - documento-fonte** (o "livro-texto"): funde extracao + fundamentacoes + verificacao
adversarial. Estrutura de MANUAL OPERACIONAL, cada secao = uma decisao. Para CADA regra: a REGRA
(o que o operador faz), o PORQUE (fundamentacao com fonte), COMO RECONHECER (condicao objetiva
em candle). Sistema de fidelidade obrigatorio, 3 marcadores:
- `[FONTE]` / `[<operador>]` = regra real dele, ancorada no material.
- `[FUND]` = fundamentacao de pesquisa que ele NAO verbaliza; refino opcional, nunca como regra dele.
- `[MATE]` = matematica universal (sizing, expectancia, breakeven).
Terminar com um CHECKLIST de decisao: funil ordenado de N passos, cada passo [OBRIGATORIO]
(falhou = fora, para o funil) ou [PESO] (rebaixa confianca). Default = FICAR FORA.

**Estagio B - KB destilada** (a "cola de prova"): reformatar no padrao da skill Gemini de KB.
Cada bloco vira `## <TIPO>: <titulo>` + linha `Tags: ...` (termos de busca pro retrieval).
Tipos: REGRA, REFERENCIA, CHECKLIST, LIMITE. Cortar URLs, discussao academica, o PORQUE longo:
a KB carrega o FATO e a CONDICAO CHECAVEL. Preservar as regras [FONTE], as formulas fechadas, o
checklist inteiro, e os LIMITES de honestidade (nunca cravar win rate; edge esta na gestao de
risco, nao no sinal; default FICAR FORA). Verificar por diff que nenhuma regra/formula/passo se
perdeu e que marcadores nao foram trocados (nao inflar o metodo). Ver `ai-agent-prompt-builder-gemini`.

## Fase 4 - Definir a API de dados de mercado

O agente precisa dos candles do ativo. Regras aprendidas (build NQ):
- Dados de FUTUROS da CME (NQ/MNQ) sao licenciados/pagos; quase nenhuma API gratis entrega.
  Saida: PROXY gratis que anda junto (QQQ para o Nasdaq, correlacao ~0.95) + o ativo real so
  para os niveis exatos (Yahoo `NQ=F`, endpoint nao-oficial). Para forex/cripto, geralmente ha
  candle gratis do proprio ativo.
- Titular recomendado: **Twelve Data** (plano gratis 800 req/dia, tem `interval=4h` NATIVO,
  JSON limpo). Apoio: **Yahoo** `query1.finance.yahoo.com/v8/finance/chart/SIMBOLO` (precisa
  header `User-Agent: Mozilla/5.0`, vem em listas paralelas com nulls, agregar H1->H4 no codigo).
  Upgrade quando precisar do futuro real barato: **Databento** ($125 credito, historico de
  candle fechado nao paga base fee da CME).
- Pegadinha: proxy tipo QQQ so negocia no RTH -> gap de abertura vira falso rompimento; virar
  regra na KB ("primeiro candle do dia pode ser gap, descontar"). Sempre descartar o candle em
  formacao (anti-repaint) antes de calcular indicador.
- `outputsize`: EMA200 precisa de 200 candles so pra nascer; pedir ~400-500 pra ela estabilizar.

## Fase 5 - Escrever o prompt do agente analista

Usar a skill `ai-agent-prompt-builder-gemini`. E um agente ANALITICO (nao conversacional): sem
tom caloroso, sem objecoes de venda. Adaptar a estrutura:
- Identidade funcional (analista, nao teatral). Emite UM de tres vereditos: ENTRAR / FICAR FORA
  (formato do ENTRAR depende do instrumento: entrada/stop/alvo/RR para futuros; CALL/PUT + prazo
  para binarias).
- Tool `info_trader` (RAG na KB, pgvector) com descricao FORTE de QUANDO usar (alavanca nº1
  anti-sub-chamada: "consulte SEMPRE antes de aplicar qualquer regra do funil"). QUANDO NAO usar.
- Fluxo = o funil de N passos da KB (aponta pra KB, nao repete os limiares no prompt).
- Verificacao em dois passos anti-alucinacao (dado faltante -> FICAR FORA, nunca inventar).
- Regras Invioaveis no FIM (nunca executar ordem; nunca cravar win rate; sempre consultar
  info_trader; so candle fechado; default FICAR FORA; frase de honestidade em todo ENTRAR).
- Config de deploy (fora do prompt): `thinking_level: medium`, `temperature: 1.0`. Evitar a tool
  `think` explicita: em teste ficou lenta e o thinking nativo do medium ja cobre.
- Contexto Variavel: ensinar o agente a LER o campo injetado (nomes exatos dos campos do Code
  node: candles, indicadores ja calculados, preco atual, avisos). O agente NAO recalcula: compara.

## Fase 6 - Montar o encanamento n8n

Arquitetura (dados viram NOS antes do agente; o agente NAO tem tool de buscar preco):
```
Gatilho (Schedule cron nos horarios do mercado, OU webhook TradingView se plano pago)
  -> HTTP Request dados principais (ex Twelve Data) -> Aggregate
  -> HTTP Request dados de apoio (ex Yahoo) -> Aggregate
  -> Code node (normaliza, casa timestamps, tira nulls, agrega TF, CALCULA EMA/RSI, descarta
     candle em formacao, monta objeto limpo)
  -> Aggregate (vira campo unico dados_mercado)
  -> AI Agent (Gemini + info_trader/pgvector + embeddings Gemini)
  -> Evolution API (manda o sinal no WhatsApp)
```
Detalhes que morderam no build:
- O Code faz as CONTAS (indicadores), o agente toma as DECISOES. Nao pedir a EMA200 pro LLM
  (ele erra media de 200 numeros); JS calcula exato.
- Aninhamento do Aggregate: `chart.result` do Yahoo JA e array, entao apos Aggregate o objeto
  fica em `resultados_nq[0][0]` (dois niveis), nao `[0]`.
- Input do agente: `{{ JSON.stringify($json.dados_mercado[0], null, 2) }}` (o `[0]` tira o array).
  JSON indentado e o formato IDEAL pra LLM (nao "string dificil"); nao separar em campos.
- Data/hora: injetar `$now.setZone('America/Sao_Paulo')` no input; o sinal mostra hora de Brasilia
  pro humano, mas os gates internos raciocinam em ET (horario do mercado) lido do datetime do candle.
- Timezone do n8n: se estiver em UTC, o cron dispara adiantado e pega mercado fechado. Confirmar
  `America/Sao_Paulo` (ou setar no Schedule node), senao sempre da FICAR FORA por horario.
- Acentuacao: texto do sinal COM acento PT-BR; queries do info_trader SEM acento (KB indexada sem
  acento, buscar com acento piora o retrieval).

## Fase 7 - Validar

Testar com "Execute Workflow" manual (nao esperar o cron). Fora do horario de mercado o agente
CORRETAMENTE da FICAR FORA no passo de tempo: isso valida o funil, mas para ver um ENTRAR
completo, testar em horario de pregao OU forcar um candle de teste com horario valido. Conferir:
o agente consulta info_trader na ordem do funil (log das queries), a mensagem chega no WhatsApp,
acentuacao e hora de Brasilia corretas. Ativar o workflow (toggle Active) so quando o timezone
estiver confirmado.

## Adaptacoes por tipo de mercado

- **Futuros/indices (validado: NQ)**: entrada/stop/alvo/RR, sizing por contrato, gates de mesa
  proprietaria se aplicavel. Proxy gratis + ativo real pros niveis.
- **Forex/cripto**: candle gratis do proprio par costuma existir; sinal com entrada/stop/alvo.
- **Opcoes binarias**: MUDA a filosofia. Nao ha stop/alvo/RR: aposta direcional CALL/PUT ate um
  prazo. Binaria paga ~80% no acerto e perde 100% no erro, entao exige win rate alto (~55%+ so
  pra empatar) em vez de R:R assimetrico. A KB e OUTRA (metodo de direcao curta), o formato do
  sinal e CALL/PUT + prazo, e a honestidade e ainda mais dura (errar custa 100%). Operar sobre
  ativo REAL (fora do OTC, onde a corretora fabrica o preco): o dado de mercado vem do ativo
  subjacente real (ex par forex), nao da corretora binaria.

## Etica e honestidade (nao negociavel)

A saida e ANALISE, nunca execucao (human-in-the-loop). Comecar em conta DEMO. A KB carrega os
limites: nunca prometer acerto, nunca cravar win rate, dizer quando nao ha edge comprovado, e
FICAR FORA como default. Isso protege o usuario de acreditar em edge inexistente e e o que da
credibilidade ao sistema. Nao vender numero infundado por amostra pequena.

## Formato de saida da skill

Entregar, versionados numa pasta do projeto:
1. `extracao-<operador>.md` - catalogo do metodo dele (Fase 1)
2. `kb-conhecimento-<operador>.md` - documento-fonte fundamentado (Fase 3A)
3. `kb-agente-<operador>.md` - KB destilada com tags (Fase 3B)
4. `recomendacao-api-dados.md` - qual API e passo a passo n8n (Fase 4)
5. `prompt-agente-<operador>-gemini.md` - system prompt (Fase 5)
6. `code-node-preparar-dados.js` - Code node do n8n (Fase 6)
7. descricoes das tools (`info_trader`) prontas pra colar
