-- Migration 005: Memory query audit log

CREATE TABLE memory_queries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  query_text TEXT NOT NULL,
  query_embedding vector(1536),
  query_source TEXT NOT NULL DEFAULT 'manual',
  session_id UUID REFERENCES memory_sessions(id) ON DELETE SET NULL,
  agent_id TEXT,
  results_count INTEGER DEFAULT 0,
  top_similarity FLOAT,
  results_ids UUID[],
  latency_ms INTEGER,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_memory_queries_source ON memory_queries(query_source);
CREATE INDEX idx_memory_queries_created ON memory_queries(created_at DESC);
CREATE INDEX idx_memory_queries_session ON memory_queries(session_id);
