// ============================================================================
// MOTOR DE CAPTURA GENERICO - login robusto + browser VIVO + servidor de comandos.
// READ-ONLY: so navega e fotografa. NUNCA cria/edita/salva/envia nada na conta.
//
// Funde os dois casos reais:
//  - Clinicorp: 2FA por email (codigo via flag+_code.txt) + sessao que MORRE em reload
//               (navegar so por clique; login+captura no mesmo processo).
//  - Dietbox:   Azure B2C sem 2FA + cookie JWT que SOBREVIVE a reload (pode navegar por goto).
//
// Tudo por variaveis de ambiente (nenhuma URL/seletor hardcoded). Defaults cobrem
// Azure B2C e formularios comuns. Ajustar os CAP_*_SEL ao alvo depois do recon.
//
// ENV principais:
//   CAP_ROOT                    pasta de trabalho (default: cwd). Cria _recon/ e screens/.
//   CAP_LOGIN_URL               URL da tela de login (obrigatorio).
//   CAP_ORIGIN                  origin do app (ex.: https://app.exemplo.com). default: origin do LOGIN_URL.
//   CAP_HOME_URL                rota/URL da home pos-login (usada se a sessao sobrevive a reload).
//   CAP_USER / CAP_PASS         credenciais (obrigatorio).
//   CAP_USER_SEL / CAP_PASS_SEL / CAP_SUBMIT_SEL   seletores de login (defaults amplos).
//   CAP_LOGGED_SEL              CSS que SO existe logado (marcador de sessao). Se vazio, usa heuristica de URL.
//   CAP_LOGIN_RE                regex de host/rota de login (default: b2clogin|microsoftonline|/auth|/login|/signin).
//   CAP_2FA                     email | none | manual (default: auto-detecta a tela de codigo).
//   CAP_2FA_METHOD_TEXT         texto do metodo 2FA a escolher, se o sistema perguntar (ex.: "e-mail").
//   CAP_SESSION_SURVIVES_RELOAD 1|0 (do recon). 1 = home por goto; 0 = home por clique.
//   CAP_HOME_TEXT               texto(s) do link "Inicio" pra voltar por clique (| separado). default: Inicio|Início|Home|Painel|Dashboard.
//   CAP_MODULES                 lista opcional de modulos pra varrer sozinho (| separado). Vazio = so home + modo comando.
//   CAP_ALIVE_MIN               minutos de browser vivo (default 45).
//   CAP_UA                      user-agent (default Chrome desktop real).
//   CAP_CHROME                  caminho do chrome (default: acha o chromium-* do playwright).
//   CAP_PW                      caminho do playwright-core (default: /root/my-zap/node_modules/playwright-core/index.js).
// ============================================================================
import fs from 'node:fs';
const PW = process.env.CAP_PW || '/root/my-zap/node_modules/playwright-core/index.js';
const _pw = await import(PW);
const chromium = _pw.chromium ?? _pw.default?.chromium ?? _pw.default;

const ROOT = process.env.CAP_ROOT || process.cwd();
const OUT = ROOT + '/_recon', SCREENS = ROOT + '/screens', MODS = SCREENS + '/modulos';
const LOGIN_URL = process.env.CAP_LOGIN_URL || '';
const ORIGIN = process.env.CAP_ORIGIN || (LOGIN_URL ? new URL(LOGIN_URL).origin : '');
const HOME_URL = process.env.CAP_HOME_URL || ORIGIN;
const USER = process.env.CAP_USER, PASS = process.env.CAP_PASS;
const LOGGED_SEL = process.env.CAP_LOGGED_SEL || '';
const LOGIN_RE = new RegExp(process.env.CAP_LOGIN_RE || 'b2clogin|microsoftonline|/auth|/login|/signin', 'i');
const MODE_2FA = (process.env.CAP_2FA || 'auto').toLowerCase();
const METHOD_2FA_TEXT = process.env.CAP_2FA_METHOD_TEXT || 'e-mail';
const SURVIVES = process.env.CAP_SESSION_SURVIVES_RELOAD === '1';
const HOME_TEXTS = (process.env.CAP_HOME_TEXT || 'Inicio|Início|Home|Painel|Dashboard').split('|').map(s => s.trim()).filter(Boolean);
const MODULES = (process.env.CAP_MODULES || '').split('|').map(s => s.trim()).filter(Boolean);
const ALIVE_MS = (parseInt(process.env.CAP_ALIVE_MIN || '45', 10) || 45) * 60 * 1000;
const UA = process.env.CAP_UA || 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36';
const USER_SELS = (process.env.CAP_USER_SEL || '#signInName,#login-username-input,#email,input[type="email"],input[name="signInName"],input[name="username"],input[autocomplete="username"]').split(',');
const PASS_SELS = (process.env.CAP_PASS_SEL || '#password,#login-password-input,input[type="password"]').split(',');
const SUBMIT_SELS = (process.env.CAP_SUBMIT_SEL || '#next,#continue,button[type="submit"],button:has-text("Entrar"),button:has-text("Login"),button:has-text("Acessar")').split(',');

function resolveChrome() {
  if (process.env.CAP_CHROME) return process.env.CAP_CHROME;
  const base = (process.env.HOME || '/root') + '/.cache/ms-playwright';
  try { for (const d of fs.readdirSync(base).filter(x => x.startsWith('chromium-')).sort().reverse()) { const p = base + '/' + d + '/chrome-linux64/chrome'; if (fs.existsSync(p)) return p; } } catch {}
  return null;
}
const CHROME = resolveChrome();

const FLAG = OUT + '/_need_code.flag', CODE = OUT + '/_code.txt', RESULT = OUT + '/_login-result.json', PROG = OUT + '/_progress.log';
const CMD = OUT + '/_cmd.txt', CMDRES = OUT + '/_cmd-result.json', ALIVE = OUT + '/_alive.flag', STATE = OUT + '/_storage-state.json';
fs.mkdirSync(MODS, { recursive: true });
for (const f of [FLAG, CODE, RESULT, CMD, CMDRES, ALIVE]) { try { fs.unlinkSync(f); } catch {} }
fs.writeFileSync(PROG, '');
const save = (n, d) => fs.writeFileSync(n, typeof d === 'string' ? d : JSON.stringify(d, null, 2));
const log = (...a) => { fs.appendFileSync(PROG, `[${new Date().toISOString().slice(11, 19)}] ${a.join(' ')}\n`); };

let PAGE = null, CTX = null, MANIFEST = [];

const onLoginArea = (p) => { try { const u = new URL(p.url()); return LOGIN_RE.test(u.host) || LOGIN_RE.test(u.pathname); } catch { return true; } };
async function isLogged(p) {
  if (LOGGED_SEL) { try { const l = p.locator(LOGGED_SEL).first(); return (await l.count()) > 0 && await l.isVisible().catch(() => false); } catch { return false; } }
  return !onLoginArea(p);
}
const tryFill = async (p, sels, v) => { for (const s of sels) { const l = p.locator(s.trim()).first(); if (await l.count().catch(() => 0)) { await l.fill(v).catch(() => {}); return true; } } return false; };
const tryClick = async (p, sels) => { for (const s of sels) { const l = p.locator(s.trim()).first(); if (await l.count().catch(() => 0)) { await Promise.all([p.waitForLoadState('domcontentloaded').catch(() => {}), l.click().catch(() => {})]); return true; } } return false; };

async function doLogin(page) {
  log('goto login', LOGIN_URL);
  await page.goto(LOGIN_URL, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
  await page.waitForTimeout(2500);
  if (await isLogged(page)) { log('ja tinha sessao'); return; }
  await page.waitForSelector([...USER_SELS, ...PASS_SELS].join(','), { timeout: 30000 }).catch(() => {});
  await tryFill(page, USER_SELS, USER);
  await tryFill(page, PASS_SELS, PASS);
  log('submit credenciais');
  await tryClick(page, SUBMIT_SELS);
  // esperar: logado OU tela de 2FA (campos de codigo) OU segunda etapa
  await page.waitForSelector('input[maxlength="1"],input[autocomplete=one-time-code],#challenge-EMAIL,input[inputmode=numeric]', { timeout: 20000 }).catch(() => {});
  await page.waitForTimeout(1500);
  if (await isLogged(page)) { log('logou sem 2fa'); return; }

  const has2faScreen = await page.locator('input[maxlength="1"],input[autocomplete=one-time-code],#challenge-EMAIL,input[inputmode=numeric]').count().catch(() => 0);
  if (MODE_2FA === 'none' || (MODE_2FA === 'auto' && !has2faScreen)) {
    // sem 2FA esperado: dar mais tempo pro redirect logar
    for (let i = 0; i < 12 && !(await isLogged(page)); i++) await page.waitForTimeout(1500);
    return;
  }
  log('tela de 2FA detectada');
  // se o sistema pergunta o METODO (ex.: #challenge-EMAIL), escolher e avancar
  if (await page.locator('#challenge-EMAIL').count().catch(() => 0)) {
    await page.locator('#challenge-EMAIL').check({ force: true }).catch(async () => { await page.locator(`label:has-text("${METHOD_2FA_TEXT}")`).first().click().catch(() => {}); });
    await page.getByRole('button', { name: /Pr[óo]ximo|Continuar|Enviar/i }).first().click().catch(() => {});
    await page.waitForTimeout(1500);
  }
  await page.waitForSelector('input[maxlength="1"],input[autocomplete=one-time-code],input[inputmode=numeric],input[type=tel]', { timeout: 45000 }).catch(() => {});

  for (let attempt = 1; attempt <= 6; attempt++) {
    log(`codigo pedido (tentativa ${attempt}) -> escreve _need_code.flag`);
    save(FLAG, JSON.stringify({ at: new Date().toISOString(), attempt, method: MODE_2FA }));
    let w = 0, code = null;
    while (w < 15 * 60 * 1000) { if (fs.existsSync(CODE)) { code = fs.readFileSync(CODE, 'utf8').trim(); break; } await page.waitForTimeout(2000); w += 2000; }
    try { fs.unlinkSync(FLAG); } catch {}
    if (!code) throw new Error('timeout codigo 2FA');
    const digits = code.replace(/\D/g, ''); log('recebeu codigo');
    const boxes = page.locator('input[maxlength="1"],input[autocomplete=one-time-code]'); const nb = await boxes.count().catch(() => 0);
    if (nb > 1) { for (let i = 0; i < nb && i < digits.length; i++) await boxes.nth(i).fill(digits[i]).catch(() => {}); }
    else await page.locator('input[autocomplete=one-time-code],input[inputmode=numeric],input[type=tel]').first().fill(digits).catch(() => {});
    await page.waitForTimeout(400);
    await page.locator('button:has-text("Confirmar"),button:has-text("Verificar"),button:has-text("Entrar"),button[type="submit"]').first().click().catch(() => {});
    try { fs.unlinkSync(CODE); } catch {}
    for (let k = 0; k < 16; k++) { await page.waitForTimeout(1500); if (await isLogged(page)) { log('2fa OK'); return; } }
    log('codigo nao autenticou -> tentar reenviar');
    for (let s = 0; s < 40; s++) { const rl = page.locator('text=/Reenviar c[óo]digo|Reenviar|Resend/i').first(); if (await rl.count().catch(() => 0) && await rl.isVisible().catch(() => false)) { await rl.click().catch(() => {}); break; } await page.waitForTimeout(2000); }
    await page.waitForTimeout(1500);
  }
  throw new Error('esgotou tentativas de codigo 2FA');
}

const dumpStructure = (page) => page.evaluate(() => {
  const clean = el => (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 90);
  const q = s => [...document.querySelectorAll(s)]; const uniq = a => [...new Set(a.filter(Boolean))];
  return {
    title: document.title, url: location.href,
    headings: uniq(q('h1,h2,h3,h4').map(clean)).slice(0, 60),
    tabs: uniq(q('[role=tab],.nav-tabs a,[class*="tab"] a,ul[class*="tab"] li,[class*="Tab"]').map(clean)).slice(0, 60),
    tableHeaders: uniq(q('table th').map(clean)).slice(0, 120),
    buttons: uniq(q('button,[role=button],a.btn,[class*="btn"]').map(clean)).slice(0, 140),
    labels: uniq(q('label').map(clean)).slice(0, 120),
    fields: q('input,select,textarea').slice(0, 160).map(i => ({ tag: i.tagName.toLowerCase(), type: i.type || null, name: i.name || i.id || null, placeholder: i.placeholder || null })),
    selectOptions: q('select').slice(0, 50).map(s => ({ name: s.name || s.id || null, options: [...s.options].map(o => o.text.trim()).slice(0, 60) })),
    // navLinks/listItems costumam carregar nomes de cliente/chat (PII). sanitizar-manifest.mjs os REMOVE antes de empacotar.
    navLinks: uniq(q('nav a, aside a, [class*="menu"] a, [class*="sidebar" i] a, [class*="nav" i] a').map(el => `${clean(el)} => ${el.getAttribute('href') || ''}`)).slice(0, 160),
    listItems: uniq(q('nav li, aside li, [class*="menu"] li, [class*="list"] li, li').map(clean)).slice(0, 160),
  };
});

const snap = async (label) => {
  const p = PAGE; await p.waitForTimeout(1500);
  if (onLoginArea(p) && !(await isLogged(p))) { log('perdeu sessao / em login em ' + label); return { ok: false, lost: true }; }
  const n = String(MANIFEST.length + 1).padStart(2, '0');
  const safe = (label || 'tela').normalize('NFD').replace(/[^\w]+/g, '-').toLowerCase().slice(0, 46);
  const shot = `mod-${n}-${safe}.png`;
  await p.screenshot({ path: MODS + '/' + shot, fullPage: true }).catch(() => {});
  MANIFEST.push({ label, url: p.url(), shot, structure: await dumpStructure(p) });
  save(OUT + '/manifest.json', MANIFEST); log(`capturou ${label} (${p.url()})`);
  return { ok: true, shot, url: p.url() };
};
const openMenu = async () => { const p = PAGE; for (const sel of ['button[aria-label*="menu" i]', '[class*="hamburger"]', 'header button:first-of-type', 'header button:has(svg)', 'nav button', 'button:has(svg)']) { const l = p.locator(sel).first(); if (await l.count().catch(() => 0) && await l.isVisible().catch(() => false)) { await l.click().catch(() => {}); await p.waitForTimeout(1000); return true; } } return false; };
const clickText = async (text) => { const p = PAGE; const scoped = p.locator('nav, aside, [class*="sidebar" i], [class*="menu" i], [role=navigation]').getByText(text, { exact: true }).first(); if (await scoped.count().catch(() => 0)) { await scoped.click().catch(() => {}); return true; } const any = p.getByText(text, { exact: true }).first(); if (await any.count().catch(() => 0)) { await any.click().catch(() => {}); return true; } return false; };
const dismissModals = async () => { const p = PAGE; for (const sel of ['button:has-text("Continuar na agenda atual")', 'button:has-text("Continuar")', 'button:has-text("Entendi")', 'button:has-text("Fechar")', 'button:has-text("Depois")', 'button:has-text("Pular")', 'button:has-text("Agora não")', 'button[aria-label*="fechar" i]', 'button[aria-label*="close" i]', '.modal button.close']) { try { const b = p.locator(sel).first(); if (await b.count().catch(() => 0) && await b.isVisible().catch(() => false)) { await b.click().catch(() => {}); await p.waitForTimeout(600); } } catch {} } };
const goHome = async () => {
  const p = PAGE;
  if (SURVIVES) { await p.goto(HOME_URL, { waitUntil: 'domcontentloaded' }).catch(() => {}); await p.waitForTimeout(2500); await dismissModals(); return await isLogged(p); }
  await openMenu();
  for (const t of HOME_TEXTS) { const l = p.getByText(t, { exact: true }).first(); if (await l.count().catch(() => 0)) { await l.click().catch(() => {}); await p.waitForTimeout(2000); break; } }
  await dismissModals(); return await isLogged(p);
};

(async () => {
  if (!LOGIN_URL || !USER || !PASS) { save(RESULT, { loggedIn: false, reason: 'faltou CAP_LOGIN_URL/CAP_USER/CAP_PASS' }); log('faltou config'); process.exit(1); }
  const browser = await chromium.launch({ executablePath: CHROME || undefined, headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  try {
    const ctx = await browser.newContext({ userAgent: UA, locale: 'pt-BR', viewport: { width: 1440, height: 900 } });
    CTX = ctx; const page = await ctx.newPage(); PAGE = page;
    const net = []; page.on('request', r => { try { if (['xhr', 'fetch'].includes(r.resourceType())) net.push(r.method() + ' ' + r.url().slice(0, 200)); } catch {} });

    await doLogin(page);
    let logged = await isLogged(page); for (let i = 0; i < 12 && !logged; i++) { await page.waitForTimeout(1500); logged = await isLogged(page); }
    if (!logged) { log('NAO logou. url=' + page.url()); save(RESULT, { loggedIn: false, reason: 'sem marcador de logado', url: page.url() }); process.exit(1); }
    log('LOGADO. url=' + page.url()); await dismissModals();
    try { save(STATE, await ctx.storageState()); } catch {}
    await snap('home');
    save(RESULT, { loggedIn: true, telas: MANIFEST.length, fase: 'capturando' });

    // varredura base opcional (so se CAP_MODULES foi passado). Senao, o driver dirige.
    for (const mod of MODULES) {
      try { await goHome(); await openMenu(); if (await clickText(mod)) { await page.waitForTimeout(3000); await dismissModals(); await snap(mod); } else log('nao clicou ' + mod); }
      catch (e) { log('erro ' + mod + ': ' + e); }
    }

    save(RESULT, { loggedIn: true, telas: MANIFEST.length, fase: 'vivo-aguardando-comandos' });
    log('base FIM. telas=' + MANIFEST.length + '. modo comando (driver.mjs).');

    // SERVIDOR DE COMANDOS (browser VIVO). verbos: click|snap|menu|tab|goto|goback|home|dismiss|sel|selnth|type|dump|quit
    const tEnd = Date.now() + ALIVE_MS; save(ALIVE, JSON.stringify({ since: new Date().toISOString(), aliveMin: ALIVE_MS / 60000 }));
    while (Date.now() < tEnd) {
      if (!fs.existsSync(CMD)) { await page.waitForTimeout(1000); continue; }
      const raw = fs.readFileSync(CMD, 'utf8').trim(); try { fs.unlinkSync(CMD); } catch {}
      const [verb, ...rest] = raw.split(':'); const arg = rest.join(':').trim(); log('CMD ' + raw);
      let res = { ok: false, cmd: raw };
      try {
        if (verb === 'quit') { save(CMDRES, { ok: true, bye: true }); break; }
        else if (verb === 'menu') { await openMenu(); res = await snap('menu'); }
        else if (verb === 'home') { const ok = await goHome(); res = { ok, url: page.url() }; }
        else if (verb === 'dismiss') { await dismissModals(); res = { ok: true, url: page.url() }; }
        else if (verb === 'dump') { res = { ok: true, url: page.url(), structure: await dumpStructure(page) }; }
        else if (verb === 'click') { const c = await clickText(arg); await page.waitForTimeout(2800); await dismissModals(); res = { ok: c, clicked: arg, url: page.url() }; }
        else if (verb === 'tab') { const c = await clickText(arg); await page.waitForTimeout(2000); res = { ok: c, tab: arg, url: page.url() }; }
        else if (verb === 'goto') { await page.goto(new URL(arg, ORIGIN).href, { waitUntil: 'domcontentloaded' }).catch(() => {}); await page.waitForTimeout(2600); await dismissModals(); res = { ok: await isLogged(page), url: page.url() }; }
        else if (verb === 'goback') { await page.goBack({ waitUntil: 'domcontentloaded' }).catch(() => {}); await page.waitForTimeout(2000); res = { ok: await isLogged(page), url: page.url() }; }
        else if (verb === 'sel') { const l = page.locator(arg).first(); const c = await l.count().catch(() => 0); if (c) await l.click().catch(() => {}); await page.waitForTimeout(2600); await dismissModals(); res = { ok: !!c, sel: arg, url: page.url() }; }
        else if (verb === 'selnth') { const i = arg.lastIndexOf('::'); const sel = arg.slice(0, i); const n = parseInt(arg.slice(i + 2), 10) || 0; const l = page.locator(sel).nth(n); const c = await l.count().catch(() => 0); if (c) await l.click().catch(() => {}); await page.waitForTimeout(2800); await dismissModals(); res = { ok: !!c, sel, n, url: page.url() }; }
        else if (verb === 'type') { const i = arg.indexOf('::'); const sel = arg.slice(0, i); const txt = arg.slice(i + 2); const l = page.locator(sel).first(); const c = await l.count().catch(() => 0); if (c) { await l.fill(txt).catch(() => {}); await page.waitForTimeout(1800); } res = { ok: !!c, typed: txt, url: page.url() }; }
        else if (verb === 'xy') { const [x, y] = arg.split(',').map(n => parseFloat(n)); await page.mouse.click(x, y).catch(() => {}); await page.waitForTimeout(2200); await dismissModals(); res = { ok: true, xy: [x, y], url: page.url() }; }
        else if (verb === 'eval') { const r = await page.evaluate((code) => { try { const out = eval(code); return typeof out === 'string' ? out : JSON.stringify(out); } catch (e) { return 'EVAL_ERR: ' + e.message; } }, arg); res = { ok: true, eval: r, url: page.url() }; }
        else if (verb === 'press') { await page.keyboard.press(arg).catch(() => {}); await page.waitForTimeout(900); res = { ok: true, pressed: arg, url: page.url() }; }
        else if (verb === 'kbtype') { await page.keyboard.type(arg, { delay: 60 }).catch(() => {}); await page.waitForTimeout(900); res = { ok: true, kbtyped: arg, url: page.url() }; }
        else if (verb === 'snap') { res = await snap(arg || 'tela'); }
        else res = { ok: false, err: 'verbo desconhecido: ' + verb };
      } catch (e) { res = { ok: false, err: String(e) }; }
      res.loggedIn = await isLogged(page); res.at = new Date().toISOString(); save(CMDRES, res);
      save(RESULT, { loggedIn: res.loggedIn, telas: MANIFEST.length, fase: 'vivo' });
    }
    try { fs.unlinkSync(ALIVE); } catch {}
    save(OUT + '/net-calls-app.json', net.slice(0, 1200));
    save(RESULT, { loggedIn: true, telas: MANIFEST.length, fase: 'encerrado' }); log('encerrado. telas=' + MANIFEST.length);
    process.exit(0);
  } catch (e) { save(RESULT, { loggedIn: false, error: String(e), telas: MANIFEST.length }); log('EXCECAO ' + e); console.error(e); process.exit(1); }
  finally { await browser.close(); }
})();
