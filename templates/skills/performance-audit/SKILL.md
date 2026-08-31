---
name: performance-audit
description: "Auditoria de performance. SQL, cache, re-renders, bundle, animacoes. Suporta Agent Teams para auditoria completa multi-dominio. Use ao otimizar performance."
---

# Performance Audit

Alvo da auditoria: $ARGUMENTS

---

## Checklist Completo

### SQL
- [ ] EXPLAIN ANALYZE em queries lentas (> 100ms)
- [ ] Indices em colunas de WHERE e JOIN
- [ ] Sem SELECT * em producao (so colunas necessarias)
- [ ] Sem N+1 (fetch em loop → JOIN ou batch)
- [ ] Connection pooling configurado
- [ ] Queries paginadas (LIMIT + OFFSET ou cursor)

### Cache
- [ ] Cache aplicado em dados que nao mudam frequentemente
- [ ] TTLs adequados por tipo de dado
- [ ] Invalidacao ao criar/editar/deletar
- [ ] Cache key com namespace (evita colisao)

### Frontend — Re-renders
- [ ] React.memo em componentes pesados
- [ ] useCallback/useMemo para referencias estaveis
- [ ] Keys unicas em listas (nao index)
- [ ] Context granular (nao context gigante)
- [ ] Sem state lift desnecessario

### Frontend — Bundle
- [ ] Lazy loading para rotas/componentes pesados
- [ ] Dynamic import para libs grandes
- [ ] Tree shaking funcionando
- [ ] Imagens otimizadas (formato, tamanho, next/image)

### Animacoes
- [ ] Shapes decorativos: div estatico (NUNCA animate Infinity)
- [ ] blur CSS: max 30px animado, 50px estatico
- [ ] ScrollReveal: so opacity + translate (sem blur/perspective)
- [ ] GSAP: scrub 0.5 (nao 1), scroll distance 100% (nao 200%)
- [ ] Sem Framer Motion animate com repeat: Infinity

### Backend
- [ ] Retry com backoff exponencial (3x: 2s-4s-8s)
- [ ] Timeout em chamadas externas
- [ ] Streaming para respostas grandes
- [ ] Compressao gzip/brotli
- [ ] Health check endpoint rapido (< 50ms)

### Metricas Alvo
| Metrica | Alvo |
|---------|------|
| LCP | < 2.5s |
| FID | < 100ms |
| CLS | < 0.1 |
| API Response | < 200ms (95th) |
| SQL Query | < 100ms |
| Health Check | < 50ms |

---

## Modo Agent Teams (Auditoria Completa)

Usar quando: auditoria cobre todos os dominios (SQL + frontend + backend + animacoes) em projeto grande.

### Time de Auditoria

| Teammate | Tipo | Dominio | O que audita |
|----------|------|---------|-------------|
| **db-auditor** | Explore (sonnet) | SQL + Cache | Queries, indices, N+1, pooling, cache TTLs |
| **frontend-auditor** | Explore (sonnet) | React + Bundle | Re-renders, memo, bundle size, lazy loading, imagens |
| **backend-auditor** | Explore (sonnet) | Node.js + API | Timeouts, retry, streaming, compressao, health |
| **animation-auditor** | Explore (sonnet) | CSS + Motion | Blur budget, infinite loops, GSAP config, scroll perf |

### Execucao

```
TeamCreate: { team_name: "perf-audit", description: "Performance audit [projeto]" }

Wave 1 (todos paralelos — read-only, sem conflito):
Todos os 4 auditores rodam simultaneamente.
Cada um gera relatorio com: issues encontrados, severidade, recomendacao.

Consolidacao: Lead merge todos relatorios em ranking unico:
- CRITICO: impacta usuario visivelmente
- ALTO: degradacao mensuravel
- MEDIO: melhoria recomendada
- BAIXO: nice-to-have

TeamDelete
```

### Formato do Relatorio Final

```
## Resultado — Performance Audit

| # | Issue | Severidade | Dominio | Recomendacao |
|---|-------|-----------|---------|-------------|
| 1 | N+1 em listUsers | CRITICO | SQL | JOIN ou batch query |
| 2 | Bundle 2.1MB | ALTO | Frontend | Lazy load rotas |
| ... | ... | ... | ... | ... |

**Score geral:** [N] issues (X criticos, Y altos, Z medios)
**Acao imediata:** [top 3 issues criticos]
```

### Quando NAO usar Agent Teams
- Auditoria de 1 dominio especifico (so SQL, so frontend) → fazer direto
- Projeto pequeno (menos de 20 arquivos) → checklist manual suficiente
