---
description: Atualizar arquivos de memoria do projeto com mudancas da sessao
user-invocable: true
---

Atualize os arquivos de memoria do projeto para preservar contexto entre sessoes.

## Instrucoes

Leia os seguintes arquivos de memoria atuais:
- `memoria/insights.md`
- `memoria/progresso.md` (se existir)
- Todos os arquivos em `memoria/roadmaps/`

Depois, atualize cada um com base no trabalho realizado nesta sessao:

### 1. `memoria/insights.md`
- Adicione novas **decisoes** tomadas (com data, contexto e alternativas descartadas)
- Adicione novos **padroes** identificados no codigo
- Adicione novas **armadilhas** (gotchas) descobertas
- Adicione uma entrada em **Notas de Sessao** resumindo o que foi feito
- NAO remova entradas anteriores (insights sao cumulativos)

### 2. `memoria/progresso.md`
- Atualize o **Estado Geral** de cada area
- Atualize **O Que Foi Feito** com as tarefas desta sessao
- Defina o **Proximo Passo Imediato** baseado no que discutimos
- Atualize **Contexto Importante** com decisoes ou caminhos relevantes
- Atualize **Nao Testado Ainda** removendo o que foi testado e adicionando novos
- Atualize a data da ultima atualizacao e numero da sessao

### 3. `memoria/sistema/*.md` (se existirem)
- Schema do banco alterado? -> Atualize `database-schema.md`
- Novos endpoints? -> Atualize `api-endpoints.md`
- Mudancas de permissao? -> Atualize `permissoes.md`
- Novo bug/fix? -> Atualize `troubleshooting.md`
- Conhecimento de dominio novo? -> Atualize ou crie em `memoria/conhecimento/`

### 4. `memoria/roadmaps/*.md`
- Marque checkboxes de itens completados: `[ ]` -> `[x]`
- Adicione novos itens se surgiram durante a sessao

### 5. CLAUDE.md
- Se criou novos arquivos/componentes importantes, atualize o CLAUDE.md

### 6. Persistir no pgvector (se MCP aios-memory disponivel)

Apos atualizar os arquivos Markdown, persista as mudancas no banco vetorial:

1. Se ainda nao ha sessao aberta, chame `start_session` (MCP tool do aios-memory)
2. Para cada **decisao** nova: `store_memory` com `memory_type: 'decision'`, `importance: 'high'`
3. Para cada **padrao** novo: `store_memory` com `memory_type: 'pattern'`
4. Para cada **gotcha** novo: `store_memory` com `memory_type: 'gotcha'`, `importance: 'high'`
5. Para cada **nota de sessao**: `store_memory` com `memory_type: 'session_note'`
6. Chame `end_session` com summary, work_done, next_steps, files_changed
7. Chame `sync_from_markdown` para garantir sincronizacao completa

Se o MCP aios-memory nao estiver disponivel, pule silenciosamente.
Os arquivos Markdown continuam como source of truth; pgvector e camada de aceleracao.

### Regras
- Use somente ASCII (sem acentos nos arquivos de memoria)
- Seja conciso mas preciso
- So atualize o que realmente mudou (nao reescreva tudo)
- Priorize informacao que ajude a proxima sessao a continuar sem perguntas
- O `progresso.md` deve ser escrito como se fosse um briefing para outro desenvolvedor
