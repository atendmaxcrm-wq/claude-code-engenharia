// Grava SO as chamadas de API (xhr/fetch) de um contexto do Playwright em ndjson, uma linha por
// chamada, direto em disco. Existe porque o recordHar do Playwright guarda a sessao inteira na
// memoria ate o ctx.close(): numa captura longa chegou a 4,6 GB e o processo morreu por OOM.
// Depois: python3 ndjson2har.py api.ndjson api.har  ->  npx rea inspect-web-network-capture api.har har
//
// Uso:
//   import { gravarApi } from './.claude/skills/rea/scripts/gravador-api.mjs';
//   gravarApi(ctx, { arquivo: 'har/api.ndjson', hostRe: /api\.exemplo\.com/ });
import fs from 'node:fs';
import path from 'node:path';

// Rotas que NUNCA vao para o disco: o corpo de login carrega senha, codigo de 2FA ou token.
const IGNORAR_PADRAO = /\/(auth|login|signin|sign-in|verify|two-factor|otp|token|session)s?(\/|\?|$)/i;
// Cabecalhos que carregam credencial.
const SEM = /^(authorization|cookie|set-cookie|x-xsrf-token|x-csrf-token|x-api-key)$/i;

export function gravarApi(ctx, { arquivo, hostRe = /./, ignorarRe = IGNORAR_PADRAO, maxCorpo = 300000 } = {}) {
  if (!arquivo) throw new Error('gravarApi: informe { arquivo }');
  fs.mkdirSync(path.dirname(path.resolve(arquivo)), { recursive: true });
  const hdr = h => Object.fromEntries(Object.entries(h || {}).filter(([k]) => !SEM.test(k)));
  ctx.on('requestfinished', async req => {
    try {
      if (!['xhr', 'fetch'].includes(req.resourceType()) || !hostRe.test(req.url())) return;
      if (ignorarRe.test(req.url())) return;
      const res = await req.response(); let body = null;
      try { const t = await res.text(); body = t.length > maxCorpo ? t.slice(0, maxCorpo) : t; } catch {}
      fs.appendFileSync(arquivo, JSON.stringify({
        t: new Date().toISOString(), method: req.method(), url: req.url(),
        reqHeaders: hdr(req.headers()), postData: req.postData(), status: res.status(),
        resHeaders: hdr(res.headers()), body,
      }) + '\n');
    } catch {}
  });
}
