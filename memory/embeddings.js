'use strict';

/**
 * Embedding Generator - Memory RAG System
 *
 * Generates vector embeddings using Google Gemini API (default) with optional
 * OpenAI fallback. Output is fixed at 1536 dimensions so it stays compatible
 * with the existing `vector(1536)` column and pgvector indexes.
 *
 * Provider selection:
 *   - If GEMINI_API_KEY (or GOOGLE_API_KEY) is set -> Gemini (default).
 *   - Else if OPENAI_API_KEY is set -> OpenAI (legacy fallback).
 *   - Force a provider with EMBEDDING_PROVIDER=gemini|openai.
 *
 * IMPORTANT (Gemini): when outputDimensionality != 3072 the returned vector is
 * NOT normalized. We L2-normalize it here so cosine/inner-product search stays
 * correct. OpenAI vectors already come normalized.
 *
 * Environment variables:
 *   - GEMINI_API_KEY / GOOGLE_API_KEY   (Gemini auth)
 *   - GEMINI_EMBEDDING_MODEL            (default: gemini-embedding-001)
 *   - OPENAI_API_KEY                    (OpenAI fallback auth)
 *   - OPENAI_EMBEDDING_MODEL            (default: text-embedding-3-small)
 *   - EMBEDDING_PROVIDER                (optional: 'gemini' | 'openai')
 *   - EMBEDDING_DIMENSIONS              (default: 1536)
 */

const DIMENSIONS = parseInt(process.env.EMBEDDING_DIMENSIONS || '1536', 10);
const BATCH_SIZE = 100;
const MAX_INPUT_LENGTH = 8000;

const GEMINI_MODEL = process.env.GEMINI_EMBEDDING_MODEL || 'gemini-embedding-001';
const OPENAI_MODEL = process.env.OPENAI_EMBEDDING_MODEL || 'text-embedding-3-small';

function getGeminiKey() {
  return process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY || null;
}

function resolveProvider() {
  const forced = (process.env.EMBEDDING_PROVIDER || '').toLowerCase();
  if (forced === 'gemini') return 'gemini';
  if (forced === 'openai') return 'openai';
  if (getGeminiKey()) return 'gemini';
  if (process.env.OPENAI_API_KEY) return 'openai';
  throw new Error('No embedding provider configured: set GEMINI_API_KEY or OPENAI_API_KEY');
}

// ─── Gemini ─────────────────────────────────────────────────────

const GEMINI_BASE = 'https://generativelanguage.googleapis.com/v1beta';

/** L2-normalize a vector in place (required for Gemini outputDimensionality != 3072). */
function l2normalize(vec) {
  let sum = 0;
  for (let i = 0; i < vec.length; i++) sum += vec[i] * vec[i];
  const norm = Math.sqrt(sum);
  if (norm === 0 || !isFinite(norm)) return vec;
  for (let i = 0; i < vec.length; i++) vec[i] = vec[i] / norm;
  return vec;
}

async function geminiEmbedSingle(text) {
  const key = getGeminiKey();
  const url = `${GEMINI_BASE}/models/${GEMINI_MODEL}:embedContent?key=${key}`;
  const body = {
    model: `models/${GEMINI_MODEL}`,
    content: { parts: [{ text: text.substring(0, MAX_INPUT_LENGTH) }] },
    outputDimensionality: DIMENSIONS,
  };
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Gemini embedContent failed (${res.status}): ${errText.substring(0, 300)}`);
  }
  const data = await res.json();
  const values = data.embedding && data.embedding.values;
  if (!values) throw new Error('Gemini embedContent returned no values');
  return l2normalize(values);
}

async function geminiEmbedBatch(texts) {
  const key = getGeminiKey();
  const url = `${GEMINI_BASE}/models/${GEMINI_MODEL}:batchEmbedContents?key=${key}`;
  const requests = texts.map((t) => ({
    model: `models/${GEMINI_MODEL}`,
    content: { parts: [{ text: t.substring(0, MAX_INPUT_LENGTH) }] },
    outputDimensionality: DIMENSIONS,
  }));
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ requests }),
  });
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Gemini batchEmbedContents failed (${res.status}): ${errText.substring(0, 300)}`);
  }
  const data = await res.json();
  const embeddings = data.embeddings || [];
  if (embeddings.length !== texts.length) {
    throw new Error(`Gemini batch size mismatch: got ${embeddings.length}, expected ${texts.length}`);
  }
  return embeddings.map((e) => l2normalize(e.values));
}

// ─── OpenAI (legacy fallback) ───────────────────────────────────

let _openaiClient = null;
function getOpenAIClient() {
  if (!_openaiClient) {
    const OpenAI = require('openai');
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) throw new Error('OPENAI_API_KEY environment variable is required');
    _openaiClient = new OpenAI({ apiKey });
  }
  return _openaiClient;
}

async function openaiEmbedSingle(text) {
  const client = getOpenAIClient();
  const response = await client.embeddings.create({
    model: OPENAI_MODEL,
    input: text.substring(0, MAX_INPUT_LENGTH),
    dimensions: DIMENSIONS,
  });
  return response.data[0].embedding;
}

async function openaiEmbedBatch(texts) {
  const client = getOpenAIClient();
  const results = [];
  for (let i = 0; i < texts.length; i += BATCH_SIZE) {
    const batch = texts.slice(i, i + BATCH_SIZE).map((t) => t.substring(0, MAX_INPUT_LENGTH));
    const response = await client.embeddings.create({
      model: OPENAI_MODEL,
      input: batch,
      dimensions: DIMENSIONS,
    });
    results.push(...response.data.map((d) => d.embedding));
  }
  return results;
}

// ─── Public API (provider-agnostic, stable signatures) ──────────

/**
 * Generate embedding for a single text.
 * @param {string} text
 * @returns {Promise<number[]>} DIMENSIONS-dimensional vector (default 1536)
 */
async function generateEmbedding(text) {
  const provider = resolveProvider();
  return provider === 'gemini' ? geminiEmbedSingle(text) : openaiEmbedSingle(text);
}

/**
 * Generate embeddings for multiple texts in batches.
 * @param {string[]} texts
 * @returns {Promise<number[][]>} Array of embeddings
 */
async function generateEmbeddingsBatch(texts) {
  if (!texts || texts.length === 0) return [];
  const provider = resolveProvider();
  if (provider === 'openai') return openaiEmbedBatch(texts);

  // Gemini: chunk into BATCH_SIZE groups
  const results = [];
  for (let i = 0; i < texts.length; i += BATCH_SIZE) {
    const batch = texts.slice(i, i + BATCH_SIZE);
    const embeddings = await geminiEmbedBatch(batch);
    results.push(...embeddings);
  }
  return results;
}

/**
 * Build embedding text from memory fields.
 * @param {string} title
 * @param {string} content
 * @returns {string}
 */
function buildEmbeddingText(title, content) {
  return `${title} ${content}`.substring(0, MAX_INPUT_LENGTH);
}

/** Which provider/model is active (for diagnostics/logging). */
function activeProvider() {
  const provider = resolveProvider();
  return {
    provider,
    model: provider === 'gemini' ? GEMINI_MODEL : OPENAI_MODEL,
    dimensions: DIMENSIONS,
  };
}

module.exports = {
  generateEmbedding,
  generateEmbeddingsBatch,
  buildEmbeddingText,
  activeProvider,
};
