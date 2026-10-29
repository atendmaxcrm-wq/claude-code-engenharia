---
name: rea
description: Instala e opera o REA (rea-agents, https://github.com/morluto/rea, MIT) no projeto para engenharia reversa - pacote/binario, app Electron/JS, bundle web e sistema web logado (endpoints e forma de payload via HAR, DOM/a11y/storage da pagina viva via CDP). Instalacao LOCAL ao projeto (sem nada global) + MCP no .mcp.json do projeto + a skill oficial reverse-engineer-anything. Traz as armadilhas medidas em captura real (heap do analyze-web-bundle, recordHar estourando memoria, senha gravada no HAR, pkill que mata o shell). Use quando o usuario disser "usa o REA", "engenharia reversa", "descobrir os endpoints/payloads desse sistema", "como esse app funciona por dentro", "decompilar", ou junto da capturar-logica-saas para ir alem do que a tela mostra.
---

# REA no projeto

O REA e uma CLI + servidor MCP de engenharia reversa (207 ferramentas). Esta skill cuida de
INSTALAR no projeto e de como usar sem derrubar a maquina. O "como investigar" de verdade esta na
skill oficial dele, `reverse-engineer-anything`, que vem dentro do pacote npm.

## 1. Instalar (local ao projeto, uma vez)

```bash
npm init -y >/dev/null 2>&1 || true            # so se o projeto ainda nao tem package.json
npm install --save-dev rea-agents@latest --ignore-scripts
npx rea --version

# skill oficial (instrucoes de investigacao) para dentro do projeto
cp -r node_modules/rea-agents/skills/reverse-engineer-anything .claude/skills/
```

MCP SO no projeto (o `rea setup` e o `rea mcp add` gravam no escopo do USUARIO, valendo para
todos os projetos da maquina; e o `rea mcp add` NAO tem `--dry-run`, ele aplica na hora). Acrescente
ao `.mcp.json` da raiz:

```json
{ "mcpServers": { "rea": { "command": "node", "args": ["<RAIZ_DO_PROJETO>/node_modules/rea-agents/scripts/rea.mjs", "--mcp"] } } }
```

Reabrir o Claude Code no projeto para o MCP carregar. Sem o MCP, tudo funciona pela CLI (`npx rea <comando>`).
Diagnostico: `npx rea doctor --client claude_code`. Ghidra/IDA/Hopper/JADX so sao precisos para
binario nativo/Android; JavaScript e web nao precisam de motor nenhum.

## 2. Receita para sistema web logado (testada)

O REA nao faz login. Divida o trabalho:

1. **Nosso Playwright faz o login** (e o 2FA; ver skill capturar-logica-saas) e grava SO a API em
   ndjson com `scripts/gravador-api.mjs` (`gravarApi(ctx, { arquivo, hostRe })`).
2. `python3 .claude/skills/rea/scripts/ndjson2har.py api.ndjson api.har` converte para HAR 1.2.
3. `npx rea inspect-web-network-capture api.har har` lista endpoints + forma de payload.
4. Pagina viva: `.claude/skills/rea/scripts/cdp.sh 9333 <url>` sobe um Chrome com CDP em 127.0.0.1;
   depois `npx rea list-browser-targets` e `npx rea inspect-web-page` (DOM, a11y, scripts, storage;
   o REA redige valores sensiveis sozinho).

## 3. Armadilhas medidas (nao repetir)

- **`rea analyze-web-bundle` estourou 4 GB de heap** numa pagina de login simples. Nao rodar sem
  limite de memoria; prefira os comandos de inspecao pontual.
- **`recordHar` do Playwright guarda TUDO na memoria** ate o fim: 4,6 GB e OOM em 15 min. Por isso
  o `gravador-api.mjs` escreve em disco, uma linha por chamada, so xhr/fetch.
- **O gravador pegou a SENHA** no corpo do `auth/signin`. O gravador ignora rotas de
  auth/login/verify/2FA/token e tira `authorization`/`cookie` dos cabecalhos. Confira o `ignorarRe`
  para o sistema alvo antes de gravar.
- **`inspect-web-network-capture` tem heap fixo de ~192 MB**: HAR grande morre. Filtre antes
  (ex.: so as escritas, `method != GET`) e passe o arquivo menor.
- **Sistema alvo pode limitar carregamento de PAGINA** (HTML) e nao a API: navegue pelo roteador do
  SPA (`$router.push` / `history.pushState`), nunca `page.goto` em lote.
- **`pkill -f "remote-debugging-port=9333"` mata o PROPRIO shell** (o padrao casa com a linha de
  comando do pkill). Use `pgrep -f "port=933[3]" | xargs -r kill`.
- **Maquina compartilhada com producao**: rode REA e Chrome com teto de CPU/memoria (ex.:
  `systemd-run --scope -p CPUQuota=200% -p MemoryMax=6G -- npx rea ...`, ou o wrapper do projeto se
  ele tiver um).

## 4. Limites eticos e de conta

- Credencial do sistema alvo so por variavel de ambiente, nunca em arquivo nem no repo.
- Read-only por padrao. Nada que mande mensagem, cobranca ou convite para terceiro real.
- Respeite os termos do sistema alvo e o `DISCLAIMER.md` do REA: so engenharia reversa autorizada
  (conta propria, software proprio, pesquisa permitida).
