'use strict';

/**
 * Query Logger - Audit log for memory queries
 */

const { query } = require('./db');

/**
 * Log a memory query to the audit table
 * @param {object} data
 * @returns {Promise<void>}
 */
async function logQuery(data) {
  const {
    query_text,
    query_embedding = null,
    query_source = 'manual',
    session_id = null,
    agent_id = null,
    results_count = 0,
    top_similarity = null,
    results_ids = [],
    latency_ms = null,
    metadata = {},
  } = data;

  await query(
    `INSERT INTO memory_queries (
      query_text, query_embedding, query_source, session_id, agent_id,
      results_count, top_similarity, results_ids, latency_ms, metadata
    ) VALUES ($1, $2::vector, $3, $4, $5, $6, $7, $8, $9, $10)`,
    [
      query_text, query_embedding, query_source, session_id, agent_id,
      results_count, top_similarity, results_ids, latency_ms,
      JSON.stringify(metadata),
    ],
  );
}

module.exports = { logQuery };
