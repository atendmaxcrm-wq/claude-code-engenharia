---
name: ai-agent-prompt-builder-gemini
description: "Cria system prompts e bases de conhecimento profissionais para agentes de IA conversacionais (WhatsApp, atendimento, vendas, agendamento) otimizados para Google Gemini 3 — especialmente Gemini 3.1 Flash-Lite. Use sempre que o usuário quiser criar, analisar, melhorar ou MIGRAR prompts de agente para Gemini. Ativa em: prompts de agente Gemini, migração GPT → Gemini, agentes que deixam de chamar tools quando deveriam, que escrevem o nome da tool como texto, verbosos demais, ou que ignoram regras absolutas. Ativa quando o usuário menciona Gemini 3, gemini-3.1-flash-lite, thinking levels, ou compara Gemini vs GPT em produção. Ativa também para a camada comercial: agente que 'soa como IA/robô' ou tem 'cara de IA', quebra de objeções, insistência/persistência comercial, humanizar conversa, agente que recita a KB como script, ou que promete capacidade que não tem (ex: 'ver horários' sem tool de agenda)."
---

# AI Agent Prompt Builder (Gemini-Optimized)

Cria e otimiza system prompts e bases de conhecimento para agentes de IA conversacionais em produção, rodando em modelos **Google Gemini 3** — com foco principal no **Gemini 3.1 Flash-Lite**, modelo mais cost-efficient da família e ideal para chatbots de alto volume.

Esta skill é a versão Gemini da `ai-agent-prompt-builder` (GPT). O **núcleo é o mesmo** — construir o menor conjunto de tokens de alto sinal que maximize o resultado, separando prompt (princípios) de KB (fatos). O que muda são as inversões específicas do Gemini abaixo. A configuração de API/deploy fica num apêndice no fim, pra não inflar o núcleo.

> **Nota de calibragem (versão revisada).** As recomendações aqui foram validadas contra a documentação oficial do Google (guia de prompting do Gemini 3, docs de function calling) e contra um caso real em produção (agente Raquel, ver "Lições Aprendidas"). Onde a prática contradiz o folclore, a prática venceu — em especial sobre notação de tool, que era superdimensionada, e sobre a tool `think`, que na prática da AtendMax é padrão porque melhora o desempenho em raciocínio (datas, cálculos, repensar), não algo a descartar (ver §6 e apêndice).

## Por que uma skill separada da versão GPT

Gemini 3 e GPT-4.1 interpretam prompts de formas diferentes. Um prompt GPT roda no Gemini, mas há ajustes que melhoram aderência. As inversões reais:

| Aspecto | GPT-4.1 | Gemini 3 |
|---|---|---|
| Verbosidade padrão | Verboso, precisa frear | Conciso, precisa pedir pra ser conversacional |
| Tamanho do prompt | Quanto mais detalhe, melhor | Prefere direto; pode super-analisar prompt inflado |
| Constraints negativos | Funcionam em qualquer posição | **Devem ficar no FINAL** (oficial) |
| Formato (XML/Markdown) | Aceita mistura | **Não misture** — escolha um (XML e Markdown funcionam igual) |
| Persona | Segue mas não dramatiza | Leva a sério, pode performar a ponto de ignorar regra |
| Temperature | 0.3–0.7 típico | **Manter 1.0 (default)** — abaixar causa loops |
| Notação `[tool]` em exemplos | Meta-notação | Raramente vaza com function declarations reais; ainda assim, notação clara é boa prática |
| Raciocínio explícito | Induzido via prompt | `thinking_level` como parâmetro de API |
| Disciplina de tool | Tende a chamar quando manda | Pode **deixar de chamar** tool condicional ("resolve na mão") |

**Implicação prática:** migrar é, na maior parte, ajuste estrutural — não uma reescrita do zero. O risco real do Gemini **não** é vazar tool como texto (isso quase não acontece com declarations reais); é **deixar de chamar** uma tool condicional e ignorar constraint que está cedo demais no prompt.

## Filosofia Central

O princípio central permanece: **encontrar o menor conjunto possível de tokens de alto sinal que maximize a probabilidade do resultado desejado.**

Para agentes Gemini, três pilares:

1. **Brevidade estrutural (iterativa, não dogmática).** Gemini 3 responde melhor a instruções diretas — remova repetição e o óbvio. Mas é um processo iterativo: corte, teste, e readicione detalhe se a qualidade cair. Não existe "% obrigatório": prompt longo e bem estruturado funciona; o problema é só repetição inflada.
2. **Constraints críticos no fim.** Negative constraints e regras absolutas fecham o prompt, não abrem.
3. **Disciplina de tool nos dois sentidos.** Que o modelo chame a tool certa **quando deve** (problema mais comum) e não escreva tool como texto (problema raro).

## Quando Ler os Arquivos de Referência

A KB é agnóstica de modelo, então a arquitetura de base de conhecimento é compartilhada com a skill GPT e mantida em `references/`. Leia antes de construir a parte de KB:

| Tarefa | Leia Primeiro |
|--------|--------------|
| Criar/reestruturar a base de conhecimento de um agente Gemini | `references/knowledge-base-architecture.md` |
| **Diagnosticar bug de retrieval (agente Gemini erra dado que está na KB)** | `references/knowledge-base-architecture.md` seção 7 (Chunking Semântico) |
| Build completo (prompt + KB) | Este `SKILL.md` (prompt) + `references/knowledge-base-architecture.md` (KB) |
| **Agente comercial/vendas: objeções, insistência, naturalidade ("cara de IA")** | `references/persuasao-e-naturalidade.md` |
| Agente recita a KB como script, solta lead na 1ª objeção, ou promete capacidade que não tem | `references/persuasao-e-naturalidade.md` §§ 1, 2 e 4 |

O conteúdo de prompt (constraints no fim, persona contida, gatilho de tool, etc.) é específico do Gemini e vive **neste** `SKILL.md`. A arquitetura de KB e a configuração de embeddings vivem na referência e no apêndice de deploy. Não duplique regra entre eles.

## Princípios Específicos do Gemini 3

### 1. Formato consistente (não misture XML com Markdown)
A regra oficial do Google é: **use XML ou Markdown como delimitador, escolha um e seja consistente no mesmo prompt.** Os dois funcionam igual — XML não "quebra" o Gemini. O que quebra é misturar (`<exemplos>` dentro de um prompt Markdown). Esta skill **padroniza Markdown** por dois motivos práticos: (a) os prompts da AtendMax já são majoritariamente Markdown, com XML só em `<exemplos>` e `<variaveis>`, então padronizar em Markdown é a conversão mais leve; (b) evita a tentação de misturar. Se um prompt já fosse XML consistente, manter XML também seria válido.

### 2. Verbosidade INVERSA
GPT é verboso por padrão; Gemini é conciso por padrão (oficial). Se você quer respostas curtas (típico em WhatsApp), pouco precisa instruir. Se quer um agente conversacional/caloroso, **precisa pedir explicitamente**.

### 3. Constraints negativos no FIM
Confirmado pela documentação oficial: o modelo pode ignorar restrições negativas, de formatação ou de quantidade se elas aparecerem cedo demais; coloque o pedido principal e as restrições mais críticas como a **última coisa** da instrução. Regras como "NUNCA invente preços", "NUNCA chame `transfere` duas vezes", "uma pergunta por vez" vão na seção final do prompt.

### 4. Persona contida
Gemini leva persona a sério e pode performar o papel a ponto de ignorar instruções operacionais. Use personas funcionais ("consultor objetivo") em vez de teatrais ("o melhor consultor da região, apaixonado por caminhões").

### 5. Notação de tool nos exemplos: clareza, não catástrofe
O function calling do Gemini é dirigido por **schema** — o modelo escolhe a função pelas declarations e suas descrições, não pela notação do exemplo. Com tools declaradas de verdade (caso de N8N/LangChain), a notação `[nome_da_tool]` nos exemplos **raramente vaza** como texto. (Em teste real, um prompt com 15 ocorrências de colchete rodou seis conversas sem vazar uma vez.) Ainda assim, a **notação anti-roleplay** (ver `## Padrão de Exemplos com Tools`) é mais limpa e recomendada para build novo — só não a trate como o ponto que decide a migração. Se um prompt GPT já usa colchete, isso **não** é motivo isolado pra reescrever tudo.

### 6. Thinking levels como parâmetro de API
Gemini 3.1 Flash-Lite suporta `thinking_level: minimal | low | medium | high`. **Não fixe `minimal` por padrão em agente pesado em tool.** Thinking baixo reduz a propensão a chamar tool e a raciocinar sobre data/cálculo — ou seja, `minimal` pode ser a própria causa de um agente "esquecer" de chamar `transfere` ou errar dia da semana. Heurística:
- Q&A simples, classificação: `minimal`/`low`.
- Agente conversacional pesado em tool e instrução (a maioria dos casos AtendMax): **teste `low` ou `medium`** — o raciocínio extra melhora seleção de tool e aderência a regra; o custo é latência.

**Padrão AtendMax: a tool `think` é padrão no N8N.** Na stack de produção da AtendMax (N8N), o fluxo declara uma tool `think` explícita por um motivo de desempenho: um passo de raciocínio antes de responder melhora justamente as tarefas onde o Flash-Lite mais tropeça, cálculo de datas, contas em geral, e qualquer decisão que se beneficia do modelo repensar antes de agir (seleção de tool, decisão de escalar, aderência a regra). É um scratchpad: o modelo pensa em voz alta ali, erra menos no reflexo. Um caso concreto desse ganho é a sub-chamada, a `think` obriga o agente a classificar o assunto ("é papo ou virou operacional/sério?") antes de decidir chamar `transfere`/`chamar_humano`. Ela não substitui o `thinking_level`: os dois convivem. Declare a `think` e rode em `low`, subindo pra `medium` se ainda faltar raciocínio em algum caso. O ponto de nunca fixar `minimal` segue firme, porque `minimal` derruba o próprio ganho que a `think` traz. Gatilho da `think` na descrição da função: usar antes de um cálculo (data, conta), antes de decidir escalar, e antes de compor uma fala factual; não usar num "oi" ou papo trivial que não pede raciocínio.

### 7. Temperature 1.0
Não baixe a temperature pra "deixar determinístico". No Gemini 3, temperature abaixo de 1.0 causa loops e degradação (oficial). Determinismo vem de instruções claras, não de temperature.

## Disciplina de Tool nos Dois Sentidos

### Sub-chamada: a tool que não dispara (problema mais comum no Gemini)
O Gemini, sendo prestativo, às vezes **resolve o assunto sozinho** em vez de invocar uma tool condicional (ex: não chamar `transfere` numa exceção que manda transferir; não consultar `info_*` e responder de cabeça). Três alavancas, em ordem:

1. **O gatilho mora na DESCRIÇÃO da tool, não só no corpo do prompt.** O Gemini pesa muito a descrição da função pra decidir quando chamar. Seja explícito: "Use sempre que o paciente pedir orçamento de medicação injetável, X, Y." (ver `## Padrão de Descrição de Tools`).
2. **Suba o `thinking_level`** (low/medium) — mais raciocínio, melhor decisão de chamar.
3. **Tool config / function calling mode** pra forçar chamada quando o fluxo exige determinismo.

### Verificação em dois passos (padrão oficial anti-alucinação)
Quando o modelo não tem a informação ou a capacidade, ele tende a inventar algo plausível pra atender. O padrão oficial é dividir em dois passos: **primeiro verifique se a informação/capacidade existe, depois responda.** Aplicação direta em agente: "Antes de oferecer qualquer data, consulte a agenda via tool. Se a tool não retornar, diga que vai verificar e NÃO invente horário." Isso ataca data inventada e o "resolver na mão".

### Sobre-chamada (mais raro)
Se o agente chama tool demais, baixe o `thinking_level` ou adicione uma instrução de orçamento: "Você tem um limite de N chamadas de tool por turno; use com eficiência."

## Raciocínio de Data e Cálculo

Não use "nunca calcule" nem "não infira" de forma ampla — isso faz o Gemini travar até em aritmética básica (ver anti-padrão). O certo é o **padrão positivo**:

- Injete os valores prontos no contexto (Data, Hora, dia da semana, Data+15, dia da semana do +15) e mande **usar esses valores** pra raciocinar: "Use a Data e a Data+15 fornecidas; não calcule datas de cabeça."
- Para casos de borda, dê a regra explícita: "Se a data piso cair em sábado ou domingo, avance para o próximo dia útil **antes** de oferecer."
- Quando possível, prefira que a **tool** devolva o dado já mastigado (intervalos livres + dia da semana prontos), em vez de pedir cálculo ao modelo.
- Um passo de `think` antes de responder ajuda o modelo a raciocinar sobre esses valores (conferir o dia da semana, aplicar a regra de pular fim de semana, revisar uma conta) em vez de responder no reflexo. É um dos motivos de a `think` ser padrão na AtendMax (ver §6).

## Padrão de Exemplos com Tools

A notação anti-roleplay deixa inequívoco que tool é algo **executado**, não escrito. Recomendada para build novo (não é obrigatória para migração — ver princípio #5).

### Notação anti-roleplay (recomendada)

Use seções separadas para texto do agente vs ação de tool:

```markdown
**Exemplo: Handoff**

Lead: BH, tenho 3 VW Delivery hoje na empresa

> Raciocínio interno do agente (via tool `think`):
> "Tenho nome (Ricardo), cidade (BH), veículo (1217). Dados completos. Hora de transferir."

Resposta do agente ao lead:
"Faz sentido pra essa operação, Ricardo. Vou te conectar com nosso consultor comercial agora pra montar a melhor proposta."

Ação de tool executada: invocar `transfere` (sem argumentos visíveis ao lead).
```

### Evite a notação colada (mistura resposta + ação)

```
Eustáquio: Vou te transferir agora.
[transfere]
```

Não porque o colchete necessariamente vaza (raramente vaza com declarations reais), mas porque colar a "ação" na "fala" é ambíguo. A separação visual ensina melhor.

### Reforço explícito no prompt

Após os exemplos, incluir uma seção curta:

```markdown
## Disciplina de Tools (LEIA COM ATENÇÃO)

Quando os exemplos mostram "Ação de tool: invocar `transfere`", isso significa que você DEVE chamar a função via function calling do sistema. Você NUNCA escreve o nome da tool, colchetes ou a descrição da ação na mensagem ao lead — a mensagem contém apenas texto natural. E o inverso também vale: quando uma regra manda chamar uma tool (ex: transferir num caso específico), você DEVE chamá-la, não resolver por conta própria.

Se você não consegue invocar a tool, NÃO finja que invocou. Diga ao lead que houve um problema técnico e que vai verificar.
```

## Estrutura Recomendada do Prompt (Gemini)

A ordem importa. Sequência que melhor performa em Gemini 3.1 Flash-Lite:

```markdown
# Identidade e Objetivo
[curto, funcional, sem teatralidade]

# Tom de Voz
[se quer respostas conversacionais, peça aqui — Gemini default é seco. Em agente comercial de WhatsApp, inclua a sub-seção "Como NÃO soar robô" — ver Camada Comercial]

# Saudações / Convenções de Linguagem
[fatos rápidos: horários, formato de saudação]

# Ferramentas Disponíveis
[descrições explícitas e granulares — ver Padrão de Descrição de Tools]

# Fluxo de Conversa
[etapas em alto nível, princípios não scripts]

# Princípios de Decisão
[heurísticas, frameworks de classificação; em agente comercial: framework de objeções (validar → contextualizar → teto de 3 → sem fabricar) e tom por ICP]

# Exemplos
[2-3 conversas canônicas no padrão anti-roleplay]

# Disciplina de Tools
[reforço: tool é executada, não escrita; e tool obrigatória é chamada, não resolvida na mão]

# Contexto Variável
[data, hora, dia da semana, valores +15 — injetados via N8N]

# Regras Invioláveis (FIM DO PROMPT — última coisa antes da execução)
[constraints negativos absolutos: NUNCA invente preço, NUNCA chame transfere 2x, sempre consulte info_* antes de afirmar fato, uma pergunta por vez, etc.]
```

**A inversão mais importante vs prompt GPT:** "Regras Invioláveis" no fim. No GPT ficavam logo após Identidade; no Gemini, fechar o prompt com elas é o que garante aderência (oficial).

## Padrão de Descrição de Tools

Esta é a alavanca nº1 contra sub-chamada. O Gemini é muito sensível à qualidade da descrição da função — é por ela que ele decide **quando** chamar. Cada tool deve seguir:

```markdown
**nome_da_tool**

Descrição funcional curta: o que a tool faz, em uma frase.

QUANDO usar:
- Situação 1 específica e concreta (descreva como explicaria a um colega no primeiro dia)
- Situação 2 específica

QUANDO NÃO usar:
- Antipadrão 1
- Antipadrão 2

Como invocar: descrição neutra (ex: "Chame com palavras-chave descritivas como 'objeção marca chinesa'").

Tratamento de falha: o que fazer se a tool retornar erro.
```

Tanto o `QUANDO usar` (combate sub-chamada) quanto o `QUANDO NÃO usar` (combate sobre-chamada) importam mais no Gemini que no GPT. Para tools de escalação (`transfere`) e de consulta (`info_*`), capriche no `QUANDO usar` com gatilhos concretos — é o que faz o modelo disparar quando deve.

**Tools acopladas:** quando duas tools devem SEMPRE disparar juntas (ex.: resumo + transferência), coloque cross-reference nas DUAS descriptions ("sempre que chamar esta, chame também X") e espelhe nas Regras Invioláveis. Se o acoplamento for crítico ("o resumo nunca pode faltar"), encadeie a segunda no fluxo do N8N em vez de confiar no LLM — determinístico ganha. Detalhe em `references/persuasao-e-naturalidade.md` §5.

## Camada Comercial: Objeções, Insistência e Naturalidade

Para agentes de venda/conversão (SDR, pré-atendimento, reativação), a estrutura acima não basta — o que separa um agente que converte de um bot que responde é a camada comercial. O detalhe completo (frameworks, formatos de KB, checklist) está em `references/persuasao-e-naturalidade.md`; leia antes de construir agente comercial. Resumo dos cinco pilares:

1. **Quebra de objeções:** validar antes de contornar → **contextualizar no cenário que o lead trouxe** (nunca frase de manual) → teto de **3 tentativas** com ângulos diferentes (soltar na 1ª é erro; insistir além de 3 também) → **nunca fabricar** pra convencer (desconto/urgência/"agendei" falsos) → ler sinal de saída real. Codifique em Princípios de Decisão + Invioláveis + **1 exemplo multi-turno mostrando as 3 tentativas e o encerramento**.
2. **KB como matéria-prima, não script:** princípios de contorno no PROMPT; **ângulos** (não scripts fechados) na KB; a fala é montada fresca no contexto. Regra explícita: "nunca recite o script da KB palavra por palavra". Script pronto na KB + Flash-Lite = recitação robótica.
3. **Anti-"cara de IA":** os padrões que entregam IA no WhatsApp — nome do lead em toda mensagem, aberturas formulaicas ("Entendido/Perfeito" todo turno), linguagem de folheto, validações empilhadas, travessão/em-dash, 4-6 balões por turno. Codifique como seção "Como NÃO soar robô" no Tom de Voz + espelho nas Invioláveis + demonstração nos exemplos. (E cheque o split de balões no N8N — pipeline também causa isso.)
4. **Limites de capacidade honestos:** para cada capacidade que o agente NÃO tem (ex.: agenda), proíba **a linguagem que a implica** ("vou ver os horários"), não só a ação. Padrão substituto: colher preferência como insumo + handoff com papel claro ("a secretária que cuida da agenda te retorna").
5. **Persona comercial saudável:** mentalidade na identidade ("comissionada por conversão, mas pressão não converte — você vende cuidando") + tom por ICP com sinais de identificação e um exemplo por registro. Em vertical médica: nunca explorar insegurança/vergonha/medo como alavanca.

## Workflow de Criação ou Migração

### Cenário A: Criar Agente Novo do Zero (Gemini)

1. **Briefing** — Identidade, plataforma, objetivo, tools, regras de negócio, escalação.
2. **Arquitetura** — Separe System Prompt (princípios) e KB (fatos). Para a KB, siga `references/knowledge-base-architecture.md`, em especial a seção 7 (Chunking Semântico).
3. **Build** — Use a estrutura acima. Comece direto e enxuto; readicione detalhe se a qualidade cair.
4. **Descrições de tool** — Caprichar nos gatilhos `QUANDO usar`.
5. **Exemplos** — 2-3 canônicos no padrão anti-roleplay.
6. **Regras Invioláveis no fim** — Últimas linhas.

### Cenário B: Migrar Agente Existente de GPT-4.1 → Gemini 3.1 Flash-Lite

A migração é, na maior parte, ajuste estrutural — não reescrita do zero. Roteiro:

#### Passo 1: Diagnóstico do prompt GPT atual
- Mistura XML com Markdown? → Padronizar num formato só (Markdown é a conversão mais leve se o prompt já é majoritariamente Markdown). XML consistente também pode ficar.
- Regras absolutas estão no início? → **Mover pro fim.**
- Tem ALL CAPS abusivo? → Reduzir.
- Tem instruções tipo "seja caloroso, próximo"? → **Manter ou reforçar** (Gemini é seco por default).
- Persona dramática? → Tornar funcional.
- Os gatilhos das tools (transfere, info_*) estão claros na descrição da função? → Reforçar (alavanca contra sub-chamada).
- (Opcional) Exemplos usam `[tool]`? → Migrar pro padrão anti-roleplay é bom, mas não é bloqueador — só não misture com a fala.

#### Passo 2: Reescrita estrutural
- Mover regras absolutas pra `# Regras Invioláveis` no fim.
- Reforçar gatilhos nas descrições de tool.
- Adicionar `## Disciplina de Tools` (anti-roleplay E anti-sub-chamada) após exemplos.
- Padronizar o formato (sem mistura). Enxugar repetição; manter o sinal alto.

#### Passo 3: Configuração no N8N
Ver apêndice "Configuração e Deploy (Gemini)" no fim.

#### Passo 4: Validação A/B
Antes de promover, validar em paralelo com a versão GPT:
1. **Tool calling correto** — invoca `transfere`/`info_*` **quando deveria** (sub-chamada é o risco principal)? Escreve como texto (raro)?
2. **Aderência a regras absolutas** — chama `transfere` só uma vez? Não inventa preços? Consulta info_* antes de afirmar?
3. **Raciocínio de data** — usa os valores injetados, pula fim de semana, não inventa horário?
4. **Tom e brevidade** — respeita "2-3 frases por bloco"? Não ficou robótico demais?

Reprovou em 1, 2 ou 3 → estrutural (gatilho de tool, regra no fim, thinking_level). Reprovou em 4 → ajuste fino de tom.

### Cenário C: Debug de Agente Gemini Que Está Falhando

| Sintoma | Diagnóstico provável | Correção |
|---|---|---|
| **Deixa de chamar tool obrigatória (resolve na mão)** | Gatilho fraco na descrição da função + thinking baixo | Reforçar `QUANDO usar` na descrição da tool; subir `thinking_level`; considerar tool config forçando a chamada |
| Inventa dado (preço, endereço, horário) | KB/agenda não consultada antes de responder | Aplicar verificação em dois passos: "consulte a tool antes; se não retornar, diga que vai verificar" |
| Escreve `[tool]` como texto (raro) | Notação colada à fala nos exemplos | Migrar exemplos pro padrão anti-roleplay |
| Chama `transfere` várias vezes | Constraint absoluto cedo demais | Mover pra Regras Invioláveis no fim |
| Respostas longas demais | Persona teatral ou falta de instrução de brevidade | Persona funcional; reforçar "máximo 2-3 frases" no fim |
| Faz múltiplas perguntas por vez | Regra "uma pergunta por vez" enterrada | Mover pra Regras Invioláveis no fim |
| Erra cálculo de data / dia da semana | "Não calcule" amplo demais, ou modelo calculando de cabeça | Injetar valores prontos + mandar usá-los; regra de pular fim de semana; idealmente tool devolve dado mastigado |
| Usa contexto obsoleto (ex: id de agendamento cancelado) | **Dado sujo injetado** — Gemini usa fielmente o que recebe | Limpar a origem do dado (backend), não o prompt; o Gemini não ignora dado obsoleto como o GPT |
| Erra dado factual que está na KB | **Bug de retrieval**, não de prompt | `references/knowledge-base-architecture.md` seção 7. NÃO reforçar regra no prompt — só infla tokens |
| **Soa robótico / "cara de IA"** (nome em toda msg, "Entendido/Perfeito" todo turno, linguagem de folheto) | Falta de anti-padrões de naturalidade no prompt (e/ou split de balões no N8N) | Seção "Como NÃO soar robô" no Tom de Voz + espelho nas Invioláveis + exemplos que demonstram; checar split no N8N. `references/persuasao-e-naturalidade.md` §3 |
| Solta o lead na 1ª objeção OU insiste sem parar | Sem framework de persistência com teto | Framework validar → contextualizar → teto de 3 + exemplo multi-turno das 3 tentativas. §1 do reference |
| Responde objeção com frase de manual / recita a KB palavra por palavra | KB com script fechado + sem regra de composição | Converter seções OBJEÇÃO pra ângulos; regra "não recite a KB"; §2 do reference |
| Diz que vai "ver horários / consultar disponibilidade" sem ter tool de agenda | Capacidade implicada não proibida (proibiu a ação, não a linguagem) | Proibir a linguagem que implica a capacidade + padrão de handoff com papel claro; §4 do reference |

## Anti-Padrões Específicos do Gemini

1. **Misturar XML com Markdown.** Escolha um formato e siga (XML ou Markdown — os dois funcionam, só não misture).
2. **ALL CAPS abusivo.** Gemini dá menos peso a CAPS que GPT. Use **negrito** e posicionamento no fim.
3. **Notação de tool colada à fala** nos exemplos. Prefira o padrão anti-roleplay (separar resposta de ação) — não porque o colchete sempre vaza, mas por clareza.
4. **Persona teatral.** "Você é o melhor consultor, apaixonado por caminhões" → o Gemini performa isso e ignora regra operacional.
5. **Constraints negativos no início.** Mais ignorados que no fim (oficial).
6. **Temperature abaixada.** Determinismo via instrução, não temperature.
7. **Instruções abertas demais.** "Não infira" / "não chute" sem qualificação faz o Gemini travar em dedução básica. Prefira "Use apenas as informações de info_* e da conversa atual para suas deduções".
8. **Fixar `thinking_level: minimal` em agente pesado em tool.** Minimal reduz chamada de tool e raciocínio — pode ser a causa de sub-chamada e de erro de data, e derruba a utilidade da tool `think`. Teste low/medium nesses casos.
9. **Scripts fechados de objeção na KB.** "Script Principal" pronto na KB + Flash-Lite = o agente cola o script e soa decorado. Use ângulos de contorno na KB e componha a fala no contexto do lead (`references/persuasao-e-naturalidade.md` §2).
10. **Proibir a ação mas não a linguagem.** "Você não acessa a agenda" sem proibir "vou ver os horários" deixa o agente implicar a capacidade que não tem. Proíba a linguagem que implica (§4 do reference).

## Checklist de Qualidade Pre-Deploy

- [ ] Prompt usa um formato consistente (Markdown OU XML, sem mistura)
- [ ] Regras absolutas estão na ÚLTIMA seção do prompt
- [ ] Descrições de tool têm `QUANDO usar` com gatilhos concretos (anti-sub-chamada) e `QUANDO NÃO usar`
- [ ] Existe seção `## Disciplina de Tools` cobrindo os dois sentidos (não escrever como texto / não deixar de chamar)
- [ ] Verificação em dois passos onde há risco de invenção (datas, fatos, capacidades)
- [ ] Raciocínio de data usa valores injetados + regra de pular fim de semana
- [ ] Persona é funcional, não teatral
- [ ] Não há ALL CAPS abusivo nem "não infira" amplo
- [ ] `thinking_level` adequado ao agente (não `minimal` por padrão em agente pesado em tool)
- [ ] Tool `think` declarada como padrão no N8N (melhora raciocínio: datas, cálculos, repensar antes de escalar/agir); roda junto com o `thinking_level`, não no lugar dele
- [ ] Temperature em default (1.0)
- [ ] N8N tratando thought signatures (ver apêndice)
- [ ] **(Agente comercial)** Framework de objeções presente: validar → contextualizar no cenário do lead → teto de 3 → sem fabricar → sinal de saída (+ exemplo multi-turno das 3 tentativas)
- [ ] **(Agente comercial)** Seções OBJEÇÃO da KB em formato de **ângulos** (não script fechado) + regra "não recite a KB" no prompt
- [ ] **(Agente comercial)** Checklist anti-"cara de IA" aplicado (nome só na 1ª msg/empatia, sem aberturas formulaicas, sem folheto, sem em-dash) e demonstrado nos exemplos
- [ ] Capacidades que o agente NÃO tem estão mapeadas com a **linguagem que as implica proibida** (ex: "vou ver os horários" sem tool de agenda)
- [ ] Tools acopladas com cross-reference nas duas descriptions (ou encadeadas deterministicamente no N8N)
- [ ] Testado pelo menos 6 conversas reais cobrindo os casos difíceis antes de promover

## Lições Aprendidas (Casos Reais AtendMax)

### Caso Raquel (Ayra Clínica) — migração GPT-4.1 → Gemini 3.1 Flash-Lite

Agente pesado em tool (~13 tools: agenda, RAG, transfere, notificações, cancelamento). Testado no Gemini 3.1 Flash-Lite com o prompt GPT (ainda não reescrito), seis conversas cobrindo agendamento, escalação e fatos. Resultados que recalibraram esta skill:

1. **Notação de tool não vazou.** O prompt tinha 15 ocorrências de `[tool]` em colchete (incluindo `[transfere]`). Em seis conversas, **nenhum vazamento**. Confirma que, com function declarations reais (N8N), a notação dos exemplos quase não causa o bug que se temia. → o medo da notação estava superdimensionado.
2. **Sub-chamada apareceu.** Numa exceção que mandava transferir (orçamento de injetável), o agente **resolveu sozinho** em vez de chamar `transfere`. Esse é o risco real do Gemini, e a correção é gatilho na descrição da tool + thinking_level, não notação.
3. **Contexto sujo virou bug.** Um `id_agendamento` órfão (de um agendamento cancelado que o backend não limpou) foi usado fielmente pelo Gemini, que saudou referindo um agendamento inexistente. O GPT ignorava; o Gemini não. → higiene de contexto é Gemini-específica; conserto é no dado, não no prompt.
4. **Raciocínio de data.** O piso de 15 dias caiu num sábado e o agente propôs o sábado em vez de pular pro dia útil. → injetar valor pronto + regra explícita de pular fim de semana.
5. **Bug de pipeline ≠ bug de modelo.** Uma mensagem que misturava texto + link de PDF foi roteada errada por um Switch single-path no N8N — nada a ver com o prompt nem com o Gemini.

**Lição genérica:** migrar da AtendMax de GPT pra Gemini é **ajuste estrutural** (regras no fim, gatilho de tool, thinking_level, formato consistente), não reescrita do zero nem caça a colchetes. Valide os casos difíceis (escalação condicional, raciocínio de data, encadeamento de tools) antes de promover.

### Caso agente de clínica médica — agente comercial nativo Gemini + teste em conversa real

Agente de pré-atendimento/conversão (nutrologia) construído nativo pra Gemini 3.1 Flash-Lite com a estrutura desta skill. O teste em conversa real passou nas regras duras (consultou KB antes do preço, transferiu no momento certo) mas expôs a camada que faltava:

1. **"Cara de IA" mesmo com prompt estruturado.** Nome do lead em quase toda mensagem, turnos abrindo com "Entendido/Entendi/Perfeito", linguagem de folheto ("divisor de águas", "excelente ponto de partida") e 4-6 balões por turno. Regra de tom genérica não previne; foi preciso codificar os **anti-padrões explícitos** + demonstrar nos exemplos. → virou o §3 do reference.
2. **Capacidade implicada.** O agente (sem tool de agenda) ofereceu "ver os horários disponíveis". Proibir a ação não bastou — foi preciso proibir a **linguagem** e dar o padrão substituto (colher preferência + handoff com papel claro). → §4.
3. **Recitação da KB.** Scripts fechados de objeção na KB saíam palavra por palavra. Correção: ângulos na KB + regra "não recite" + composição no contexto. → §2 (e o kb-template foi atualizado).
4. **Framework de persistência é portável entre nichos.** O framework maduro de um agente de academia (validar → contextualizar → teto de 3 → sem fabricar) portou pra vertical médica com um guardrail extra: nunca explorar insegurança/vergonha/medo do paciente como alavanca. → §1 e §6.
5. **Tools acopladas.** Resumo + transferência deviam sempre disparar juntas; cross-reference nas duas descriptions resolveu, com encadeamento no N8N como opção determinística. → §5.

**Lição genérica:** a estrutura Gemini (regras no fim, gatilhos, thinking) garante *obediência*; a camada comercial (`references/persuasao-e-naturalidade.md`) garante *conversão e naturalidade*. Agente de venda precisa das duas — e o teste de conversa real é o que revela a segunda.

## Quando NÃO usar Gemini 3.1 Flash-Lite

O Google posiciona o 3.1 Flash-Lite como caminho de migração confiável para chatbots complexos e pesados em instrução, e ele iguala o 2.5 Flash em capacidade. A Raquel (~13 tools) rodou bem nele. Então a régua é mais alta do que parecia. Considere subir pra **Gemini 3 Flash padrão** (mais caro, mais inteligente) ou manter GPT-4.1 em casos como:

- Verticais críticas onde alucinação tem custo alto (médico/jurídico) e o thinking_level alto no Flash-Lite não basta.
- Agentes onde a empatia/persona é o produto principal (terapia, suporte emocional).
- KBs muito ambíguas que exigem o reasoning do Flash padrão.

A quantidade de tools, por si só, **não** é critério pra evitar o Flash-Lite — a alavanca é thinking_level + descrições de tool fortes.

## Formato de Saída

Ao criar agentes Gemini do zero, entregue:
1. `prompt-[nome-agente]-gemini.md` — System prompt otimizado pra Gemini
2. `kb-[nome-agente].md` — Base de conhecimento (siga `references/knowledge-base-architecture.md`; estrutura idêntica à da skill GPT, KB é agnóstica de modelo)

Ao migrar agente existente, entregue:
1. Documento de análise: o que mudou e por quê
2. `prompt-[nome-agente]-gemini.md` — Versão migrada
3. Checklist de validação A/B preenchível

Ao debugar, entregue:
1. Diagnóstico (sintoma → causa raiz)
2. Patch específico
3. Sugestão de teste pra confirmar o fix

---

## Apêndice: Configuração e Deploy (Gemini no N8N)

Isto não é prompt — é a config de API/infra que faz o prompt funcionar. Mantido separado do núcleo.

### Modelo e parâmetros
- Modelo: `gemini-3.1-flash-lite-preview` (modelo preview; comportamento pode mudar).
- `thinking_level`: comece em `low`; suba pra `medium` se houver sub-chamada de tool ou erro de data; `minimal` só pra fluxos simples e latência crítica. (Não fixe `minimal` por padrão em agente pesado em tool.)
- `temperature`: default `1.0`. Não baixe (causa loops).
- Se usar a camada de compatibilidade OpenAI, o `reasoning_effort` é mapeado automaticamente pra `thinking_level`.
- Tool `think`: no N8N, declare uma tool `think` explícita como padrão (é o que a AtendMax roda em produção). Melhora o desempenho em tarefas de raciocínio, cálculo de datas, contas em geral, decisões que pedem repensar (seleção de tool, escalação), funcionando como um scratchpad antes da resposta. Roda junto com o `thinking_level`, não no lugar dele.

### Thought signatures e IDs de função (pegadinha de N8N)
O Gemini 3 valida thought signatures de forma mais estrita e retorna um `id` único por function call. Para manter contexto em fluxos com várias tools (sequências de agendamento, por exemplo), as signatures e os IDs precisam voltar nas requisições seguintes. Os SDKs oficiais fazem isso sozinhos; verifique se o nó/community node do Gemini no seu N8N trata — versões antigas podem dar erro 400 ou perder contexto entre passos. Não concatene partes que carregam signature.

### Embeddings (RAG)
- Embedding e LLM são **desacoplados**: migrar o LLM pra Gemini **não** exige trocar o embedder. Não troque o embedder como parte da migração do LLM.
- Use o **mesmo modelo** pra indexar e pra consultar. Trocar de modelo de embedding = re-indexar tudo (vetores incompatíveis entre modelos).
- Modelos atuais (2026): `gemini-embedding-001` (texto, flagship; forte em multilíngue/PT), `gemini-embedding-2-preview` (multimodal, preview), e `text-embedding-3-small` da OpenAI (mais barato pra texto). Qualquer um serve; o importante é consistência e não trocar no meio.
- **Task types (ganho de qualidade no gemini-embedding-001):** use `RETRIEVAL_DOCUMENT` ao indexar documentos e `RETRIEVAL_QUERY` ao embeddar a pergunta. Sem task type, o default é `RETRIEVAL_QUERY` para ambos — subótimo, porque pergunta e resposta nem sempre são semanticamente parecidas. Ressalva: o nó de embedding padrão do N8N costuma **não** expor o task_type; pra usar, é uma chamada HTTP direta à API. Se for usar, re-indexe a KB inteira com `RETRIEVAL_DOCUMENT`.
- Truncamento MRL: 768 dimensões é o ponto recomendado de produção (qualidade quase plena, 1/4 do storage).

## Assets

- `assets/kb-template.md` — Template inicial para novas bases de conhecimento (agnóstico de modelo; idêntico ao da skill GPT). O template de prompt não é um asset separado porque a estrutura recomendada já está inline neste `SKILL.md`.
