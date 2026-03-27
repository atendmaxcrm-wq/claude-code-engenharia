-- Migration 003: Memory sessions table
-- Tracks Claude Code sessions for continuity

CREATE TABLE memory_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_number INTEGER NOT NULL,
  agent_id TEXT,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  ended_at TIMESTAMPTZ,
  summary TEXT,
  work_done TEXT[],
  next_steps TEXT[],
  files_changed TEXT[],
  compact_count INTEGER DEFAULT 0,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_memory_sessions_number ON memory_sessions(session_number);
CREATE INDEX idx_memory_sessions_agent ON memory_sessions(agent_id);
CREATE INDEX idx_memory_sessions_started ON memory_sessions(started_at DESC);
