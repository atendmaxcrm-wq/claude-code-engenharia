---
name: api-patterns
description: Padroes de endpoints da API. Use ao criar ou modificar endpoints REST.
---

# API Patterns

## Estrutura de Endpoint
```javascript
router.get('/api/recurso', async (req, res) => {
  try {
    // 1. Validar input
    // 2. Processar
    // 3. Responder
    res.json({ success: true, data: resultado });
  } catch (error) {
    console.error('[RECURSO] Erro:', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});
```

## Status Codes
| Code | Uso |
|------|-----|
| 200 | Sucesso (GET, PUT, PATCH) |
| 201 | Criado (POST) |
| 400 | Input invalido |
| 401 | Nao autenticado |
| 403 | Sem permissao |
| 404 | Nao encontrado |
| 500 | Erro interno |

## Seguranca
- Queries SEMPRE parametrizadas ($1, $2...)
- NUNCA concatenar strings em SQL
- Sanitizar input do usuario
- Rate limiting em endpoints publicos

## Error Handling
- try/catch em todo handler
- Log com contexto: `[MODULO] Acao: detalhes`
- Retornar mensagem util ao cliente (sem stack trace)
- Retry com backoff exponencial para servicos externos (3x: 2s-4s-8s)

## Respostas
- Padrao: `{ success: boolean, data?: any, error?: string }`
- Listas: `{ success: true, data: [], total: number }`
- Paginacao: `{ data: [], page, limit, total, totalPages }`

## Cache
- TTLs por tier: SHORT=10s, MEDIUM=60s, LONG=5min, VERY_LONG=15min
- Invalidar ao criar/editar/deletar
- Key pattern: `modulo:recurso:id`

## Convencoes
- Rotas em kebab-case: `/api/blog-posts`
- Verbos REST: GET (ler), POST (criar), PUT (atualizar), DELETE (remover)
- Filtros via query params: `?status=active&limit=10`
- IDs via path params: `/api/posts/:id`
