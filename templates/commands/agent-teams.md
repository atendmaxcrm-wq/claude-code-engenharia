---
description: Estruturar tarefa complexa com agent teams paralelos
argument-hint: "[descricao da tarefa]"
user-invocable: true
---

Estruture a tarefa usando agent teams: $ARGUMENTS

### Fase 1: Decompor
- Decompor em sub-tarefas independentes (paralelas)
- Identificar dependencias (o que precisa rodar antes do que)
- Apresentar plano:

Sub-tarefas paralelas (Onda 1):
  - Agent A (tipo): [o que faz]
  - Agent B (tipo): [o que faz]

Sub-tarefas sequenciais (Onda 2):
  - Agent C (tipo): [o que faz]

Revisao:
  - Agent Reviewer: valida tudo

### Fase 2: Selecao de Agents
| Tipo | Quando | Tools |
|------|--------|-------|
| dev | Implementar | Todos (edit, write, bash) |
| reviewer | Revisar | Todos |
| investigador | Diagnosticar | Todos |
| arquiteto | Analisar impacto | Todos |
| Explore | Pesquisar codebase | Read-only |
| Plan | Projetar estrategia | Read-only |

### Fase 3: Execucao
Cada agent recebe prompt autossuficiente com:
1. CONTEXTO: Stack e informacoes do projeto
2. TAREFA: Exatamente o que fazer
3. RESTRICOES: O que NAO fazer
4. ENTREGAVEL: O que esperar
5. ARQUIVOS: Lista de paths

### Fase 4: Integracao
- Verificar conflitos entre agents
- Testar servico apos mudancas
- Verificar logs
- Checar anti-padroes

Maximo 5 agents simultaneos. NUNCA spawnar sem plano aprovado.
