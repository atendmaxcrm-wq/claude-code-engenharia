---
paths:
  - "services/**"
  - "types/**"
  - "**/types.ts"
  - "**/types.d.ts"
---

# Regras para Services e Types

## Services
- async/await para operacoes assincronas
- Cada service = 1 responsabilidade (Single Responsibility)
- Error handling: try/catch com log contextual
- Retry com backoff exponencial para servicos externos (3x: 2s-4s-8s)
- Nao importar Express (req/res) dentro de services — services sao agnosticos
- Retornar dados, nao respostas HTTP

## Types
- Interface para objetos (nao type alias)
- Sem `any` — usar `unknown` e narrow com type guards
- Exportar types do arquivo types.ts da feature
- Nomear com sufixo descritivo: `BlogPost`, `BlogPostCreate`, `BlogPostUpdate`
- Discriminated unions para variantes de estado
- Enums como const objects (nao enum keyword — tree-shaking)

## Convencoes
- Nomes em PascalCase para interfaces/types
- Nomes em camelCase para funcoes e variaveis
- Nomes em UPPER_SNAKE_CASE para constantes
- Arquivos em kebab-case: `blog-post-generator.js`
