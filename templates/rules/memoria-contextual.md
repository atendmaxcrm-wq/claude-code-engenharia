# Memoria Contextual - Reformulacao Ativa de Query

## Contexto

O hook `contextual-memory.cjs` (UserPromptSubmit) faz busca automatica no pgvector
a cada mensagem do usuario, mas envia o `prompt` CRU como query para o embedding.

Limitacao conhecida:
- Sem reescrita de query (saudacao, ruido e digitacao livre poluem o embedding)
- Sem expansao multi-query (single-shot)
- Sem reranker
- Threshold 0.45 traz resultados tangenciais

Resultado: o hook entrega contexto util mas nem sempre o MAIS relevante.

## Regra (OBRIGATORIO)

Em toda mensagem do usuario com intencao real (nao trivial), Claude DEVE:

1. **Ler a mensagem** e identificar a intencao tecnica/factual real
2. **Reformular** internamente como query densa de busca:
   - Substantivos-chave do dominio
   - Termos tecnicos especificos (nome de arquivo, funcao, lib, conceito)
   - Descartar saudacao, hedge, conectivos, primeira pessoa
3. **Disparar `mcp__aios-memory__search_memories`** com a query reformulada
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

## Exemplo de reformulacao

| Mensagem do usuario | Query reformulada |
|---------------------|-------------------|
| "Cara, e como ta sendo feito a busca, a query a ser enviada no banco vetorial?" | `pgvector embedding query searchSimilar text-embedding-3-small contextual-memory hook` |
| "Nao funciona o blog, da erro 500" | `blog-post-generator framer-service erro 500 troubleshooting publish` |
| "Quero adicionar autenticacao na API" | `autenticacao API middleware JWT routes monitor-server endpoints` |

## Custo

- `mcp__aios-memory__search_memories` usa `text-embedding-3-small`
- ~$0.00002 por query reformulada
- Latencia: ~300-500ms (aceitavel pos-resposta do hook)

## Fallback

Se a busca manual falhar (MCP indisponivel, timeout):
- Logar mentalmente a falha
- Responder usando apenas o que o hook automatico trouxe
- NUNCA bloquear resposta por falha de RAG
