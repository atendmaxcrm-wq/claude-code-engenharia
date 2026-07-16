# Referência de Arquitetura de Prompts (GPT-Optimized)

Como construir system prompts para agentes de IA conversacionais rodando em modelos GPT (OpenAI) que sejam robustos, manuteníveis e eficazes em produção.

## Índice

1. [Princípios Estruturais](#1-princípios-estruturais)
2. [As Oito Seções de um Prompt de Agente](#2-as-oito-seções-de-um-prompt-de-agente)
3. [Escrevendo na Altitude Certa](#3-escrevendo-na-altitude-certa)
4. [O Padrão Think-Search-Act](#4-o-padrão-think-search-act)
5. [Orientação de Tools](#5-orientação-de-tools)
6. [Exemplos Few-Shot](#6-exemplos-few-shot)
7. [Guardrails e Limites](#7-guardrails-e-limites)
8. [Informação Temporal](#8-informação-temporal)
9. [Técnicas Avançadas de Conversão](#9-técnicas-avançadas-de-conversão)
10. [Anti-Padrões Comuns](#10-anti-padrões-comuns)
11. [Template Completo de Prompt](#11-template-completo-de-prompt)

---

## 1. Princípios Estruturais

### Markdown para Estrutura, XML para Limites

Modelos GPT foram treinados com Markdown extensivo nos dados de treino. Os próprios system prompts e documentação da OpenAI usam Markdown como formato principal. Pesquisas mostram que GPT-4 atinge maior precisão com prompts estruturados em Markdown.

**Use Markdown para:**
- Headers de seção (`#`, `##`, `###`)
- Regras e instruções (listas com `-`)
- Subcategorias de instruções
- Ênfase em termos-chave (`**negrito**`)

**Use XML apenas para:**
- Delimitar exemplos de conversa (onde limites início/fim precisam ser inequívocos)
- Variáveis de runtime injetadas no prompt
- Conteúdo que precisa de marcadores explícitos para que o modelo não confunda com instruções

```markdown
# Identidade

Você é a Dani, consultora de relacionamento da OdontoBarra.
Personalidade: acolhedora, profissional, empática.

# Regras Críticas

1. Sempre consulte info_odontobarra para informação factual. Nunca invente.
2. Nunca compartilhe preços antes da qualificação.

# Exemplos

<exemplos>
  <exemplo tipo="caminho_feliz">
    Lead: Oi, boa tarde
    Dani: Boa tarde! Sou a Dani da OdontoBarra. Como posso te chamar? 😊
  </exemplo>
</exemplos>

# Contexto

<variaveis>
  Data atual: {{current_date}}
</variaveis>
```

Essa abordagem híbrida te dá a legibilidade e eficiência de tokens do Markdown para o grosso do prompt, usando XML apenas onde delimitadores explícitos previnem má interpretação.

### Mantenha Enxuto Mas Completo

O prompt deve conter o MÍNIMO de informação necessária para definir completamente o comportamento esperado. Cada frase deve justificar sua presença. Se você pode remover uma frase e o comportamento não muda, remova.

Markdown economiza aproximadamente 15% de tokens comparado a equivalentes em XML. Para agentes com múltiplas tools e fluxos detalhados, isso se acumula significativamente.

### Princípios Sobre Prescrições

Ensine ao agente heurísticas e frameworks de raciocínio ao invés de regras if/then hardcoded. Regras rígidas criam fragilidade — o agente quebra quando encontra um cenário não coberto. Princípios criam adaptabilidade.

**Frágil (evite):**
```
Se lead perguntar preço → diga "cada caso é único"
Se lead perguntar sobre medo → diga "nossa equipe tem experiência com pacientes ansiosos"
```

**Baseado em princípios (prefira):**
```
Quando um lead levantar uma preocupação ou objeção:
1. Pense passo a passo para identificar a emoção ou necessidade central por trás da objeção
2. Valide o sentimento com empatia genuína (não frases decoradas)
3. Busque na base de conhecimento o script relevante de objeção
4. Adapte o script ao contexto específico que o lead compartilhou
5. Conduza para o próximo passo no fluxo de conversa
```

### GPT Segue Instruções Literalmente

Diferente do Claude, que tende a inferir intenção de prompts vagos, GPT-4.1+ segue instruções muito literalmente. Isso é tanto uma força quanto um risco:

**Força:** Se seu prompt é preciso, o agente vai segui-lo exatamente.
**Risco:** Se suas regras são absolutas sem saídas de emergência, o modelo pode fabricar informação para cumprir a regra.

Sempre adicione ressalvas a regras absolutas:
```
# Ruim
Sempre chame a tool de agendamento antes de responder sobre disponibilidade.

# Bom
Sempre chame a tool de agendamento antes de responder sobre disponibilidade. Se a tool estiver indisponível ou retornar erro, informe ao lead que está verificando e confirmará em breve.
```

---

## 2. As Oito Seções de um Prompt de Agente

Um prompt de agente bem estruturado tem oito seções, mapeadas à estrutura recomendada pela OpenAI:

| Nossa Seção | Equivalente OpenAI | Header Markdown |
|---|---|---|
| Identidade | Role and Objective | `# Identidade e Objetivo` |
| Regras Críticas | Instructions | `# Instruções` → `## Regras Críticas` |
| Ferramentas | Instructions | `# Instruções` → `## Ferramentas` |
| Fluxo de Conversa | Instructions | `# Fluxo de Conversa` |
| Princípios de Decisão | Reasoning Steps + Instructions | `# Princípios de Decisão` |
| Exemplos | Examples | `# Exemplos` |
| Variáveis | Context | `# Contexto` |
| Lembretes Finais | Final Reminders (GPT-Specific) | `# Lembretes Finais` |

### Seção 1: Identidade (`# Identidade e Objetivo`)

Define quem o agente é. Mantenha conciso — personalidade emerge mais dos exemplos e regras de tom do que de descrições longas.

Inclua:
- Nome, função e empresa
- Traços de personalidade (3-5 adjetivos no máximo)
- Regras de tom de voz (concretas e específicas)
- Regras de saudação (por horário, se aplicável)
- O que o agente NÃO é (limites da persona)
- Objetivo principal

```markdown
# Identidade e Objetivo

Você é a Polli, Consultora de Vendas da Pollo Corretora de Seguros.
Personalidade: simpática, consultiva, objetiva, tecnicamente competente, transparente.
Objetivo: qualificar leads, responder dúvidas sobre planos de saúde usando as bases de conhecimento, e agendar reuniões com o consultor humano.

## Tom de Voz
- Mensagens: máximo 3 linhas cada
- Emojis: máximo 1-2 por mensagem, preferir 😊 e 💛
- Linguagem: conversa natural de WhatsApp, vocabulário técnico quando necessário
- Proibido: abreviações, gírias, piadas, formatação robótica
```

### Seção 2: Regras Críticas (`## Regras Críticas`)

Regras invioláveis. Mantenha a lista curta (5-8 regras no máximo) — cada regra que você adiciona dilui o peso das outras.

**IMPORTANTE para GPT:** Sempre inclua fallbacks para regras absolutas. GPT vai tentar cumprir literalmente mesmo quando não consegue, o que leva a fabricação de dados. Adicione saídas de emergência como "Se não encontrar a informação, diga que vai verificar com a equipe" ou "Se a tool falhar, informe ao lead."

```markdown
## Regras Críticas

1. Sempre consulte a base de conhecimento para QUALQUER informação factual. Nunca confie na memória. Se não encontrar a resposta, diga ao lead que vai verificar com a equipe.
2. Nunca compartilhe preços exatos — o valor depende do perfil do cliente.
3. Nunca feche vendas nem dê descontos. Você informa, qualifica e agenda. O consultor humano apresenta propostas.
4. Faça 3 tentativas contextuais antes de aceitar qualquer recusa.
5. Nunca prometa resultados garantidos.
6. Se não sabe, não invente. Diga que vai verificar com o consultor.
```

### Seção 3: Ferramentas (`## Ferramentas`)

Orientação clara e sem ambiguidade sobre quando e como usar cada tool.

```markdown
## Ferramentas

**think**
Use ANTES de qualquer decisão que exija raciocínio: classificar a situação, identificar tipo de objeção, planejar próximos passos, decidir qual base de conhecimento buscar.
Este é um rascunho interno — o cliente nunca vê isso.

**info_[empresa]**
Use para QUALQUER informação factual: endereço, horários, serviços, scripts de objeção, FAQs, fluxos de qualificação.
Busque com palavras-chave descritivas: "objeção preço", "fluxo qualificação PME".
Nunca transfira para humano uma pergunta que você pode responder consultando a base de conhecimento.

**verifica_agenda**
Use ANTES de oferecer qualquer horário. Nunca invente disponibilidade.
```

### Seção 4: Fluxo de Conversa (`# Fluxo de Conversa`)

Fluxo de alto nível com objetivos por etapa. NÃO é um script rígido.

```markdown
# Fluxo de Conversa

## Etapa 1: ABERTURA
Sempre se apresente: "[Saudação]! Sou a [Nome], da [Empresa] 😊"
Capture o nome do lead. Se chegar já com uma pergunta, responda primeiro, depois se apresente.

## Etapa 2: IDENTIFICAR NECESSIDADE
Entenda o que a pessoa precisa. Ao perguntar, sempre liste os produtos pelo nome completo — nunca use "..." ou listas incompletas.
Direcione com base no que identificar.

## Etapa 3: QUALIFICAR E CONSULTAR
Qualifique através de conversa natural — não interrogatório. Uma pergunta por vez.
SEJA CONSULTIVO: responda perguntas usando as bases de conhecimento ativamente. Você é consultor, não apenas coletor de dados.
Só direcione ao consultor humano DEPOIS de uma conversa consultiva completa.

## Etapa 4: CONVERTER
Conduza para o agendamento. Pergunte a preferência primeiro, depois verifique disponibilidade.

## Etapa 5: CONFIRMAR
Confirme detalhes, forneça logística, feche com calor humano.
```

### Seção 5: Princípios de Decisão (`# Princípios de Decisão`)

Onde a instrução literal do GPT precisa de mais orientação. Esta seção ensina o agente a raciocinar.

```markdown
# Princípios de Decisão

## Processo de Raciocínio
Para toda decisão, pense passo a passo:
1. CLASSIFIQUE: Que tipo de situação é essa?
2. BUSQUE: Que informação relevante existe na base de conhecimento?
3. AJA: Responda adaptando o que encontrou ao contexto específico do lead.

Sempre pense antes de responder. Planeje qual tool consultar antes de montar sua mensagem.

## Persistência (Framework de 3 Tentativas)
Quando um lead resistir:
- 1ª tentativa: Investigue o motivo real. Pergunte com curiosidade genuína.
- 2ª tentativa: Endereçe o motivo específico usando o script relevante da KB, adaptado ao contexto.
- 3ª tentativa: Ofereça um caminho alternativo ou incentivo relevante à situação.
- Após 3 tentativas: Feche com elegância, deixe a porta aberta.

Nunca repita o mesmo argumento. Cada tentativa traz um NOVO ângulo.

## Hierarquia de Prioridades
1. Segurança e ética (nunca fabricar, nunca prometer, nunca diagnosticar)
2. Experiência do cliente (empatia e respeito sempre)
3. Conversão (agendamento/qualificação)
4. Coleta de dados (nome, contato, perfil)
```

### Seção 6: Exemplos (`# Exemplos`)

Esta é a seção de maior impacto para qualidade do agente. GPT aprende padrões de comportamento principalmente dos exemplos.

**AVISO CRÍTICO:** GPT-4.1+ tende a repetir frases dos exemplos literalmente. Isso cria conversas robóticas e repetitivas. **Sempre inclua** esta instrução antes dos exemplos:

```markdown
# Exemplos

Importante: Estes exemplos mostram o padrão de conversa esperado. Varie seu fraseado naturalmente — NÃO repita estes exemplos palavra por palavra. Adapte sua linguagem ao tom e contexto do lead.
```

Depois envolva as conversas em XML para delimitação clara:

```xml
<exemplos>
  <exemplo tipo="caminho_feliz" descricao="Lead interessado, qualificação suave até agendamento">
    Lead: Oi, boa tarde

    Dani: Boa tarde! Sou a Dani da OdontoBarra 😊 Como posso te chamar?

    Lead: Maria

    [think]: "Maria chegou, cumprimentou. Vou descobrir o que trouxe ela."

    Dani: Oi Maria! O que te trouxe até a gente hoje?
    ...
  </exemplo>
</exemplos>
```

Mantenha 2-3 exemplos cobrindo: caminho feliz, tratamento de objeção e transferência/escalação.

**Diretrizes para bons exemplos:**
1. **Realistas**: Use linguagem conversacional natural (mensagens curtas, fala coloquial)
2. **Completos**: Mostre o fluxo inteiro de saudação até resolução
3. **Diversos**: Cada exemplo cobre um caminho diferente
4. **Mostram raciocínio**: Inclua a tool think para mostrar COMO o agente decide
5. **Mostram uso de tools**: Demonstre buscas na KB e uso dos resultados
6. **Apropriados à plataforma**: Match com o estilo de mensagem da plataforma-alvo

### Seção 7: Variáveis e Contexto (`# Contexto`)

Variáveis dinâmicas injetadas em runtime. Use XML para delimitação clara:

```markdown
# Contexto

<variaveis>
  Data atual: {{current_date}}
  Horário atual: {{current_time}}
  Dia da semana: {{day_of_week}}
</variaveis>
```

### Seção 8: Lembretes Finais (Específico do GPT)

GPT se beneficia de ter instruções-chave repetidas no FINAL do prompt. A OpenAI recomenda colocar instruções críticas tanto no início QUANTO no fim para prompts longos.

```markdown
# Lembretes Finais

- Sempre pense passo a passo antes de responder
- Sempre consulte a base de conhecimento antes de responder perguntas factuais — não adivinhe
- Varie suas respostas naturalmente — nunca repita a mesma frase duas vezes
- Seja humano: reaja ao que o lead disse antes de avançar
- Uma pergunta por vez — nunca sobrecarregue com múltiplas perguntas
```

---

## 3. Escrevendo na Altitude Certa

A altitude ideal de prompt é a zona Goldilocks entre dois modos de falha:

**Muito Baixa (Super-prescritiva):** Lógica if/then hardcoded para cada cenário. Cria agentes frágeis que quebram em edge cases.

**Muito Alta (Sub-especificada):** Orientação vaga que assume que o modelo vai descobrir sozinho. GPT especialmente precisa de instruções explícitas — ele não vai inferir tanto quanto o Claude.

**Na Medida (Baseada em princípios):** Heurísticas claras com especificidade suficiente para guiar comportamento, mais exemplos que demonstram os princípios em ação.

O teste de altitude: um funcionário novo inteligente conseguiria seguir estas instruções no primeiro dia e tomar boas decisões, mesmo em situações não explicitamente cobertas?

---

## 4. O Padrão Think-Search-Act

O padrão mais poderoso para agentes conversacionais:

1. **Think** (tool `think`): Raciocinar sobre o que está acontecendo — classificar a situação, identificar o estado emocional do lead, planejar próximos passos
2. **Search** (tool `info_`): Buscar scripts, fatos ou protocolos relevantes na base de conhecimento
3. **Act**: Responder ao lead usando a informação recuperada, adaptada ao contexto

**Nota Específica do GPT:** Diferente do extended thinking do Claude, GPT não raciocina internamente por padrão. Você PRECISA incluir instruções explícitas como "Pense passo a passo antes de responder" e "Planeje qual tool consultar antes de montar sua mensagem." A tool `think` serve como o container estruturado para esse raciocínio.

---

## 5. Orientação de Tools

### Princípios de Design para Tools de Agente

Cada tool deve ser:
- **Autocontida**: Um propósito claro, sem sobreposição com outras tools
- **Descritiva**: Nome e descrição dizem ao agente exatamente quando usar
- **Consciente de erros**: O agente sabe o que fazer quando a tool falha

**Aviso Específico do GPT:** Dizer ao GPT que ele DEVE SEMPRE chamar uma tool pode levar a fabricação de inputs quando informação está faltando. Sempre inclua fallback: "Se você não tem informação suficiente para chamar esta tool, pergunte ao lead primeiro."

### Padrões Comuns de Tools

| Tipo de Tool | Propósito | Orientação |
|-------------|-----------|-----------|
| Raciocínio (think) | Rascunho interno para tomada de decisão | Use ANTES de qualquer decisão não trivial |
| Conhecimento (info_) | Buscar informação factual e scripts | Use para QUALQUER afirmação factual — nunca confie na memória |
| Verificação (verifica_) | Verificar estado antes de ação | Use ANTES de oferecer ou confirmar qualquer coisa |
| Ação (agenda_, transfere_) | Executar ações | Use apenas APÓS receber confirmação do lead |
| Resumo (resumo) | Resumir conversa para handoff | SEMPRE use antes de qualquer transferência para humanos |

### Tratamento de Falha de Tools

Sempre inclua:
```
Se qualquer tool retornar erro ou timeout:
- Nunca fabrique informação para compensar
- Informe ao lead que está verificando
- Tente novamente uma vez
- Se persistir, resuma e transfira para equipe humana
```

---

## 6. Exemplos Few-Shot

### Por Que Exemplos São Críticos

Exemplos são o elemento de maior impacto para qualidade de agente. Comunicam mais sobre comportamento desejado do que páginas de instruções.

### Quantos Exemplos

2-3 exemplos canônicos é o ponto ideal. Mais que isso consome muitos tokens. Menos que isso não fornece sinal suficiente.

### Específico do GPT: Risco de Repetição Verbatim

GPT-4.1+ tende a ecoar frases dos exemplos literalmente em produção. Isso cria conversas robóticas e repetitivas. **Sempre inclua** esta instrução antes dos exemplos:

```
Importante: Estes exemplos mostram o padrão de conversa esperado. Varie seu fraseado naturalmente — NÃO repita estes exemplos palavra por palavra. Adapte sua linguagem ao tom e contexto do lead.
```

---

## 7. Guardrails e Limites

### Regras com Saídas de Emergência (Crítico para GPT)

GPT segue regras literalmente. Regras absolutas sem fallbacks causam fabricação:

```markdown
# Ruim (causa fabricação)
Sempre forneça ao lead os horários de funcionamento da empresa.

# Bom (tem fallback)
Sempre forneça ao lead os horários de funcionamento consultando info_empresa. Se a tool não retornar essa informação, diga que vai verificar e retorna.
```

### Limites de Escopo

Defina o que o agente NÃO faz:
- Não lida com (tipos específicos de pedido) → transfere para humano
- Não discute (assuntos fora do escopo) → redireciona com empatia
- Não processa (tipos de mídia que não consegue) → pede texto
- Não faz promessas sobre (resultados, garantias) → redireciona para profissional

### Regras de Escalação

```
Sempre escale para humano quando:
- Situação requer atenção especializada além das bases de conhecimento
- Lead fica agressivo ou abusivo
- Lead menciona ação legal
- Agente não consegue resolver após 3 tentativas genuínas
- Falhas de tools impedem operação normal
- Lead explicitamente pede um humano
```

---

## 8. Informação Temporal

### O Que Vai no Prompt
- Variáveis de runtime (data atual, hora, dia da semana)
- A REGRA de verificar restrições temporais na KB

### O Que Vai na Base de Conhecimento
- Calendários de feriados e datas fechadas
- Promoções sazonais ou ofertas
- Restrições temporárias ou mudanças
- Horários de funcionamento

---

## 9. Técnicas Avançadas de Conversão

Estas técnicas são módulos opcionais para agentes cujo objetivo principal é agendamento, reserva ou venda de serviços de alto valor. Nem todo agente precisa — use quando o modelo de negócio exige táticas sofisticadas de conversão.

### 9.1 Framework de Persistência (Sistema de 3 Tentativas)

O princípio básico de persistência (investigar → endereçar → alternativa → fechar) é universal. Mas para agentes de alta conversão, cada tentativa segue uma estratégia de escalação deliberada:

**1ª Tentativa — Investigar e Reposicionar:**
O lead resiste. O agente usa `think` para identificar a objeção real por trás da resposta superficial. Depois faz uma pergunta que reposiciona a situação.

```
Lead: "Vou pensar"

[think]: "Lead quer pensar. Mas o que está por trás? Preço? Medo?
Comparando com concorrente? Preciso investigar antes de responder."

Agente: "Claro! Posso perguntar o que te deixou em dúvida?
Às vezes é algo que consigo esclarecer agora mesmo."
```

O objetivo não é empurrar — é descobrir o bloqueio real. Uma vez revelado, o agente busca na KB o script de objeção relevante.

**2ª Tentativa — Resposta Direcionada:**
Agora o agente sabe o motivo real. Busca na KB o script específico de objeção e adapta ao que o lead compartilhou. Não é resposta genérica — endereça diretamente a preocupação usando as palavras e contexto deles.

**3ª Tentativa — Caminho Alternativo:**
Se o lead ainda resistir, ofereça algo diferente — uma opção de menor compromisso, uma reserva por tempo limitado, ou uma versão reposicionada do serviço.

**Após 3 Tentativas — Fechamento Elegante:**
Aceite com graça, reforce o relacionamento, e deixe a porta aberta. Nunca termine com energia de derrota — termine com calor.

### 9.2 Técnica de Valorização de Agenda

Para agentes que marcam consultas ou atendimentos, a forma como a disponibilidade é apresentada afeta dramaticamente a conversão. O princípio: **nunca exponha a disponibilidade real, sempre enquadre cada vaga como escassa e privilegiada.**

Usa um sistema de 3 ofertas:

**1ª Oferta — Próxima vaga disponível, apresentada como exclusiva:**
Após o lead aceitar agendar, pergunte preferência (manhã/tarde), verifique disponibilidade para o PRÓXIMO dia útil no período escolhido.

```
Agente: "Você prefere pela manhã ou tarde?"
Lead: "De tarde"

[verifica_agenda]: próximo dia útil, tarde
Agente: "A agenda liberou um horário especial amanhã às 14h30.
Posso reservar pra você?"
```

Linguagem-chave: "a agenda liberou", "horário especial", "consegui uma vaga". Nunca: "temos vários horários", "qual horário prefere entre X, Y e Z".

**2ª Oferta — DIA diferente (não apenas horário diferente):**
Se recusar a primeira, a segunda oferta deve ser um DIA DIFERENTE, não apenas outro horário no mesmo dia. Isso mantém a ilusão de escassez.

```
Lead: "Amanhã não consigo"

[think]: "Recusou amanhã. Próxima oferta: outro DIA, não outro horário."
[verifica_agenda]: próximo dia útil + 1

Agente: "Consegui uma vaga na quinta às 15h. Esse fica melhor pra você?"
```

**3ª Oferta — Preferência do lead + Script de Valorização:**
Se recusar de novo, pergunte que dia/horário funciona. Verifique disponibilidade e SEMPRE use o script de valorização, mesmo que a vaga esteja livre:

```
Lead: "Só consigo na sexta de manhã"

[verifica_agenda]: sexta manhã

Agente: "Deixa eu verificar... Olha, nesse horário tenho uma cliente,
mas ela havia me pedido pra antecipar. Vou encaixar ela em outro
horário e reservar esse pra você. Posso confirmar?"
```

O script da "cliente que pediu pra antecipar" transforma uma reserva simples em um favor — o lead se sente priorizado e especial. Use consistentemente na 3ª oferta.

**Regras de Valorização de Agenda:**
- NUNCA diga "temos vários horários disponíveis" ou "nossa agenda está aberta"
- NUNCA ofereça múltiplas opções de horário de uma vez (quebra escassez)
- SEMPRE enquadre cada vaga como limitada, exclusiva ou especialmente arranjada
- Na 3ª oferta, SEMPRE use o script de valorização
- Ofereça uma vaga por vez, espere resposta antes de oferecer outra

### 9.3 Técnica de Oferta Contextualizada

Para agentes que têm uma oferta especial ou convite (avaliação cortesia, consulta gratuita, pacote experiência), a oferta NUNCA deve ser apresentada genericamente. Deve sempre ser contextualizada com o que o lead compartilhou.

**O princípio:** A oferta parece conquistada, não anunciada.

**Quando usar:**
- Após a 2ª ou 3ª tentativa de persistência, quando preço é o bloqueio
- Quando o lead está interessado mas hesita financeiramente
- Quando o lead precisa de mais informação para decidir

**Estrutura:**
1. Referencie o que o lead compartilhou (situação, preocupação ou desejo específico)
2. Conecte ao porquê essa oferta é relevante PRA ELE(A)
3. Apresente os detalhes da oferta
4. Feche com chamada para ação

```
RUIM (genérico): "Temos uma avaliação gratuita! Quer agendar?"

BOM (contextualizado): "[Nome], pelo que você me contou sobre [coisa específica
que compartilhou], e por ter demonstrado interesse real em [objetivo dela],
consegui liberar [nome da oferta] pra você. Inclui [detalhes].
Normalmente custa [valor] mas fica por nossa conta.
Assim você [benefício conectado à situação dela]. Que tal marcarmos?"
```

### 9.4 Calibração de Urgência

Diferentes segmentos requerem níveis diferentes de urgência. O agente deve calibrar a urgência ao contexto:

**Alta urgência (saúde, odontologia, médico):**
Foco em consequências do adiamento — deterioração progressiva, complexidade aumentada, custos futuros maiores.
```
"Quanto mais tempo passa, maior a perda óssea, e o tratamento
pode precisar ser mais complexo no futuro."
```

**Média urgência (casamentos, eventos, sazonal):**
Foco em escassez de disponibilidade — datas limitadas, períodos de alta demanda, janelas de reserva.
```
"As datas de outubro são as mais procuradas.
Garantir a sua agora te dá tranquilidade pra planejar o resto."
```

**Baixa urgência (consultoria, cursos, serviços contínuos):**
Foco em custo de oportunidade — o que estão perdendo ao esperar, vantagem competitiva.
```
"Cada mês sem aplicar essas estratégias é resultado que fica na mesa.
Quanto antes começar, antes você colhe os frutos."
```

A base de conhecimento deve conter os scripts de urgência calibrados ao segmento específico. O prompt ensina o PRINCÍPIO de urgência calibrada, não os scripts específicos.

### 9.5 Quando Aplicar Estas Técnicas

Inclua estas técnicas no prompt do agente quando:
- O objetivo principal do agente é agendar ou vender
- O serviço é de alto valor ou alta consideração (não compras por impulso)
- O modelo de negócio depende de taxas de conversão
- O ciclo de vendas envolve tratamento de objeções

Pule estas técnicas quando:
- O agente é primariamente informacional ou de suporte
- O produto é de baixo custo ou self-service
- Forçar conversão danificaria a marca
- O agente lida com demandas inbound que já são de alta intenção

Para implementar, adicione as técnicas relevantes como princípios na seção de Princípios de Decisão do prompt, e armazene os scripts específicos (frases de valorização, templates de oferta contextualizada, calibrações de urgência) na base de conhecimento para retrieval.

---

## 10. Anti-Padrões Comuns

### Anti-Padrão 1: Script Dumping
Colocar scripts completos de conversa no system prompt ao invés da base de conhecimento. Desperdiça tokens de contexto e torna o prompt rígido.

### Anti-Padrão 2: Duplicação de Regras
Repetir a mesma regra em múltiplas seções. Desperdiça tokens e arrisca inconsistência.

### Anti-Padrão 3: Mapeamento Exaustivo If/Then
Tentar cobrir cada cenário com regras específicas. Cria gaps e fragilidade.

### Anti-Padrão 4: Personalidade Vaga
Descrever personalidade com adjetivos abstratos ("amigável", "profissional") sem exemplos concretos de comportamento.

### Anti-Padrão 5: Modos de Falha Ausentes
Não definir o que acontece quando tools falham ou situações caem fora do escopo.

### Anti-Padrão 6: Dados Temporais Hardcoded
Colocar datas específicas, agendas ou promoções diretamente no prompt.

### Anti-Padrão 7: Contexto Sobrecarregado
Incluir informação "por precaução" ao invés de torná-la recuperável sob demanda.

### Anti-Padrão 8: Uso Excessivo de CAPS LOCK (Específico GPT)
GPT-4.1+ hiper-foca em instruções em ALL CAPS, às vezes em detrimento de outras regras. Use caps moderadamente para ênfase verdadeira, não como forma padrão de destacar instruções.

### Anti-Padrão 9: Regras Absolutas Sem Fallbacks (Específico GPT)
Regras como "SEMPRE chame a tool" ou "NUNCA responda sem verificar" podem levar GPT a fabricar inputs de tools quando informação está faltando. Sempre adicione saídas de emergência.

### Anti-Padrão 10: Exemplos Sem Instrução de Variação (Específico GPT)
GPT tende a repetir frases de exemplos literalmente. Sempre instrua: "Varie o fraseado dos exemplos conforme necessário. Não repita exemplos palavra por palavra."

---

## 11. Template Completo de Prompt

Veja `assets/prompt-template.md` para um template pronto para uso que implementa todos os princípios descritos acima.
