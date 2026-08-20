# Gotchas medidos (Clinicorp + Dietbox)

Armadilhas reais, todas medidas em campo. Agrupadas por fase.

## Autenticacao

- **Sessao que morre em reload** (Clinicorp): o token vive em memoria/sessionStorage; cookie
  sozinho nao basta. Qualquer `goto`/reload pos-login volta pra `/auth` e PERDE a sessao. =>
  login + captura no MESMO processo (browser vivo); navegar SO por clique;
  `CAP_SESSION_SURVIVES_RELOAD=0`. Ao FECHAR o processo, a sessao morre.
- **Sessao que sobrevive** (Dietbox): auth por cookie JWT (~2h) => `goto` em rotas reais
  funciona, `storageState` reusavel, captura trivial. `CAP_SESSION_SURVIVES_RELOAD=1`.
- **Como descobrir qual e**: apos logar no run.mjs, mande `goto:<home>` pelo driver e veja o
  campo `loggedIn` do `_cmd-result.json`. `true` = sobrevive; caiu no login = nao sobrevive.
- **Codigo 2FA velho expira** (> ~5min): da "erro ao autenticar dispositivo, tente novamente".
  O run.mjs reenvia e pede outro (ate 6 tentativas).
- **Persistent context recusado** no passo "autenticar dispositivo": usar contexto
  NAO-persistente (o run.mjs ja usa `newContext`, nao `launchPersistentContext`).
- **Gmail conectado != caixa do codigo**: confirmar o destinatario real do codigo (ver 2fa-email.md).
- **Login em 2 passos** (usuario -> proximo -> senha): alguns B2C so mostram a senha depois de
  submeter o usuario. O run.mjs preenche o que achar e submete; se o campo senha nao existia na
  1a tela, ajustar o fluxo (submeter usuario primeiro).

## Navegacao

- **`goback` demais cai em `about:blank`** e trava a navegacao (nao ha goForward). NAO usar
  goback pra "voltar pra home". Voltar por CLIQUE no item "Inicio"/"Home".
- **Menu global costuma ser TOGGLE** e as vezes so abre a partir de "/" (home). Em rotas
  internas o botao superior-esquerdo pode ser outro toggle (ex.: painel de relatorios), nao o
  menu. Voltar pra home antes de abrir o menu.
- **SPA mantem a url "/"** na maioria dos modulos: dedupar telas por URL PULA tudo. Dedupar por
  ROTULO. So algumas telas viram rota real (ex.: /reports, /management/users, /calendar).
- **Modal de boas-vindas bloqueia cliques** (ex.: "Conheca a nova Agenda"): fechar antes
  (o run.mjs tenta varios botoes de dismiss; se aparecer um novo, adicionar ao dismissModals).
- **Modal de "criar X" nao fecha no dismiss generico** e enquanto aberto BLOQUEIA tudo (as
  telas seguintes viram o modal). Fechar com o botao Cancelar especifico.

## Captura

- **run.mjs ZERA o manifest a cada sessao** (comeca vazio). Se precisar relogar no meio (ex.:
  pra abrir 1 prontuario), o novo run SOBRESCREVE o manifest anterior. Salvar o manifest antigo
  antes (copiar pra um staging) e reconciliar.
- **driver.mjs em foreground morre no cap de 2min do Bash** com 10+ cliques lentos (~30s cada).
  Rodar em `run_in_background=true` OU em lotes curtos (5-8 comandos).
- **Colunas de relatorio so renderizam com dados no periodo** (default Total 0). Sem a base
  real do cliente, documentar a ESTRUTURA (filtros, categorias), nao os valores. Alguns nomes de
  relatorio nao navegam no clique (flaky) - tentar por rota se souber.
- **Ler o manifest (texto) e barato; abrir imagem e caro.** Preferir o manifest pra mapear
  estrutura; abrir screenshot so pra confirmar layout/aparencia.

## PII (ver pii-sanitizacao.md pro protocolo)

- **Modal sobre lista vaza o fundo**: "Adicionar paciente"/"Novo cliente" abre POR CIMA da
  lista e os nomes atras aparecem no screenshot. Conferir o FUNDO de todo shot de modal;
  excluir os que vazam.
- **Sidebar carrega lista de chat/clientes** (100+ nomes) em navLinks/listItems de TODA tela.
  O sanitizar-manifest.mjs DROPA esses dois campos.
- **Pagina publica do profissional/lead**: abrir a tela de ENTRADA e ok; NAO percorrer os
  passos que criam um lead/registro real, e NAO publicar a pagina (seria escrita na conta).
