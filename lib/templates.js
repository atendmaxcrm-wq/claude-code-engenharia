'use strict';

/**
 * Template engine and file copier
 *
 * Handles {{variable}} replacement in .tmpl files
 * and direct copy for non-template files.
 */

const fs = require('fs');
const path = require('path');

/**
 * Replace {{variable}} patterns in text
 * @param {string} text - Template text
 * @param {object} vars - Variables to replace
 * @returns {string}
 */
function renderTemplate(text, vars) {
  return text.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    return vars[key] !== undefined ? vars[key] : match;
  });
}

/**
 * Build the file manifest based on config
 * @param {object} config - Installation config
 * @param {string} packageRoot - Root of the npm package
 * @returns {object[]} Array of {src, dest, relativePath, isTemplate}
 */
function buildManifest(config, packageRoot) {
  const templatesDir = path.join(packageRoot, 'templates');
  const memoryDir = path.join(packageRoot, 'memory');
  const files = [];

  // === CORE MODULE ===

  // Hooks
  const hooks = ['block-destructive.sh', 'reinject-memory.js', 'safari-guard.js'];
  if (config.module === 'full') {
    hooks.push('contextual-memory.js');
  }
  for (const hook of hooks) {
    files.push({
      src: path.join(templatesDir, 'hooks', hook),
      dest: path.join('.claude', 'hooks', hook),
      relativePath: `.claude/hooks/${hook}`,
    });
  }

  // Rules
  const rules = ['workflow-engineering.md', 'api-backend.md', 'component-architecture.md', 'frontend-react.md', 'services-types.md'];
  for (const rule of rules) {
    files.push({
      src: path.join(templatesDir, 'rules', rule),
      dest: path.join('.claude', 'rules', rule),
      relativePath: `.claude/rules/${rule}`,
    });
  }

  // Commands
  const commands = [
    'atualizar-memoria.md', 'resumo-sessao.md', 'nova-feature.md',
    'investigar-bug.md', 'pesquisar-tech.md', 'migrar-componente.md',
    'deploy.md',
  ];
  for (const cmd of commands) {
    files.push({
      src: path.join(templatesDir, 'commands', cmd),
      dest: path.join('.claude', 'commands', cmd),
      relativePath: `.claude/commands/${cmd}`,
    });
  }

  // Agents
  const agents = ['dev.md', 'reviewer.md', 'investigador.md', 'arquiteto.md'];
  for (const agent of agents) {
    files.push({
      src: path.join(templatesDir, 'agents', agent),
      dest: path.join('.claude', 'agents', agent),
      relativePath: `.claude/agents/${agent}`,
    });
  }

  // Memoria templates
  const memoriaFiles = [
    'COMO_USAR_ESTE_SISTEMA.md', 'insights.md', 'progresso.md',
  ];
  for (const f of memoriaFiles) {
    files.push({
      src: path.join(templatesDir, 'memoria', f),
      dest: path.join('memoria', f),
      relativePath: `memoria/${f}`,
    });
  }

  const sistemaFiles = [
    'database-schema.md', 'api-endpoints.md', 'permissoes.md',
    'troubleshooting.md', 'changelog.md', 'critical-rules.md',
  ];
  for (const f of sistemaFiles) {
    files.push({
      src: path.join(templatesDir, 'memoria', 'sistema', f),
      dest: path.join('memoria', 'sistema', f),
      relativePath: `memoria/sistema/${f}`,
    });
  }

  // Settings.json (template - full gets contextual-memory hook, core/standard don't)
  const settingsTmpl = config.module === 'full' ? 'settings-json.tmpl' : 'settings-json-core.tmpl';
  files.push({
    src: path.join(templatesDir, settingsTmpl),
    dest: path.join('.claude', 'settings.json'),
    relativePath: '.claude/settings.json',
    isTemplate: true,
  });

  // === STANDARD MODULE (adds skills + CLAUDE.md) ===
  if (config.module === 'standard' || config.module === 'full') {
    // CLAUDE.md template
    files.push({
      src: path.join(templatesDir, 'claude-md.tmpl'),
      dest: 'CLAUDE.md',
      relativePath: 'CLAUDE.md',
      isTemplate: true,
    });

    // Skills
    const skillCategories = {
      core: [
        'systematic-debugging', 'code-review', 'commit',
        'verification-before-completion', 'performance-audit',
      ],
      frontend: [
        'react-best-practices', 'frontend-design', 'modern-ui-design',
        'component-builder', 'interaction-patterns', 'design-system',
        'safari-check',
      ],
      backend: [
        'api-patterns', 'database-query', 'postgres-best-practices',
        'test-driven-development',
      ],
      workflow: [
        'planejar-feature', 'analise-impacto', 'create-pr',
        'ai-agent-prompt-builder',
      ],
    };

    for (const [category, skills] of Object.entries(skillCategories)) {
      for (const skill of skills) {
        const skillSrc = path.join(templatesDir, 'skills', category, skill);
        if (fs.existsSync(skillSrc)) {
          // Copy entire skill directory
          const skillFiles = walkDir(skillSrc);
          for (const sf of skillFiles) {
            const relInSkill = path.relative(skillSrc, sf);
            files.push({
              src: sf,
              dest: path.join('.claude', 'skills', skill, relInSkill),
              relativePath: `.claude/skills/${skill}/${relInSkill}`,
            });
          }
        }
      }
    }
  }

  // === FULL MODULE (adds memory system + MCP config) ===
  if (config.module === 'full') {
    // Memory system files
    const memoryFiles = [
      'package.json', 'db.js', 'embeddings.js', 'search.js',
      'memory-store.js', 'session-store.js', 'query-logger.js',
      'markdown-importer.js',
    ];
    for (const f of memoryFiles) {
      files.push({
        src: path.join(memoryDir, f),
        dest: path.join('memory', f),
        relativePath: `memory/${f}`,
      });
    }

    // Migrations
    const migrationsDir = path.join(memoryDir, 'migrations');
    if (fs.existsSync(migrationsDir)) {
      const migrationFiles = fs.readdirSync(migrationsDir).filter(f => f.endsWith('.sql'));
      for (const f of migrationFiles) {
        files.push({
          src: path.join(migrationsDir, f),
          dest: path.join('memory', 'migrations', f),
          relativePath: `memory/migrations/${f}`,
        });
      }
    }

    // Setup script
    const setupScript = path.join(memoryDir, 'scripts', 'setup-memory-db.js');
    if (fs.existsSync(setupScript)) {
      files.push({
        src: setupScript,
        dest: path.join('memory', 'scripts', 'setup-memory-db.js'),
        relativePath: 'memory/scripts/setup-memory-db.js',
      });
    }

    // MCP Server
    const mcpDir = path.join(memoryDir, 'mcp-memory');
    if (fs.existsSync(mcpDir)) {
      const mcpFiles = walkDir(mcpDir).filter(f => !f.includes('node_modules'));
      for (const f of mcpFiles) {
        const rel = path.relative(mcpDir, f);
        files.push({
          src: f,
          dest: path.join('memory', 'mcp-memory', rel),
          relativePath: `memory/mcp-memory/${rel}`,
        });
      }
    }

    // .mcp.json template
    files.push({
      src: path.join(templatesDir, 'mcp-json.tmpl'),
      dest: '.mcp.json',
      relativePath: '.mcp.json',
      isTemplate: true,
    });
  }

  return files;
}

/**
 * Walk directory recursively, return all file paths
 * @param {string} dir
 * @returns {string[]}
 */
function walkDir(dir) {
  const results = [];
  if (!fs.existsSync(dir)) return results;

  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === 'node_modules' || entry.name === '.git') continue;
      results.push(...walkDir(fullPath));
    } else {
      results.push(fullPath);
    }
  }
  return results;
}

/**
 * Render and copy templates to target directory
 * @param {object} config - Installation config
 * @param {string} packageRoot - Root of the npm package
 * @param {object} options - {dryRun, skipExisting, force}
 * @returns {object} Result stats or file list
 */
function renderTemplates(config, packageRoot, options = {}) {
  const manifest = buildManifest(config, packageRoot);

  // Template variables
  const vars = {
    project_name: config.projectName,
    project_description: config.projectDescription || 'Projeto de software',
    stack_description: config.stackDescription || '(Preencha com sua stack)',
    health_check_command: config.healthCheckCommand || 'curl http://localhost:3000/health',
    log_command: config.logCommand || 'pm2 logs --lines 20',
    memory_mcp_path: path.join(config.targetDir, 'memory', 'mcp-memory', 'src', 'index.js'),
    db_host: config.dbHost || 'localhost',
    db_port: config.dbPort || '5432',
    db_user: config.dbUser || 'postgres',
    db_password: config.dbPassword || '',
    db_name: config.dbName || 'claude_memory',
    openai_api_key: config.openaiKey || '',
  };

  if (options.dryRun) {
    return manifest.map(f => ({ relativePath: f.relativePath }));
  }

  const stats = { created: 0, skipped: 0, updated: 0 };
  const skipSet = new Set(options.skipExisting || []);

  for (const file of manifest) {
    const destPath = path.join(config.targetDir, file.dest);

    // Skip existing files unless --force
    if (!options.force && skipSet.has(file.relativePath)) {
      stats.skipped++;
      continue;
    }

    // Ensure directory exists
    const dir = path.dirname(destPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    // Read source
    if (!fs.existsSync(file.src)) {
      continue; // Skip if source doesn't exist (optional files)
    }

    let content = fs.readFileSync(file.src, 'utf-8');

    // Apply template rendering
    if (file.isTemplate || file.src.endsWith('.tmpl')) {
      content = renderTemplate(content, vars);
    }

    // Check if file already exists
    const existed = fs.existsSync(destPath);

    // Write file
    fs.writeFileSync(destPath, content);

    // Make shell scripts executable
    if (destPath.endsWith('.sh')) {
      fs.chmodSync(destPath, '755');
    }

    if (existed) {
      stats.updated++;
    } else {
      stats.created++;
    }
  }

  return stats;
}

module.exports = { renderTemplates, renderTemplate, buildManifest };
