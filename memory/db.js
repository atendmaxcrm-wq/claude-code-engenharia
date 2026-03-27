#!/usr/bin/env node
'use strict';

/**
 * Database Connection Pool - Memory RAG System
 *
 * Manages PostgreSQL connection pool with pgvector support.
 * Singleton pool pattern.
 *
 * Environment variables:
 *   - MEMORY_DB_HOST (default: localhost)
 *   - MEMORY_DB_PORT (default: 5432)
 *   - MEMORY_DB_USER (default: postgres)
 *   - MEMORY_DB_PASSWORD (default: empty)
 *   - MEMORY_DB_NAME (default: claude_memory)
 *   - MEMORY_DATABASE_URL (full connection string, overrides individual vars)
 */

const { Pool } = require('pg');

let _pool = null;

function getConnectionConfig() {
  if (process.env.MEMORY_DATABASE_URL) {
    return { connectionString: process.env.MEMORY_DATABASE_URL };
  }
  return {
    host: process.env.MEMORY_DB_HOST || 'localhost',
    port: parseInt(process.env.MEMORY_DB_PORT || '5432', 10),
    user: process.env.MEMORY_DB_USER || 'postgres',
    password: process.env.MEMORY_DB_PASSWORD || '',
    database: process.env.MEMORY_DB_NAME || 'claude_memory',
  };
}

function getPool() {
  if (!_pool) {
    _pool = new Pool({
      ...getConnectionConfig(),
      max: 10,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 5000,
    });
    _pool.on('error', (err) => {
      process.stderr.write(`[memory-db] Pool error: ${err.message}\n`);
    });
  }
  return _pool;
}

async function query(text, params) {
  const pool = getPool();
  const start = Date.now();
  const result = await pool.query(text, params);
  const duration = Date.now() - start;
  if (duration > 1000) {
    process.stderr.write(`[memory-db] Slow query (${duration}ms): ${text.substring(0, 100)}\n`);
  }
  return result;
}

async function close() {
  if (_pool) {
    await _pool.end();
    _pool = null;
  }
}

async function healthCheck() {
  try {
    const result = await query('SELECT 1 as ok, version() as pg_version');
    const vectorCheck = await query(
      "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'",
    );
    return {
      connected: true,
      pg_version: result.rows[0].pg_version,
      pgvector: vectorCheck.rows.length > 0 ? vectorCheck.rows[0].extversion : 'not installed',
    };
  } catch (err) {
    return { connected: false, error: err.message };
  }
}

module.exports = { getPool, query, close, healthCheck };
