---
name: agent-teams
description: "Orquestracao multi-agent com Agent Teams nativo do Claude Code. Cria times reais com comunicacao entre teammates, task list compartilhada e quality gates. Use para tarefas grandes que envolvem multiplos arquivos ou dominios. Ativa quando o usuario pede: agent teams, time de agentes, trabalho paralelo, decompor tarefa, orquestrar agentes, swarm, ou qualquer tarefa complexa que beneficie de paralelismo."
---

# Agent Teams — Orquestracao Multi-Agent Nativa

Tarefa recebida: $ARGUMENTS

---

## COMO FUNCIONA

Agent Teams usa as ferramentas nativas do Claude Code:
- **TeamCreate** — cria o time + task list compartilhada
- **Agent tool** com `team_name` + `name` — spawna teammates que entram no time
- **TaskCreate/TaskUpdate** — gerencia tasks compartilhadas com dependencias
- **SendMessage** — comunicacao direta entre teammates (peer-to-peer)
- **TeamDelete** — cleanup ao final

**Voce (lead) coordena.** Teammates sao instancias Claude independentes com contexto proprio.

---

## FASE 1: ANALISE E DECOMPOSICAO

Antes de criar o time:

1. **Classificar a tarefa:**
   - Qual o escopo? (5-10 arquivos / 10+ arquivos / sistema inteiro)
   - Tem dependencias entre sub-tarefas?
   - Qual o risco? (baixo: UI/CSS | medio: logica | alto: types/API/banco)

2. **Mapear arquivos afetados:**
   - Use Agent tool com subagent_type="Explore" para levantar todos os arquivos
   - Agrupe por dominio (UI, logica, types, backend, config)

3. **Verificar se Agent Teams e necessario:**
   - Menos de 3 tarefas independentes? → Usar Agent tool simples (subagents)
   - Tarefas sequenciais sem paralelismo? → Fazer direto, sem time
   - 3+ tarefas paralelas com comunicacao util? → Agent Teams

4. **Escolher padrao de orquestracao:**

   | Padrao | Quando usar | Exemplo |
   |--------|-------------|---------|
   | **Parallel** | Sub-tarefas 100% independentes | Aplicar design em 5 modulos |
   | **Pipeline** | Fases sequenciais com handoff | Analyze → Implement → Test |
   | **Competing** | Multiplas hipoteses pro mesmo problema | Debug com 3 teorias |
   | **Specialist** | Cada teammate tem dominio diferente | Frontend + Backend + DB |
   | **Review** | Multiplos revisores com perspectivas distintas | Security + Performance + Patterns |

---

## FASE 2: MONTAGEM DO PLANO

Apresentar ao usuario neste formato ANTES de executar:

```
## Plano de Execucao — Agent Teams

**Tarefa:** [descricao]
**Padrao:** [parallel/pipeline/competing/specialist/review]
**Risco:** [baixo/medio/alto]
**Arquivos afetados:** [N arquivos]
**Custo estimado:** [N teammates x contexto = ~Nx tokens]

### Time
| # | Teammate | Tipo | Dominio | Arquivos |
|---|----------|------|---------|----------|
| 1 | [nome] | [general-purpose/Explore/Plan] | [area] | file1, file2 |
| 2 | [nome] | [tipo] | [area] | file3, file4 |

### Tasks (com dependencias)
| # | Task | Owner | Depende de |
|---|------|-------|------------|
| 1 | [descricao] | [teammate] | — |
| 2 | [descricao] | [teammate] | Task 1 |
| 3 | [descricao] | [teammate] | — |

### Quality Gate
| Validacao | Como |
|-----------|------|
| Build | npm run build / tsc |
| Testes | npm test (se existir) |
| Health | curl endpoint (se backend) |
| Conflitos | Verificar se teammates nao sobrescreveram mesmo arquivo |

**Aguardando aprovacao para executar...**
```

### Regras do plano:
- Maximo **5 teammates simultaneos** (custo escala linearmente)
- Cada teammate recebe **lista explicita de arquivos** que pode editar
- Teammates em paralelo **NAO podem editar o mesmo arquivo** (segundo sobrescreve primeiro)
- Quality gate **obrigatorio** ao final
- Se risco alto: adicionar teammate arquiteto na fase de design
- **5-6 tasks por teammate** e o ideal
- Preferir **haiku** ou **sonnet** para teammates de execucao (custo menor)
- Reservar **opus** para lead e tarefas que exigem raciocinio profundo

---

## FASE 3: EXECUCAO (Apos aprovacao do usuario)

### Passo 1 — Criar o time
```
TeamCreate: { team_name: "[nome-descritivo]", description: "[objetivo]" }
```

### Passo 2 — Criar tasks com dependencias
```
TaskCreate para cada task do plano
TaskUpdate com addBlockedBy para definir dependencias
```

### Passo 3 — Spawnar teammates
Spawnar teammates da mesma onda em PARALELO (multiplos Agent calls no mesmo bloco):
```
Agent tool: {
  prompt: "[prompt autossuficiente]",
  team_name: "[nome-do-time]",
  name: "[nome-do-teammate]",
  subagent_type: "[tipo]",
  model: "[sonnet/haiku/opus]"
}
```

### Template de prompt para teammate:
```
## CONTEXTO
Voce e [papel] no time [nome-do-time].
Projeto: [stack, framework, patterns relevantes]

## SUA TAREFA
[Descricao clara e especifica do que fazer]

## ARQUIVOS QUE VOCE PODE EDITAR
- [lista explicita de arquivos]

## ARQUIVOS QUE VOCE PODE LER (mas NAO editar)
- [arquivos de referencia]

## RESTRICOES
- NAO edite arquivos fora da sua lista
- NAO instale dependencias sem comunicar ao lead
- Ao terminar, marque sua task como completed via TaskUpdate

## ENTREGAVEL
[O que exatamente se espera como resultado]

## COMUNICACAO
- Para falar com outro teammate: SendMessage to "[nome]"
- Para reportar ao lead: SendMessage to "lead"
- Ao terminar: TaskUpdate status completed + mensagem ao lead
```

### Passo 4 — Monitorar
- Mensagens de teammates chegam automaticamente (nao precisa poll)
- Se teammate ficar idle: verificar se completou a task
- Se teammate travar: SendMessage com orientacao
- Se conflito detectado: intervir e redirecionar

### Passo 5 — Quality Gate
Apos todos teammates completarem:
1. Verificar que todas tasks estao completed
2. Build: verificar que compila sem erros
3. Conflitos: verificar se algum teammate sobrescreveu outro
4. Health check: curl endpoints se alterou backend
5. Testes: rodar se existirem

### Passo 6 — Cleanup
```
SendMessage to "*": { type: "shutdown_request" }
[Aguardar todos teammates confirmarem shutdown]
TeamDelete
```

---

## FASE 4: RELATORIO FINAL

```
## Resultado — Agent Teams

**Time:** [nome]
**Duracao:** [tempo aproximado]
**Teammates:** [N]

### Status por Teammate
| Teammate | Tasks | Status | Observacoes |
|----------|-------|--------|-------------|
| [nome] | [N/M] | Completo | [notas] |

### Quality Gate
| Check | Resultado |
|-------|-----------|
| Build | OK/FALHA |
| Testes | OK/FALHA/N/A |
| Health | OK/FALHA/N/A |
| Conflitos | Nenhum/[detalhes] |

### Arquivos Modificados
- [lista de todos os arquivos tocados por todos teammates]
```

---

## QUANDO NAO USAR AGENT TEAMS

- Tarefa com menos de 3 sub-tarefas independentes → Agent tool simples
- Tudo toca os mesmos 2-3 arquivos → sessao unica
- Workflow estritamente sequencial sem paralelismo → sessao unica
- Ajuste simples (texto, cor, config) → fazer direto
- Custo e preocupacao principal → subagents sao mais baratos

## REGRAS INVIOLAVEIS

1. **NUNCA criar time sem plano aprovado pelo usuario**
2. **NUNCA dois teammates editando o mesmo arquivo** (segundo sobrescreve)
3. **SEMPRE cleanup com TeamDelete ao final**
4. **SEMPRE quality gate antes de declarar concluido**
5. **NUNCA spawnar mais de 5 teammates simultaneos**
6. **SEMPRE dar prompt autossuficiente** (teammate nao tem seu contexto)
7. **NUNCA deixar teammates orfaos** (sem shutdown)
