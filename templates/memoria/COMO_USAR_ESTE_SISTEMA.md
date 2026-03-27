# Como Usar o Sistema de Memoria

## Arquivos de Memoria

| Arquivo | Tipo | Descricao |
|---------|------|-----------|
| `insights.md` | Permanente | Decisoes, padroes, armadilhas (cumulativo) |
| `progresso.md` | Volatil | Onde paramos, proximo passo (atualizado toda sessao) |
| `sistema/*.md` | Semi-permanente | Schema, endpoints, troubleshooting |
| `roadmaps/*.md` | Semi-permanente | Planos multi-fase com checkboxes |

## Workflow

### Inicio de Sessao
1. O hook `contextual-memory.js` busca memorias relevantes automaticamente
2. Se o contexto foi compactado, `reinject-memory.js` reinjeta o essencial

### Durante a Sessao
- Consulte `memoria/insights.md` para decisoes e gotchas
- Use `search_memories` (MCP) para busca semantica aprofundada
- Use `search_memories_by_text` (MCP) para busca por keywords

### Fim de Sessao
Execute `/atualizar-memoria` para salvar:
- Decisoes tomadas
- Padroes descobertos
- Armadilhas encontradas
- Progresso atual
- Proximos passos

## pgvector (Busca Inteligente)

O sistema usa PostgreSQL + pgvector para busca semantica.
Embeddings de 1536 dimensoes (text-embedding-3-small).

### MCP Tools Disponiveis
- `store_memory` — Armazenar nova memoria
- `update_memory` — Atualizar memoria existente
- `deactivate_memory` — Desativar (soft-delete)
- `search_memories` — Busca semantica por similaridade
- `search_memories_by_text` — Busca full-text por keywords
- `get_memory_by_id` — Buscar por UUID
- `start_session` — Iniciar sessao
- `end_session` — Encerrar sessao com resumo
- `get_current_session` — Sessao atual
- `import_markdown` — Importar arquivo markdown
- `sync_from_markdown` — Sincronizar todos os markdowns
- `memory_stats` — Estatisticas do banco
