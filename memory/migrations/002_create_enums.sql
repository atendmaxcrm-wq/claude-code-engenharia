-- Migration 002: Custom ENUM types for memory system

CREATE TYPE memory_type_enum AS ENUM (
  'decision',
  'pattern',
  'gotcha',
  'insight',
  'session_note',
  'progress',
  'roadmap',
  'knowledge'
);

CREATE TYPE importance_enum AS ENUM (
  'critical',
  'high',
  'normal',
  'low'
);
