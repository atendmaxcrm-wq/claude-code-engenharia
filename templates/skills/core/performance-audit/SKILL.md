---
name: performance-audit
description: Auditoria de performance. SQL, cache, re-renders, bundle, animacoes. Use ao otimizar performance.
---

# Performance Audit

## SQL
- [ ] EXPLAIN ANALYZE em queries lentas (> 100ms)
- [ ] Indices em colunas de WHERE e JOIN
- [ ] Sem SELECT * em producao (so colunas necessarias)
- [ ] Sem N+1 (fetch em loop → JOIN ou batch)
- [ ] Connection pooling configurado
- [ ] Queries paginadas (LIMIT + OFFSET ou cursor)

## Cache
- [ ] Cache aplicado em dados que nao mudam frequentemente
- [ ] TTLs adequados por tipo de dado
- [ ] Invalidacao ao criar/editar/deletar
- [ ] Cache key com namespace (evita colisao)

## Frontend — Re-renders
- [ ] React.memo em componentes pesados
- [ ] useCallback/useMemo para referencias estaveis
- [ ] Keys unicas em listas (nao index)
- [ ] Context granular (nao context gigante)
- [ ] Sem state lift desnecessario

## Frontend — Bundle
- [ ] Lazy loading para rotas/componentes pesados
- [ ] Dynamic import para libs grandes
- [ ] Tree shaking funcionando
- [ ] Imagens otimizadas (formato, tamanho, next/image)

## Animacoes (CRITICO neste projeto)
- [ ] Shapes decorativos: div estatico (NUNCA animate Infinity)
- [ ] blur CSS: max 30px animado, 50px estatico
- [ ] ScrollReveal: so opacity + translate (sem blur/perspective)
- [ ] GSAP: scrub 0.5 (nao 1), scroll distance 100% (nao 200%)
- [ ] requestAnimationFrame com gate (30fps OK para backgrounds)
- [ ] Sem Framer Motion animate com repeat: Infinity

## Backend
- [ ] Retry com backoff exponencial (3x: 2s-4s-8s)
- [ ] Timeout em chamadas externas
- [ ] Streaming para respostas grandes
- [ ] Compressao gzip/brotli
- [ ] Health check endpoint rapido (< 50ms)

## Metricas Alvo
| Metrica | Alvo |
|---------|------|
| LCP | < 2.5s |
| FID | < 100ms |
| CLS | < 0.1 |
| API Response | < 200ms (95th) |
| SQL Query | < 100ms |
| Health Check | < 50ms |
