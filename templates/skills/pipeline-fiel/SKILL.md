---
name: pipeline-fiel
description: Pipeline completo e opinado para replicar um sistema em MOCKUPS fieis, modulo a modulo em ONDAS. Recebe uma REFERENCIA DE DESIGN obrigatoria (um mockup/artefato canonico ja aprovado, que PODE ser output do /replicar-sistema) da qual todo modulo herda a linguagem visual, e OPCIONALMENTE um BLUEPRINT (prints + docs de texto do sistema-fonte) que liga a auditoria de fidelidade. Fluxo por onda: agent-teams (1 builder por modulo) -> gate visual automatico (Playwright: overflow + console) -> gate de screenshot (eyeball do que o automatico nao pega) -> auditar-fidelidade contra o blueprint (TEXTO = verdade de logica, PRINT = verdade visual) -> auto-correcao de gaps ALTOS -> checklist anti-regressao -> backlog salvo -> APROVACAO HUMANA (onda a onda, ou autonoma via /loop aprovando no final). Compoe replicar-sistema + agent-teams + auditar-fidelidade. Use quando o usuario disser "roda a pipeline", "proxima onda de mockups", "pipeline-fiel", "usa /loop na pipeline-fiel", ou quando for replicar/estender um SaaS em muitos modulos com gate de fidelidade. NAO e para 1 tela (use replicar-sistema direto).
---

# Pipeline Fiel (referencia -> mockups em ondas, com gates de fidelidade)

> Skill do CCE (claude-code-engenharia). Portavel: os scripts gate.mjs/shot.mjs resolvem
> playwright-core e chromium por env (PLAYWRIGHT_CORE, CHROME) ou pelo sibling capturar-logica-saas.
> Nasceu no CRMAX 2 (Agenda + Onda 1 + back-fill de auditoria).

Orquestrar uma onda (ou todas) do pipeline: $ARGUMENTS

## Filosofia
Mockup bonito != sistema fiel. A CARA vem do artefato canonico; a LOGICA vem do blueprint-texto.
Cada onda so chega ao dono depois dos gates (automatico + eyeball) + auditoria, e NUNCA se aprova
sozinho.

## O que a skill RECEBE (inputs) - "precisa de blueprint?"
- **REFERENCIA DE DESIGN (OBRIGATORIA):** um mockup/artefato CANONICO ja aprovado, que define a
  linguagem visual (o bloco de componentes + shell que cada modulo herda VERBATIM). **PODE ser um
  output do `/replicar-sistema`.** Ex. CRMAX: `docs/mockups-aprovados/crmax2-agendamento.html`.
- **BLUEPRINT (OPCIONAL - define o MODO):** prints + docs de texto do sistema-fonte, a verdade de
  fidelidade. Ex. CRMAX: `docs/inspiracao/ce-blueprint-*/screens` + `.../DOCS/blueprint/*.md`.
- **Lista de modulos -> telas**, e a **pasta de saida** dos mockups (ex. `docs/mockups/`).
- **CHECKLIST-MOCKUP.md** (definition-of-done) e **BACKLOG** por modulo (na pasta de saida).

### Dois modos (a resposta a "so preciso de blueprint?")
- **MODO A - Replicar (COM blueprint):** existe um sistema-fonte. Constroi fiel + AUDITA fidelidade
  (skill `auditar-fidelidade`) contra o blueprint. É o pipeline completo. (Foi o do CRMAX 2.)
- **MODO B - Estender padrao (SEM blueprint, so o artefato canonico):** nao ha fonte externa; o
  artefato canonico (ex. um `/replicar-sistema`) e o PADRAO. Nao existe "fonte" pra ser fiel, entao
  a auditoria DEGRADA para: consistencia vs o canonico + completude vs o CHECKLIST. Use quando o
  alvo e so manter a linguagem do canonico em modulos novos (produto proprio, sem clonar ninguem).
  Nesse modo, a Fase 4 troca "auditar-fidelidade contra blueprint" por "auditar consistencia +
  checklist".

## Fase 0 - Pre-requisitos
Validar os inputs acima. Scripts na pasta da skill: `gate.mjs` (overflow/console) e `shot.mjs`
(screenshots). Precisam de playwright-core + chromium; resolvem por env/sibling (ver topo dos
scripts) - em maquina nova, setar `PLAYWRIGHT_CORE` e/ou `CHROME` se nao achar.
ALERTA (Modo A): prints podem estar MISLABELED (caem no dashboard do trial). Conferir pelo CONTEUDO,
nunca so pelo nome do arquivo. Quando o print falhar, o TEXTO e a verdade.

## Fase 1 - Decompor em ondas
Agrupar modulos em ondas coerentes (ex.: por fase do roadmap). Alvo: 3-5 modulos por onda.

## Fase 2 - Construir a onda (agent-teams em leque)
1 builder nomeado por modulo (Agent com `name`, subagent_type dev/general-purpose, model opus).
Prompt: papel + o modulo + as telas de referencia (prints + doc de texto se houver) + o artefato
canonico pra herdar componentes + o caminho do CHECKLIST-MOCKUP.md (APLICAR) + as divergencias
intencionais. Saida: 1 `.html` artifact-ready por modulo na pasta de saida. Herdar tokens/shell
verbatim; cara da plataforma; PT-BR com acento; sem travessao no conteudo; navegador .mocknav.

## Fase 3 - Gate visual (2 partes)
**3a. Automatico (overflow + console):** `node <skill>/gate.mjs <arquivo.html>` por mockup. Cada
.screen em claro+escuro, overflow POR ELEMENTO + erros de console. PASSA exige 0/0. AJUSTAR -> volta.
**3b. Screenshot (eyeball):** `node <skill>/shot.mjs <arquivo.html> <outDir>` gera 1 PNG por tela x
tema. LER os PNGs e conferir o que o automatico NAO pega: alinhamento fino (icone+texto), espacamento,
truncamento, sobreposicao, contraste. Achou algo -> fix (volta ao builder) + regra nova no
CHECKLIST-MOCKUP.md. (Licao do botao "Iniciar atendimento" da Agenda: o automatico so ve overflow/
console; polish de pixel so o olho ve.)

## Fase 4 - Auditoria (skill auditar-fidelidade, em leque)
1 auditor READ-ONLY por modulo. **Modo A:** referencia = blueprint (TEXTO pra logica, PRINT pra
visual); app = o mockup. **Modo B:** referencia = o artefato canonico + o CHECKLIST; audita
consistencia + completude. Saida por modulo: gaps `{ item, status, detalhe, prioridade }`, separando
divergencias INTENCIONAIS.
**VERIFICACAO NA FONTE (live-verify, CONDICIONAL):** quando o PRINT do CE esta vazio/mislabeled e o
TEXTO foi a unica fonte, E houver acesso AUTORIZADO ao sistema-fonte (conta propria do dono, ex.: o
mesmo trial/login que gerou o blueprint), usar a skill `capturar-logica-saas` pra logar READ-ONLY,
navegar ate a tela real, captura-la, e so entao confirmar/ajustar o mockup contra ela. Roda SO pros
casos sem print bom (nao pra tudo). NAO rodar se o trial expirou ou sem autorizacao -> ai o TEXTO
segue como verdade. Login em sistema de terceiro = so conta autorizada do dono, read-only, sem extrair dados.

## Fase 5 - Triagem dos gaps
- **ALTO** (feature/tela/campo real faltando ou quebrado): **AUTO-CORRIGE** (fixer, re-gate, re-audita
  a tela mexida) ANTES de entregar. O dono nunca recebe gap alto.
- **MEDIO/BAIXO**: gravar no `BACKLOG` (resolver na fase de CODIGO / entrega-verificada).
- **DECISAO DE PRODUTO** (escopo, incluir tela X, ativar vertical Y): **PAUSAR e perguntar** ao dono.

## Fase 6 - Publicar e entregar
Publicar cada mockup como artifact. ANTES de publicar, LER o arquivo inteiro (voce distribui o
conteudo). Apresentar ao dono pra aprovar, com o laudo junto. Ao aprovar: copiar pro canonico +
atualizar a memoria.

## Fase 7 - Proxima onda
Repetir da Fase 2. Ordem = roadmap.

## MODO /loop  (`/loop /pipeline-fiel`)
Construir tudo autonomo, dono aprova 1 a 1 no final:
- Cada iteracao = UMA onda completa (Fases 2-6), SEM bloquear em aprovacao: publica + grava backlog + segue.
- Auto-corrige gap alto sozinho; PAUSA so em decisao de produto (segura e pinga o dono).
- Avanca onda apos onda ate acabar os modulos, entao PARA (ScheduleWakeup stop).

## REGRAS INVIOAVEIS
1. agent-teams (time implicito nomeado + task list + SendMessage), NUNCA Workflow solto nem Agent isolado.
2. CHECKLIST-MOCKUP.md aplicado por TODO builder e verificado na auditoria, SEMPRE.
3. Modo A: TEXTO = verdade de logica, PRINT = verdade visual. Nao confiar no nome do print (mislabels).
4. NUNCA aprovar no lugar do dono. Gap alto se auto-corrige; produto se pergunta.
5. Herdar os componentes do canonico verbatim (consistencia entre modulos por construcao).
6. Gate visual (automatico 0/0 + eyeball dos screenshots via shot.mjs) antes da auditoria; auditoria antes do dono.
