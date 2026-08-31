---
name: postgres-best-practices
description: PostgreSQL otimizado. Indices, EXPLAIN, pooling, tipos, vacuuming. Use ao otimizar queries ou projetar schema.
---

# PostgreSQL Best Practices

## Schema Design
- Nomes em snake_case (tabelas e colunas)
- Primary key: `id SERIAL` ou `id UUID DEFAULT gen_random_uuid()`
- Timestamps: `created_at TIMESTAMP DEFAULT NOW()`, `updated_at`
- Soft delete: `is_active BOOLEAN DEFAULT true`
- Enums como TEXT com CHECK constraint (nao ENUM type — dificulta migracao)
- Foreign keys com ON DELETE CASCADE ou SET NULL (nunca RESTRICT sem motivo)

## Indices
- Indice em toda coluna usada em WHERE, JOIN, ORDER BY frequente
- Indice composto para queries com AND (ex: `(user_id, created_at)`)
- Indice parcial para filtros comuns: `WHERE is_active = true`
- GIN para busca full-text (tsvector)
- GiST para tipos geometricos e ranges
- BRIN para tabelas append-only (logs, eventos)
- NAO indexar tudo — cada indice custa no INSERT/UPDATE

## Queries
- EXPLAIN ANALYZE para queries > 100ms
- Queries parametrizadas SEMPRE ($1, $2)
- LIMIT em toda query sem WHERE especifico
- Evitar SELECT * — listar colunas explicitamente
- JOIN > subquery na maioria dos casos
- EXISTS > COUNT quando so precisa saber se existe
- Batch INSERT/UPDATE para operacoes em massa

## pgvector
- Tipo `vector(1536)` para embeddings OpenAI
- Operador `<=>` para distancia cosseno (mais comum)
- Indice IVFFlat para < 1M vetores
- Indice HNSW para > 1M vetores (melhor recall)
- Filtrar ANTES de buscar vetores (WHERE + ORDER BY <=>)

## Connection Pooling
- NUNCA abrir conexao por request
- Pool de 10-20 conexoes (ajustar por carga)
- Timeout de conexao: 5s
- Idle timeout: 30s
- Statement timeout: 30s (evita queries runaway)

## Manutencao
- VACUUM ANALYZE semanal em tabelas com muitos UPDATEs
- pg_stat_statements para identificar queries lentas
- pg_stat_user_tables para tabelas com dead tuples
- Monitorar tamanho de indices (pg_relation_size)

## Tipos Recomendados
| Dado | Tipo PostgreSQL |
|------|-----------------|
| ID numerico | SERIAL / BIGSERIAL |
| ID universal | UUID |
| Texto curto | VARCHAR(255) |
| Texto longo | TEXT |
| Booleano | BOOLEAN |
| Inteiro | INTEGER |
| Decimal | NUMERIC(10,2) |
| Data/hora | TIMESTAMP |
| JSON flexivel | JSONB |
| Vetor ML | vector(1536) |
