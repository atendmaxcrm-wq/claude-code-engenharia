---
name: systematic-debugging
description: "Debug sistematico em 4 fases. Suporta Agent Teams com hipoteses paralelas para bugs complexos. Proibe quick fixes. Use ao investigar bugs ou comportamento inesperado."
---

# Systematic Debugging

Bug/comportamento inesperado: $ARGUMENTS

---

## Principio
> Quick fixes mascaram problemas. Encontre a CAUSA RAIZ, nao o sintoma.

## Workflow Padrao (4 Fases)

### Fase 1: INVESTIGAR
- Reproduzir o problema (cenario exato)
- Coletar evidencias: logs, estado, console, rede
- Tracar fluxo de dados: input → processamento → output
- Onde exatamente o comportamento desvia do esperado?

### Fase 2: ANALISAR
- Isolar o trecho de codigo responsavel
- Dados de entrada estao corretos?
- Logica de processamento esta correta?
- Output esta sendo usado corretamente?
- Como funcionava antes? O que mudou?

### Fase 3: HIPOTESE
- Formular ate 3 hipoteses ordenadas por probabilidade
- Para cada hipotese: o que explicaria? como testar? qual a correcao?
- Testar a hipotese mais provavel primeiro

### Fase 4: IMPLEMENTAR
- Corrigir a causa raiz (nao o sintoma)
- Testar que o problema original foi resolvido
- Testar que nao introduziu regressoes
- Documentar em troubleshooting.md

---

## Modo Agent Teams (Hipoteses Paralelas)

Usar quando: causa raiz nao obvia, multiplas teorias plausiveis, bug afeta multiplas camadas.

### Padrao "Competing Hypotheses"

Spawnar 3 teammates que testam hipoteses diferentes simultaneamente:

| Teammate | Hipotese | Investigacao |
|----------|---------|-------------|
| **hypothesis-a** | Explore (sonnet) | Testa teoria A — busca evidencias a favor e contra |
| **hypothesis-b** | Explore (sonnet) | Testa teoria B — busca evidencias a favor e contra |
| **hypothesis-c** | Explore (sonnet) | Testa teoria C — busca evidencias a favor e contra |

### Execucao

```
TeamCreate: { team_name: "debug-[bug]", description: "Debug: [sintoma]" }

Antes de spawnar: Lead formula 3 hipoteses baseado em evidencias iniciais.

Wave 1 (todos paralelos — read-only):
- hypothesis-a: "Hipotese: [teoria A]" — investiga e tenta provar/refutar
- hypothesis-b: "Hipotese: [teoria B]" — investiga e tenta provar/refutar
- hypothesis-c: "Hipotese: [teoria C]" — investiga e tenta provar/refutar

Comunicacao entre teammates:
- Se um REFUTA sua hipotese → avisa os outros (eliminacao)
- Se um CONFIRMA sua hipotese → avisa os outros (podem parar)
- Se um encontra pista relevante pra outro → SendMessage direto

Consolidacao: Lead analisa resultados:
- Hipotese confirmada → implementar fix
- Todas refutadas → formular novas hipoteses
- Evidencias contraditórias → investigacao mais profunda

TeamDelete
```

### Padrao "Multi-Layer Investigation"

Para bugs que atravessam camadas (frontend → API → banco):

```
- frontend-investigator: examina componentes, estado, requests
- api-investigator: examina rotas, middleware, services
- db-investigator: examina queries, dados, triggers
```

Todos rodam em paralelo (read-only). Lead cruza achados.

### Quando NAO usar Agent Teams
- Erro obvio nos logs (stack trace claro) → corrigir direto
- Bug em 1 arquivo/funcao isolada → debug manual
- Problema de config (.env, package.json) → verificar direto

---

## Anti-padroes (PROIBIDO)
- Adicionar try/catch para esconder erro
- Adicionar setTimeout/retry sem entender por que falha
- Mudar codigo "pra ver se funciona" sem hipotese
- Dizer "funciona agora" sem entender por que
- Corrigir sintoma sem investigar causa
