---
paths:
  - "src/**/*.js"
  - "src/**/*.ts"
  - "api/**"
  - "routes/**"
---

# Regras para Backend Node.js

## Padroes

### Imports
- CJS: `const x = require('...')`
- ESM-only packages: dynamic `import()` com cache
- Env vars via `process.env.NOME`

### Funcoes Async
- async/await para operacoes assincronas
- Sempre tratar erros com try/catch
- Log de erros com contexto: `console.error('[Servico] Erro:', error.message)`

### API Endpoints
- Status codes: 200 (ok), 201 (created), 400 (bad request), 500 (error)
- Respostas JSON com `{ success, data?, error? }`
- Queries parametrizadas (prevencao SQL injection)

### OpenAI
- Embeddings: `text-embedding-3-small` (1536 dims)
- Sempre use `max_completion_tokens` para modelos recentes

### Padrao de Services
```
const CONFIG = {
  apiKey: process.env.OPENAI_API_KEY,
};

async function minhaFuncao() { ... }

module.exports = { minhaFuncao };
```

## Conteudo Gerado
- Acentuacao correta em PT-BR (SEMPRE)
- Queries parametrizadas (prevencao SQL injection)
