---
description: Executar tarefa complexa com sub-agentes paralelos. Use para features grandes, migrações, varreduras, pesquisas multi-frente ou qualquer tarefa que beneficie de paralelismo.
argument-hint: "[descricao da tarefa]"
user-invocable: true
---

Execute a seguinte tarefa usando agentes paralelos: $ARGUMENTS

## Escolha da Abordagem

Decida AUTOMATICAMENTE qual abordagem usar. O usuário NÃO precisa saber a diferença.

### Sub-agentes simples (Task tool) — PADRÃO, usar em 90% dos casos

Spawnar via `Task` tool com `subagent_type`. Cada agente roda, entrega resultado e encerra.

**Quando usar:**
- Sub-tarefas independentes que não precisam conversar entre si
- Varreduras paralelas (ex: corrigir acentuação em N arquivos)
- Feature com backend + frontend independentes
- Pesquisas paralelas
- Qualquer tarefa onde cada agente faz seu trabalho isolado

**Vantagens:** Mais rápido, menos tokens, mais confiável, menos overhead.

### Agent Teams real (TeamCreate + @nomes) — RARO, usar só quando necessário

Criar team via `TeamCreate`, spawnar teammates com `team_name` + `name`.

**Quando usar (SOMENTE se todos os critérios se aplicam):**
- Agentes precisam **trocar mensagens entre si** durante execução
- Há dependências dinâmicas que só se revelam durante o trabalho
- Tarefa de longa duração com múltiplas ondas E coordenação contínua

**Na dúvida:** Usar sub-agentes simples. É quase sempre suficiente.

## Processo

### Fase 1: Análise e Decomposição

ANTES de spawnar qualquer agente:

1. **Entender o escopo completo** da tarefa
2. **Decompor em sub-tarefas independentes** que possam rodar em paralelo
3. **Identificar dependências** (o que precisa rodar antes do quê → ondas)
4. **Apresentar o plano** ao usuário:

```
Tarefa: [descrição]

Onda 1 (paralela):
  - Agent A (tipo: X): [o que faz]
  - Agent B (tipo: X): [o que faz]

Onda 2 (depende da Onda 1):
  - Agent C (tipo: X): [o que faz]
```

### Fase 2: Seleção de Tipos

| Tipo | Quando usar | Capacidade |
|------|-------------|------------|
| `dev` | Implementar código (features, fixes) | Lê + escreve + bash |
| `reviewer` | Revisar código, segurança, qualidade | Lê + escreve + bash |
| `investigador` | Diagnosticar bugs, analisar problemas | Lê + escreve + bash |
| `arquiteto` | Analisar impacto, propor soluções | Lê + escreve + bash |
| `Explore` | Pesquisar codebase, buscar arquivos | Somente leitura |
| `general-purpose` | Tarefas genéricas, pesquisa web | Lê + escreve + bash |
| `Plan` | Projetar estratégia | Somente leitura |

### Fase 3: Preparação dos Prompts

Cada agente DEVE receber prompt **completo e autossuficiente**:

```
Prompt deve conter:
1. CONTEXTO: Projeto, stack, arquivos relevantes
2. TAREFA: Exatamente o que fazer (específico, não genérico)
3. RESTRIÇÕES: O que NÃO fazer, limites, padrões a seguir
4. ENTREGÁVEL: O que esperar como resultado
5. ARQUIVOS: Paths absolutos dos arquivos que deve ler/modificar
```

**Regras:**
- Nunca assumir que o agente sabe algo — seja explícito
- Incluir paths absolutos
- Incluir padrões do design system se for UI
- Incluir schema do banco se for backend
- Incluir exemplos de código similar existente

### Fase 4: Execução

**Sub-agentes simples (padrão):**
```
Task({
  subagent_type: "dev",
  description: "Implementar endpoint X",
  prompt: "...",
  mode: "bypassPermissions"
})
```
- Spawnar todos os agentes independentes em paralelo (mesmo bloco de tool calls)
- Esperar resultados
- Se houver Onda 2, spawnar após Onda 1 completar

**Agent Teams real (quando necessário):**
1. `TeamCreate({ team_name: "nome", description: "..." })`
2. `TaskCreate` para cada sub-tarefa
3. `TaskUpdate` para dependências
4. `Task` com `team_name` + `name` para spawnar teammates
5. Monitorar via `TaskList` + mensagens automáticas
6. `SendMessage({ type: "shutdown_request" })` ao final
7. `TeamDelete()`

### Fase 5: Integração e Revisão

Após todos agentes completarem:

1. **Verificar conflitos** entre mudanças de agentes diferentes
2. **Build**: `npm run build` (se frontend alterado)
3. **API**: `curl localhost:3001/health` (se backend alterado)
4. **Testar no dev**: `npm run dev` → validar no browser `http://82.25.71.99:3000`
5. **Checar padrões**: tokens semânticos, CSS sem concatenação, etc.

### Fase 6: Consolidação

1. **Resumir** o que foi feito para o usuário
2. **Listar arquivos** modificados
3. **Registrar na memória** se relevante

## Padrões de Decomposição

### Feature (frontend + backend):
```
Onda 1 (paralela): Agent Backend (endpoints) + Agent Frontend (componente)
Onda 2 (sequencial): Integração + revisão (pode ser feita pelo lead)
```

### Varredura/Correção em massa:
```
Onda única (paralela): N agentes, cada um com grupo de arquivos
Consolidação: Lead verifica + build
```

### Pesquisa:
```
Onda 1 (paralela): Pesquisadores com diferentes ângulos
Onda 2: Consolidar em matriz comparativa
```

## Ambiente de Trabalho

- **Branch**: `dev` (NUNCA `main` direto)
- **Fluxo**: dev → usuário aprova → merge main → /deploy → produção
- **Teste obrigatório** antes de considerar tarefa completa
- **Máximo 5 agentes simultâneos**
- **Prompts autossuficientes** — agente não deve precisar perguntar
- **Revisar SEMPRE** — nunca confiar cegamente no output dos agentes
