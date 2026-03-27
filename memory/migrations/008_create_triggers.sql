-- Migration 008: Auto-update triggers

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_memories_updated_at
BEFORE UPDATE ON memories
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_memory_sessions_updated_at
BEFORE UPDATE ON memory_sessions
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
