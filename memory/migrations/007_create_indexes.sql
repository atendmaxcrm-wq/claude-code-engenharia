-- Migration 007: Performance indexes

-- Vector similarity index (IVFFlat)
-- lists=10 for small datasets; rebuild with sqrt(N) when data grows
CREATE INDEX idx_memories_embedding ON memories
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

-- Full-text search index (Portuguese)
CREATE INDEX idx_memories_fts ON memories
  USING gin(to_tsvector('portuguese',
    COALESCE(title, '') || ' ' || COALESCE(content, '')));

-- JSONB indexes
CREATE INDEX idx_memories_metadata ON memories USING gin(metadata);
CREATE INDEX idx_memories_tags ON memories USING gin(tags);

-- Composite index for common query patterns
CREATE INDEX idx_memories_type_active ON memories(memory_type, is_active)
  WHERE is_active = true;

CREATE INDEX idx_memories_agent_type ON memories(agent_id, memory_type)
  WHERE is_active = true;
