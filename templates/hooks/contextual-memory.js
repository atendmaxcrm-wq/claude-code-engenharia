#!/usr/bin/env node
'use strict';

/**
 * Hook: Contextual Memory Search (UserPromptSubmit)
 *
 * A cada mensagem do usuario, busca memorias relevantes no pgvector
 * e injeta como contexto adicional no Claude Code.
 *
 * Arquitetura hibrida:
 *   1. Keyword ILIKE search (~50ms) - sempre roda
 *   2. Semantic embedding search (~300-800ms) - race com timeout 400ms
 *   3. Merge + dedup + session cache
 *
 * Custo: ~$0.02/mes (text-embedding-3-small)
 */

const fs = require('fs');
const path = require('path');

const SCRIPT_DIR = __dirname;
const PROJECT_ROOT = path.resolve(SCRIPT_DIR, '..', '..');
const MEMORY_MODULE = path.join(PROJECT_ROOT, 'memory');

// Configuracao
const SEMANTIC_TIMEOUT_MS = 400;
const MAX_RESULTS = 6;
const MAX_CONTENT_LENGTH = 200;
const SESSION_CACHE_DIR = '/tmp/claude-memory-sessions';
const MIN_PROMPT_LENGTH = 10;

// Stopwords PT-BR + EN
const STOPWORDS = new Set([
  'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'do', 'da', 'dos', 'das',
  'em', 'no', 'na', 'nos', 'nas', 'por', 'para', 'com', 'sem', 'como',
  'que', 'ou', 'se', 'nao', 'mais', 'menos', 'muito', 'pouco', 'tambem',
  'ja', 'ainda', 'so', 'apenas', 'quero', 'preciso', 'pode', 'fazer',
  'criar', 'mudar', 'trocar', 'ajustar', 'verificar', 'olhar', 'ver',
  'me', 'meu', 'minha', 'esta', 'esse', 'isso', 'ter', 'ser', 'estar',
  'tem', 'sao', 'foi', 'vou', 'vai', 'vamos', 'aqui', 'ali', 'la',
  'bem', 'bom', 'boa', 'tudo', 'todo', 'toda', 'todos', 'todas',
  'the', 'and', 'is', 'to', 'of', 'in', 'it', 'this', 'that', 'can',
  'you', 'how', 'what', 'why', 'where', 'when', 'are', 'was', 'were',
]);

// Mensagens triviais que nao precisam de busca
const TRIVIAL_PATTERN = /^(sim|nao|s|n|ok|certo|feito|pronto|valeu|obrigado|beleza|perfeito|yes|no|y|continua|pode|bora|vai|legal|show|massa|top|dale|boa|blz|vlw|tmj|opa)$/i;

function shouldSearch(prompt) {
  if (!prompt) return false;
  const trimmed = prompt.trim();
  if (trimmed.length < MIN_PROMPT_LENGTH) return false;
  if (TRIVIAL_PATTERN.test(trimmed)) return false;
  if (/^\/[a-z-]+$/i.test(trimmed)) return false;
  return true;
}

function extractKeywords(text) {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s\-_\.]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 2 && !STOPWORDS.has(w));
}

async function keywordSearch(dbQuery, keywords, limit = 8) {
  if (keywords.length === 0) return [];

  const conditions = keywords.map((_, i) =>
    `(LOWER(title) LIKE '%' || $${i + 1} || '%' OR LOWER(content) LIKE '%' || $${i + 1} || '%')`
  ).join(' OR ');

  const scoreExpr = keywords.map((_, i) =>
    `(CASE WHEN LOWER(title) LIKE '%' || $${i + 1} || '%' THEN 3 ELSE 0 END + ` +
    `CASE WHEN LOWER(content) LIKE '%' || $${i + 1} || '%' THEN 1 ELSE 0 END)`
  ).join(' + ');

  const sql = `
    SELECT id, memory_type, title, LEFT(content, ${MAX_CONTENT_LENGTH}) as content,
           importance, tags, (${scoreExpr}) as keyword_score
    FROM memories
    WHERE is_active = true
      AND (expires_at IS NULL OR expires_at > NOW())
      AND (${conditions})
    ORDER BY keyword_score DESC,
      CASE importance
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'normal' THEN 3
        ELSE 4
      END,
      created_at DESC
    LIMIT $${keywords.length + 1}
  `;

  const result = await dbQuery(sql, [...keywords, limit]);
  return result.rows;
}

async function semanticSearchWithTimeout(searchSimilar, prompt, timeoutMs) {
  return Promise.race([
    searchSimilar(prompt, {
      match_count: 8,
      similarity_threshold: 0.45,
      query_source: 'hook-contextual',
    }),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('timeout')), timeoutMs)
    ),
  ]).catch(() => null);
}

function mergeResults(kwResults, semResults, limit) {
  const seen = new Set();
  const merged = [];

  if (semResults && semResults.matches) {
    for (const m of semResults.matches) {
      if (!seen.has(m.id)) {
        seen.add(m.id);
        merged.push({ ...m, source: 'semantic' });
      }
    }
  }

  for (const m of kwResults) {
    if (!seen.has(m.id)) {
      seen.add(m.id);
      merged.push({ ...m, source: 'keyword' });
    }
  }

  return merged.slice(0, limit);
}

function getSessionCache(sessionId) {
  if (!sessionId) return { injected: [] };
  const cacheFile = path.join(SESSION_CACHE_DIR, `${sessionId}.json`);
  try {
    if (fs.existsSync(cacheFile)) {
      const data = JSON.parse(fs.readFileSync(cacheFile, 'utf-8'));
      return data;
    }
  } catch { /* ignore */ }
  return { injected: [] };
}

function saveSessionCache(sessionId, cache) {
  if (!sessionId) return;
  try {
    if (!fs.existsSync(SESSION_CACHE_DIR)) {
      fs.mkdirSync(SESSION_CACHE_DIR, { recursive: true });
    }
    fs.writeFileSync(
      path.join(SESSION_CACHE_DIR, `${sessionId}.json`),
      JSON.stringify(cache)
    );
  } catch { /* ignore */ }
}

function filterAlreadyInjected(sessionId, results) {
  const cache = getSessionCache(sessionId);
  const injectedSet = new Set(cache.injected);
  const filtered = results.filter(m => !injectedSet.has(m.id));

  cache.injected.push(...filtered.map(m => m.id));
  saveSessionCache(sessionId, cache);

  return filtered;
}

function formatOutput(results, prompt) {
  if (results.length === 0) return null;

  const typeLabels = {
    decision: 'DECISAO',
    gotcha: 'GOTCHA',
    pattern: 'PADRAO',
    insight: 'INSIGHT',
    session_note: 'NOTA',
    progress: 'PROGRESSO',
    roadmap: 'ROADMAP',
    knowledge: 'CONHECIMENTO',
  };

  const lines = [];
  lines.push(`[Memoria contextual: ${results.length} memorias relevantes]`);
  lines.push('');

  for (const m of results) {
    const type = typeLabels[m.memory_type] || m.memory_type.toUpperCase();
    const imp = m.importance === 'critical' ? ' [CRITICO]' : '';
    const content = m.content
      ? m.content.replace(/\n/g, ' ').substring(0, MAX_CONTENT_LENGTH)
      : '';

    lines.push(`- **[${type}${imp}]** ${m.title}`);
    if (content) {
      lines.push(`  ${content}`);
    }
  }

  lines.push('');
  lines.push('[Use search_memories (MCP) para detalhes completos]');

  return lines.join('\n');
}

function loadEnvFromMcp() {
  try {
    const mcpPath = path.join(PROJECT_ROOT, '.mcp.json');
    const mcpConfig = JSON.parse(fs.readFileSync(mcpPath, 'utf-8'));
    const env = mcpConfig.mcpServers['claude-code-memory'].env;
    for (const [key, val] of Object.entries(env)) {
      if (!process.env[key]) process.env[key] = val;
    }
  } catch (err) {
    throw new Error(`Failed to load .mcp.json: ${err.message}`);
  }
}

async function main() {
  loadEnvFromMcp();

  let input = '';
  for await (const chunk of process.stdin) {
    input += chunk;
  }

  let data;
  try {
    data = JSON.parse(input);
  } catch {
    process.exit(0);
  }

  const prompt = data.prompt || '';
  const sessionId = data.session_id || '';

  if (!shouldSearch(prompt)) {
    process.exit(0);
  }

  const { query, close } = require(path.join(MEMORY_MODULE, 'db'));

  let searchSimilar;
  try {
    searchSimilar = require(path.join(MEMORY_MODULE, 'search')).searchSimilar;
  } catch {
    searchSimilar = null;
  }

  try {
    const keywords = extractKeywords(prompt);

    const [kwResults, semResults] = await Promise.all([
      keywords.length > 0
        ? keywordSearch(query, keywords, 8)
        : Promise.resolve([]),
      searchSimilar
        ? semanticSearchWithTimeout(searchSimilar, prompt, SEMANTIC_TIMEOUT_MS)
        : Promise.resolve(null),
    ]);

    const merged = mergeResults(kwResults, semResults, MAX_RESULTS);
    const filtered = filterAlreadyInjected(sessionId, merged);
    const output = formatOutput(filtered, prompt);

    if (output) {
      process.stdout.write(output);
    }
  } catch (err) {
    process.stderr.write(`[contextual-memory] Error: ${err.message}\n`);
  } finally {
    await close().catch(() => {});
  }

  process.exit(0);
}

main().catch(() => process.exit(0));
