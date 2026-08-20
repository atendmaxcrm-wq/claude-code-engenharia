#!/usr/bin/env python3
# ============================================================================
# Leitor automatico do codigo 2FA por EMAIL (IMAP). Torna o login 100% automatico.
#
# Quando run.mjs escreve _recon/_need_code.flag, este watcher busca na caixa o email com
# o codigo de N digitos recebido DEPOIS do flag, extrai e escreve _recon/_code.txt.
#
# Generico: a caixa e o filtro do remetente vem por env (funciona pra qualquer provedor
# IMAP, nao so Hostinger). So usa a stdlib (imaplib), sem dependencia.
#
# ENV:
#   CAP_ROOT        pasta de trabalho (default: cwd). Le/escreve em CAP_ROOT/_recon.
#   CAP_MAIL_HOST   servidor IMAP (ex.: imap.hostinger.com, imap.gmail.com). obrigatorio.
#   CAP_MAIL_PORT   porta IMAP SSL (default 993).
#   CAP_MAIL_USER   usuario/email da caixa que RECEBE o codigo. obrigatorio.
#   CAP_MAIL_PASS   senha (ou app-password). obrigatorio.
#   CAP_MAIL_FROM   substring/assunto que identifica o email do codigo (ex.: "clinicorp",
#                   "verifica", "codigo", "acesso"). | separado. default: verifica|codigo|código|acesso|code.
#   CAP_CODE_LEN    tamanho do codigo (default 6).
#
# Uso:
#   CAP_MAIL_HOST=... CAP_MAIL_USER=... CAP_MAIL_PASS=... python3 code-watcher.py test  # so lista/testa
#   CAP_MAIL_HOST=... CAP_MAIL_USER=... CAP_MAIL_PASS=... python3 code-watcher.py        # modo watcher
# ============================================================================
import imaplib, email, re, time, os, sys, json
from email.utils import parsedate_to_datetime

ROOT = os.environ.get('CAP_ROOT', os.getcwd())
OUT = ROOT + '/_recon'
HOST = os.environ.get('CAP_MAIL_HOST', '')
PORT = int(os.environ.get('CAP_MAIL_PORT', '993') or '993')
USER = os.environ.get('CAP_MAIL_USER', '')
PW = os.environ.get('CAP_MAIL_PASS', '')
FROM_HINTS = [h.strip().lower() for h in os.environ.get('CAP_MAIL_FROM', 'verifica|codigo|código|acesso|code').split('|') if h.strip()]
CODE_LEN = int(os.environ.get('CAP_CODE_LEN', '6') or '6')

FLAG = OUT + '/_need_code.flag'
CODE = OUT + '/_code.txt'
STOP = OUT + '/_watcher-stop.flag'
LOG = OUT + '/_watcher.log'
CODE_RE = re.compile(r'(?<!\d)(\d{%d})(?!\d)' % CODE_LEN)


def log(*a):
    line = '[' + time.strftime('%H:%M:%S') + '] ' + ' '.join(str(x) for x in a)
    print(line, flush=True)
    try:
        os.makedirs(OUT, exist_ok=True)
        open(LOG, 'a').write(line + '\n')
    except Exception:
        pass


def body_text(msg):
    out = []
    if msg.is_multipart():
        for p in msg.walk():
            if p.get_content_type() in ('text/plain', 'text/html'):
                try:
                    out.append(p.get_payload(decode=True).decode(p.get_content_charset() or 'utf-8', 'ignore'))
                except Exception:
                    pass
    else:
        try:
            out.append(msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', 'ignore'))
        except Exception:
            pass
    txt = ' '.join(out)
    return re.sub(r'<[^>]+>', ' ', txt)  # tira tags HTML


def connect():
    M = imaplib.IMAP4_SSL(HOST, PORT)
    M.login(USER, PW)
    M.select('INBOX')
    return M


def matches_hint(subj, frm):
    blob = (subj + ' ' + frm).lower()
    return any(h in blob for h in FROM_HINTS) if FROM_HINTS else True


def latest_code(M, since_epoch=0, verbose=False):
    typ, data = M.search(None, 'ALL')
    ids = data[0].split()
    best_t, best_code = 0, None
    for i in reversed(ids[-25:]):
        typ, d = M.fetch(i, '(RFC822)')
        if not d or not d[0]:
            continue
        msg = email.message_from_bytes(d[0][1])
        subj = str(msg.get('Subject', '') or '')
        frm = str(msg.get('From', '') or '')
        try:
            when = parsedate_to_datetime(msg.get('Date')).timestamp()
        except Exception:
            when = 0
        if verbose:
            log('  -', time.strftime('%H:%M', time.localtime(when)), '|', frm[:40], '|', subj[:60])
        if not matches_hint(subj, frm):
            continue
        body = body_text(msg)
        m = CODE_RE.search(body) or CODE_RE.search(subj)
        if m and when >= since_epoch - 90 and when > best_t:
            best_t, best_code = when, m.group(1)
    return best_code, best_t


def main():
    if not HOST or not USER or not PW:
        log('faltou CAP_MAIL_HOST/CAP_MAIL_USER/CAP_MAIL_PASS'); sys.exit(2)
    mode = sys.argv[1] if len(sys.argv) > 1 else 'watch'
    if mode == 'test':
        M = connect(); log('LOGIN OK em', HOST, 'como', USER); log('ultimos emails:')
        code, t = latest_code(M, 0, verbose=True)
        log('codigo mais recente que casa o filtro:', code, '(', time.strftime('%d/%m %H:%M', time.localtime(t)) if t else '-', ')')
        M.logout(); return
    log('watcher iniciado; host=%s user=%s; aguardando _need_code.flag' % (HOST, USER))
    served = set()
    while True:
        if os.path.exists(STOP):
            log('stop flag -> saindo'); break
        if os.path.exists(FLAG):
            try:
                info = json.load(open(FLAG)); flag_at = info.get('at', '')
            except Exception:
                flag_at = ''
            try:
                import datetime
                flag_epoch = datetime.datetime.fromisoformat(flag_at.replace('Z', '+00:00')).timestamp()
            except Exception:
                flag_epoch = time.time() - 10
            if flag_at in served:
                time.sleep(4); continue
            try:
                M = connect(); code, t = latest_code(M, flag_epoch); M.logout()
            except Exception as e:
                log('erro IMAP:', e); time.sleep(6); continue
            if code:
                open(CODE, 'w').write(code)
                served.add(flag_at)
                log('codigo', code, 'entregue (flag', flag_at, ')')
            else:
                log('ainda sem email de codigo pos-flag; retry')
        time.sleep(4)


if __name__ == '__main__':
    main()
