'use strict';

/**
 * Memory Store - CRUD operations for the memories table
 */

const { query } = require('./db');
const { generateEmbedding, buildEmbeddingText } = require('./embeddings');

/**
 * Create a new memory with auto-generated embedding
 * @param {object} memory
 * @returns {Promise<{id: string, is_new: boolean}>}
 */
async function createMemory(memory) {
  const {
    memory_type,
    title,
    content,
    source = 'manual',
    source_file = null,
    session_id = null,
    agent_id = null,
    importance = 'normal',
    tags = [],
    metadata = {},
    expires_at = null,
  } = memory;

  let embedding = null;
  let embedded_at = null;

  try {
    const embeddingText = buildEmbeddingText(title, content);
    embedding = await generateEmbedding(embeddingText);
    embedded_at = new Date().toISOString();
  } catch (err) {
    process.stderr.write(`[memory-store] Embedding failed, storing without vector: ${err.message}\n`);
  }

  const vectorStr = embedding ? `[${embedding.join(',')}]` : null;

  const result = await query(
    `INSERT INTO memories (
      memory_type, title, content, source, source_file, session_id,
      agent_id, importance, tags, embedding, metadata, is_active,
      embedded_at, expires_at
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10::vector, $11, true, $12, $13)
    ON CONFLICT DO NOTHING
    RETURNING id, (xmax = 0) AS is_new`,
    [
      memory_type, title, content, source, source_file, session_id,
      agent_id, importance, tags, vectorStr, JSON.stringify(metadata),
      embedded_at, expires_at,
    ],
  );

  if (result.rows.length === 0) {
    return { id: null, is_new: false, note: 'duplicate or conflict' };
  }

  return result.rows[0];
}

/**
 * Update an existing memory
 * @param {string} id - Memory UUID
 * @param {object} updates
 * @returns {Promise<object>}
 */
async function updateMemory(id, updates) {
  const sets = [];
  const params = [id];
  let paramIdx = 2;

  const allowedFields = ['title', 'content', 'importance', 'tags', 'metadata', 'is_active', 'expires_at', 'agent_id'];
  const contentChanged = updates.title !== undefined || updates.content !== undefined;

  for (const field of allowedFields) {
    if (updates[field] !== undefined) {
      if (field === 'metadata') {
        sets.push(`metadata = metadata || $${paramIdx}::jsonb`);
        params.push(JSON.stringify(updates[field]));
      } else if (field === 'tags') {
        sets.push(`tags = $${paramIdx}`);
        params.push(updates[field]);
      } else {
        sets.push(`${field} = $${paramIdx}`);
        params.push(updates[field]);
      }
      paramIdx++;
    }
  }

  if (contentChanged) {
    try {
      const currentResult = await query('SELECT title, content FROM memories WHERE id = $1', [id]);
      if (currentResult.rows.length > 0) {
        const current = currentResult.rows[0];
        const newTitle = updates.title || current.title;
        const newContent = updates.content || current.content;
        const embeddingText = buildEmbeddingText(newTitle, newContent);
        const embedding = await generateEmbedding(embeddingText);
        sets.push(`embedding = $${paramIdx}::vector`);
        params.push(`[${embedding.join(',')}]`);
        paramIdx++;
        sets.push(`embedded_at = $${paramIdx}`);
        params.push(new Date().toISOString());
        paramIdx++;
      }
    } catch (err) {
      process.stderr.write(`[memory-store] Re-embedding failed: ${err.message}\n`);
    }
  }

  if (sets.length === 0) {
    return { updated: false };
  }

  const result = await query(
    `UPDATE memories SET ${sets.join(', ')} WHERE id = $1 RETURNING id, memory_type, title`,
    params,
  );

  return result.rows[0] || { updated: false };
}

/**
 * Soft-delete a memory
 * @param {string} id - Memory UUID
 * @returns {Promise<object>}
 */
async function deactivateMemory(id) {
  const result = await query(
    'UPDATE memories SET is_active = false WHERE id = $1 RETURNING id, title',
    [id],
  );
  return result.rows[0] || { deactivated: false };
}

/**
 * Get memory by ID
 * @param {string} id - Memory UUID
 * @returns {Promise<object|null>}
 */
async function getById(id) {
  const result = await query(
    `SELECT id, memory_type, title, content, source, source_file,
            session_id, agent_id, importance, tags, metadata,
            is_active, embedded_at, expires_at, created_at, updated_at
     FROM memories WHERE id = $1`,
    [id],
  );
  return result.rows[0] || null;
}

/**
 * Upsert memory by title and source_file (for markdown sync)
 * @param {object} memory
 * @returns {Promise<{id: string, is_new: boolean}>}
 */
async function upsertByTitle(memory) {
  const existing = await query(
    'SELECT id FROM memories WHERE title = $1 AND source_file = $2 AND is_active = true',
    [memory.title, memory.source_file],
  );

  if (existing.rows.length > 0) {
    const updated = await updateMemory(existing.rows[0].id, memory);
    return { id: existing.rows[0].id, is_new: false, ...updated };
  }

  return createMemory(memory);
}

module.exports = { createMemory, updateMemory, deactivateMemory, getById, upsertByTitle };
