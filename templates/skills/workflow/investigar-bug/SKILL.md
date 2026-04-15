---
name: investigar-bug
description: "Investigar e diagnosticar um bug reportado no sistema. Suporta Agent Teams para bugs complexos com hipoteses paralelas. Use quando algo nao funciona, da erro ou quebrou."
---

# Investigar Bug — Diagnostico Sistematico

Bug reportado: $ARGUMENTS

---

## Workflow Padrao (Bug Simples)

1. **Entender o problema**: Ler troubleshooting.md para ver se ja e conhecido
2. **Localizar codigo**: Identificar arquivos envolvidos via memoria e grep
3. **Analisar causa raiz**: Ler codigo, tracar fluxo de dados
4. **Verificar logs**: Checar pm2 logs, console, rede
5. **Propor solucao**: Apresentar causa raiz + correcao sugerida

NAO aplicar correcoes automaticamente. Apresentar diagnostico e aguardar aprovacao.

---

## Modo Agent Teams (Bug Complexo)

Usar quando: bug afeta multiplas camadas, causa raiz nao obvia, multiplas hipoteses possiveis.

### Time de Investigacao

| Teammate | Tipo | Foco |
|----------|------|------|
| **log-analyst** | Explore | Analisa logs, erros, stack traces |
| **code-tracer** | Explore | Traca fluxo de dados no codigo fonte |
| **db-inspector** | Explore | Verifica estado do banco, queries, dados |
| **env-checker** | Explore | Verifica configs, env vars, dependencias, versoes |

### Execucao

```
TeamCreate: { team_name: "bug-investigation", description: "[bug description]" }

Wave 1 (todos paralelos — read-only, sem conflito):
- log-analyst: busca erros em logs, identifica timestamps e patterns
- code-tracer: le o codigo do fluxo afetado, mapeia chamadas
- db-inspector: verifica dados no banco, queries recentes, estado
- env-checker: verifica .env, package.json, configs, versoes de libs

Consolidacao: Lead cruza achados de todos teammates
Diagnostico: Hipoteses ranqueadas por probabilidade
TeamDelete
```

### Padrao "Hipoteses Competitivas"

Para bugs especialmente dificeis, spawnar 3 teammates que testam hipoteses diferentes simultaneamente:

```
- hypothesis-1: "O bug e causado por [teoria A]" — investiga e tenta provar/refutar
- hypothesis-2: "O bug e causado por [teoria B]" — investiga e tenta provar/refutar  
- hypothesis-3: "O bug e causado por [teoria C]" — investiga e tenta provar/refutar
```

Teammates comunicam entre si: se um refuta sua hipotese, avisa os outros. Se um confirma, os outros param.

### Quando NAO usar Agent Teams
- Bug obvio (typo, import errado, config faltando) → investigar direto
- Bug em 1 arquivo isolado → nao precisa de time
- Logs ja mostram a causa clara → corrigir direto

---

## Anti-padroes (PROIBIDO)
- Adicionar try/catch para esconder erro
- Adicionar setTimeout/retry sem entender por que falha
- Mudar codigo "pra ver se funciona" sem hipotese
- Dizer "funciona agora" sem entender por que
- Corrigir sintoma sem investigar causa
