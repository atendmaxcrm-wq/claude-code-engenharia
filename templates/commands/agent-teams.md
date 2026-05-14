---
description: Orquestrar tarefa complexa com Agent Teams nativo (TeamCreate + teammates com team_name + SendMessage + TaskCreate). Use para tarefas grandes com multiplos dominios ou arquivos.
argument-hint: "[descricao da tarefa]"
user-invocable: true
---

Invoque imediatamente a skill `agent-teams` passando a tarefa adiante.

Tarefa: $ARGUMENTS

## Por que este command e fino

Este command NAO contem logica propria. Ele existe so para te dar `/agent-teams`
no autocomplete. A logica esta na skill `agent-teams` (em
`.claude/skills/agent-teams/SKILL.md`) que voce DEVE invocar via tool `Skill`:

```
Skill({ skill: "agent-teams", args: "$ARGUMENTS" })
```

## Importante

- NAO tente improvisar com Agent tool sem time
- NAO assuma "uso subagents simples na maioria dos casos" — a skill avalia
  isso internamente. Sua unica responsabilidade aqui e delegar pra skill
- A skill comeca com STOP gate que carrega schemas via ToolSearch. Sem isso,
  TeamCreate/SendMessage/TaskCreate ficam indisponiveis e o time nunca e
  criado de verdade
