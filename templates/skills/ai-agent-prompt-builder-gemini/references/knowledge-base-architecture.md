# Referência de Arquitetura de Base de Conhecimento

> **Nota:** Bases de conhecimento são agnósticas de modelo — são servidas via RAG/pgvector/tools, não embarcadas no system prompt. O formato e a estrutura abaixo funcionam identicamente para Gemini, GPT, Claude ou qualquer outro LLM, e a recomendação desta família de skills é manter embeddings OpenAI mesmo rodando o LLM no Gemini (ver `SKILL.md`, seção "Decisão Crítica: Embeddings"). A única consideração específica do Gemini é a ponte entre KB e prompt: as tags de busca da KB precisam casar com as **palavras-chave que o agente passa na invocação da tool** (`info_*`). No Gemini isso é mais sensível que no GPT porque a chamada de tool é representada via padrão anti-roleplay (ver `SKILL.md`, seção "Padrão de Exemplos com Tools") — a query que o agente gera ao invocar `info_*` deve usar exatamente os termos que aparecem nas linhas `Tags:` dos sub-blocos. Sempre que projetar um sub-bloco com `Tags:`, garanta que essas mesmas palavras apareçam como exemplos de query na descrição da tool no prompt.

---

## Índice

1. [O Papel da Base de Conhecimento](#1-o-papel-da-base-de-conhecimento)
2. [Princípios de Organização](#2-princípios-de-organização)
3. [Design de Seções](#3-design-de-seções)
4. [Estrutura Otimizada para Busca](#4-estrutura-otimizada-para-busca)
5. [Diretrizes de Conteúdo](#5-diretrizes-de-conteúdo)
6. [O Que Pertence Aqui vs. No Prompt](#6-o-que-pertence-aqui-vs-no-prompt)
7. [Chunking Semântico (Tags por Sub-Bloco)](#7-chunking-semântico-tags-por-sub-bloco)
8. [Estratégia de Manutenção](#8-estratégia-de-manutenção)
9. [Template Completo de KB](#9-template-completo-de-kb)

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
| **Regras de combinação de produtos** (ex: 4 pessoas = 2 DUOs, 5 = DUO + TRIO) | **Princípio: "grupos 4+ → consulte info_X com `grupos família`"** |
| **Listas de exceções por categoria** (ex: unidades sem DUO LOCAL) | **Princípio: "apresentar sempre o caminho positivo, nunca 'não tem'"** |
| **Scripts de apresentação com formato específico** | **Princípio: "apresentar Mensal + Anual GOLD como padrão"** |
| **Tabelas de valores por variação** (ex: diária por grupo de unidade) | **Princípio: "ao informar preço, sempre consultar a tool"** |

**Regra de ouro:** Se responde "o que eu devo dizer/saber?", é KB. Se responde "como eu devo pensar/decidir?", é prompt.

### Padrão de Seção para Regras de Negócio

Quando uma regra de negócio tem dados concretos (números, listas, scripts específicos), ela merece **seção própria na KB** com estrutura:

```markdown
## CATEGORIA: Nome da Regra
Tags: [palavras-chave descritivas para retrieval]

### Contexto
[Quando essa regra se aplica]

### Regras / Tabela
[Os dados específicos — combinações, valores, listas]

### Scripts de Apresentação
[Como apresentar para o lead — formato específico]

### Exceções
[Casos especiais que mudam a regra padrão]

### Quando transferir
[Se houver critério de escalação específico dessa regra]
```

Com isso, o prompt só precisa saber: "Se a situação X acontecer, consulte `info_X` com palavra-chave Y". A complexidade fica encapsulada na KB, onde é fácil de atualizar sem mexer no comportamento do agente.

---

## 7. Chunking Semântico (Tags por Sub-Bloco)

Quando a KB é consumida via retrieval semântico (pgvector, embeddings), a forma como o conteúdo é organizado em **chunks** afeta diretamente se o agente vai receber a info certa no top-K. Este é um padrão comprovado para evitar uma classe inteira de bugs de retrieval falho.

### O bug que esse padrão resolve

Cenário típico: o lead usa um **alias** ou **sinônimo** para identificar algo (uma unidade pelo bairro, um produto pelo apelido, etc). A KB tem o conteúdo correto, mas dentro de um bloco cujo cabeçalho usa o **nome oficial**. Resultado: a query do retrieval não encontra match forte com o cabeçalho do chunk certo, e outros chunks (com info incorreta para o caso específico) ganham no top-K. O agente recebe dados de outro item e responde errado.

**Exemplo real:** lead diz "Restinga" (alias da unidade Extremo Sul). KB tem bloco `### EXTREMO SUL (Center Kan)` com `**Aliases:** Restinga, Center Kan, ...`. Query `planos Restinga` retornou blocos de outras unidades (com valores padrão diferentes), porque "Restinga" não estava no cabeçalho do chunk certo, só no conteúdo. Agente apresentou valor errado — DUO LOCAL 12x 219,80 (valor padrão) em vez de 12x 179,80 (valor especial da Restinga). R$ 500 a mais cobrados errado.

### A solução: Tags semânticas por sub-bloco

Para cada item identificável (unidade, produto, categoria) que possa ser referido por aliases ou termos variados, criar um **sub-bloco dedicado** com:

1. **Cabeçalho específico e único** (`### NomeBloco: Identificador` ou `### Categoria: NomeItem`)
2. **Linha `Tags:` logo abaixo** com todas as palavras-chave de busca (aliases, sinônimos, variações de query)
3. **Conteúdo completo dentro do bloco** — o sub-bloco deve ser autossuficiente, sem depender que outros chunks venham junto

```markdown
### Endereço: EXTREMO SUL (Restinga)
Tags: endereço extremo sul, endereço restinga, horário restinga, telefone restinga, center kan, joão antônio silveira, restinga
- **Endereço:** Estrada João Antônio Silveira, 1335 – 2º andar (Center Kan, Restinga)
- **Horários:** Seg-Sex 05h30-23h | Sáb 08h-20h | Dom/Fer 09h-15h
- **WhatsApp:** (51) 98146-0158
```

Agora a query "endereço Restinga" pesca esse bloco diretamente — `restinga` está nas Tags, e o conteúdo está completo no chunk.

### Quando aplicar (sinais de risco)

Aplique o padrão preventivamente quando o conteúdo tiver QUALQUER destes:

- **Aliases dentro do bloco**: cabeçalho usa nome oficial, mas o conteúdo cita outros nomes (bairro, ponto de referência, apelido). Classic.
- **Tabela monolítica de N itens**: ex: tabela única com 25 unidades + endereços. Vira chunk único enorme; quando o lead pergunta sobre uma unidade específica, ou o chunk inteiro vem (ineficiente) ou não vem (bug).
- **Sub-categorias dentro de uma seção**: ex: "Estacionamento — 4 categorias" listadas em um bloco. Cada categoria deve virar sub-bloco com Tags próprias incluindo as unidades que pertencem àquela categoria.
- **Conteúdo que pode ser pedido por sinônimos**: "valores X" ou "preços X" ou "mensalidade X" — todas devem estar nas Tags do bloco de planos da unidade X.

### Construção das Tags (anatomia)

Para cada sub-bloco, as Tags devem incluir:

1. **Termos de query padrão** com o nome principal: `planos NOMEUNIDADE, valores NOMEUNIDADE, preço NOMEUNIDADE, mensalidade NOMEUNIDADE` (adapte ao domínio)
2. **Todos os aliases conhecidos**: bairros, ruas, pontos de referência, apelidos, nomes de shopping
3. **Variações morfológicas comuns**: singular/plural, com/sem acento, com/sem preposição (`av padre cacique` e `padre cacique`)
4. **Termos contrastivos**: se o item é "valores especiais" ou "diferenciado", incluir essas palavras

```markdown
### Grade: TERESÓPOLIS
Tags: grade teresópolis, aulas teresópolis, horários teresópolis, bourbon teresópolis aulas, cel aparício 250 aulas
```

### Atenção a colisões cruzadas

Quando dois blocos compartilham aliases (ex: "Cidade Baixa" pode ser Venâncio OU República), use **disambiguators explícitos** dentro do bloco — uma frase curta deixando claro o que NÃO é:

```markdown
### Ambiguidade: Cidade Baixa
Tags: cidade baixa, bairro cidade baixa, qual unidade da cidade baixa, venâncio, república
- O lead diz: "Cidade Baixa" / "bairro Cidade Baixa"
- Pode ser: **Venâncio** (Av. Venâncio Aires) ou **República** (Rua da República)
- ⚠️ Cidade Baixa NÃO inclui Centro/Andradas — Centro é outro bairro (Centro Histórico).
```

Isso evita que o agente cruze conceitos quando o retrieval traz dois blocos similares no top-K.

### Diagnóstico rápido: é bug de retrieval?

Quando um agente erra um dado factual que sabidamente está na KB, antes de mexer no prompt, **inspecione o que a tool retornou de fato**:

- ✅ Veio o chunk certo? Bug é comportamental (modelo embaralhou ou ignorou).
- ❌ Não veio o chunk certo, vieram chunks de itens parecidos? **Bug de retrieval.** Aplicar este padrão (Tags + sub-bloco autossuficiente).

A solução para retrieval falho **não é mexer no prompt** — é mexer na KB. Reforçar regras no prompt enquanto o retrieval continua falhando só infla tokens sem resolver o problema raiz.

### Ordem de operações ao aplicar em escala

Quando uma KB existente vai receber Tags em todas as seções vulneráveis, seguir esta ordem evita retrabalho:

1. **Mapear blocos vulneráveis** — listar tudo que tem aliases dentro do conteúdo, tabelas monolíticas de N itens, sub-categorias listadas em bloco único.
2. **Priorizar pelo histórico de bugs** — onde já houve bug, tratar primeiro.
3. **Para cada bloco vulnerável**: explodir em sub-blocos com Tags se for tabela; adicionar linha `Tags:` se for bloco já estruturado.
4. **Confirmar que o conteúdo é autossuficiente** — cada sub-bloco precisa funcionar sozinho. Se depende de outro chunk vir junto, refatorar pra incluir o necessário.
5. **Reindexar o pgvector** — chunks novos só aparecem após reindex.
6. **Conferir contagem de chunks pós-reindex** — deve aumentar (mais sub-blocos = mais chunks atômicos).
7. **Testar queries que usem aliases** — não só o nome oficial.

### Padrões de cabeçalho recomendados

Para clareza visual e match semântico, padronizar os cabeçalhos por categoria:

- `### Grade: NOMEUNIDADE` — para grades de aulas
- `### Endereço: NOMEUNIDADE` — para endereços/horários/telefones
- `### Ambiguidade: TERMO` — para casos onde um termo pode ser N coisas
- `#### Lutas: NOMEUNIDADE` — para sub-blocos dentro de uma seção pai (`## PLANOS: Lutas`)
- `#### Estacionamento: TIPO` — para sub-blocos dentro de seção pai

Esse padrão tem se provado robusto em produção. Sempre que o pgvector falha em entregar o chunk certo no top-K, a solução tem sido aplicar exatamente este formato.

---

## 8. Estratégia de Manutenção

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

## 9. Template Completo de KB

Veja `assets/kb-template.md` para um template pronto para uso que implementa todos os princípios descritos acima.
