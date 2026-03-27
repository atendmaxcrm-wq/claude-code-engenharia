'use strict';

/**
 * Interactive wizard for installation configuration
 * Uses native readline (zero dependencies)
 */

const readline = require('readline');
const path = require('path');

function createRL() {
  return readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
}

function ask(rl, question, defaultValue) {
  return new Promise((resolve) => {
    const suffix = defaultValue ? ` [${defaultValue}]` : '';
    rl.question(`  ${question}${suffix}: `, (answer) => {
      resolve(answer.trim() || defaultValue || '');
    });
  });
}

function askChoice(rl, question, options, defaultIdx = 0) {
  return new Promise((resolve) => {
    console.log(`  ${question}`);
    options.forEach((opt, i) => {
      const marker = i === defaultIdx ? '>' : ' ';
      console.log(`  ${marker} ${i + 1}. ${opt.label} — ${opt.description}`);
    });
    rl.question(`  Escolha [${defaultIdx + 1}]: `, (answer) => {
      const idx = parseInt(answer, 10) - 1;
      if (idx >= 0 && idx < options.length) {
        resolve(options[idx].value);
      } else {
        resolve(options[defaultIdx].value);
      }
    });
  });
}

/**
 * Run the interactive wizard
 * @param {object} opts - CLI options
 * @returns {Promise<object>} Configuration object
 */
async function runWizard(opts) {
  const config = {
    targetDir: opts.targetDir,
    projectName: path.basename(opts.targetDir),
    projectDescription: '',
    module: opts.module || null,
    stackDescription: '',
    healthCheckCommand: '',
    logCommand: '',
    // DB config (full module only)
    dbHost: 'localhost',
    dbPort: '5432',
    dbUser: 'postgres',
    dbPassword: '',
    dbName: 'claude_memory',
    openaiKey: '',
  };

  // If --quiet or all options provided, skip wizard
  if (opts.quiet && opts.module) {
    config.module = opts.module;
    return config;
  }

  const rl = createRL();

  try {
    // Project info
    config.projectName = await ask(rl, 'Nome do projeto', config.projectName);
    config.projectDescription = await ask(rl, 'Descricao breve', 'Projeto de software');

    // Module selection
    if (!config.module) {
      console.log('');
      config.module = await askChoice(rl, 'Qual modulo instalar?', [
        {
          label: 'core',
          description: 'Hooks + Rules + Commands + Agents + Memoria markdown',
          value: 'core',
        },
        {
          label: 'standard',
          description: 'Core + 19 Skills + CLAUDE.md template',
          value: 'standard',
        },
        {
          label: 'full (Recomendado)',
          description: 'Standard + pgvector + MCP Server + busca semantica',
          value: 'full',
        },
      ], 2);
    }

    // Stack info (for CLAUDE.md)
    console.log('');
    config.stackDescription = await ask(rl, 'Stack principal (ex: Next.js + PostgreSQL)', '');
    config.healthCheckCommand = await ask(rl, 'Comando de health check', 'curl http://localhost:3000/health');
    config.logCommand = await ask(rl, 'Comando de logs', 'pm2 logs --lines 20');

    // Database config (full module only)
    if (config.module === 'full') {
      console.log('\n  Configuracao PostgreSQL:');
      config.dbHost = await ask(rl, 'DB Host', 'localhost');
      config.dbPort = await ask(rl, 'DB Port', '5432');
      config.dbUser = await ask(rl, 'DB User', 'postgres');
      config.dbPassword = await ask(rl, 'DB Password', '');
      config.dbName = await ask(rl, 'DB Name (sera criado)', 'claude_memory');
      console.log('');
      config.openaiKey = await ask(rl, 'OpenAI API Key (para embeddings)', '');
    }
  } finally {
    rl.close();
  }

  return config;
}

module.exports = { runWizard };
