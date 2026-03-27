#!/usr/bin/env node
'use strict';

/**
 * Hook: Reinject Memory after Context Compact
 *
 * Injects critical context after context window compaction.
 * Focused on: last session summary + critical gotchas + safety rules.
 *
 * Mode 1 (primary): pgvector queries
 * Mode 2 (fallback): markdown files
 */

const fs = require('fs');
const path = require('path');

const SCRIPT_DIR = __dirname;
const PROJECT_ROOT = path.resolve(SCRIPT_DIR, '..', '..');
const MEMORIA_DIR = path.join(PROJECT_ROOT, 'memoria');
const MEMORY_MODULE = path.join(PROJECT_ROOT, 'memory');

// Critical rules from file or empty
function loadCriticalRules() {
  const rulesPath = path.join(MEMORIA_DIR, 'sistema', 'critical-rules.md');
  try {
    if (fs.existsSync(rulesPath)) {
      return fs.readFileSync(rulesPath, 'utf-8');
    }
  } catch { /* ignore */ }
  return '';
}

async function injectFromPgvector() {
  // Load env from .mcp.json
  try {
    const mcpPath = path.join(PROJECT_ROOT, '.mcp.json');
    const mcpConfig = JSON.parse(fs.readFileSync(mcpPath, 'utf-8'));
    const env = mcpConfig.mcpServers['claude-code-memory'].env;
    for (const [key, val] of Object.entries(env)) {
      if (!process.env[key]) process.env[key] = val;
    }
  } catch { /* ignore */ }

  const { query, close } = require(path.join(MEMORY_MODULE, 'db'));

  const output = [];
  output.push('---');
  output.push('## [MEMORIA REINJETADA apos compactacao]');
  output.push('');

  // Last session info
  const lastSession = await query(`
    SELECT session_number, summary, work_done, next_steps, ended_at
    FROM memory_sessions
    ORDER BY started_at DESC LIMIT 1
  `);

  if (lastSession.rows.length > 0) {
    const s = lastSession.rows[0];
    output.push('### Ultima Sessao');
    output.push(`- **Sessao #${s.session_number}** (${s.ended_at ? new Date(s.ended_at).toISOString().split('T')[0] : 'em andamento'})`);
    if (s.summary) output.push(`- ${s.summary}`);
    if (s.next_steps && s.next_steps.length > 0) {
      output.push('- **Proximos passos:**');
      s.next_steps.forEach(step => output.push(`  - ${step}`));
    }
    output.push('');
  }

  // Critical gotchas only
  const gotchas = await query(`
    SELECT title, content FROM memories
    WHERE memory_type = 'gotcha' AND is_active = true
      AND importance = 'critical'
      AND (expires_at IS NULL OR expires_at > NOW())
    ORDER BY created_at DESC LIMIT 3
  `);

  if (gotchas.rows.length > 0) {
    output.push('### Armadilhas Criticas');
    gotchas.rows.forEach(g => {
      output.push(`- **${g.title}**: ${g.content.substring(0, 120)}`);
    });
    output.push('');
  }

  // Critical rules from file
  const rules = loadCriticalRules();
  if (rules) {
    output.push(rules);
    output.push('');
  }

  // How memory system works
  output.push('### Sistema de Memoria');
  output.push('- Hook **contextual-memory.js** busca memorias relevantes a CADA mensagem automaticamente');
  output.push('- Use `search_memories` (MCP) para busca manual aprofundada');
  output.push('- Use `search_memories_by_text` (MCP) para busca por keywords');
  output.push('');

  // Memory stats
  const stats = await query(`SELECT COUNT(*) as total FROM memories WHERE is_active = true`);
  output.push(`### Stats: ${stats.rows[0].total} memorias ativas no banco`);
  output.push('');

  output.push('---');

  await close();
  return output.join('\n');
}

function injectFromFiles() {
  const output = [];
  output.push('---');
  output.push('## [MEMORIA REINJETADA via Markdown (fallback)]');
  output.push('');

  // Critical rules from file
  const rules = loadCriticalRules();
  if (rules) {
    output.push(rules);
    output.push('');
  }

  const progressoPath = path.join(MEMORIA_DIR, 'progresso.md');
  if (fs.existsSync(progressoPath)) {
    output.push('### Progresso Atual');
    output.push('');
    output.push(fs.readFileSync(progressoPath, 'utf-8'));
    output.push('');
    output.push('---');
    output.push('');
  }

  const insightsPath = path.join(MEMORIA_DIR, 'insights.md');
  if (fs.existsSync(insightsPath)) {
    output.push('### Insights do Projeto');
    output.push('');
    output.push(fs.readFileSync(insightsPath, 'utf-8'));
    output.push('');
    output.push('---');
    output.push('');
  }

  ['roadmaps', 'sistema', 'conhecimento'].forEach(subdir => {
    const dir = path.join(MEMORIA_DIR, subdir);
    if (fs.existsSync(dir)) {
      const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'));
      if (files.length > 0) {
        output.push(`### Memoria/${subdir} (leia sob demanda)`);
        files.forEach(f => {
          const lines = fs.readFileSync(path.join(dir, f), 'utf-8').split('\n').length;
          output.push(`  - ${f} (${lines} linhas)`);
        });
        output.push('');
      }
    }
  });

  output.push('---');

  return output.join('\n');
}

async function main() {
  try {
    const output = await injectFromPgvector();
    process.stdout.write(output);
  } catch (err) {
    process.stderr.write(`[reinject-memory] pgvector failed (${err.message}), using markdown fallback\n`);
    const output = injectFromFiles();
    process.stdout.write(output);
  }
}

main().catch(() => {
  // Never block Claude Code
  process.exit(0);
});
