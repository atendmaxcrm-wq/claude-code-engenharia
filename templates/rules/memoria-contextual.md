# Memoria Contextual - Reformulacao Ativa de Query

## Contexto

O hook `contextual-memory.cjs` (UserPromptSubmit) faz busca automatica no pgvector
a cada mensagem do usuario, mas envia o `prompt` CRU como query para o embedding.

Limitacao conhecida:
- Sem reescrita de query (saudacao, ruido e digitacao livre poluem o embedding)
- Sem expansao multi-query (single-shot)
- Sem reranker
- Threshold padrao traz resultados tangenciais

Resultado: o hook entrega contexto util mas nem sempre o MAIS relevante.

## Pre-requisito: RAG vivo

Esta regra so faz sentido se o banco vetorial esta **populado**. Se a tabela
`memories` estiver vazia ou com poucas linhas, qualquer reformulacao retorna 0
resultados e a regra vira teatro.

**Antes de aplicar, validar:**

```sql
SELECT COUNT(*) total, COUNT(embedding) com_embedding
FROM memories WHERE is_active = true;
```

Se `com_embedding = 0`: popular o RAG primeiro (importar markdown via
`import_markdown` do MCP, migrar de outra base, ou comecar a salvar memorias
durante as sessoes via `store_memory`). Sem isso, ignorar esta regra.

## Identificacao do MCP de memoria ativo

O nome exato do tool depende do nome do MCP no `.mcp.json` do projeto. Padroes
mais comuns gerados pelo installer:

- `mcp__aios-memory__search_memories`
- `mcp__claude-code-memory__search_memories`
- `mcp__memory__search_memories`

Claude DEVE detectar o nome correto **uma vez por sessao** olhando a lista de
tools disponiveis (qualquer tool que termine em `__search_memories`) e usar esse
nome consistentemente. Se nenhum MCP de memoria estiver disponivel: ignorar
esta regra (so o hook automatico atua).

## Regra (OBRIGATORIO)

Em toda mensagem do usuario com intencao real (nao trivial), Claude DEVE:

1. **Ler a mensagem** e identificar a intencao tecnica/factual real
2. **Reformular** internamente como query densa de busca:
   - Substantivos-chave do dominio
   - Termos tecnicos especificos (nome de arquivo, funcao, lib, conceito)
   - Descartar saudacao, hedge, conectivos, primeira pessoa
3. **Disparar `<mcp_memoria>__search_memories`** com a query reformulada
   (substituir `<mcp_memoria>` pelo nome detectado, ex: `mcp__aios-memory`)
4. **Cruzar** os resultados com o que o hook automatico ja injetou no contexto
5. **Responder** usando o conjunto consolidado (hook + busca manual)

## Quando aplicar

SIM:
- Pergunta tecnica ("como funciona X?", "onde fica Y?", "por que Z?")
- Pedido de implementacao ("quero criar X", "adicionar Y")
- Pedido de mudanca em codigo existente
- Investigacao de bug ("nao funciona X", "erro em Y")
- Decisao tecnica ("devo usar A ou B?")

NAO aplicar (pular busca manual):
- Confirmacoes triviais: "sim", "ok", "vai", "pode", "beleza"
- Mensagens de continuacao curta: "continua", "proximo"
- Quando o hook ja trouxe EXATAMENTE o que precisa para responder
- Slash commands diretos (/help, /clear, /compact)
- Mensagens com menos de 10 caracteres uteis
- RAG vazio (ver pre-requisito acima)
- Nenhum MCP de memoria disponivel na sessao

## Exemplo de reformulacao

| Mensagem do usuario | Query reformulada |
|---------------------|-------------------|
| "Cara, e como ta sendo feito a busca, a query a ser enviada no banco vetorial?" | `pgvector embedding query searchSimilar contextual-memory hook` |
| "Nao funciona o servico, da erro 500" | `servico erro 500 troubleshooting deploy logs` |
| "Quero adicionar autenticacao na API" | `autenticacao API middleware JWT routes endpoints` |

## Custo

- Embedding via `text-embedding-3-small`: ~$0.00002 por query
- Latencia: ~300-500ms (aceitavel apos resposta do hook)

## Fallback

Se a busca manual falhar (MCP indisponivel, timeout, RAG vazio):
- Logar mentalmente a falha
- Responder usando apenas o que o hook automatico trouxe
- NUNCA bloquear resposta por falha de RAG
