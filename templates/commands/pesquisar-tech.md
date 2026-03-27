---
description: Pesquisar e avaliar tecnologias/libs antes de implementar
argument-hint: "[tema - ex: drag and drop, form validation, state management]"
user-invocable: true
---

Pesquise sobre: $ARGUMENTS

### Fase 1: Contexto
- O que temos hoje? Qual lib/implementacao?
- Quais problemas motivam a troca?
- Requisitos obrigatorios e desejaveis
- Restricoes tecnicas (versao Node, compatibilidade CJS/ESM, bundle size)

### Fase 2: Pesquisa Ampla
Use agent teams em paralelo:
- Agent 1: Top 5 libs mais populares (npm downloads, stars, ultima release)
- Agent 2: Artigos comparativos, benchmarks, migration guides
- Agent 3: Alternativas nao-obvias, implementacao nativa

### Fase 3: Matriz de Decisao

| Criterio | Peso | Lib A | Lib B | Lib C |
|----------|------|-------|-------|-------|
| Requisito 1 | ALTO | ? | ? | ? |
| Bundle size | MEDIO | ? | ? | ? |
| TypeScript | ALTO | ? | ? | ? |
| Manutencao | ALTO | ? | ? | ? |
| CJS compativel | ALTO | ? | ? | ? |

### Fase 4: Recomendacao
1. Recomendacao principal + justificativa
2. Alternativa
3. Riscos da migracao
4. Esforco estimado
5. Plano em alto nivel

NUNCA implementar durante a pesquisa. So recomendacao.
