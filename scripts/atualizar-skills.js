#!/usr/bin/env node
'use strict';
// Atualiza SO as skills de uma instalacao do CCE que ja existe, sem tocar em CLAUDE.md, memoria/, settings, rules, hooks.
// (o install.js sem --force pula o que existe e nao atualiza skill nenhuma; com --force sobrescreve CLAUDE.md e memoria/.)
// Uso, de dentro do clone do repo:
//   node scripts/atualizar-skills.js --dir /root            # previa: lista o que seria criado/atualizado
//   node scripts/atualizar-skills.js --dir /root --apply    # copia (faz backup .tar.gz das skills antes)
// Skills que so existem na maquina (nao estao no repo) ficam intactas.
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { buildManifest } = require('../lib/templates.js');

const args = process.argv.slice(2);
const dirIdx = args.indexOf('--dir');
const raiz = path.resolve(dirIdx >= 0 ? args[dirIdx + 1] : process.cwd());
const aplicar = args.includes('--apply');
const repo = path.resolve(__dirname, '..');

const arquivos = buildManifest({ module: 'full' }, repo).filter((f) => f.relativePath.startsWith('.claude/skills/'));
const novos = [], mudados = [];
for (const f of arquivos) {
  const dest = path.join(raiz, f.dest);
  if (!fs.existsSync(dest)) novos.push(f);
  else if (!fs.readFileSync(dest).equals(fs.readFileSync(f.src))) mudados.push(f);
}
const porSkill = (l) => [...new Set(l.map((f) => f.relativePath.split('/')[2]))];
console.log(`raiz: ${raiz}`);
console.log(`skills no repo: ${porSkill(arquivos).length} | arquivos novos: ${novos.length} | arquivos diferentes: ${mudados.length}`);
console.log(`skills com novidade: ${porSkill([...novos, ...mudados]).join(', ') || '(nenhuma)'}`);
if (!aplicar) { console.log('\nPrevia. Rode de novo com --apply para copiar.'); process.exit(0); }

const skillsDir = path.join(raiz, '.claude', 'skills');
if (fs.existsSync(skillsDir)) {
  const bkDir = path.join(raiz, '.claude', 'backups');
  fs.mkdirSync(bkDir, { recursive: true });
  const bk = path.join(bkDir, `skills-pre-${new Date().toISOString().replace(/[:.]/g, '-')}.tar.gz`);
  execFileSync('tar', ['-czf', bk, '-C', path.join(raiz, '.claude'), 'skills']);
  console.log(`backup: ${bk}`);
}
for (const f of [...novos, ...mudados]) {
  const dest = path.join(raiz, f.dest);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(f.src, dest);
  fs.chmodSync(dest, fs.statSync(f.src).mode);
}
console.log(`copiados ${novos.length + mudados.length} arquivo(s). Reinicie o Claude Code para carregar.`);
console.log('Skills de terceiros (Felipe Borges, impeccable): bash terceiros/instalar.sh ' + path.join(raiz, '.claude', 'skills'));
