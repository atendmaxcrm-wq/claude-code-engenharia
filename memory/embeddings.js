'use strict';

/**
 * Embedding Generator - Memory RAG System
 *
 * Generates vector embeddings using OpenAI API.
 * Supports single and batch processing.
 *
 * Environment variables:
 *   - OPENAI_API_KEY
 *   - OPENAI_EMBEDDING_MODEL (default: text-embedding-3-small)
 */

const OpenAI = require('openai');

let _client = null;

function getClient() {
  if (!_client) {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      throw new Error('OPENAI_API_KEY environment variable is required');
    }
    _client = new OpenAI({ apiKey });
  }
  return _client;
}

const MODEL = process.env.OPENAI_EMBEDDING_MODEL || 'text-embedding-3-small';
const BATCH_SIZE = 100;
const MAX_INPUT_LENGTH = 8000;

/**
 * Generate embedding for a single text
 * @param {string} text
 * @returns {Promise<number[]>} 1536-dimensional vector
 */
async function generateEmbedding(text) {
  const client = getClient();
  const response = await client.embeddings.create({
    model: MODEL,
    input: text.substring(0, MAX_INPUT_LENGTH),
    dimensions: 1536,
  });
  return response.data[0].embedding;
}

/**
 * Generate embeddings for multiple texts in batches
 * @param {string[]} texts
 * @returns {Promise<number[][]>} Array of embeddings
 */
async function generateEmbeddingsBatch(texts) {
  const client = getClient();
  const results = [];

  for (let i = 0; i < texts.length; i += BATCH_SIZE) {
    const batch = texts.slice(i, i + BATCH_SIZE).map((t) => t.substring(0, MAX_INPUT_LENGTH));
    const response = await client.embeddings.create({
      model: MODEL,
      input: batch,
      dimensions: 1536,
    });
    results.push(...response.data.map((d) => d.embedding));
  }

  return results;
}

/**
 * Build embedding text from memory fields
 * @param {string} title
 * @param {string} content
 * @returns {string}
 */
function buildEmbeddingText(title, content) {
  return `${title} ${content}`.substring(0, MAX_INPUT_LENGTH);
}

module.exports = { generateEmbedding, generateEmbeddingsBatch, buildEmbeddingText };
