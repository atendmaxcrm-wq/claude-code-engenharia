'use strict';
// Importa as auto-memorias do Claude Code (~/.claude/projects/<projeto>/memory/*.md, 1 fato por arquivo) para o pgvector.
// O sync_from_markdown do MCP NAO le essa pasta; sem este passo o que o Claude salva sozinho nao aparece na busca contextual.
// Idempotente: upsertByTitle casa por (title, source_file) e atualiza o que mudou. Rode na RAIZ onde o CCE foi instalado:
//   node memory/scripts/importar-auto-memoria.js [pasta-das-auto-memorias]
// Pasta padrao: ~/.claude/projects/<caminho da raiz com / trocado por ->/memory (o mesmo nome que o Claude Code usa).
// Banco + chave de embedding: variaveis de ambiente, ou o env do servidor claude-code-memory no .mcp.json da raiz.
const fs = require('fs');
const os = require('os');
const path = require('path');

const RAIZ = process.env.CCE_ROOT || process.cwd();
try {
  const mcp = JSON.parse(fs.readFileSync(path.join(RAIZ, '.mcp.json'), 'utf8')).mcpServers['claude-code-memory'];
  for (const [k, v] of Object.entries((mcp && mcp.env) || {})) if (!process.env[k]) process.env[k] = v;
} catch { /* sem .mcp.json: usa so o ambiente */ }

const { upsertByTitle } = require('../memory-store');
const DIR = process.argv[2] || path.join(os.homedir(), '.claude', 'projects', path.resolve(RAIZ).replace(/[^A-Za-z0-9]/g, '-'), 'memory');
if (!fs.existsSync(DIR)) { console.log(JSON.stringify({ aviso: `pasta de auto-memorias nao existe: ${DIR}` })); process.exit(0); }
// tipo do frontmatter -> tipo do pgvector
const TIPO = { feedback: 'decision', user: 'knowledge', project: 'progress', reference: 'knowledge' };

function ler(arquivo) {
  const txt = fs.readFileSync(arquivo, 'utf8');
  const m = txt.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  const fm = {}, corpo = m ? m[2].trim() : txt.trim();
  if (m) {
    for (const l of m[1].split('\n')) {
      const x = l.match(/^\s*(name|description|type):\s*(.*)$/);
      if (x && !fm[x[1]]) fm[x[1]] = x[2].replace(/^["']|["']$/g, '').trim();
    }
  }
  return { fm, corpo };
}

(async () => {
  const arquivos = fs.readdirSync(DIR).filter((f) => f.endsWith('.md') && f !== 'MEMORY.md').sort();
  const r = { novos: 0, atualizados: 0, erros: [] };
  for (const f of arquivos) {
    const p = path.join(DIR, f);
    const { fm, corpo } = ler(p);
    if (!corpo) continue;
    const nome = fm.name || f.replace(/\.md$/, '');
    const tipo = /^gotcha/.test(nome) ? 'gotcha' : TIPO[fm.type] || 'knowledge';
    try {
      const x = await upsertByTitle({
        memory_type: tipo,
        title: `${nome}: ${(fm.description || '').slice(0, 160)}`.trim(),
        content: `${fm.description ? fm.description + '\n\n' : ''}${corpo}`,
        source: 'auto-memoria',
        source_file: p,
        agent_id: 'global',
        importance: tipo === 'gotcha' || tipo === 'decision' ? 'high' : 'normal',
        tags: ['auto-memoria', fm.type || 'sem-tipo', nome],
      });
      x.is_new ? r.novos++ : r.atualizados++;
    } catch (e) {
      r.erros.push(`${f}: ${e.message}`);
    }
  }
  console.log(JSON.stringify({ arquivos: arquivos.length, ...r }, null, 1));
  process.exit(0);
})();
