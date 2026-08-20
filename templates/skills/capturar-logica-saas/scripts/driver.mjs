// Driver do browser VIVO: le comandos de um arquivo (1 por linha) e os executa no
// servidor (run.mjs em modo comando), coletando cada resultado.
// Uso: CAP_ROOT=/root/<slug>-blueprint node driver.mjs <arquivo-de-comandos>
// Linhas iniciadas por # sao comentario. Verbos: click|snap|menu|tab|goto|goback|home|
// dismiss|sel|selnth|type|dump|quit  (ver run.mjs).
//
// GOTCHA: em foreground o Bash mata o processo em ~2min. Para lotes longos, rodar com
// run_in_background=true OU quebrar em lotes de 5-8 comandos.
import fs from 'node:fs';
const ROOT = process.env.CAP_ROOT || process.cwd();
const OUT = ROOT + '/_recon';
const CMD = OUT + '/_cmd.txt', RES = OUT + '/_cmd-result.json';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const file = process.argv[2];
if (!file) { console.log('uso: node driver.mjs <arquivo-de-comandos>'); process.exit(1); }
const lines = fs.readFileSync(file, 'utf8').split('\n').map(s => s.trim()).filter(l => l && !l.startsWith('#'));
if (!fs.existsSync(OUT + '/_alive.flag')) console.log('AVISO: _alive.flag ausente (o run.mjs pode nao estar vivo ainda)');
for (const c of lines) {
  try { fs.unlinkSync(RES); } catch {}
  fs.writeFileSync(CMD, c);
  let res = null;
  for (let i = 0; i < 60; i++) { await sleep(1000); if (fs.existsSync(RES)) { res = fs.readFileSync(RES, 'utf8'); break; } }
  console.log('>>> ' + c);
  console.log(res ? res.replace(/\s+/g, ' ').slice(0, 400) : '(timeout: sem resposta em 60s)');
  await sleep(600);
}
console.log('--- driver fim ---');
