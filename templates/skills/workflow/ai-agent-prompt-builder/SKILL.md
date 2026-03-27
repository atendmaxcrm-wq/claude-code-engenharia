---
name: ai-agent-prompt-builder
description: "Cria system prompts e bases de conhecimento de nível profissional para agentes de IA conversacionais (WhatsApp, chatbots, atendimento, vendas, agendamento). Otimizado para modelos GPT (OpenAI). Use esta skill sempre que o usuário quiser criar, analisar, melhorar ou reestruturar prompts para agentes de IA — especialmente agentes que interagem com clientes via plataformas de mensagem. Ativa em pedidos envolvendo: prompts de agente, system prompts para chatbots, automação de WhatsApp, comportamento de IA conversacional, criação de base de conhecimento, scripts de agentes de vendas, agentes de agendamento, agentes de atendimento, qualificação de leads, separação prompt + base de conhecimento, ou qualquer menção a tools como 'think', 'info_', 'resumo', 'transfere'. Também ativa quando o usuário compartilha um prompt existente e quer feedback, otimização ou reestruturação."
---

# AI Agent Prompt Builder (GPT-Optimized)

Cria e otimiza system prompts e bases de conhecimento para agentes de IA conversacionais em produção, rodando em modelos GPT (OpenAI), seguindo princípios comprovados de context engineering.

## Filosofia Central

O princípio central: **encontrar o menor conjunto possível de tokens de alto sinal que maximize a probabilidade do resultado desejado.** Para agentes conversacionais, isso significa ensinar o agente a PENSAR e DECIDIR, não O QUE dizer em cada cenário.

## Princípios Específicos do GPT

- **Markdown como estrutura principal** — Modelos GPT foram treinados extensivamente com Markdown e performam melhor com headers `#`, listas `-` e formatação padrão. Use XML tags apenas onde limites explícitos de conteúdo são necessários (exemplos, variáveis de runtime).
- **GPT segue instruções literalmente** — Seja explícito e específico. Não confie que o modelo vai inferir a intenção.
- **GPT não raciocina por padrão** — Chain-of-thought precisa ser induzido via prompt. Sempre inclua instruções explícitas de raciocínio ("pense passo a passo").
- **GPT pode ecoar exemplos literalmente** — Sempre instrua o agente a variar respostas e não repetir exemplos palavra por palavra.

## Quando Ler os Arquivos de Referência

Antes de iniciar qualquer trabalho, leia os arquivos de referência apropriados:

| Tarefa | Leia Primeiro |
|--------|--------------|
| Criar um agente novo do zero | `references/prompt-architecture.md` depois `references/knowledge-base-architecture.md` |
| Analisar/melhorar um prompt existente | `references/prompt-architecture.md` depois `references/analysis-checklist.md` |
| Criar/reestruturar uma base de conhecimento | `references/knowledge-base-architecture.md` |
| Build completo (prompt + KB) | Todos os três arquivos de referência |

## Workflow Rápido

### 1. Briefing (Entender o Agente)

Antes de escrever qualquer coisa, levante:
- **Identidade**: Quem é esse agente? Nome, função, personalidade
- **Plataforma**: WhatsApp, webchat, telefone, multi-canal?
- **Objetivo**: Qual é o objetivo principal de conversão?
- **Tools**: Que ferramentas/APIs o agente tem acesso?
- **Regras de negócio**: O que pode/não pode fazer?
- **Escalação**: Quando e como transfere para humanos?

### 2. Arquitetura (Separar Responsabilidades)

Todo agente tem dois documentos com propósitos distintos:

**System Prompt** → Ensina o agente COMO se comportar
- Identidade e personalidade
- Princípios de tomada de decisão e heurísticas
- Orientação de uso de ferramentas
- Fluxo de conversa (alto nível)
- Guardrails e limites

**Base de Conhecimento** → Fornece O QUE o agente precisa saber
- Fatos da empresa (endereço, horários, contatos)
- Detalhes de produtos/serviços
- Preços e informações de pagamento
- Scripts para objeções e edge cases
- FAQs e respostas prontas

A linha divisória: se muda quando o negócio atualiza informações, é base de conhecimento. Se muda quando você quer que o agente se comporte diferente, é prompt.

### 3. Build (Aplicar a Arquitetura)

Siga os padrões em `references/prompt-architecture.md` para o system prompt e `references/knowledge-base-architecture.md` para a KB. Princípios-chave:

- Use headers Markdown para clareza estrutural no prompt
- Use XML tags apenas para limites de conteúdo (exemplos, variáveis)
- Ensine princípios ao invés de prescrever scripts
- Inclua 2-3 exemplos canônicos de conversa (few-shot) com instrução explícita para variar fraseado
- Projete tools autocontidas e sem ambiguidade
- Mantenha dados temporais/voláteis na KB, não no prompt
- Inclua instruções explícitas de raciocínio (GPT não raciocina por padrão)

### 4. Revisão (Validar Qualidade)

Passe pelo `references/analysis-checklist.md` para verificar se prompt e KB atendem aos padrões de qualidade.

## Formato de Saída

Ao criar agentes, sempre entregue dois arquivos separados:
1. `prompt-[nome-agente].md` — O system prompt
2. `kb-[nome-agente].md` — A base de conhecimento

Ao analisar agentes existentes, entregue:
1. Documento de análise com pontos fortes, melhorias e ações prioritárias
2. Opcionalmente: versões reestruturadas do prompt e KB

## Assets

- `assets/prompt-template.md` — Template inicial para novos prompts de agente
- `assets/kb-template.md` — Template inicial para novas bases de conhecimento
