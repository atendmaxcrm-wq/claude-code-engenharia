# 2FA por email - as 3 vias de resolver o codigo

O gargalo do Clinicorp: o login manda um codigo de 6 digitos por email a cada sessao (e
codigo velho > ~5min expira). Sem resolver isso, a captura trava toda hora pedindo codigo.
A solucao e dar ao script uma forma de LER o codigo. Tres vias, em ordem de preferencia.

O contrato entre o `run.mjs` e quem resolve o codigo e por ARQUIVO:
- `run.mjs` escreve `_recon/_need_code.flag` (JSON com `at` = timestamp do pedido) quando
  chega na tela de codigo.
- Quem resolve escreve o codigo em `_recon/_code.txt`.
- `run.mjs` le, preenche, apaga o `_code.txt` e segue. Se o codigo nao autenticar, reenvia e
  pede de novo (ate 6 tentativas).

Isso significa que QUALQUER das 3 vias funciona sem mexer no run.mjs - muda so QUEM escreve o
`_code.txt`.

---

## (A) IMAP watcher automatico - PREFERIDO

`code-watcher.py` fica de olho no `_need_code.flag`; quando aparece, conecta na caixa por
IMAP, acha o email do codigo recebido DEPOIS do flag, extrai os N digitos e escreve o
`_code.txt`. Login 100% automatico, sem relay humano. Foi assim no Clinicorp (Hostinger).

Funciona pra qualquer provedor IMAP (Hostinger, Gmail com app-password, Zoho, etc). O
filtro do remetente/assunto e por env (`CAP_MAIL_FROM`), pra achar o email certo.

```bash
# 1) testar o acesso e ver que codigo ele acharia (antes de logar)
CAP_ROOT=/root/<slug>-blueprint \
CAP_MAIL_HOST=imap.hostinger.com CAP_MAIL_USER=caixa@dominio CAP_MAIL_PASS=... \
CAP_MAIL_FROM='clinicorp|verifica|codigo|acesso' \
python3 code-watcher.py test

# 2) rodar o watcher (background) junto com o run.mjs
CAP_ROOT=/root/<slug>-blueprint \
CAP_MAIL_HOST=imap.hostinger.com CAP_MAIL_USER=... CAP_MAIL_PASS=... \
python3 code-watcher.py
```

Requisitos: a caixa precisa ter IMAP habilitado. Gmail exige "app password" (senha de app),
a senha normal nao loga por IMAP.

## (B) Email conectado ao Claude (Gmail MCP)

Se a caixa que recebe o codigo for a conta de email conectada a esta sessao do Claude, da
pra ler o codigo pela tool de email (procurar o email recente do remetente do sistema,
extrair os digitos) e escrever no `_code.txt` a mao:

```bash
echo "123456" > /root/<slug>-blueprint/_recon/_code.txt
```

ARMADILHA: confirmar que a conta conectada e a MESMA que RECEBE o codigo. No Clinicorp o
Gmail conectado (`gleidsongirao0631@gmail.com`) NAO era o destinatario (o codigo ia pra
`gleidson@atendmax.com`); nesse caso a via (B) nao serve, cair pra (A) ou (C).

## (C) Relay manual - fallback universal

Serve pra 2FA por SMS ou app autenticador (onde nao ha como automatizar) e como rede de
seguranca quando (A) e (B) falham. O run.mjs escreve o `_need_code.flag` e ESPERA ate 15min.
O usuario le o codigo (no celular / no email) e o passa; escrever no arquivo:

```bash
echo "123456" > /root/<slug>-blueprint/_recon/_code.txt
```

Como o run.mjs roda em background, da pra monitorar quando ele pede o codigo:

```bash
# aparece uma linha "codigo pedido (tentativa N)" quando esta esperando
tail -f /root/<slug>-blueprint/_recon/_progress.log
```

---

## Regras que evitam falso-negativo

- **Codigo expira**: o run.mjs so escreve o flag quando JA esta na tela de codigo; resolver
  rapido. Se demorar > ~5min, o codigo pode ter expirado - o run.mjs reenvia e pede de novo.
- **Codigo do email ANTERIOR**: o watcher so aceita email recebido DEPOIS do timestamp do
  flag (com folga de 90s), pra nao pegar um codigo velho da caixa.
- **Persistent context recusado**: alguns sistemas recusam o passo "autenticar dispositivo"
  com contexto persistente do Playwright. Usar contexto NAO-persistente (o run.mjs ja faz).
- **1 codigo cobre a sessao inteira**: por isso o browser fica VIVO ~45min. Nao reiniciar o
  run.mjs a toa - cada restart custa um novo codigo.
