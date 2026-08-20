---
name: capturar-logica-saas
description: Captura a LOGICA e a UX de um SaaS de referencia (sistema logado, atras de credenciais) e produz um BLUEPRINT navegavel - "como funciona" tela a tela, campos, fluxos e modelagem de entidades sugerida - para reconstruir um sistema proprio em OUTRA maquina/VPS. Metodo validado no Clinicorp (odonto) e no Dietbox (nutri). Faz login robusto (inclui 2FA por email resolvido de forma automatica via IMAP), navega READ-ONLY com um browser vivo dirigido por comandos, fotografa cada tela e extrai a estrutura DOM (headings/abas/botoes/labels/campos), sanitiza PII e empacota tudo num zip pronto pra levar. Comeca SEMPRE por uma fase de PRE-VERIFICACOES (acesso, ambiente, 2FA/acesso ao email, permissao, privacidade) antes de tocar o sistema. Use quando o usuario disser "captura a logica do <sistema>", "faz o blueprint desse SaaS", "quero entender como funciona o <sistema> pra reconstruir", "igual fizemos no Clinicorp/Dietbox", "clona a logica desse sistema", "mapeia as telas/fluxos desse painel logado". NAO e replicar-sistema (imagem/video -> a CARA) nem clonar-site (URL publica -> site de marketing); aqui a entrada e um SISTEMA LOGADO de terceiro e a saida e um BLUEPRINT da logica/UX. Extrair os DADOS reais do cliente e um metodo IRMAO (ver secao "Quando tambem precisar dos dados"), nao esta skill.
---

# Capturar a logica/UX de um SaaS (blueprint pra reconstruir)

Captura como um sistema logado FUNCIONA (telas, fluxos, campos, config, relatorios) e
entrega um BLUEPRINT que viaja pra outra VPS, onde o BUILD acontece de fato. Nao e o
visual (isso e `replicar-sistema`) nem um site publico (isso e `clonar-site`): aqui a
entrada e um SaaS de terceiro atras de login e a saida e o "manual de funcionamento".

Casos que validaram o metodo: Clinicorp (gestao odontologica, login com 2FA por email +
sessao que morre em reload) e Dietbox (gestao pra nutri, Azure B2C sem 2FA + JWT que
sobrevive). Os dois cobrem as duas ramificacoes de autenticacao que este metodo trata.

```
PRE-VERIFICACOES (Fase 0) -> RECON DE AUTH (Fase 1) -> MOTOR DE CAPTURA (Fase 2)
-> VARREDURA SISTEMATICA (Fase 3) -> SANITIZAR + BLUEPRINT + PACOTE (Fase 4)
```

> REGRA DE OURO: **READ-ONLY sempre.** A captura so navega e fotografa. NUNCA cria,
> edita, salva, envia ou publica nada na conta do cliente. Fluxo que gravaria dado
> (cadastrar paciente, publicar pagina publica, enviar mensagem, submeter formulario de
> lead) e DESCRITO em texto, nao percorrido.

---

## Fase 0 - PRE-VERIFICACOES (pre-flight) - NAO PULAR

Esta e a fase que o dono pediu em destaque. Antes de tocar o sistema, rodar esta
checklist com o usuario e so seguir quando cada item estiver resolvido. O detalhe de
cada uma esta em `references/pre-flight.md`; o resumo:

1. **Autorizacao e escopo.** Confirmar com o usuario que ele tem direito de acessar a
   conta (e do cliente dele / propria / com autorizacao). Registrar QUAL sistema, QUAL
   conta e o OBJETIVO (que sistema ele vai reconstruir). Isto e captura de um sistema de
   TERCEIRO: sem autorizacao clara, parar e perguntar.

2. **Acesso (credenciais).** Coletar URL de login + usuario/email + senha. Se faltar
   qualquer um, PEDIR ao usuario antes de comecar (nunca chutar). Guardar em variaveis de
   ambiente, nunca hardcode no script nem no repo.

3. **Ambiente tecnico.** Verificar que da pra rodar a captura nesta maquina:
   - Node + `playwright-core` (reusar `/root/my-zap/node_modules/playwright-core` se existir).
   - Chromium do Playwright (`~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome`).
   - `python3` com `imaplib` (stdlib) SE for usar o watcher de 2FA.
   Comando de sondagem em `references/pre-flight.md`. Se faltar, instalar/apontar antes.

4. **2FA / acesso ao email (o ponto critico).** Perguntar/descobrir se o login tem
   segundo fator e por onde chega o codigo. Se for **codigo por email**, precisamos de UMA
   destas tres vias (cascata, ver `references/2fa-email.md`):
   - **(A) IMAP watcher automatico** (preferido): usuario da as credenciais da caixa que
     RECEBE o codigo (host/porta/user/senha IMAP). O `code-watcher.py` le o codigo sozinho
     e o login fica 100% automatico. Foi assim no Clinicorp (Hostinger IMAP).
   - **(B) Email conectado ao Claude** (Gmail MCP): se a caixa que recebe o codigo for a
     conta conectada, ler o codigo pela tool de email. ATENCAO: confirmar que e a MESMA
     caixa que recebe o codigo (no Clinicorp o Gmail conectado NAO era o destinatario).
   - **(C) Relay manual** (fallback): o script pede e o usuario COLA o codigo. Funciona pra
     2FA por SMS ou app autenticador, onde nao ha como automatizar.
   Decidir a via AQUI, na Fase 0, e ja coletar o que ela exige. 2FA descoberto so na hora
   de logar trava a captura.

5. **Privacidade / PII.** Avisar o usuario: a navegacao vai passar por telas com dado real
   (pacientes, clientes, financeiro). O pacote final e SANITIZADO (ver Fase 4 e
   `references/pii-sanitizacao.md`). Combinar se o pacote inclui a senha de acesso (por
   padrao NAO; so com pedido explicito, num `ACESSO.md` avisado como sensivel).

6. **Workspace.** Definir a pasta de trabalho FORA de qualquer repo versionado (ex.:
   `/root/<slug>-blueprint/`). Nunca dentro de um repo git publico (vazaria screenshots
   com PII e credenciais).

Saida da Fase 0: um pequeno resumo escrito ("vou capturar o sistema X, conta Y, 2FA por
email via IMAP tal, workspace em Z, read-only, pacote sanitizado") que o usuario confirma.

---

## Fase 1 - Recon de autenticacao

Duas perguntas decidem a estrategia inteira. Rodar `scripts/login-probe.mjs` (ou inspecao
manual) pra responder:

1. **Que tipo de login e?** Formulario proprio, Azure AD B2C
   (`#signInName`/`#password`/`#next`), OAuth de terceiro, com ou sem 2FA. O probe reporta
   os campos que achou e se caiu numa tela de 2FA.

2. **A sessao sobrevive a um reload?** Isto muda TUDO:
   - **Sobrevive** (auth por cookie JWT persistente, ex.: Dietbox): da pra navegar por
     `goto` em rotas reais, reusar `storageState`, e a captura fica trivial.
   - **NAO sobrevive** (token em memoria/sessionStorage, ex.: Clinicorp): login + captura
     no MESMO processo, navegar SO por clique, browser vivo. `goto`/reload pos-login volta
     pra tela de login e perde a sessao.

O `run.mjs` cobre os dois modos; o recon so diz qual ligar (`CAP_SESSION_SURVIVES_RELOAD`).

---

## Fase 2 - Motor de captura (browser vivo dirigido por comandos)

O motor tem duas pecas, ambas parametrizadas por variaveis de ambiente (nenhuma URL ou
seletor hardcoded):

- **`scripts/run.mjs`** - faz o login robusto (com/sem 2FA por email), abre a home, roda
  uma varredura base dos modulos e depois entra em **modo servidor**: mantem o browser
  VIVO por ~45min lendo comandos de um arquivo. UM codigo de 2FA cobre a sessao inteira.
- **`scripts/driver.mjs`** - le um arquivo de comandos (1 por linha) e os manda pro
  servidor vivo, coletando cada resultado. E assim que voce "dirige" a captura.

Verbos do servidor:
`click:TEXTO` `snap:ROTULO` `menu` `tab:TEXTO` `goto:/rota` `goback` `home` `dismiss`
`sel:CSS` `selnth:CSS::N` `type:CSS::texto` `dump` `quit`
`xy:X,Y` (clique por coordenada - pra FAB/elemento sem seletor)
`eval:JS` (roda JS no browser vivo e retorna o resultado - inspecionar DOM/achar coordenadas)
`press:TECLA` (keyboard.press - Enter/ArrowDown/Tab)
`kbtype:TEXTO` (keyboard.type no foco atual - pra MASCARA e Multiselect Vue que so aceitam
teclado: clicar o campo, kbtype o filtro, press ArrowDown, press Enter).

Cada tela capturada gera: um **screenshot** (`screens/modulos/mod-NN-rotulo.png`) e uma
entrada no **`manifest.json`** com a ESTRUTURA DOM (title, headings, tabs, tableHeaders,
buttons, labels, fields, selectOptions, navLinks, listItems). Ler a estrutura em TEXTO
(o manifest) e barato; o screenshot fica como referencia visual. Preferir ler o manifest
a abrir imagem, exceto quando precisa confirmar layout/aparencia.

Como rodar (o motor fica em background porque o browser vive ~45min):

```bash
# 1) subir o motor (background). Ele loga, abre a home e espera comandos.
CAP_ROOT=/root/<slug>-blueprint \
CAP_LOGIN_URL='https://.../login' CAP_ORIGIN='https://...' \
CAP_USER="$USUARIO" CAP_PASS="$SENHA" \
CAP_2FA=email CAP_SESSION_SURVIVES_RELOAD=0 \
node scripts/run.mjs        # rodar com run_in_background=true

# 2) SE 2FA por email via IMAP: subir o watcher junto (background)
CAP_MAIL_HOST=imap.hostinger.com CAP_MAIL_USER=... CAP_MAIL_PASS=... \
CAP_ROOT=/root/<slug>-blueprint python3 scripts/code-watcher.py

# 3) dirigir a captura (foreground, em LOTES curtos - ver gotcha do timeout)
node scripts/driver.mjs comandos.txt
```

GOTCHA de shell (medido): `driver.mjs` com muitos cliques lentos estoura o cap de 2min do
Bash em foreground. Rodar em `run_in_background` OU em lotes curtos (5-8 comandos). O
`run.mjs` SEMPRE em background (vive 45min).

---

## Fase 3 - Varredura sistematica

Ordem que funcionou (dirigir com `driver.mjs`, um lote por area):

1. **Home / dashboard** - os cards e KPIs de entrada.
2. **Modulos principais** do menu, um a um (agenda, clientes/pacientes, financeiro,
   mensagens, config, relatorios, usuarios/permissoes...).
3. **Aprofundar os formularios-chave**: abrir o form de "criar X" (agendamento, paciente,
   usuario) e fotografar os campos + a matriz de opcoes. NAO submeter (read-only).
4. **Configuracoes**: percorrer cada secao (costuma ser o mapa das entidades do sistema).
5. **Catalogo de relatorios**: listar categorias e o padrao de filtro. Colunas de
   relatorio so renderizam com dados no periodo; sem a base real, documentar a ESTRUTURA.
6. **Tela de detalhe / prontuario** (se autorizado abrir 1 registro): mapear as ABAS e a
   composicao, SO a estrutura. Screenshots com dado real ficam FORA do pacote.
7. **Pagina publica / link do lead** (se houver): capturar a tela de ENTRADA sem percorrer
   os passos que criam um registro real.

Dedupar por ROTULO, nao por URL: em SPAs a maioria dos modulos mantem a url "/". Registrar
tudo no manifest conforme captura.

---

## Fase 4 - Sanitizar, escrever o BLUEPRINT e empacotar

1. **Sanitizar o manifest** (`scripts/sanitizar-manifest.mjs`): dropar `navLinks` e
   `listItems` (a sidebar costuma carregar lista de chat/clientes com nomes reais) e
   qualquer campo com PII. Conferir o FUNDO dos screenshots de modal: modal sobre lista
   vaza os nomes atras - excluir esses shots. Protocolo completo em
   `references/pii-sanitizacao.md`.

2. **Escrever o BLUEPRINT** `BLUEPRINT-<SISTEMA>.md` a partir do template
   `references/blueprint-template.md`: arquitetura, navegacao, cada modulo com campos e
   fluxos, catalogo de relatorios, e uma **modelagem de entidades sugerida** pra
   reconstruir. Le como "manual de funcionamento", nao como diario da captura.

3. **Escrever o `LEIA-ME-PRIMEIRO.md`**: briefing curto pro agente/dev que vai receber o
   pacote na outra VPS (por onde comecar, o que e cada arquivo, o aviso de PII, e que o
   BUILD e la).

4. **Empacotar** (`scripts/empacotar.sh`): zip com o BLUEPRINT + LEIA-ME + screens
   sanitizados + manifest sanitizado + os scripts. SEM `_recon/` de sessao, SEM logs, SEM
   `_storage-state.json`, SEM senha (a nao ser que o dono peca o `ACESSO.md`). Gerar e
   registrar o SHA256. O usuario leva por SFTP pra outra VPS.

---

## Quando tambem precisar dos DADOS (metodo irmao, NAO esta skill)

Esta skill captura a FORMA (logica/UX). Se o objetivo tambem for migrar o CONTEUDO real do
cliente (a base de clientes, historico, biblioteca), isso e um metodo IRMAO: mapear os
endpoints da API que o proprio front chama (a aba de network do browser vivo ja loga em
`_recon/net-calls-app.json`) e extrair via chamadas autenticadas, com um dicionario de
campos e UNIDADES provadas por censo. Foi o que se fez com a base do Dietbox (1524
pacientes). Avisar o usuario que e um segundo esforco e tratar separado. As duas entregas
se complementam: esta da a forma, aquela da o conteudo.

---

## Anti-padroes (o que estraga a captura)

- Pular a Fase 0 e descobrir o 2FA so na hora de logar (trava tudo).
- `goto`/reload pos-login num sistema cuja sessao nao sobrevive (perde a sessao, cai no login).
- `goback` demais: cai em `about:blank` e trava a navegacao (sem goForward). Voltar pra
  home por CLIQUE, nao por goback.
- Dedupar telas por URL numa SPA (a url fica "/" e voce pula tudo). Dedupar por ROTULO.
- Deixar screenshot/manifest com PII entrar no pacote. Sanitizar SEMPRE antes de zipar.
- Percorrer fluxo que grava dado (cadastro, publicar pagina, enviar msg) na conta do cliente.
- Workspace dentro de repo git (vaza PII e credencial no historico).
- Rodar `driver.mjs` pesado em foreground (morre no cap de 2min do Bash).

## Referencias

- `references/pre-flight.md` - a checklist de pre-verificacoes, item a item, com comandos.
- `references/2fa-email.md` - as 3 vias de resolver o codigo por email + como decidir.
- `references/gotchas.md` - catalogo de armadilhas medidas (auth, navegacao, captura, PII).
- `references/pii-sanitizacao.md` - protocolo de privacidade no empacotamento.
- `references/blueprint-template.md` - esqueleto do BLUEPRINT-<SISTEMA>.md.

## Notas

- PT-BR com acentuacao correta; sem travessao (em-dash).
- Scripts sao TEMPLATES: parametrizados por env, com defaults que cobrem B2C e formularios
  comuns. Ajustar os seletores (`CAP_*_SEL`) ao sistema-alvo depois do recon.
- Caso-exemplo completo: Clinicorp (2FA email + nav por clique) e Dietbox (B2C + goto).
