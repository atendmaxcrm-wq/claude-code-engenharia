# Claude Code Engenharia

Sistema de engenharia profissional para Claude Code -- memoria persistente com pgvector, hooks de protecao, 19 skills, agentes especializados e workflows automaticos.

Construido ao longo de 50+ sessoes de desenvolvimento real. Custo: ~R$ 0,10/mes.

---

## O que e

Claude Code Engenharia organiza todo o conhecimento, protecoes e automacoes do seu projeto em 5 pilares:

| Pilar | O que faz |
|-------|-----------|
| **Memoria** | Armazena decisoes, padroes e gotchas em pgvector com busca semantica automatica |
| **Skills** | 19 skills especializadas que ensinam Claude a executar tarefas complexas com consistencia |
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
| 19 skills organizadas | 4 categorias: core, frontend, backend, workflow -- cada skill e um diretorio com SKILL.md + exemplos |
| 10 commands | Workflows padronizados: /commit, /review-pr, /deploy, /atualizar-memoria, entre outros |
| 4 agentes especializados | dev (implementacao), reviewer (code review), investigador (debug), arquiteto (decisoes tecnicas) |
| 5 rules com roteador | Roteador inteligente ativa apenas regras relevantes por tipo de arquivo ou contexto |
| Custo minimo | text-embedding-3-small da OpenAI: ~$0.02/1M tokens, estimativa real ~R$ 0,10/mes |
| Instalacao modular | Escolha entre core (sem banco), standard (com skills) ou full (pgvector + MCP) |

---

## Instalacao rapida

```bash
npx claude-code-engenharia
```

O instalador interativo guia voce pela escolha do modulo e configuracao.

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
- Chave de API da OpenAI (para embeddings text-embedding-3-small)

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

| Categoria | Skill | O que faz |
|-----------|-------|-----------|
| **Core** | error-handling | Padroes de tratamento de erro consistentes |
| **Core** | testing | Estrategias de teste (unit, integration, e2e) |
| **Core** | code-review | Checklist de review automatizado |
| **Core** | refactoring | Tecnicas de refatoracao segura |
| **Core** | documentation | Geracao de docs tecnicos |
| **Frontend** | component-design | Arquitetura de componentes React |
| **Frontend** | styling | Padroes CSS/Tailwind |
| **Frontend** | accessibility | Checklist WCAG e a11y |
| **Frontend** | performance | Otimizacao de bundle e rendering |
| **Frontend** | animation | GSAP, Framer Motion, scroll-driven |
| **Backend** | api-design | RESTful patterns e versionamento |
| **Backend** | database | Queries, migrations, indices |
| **Backend** | auth | Autenticacao e autorizacao |
| **Backend** | caching | Estrategias de cache |
| **Backend** | monitoring | Logs, metricas, alertas |
| **Workflow** | git-workflow | Branch strategy e conventional commits |
| **Workflow** | ci-cd | Pipelines de build e deploy |
| **Workflow** | debugging | Metodologia sistematica de debug |
| **Workflow** | ai-prompt-builder | Construcao de system prompts para agentes IA |

---

## Custo

O modulo full usa `text-embedding-3-small` da OpenAI para gerar embeddings das memorias.

| Metrica | Valor |
|---------|-------|
| Modelo | text-embedding-3-small |
| Preco | $0.02 por 1M tokens |
| Tokens por memoria | ~200-500 tokens |
| Memorias tipicas/mes | ~100-500 |
| **Custo estimado** | **~$0.02/mes (~R$ 0,10)** |

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
