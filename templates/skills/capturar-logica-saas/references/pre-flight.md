# Pre-flight - a checklist de pre-verificacoes (Fase 0)

Rodar ANTES de tocar o sistema. Cada item resolvido = uma trava a menos no meio da
captura. O 2FA e o item 4 e e o mais critico (descobrir so na hora de logar trava tudo).

---

## 1. Autorizacao e escopo

- [ ] O usuario tem direito de acessar esta conta? (conta do cliente dele / propria / com
      autorizacao explicita). Isto e um sistema de TERCEIRO atras de login: sem
      autorizacao clara, PARAR e perguntar.
- [ ] Registrar por escrito: QUAL sistema (nome + URL), QUAL conta (login), e o OBJETIVO
      (que sistema o usuario vai reconstruir a partir do blueprint).
- [ ] Confirmar que a captura sera READ-ONLY (so navegar e fotografar).

## 2. Acesso (credenciais)

- [ ] URL de login.
- [ ] Usuario ou email de acesso. (Alguns sistemas usam "usuario", nao email - anotar qual.)
- [ ] Senha.
- [ ] Se faltar qualquer um, PEDIR ao usuario. Nunca chutar nem seguir sem.
- [ ] Guardar em variaveis de ambiente (`CAP_USER`, `CAP_PASS`), nunca no script nem em repo.

## 3. Ambiente tecnico

Sondar o que a captura precisa:

```bash
# Node
node -v
# playwright-core (reusar o do my-zap se existir)
ls /root/my-zap/node_modules/playwright-core/index.js 2>/dev/null && echo "playwright-core OK"
# Chromium do Playwright
ls ~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome 2>/dev/null && echo "chromium OK"
# python3 (so se for usar o watcher de 2FA por email)
python3 -c "import imaplib; print('imaplib OK')"
```

- [ ] Node presente.
- [ ] `playwright-core` acessivel (ou instalar; apontar `CAP_PW`).
- [ ] Chromium do Playwright presente (ou apontar `CAP_CHROME`).
- [ ] `python3` + `imaplib` (so se for IMAP watcher).

## 4. 2FA / acesso ao email (O PONTO CRITICO)

- [ ] O login tem segundo fator? Descobrir ANTES. Se nao souber, rodar `login-probe.mjs` e,
      no primeiro teste de login, observar se aparece tela de codigo.
- [ ] Por onde chega o codigo? EMAIL, SMS, ou app autenticador?

Se for **codigo por EMAIL**, escolher UMA das tres vias (detalhe em `2fa-email.md`) e ja
coletar o que ela exige AGORA:

- [ ] **(A) IMAP watcher** (preferido, 100% automatico): pedir ao usuario host/porta/user/
      senha IMAP da caixa que RECEBE o codigo. Setar `CAP_MAIL_HOST/PORT/USER/PASS`.
      Testar com `python3 code-watcher.py test` (lista os ultimos emails e o codigo achado).
- [ ] **(B) Email conectado ao Claude** (Gmail MCP): confirmar que a caixa conectada e a
      MESMA que recebe o codigo. (No Clinicorp o Gmail conectado NAO era o destinatario.)
- [ ] **(C) Relay manual** (fallback / SMS / autenticador): combinar que o usuario vai colar
      o codigo quando o script pedir (o script escreve `_recon/_need_code.flag`; o usuario
      responde escrevendo o codigo em `_recon/_code.txt`).

Se for **SMS ou app autenticador**: so a via (C) manual serve (nao ha como automatizar).

## 5. Privacidade / PII

- [ ] Avisar o usuario: a navegacao passa por telas com dado real (pacientes, clientes,
      financeiro). O pacote final e SANITIZADO (ver `pii-sanitizacao.md`).
- [ ] Combinar: o pacote inclui a senha de acesso? Por padrao NAO. So com pedido explicito,
      num `ACESSO.md` avisado como sensivel (usar `INCLUIR_ACESSO=1` no empacotar.sh).
- [ ] Nao percorrer fluxo que grava dado (cadastrar, publicar, enviar msg) na conta do cliente.

## 6. Workspace

- [ ] Definir a pasta de trabalho FORA de qualquer repo versionado:
      `CAP_ROOT=/root/<slug>-blueprint`.
- [ ] Nunca dentro de um repo git (vaza screenshots com PII e credenciais no historico).

---

## Resumo pra confirmar com o usuario

Fechar a Fase 0 com uma frase que o usuario confirma, do tipo:

> "Vou capturar o **<sistema>** (conta **<login>**), read-only, pra voce reconstruir
> **<objetivo>**. Login e **<tipo>**, 2FA por **<email/sms/none>** resolvido via
> **<IMAP watcher / MCP / manual>**. Workspace em **/root/<slug>-blueprint**. Pacote final
> sanitizado (sem PII){, com ACESSO.md incluso / sem senha}. Ok?"

So depois do "ok" seguir pra Fase 1.
