---
name: codar-em-ondas
description: Pipeline de CODIGO em ondas (o motor que constroi o sistema real, irmao da pipeline-fiel que faz os mockups). Transforma mockups aprovados + blueprint-texto + PLANO em codigo verificado, modulo a modulo, em 3 fases com paralelismos DIFERENTES: (A) SPEC de logica por modulo (paralelizavel, agent-teams em leque, o dono aprova); (B) FUNDACAO solo e sequencial (scaffold + tokens + shell + component lib + camada de dados + auth + guard multi-tenant, junto do 1o modulo, NAO paralelizavel, e o contrato de que tudo depende); (C) MODULOS em paralelo DEPOIS da fundacao (agent-teams + git worktrees isolados, /entrega-verificada por modulo, gate de teste REAL build+test+health, aprovacao humana por modulo antes do merge). Compoe /entrega-verificada + agent-teams + git worktree. Roda sob /loop com pausa em fundacao-nao-pronta / decisao de produto / aprovacao de merge. Use quando o usuario disser "codar em ondas", "montar a spec e construir", "rodar /entrega-verificada em loop", "construir o sistema real dos mockups", "codar os modulos aprovados". NAO e pipeline-fiel (aquele faz MOCKUP/HTML); aqui a entrada e MOCKUP APROVADO e a saida e CODIGO no repo.
---

# Codar em Ondas (mockups aprovados -> codigo verificado, em ondas)

> Skill do CCE. Irma da pipeline-fiel, mas pra CODIGO. Nasceu no CRMAX 2.

Orquestrar a construcao de codigo em ondas: $ARGUMENTS

## Filosofia (a diferenca que muda tudo)
Codigo != mockup. Mockup e arquivo HTML INDEPENDENTE (paraleliza sem conflito). Codigo e UM projeto
Next.js COMPARTILHADO: scaffold, tokens, shell, component lib, schema de banco, tipos, router, auth,
tudo em comum. Nao da pra codar N modulos do zero em paralelo (cada um inventa o proprio contrato e
nao fecha no merge). E: mockup que "parece certo" esta pronto; CODIGO que "parece certo" pode estar
QUEBRADO. Logo o gate e verificacao REAL (build + testes + health), nunca eyeball. Fundacao primeiro,
solo. Humano aprova por modulo (codigo e alto risco).

## Composicao (orquestrar, nao reinventar)
- **/entrega-verificada** = o motor POR MODULO (spec -> build em etapas testadas -> valida cada etapa).
- **agent-teams** = leque (na Fase A specs; e na Fase C modulos DEPOIS da fundacao).
- **git worktree** = isolamento por modulo na Fase C (cada teammate na sua worktree; evita merge hell).

## Fase 0 - Pre-requisitos (o que ela CONSOME)
- **MOCKUP APROVADO (OBRIGATORIO)** = alvo visual/UX/campos canonico (ex.: docs/mockups-aprovados/).
- **BLUEPRINT-TEXTO (OPCIONAL, define a PROFUNDIDADE da spec):** a LOGICA / data model / regras do
  sistema-fonte. COM ele (**Modo A**, ex.: CRMAX 2 replicando o Clinic Expert) a spec captura a
  PROVENIENCIA real ("x vem de y igual ao CE") + regras + ciclos de vida. SEM ele (**Modo B**,
  produto proprio greenfield) a spec INFERE a logica a partir do mockup + decisoes de produto:
  suficiente pra CRUD simples, arriscado pra logica complexa (comissao, split, FEFO, titulo->parcela->
  liquidacao). Regra: mockup = a CARA; blueprint = a LOGICA. Os dois juntos = fidelidade de logica.
- PLANO / modelo de dados de alto nivel (se houver) reforca a Fase A.
- Repo git inicializado (git init se ainda nao for). Stack alvo (ex.: Next.js 16 + Tailwind v4 + Postgres/pgvector).
- BACKLOG-FIDELIDADE.md (gaps M/B dos mockups) pra resolver conforme cada modulo e codado.

## Fase A - SPEC de logica (PARALELIZAVEL; agent-teams em leque; loop-friendly)
1 spec-writer por modulo. Extrai de: o MOCKUP APROVADO (telas/campos/UX) + BLUEPRINT-TEXTO (logica,
data model, regras) + PLANO (modelo de dados). Saida por modulo em docs/specs/<modulo>.md:
- Entidades e campos; PROVENIENCIA de cada campo (stored / computed / derived de qual entidade / input / integracao) = o "x vem de y".
- Relacionamentos + cardinalidade; estados e transicoes (ciclos de vida); regras de negocio + validacoes.
- Endpoints/contratos de API; fluxos de dado entre modulos.
- O PLANO DE ETAPAS que o /entrega-verificada vai executar (cada etapa testavel).
Specs sao DOCUMENTOS -> sem conflito, paraleliza. Gate: consistencia + **o dono APROVA a spec**.
VERIFICACAO NA FONTE (CONDICIONAL): pros campos/regras que so um print vazio/mislabeled cobriria, SE
houver acesso AUTORIZADO ao sistema-fonte (conta propria do dono), usar `capturar-logica-saas` (login
READ-ONLY) pra ver a tela real antes de fixar a proveniencia na spec. So pros casos sem print bom;
senao, o TEXTO manda. Terceiro = so conta autorizada, read-only.

## Fase B - FUNDACAO (Wave 0, SOLO, NAO paralelizar, vem ANTES de tudo)
Uma sessao constroi o "chao" e SO ele congela o contrato:
- Scaffold real (Next.js) + tokens (do design system aprovado) + shell (sidebar/topbar/layout).
- Biblioteca de componentes base (data-table, drawer, modal, kpi-card, badges... extraidos dos mockups).
- Camada de dados: schema base + migrations + client; auth (OTP+JWT); organizacao/RBAC; guard multi-tenant fail-closed.
Feito JUNTO do 1o modulo (ex.: Agenda), que exercita e prova a fundacao. Gate: `build` + testes +
app SOBE + health OK. So congela quando passa. TUDO na Fase C depende deste contrato.

## Fase C - MODULOS (PARALELIZAVEL DEPOIS da fundacao; agent-teams + worktrees)
1 teammate por modulo, cada um em `isolation: worktree` (git worktree propria), rodando
**/entrega-verificada** contra a SUA spec (Fase A) + a fundacao congelada, em ETAPAS testadas.
- Conflito em arquivos compartilhados (schema/migrations, componentes, tipos, router) = pontos de
  merge: migrations numeradas/sem colisao; componentes so ADICIONAR (nao editar os da fundacao sem avisar o lead).
- Gate POR MODULO: `build` + testes do modulo passam + health-check dos endpoints + quality gate (code-review).
- Merge de volta via git. **APROVACAO HUMANA por modulo ANTES do merge.**
- Resolver os itens do BACKLOG-FIDELIDADE.md do modulo aqui (os fluxos CRUD materializam agora).

## MODO /loop
- **Fase A (specs):** loop paralelo; publica as specs; dono aprova no final.
- **Fase C (modulos):** loop, MAS PAUSA em: (1) fundacao nao congelada (bloqueia ate Fase B passar),
  (2) decisao de produto, (3) aprovacao de merge de cada modulo (NAO auto-merge codigo). Teste que
  falha se AUTO-CORRIGE (re-tenta ate N vezes); se nao passar, para e reporta ao dono.

## REGRAS INVIOAVEIS
1. Fundacao (Fase B) e SOLO e vem ANTES de qualquer paralelismo de codigo. Sem excecao.
2. agent-teams (time implicito nomeado + task list + SendMessage), NUNCA Workflow solto; modulos paralelos SEMPRE em git worktree.
3. Gate de codigo = build + testes REAIS + health-check. Nunca so "parece certo".
4. NUNCA fazer merge nem aprovar codigo no lugar do dono. Teste que falha se auto-corrige; produto/merge se pergunta.
5. Consumir a SPEC aprovada + a FUNDACAO congelada. Nao reinventar scaffold/tokens/componentes/schema.
6. Cada modulo herda a UX do mockup APROVADO (pixel-alvo) e resolve seu backlog de fidelidade.
