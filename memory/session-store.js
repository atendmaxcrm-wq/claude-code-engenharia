'use strict';

/**
 * Session Store - CRUD operations for memory_sessions table
 */

const { query } = require('./db');

/**
 * Start a new session
 * @param {object} options
 * @returns {Promise<object>}
 */
async function startSession({ session_number, agent_id = null, metadata = {} }) {
  const result = await query(
    `INSERT INTO memory_sessions (session_number, agent_id, metadata)
     VALUES ($1, $2, $3)
     RETURNING id, session_number, started_at`,
    [session_number, agent_id, JSON.stringify(metadata)],
  );
  return result.rows[0];
}

/**
 * End a session with summary
 * @param {string} sessionId
 * @param {object} data
 * @returns {Promise<object>}
 */
async function endSession(sessionId, { summary, work_done = [], next_steps = [], files_changed = [] }) {
  const result = await query(
    `UPDATE memory_sessions
     SET ended_at = NOW(), summary = $2, work_done = $3,
         next_steps = $4, files_changed = $5
     WHERE id = $1
     RETURNING id, session_number, started_at, ended_at, summary`,
    [sessionId, summary, work_done, next_steps, files_changed],
  );
  return result.rows[0] || null;
}

/**
 * Get the most recent open session
 * @returns {Promise<object|null>}
 */
async function getCurrentSession() {
  const result = await query(
    `SELECT id, session_number, agent_id, started_at, compact_count, metadata
     FROM memory_sessions
     WHERE ended_at IS NULL
     ORDER BY started_at DESC
     LIMIT 1`,
  );
  return result.rows[0] || null;
}

/**
 * Get the most recent session (open or closed)
 * @returns {Promise<object|null>}
 */
async function getLastSession() {
  const result = await query(
    `SELECT id, session_number, agent_id, started_at, ended_at,
            summary, work_done, next_steps, files_changed, compact_count
     FROM memory_sessions
     ORDER BY started_at DESC
     LIMIT 1`,
  );
  return result.rows[0] || null;
}

/**
 * Increment compact count for a session
 * @param {string} sessionId
 * @returns {Promise<object>}
 */
async function incrementCompact(sessionId) {
  const result = await query(
    `UPDATE memory_sessions
     SET compact_count = compact_count + 1
     WHERE id = $1
     RETURNING id, compact_count`,
    [sessionId],
  );
  return result.rows[0] || null;
}

/**
 * Get next session number
 * @returns {Promise<number>}
 */
async function getNextSessionNumber() {
  const result = await query(
    'SELECT COALESCE(MAX(session_number), 0) + 1 AS next FROM memory_sessions',
  );
  return result.rows[0].next;
}

module.exports = {
  startSession,
  endSession,
  getCurrentSession,
  getLastSession,
  incrementCompact,
  getNextSessionNumber,
};
