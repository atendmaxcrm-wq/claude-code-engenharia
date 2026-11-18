# Claude Code Engenharia

Sistema de engenharia profissional para Claude Code -- memoria persistente com pgvector, hooks de protecao, 56 skills, agentes especializados e workflows automaticos.

Construido ao longo de 50+ sessoes de desenvolvimento real. Custo: ~R$ 0,10/mes.

---

## O que e

Claude Code Engenharia organiza todo o conhecimento, protecoes e automacoes do seu projeto em 5 pilares:

| Pilar | O que faz |
|-------|-----------|
| **Memoria** | Armazena decisoes, padroes e gotchas em pgvector com busca semantica automatica |
| **Skills** | 56 skills especializadas que ensinam Claude a executar tarefas complexas com consistencia |
| **Commands** | 10 comandos padronizados para workflows recorrentes (commit, review, deploy, etc.) |
| **Rules** | 5 regras com roteador inteligente que ativa apenas as regras relevantes por contexto |
| **Hooks** | 3 hooks de protecao que interceptam comandos perigosos e injetam contexto automaticamente |

O resultado: Claude Code que lembra do projeto entre sessoes, segue padroes sem precisar repetir instrucoes, e se protege contra erros destrutivos.

---

## Features

| Feature | Descricao |
|---------|-----------|
| Memoria contextual | Busca pgvector automatica a cada mensagem -- contexto relevante injetado sem intervencao |
| 3 hooks de protecao | `block-destructive` (bloqueia git push --force, rm -rf), `contextual-memory` (busca automatica), `reinject-memory` (reinjeta apos compactacao) |
| 56 skills | cada skill e um diretorio com SKILL.md + scripts/exemplos; + 11 de terceiros por instalador separado |
| 10 commands | Workflows padronizados: /commit, /review-pr, /deploy, /atualizar-memoria, entre outros |
| 4 agentes especializados | dev (implementacao), reviewer (code review), investigador (debug), arquiteto (decisoes tecnicas) |
| 5 rules com roteador | Roteador inteligente ativa apenas regras relevantes por tipo de arquivo ou contexto |
| Custo minimo | Embeddings via Gemini (gemini-embedding-001, free tier generoso) por padrao; OpenAI text-embedding-3-small como fallback opcional |
| Instalacao modular | Escolha entre core (sem banco), standard (com skills) ou full (pgvector + MCP) |

---

## Instalacao rapida

```bash
git clone https://github.com/atendmaxcrm-wq/claude-code-engenharia.git
cd claude-code-engenharia
node install.js
```

O instalador interativo guia voce pela escolha do modulo e configuracao.

> **Nota:** o pacote ainda nao esta publicado no npm, entao `npx claude-code-engenharia` nao funciona. Use o clone manual acima.

---

## Instalacao para agentes (Claude Code, etc.)

Se voce e um agente pedindo instalacao, o instalador interativo trava em prompts que voce nao consegue responder. Use o modo nao-interativo:

```bash
git clone https://github.com/atendmaxcrm-wq/claude-code-engenharia.git /tmp/cce \
  && cd /tmp/cce \
  && node install.js --yes --module core --dir "$TARGET_PROJECT_DIR"
```

Flags:

| Flag | Efeito |
|------|--------|
| `--yes` (ou `-y`) | Pula o wizard. Usa defaults para todo campo. |
| `--module <core\|standard\|full>` | Escolhe o modulo. Default com `--yes`: `full`. |
| `--dir <path>` | Diretorio de instalacao. Default: cwd. |
| `--dry-run` | Lista o que seria criado, sem escrever. Rode antes pra auditar. |
| `--force` | Sobrescreve arquivos existentes no modo brownfield. |

Para modulo `full` (pgvector + embeddings), passe credenciais via env:

```bash
CCE_DB_PASSWORD=xxx OPENAI_API_KEY=sk-xxx \
  node install.js --yes --module full --dir "$TARGET_PROJECT_DIR"
```

Env vars aceitas: `CCE_DB_HOST`, `CCE_DB_PORT`, `CCE_DB_USER`, `CCE_DB_PASSWORD`, `CCE_DB_NAME`, `CCE_OPENAI_KEY` (ou `OPENAI_API_KEY`), `CCE_STACK`, `CCE_HEALTH_CHECK`, `CCE_LOG_COMMAND`.

**Verificacao pos-install** (o agente deve rodar isto antes de reportar "pronto"):

```bash
ls "$TARGET_PROJECT_DIR/.claude/hooks/" "$TARGET_PROJECT_DIR/.claude/skills/" 2>/dev/null
test -f "$TARGET_PROJECT_DIR/CLAUDE.md" && echo "CLAUDE.md OK"
```

Se algum desses nao existir, a instalacao falhou silenciosamente — investigue os logs do `install.js` ao inves de reportar sucesso.

---

## Atualizar uma VPS que ja tem o CCE

O `install.js` sem `--force` pula tudo que ja existe (nao atualiza skill nenhuma) e com `--force` sobrescreve `CLAUDE.md`, `memoria/` e settings com os templates. Para trazer so as skills novas/atualizadas sem mexer no resto:

```bash
git clone https://github.com/atendmaxcrm-wq/claude-code-engenharia.git /tmp/cce && cd /tmp/cce
node scripts/atualizar-skills.js --dir /root            # previa
node scripts/atualizar-skills.js --dir /root --apply    # backup .tar.gz + copia
bash terceiros/instalar.sh /root/.claude/skills         # skills de terceiros (opcional)
```

Skills que so existem na maquina ficam intactas. Reinicie o Claude Code depois. No modulo `full`, o passo 8 do `/atualizar-memoria` usa `node memory/scripts/importar-auto-memoria.js` (leva as auto-memorias do Claude Code para o pgvector).

---

## Modulos

| Recurso | Core | Standard | Full |
|---------|------|----------|------|
| Hooks de protecao | Sim | Sim | Sim |
| Rules com roteador | Sim | Sim | Sim |
| Commands padronizados | Sim | Sim | Sim |
| Agentes especializados | Sim | Sim | Sim |
| Memoria markdown | Sim | Sim | Sim |
| 19 Skills | -- | Sim | Sim |
| CLAUDE.md template | -- | Sim | Sim |
| pgvector + embeddings | -- | -- | Sim |
| MCP Server aios-memory | -- | -- | Sim |
| Busca semantica automatica | -- | -- | Sim |
| **Requer PostgreSQL** | Nao | Nao | Sim |
| **Requer OpenAI key** | Nao | Nao | Sim |

**Core** e suficiente para a maioria dos projetos. **Full** e recomendado para projetos de longa duracao com muitas sessoes.

---

## Pre-requisitos

**Todos os modulos:**
- Node.js 18+
- jq (para manipulacao de JSON)
- Claude Code instalado e configurado

**Apenas para modulo full:**
- PostgreSQL 16+ com extensao pgvector 0.8+
- Chave de API do Gemini (para embeddings gemini-embedding-001, 1536 dims) -- OpenAI text-embedding-3-small fica como fallback opcional

---

## Como funciona

```
Mensagem do usuario
      |
      v
[Hook contextual-memory.js]
      |
      +-- Busca keyword (ILIKE ~50ms)
      +-- Busca semantica (embedding ~400ms)
      |
      v
Contexto relevante injetado automaticamente
      |
      v
Claude responde com conhecimento do projeto
```

A cada mensagem enviada, o hook `contextual-memory` extrai palavras-chave e busca memorias relevantes no banco pgvector. O contexto encontrado e injetado no prompt antes de Claude processar a mensagem. Isso significa que Claude "lembra" de decisoes passadas, erros conhecidos e padroes do projeto sem que voce precise repetir nada.

No modo core/standard (sem PostgreSQL), a memoria funciona via arquivos markdown com busca por texto.

---

## Estrutura

Apos a instalacao, os seguintes arquivos sao adicionados ao seu projeto:

```
.claude/
  hooks/
    block-destructive.js      # Bloqueia comandos perigosos (git push --force, rm -rf /)
    contextual-memory.js       # Busca memorias relevantes a cada mensagem
    reinject-memory.js         # Reinjeta contexto apos compactacao de sessao
  rules/
    router.md                  # Roteador que ativa regras por contexto
    backend.md                 # Regras para arquivos backend
    frontend.md                # Regras para arquivos frontend
    database.md                # Regras para queries e migrations
    general.md                 # Regras gerais do projeto
  commands/
    commit.md                  # Workflow de commit padronizado
    review-pr.md               # Code review automatizado
    deploy.md                  # Checklist de deploy
    atualizar-memoria.md       # Atualiza memorias do projeto
    ... (10 commands total)
  agents/
    dev.md                     # Agente implementador
    reviewer.md                # Agente revisor de codigo
    investigador.md            # Agente de debug e investigacao
    arquiteto.md               # Agente de decisoes tecnicas
  skills/                      # 19 skills (modulo standard+)
    core/
    frontend/
    backend/
    workflow/
memoria/
  insights.md                  # Decisoes e padroes aprendidos
  progresso.md                 # Estado atual do projeto
  sistema/
    database-schema.md         # Schema do banco
    api-endpoints.md           # Endpoints da API
    troubleshooting.md         # Problemas conhecidos
    changelog.md               # Historico de mudancas
CLAUDE.md                      # Instrucoes do projeto (modulo standard+)
```

---

## Skills incluidas

56 skills, instaladas em `.claude/skills/` da raiz escolhida (lista gerada do manifesto do instalador):

| Skill | O que faz |
|-------|-----------|
| `agent-teams` | Orquestracao multi-agent com Agent Teams nativo do Claude Code. |
| `ai-agent-prompt-builder` | Cria system prompts e bases de conhecimento de nível profissional para agentes de IA conversacionais (WhatsApp, chatbots, atendimento,... |
| `ai-agent-prompt-builder-gemini` | Cria system prompts e bases de conhecimento profissionais para agentes de IA conversacionais (WhatsApp, atendimento, vendas,... |
| `analise-impacto` | Analise obrigatoria antes de editar arquivos core. |
| `api-patterns` | Padroes de endpoints da API. |
| `atualizar-memoria` | Atualizar arquivos de memoria do projeto com mudancas da sessao. |
| `auditar-fidelidade` | Auditoria EXAUSTIVA de fidelidade e completude entre uma REFERENCIA (mockup HTML/SPA, print, video ou site) e um app JA IMPLEMENTADO,... |
| `capturar-logica-saas` | Captura a LOGICA e a UX de um SaaS de referencia (sistema logado, atras de credenciais) e produz um BLUEPRINT navegavel - "como... |
| `clonar-design` | Extrair design system completo de um site (cores, tipografia, animacoes, layout, screenshots, video). |
| `clonar-site` | Reconstruir um site inteiro pixel-perfect como projeto Next.js moderno. |
| `codar-em-ondas` | Pipeline de CODIGO em ondas (o motor que constroi o sistema real, irmao da pipeline-fiel que faz os mockups). |
| `code-review` | Checklist de revisao de codigo. |
| `commit` | Commits convencionais. |
| `component-builder` | Como criar componentes neste projeto. |
| `create-pr` | Pull requests com descricoes claras. |
| `criacao-form` | Cria formulario/diagnostico interativo com wizard carousel, rating por estrelas, analise por IA com streaming e pagina de resultado rica. |
| `database-query` | Padroes de queries SQL e schema PostgreSQL. |
| `deploy` | Deploy completo (restart PM2 + verificacao). |
| `design-system` | Padroes visuais do projeto. |
| `entrega-verificada` | Ciclo de entrega verificada - monta uma SPEC com todo o plano, executa em ETAPAS, testa cada etapa em CÓDIGO e apertando os botões... |
| `extrair-design-imagem` | Extrai um design system completo (cores com hex + papel, tipografia hierarquica, tokens, combos de contraste, decisoes notaveis) a... |
| `frontend-design` | Design UI excepcional, nao-generico. |
| `gsap-animations` | Implementa animacoes avancadas com GSAP (100% gratuito) e AnimeJS. |
| `interaction-patterns` | Como as coisas se movem. |
| `investigar-bug` | Investigar e diagnosticar um bug reportado no sistema. |
| `migrar-componente` | Migrar lib ou refatorar implementacao de componente. |
| `modern-ui-design` | Principios universais de design moderno. |
| `notebooklm` | Controla o Google NotebookLM pela linha de comando (biblioteca nao oficial notebooklm-py) - cria notebooks, adiciona fontes (URL, PDF,... |
| `nova-feature` | Planejar e implementar nova feature com analise de impacto. |
| `performance-audit` | Auditoria de performance. |
| `pesquisar-tech` | Pesquisar e avaliar tecnologias/libs antes de implementar. |
| `pipeline-fiel` | Pipeline completo e opinado para replicar um sistema em MOCKUPS fieis, modulo a modulo em ONDAS. |
| `planejar-feature` | Workflow de 6 fases para planejar features, com suporte a Agent Teams para features grandes. |
| `postgres-best-practices` | PostgreSQL otimizado. |
| `proposta-workana` | Cria propostas vencedoras para projetos do Workana. |
| `rea` | Instala e opera o REA (rea-agents, https://github.com/morluto/rea, MIT) no projeto para engenharia reversa - pacote/binario, app... |
| `react-best-practices` | 57 regras de performance React. |
| `replicar-operador-trade` | Pipeline validado para replicar o METODO de um operador de mercado (trader/day trade/opcoes) que ensina em video/Instagram,... |
| `replicar-sistema` | Pipeline completo para replicar o design de qualquer sistema a partir de foto/print OU VIDEO (screen recording) e construir um sistema... |
| `resumo-sessao` | Gerar resumo completo da sessao de trabalho atual. |
| `safari-check` | Auditoria de compatibilidade Safari iOS/macOS. |
| `scraping` | Fazer scraping completo de um site (texto + imagens + videos + base de conhecimento). |
| `scraping-insta` | Baixa posts/reels de um perfil Instagram, transcreve com Whisper, analisa hooks/estrutura/CTAs e destila um padrao viral replicavel. |
| `site-3d` | Criar sites 3D premium nivel Awwwards (cena/objeto 3D protagonista que reage a scroll e mouse), com React Three Fiber + drei +... |
| `site-elite` | Criar sites premium nivel Asimov/Linear/Vercel/Aura.build. |
| `site-elite-cinema` | Adiciona camada cinematografica ao /site-elite. |
| `spec-plan` | Cria design tecnico versionado (specs/<slug>/design.md) a partir de requirements.md ja existente. |
| `spec-specify` | Cria spec de requisitos versionada (specs/<slug>/requirements.md) ANTES de qualquer codigo ou decisao tecnica. |
| `systematic-debugging` | Debug sistematico em 4 fases. |
| `test-driven-development` | RED-GREEN-REFACTOR. |
| `testar-agente` | Testa um agente de IA nosso de ponta a ponta com persona simulado, leitura do resultado GRAVADO e juizes independentes contra gabarito. |
| `text-humanizer` | Reescreve textos gerados por IA para soar naturais e humanos, evitando detecção por ferramentas como GPTZero, Turnitin, Originality.ai e... |
| `upgrade-visual` | Transforma qualquer sistema com 'cara de sistema' em produto premium. |
| `verification-before-completion` | Proibe dizer "pronto" sem evidencia. |
| `video-motion` | Gera vídeos curtos de MOTION GRAPHICS por código (não é edição de cortes nem vídeo gerado por IA) para QUALQUER assunto - filme de... |
| `yt-search` | Busca videos no YouTube pelo terminal e devolve lista estruturada (titulo, canal, views, duracao, data, URL), com filtro de recencia. |

### Skills de terceiros (instalador separado)

Usamos tambem 11 skills de outros autores (Felipe Borges / @FelipeBorgesFalaIA e `pbakaus/impeccable`): `reel`, `criador-de-carrosseis-simples`, `gerar-imagem`, `super-copy`, `loop-de-design` (automaticas) e `motion-graphics`, `motion-por-referencia`, `prompts-de-motion`, `scrollar`, `showreel-interface`, `impeccable` (manuais: `disable-model-invocation`, chame com `/nome`). O codigo delas **nao fica neste repo** (algumas nao tem licenca publicada): o script baixa cada uma do repo oficial no commit fixado em `terceiros/skills.tsv` e aplica so os nossos ajustes.

```bash
bash terceiros/instalar.sh /root/.claude/skills            # todas
bash terceiros/instalar.sh /root/.claude/skills reel        # so algumas
bash terceiros/instalar.sh /root/.claude/skills --com-whisper-gemini   # + whisper-cli que transcreve pelo Gemini (a /reel usa)
ATUALIZAR=1 bash terceiros/instalar.sh /root/.claude/skills # pega o HEAD atual de cada repo
```

---

## Custo

O modulo full usa `gemini-embedding-001` do Gemini para gerar embeddings das memorias (1536 dims, L2-normalizado). OpenAI `text-embedding-3-small` continua disponivel como fallback (defina `EMBEDDING_PROVIDER=openai`).

| Metrica | Valor |
|---------|-------|
| Modelo padrao | gemini-embedding-001 (1536 dims) |
| Fallback | text-embedding-3-small (OpenAI) |
| Selecao | `EMBEDDING_PROVIDER=gemini\|openai` (auto: Gemini se houver GEMINI_API_KEY) |
| Tokens por memoria | ~200-500 tokens |
| Memorias tipicas/mes | ~100-500 |
| **Custo estimado** | **~zero (Gemini free tier cobre embedding com folga)** |

Os modulos core e standard nao tem custo adicional (usam busca por texto em arquivos markdown).

---

## Documentacao completa

Para documentacao detalhada de cada componente, consulte:

- [Sistema de Engenharia](docs/SISTEMA-ENGENHARIA.md) -- Arquitetura completa e decisoes de design
- [Guia de Instalacao](docs/INSTALACAO.md) -- Passo a passo detalhado
- [Referencia de Skills](docs/SKILLS.md) -- Documentacao de cada skill
- [Referencia de Hooks](docs/HOOKS.md) -- Como cada hook funciona
- [FAQ](docs/FAQ.md) -- Perguntas frequentes

---

## Licenca

MIT -- veja [LICENSE](LICENSE) para detalhes.
