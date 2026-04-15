---
name: nova-feature
description: "Planejar e implementar nova feature com analise de impacto. Suporta Agent Teams para features que envolvem multiplos dominios (DB + API + frontend). Use antes de implementar algo novo."
---

# Nova Feature — Planejamento e Implementacao

Feature solicitada: $ARGUMENTS

---

## Workflow Padrao (Feature Simples/Media)

1. **Consultar memoria**: Ler arquivos relevantes
   - Database schema: `/memoria/sistema/database-schema.md`
   - API endpoints: `/memoria/sistema/api-endpoints.md`
   - Permissoes: `/memoria/sistema/permissoes.md`
   - Changelog: `/memoria/sistema/changelog.md`

2. **Analisar impacto**: Identificar partes afetadas
   - Novas tabelas no banco?
   - Novos endpoints na API?
   - Novos componentes no frontend?
   - Mudancas em componentes existentes?

3. **Criar plano**: Apresentar plano detalhado
   - Alteracoes no banco (migrations SQL)
   - Endpoints da API necessarios
   - Componentes frontend necessarios
   - Permissoes requeridas

4. **Listar arquivos**: Criados/modificados com ordem de implementacao

NAO implementar sem aprovacao. Apresentar plano e aguardar OK.

---

## Modo Agent Teams (Feature Grande)

Usar quando: feature envolve 5+ arquivos, multiplos dominios (banco + API + frontend + testes).

### Time de Implementacao

Apos plano aprovado pelo usuario:

| Teammate | Tipo | Dominio | Arquivos |
|----------|------|---------|----------|
| **backend-dev** | general-purpose (sonnet) | Banco + API | migrations, routes, services |
| **frontend-dev** | general-purpose (sonnet) | Componentes + UI | components/, pages/, hooks/ |
| **test-dev** | general-purpose (sonnet) | Testes + validacao | tests/, build verification |

### Execucao

```
TeamCreate: { team_name: "feature-[nome]", description: "[descricao da feature]" }

Wave 1: backend-dev (banco + API precisam existir primeiro)
Wave 2 (apos Wave 1): frontend-dev + test-dev (paralelo)
Quality Gate: build + testes + health check
TeamDelete
```

### Regras
- **Wave 1 sempre backend** — frontend depende de API existente
- **Cada teammate recebe o plano aprovado** no prompt
- **Nenhum teammate muda o plano** — so implementa o que foi aprovado
- **Se surgir necessidade nova**: teammate comunica ao lead, lead consulta usuario

### Quando NAO usar Agent Teams
- Feature toca 1-3 arquivos → implementar direto
- Feature e so frontend (sem banco/API) → sessao unica
- Feature e so backend (sem frontend) → sessao unica
