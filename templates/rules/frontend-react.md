---
paths:
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/*.ts"
---

# Regras para Frontend React

## Arquitetura
- Componente > 300 linhas -> decompor em pasta por feature
- Padrao: components/[feature]/ com orquestrador + hooks + views + types
- Features novas ja nascem estruturadas

## Codigo
- TypeScript com tipagem estrita (sem `any`)
- Componentes funcionais com hooks
- Evitar re-renders desnecessarios (React.memo, useCallback)
- Tratar loading states, error states, empty states

## Imports
- Absolutos quando disponivel (via path aliases)
- Ordem: React/core -> external libs -> UI components -> utils -> stores -> features -> CSS

## Nomenclatura
- Componentes: PascalCase (WorkflowList)
- Hooks: prefixo use (useWorkflowData)
- Arquivos: kebab-case (workflow-list.tsx)
- Constantes: SCREAMING_SNAKE_CASE (MAX_RETRIES)
- Interfaces: PascalCase + sufixo (WorkflowListProps)
