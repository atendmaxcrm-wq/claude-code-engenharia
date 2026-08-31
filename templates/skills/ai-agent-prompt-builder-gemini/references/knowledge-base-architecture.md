# Referência de Arquitetura de Base de Conhecimento

> **Nota:** Bases de conhecimento são agnósticas de modelo — são servidas via RAG/tools, não embarcadas no system prompt. O formato e estrutura abaixo funcionam identicamente para GPT, Claude ou qualquer outro LLM. A única consideração específica de GPT é garantir que as tags de busca correspondam às palavras-chave que o agente vai usar nas chamadas de tools.

---

## Índice

1. [O Papel da Base de Conhecimento](#1-o-papel-da-base-de-conhecimento)
2. [Princípios de Organização](#2-princípios-de-organização)
3. [Design de Seções](#3-design-de-seções)
4. [Estrutura Otimizada para Busca](#4-estrutura-otimizada-para-busca)
5. [Diretrizes de Conteúdo](#5-diretrizes-de-conteúdo)
6. [O Que Pertence Aqui vs. No Prompt](#6-o-que-pertence-aqui-vs-no-prompt)
7. [Estratégia de Manutenção](#7-estratégia-de-manutenção)
8. [Template Completo de KB](#8-template-completo-de-kb)

---

## 1. O Papel da Base de Conhecimento

A base de conhecimento é a memória factual do agente — tudo que o agente precisa SABER mas não deveria memorizar no system prompt. É acessada através de uma tool de retrieval (como `info_[empresa]`) e serve como fonte única de verdade para toda informação factual.

O insight-chave: o system prompt ensina o agente a PENSAR e DECIDIR. A base de conhecimento fornece o que ele precisa SABER e DIZER. Quando o agente precisa de um fato, script ou protocolo específico, ele busca na base ao invés de confiar no system prompt.

Esta arquitetura significa:
- Atualizações de negócio só requerem mudanças na KB (sem mexer no prompt)
- O prompt fica enxuto e focado em comportamento
- O agente sempre busca informação atualizada
- Scripts e respostas são gerenciados em um só lugar

---

## 2. Princípios de Organização

### Use Headers Claros com Tags

Estruture a KB para que quando o agente buscar um tópico, a seção relevante seja inequívoca. Use headers e tags que correspondam à forma como o agente vai buscar.

```markdown
## OBJEÇÃO: Preço / "Quanto custa?"
Tags: preço, caro, valor, investimento, dinheiro, orçamento, quanto custa

## OBJEÇÃO: Medo / "Tenho medo do procedimento"
Tags: medo, receio, dor, ansiedade, trauma, nervoso

## FAQ: Formas de Pagamento
Tags: pagamento, parcela, cartão, pix, financiamento, convênio
```

As tags servem como âncoras de busca — quando o agente busca "objeção medo", encontra a seção certa imediatamente.

### Agrupe Conteúdo Relacionado

Organize por como o agente vai BUSCAR, não por como um humano leria:

**Boa estrutura (orientada a busca):**
```
1. INFO DA EMPRESA (endereço, horários, contatos, estacionamento)
2. EQUIPE E AUTORIDADE (credenciais, números, filosofia)
3. SERVIÇOS (lista de serviços/produtos com descrições)
4. PAGAMENTO (opções, parcelamento, política de convênio)
5. TECNOLOGIA E DIFERENCIAIS
6. OBJEÇÕES (uma seção por tipo de objeção, com tags)
7. TÉCNICAS DE VENDA (perguntas SPIN, gatilhos, scripts de fechamento)
8. OFERTAS ESPECIAIS (convite experiência, promoções)
9. FAQs (perguntas comuns com respostas)
10. TEMPORAL (feriados, fechamentos, restrições de agenda)
```

### Um Conceito Por Seção

Cada seção deve cobrir UM tópico completamente. Nunca divida informação relacionada entre múltiplas seções — o agente pode encontrar apenas uma delas.

---

## 3. Design de Seções

### Anatomia de uma Boa Seção de KB

```markdown
## OBJEÇÃO: Medo do Procedimento
Tags: medo, receio, dor, ansiedade, trauma, nervoso, assustado

### Contexto
Leads expressando medo são comuns e devem ser recebidos com validação antes de informação. Nunca minimize a preocupação.

### Script Principal
"É totalmente compreensível sentir isso. A gente escuta isso com frequência, e justamente por isso tudo no nosso atendimento é pensado pro seu conforto e segurança desde o primeiro momento."

### Linhas de Reforço
- "Nossa equipe entende que cada pessoa tem seu tempo."
- "Nosso ambiente é pensado pra acolher quem chega com receio."

### Transição para Agendamento
"Justamente por isso a avaliação existe — pra você conhecer a equipe, ver o ambiente e se sentir confortável antes de decidir qualquer coisa."
```

Cada seção fornece:
1. **Tags** para matching de busca
2. **Contexto** para o agente entender quando/como usar este conteúdo
3. **Script Principal** — a resposta principal
4. **Variações/Reforços** — linhas alternativas para follow-up
5. **Transição** — como avançar para a próxima etapa após endereçar o tópico

### Scripts vs. Regras

A KB contém SCRIPTS (o que dizer). O prompt contém REGRAS (como decidir). O agente usa `think` para decidir, busca na KB o script relevante, depois adapta o script ao contexto da conversa.

Um script na KB NUNCA deve incluir lógica de decisão como "se o lead disser X, responda Y." Essa lógica pertence aos princípios do prompt. A KB apenas fornece a matéria-prima que o agente adapta.

---

## 4. Estrutura Otimizada para Busca

### Estratégia de Tags

Tags são a ponte entre a busca do agente e a seção certa da KB:

**Sinônimos:** Inclua variações comuns de como o tópico é referenciado
```
## Formas de Pagamento
Tags: pagamento, pagar, parcela, cartão, pix, financiamento, convênio, plano, cobertura
```

**Tags de Estado Emocional:** Para objeções, inclua o estado emocional
```
## OBJEÇÃO: Quer Pensar
Tags: pensar, pensando, considerar, decidir, pesquisando, comparando, indeciso
```

**Tags de Ação:** Inclua o que o agente pode estar tentando FAZER
```
## Script de Agendamento
Tags: agendar, marcar, consulta, disponível, horário, manhã, tarde, agenda
```

### Padrões de Nomenclatura Consistentes

| Prefixo | Tipo de Conteúdo | Exemplo |
|---------|-----------------|---------|
| OBJEÇÃO: | Scripts de tratamento de objeção | OBJEÇÃO: Preço |
| FAQ: | Perguntas frequentes | FAQ: Formas de Pagamento |
| SCRIPT: | Scripts específicos de conversa | SCRIPT: Convite Experiência |
| INFO: | Informação factual da empresa | INFO: Endereço e Estacionamento |
| TÉCNICA: | Técnicas de venda ou conversa | TÉCNICA: Perguntas SPIN |
| TEMPORAL: | Informação sensível ao tempo | TEMPORAL: Agenda Feriados 2026 |

---

## 5. Diretrizes de Conteúdo

### Regras de Escrita de Scripts

Scripts devem ser:
- **Naturais**: Escritos como fala real, não copy de marketing
- **Adaptáveis**: Escritos para que o agente possa modificar conforme contexto
- **Apropriados à plataforma**: Alinhados ao comprimento de mensagem da plataforma (WhatsApp = mais curto)
- **Completos mas não rígidos**: Forneçam a mensagem core com espaço para personalização

**Muito rígido (ruim):**
```
"Oi [Nome]! Obrigado por entrar em contato com a OdontoBarra! Estamos
super animados em te ajudar na sua jornada para o sorriso perfeito! Nossa
equipe de especialistas com mais de 22 anos de experiência está pronta pra
transformar sua vida! Agende sua avaliação hoje! 😊🦷✨"
```

**Natural e adaptável (bom):**
```
"Entendo, [Nome]. Essa preocupação é muito mais comum do que você imagina.
Nossa equipe tem um cuidado especial com pacientes que se sentem assim —
a gente sabe exatamente como te acolher."
```

### Números de Autoridade

Apresente métricas de autoridade consistentemente com o mesmo fraseado toda vez:
```
Métricas de Autoridade (usar consistentemente):
- "Mais de 22 anos de experiência"
- "Mais de 10.000 pacientes atendidos"
- "Mais de 5.000 implantes realizados"
```

### Preços e Informação Sensível

Para informação que o agente NUNCA deve compartilhar diretamente, inclua com instruções claras de manuseio:

```
## PREÇOS (CONFIDENCIAL — Nunca compartilhar diretamente)
Preços de tratamento APENAS são discutidos durante avaliação presencial.
Quando perguntarem sobre preço, redirecione para qualificação e avaliação.
```

Para informação que o agente PODE compartilhar (faixas de investimento, por exemplo), indique claramente:
```
## INVESTIMENTO (Pode informar faixas)
Sophie PODE informar faixas de investimento. Sempre apresentar com
posicionamento premium — nunca como "preço" ou "custo".
```

---

## 6. O Que Pertence Aqui vs. No Prompt

| Base de Conhecimento | System Prompt |
|---|---|
| Endereço, telefone, horários da empresa | Regras de saudação por horário |
| Descrições de serviços/tratamentos | Princípios de decisão (urgência vs. rotina) |
| Informação de preços | Regra: nunca compartilhar preço antes de qualificação |
| Scripts de objeção | Princípio de persistência (3 tentativas) |
| Respostas de FAQ | Etapas do fluxo de conversa |
| Técnicas de venda (perguntas SPIN) | Orientação de uso de ferramentas |
| Calendário de feriados e fechamentos | Variáveis de runtime (data/hora atual) |
| Ofertas promocionais e scripts | Identidade e personalidade do agente |
| Credenciais e bio da equipe | Guardrails e limites |

**Regra de ouro:** Se responde "o que eu devo dizer/saber?", é KB. Se responde "como eu devo pensar/decidir?", é prompt.

---

## 7. Estratégia de Manutenção

### Atualizações Regulares

A KB deve ser revisada regularmente para:
- **Seções temporais**: Atualizar calendários de feriados, períodos promocionais
- **Scripts**: Refinar com base em dados de performance de conversas
- **FAQs**: Adicionar novas perguntas comuns de conversas reais
- **Serviços**: Atualizar quando ofertas mudarem

### Controle de Versão

Mantenha uma nota de versão simples no topo da KB:
```
Última atualização: 01/03/2026
Mudanças: Atualizado calendário de feriados, adicionado novo script de objeção
```

### Atualizações Baseadas em Performance

Ao analisar conversas reais, observe:
- Perguntas que o agente não conseguiu responder → adicione à FAQ
- Objeções não cobertas → adicione nova seção de objeção
- Scripts que têm baixa performance → reescreva com melhores abordagens
- Informação que estava errada → corrija imediatamente

---

## 8. Template Completo de KB

Veja `assets/kb-template.md` para um template pronto para uso que implementa todos os princípios descritos acima.
