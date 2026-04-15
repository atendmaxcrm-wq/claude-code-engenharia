#!/usr/bin/env node
'use strict';

/**
 * Hook: Reinject Memory after Context Compact
 *
 * Injects critical context after context window compaction.
 * Focused on: last session summary + critical gotchas + safety rules.
 *
 * The per-prompt contextual search is handled by contextual-memory.js
 * (UserPromptSubmit hook), so this hook only provides the safety net.
 *
 * Mode 1 (primary): pgvector queries - ~50 lines (~120 tokens)
 * Mode 2 (fallback): markdown files - ~200+ lines (~500+ tokens)
 */

const fs = require('fs');
const path = require('path');

const SCRIPT_DIR = __dirname;
const PROJECT_ROOT = path.resolve(SCRIPT_DIR, '..', '..');
const MEMORIA_DIR = path.join(PROJECT_ROOT, 'memoria');
const MEMORY_MODULE = path.join(PROJECT_ROOT, 'aios-core', '.aios-core', 'core', 'memory');

// Regras criticas hardcoded (safety net — nunca depender so do banco)
const CRITICAL_RULES = `
### Regras Criticas (NUNCA VIOLAR)
- **Portas VPS:** 3000(CRMax), 3100(Makewl dev), 3101(Diagnostico), 3102(Arquetipos), 3103(Legacy), 3104(Disrupty), 3105(NPS), 3106(Financa), 4001(Monitor), 5432(PG), 6379(Redis). Dev: 3100-3199.
- **Heredocs:** NUNCA usar cat/tee <<EOF via Bash tool. SEMPRE usar Write tool.
- **next dev:** NAO hidrata JS via IP externo. SEMPRE next build + next start para acesso remoto.
- **Tailwind:** Classes CSS nao refletem mudancas no Next.js 16 + Turbopack. Usar inline style={{}} para spacing/sizing.
- **SEMPRE verificar portas ocupadas ANTES de subir servidor** (ss -tlnp)
`;

async function injectFromPgvector() {
  const { query, healthCheck, close } = require(path.join(MEMORY_MODULE, 'db'));

  const health = await healthCheck();
  if (!health.connected) throw new Error('DB not connected');

  const output = [];
  output.push('---');
  output.push('## [MEMORIA REINJETADA apos compactacao]');
  output.push('');

  // Last session info (essencial apos compact)
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

  // Critical gotchas only (importance='critical')
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

  // Regras criticas hardcoded
  output.push(CRITICAL_RULES);

  // Como funciona a memoria contextual
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
  output.push('[Use `/atualizar-memoria` ao final da sessao.]');

  await close();
  return output.join('\n');
}

function injectFromFiles() {
  const output = [];
  output.push('---');
  output.push('## [MEMORIA REINJETADA via Markdown (fallback — pgvector indisponivel)]');
  output.push('');

  // Regras criticas primeiro (safety net)
  output.push(CRITICAL_RULES);

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

  // Lista arquivos disponiveis (nao conteudo)
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
  output.push('[Memoria via Markdown fallback. Use `/atualizar-memoria` ao final da sessao.]');

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
