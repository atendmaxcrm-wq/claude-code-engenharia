'use strict';

/**
 * Search Module - Semantic and full-text search for memories
 */

const { query } = require('./db');
const { generateEmbedding } = require('./embeddings');
const { logQuery } = require('./query-logger');

/**
 * Semantic similarity search
 * @param {string} queryText - Natural language query
 * @param {object} options
 * @returns {Promise<object>}
 */
async function searchSimilar(queryText, options = {}) {
  const {
    match_count = 10,
    similarity_threshold = 0.3,
    memory_type = null,
    agent_id = null,
    active_only = true,
    query_source = 'manual',
    session_id = null,
  } = options;

  const start = Date.now();

  const embedding = await generateEmbedding(queryText);
  const vectorStr = `[${embedding.join(',')}]`;

  const result = await query(
    `SELECT * FROM search_memories_by_similarity(
      $1::vector(1536), $2, $3, $4::memory_type_enum, $5, $6
    )`,
    [vectorStr, match_count, similarity_threshold, memory_type, agent_id, active_only],
  );

  const latency = Date.now() - start;

  await logQuery({
    query_text: queryText,
    query_embedding: vectorStr,
    query_source,
    session_id,
    agent_id,
    results_count: result.rows.length,
    top_similarity: result.rows.length > 0 ? result.rows[0].similarity : null,
    results_ids: result.rows.map((r) => r.id),
    latency_ms: latency,
  }).catch(() => {});

  return {
    query: queryText,
    matches: result.rows,
    total: result.rows.length,
    latency_ms: latency,
    filters: { memory_type, agent_id, similarity_threshold },
  };
}

/**
 * Full-text search using PostgreSQL tsvector (Portuguese)
 * @param {string} queryText
 * @param {object} options
 * @returns {Promise<object>}
 */
async function searchFullText(queryText, options = {}) {
  const { match_count = 10, memory_type = null, agent_id = null } = options;

  const tsQuery = queryText
    .split(/\s+/)
    .filter(Boolean)
    .map((w) => `${w}:*`)
    .join(' & ');

  const result = await query(
    `SELECT id, memory_type, title, content, source, importance, tags, agent_id, created_at,
            ts_rank(to_tsvector('portuguese', COALESCE(title, '') || ' ' || COALESCE(content, '')),
                    to_tsquery('portuguese', $1)) AS rank
     FROM memories
     WHERE is_active = true
       AND (expires_at IS NULL OR expires_at > NOW())
       AND to_tsvector('portuguese', COALESCE(title, '') || ' ' || COALESCE(content, ''))
           @@ to_tsquery('portuguese', $1)
       AND ($2::memory_type_enum IS NULL OR memory_type = $2)
       AND ($3::text IS NULL OR agent_id = $3)
     ORDER BY rank DESC
     LIMIT $4`,
    [tsQuery, memory_type, agent_id, match_count],
  );

  return {
    query: queryText,
    matches: result.rows,
    total: result.rows.length,
  };
}

/**
 * Get memories by type (non-vector, for reinject hook)
 * @param {string} memoryType
 * @param {object} options
 * @returns {Promise<object[]>}
 */
async function getByType(memoryType, options = {}) {
  const { importance = null, agent_id = null, limit = 20 } = options;

  const result = await query(
    'SELECT * FROM get_memories_by_type($1, $2::importance_enum, $3, $4)',
    [memoryType, importance, agent_id, limit],
  );

  return result.rows;
}

module.exports = { searchSimilar, searchFullText, getByType };
