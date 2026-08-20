// Sanitiza o manifest antes de empacotar: remove os campos que costumam carregar PII.
// navLinks e listItems capturam a sidebar (lista de chat/clientes com nomes reais) e a
// barra lateral de toda tela -> DROPADOS. Gera manifest-sanitizado.json ao lado.
//
// Uso: CAP_ROOT=/root/<slug>-blueprint node sanitizar-manifest.mjs
// Depois: conferir MANUALMENTE os screenshots de modal (modal sobre lista vaza os nomes
// atras) e excluir os que mostram dado real. Ver references/pii-sanitizacao.md.
import fs from 'node:fs';
const ROOT = process.env.CAP_ROOT || process.cwd();
const OUT = ROOT + '/_recon';
const SRC = OUT + '/manifest.json';
const DST = OUT + '/manifest-sanitizado.json';
if (!fs.existsSync(SRC)) { console.log('nao achei', SRC); process.exit(1); }
const manifest = JSON.parse(fs.readFileSync(SRC, 'utf8'));
// campos removidos de cada tela (fonte de nomes/PII)
const DROP = (process.env.CAP_PII_DROP || 'navLinks,listItems').split(',').map(s => s.trim()).filter(Boolean);
let dropped = 0;
for (const tela of manifest) {
  if (!tela.structure) continue;
  for (const k of DROP) { if (k in tela.structure) { delete tela.structure[k]; dropped++; } }
}
fs.writeFileSync(DST, JSON.stringify(manifest, null, 2));
console.log(`sanitizado: ${manifest.length} telas, campos removidos: ${DROP.join(', ')} (${dropped} ocorrencias)`);
console.log('gravado em', DST);
console.log('\nATENCAO manual: revise screens/modulos/ e exclua shots com dado real (modais sobre lista,');
console.log('prontuario, perfil do dono com CPF). O empacotar.sh usa o manifest-sanitizado.json.');
