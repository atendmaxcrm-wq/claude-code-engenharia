---
name: database-query
description: Padroes de queries SQL e schema PostgreSQL. Use ao criar tabelas, migrations ou queries complexas.
---

# Database Query Patterns

## Stack
- PostgreSQL 16 + pgvector
- Conexao: Conforme CLAUDE.md do projeto
- Acesso: `psql -U <user> -d <database>`

## Queries Parametrizadas (OBRIGATORIO)
```sql
-- CORRETO
SELECT * FROM posts WHERE id = $1 AND status = $2

-- ERRADO (SQL injection)
SELECT * FROM posts WHERE id = '${id}'
```

## Criar Tabela
```sql
CREATE TABLE IF NOT EXISTS nome_tabela (
  id SERIAL PRIMARY KEY,
  campo VARCHAR(255) NOT NULL,
  descricao TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_nome_tabela_campo ON nome_tabela(campo);
```

## Padroes
- Nomes em snake_case
- Sempre `id SERIAL PRIMARY KEY`
- Sempre `created_at`, `updated_at` com DEFAULT NOW()
- Soft delete: `is_active BOOLEAN DEFAULT true`
- Indices em colunas de busca frequente
- Foreign keys com ON DELETE CASCADE ou SET NULL

## pgvector
```sql
-- Criar coluna vetorial
ALTER TABLE tabela ADD COLUMN embedding vector(1536);

-- Busca semantica
SELECT *, embedding <=> $1::vector AS similarity
FROM tabela
WHERE is_active = true
ORDER BY embedding <=> $1::vector
LIMIT 10;
```

## Boas Praticas
- EXPLAIN ANALYZE para queries lentas
- Indices compostos para queries com AND
- LIMIT sempre em SELECTs sem WHERE especifico
- Transacoes para operacoes multi-tabela
- Connection pooling (nao abrir conexao por request)
- VACUUM e ANALYZE periodicos
