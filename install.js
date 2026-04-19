#!/usr/bin/env node
'use strict';

/**
 * Claude Code Engenharia - Installer
 *
 * Instala o sistema de engenharia profissional para Claude Code.
 * Modular: core (sem DB), standard (+ skills), full (+ pgvector + MCP).
 *
 * Usage:
 *   npx claude-code-engenharia
 *   npx claude-code-engenharia --dry-run
 *   npx claude-code-engenharia --module core
 *   npx claude-code-engenharia --quiet
 *   npx claude-code-engenharia --yes --module full     # non-interactive, use defaults
 */

const path = require('path');
const { preFlightChecks } = require('./lib/validators');
const { runWizard } = require('./lib/wizard');
const { renderTemplates } = require('./lib/templates');
const { handleBrownfield } = require('./lib/brownfield');
const { setupDatabase } = require('./lib/db-setup');

const PACKAGE_ROOT = __dirname;
const VERSION = require('./package.json').version;

// Parse CLI args
function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    dryRun: args.includes('--dry-run'),
    quiet: args.includes('--quiet'),
    force: args.includes('--force'),
    yes: args.includes('--yes') || args.includes('-y'),
    module: null,
    targetDir: process.cwd(),
  };

  const moduleIdx = args.indexOf('--module');
  if (moduleIdx !== -1 && args[moduleIdx + 1]) {
    opts.module = args[moduleIdx + 1];
  }

  const dirIdx = args.indexOf('--dir');
  if (dirIdx !== -1 && args[dirIdx + 1]) {
    opts.targetDir = path.resolve(args[dirIdx + 1]);
  }

  return opts;
}

async function main() {
  const opts = parseArgs();

  console.log('');
  console.log('  ╔══════════════════════════════════════════╗');
  console.log(`  ║  Claude Code Engenharia v${VERSION.padEnd(16)}║`);
  console.log('  ║  Sistema de engenharia profissional      ║');
  console.log('  ╚══════════════════════════════════════════╝');
  console.log('');

  // Step 1: Pre-flight checks
  console.log('[1/7] Pre-flight checks...');
  const checks = await preFlightChecks();
  if (!checks.ok) {
    console.error(`\n  ERRO: ${checks.error}`);
    console.error('  Corrija o problema acima e tente novamente.\n');
    process.exit(1);
  }
  console.log(`  Node ${checks.nodeVersion} OK | jq ${checks.jqAvailable ? 'OK' : 'MISSING (optional)'}`);

  // Step 2: Configuration wizard
  console.log('\n[2/7] Configuracao...');
  const config = await runWizard(opts);
  console.log(`  Projeto: ${config.projectName}`);
  console.log(`  Modulo: ${config.module}`);

  // Step 3: Brownfield detection
  console.log('\n[3/7] Detectando instalacao existente...');
  const brownfield = await handleBrownfield(config.targetDir, opts);
  if (brownfield.hasExisting) {
    console.log(`  .claude/ existente detectado (${brownfield.existingFiles.length} arquivos)`);
    console.log('  Modo: merge (preservar existentes, adicionar novos)');
  } else {
    console.log('  Instalacao limpa (greenfield)');
  }

  // Step 4: Dry-run output
  if (opts.dryRun) {
    console.log('\n[DRY RUN] Arquivos que seriam criados:\n');
    const files = renderTemplates(config, PACKAGE_ROOT, { dryRun: true });
    for (const f of files) {
      const status = brownfield.existingFiles.includes(f.relativePath) ? '[SKIP]' : '[NEW] ';
      console.log(`  ${status} ${f.relativePath}`);
    }
    console.log(`\n  Total: ${files.length} arquivos (${files.filter(f => !brownfield.existingFiles.includes(f.relativePath)).length} novos)`);
    console.log('  Nenhum arquivo foi criado (--dry-run).\n');
    process.exit(0);
  }

  // Step 5: Install files
  console.log('\n[4/7] Instalando arquivos...');
  const installed = renderTemplates(config, PACKAGE_ROOT, {
    dryRun: false,
    skipExisting: brownfield.existingFiles,
    force: opts.force,
  });
  console.log(`  ${installed.created} criados | ${installed.skipped} preservados | ${installed.updated} atualizados`);

  // Step 5-6: Dependencies + Database (full module only)
  if (config.module === 'full') {
    console.log('\n[5/7] Instalando dependencias do MCP...');
    const { execSync } = require('child_process');
    try {
      execSync('npm install', {
        cwd: path.join(config.targetDir, 'memory'),
        stdio: opts.quiet ? 'ignore' : 'inherit',
      });
      execSync('npm install', {
        cwd: path.join(config.targetDir, 'memory', 'mcp-memory'),
        stdio: opts.quiet ? 'ignore' : 'inherit',
      });
      console.log('  Dependencias instaladas.');
    } catch (err) {
      console.error(`  AVISO: npm install falhou: ${err.message}`);
      console.error('  Execute manualmente: cd memory && npm install && cd mcp-memory && npm install');
    }

    console.log('\n[6/7] Configurando banco de dados...');
    const dbResult = await setupDatabase(config);
    if (dbResult.ok) {
      console.log(`  Database: ${dbResult.dbName} OK`);
      console.log(`  pgvector: ${dbResult.pgvectorVersion}`);
      console.log(`  Tables: ${dbResult.tables.join(', ')}`);
    } else {
      console.error(`  AVISO: Setup do banco falhou: ${dbResult.error}`);
      console.error('  Voce pode configurar manualmente depois: cd memory && npm run setup');
    }
  } else {
    console.log('\n[5/7] Banco de dados (pulado - modulo nao requer)');
    console.log('[6/7] Dependencias MCP (pulado - modulo nao requer)');
  }

  // Step 7: Post-install validation
  console.log('\n[7/7] Validacao pos-instalacao...');
  const validation = validateInstallation(config);
  for (const check of validation) {
    const icon = check.ok ? 'OK' : 'FALHOU';
    console.log(`  [${icon}] ${check.name}`);
  }

  // Summary
  console.log('\n  ════════════════════════════════════════');
  console.log('  Instalacao concluida!');
  console.log('  ════════════════════════════════════════');
  console.log('');
  console.log('  Proximos passos:');
  console.log('  1. Revise o CLAUDE.md gerado e personalize');
  console.log('  2. Popule memoria/sistema/*.md com info do seu projeto');
  if (config.module === 'full') {
    console.log('  3. Verifique .mcp.json com suas credenciais');
    console.log('  4. Reinicie o Claude Code para carregar hooks');
  } else {
    console.log('  3. Reinicie o Claude Code para carregar hooks');
  }
  console.log('');
  console.log('  Ao final de cada sessao, use: /atualizar-memoria');
  console.log('');
}

function validateInstallation(config) {
  const fs = require('fs');
  const checks = [];
  const target = config.targetDir;

  // Check hooks
  checks.push({
    name: 'block-destructive.sh existe',
    ok: fs.existsSync(path.join(target, '.claude', 'hooks', 'block-destructive.sh')),
  });

  // Check settings
  checks.push({
    name: 'settings.json configurado',
    ok: fs.existsSync(path.join(target, '.claude', 'settings.json')),
  });

  // Check memoria
  checks.push({
    name: 'memoria/ criada',
    ok: fs.existsSync(path.join(target, 'memoria', 'insights.md')),
  });

  // Check rules
  checks.push({
    name: 'rules/ configuradas',
    ok: fs.existsSync(path.join(target, '.claude', 'rules', 'workflow-engineering.md')),
  });

  if (config.module === 'full') {
    checks.push({
      name: '.mcp.json configurado',
      ok: fs.existsSync(path.join(target, '.mcp.json')),
    });
    checks.push({
      name: 'memory/ instalado',
      ok: fs.existsSync(path.join(target, 'memory', 'db.js')),
    });
  }

  return checks;
}

main().catch((err) => {
  console.error(`\nErro fatal: ${err.message}`);
  process.exit(1);
});
