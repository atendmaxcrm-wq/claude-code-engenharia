---
description: Orquestracao multi-agent com Agent Teams nativo. Decompoe tarefa complexa, cria time real com comunicacao entre teammates, task list compartilhada e quality gates.
argument-hint: "[descricao da tarefa complexa]"
user-invocable: true
---

# Agent Teams v2 — Orquestracao Multi-Agent Nativa

Tarefa recebida: $ARGUMENTS

---

## FASE 1: ANALISE E DECOMPOSICAO

Antes de qualquer acao:

1. **Classificar a tarefa:**
   - [ ] Qual o escopo? (1 arquivo / 5-10 arquivos / 10+ arquivos / sistema inteiro)
   - [ ] Tem dependencias entre sub-tarefas?
   - [ ] Qual o risco? (baixo: UI/CSS | medio: logica | alto: types/API/banco)

2. **Mapear arquivos afetados:**
   - Use Agent tool com subagent_type="Explore" para levantar todos os arquivos relevantes
   - Agrupe por dominio (UI, logica, types, backend, config)

3. **Escolher padrao de orquestracao:**

   | Padrao | Quando usar | Exemplo |
   |--------|-------------|---------|
   | **Hierarchical** | Tarefa com supervisor + workers | Refatoracao grande com review |
   | **Pipeline** | Fases sequenciais dependentes | Analyze -> Implement -> Test |
   | **Parallel** | Sub-tarefas 100% independentes | Aplicar design em 5 modulos |
   | **Supervisor** | Coordenacao complexa com decisoes | Feature nova cross-cutting |
   | **Swarm** | Multiplas abordagens para mesmo problema | Debug com hipoteses paralelas |

---

## FASE 2: SELECAO DE AGENTS

Escolha o `subagent_type` baseado no que cada agent precisa fazer:

| Tipo | Especialidade | Quando usar |
|------|--------------|-------------|
| **general-purpose** | Implementar (full tools) | Features, fixes, qualquer coisa |
| **Explore** | Pesquisar codebase (read-only) | Discovery, analise |
| **Plan** | Projetar estrategia (read-only) | Antes de mudancas grandes |

Se voce tem agents customizados em `.claude/agents/`, use-os pelo nome (ex: `dev`, `reviewer`, `test-runner`).

### Regras de selecao:
- Tasks de **leitura/analise**: Explore ou agents read-only customizados
- Tasks de **implementacao**: general-purpose ou agents com permissao de edicao
- Tasks de **validacao**: agents leves (haiku) para build/test
- Tasks de **revisao**: agents read-only para checar qualidade
- **NUNCA** usar agent de implementacao para tarefa de revisao (e vice-versa)

---

## FASE 3: MONTAGEM DO PLANO

Apresentar ao usuario neste formato EXATO:

```
## Plano de Execucao — Agent Teams

**Tarefa:** [descricao]
**Padrao:** [hierarchical/pipeline/parallel/supervisor/swarm]
**Risco:** [baixo/medio/alto]
**Arquivos afetados:** [N arquivos]
**Time:** [nome do time que sera criado]

### Onda 1 — [nome da fase] (paralelo)
| # | Teammate | Tipo (subagent_type) | Arquivos | O que faz |
|---|----------|---------------------|----------|-----------|
| 1 | frontend-dev | dev | file1, file2 | descricao |
| 2 | backend-dev | dev | file3, file4 | descricao |

### Onda 2 — [nome da fase] (depende da Onda 1)
| # | Teammate | Tipo (subagent_type) | Arquivos | O que faz |
|---|----------|---------------------|----------|-----------|
| 3 | integrator | dev | file5 | descricao |

### Quality Gate
| # | Teammate | Tipo | O que valida |
|---|----------|------|-------------|
| 4 | validator | test-runner | npm run build |
| 5 | code-reviewer | reviewer | checklist de qualidade |

**Aguardando aprovacao para executar...**
```

### Regras do plano:
- Maximo **5 teammates simultaneos** por onda
- Cada teammate recebe **lista explicita** de arquivos que pode tocar
- Teammates em paralelo **NAO podem editar o mesmo arquivo**
- Quality gate **obrigatorio** ao final (test-runner + reviewer)
- Se risco alto: adicionar arquiteto na Onda 0 (analise de impacto)
- **5-6 tasks por teammate** e o ideal para produtividade

---

## FASE 4: EXECUCAO (Apos aprovacao do usuario)

### 4.1 Criar o Time

Usar `TeamCreate` para criar o time:
```
TeamCreate({
  team_name: "[nome-descritivo-do-time]",
  description: "[descricao da tarefa]"
})
```

### 4.2 Criar Tasks na Task List Compartilhada

Usar `TaskCreate` para cada tarefa do plano. Definir dependencias com `TaskUpdate` (blocks/blockedBy):
- Tasks da Onda 1: sem dependencias (paralelas)
- Tasks da Onda 2: blockedBy tasks da Onda 1
- Quality Gate: blockedBy todas as tasks de implementacao

### 4.3 Spawnar Teammates

Usar `Agent` com `team_name` e `name` para cada teammate. Cada teammate e uma **instancia independente** do Claude Code que:
- Tem seu proprio context window
- Pode se comunicar com outros teammates via mensagens
- Acessa a task list compartilhada
- Vai idle apos cada turno (isso e normal — enviar mensagem acorda o teammate)

**Spawnar teammates da mesma onda em PARALELO** (multiplos Agent calls no mesmo bloco).

### 4.4 Prompt de cada Teammate

Cada teammate recebe prompt autossuficiente com:

1. **CONTEXTO**: Stack do projeto e informacoes relevantes
2. **TIME**: Nome do time e quem sao os outros teammates
3. **TAREFA**: Exatamente o que fazer (especifico, sem ambiguidade)
4. **ARQUIVOS**: Lista COMPLETA de paths que deve ler/editar
5. **RESTRICOES**: O que NAO fazer (ex: "nao alterar logica, apenas CSS")
6. **ENTREGAVEL**: O que retornar ao final
7. **COORDENACAO**: "Apos completar sua task, marque como completed via TaskUpdate e verifique TaskList para proximas tasks disponiveis. Se precisar de informacao de outro teammate, envie mensagem via SendMessage."

### 4.5 Fluxo de Execucao

```
1. TeamCreate -> cria time e task list
2. TaskCreate (x N) -> cria todas as tasks com dependencias
3. Agent (x N, paralelo) -> spawna teammates da Onda 1 com team_name e name
   -> Teammates trabalham autonomamente:
     - Pegam tasks da task list
     - Marcam como in_progress -> completed
     - Comunicam entre si via SendMessage se necessario
     - Vao idle quando terminam (normal — enviar mensagem acorda)
4. Quando Onda 1 completa:
   -> Tasks da Onda 2 desbloqueiam automaticamente
   -> Spawnar teammates da Onda 2 (ou enviar mensagem para teammates existentes)
5. Quality Gate:
   -> Spawnar test-runner e reviewer
   -> Aguardar resultados
6. SendMessage type: "shutdown_request" -> encerrar teammates
7. TeamDelete -> limpar recursos do time
```

### 4.6 Comunicacao durante execucao

- **Mensagens automaticas**: teammates enviam mensagens automaticamente quando completam tasks — NAO precisa verificar inbox manualmente
- **Teammates idle**: e NORMAL — significa que estao esperando input. Enviar mensagem acorda o teammate.
- **Broadcast**: enviar para todos simultaneamente. Usar com moderacao.
- **DMs entre teammates**: quando um teammate envia DM para outro, um resumo aparece na notificacao de idle.

### 4.7 Resolucao de conflitos
Se dois teammates editaram o mesmo arquivo:
1. Verificar git diff do arquivo
2. Manter a versao mais completa
3. Registrar no relatorio

---

## FASE 5: INTEGRACAO E VALIDACAO

1. **Build**: npm run build (via test-runner teammate)
2. **Review**: reviewer verifica qualidade de todas as mudancas
3. **Conflitos**: verificar se algum teammate sobrescreveu outro
4. **Cleanup**: enviar shutdown_request para todos -> TeamDelete
5. **Relatorio final**:

```
## Resultado da Execucao — Agent Teams

**Status:** SUCESSO / PARCIAL / FALHA
**Time:** [nome do time]
**Teammates executados:** N
**Tasks completadas:** N/N
**Arquivos alterados:** N
**Build:** PASS / FAIL

### Por teammate:
- [nome]: OK — completou N tasks, alterou X arquivos (lista)
- [nome]: OK — completou N tasks, alterou Y arquivos (lista)

### Quality Gate:
- Build: PASS
- Review: N issues (N criticos, N medios, N baixos)

### Comunicacao entre teammates:
- [resumo das mensagens trocadas, se relevante]

### Mudancas pendentes:
- [lista do que nao foi possivel fazer, se houver]
```

---

## EXEMPLOS DE USO

### Exemplo 1: Aplicar design system no projeto inteiro
```
/agent-teams-v2 aplicar paleta de cores em todos os componentes
```
-> Padrao: **Parallel** (cada teammate pega um grupo de componentes)
-> Onda 1: 4x design-applier — comunicam entre si para consistencia
-> Quality Gate: test-runner + reviewer

### Exemplo 2: Nova feature (CRUD completo)
```
/agent-teams-v2 implementar CRUD completo de OKR com banco, API e frontend
```
-> Padrao: **Pipeline**
-> Onda 0: arquiteto (analise de impacto)
-> Onda 1: dev-backend (banco + API) + researcher (referencias de UI)
-> Onda 2: dev-frontend — recebe contexto do backend via mensagem
-> Quality Gate: test-runner + reviewer

### Exemplo 3: Debug com hipoteses concorrentes
```
/agent-teams-v2 investigar por que o dashboard trava com muitos dados
```
-> Padrao: **Swarm**
-> Onda 1: 3x investigador — debatem entre si via mensagens
-> Sintese: consolidar diagnostico

### Exemplo 4: Refatoracao cross-cutting
```
/agent-teams-v2 migrar todos os confirm() e alert() nativos para useModal()
```
-> Padrao: **Parallel**
-> Onda 1: researcher (mapeia usos — compartilha com migradores)
-> Onda 2: 3x migrator — coordenam via task list
-> Quality Gate: test-runner + reviewer

### Exemplo 5: Code review paralelo
```
/agent-teams-v2 revisar as mudancas do ultimo commit em profundidade
```
-> Padrao: **Parallel**
-> Onda 1: 3x reviewer (seguranca, performance, testes) — desafiam achados uns dos outros
-> Sintese: consolidar findings
