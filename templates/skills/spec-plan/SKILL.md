---
name: spec-plan
description: Cria design tecnico versionado (specs/<slug>/design.md) a partir de requirements.md ja existente. Fase 2 do workflow SDD adaptado ao perfil AI Engineer. Propoe schema Postgres, contratos de webhook, fluxo n8n, prompts de agente, integracoes Evolution/OpenAI. Justifica escolhas com tradeoffs reais. Use APOS /spec-specify gerar requirements.md, antes de implementar. Triggers: "spec plan", "design tecnico", "tradeoffs", "como vou implementar a spec".
---

# /spec-plan — Design tecnico com tradeoffs explicitos

## Filosofia

Voce ja sabe ler schema SQL, fluxo n8n, contrato de webhook e prompt de agente. Voce NAO digita codigo de producao. Esta fase entrega o **menu antes do prato**: o Claude prope as decisoes tecnicas em forma revisavel, justifica cada uma com tradeoff real, e SO depois da aprovacao vai pro /spec-implement.

Diferenca pro /planejar-feature antigo: aqui o design fica **persistido em markdown versionado** e separado dos requisitos. Sobrevive a compactacao, vira diff no git, pode ser revisado por terceiros.

## Pre-requisitos

Antes de gerar design.md, o Claude DEVE:
1. Verificar que `specs/<slug>/requirements.md` existe e foi lido por completo
2. Verificar que status do requirements.md e `draft` ou `aprovado` (nao `implementado`)
3. Ler memoria do projeto:
   - `memoria/sistema/database-schema.md` (schema atual)
   - `memoria/sistema/api-endpoints.md` (endpoints existentes)
   - `memoria/insights.md` (padroes e gotchas — buscar trecho relevante)
4. Buscar memorias pgvector com query reformulada (regra `memoria-contextual.md`)

Se requirements.md tem perguntas em aberto criticas, PARAR e pedir pra fechar antes.

## Stack natural do projeto (default)

O Claude DEVE assumir como stack default e SO justificar quando sair dela:

| Camada | Default |
|--------|---------|
| Banco | PostgreSQL 16 + pgvector (porta 5432) |
| Cron / orquestracao | monitor-server (PM2, porta 4001) ou n8n |
| LLM | OpenAI GPT-5.4 (criativo), gpt-4o-mini (analise) |
| WhatsApp | Evolution API (REST) |
| Cache | Redis (porta 6379) |
| Frontend | Next.js 16 + Tailwind v4 (quando aplicavel) |
| MCP | aios-memory |

Se a proposta envolver algo FORA disso (ex.: gRPC, Kafka, Mongo, novo provedor), o design.md DEVE ter secao "Por que saimos do stack default" com justificativa.

## Workflow

### Passo 1 — Mapear arquivos afetados

Antes de propor schema, listar arquivos do projeto que vao ser:
- **Criados:** (caminho + responsabilidade em 1 linha)
- **Modificados:** (caminho + o que muda em 1 linha)
- **Lidos como referencia:** (caminho — so leitura, sem alterar)

Esta secao alimenta o `spec-tasks` futuro e ja sinaliza o tamanho da feature.

### Passo 2 — Schema de dados (se aplicavel)

Pra cada tabela tocada nos requirements:

**Nova tabela:**
```sql
CREATE TABLE <nome> (
  id BIGSERIAL PRIMARY KEY,
  <colunas com tipo, NOT NULL, DEFAULT, comentario>
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_<nome>_<coluna> ON <nome>(<coluna>);
```

Cada coluna com 1 linha explicando o que armazena.

**Alteracao:**
```sql
ALTER TABLE <nome> ADD COLUMN <col> <tipo>;
-- Motivo: ...
-- Backfill: ... (ou "nao precisa, defaulta NULL")
```

Sempre incluir:
- Indices necessarios e por que
- Constraints (UNIQUE, FOREIGN KEY)
- Estrategia de backfill se for ALTER

### Passo 3 — Contratos de integracao

Pra cada sistema externo dos requirements:

**Webhook entrada (ex.: Evolution API):**
```
POST /webhook/<rota>
Body: { ... payload esperado ... }
Validacoes: ...
Resposta: 200 OK { status: "received" }
```

**Chamada saida (ex.: Evolution sendMessage):**
```
POST https://<host>/message/sendText/<instance>
Body: { number, text, ... }
Retry: ... (3x exponencial? sem retry?)
Idempotencia: ... (como evitar mensagem duplicada?)
```

**Fluxo n8n (se aplicavel):**
Descricao textual em 5-10 passos:
1. Trigger: Webhook ...
2. Postgres node: SELECT ...
3. Code node: ...
4. HTTP Request: POST Evolution ...
5. ...

### Passo 4 — Logica de negocio (pseudo-codigo de alto nivel)

NAO escrever codigo real. Escrever **passos numerados em portugues estruturado** que mapeiam diretamente pras regras de negocio dos requirements.

Exemplo:
```
Funcao: processar_pedido_agendamento(webhook_payload)
1. Extrair {telefone, mensagem, instancia} do payload
2. SELECT cliente FROM clientes WHERE telefone = ? — se nao existir, ramo A
3. Verificar regra R1 (horario comercial) — se fora, responder fallback e RETURN
4. Verificar regra R2 (agendamento futuro existente) — se sim, ramo B
5. Buscar 3 slots livres nas proximas 48h (regra R3)
6. Responder via Evolution com texto + opcoes
7. INSERT em agendamento_solicitacoes (status=aberto)
8. Log estruturado: ...
```

Cada passo referencia regra do requirements.md (R1, R2, R3) ou cenario (C1, C2, C3).

### Passo 5 — Prompts de agente IA (se aplicavel)

Se a feature usa LLM, listar:
- **Modelo:** gpt-5.4 / gpt-4o-mini / outro
- **System prompt resumo:** 3-5 linhas do que o agente faz
- **Tools que o agente expoe:** lista com nome + 1 linha do que cada tool faz
- **Custo estimado:** token in/out medio por chamada e custo por mil execucoes

NAO escrever o system prompt completo aqui — referenciar onde vai ficar (ex.: "completo em aios-core/squads/.../prompts/X.md")

### Passo 6 — Tradeoffs (a parte mais importante)

Tabela `Decisao | Escolhido | Alternativa | Por que NAO a alternativa`:

| Decisao | Escolhido | Alternativa | Por que NAO |
|---------|-----------|-------------|-------------|
| Onde rodar o cron | monitor-server (PM2) | n8n schedule | Cron precisa acessar Postgres local + Evolution direto; n8n adicionaria 2 hops de rede |
| Cache de slots | Redis TTL 5min | Postgres com index | Consulta de slot roda a cada msg de cliente; Redis evita pressao no pool |
| Idempotencia webhook | header `x-evolution-message-id` em UNIQUE | hash do body | Evolution ja envia ID estavel; hash teria colisao falsa se cliente repetir texto exato |

**Minimo 3 tradeoffs.** Se a feature nao tem decisao com alternativa real, ela e trivial demais pra precisar de spec.

### Passo 7 — Riscos e mitigacoes

Lista de "o que pode dar errado" + plano:
- **Risco:** Evolution API offline durante envio → **Mitigacao:** retry exponencial 3x + DLQ em tabela `mensagens_falhadas`
- **Risco:** Cliente envia 50 msgs em 1 segundo → **Mitigacao:** rate limit por telefone (10 msg/min) via Redis
- **Risco:** OpenAI fora do ar → **Mitigacao:** fallback pra resposta canned

### Passo 8 — Observabilidade

Como vamos saber se ta funcionando:
- **Logs estruturados:** que campos sempre logar
- **Metricas:** taxa de sucesso, latencia p95, custo OpenAI/dia
- **Alertas:** condicao + canal (ex.: "se taxa erro >5% por 10min, alerta no WhatsApp grupo X")

### Passo 9 — Gerar `specs/<slug>/design.md`

Template:
```markdown
# Design Tecnico — <Nome da Feature>

> **Slug:** <slug>
> **Requirements:** [requirements.md](./requirements.md)
> **Criado em:** YYYY-MM-DD
> **Status:** draft | aprovado | implementado
> **Proximo passo:** revisar com Gleidson, depois /spec-tasks <slug>

## 1. Arquivos afetados
**Criados:** ...
**Modificados:** ...
**Lidos:** ...

## 2. Schema de dados
```sql
...
```

## 3. Contratos de integracao
**Webhook entrada:**
...

**Chamadas saida:**
...

**Fluxo n8n (se aplicavel):**
...

## 4. Logica de negocio (passos)
...

## 5. Prompts de agente IA
- Modelo: ...
- Tools: ...
- Custo estimado: ...

## 6. Tradeoffs
| Decisao | Escolhido | Alternativa | Por que NAO |
| ... | ... | ... | ... |

## 7. Riscos
- Risco: ... → Mitigacao: ...

## 8. Observabilidade
- Logs: ...
- Metricas: ...
- Alertas: ...

## 9. Sai do stack default?
<vazio se nao; se sim, secao com justificativa>
```

### Passo 10 — Resumo pro usuario

Apos gravar:
1. **Caminho:** `specs/<slug>/design.md`
2. **Resumo de impacto:** N arquivos criados, M modificados, X tabelas novas, Y endpoints novos
3. **Custo estimado** (se LLM): $/mes em uso esperado
4. **Top 3 tradeoffs** (resumidos em 1 linha cada) — peca aprovacao
5. **Pergunta direta:** "Aprovado pra ir pra /spec-tasks ou tem ajuste?"

## Anti-padroes

- NAO propor mudanca de stack sem secao "Por que saimos do stack default"
- NAO escrever codigo real (so SQL declarativo e pseudo-codigo estruturado)
- NAO esconder alternativas — sempre 3+ tradeoffs explicitos
- NAO assumir aprovacao — sempre fechar com pergunta
- NAO usar jargao que nao esta no stack do projeto sem traducao
- NAO usar travessao (em-dash) — CLAUDE.md proibe

## Saida esperada

Arquivo `specs/<slug>/design.md` com 9 secoes, schema SQL declarativo, contratos de integracao, tradeoffs revisaveis. Suficiente pra qualquer outra sessao do Claude executar via `/spec-tasks` + `/spec-implement` (que viram em iteracao futura).
