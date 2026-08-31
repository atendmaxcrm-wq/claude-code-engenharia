---
name: spec-specify
description: Cria spec de requisitos versionada (specs/<slug>/requirements.md) ANTES de qualquer codigo ou decisao tecnica. Fase 1 do workflow SDD adaptado ao perfil AI Engineer (n8n + agentes IA + Postgres + Evolution). Use quando for iniciar uma feature media ou grande e quiser travar o que vai ser construido antes de discutir COMO. Triggers: "spec", "spec specify", "vou criar feature", "quero documentar antes de codar", "primeiro a spec".
---

# /spec-specify — Travar requisitos antes do design

## Filosofia

Voce nao programa em linha de codigo — voce programa em **fluxo de sistema**. Esta skill formaliza requisitos no nivel que voce ja pensa: comportamento observavel, integracoes, dados que entram/saem, regras de negocio.

A spec gerada e **revisavel em diff**, sobrevive a compactacao da conversa, e vira input do `/spec-plan` (proxima fase).

## Quando usar

SIM:
- Feature nova que toca **2+ sistemas** (ex.: n8n + Postgres + WhatsApp, ou cron + DB + API)
- Feature que voce vai pedir o Claude implementar em **outra sessao** (spec precisa sobreviver)
- Feature pra cliente externo (a spec vira documentacao de entrega)
- Voce sente que ainda nao consegue descrever a feature em 1 frase sem ambiguidade

NAO usar:
- Bug fix isolado (1-3 arquivos)
- Ajuste de UI / micro-mudanca
- Coisa que voce ja sabe exatamente como fazer no n8n e leva 10min
- Voce ainda nao decidiu se vale a pena fazer (use `/pesquisar-tech` antes)

## Pre-requisitos

Antes de comecar, o Claude DEVE:
1. Confirmar o **slug da feature** com o usuario (kebab-case, ex: `agendamento-whatsapp`, `alerta-monitor-down`)
2. Validar que `/root/teste-aios/specs/<slug>/` nao existe — se existir, perguntar se e pra editar a spec existente ou criar nova versao
3. Ler `memoria/sistema/database-schema.md`, `memoria/sistema/api-endpoints.md` e `memoria/progresso.md` pra ter contexto do que ja existe

## Workflow

### Passo 1 — Capturar a intencao (1 paragrafo)

Pergunte ao usuario UMA frase:
> "Em uma frase, qual o resultado observavel da feature quando estiver pronta? (o que o usuario/sistema final vai conseguir fazer que hoje nao consegue)"

Anote a resposta literal. Se a frase tiver mais de uma "e", desmembre — pode ser duas features.

### Passo 2 — Mapear sistemas envolvidos

Pergunte:
> "Quais sistemas/fontes participam? (marque tudo que se aplica: Postgres, n8n, Evolution API, OpenAI, webhook externo, cron, frontend, MCP, outro)"

Pra cada sistema marcado, em uma linha:
- **Como ele entra na feature?** (gatilho / fonte de dados / consumidor / armazenamento)

### Passo 3 — Dados (entrada e saida)

Voce trabalha com Postgres todo dia. Liste:
- **Entrada:** que dados/payload chegam? (ex.: webhook Evolution com `{from, message, instance}`)
- **Saida:** que dados ficam persistidos ou sao enviados? (ex.: linha em `tabela_x`, mensagem WhatsApp, resposta JSON)
- **Tabelas tocadas:** novas? existentes? — listar nomes (sem detalhar coluna ainda, isso e `spec-plan`)

### Passo 4 — Regras de negocio (numerar)

Forcar lista numerada. Cada regra em forma `QUANDO X ENTAO Y`:
- `R1. QUANDO usuario envia /agendar fora do horario comercial ENTAO bot responde com mensagem de fallback e nao abre fluxo`
- `R2. QUANDO mesmo cliente ja tem agendamento futuro ENTAO bot pergunta se quer remarcar`
- `R3. QUANDO slot solicitado conflita ENTAO bot oferece os 3 proximos slots livres`

Minimo 3, maximo 12. Se passar de 12, alertar: "voce talvez esteja misturando 2 features".

### Passo 5 — Criterios de aceitacao (cenarios)

Pra cada regra critica, escrever 1 cenario em estilo `Dado / Quando / Entao`:
```
Cenario: Cliente pede agendamento valido
  Dado um cliente conhecido pelo telefone +5588...
  Quando ele envia "/agendar"
  Entao o bot retorna os 3 slots disponiveis nas proximas 48h
  E grava no Postgres uma linha em `agendamento_solicitacoes` com status=aberto
```

Minimo 3 cenarios. Eles vao virar checklist do `/spec-plan` e teste manual no fim.

### Passo 6 — Fora de escopo (explicito)

Lista do que NAO faz parte desta feature, pra travar scope creep:
- "NAO vai criar UI web — so WhatsApp"
- "NAO vai notificar atendente humano — fica pra fase 2"
- "NAO vai integrar Google Calendar — fica em backlog"

### Passo 7 — Perguntas em aberto

Antes de gerar o arquivo, lista o que **ainda nao esta decidido** (pra resolver no `/spec-clarify` futuro ou perguntar agora):
- "[ABERTO] Cliente desconhecido pode agendar ou precisa cadastro previo?"
- "[ABERTO] Quantos dias de antecedencia maxima?"

Se a lista de abertos tiver >5 itens, parar e pedir ao usuario pra responder ao menos os 3 mais importantes ANTES de gerar o arquivo.

### Passo 8 — Gerar `specs/<slug>/requirements.md`

Template do arquivo:
```markdown
# Requirements — <Nome da Feature>

> **Slug:** <slug>
> **Criado em:** YYYY-MM-DD
> **Autor:** Gleidson (AI Engineer)
> **Status:** draft | aprovado | implementado
> **Proximo passo:** /spec-plan <slug>

## 1. Intencao (uma frase)
<copiar literalmente a resposta do Passo 1>

## 2. Sistemas envolvidos
| Sistema | Papel |
|---------|-------|
| <Postgres> | <armazena slots e solicitacoes> |
| <Evolution API> | <recebe webhook e envia respostas> |
| ... | ... |

## 3. Dados
**Entrada:**
- ...

**Saida:**
- ...

**Tabelas tocadas:** `tabela_a` (nova), `tabela_b` (existente, alterar)

## 4. Regras de negocio
- R1. ...
- R2. ...
- ...

## 5. Criterios de aceitacao
### Cenario 1: <titulo>
- Dado ...
- Quando ...
- Entao ...

### Cenario 2: ...

## 6. Fora de escopo
- ...

## 7. Perguntas em aberto
- [ABERTO] ...
```

### Passo 9 — Resumo final pro usuario

Apos gravar o arquivo, mostrar ao usuario:
1. **Caminho do arquivo:** `specs/<slug>/requirements.md`
2. **Numero de regras + cenarios + abertos** (ex.: "5 regras, 3 cenarios, 2 perguntas abertas")
3. **Decisao:** "Pode rodar `/spec-plan <slug>` agora ou prefere fechar os abertos antes?"

## Anti-padroes (NAO fazer)

- NAO sugerir stack/tecnologia/lib aqui. Isso e `spec-plan`. Aqui e SO O QUE.
- NAO escrever query SQL ou codigo. Aqui e descricao de comportamento.
- NAO inventar regras que o usuario nao falou. Se faltar info, virar `[ABERTO]`.
- NAO gerar requirements.md sem confirmar slug e ler memoria primeiro.
- NAO usar travessao (em-dash) no markdown — CLAUDE.md proibe.

## Saida esperada

Um arquivo `specs/<slug>/requirements.md` com 7 secoes, revisavel em diff, que serve de input direto pro `/spec-plan`.
