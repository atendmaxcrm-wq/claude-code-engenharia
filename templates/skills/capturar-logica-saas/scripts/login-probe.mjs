// RECON DE AUTENTICACAO (Fase 1). Abre SO a tela de login e reporta o que precisa pra
// configurar o run.mjs: tipo de login, seletores de usuario/senha/submit, e indicios de 2FA.
// Nao faz login (nao precisa de credenciais nem de resolver 2FA aqui).
//
// A pergunta "a sessao sobrevive a reload?" e respondida DEPOIS, ja no run.mjs: apos logar,
// mande `goto:<home>` pelo driver e veja o campo loggedIn do _cmd-result.json (true = sobrevive;
// caiu no login = nao sobrevive -> navegar so por clique, CAP_SESSION_SURVIVES_RELOAD=0).
//
// Uso: CAP_LOGIN_URL='https://.../login' node login-probe.mjs
import fs from 'node:fs';
const PW = process.env.CAP_PW || '/root/my-zap/node_modules/playwright-core/index.js';
const _pw = await import(PW);
const chromium = _pw.chromium ?? _pw.default?.chromium ?? _pw.default;
const LOGIN_URL = process.env.CAP_LOGIN_URL || '';
const UA = process.env.CAP_UA || 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36';
function resolveChrome() {
  if (process.env.CAP_CHROME) return process.env.CAP_CHROME;
  const base = (process.env.HOME || '/root') + '/.cache/ms-playwright';
  try { for (const d of fs.readdirSync(base).filter(x => x.startsWith('chromium-')).sort().reverse()) { const p = base + '/' + d + '/chrome-linux64/chrome'; if (fs.existsSync(p)) return p; } } catch {}
  return null;
}
if (!LOGIN_URL) { console.log('faltou CAP_LOGIN_URL'); process.exit(1); }

(async () => {
  const browser = await chromium.launch({ executablePath: resolveChrome() || undefined, headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  try {
    const page = await (await browser.newContext({ userAgent: UA, locale: 'pt-BR', viewport: { width: 1440, height: 900 } })).newPage();
    await page.goto(LOGIN_URL, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
    await page.waitForTimeout(3500);
    const info = await page.evaluate(() => {
      const q = s => [...document.querySelectorAll(s)];
      const desc = el => ({ tag: el.tagName.toLowerCase(), type: el.type || null, id: el.id || null, name: el.name || null, placeholder: el.placeholder || null, autocomplete: el.getAttribute('autocomplete') || null });
      const host = location.host, path = location.pathname;
      const isB2C = /b2clogin|microsoftonline/.test(host) || !!document.querySelector('#signInName');
      const userFields = q('input[type=email],input[name*=user i],input[id*=user i],#signInName,input[autocomplete=username],input[name*=email i]').map(desc);
      const passFields = q('input[type=password]').map(desc);
      const submits = q('button[type=submit],#next,#continue,button').map(b => (b.innerText || b.value || b.id || '').trim().slice(0, 40)).filter(Boolean).slice(0, 12);
      // indicios de 2FA/OTP visiveis nesta tela (raro no 1o passo, mas as vezes aparece)
      const otp = q('input[maxlength="1"],input[autocomplete=one-time-code],input[inputmode=numeric],#challenge-EMAIL,[id*=otp i],[id*=code i]').length;
      const methodHints = q('*').map(e => (e.innerText || '').trim()).filter(t => /(e-?mail|sms|autenticador|authenticator|token|verifica)/i.test(t) && t.length < 60).slice(0, 8);
      return { host, path, isB2C, userFields, passFields, submits, otpFieldsOnScreen: otp, methodHints: [...new Set(methodHints)] };
    });
    console.log(JSON.stringify(info, null, 2));
    console.log('\n--- leitura ---');
    console.log('tipo de login       :', info.isB2C ? 'Azure AD B2C (#signInName/#password/#next)' : 'formulario proprio');
    console.log('campo usuario acha? :', info.userFields.length ? 'sim' : 'NAO (ajustar CAP_USER_SEL)');
    console.log('campo senha acha?   :', info.passFields.length ? 'sim' : '(pode ser 2 passos: usuario -> proximo -> senha)');
    console.log('2FA na 1a tela?     :', info.otpFieldsOnScreen ? 'sim' : 'nao (o 2FA, se houver, aparece POS credenciais)');
    console.log('\nProximo: rodar run.mjs com CAP_USER/CAP_PASS. Se pos-login aparecer campo de codigo,');
    console.log('e 2FA -> definir CAP_2FA=email + subir o code-watcher.py (ou relay manual).');
  } catch (e) { console.error('EXCECAO', e); process.exit(1); }
  finally { await browser.close(); }
})();
