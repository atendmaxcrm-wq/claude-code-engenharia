# Checklist de Análise (GPT-Optimized)

Use este checklist para avaliar prompts e bases de conhecimento existentes de agentes. Marque cada item como PASSOU, PARCIAL ou FALHOU, depois priorize melhorias por impacto.

---

## Análise do Prompt

### Estrutura e Organização
- [ ] Usa headers Markdown (`#`, `##`) para seções, com XML apenas para limites de conteúdo (exemplos, variáveis)
- [ ] Seções em ordem lógica (identidade → regras → tools → fluxo → princípios → exemplos → variáveis → lembretes finais)
- [ ] Nenhuma seção extrapola seu escopo
- [ ] Comprimento total adequado (até ~3000 tokens para simples, ~5000 para complexos)
- [ ] Instruções-chave aparecem tanto no INÍCIO quanto no FIM do prompt

### Identidade e Tom
- [ ] Nome, função, empresa e personalidade do agente claramente definidos
- [ ] Regras de tom são CONCRETAS e acionáveis
- [ ] Limites de comprimento de mensagem especificados
- [ ] Instrução de auto-apresentação é explícita
- [ ] Objetivo principal declarado

### Regras Críticas
- [ ] Lista de regras é concisa (5-8 no máximo)
- [ ] Cada regra passa no teste de "dano real"
- [ ] Sem contradições entre regras
- [ ] Toda regra absoluta tem um fallback/saída de emergência (risco de fabricação GPT)

### Ferramentas
- [ ] Cada tool tem descrição clara de "quando usar"
- [ ] Sem ambiguidade entre tools
- [ ] Tratamento de falha de tools definido
- [ ] Instruções de tools incluem fallback para informação ausente

### Fluxo de Conversa
- [ ] Fluxo definido no nível de etapa, não de script
- [ ] Cada etapa tem objetivo claro
- [ ] Produtos/opções listados pelo nome completo (nunca "...")
- [ ] Instrução de se apresentar primeiro incluída

### Lógica de Decisão
- [ ] Usa princípios e heurísticas (não blocos if/then exaustivos)
- [ ] Inclui instrução explícita de raciocínio passo a passo (GPT não raciocina por padrão)
- [ ] Framework de persistência (3 tentativas) definido como princípio
- [ ] Hierarquia de prioridades definida

### Exemplos (Few-Shot)
- [ ] Pelo menos 2 exemplos canônicos de conversa completos
- [ ] Exemplos mostram a tool think em ação
- [ ] Exemplos mostram busca na base de conhecimento
- [ ] Inclui instrução explícita para VARIAR fraseado dos exemplos (risco verbatim GPT)
- [ ] Exemplos cobrem caminhos diferentes (feliz, objeção, escalação)

### Checks Específicos de GPT
- [ ] ALL CAPS usado moderadamente (GPT hiper-foca em CAPS)
- [ ] Nenhuma regra absoluta sem instrução de fallback
- [ ] Instrução explícita de raciocínio presente ("pense passo a passo")
- [ ] Instrução de variação para exemplos presente
- [ ] Seção de lembretes finais existe no fim do prompt

### Edge Cases
- [ ] Define comportamento para mídia não suportada (áudio, imagens)
- [ ] Define comportamento para mensagens fora de tópico
- [ ] Define comportamento para tentativas de manipulação
- [ ] Define comportamento para leads retornando após dias
- [ ] Define comportamento para mensagens vazias ou incompreensíveis

---

## Análise da Base de Conhecimento

### Organização
- [ ] Headers de seção claros com títulos descritivos
- [ ] Tags de busca em cada seção correspondendo aos padrões de busca do agente
- [ ] Convenção de nomenclatura consistente (OBJEÇÃO:, FAQ:, SCRIPT:, etc.)
- [ ] Um tópico por seção
- [ ] Agrupamento lógico (info empresa, serviços, objeções, FAQs, temporal)

### Qualidade de Conteúdo
- [ ] Scripts escritos em linguagem conversacional natural
- [ ] Scripts são adaptáveis (não recitações rígidas palavra por palavra)
- [ ] Métricas de autoridade consistentes entre menções
- [ ] Cada seção de objeção inclui: script, reforços e transição
- [ ] Informação sensível tem instruções claras de manuseio

### Completude
- [ ] Toda informação factual da empresa presente (endereço, horários, contatos)
- [ ] Todos os serviços/produtos descritos
- [ ] Opções de pagamento cobertas
- [ ] Objeções comuns têm scripts (preço, medo, tempo, concorrência, "vou pensar")
- [ ] FAQs cobrem as perguntas mais comuns de conversas reais
- [ ] Informação temporal tem seção própria

### Separação de Responsabilidades
- [ ] Sem instruções comportamentais na KB (pertencem ao prompt)
- [ ] Sem lógica de decisão na KB (sem regras if/then)
- [ ] Scripts não incluem lógica "se o lead disser X, diga Y"
- [ ] Todos os fatos referenciados no prompt são sourced da KB

### Manutenibilidade
- [ ] Data de versão anotada
- [ ] Seções temporais claramente marcadas para atualizações regulares
- [ ] Estrutura suporta adicionar novas seções sem reestruturar

---

## Matriz de Prioridade

| Prioridade | Descrição | Ação |
|-----------|-----------|------|
| P0 - Crítico | Causa comportamento incorreto ou dano ao negócio (info errada, guardrails ausentes, risco de fabricação) | Corrigir imediatamente |
| P1 - Alto | Degrada significativamente a qualidade (exemplos ausentes, estrutura ruim, prompt muito longo) | Corrigir na próxima iteração |
| P2 - Médio | Reduz eficácia mas não quebra nada (edge cases faltando, formatação subótima) | Planejar melhoria |
| P3 - Baixo | Polimento e otimização (wording levemente melhor, melhorias estruturais menores) | Endereçar quando conveniente |

---

## Template de Relatório de Análise

Ao apresentar resultados de análise, use esta estrutura:

```markdown
# Análise do Agente: [Nome do Agente]

## Resumo
Visão geral do propósito do agente e estado atual.

## Pontos Fortes (O Que Está Funcionando Bem)
- Ponto forte 1: Por que importa
- Ponto forte 2: Por que importa

## Melhorias Prioritárias

### P0 — Crítico
1. [Issue]: [Impacto] → [Correção recomendada]

### P1 — Alto
1. [Issue]: [Impacto] → [Correção recomendada]

### P2 — Médio
1. [Issue]: [Impacto] → [Correção recomendada]

### P3 — Baixo
1. [Issue]: [Impacto] → [Correção recomendada]

## Plano de Ação Recomendado
Lista ordenada de mudanças a implementar, começando pelo maior impacto.
```
