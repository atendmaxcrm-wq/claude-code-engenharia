---
name: pesquisar-tech
description: "Pesquisar e avaliar tecnologias/libs antes de implementar. Suporta Agent Teams com pesquisadores paralelos e curador. Use ao considerar trocar lib ou abordagem tecnica."
---

# Pesquisar Tech — Avaliacao de Tecnologias

Pesquisa solicitada: $ARGUMENTS

---

## Workflow Padrao (Pesquisa Simples)

### Fase 1: Contexto
- O que temos hoje? Qual lib/implementacao?
- Quais problemas motivam a troca?
- Requisitos obrigatorios e desejaveis
- Restricoes tecnicas (versao Node, CJS/ESM, bundle size)

### Fase 2: Pesquisa
- Top 5 libs mais populares (npm downloads, stars, ultima release)
- Artigos comparativos, benchmarks, migration guides
- Alternativas nao-obvias, implementacao nativa

### Fase 3: Matriz de Decisao

| Criterio | Peso | Lib A | Lib B | Lib C |
|----------|------|-------|-------|-------|
| Requisito principal | ALTO | ? | ? | ? |
| Bundle size | MEDIO | ? | ? | ? |
| TypeScript | ALTO | ? | ? | ? |
| Manutencao ativa | ALTO | ? | ? | ? |
| CJS compativel | ALTO | ? | ? | ? |
| Comunidade | MEDIO | ? | ? | ? |

### Fase 4: Recomendacao
1. Recomendacao principal + justificativa
2. Alternativa
3. Riscos da migracao
4. Esforco estimado
5. Plano em alto nivel

NUNCA implementar durante a pesquisa. So recomendacao.

---

## Modo Agent Teams (Pesquisa Profunda)

Usar quando: decisao critica (lib core do projeto), multiplas alternativas viaveis, precisa de benchmarks reais.

### Time de Pesquisa

| Teammate | Tipo | Foco |
|----------|------|------|
| **npm-researcher** | Explore (sonnet) | npm stats, GitHub stars, releases, issues abertas, breaking changes |
| **docs-researcher** | Explore (sonnet) | Documentacao oficial, migration guides, API surface, exemplos |
| **community-researcher** | Explore (sonnet) | Blog posts, benchmarks, comparativos, Reddit, Stack Overflow |

### Execucao

```
TeamCreate: { team_name: "tech-research", description: "Evaluate [tech/lib]" }

Wave 1 (todos paralelos — read-only):
- npm-researcher: WebSearch npm trends, GitHub repos, changelogs
- docs-researcher: WebFetch docs oficiais, exemplos, TypeScript support
- community-researcher: WebSearch benchmarks, comparativos, experiencias reais

Comunicacao: Researchers avisam uns aos outros sobre achados relevantes.
Ex: npm-researcher descobre lib com 0 releases em 6 meses → avisa os outros.

Consolidacao: Lead monta matriz de decisao com dados dos 3 researchers.
TeamDelete
```

### Formato da Recomendacao

```
## Pesquisa Tech — [tema]

### Contexto
[O que temos hoje e por que queremos mudar]

### Candidatos Avaliados
| Lib | Stars | Downloads/sem | Ultima release | TS | Bundle |
|-----|-------|-------------|---------------|-----|--------|

### Matriz de Decisao
| Criterio | Peso | Lib A | Lib B | Lib C |
|----------|------|-------|-------|-------|

### Recomendacao
**Principal:** [lib] — [justificativa em 1 frase]
**Alternativa:** [lib] — [quando preferir esta]
**Riscos:** [lista]
**Proximo passo:** [plano de migracao em alto nivel]
```

### Quando NAO usar Agent Teams
- Pesquisa sobre 1 lib especifica (so quer saber se e boa) → pesquisar direto
- Decisao ja tomada, so precisa confirmar → WebSearch simples
- Lib trivial (formatter, icon pack) → nao justifica time
