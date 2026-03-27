-- Migration 001: Enable required extensions
-- pgvector for vector similarity search
-- uuid-ossp for UUID generation

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
