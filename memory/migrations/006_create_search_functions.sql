-- Migration 006: Semantic search functions for memories

-- Primary: vector similarity search with filters
CREATE OR REPLACE FUNCTION search_memories_by_similarity(
  query_embedding vector(1536),
  match_count INTEGER DEFAULT 10,
  similarity_threshold FLOAT DEFAULT 0.3,
  filter_type memory_type_enum DEFAULT NULL,
  filter_agent TEXT DEFAULT NULL,
  active_only BOOLEAN DEFAULT true
)
RETURNS TABLE (
  id UUID,
  memory_type memory_type_enum,
  title TEXT,
  content TEXT,
  source TEXT,
  importance importance_enum,
  tags TEXT[],
  agent_id TEXT,
  similarity FLOAT,
  created_at TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    m.id, m.memory_type, m.title, m.content, m.source,
    m.importance, m.tags, m.agent_id,
    (1 - (m.embedding <=> query_embedding))::FLOAT AS similarity,
    m.created_at
  FROM memories m
  WHERE m.embedding IS NOT NULL
    AND (NOT active_only OR m.is_active = true)
    AND (m.expires_at IS NULL OR m.expires_at > NOW())
    AND (filter_type IS NULL OR m.memory_type = filter_type)
    AND (filter_agent IS NULL OR m.agent_id = filter_agent)
    AND (1 - (m.embedding <=> query_embedding)) > similarity_threshold
  ORDER BY m.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql STABLE;

-- Secondary: get memories by type and importance (non-vector)
CREATE OR REPLACE FUNCTION get_memories_by_type(
  filter_type memory_type_enum,
  filter_importance importance_enum DEFAULT NULL,
  filter_agent TEXT DEFAULT NULL,
  result_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
  id UUID,
  memory_type memory_type_enum,
  title TEXT,
  content TEXT,
  importance importance_enum,
  tags TEXT[],
  agent_id TEXT,
  created_at TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    m.id, m.memory_type, m.title, m.content,
    m.importance, m.tags, m.agent_id, m.created_at
  FROM memories m
  WHERE m.is_active = true
    AND m.memory_type = filter_type
    AND (m.expires_at IS NULL OR m.expires_at > NOW())
    AND (filter_importance IS NULL OR m.importance = filter_importance)
    AND (filter_agent IS NULL OR m.agent_id = filter_agent)
  ORDER BY
    CASE m.importance
      WHEN 'critical' THEN 1
      WHEN 'high' THEN 2
      WHEN 'normal' THEN 3
      WHEN 'low' THEN 4
    END,
    m.created_at DESC
  LIMIT result_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- Get session memories
CREATE OR REPLACE FUNCTION get_session_memories(
  p_session_id UUID
)
RETURNS TABLE (
  id UUID,
  memory_type memory_type_enum,
  title TEXT,
  content TEXT,
  importance importance_enum,
  created_at TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    m.id, m.memory_type, m.title, m.content,
    m.importance, m.created_at
  FROM memories m
  WHERE m.session_id = p_session_id
    AND m.is_active = true
  ORDER BY m.created_at;
END;
$$ LANGUAGE plpgsql STABLE;
