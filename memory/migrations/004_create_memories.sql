-- Migration 004: Core memories table with vector embeddings

CREATE TABLE memories (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  memory_type memory_type_enum NOT NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  source TEXT NOT NULL DEFAULT 'manual',
  source_file TEXT,
  session_id UUID REFERENCES memory_sessions(id) ON DELETE SET NULL,
  agent_id TEXT,
  importance importance_enum DEFAULT 'normal',
  tags TEXT[] DEFAULT '{}',
  embedding vector(1536),
  metadata JSONB DEFAULT '{}',
  is_active BOOLEAN DEFAULT true,
  embedded_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_memories_type ON memories(memory_type);
CREATE INDEX idx_memories_agent ON memories(agent_id);
CREATE INDEX idx_memories_active ON memories(is_active);
CREATE INDEX idx_memories_importance ON memories(importance);
CREATE INDEX idx_memories_source_file ON memories(source_file);
CREATE INDEX idx_memories_created ON memories(created_at DESC);
CREATE INDEX idx_memories_expires ON memories(expires_at) WHERE expires_at IS NOT NULL;
