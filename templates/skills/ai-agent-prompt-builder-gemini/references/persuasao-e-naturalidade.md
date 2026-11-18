# Persuasão, Objeções e Naturalidade (Agentes Comerciais Gemini)

Este reference cobre a camada COMERCIAL e de NATURALIDADE de agentes Gemini: como o agente insiste sem ser chato, quebra objeções dentro do contexto do lead, usa a KB como matéria-prima (não como script), e não soa como IA. Nasceu do ciclo de um agente de clínica médica: uma conversa real de teste soou visivelmente "cara de IA", o agente ofereceu uma capacidade que não tinha (ver agenda) e recitava scripts da KB. As correções foram validadas portando o framework de um agente comercial maduro (agente de vendas de academia em produção) com guardrails de vertical médica.

Leia quando: o agente é de vendas/conversão; o usuário reclama de "cara de IA"; o agente solta o lead na primeira objeção (ou insiste sem parar); o agente recita a KB; o agente promete capacidade que não tem.

---

## 1. Framework de Quebra de Objeções (5 regras)

A maioria dos "vou pensar / tá caro / tô sem tempo / não sei" no primeiro turno esconde **uma dúvida só**. O erro nos dois extremos: soltar o lead na primeira objeção mole (perde venda) e insistir sem teto (queima a marca). O framework:

### 1.1 Validar antes de contornar
Reconheça a objeção primeiro ("entendo", "faz sentido", "imagino"), depois responda. Nunca rebata seco. Uma validação curta e sincera — não empilhe três.

### 1.2 Contextualizar no cenário que o lead trouxe (a regra de ouro)
Não responda objeção com frase genérica de manual. Use o que o lead **acabou de dizer**.

- Lead: "tô sem tempo por causa do trabalho" → fale de como o serviço se encaixa na rotina DELE (horário flexível, praticidade), não "entendemos que a vida é corrida".
- Lead: "já tentei de tudo e não funcionou" → fale do que a abordagem investiga que ele ainda não olhou, não "nosso método é diferenciado".

**Teste rápido:** se a resposta de contorno funcionaria colada em qualquer conversa, ela é genérica demais. A objeção é sempre respondida dentro da situação específica do lead.

### 1.3 Teto de persistência: até 3 tentativas
Para cada objeção real, o agente tenta contornar — no máximo **3 vezes ao longo da conversa**, com ângulos diferentes (não repetindo o mesmo argumento). Depois de 3, se o lead seguir firme no não: respeite, encerre com elegância, deixe a porta aberta. Codifique os dois erros como invioláveis: "soltar na primeira objeção é erro grave; insistir além de 3 também".

### 1.4 Nunca fabricar para convencer
Contornar mentindo é pior que não contornar. É fabricação (proibir explicitamente):
- Prometer desconto, brinde ou condição que não existe / não foi confirmada na KB.
- Inventar urgência ("últimas vagas", "só hoje") que não é real.
- Dizer que "registrou", "agendou", "encaixou" ou "encaminhou" algo que não fez via tool.
- Em vertical médica/saúde: prometer resultado, prazo ou cura.

Reconquiste só com o que é real: ouvir, mostrar o que o serviço tem, apresentar o próximo passo.

### 1.5 Ler o sinal de saída real
Se o lead pede explicitamente para parar de receber mensagem, ou já recusou após os 3 contornos: encerrar com elegância imediatamente. Sem "última tentativa" depois do pedido de saída.

### Onde cada peça mora no prompt
- Regras 1.1–1.5 resumidas em **Princípios de Decisão** (seção "Objeções — como contornar").
- Os dois erros (soltar cedo / insistir demais) + "nunca fabrique" espelhados em **Regras Invioláveis** (fim do prompt).
- **1 exemplo multi-turno** mostrando as 3 tentativas com ângulos diferentes E o encerramento elegante na 3ª — o Gemini aprende o teto muito melhor vendo a sequência inteira do que lendo a regra.

### Guardrail extra para vertical médica/saúde
Persistência é ética quando alinhada ao interesse do paciente. Adicione às invioláveis: **nunca explorar insegurança, vergonha ou medo do paciente como alavanca de pressão** — são dores a acolher, não gatilhos. E enquadre a mentalidade comercial na identidade: "pense como comissionada por agendamento, mas pressão não agenda; seu interesse comercial e o do paciente apontam para o mesmo lugar: você vende cuidando."

---

## 2. KB Como Matéria-Prima, Não Script (objeções)

**Sintoma:** o agente responde objeções com o texto da KB palavra por palavra. Soa decorado, quebra o fluxo, e ignora o que o lead disse. No Gemini (especialmente Flash-Lite) isso é agravado: script pronto na KB = caminho de menor esforço = colar o script.

**A divisão correta:**

| Camada | O que carrega | Onde vive |
|---|---|---|
| Princípios de contorno (validar, contextualizar, teto de 3) | COMO contornar | Prompt |
| Ângulos e fatos por objeção (argumentos, dados, diferenciais) | COM O QUÊ contornar | KB (seções OBJEÇÃO) |
| A fala final | Montada fresca no contexto do lead | Nem prompt nem KB — composição em runtime |

**No prompt**, regra explícita (Tom de Voz + Invioláveis): "Nunca recite o script da KB palavra por palavra. A KB é matéria-prima; monte a fala fresca, no contexto do que o lead acabou de dizer."

**Na KB**, formato da seção OBJEÇÃO com ângulos em vez de script fechado:

```markdown
## OBJEÇÃO: Tempo / "Estou sem tempo"
Tags: sem tempo, corrido, ocupado, agenda lotada, rotina

### Contexto
[Quando essa objeção aparece e o que costuma esconder]

### Ângulos de contorno (matéria-prima — adapte ao que o lead disse, não recite)
- [Ângulo 1: ex. o serviço foi desenhado pra rotina intensa — encaixe, praticidade]
- [Ângulo 2: ex. o custo de adiar — o que continuar como está custa pra ELE]
- [Ângulo 3: ex. o primeiro passo é menor do que ele imagina]

### Fatos de apoio (se houver na base)
- [Dado real que sustenta os ângulos: horários, formato, duração]

### Transição
"[Pergunta ou convite curto que devolve a conversa ao avanço]"
```

O agente escolhe UM ângulo que casa com o cenário do lead e compõe. Três ângulos ≠ três parágrafos despejados.

---

## 3. Checklist Anti-"Cara de IA" (WhatsApp)

Padrões que entregam texto de IA em conversa de WhatsApp — cada um com a correção. Codifique como seção "Como NÃO soar robô" dentro do Tom de Voz, espelhe os críticos nas Invioláveis, e **demonstre nos exemplos** (o Gemini copia exemplos mais do que obedece regra).

| Padrão robótico | Correção |
|---|---|
| Nome do lead em toda mensagem ("Entendi, João. / Perfeito, João.") | Nome na **primeira** mensagem e em momentos genuínos de empatia — não em todo turno |
| Abertura formulaica repetida ("Entendido" / "Entendi" / "Perfeito" abrindo todo turno) | Variar ou simplesmente responder direto |
| Linguagem de folheto/marketing ("excelente ponto de partida", "divisor de águas", "cuidar da sua saúde com foco em...") | Linguagem falada: "faz sentido", "olha", "muita gente chega assim" |
| Empilhar validações ("é muito comum... justamente porque... exatamente por isso...") | Uma validação curta e sincera |
| Travessão/em-dash (—) nas mensagens | Vírgula, ponto, dois-pontos ou reticências (pessoas não digitam travessão no WhatsApp) |
| Recitar a KB palavra por palavra | Compor fresco (ver §2) |
| Todas as frases do mesmo tamanho | Misturar curtas com médias |
| 4–6 balões por turno | 2–3 frases por mensagem; explicou → pergunta |

**Pegadinha de pipeline (não é prompt):** se o N8N splita o output da IA por frase/quebra de linha antes de enviar, um turno de 3 frases vira 5-6 bolhas no WhatsApp — multiplicando a sensação robótica mesmo com prompt certo. Cheque o nó de split antes de culpar o prompt.

**Sobre "é robô?":** decisão de produto do cliente, não da skill. Se a diretriz for persona humana total (caso Iris), a regra vai nas invioláveis com instrução de naturalidade (sem negação defensiva). Se for transparência (recomendado em saúde/médico), o agente assume ser assistente virtual com leveza e redireciona — sem virar robótico por causa disso. Nos dois casos: **proíba o agente de se referir a si como "sistema", "programa" ou "máquina"** ao explicar limitações.

---

## 4. Limites de Capacidade Honestos (anti-implicação)

**Sintoma real (caso da clínica):** agente **sem tool de agenda** disse "prefere que eu veja o que temos disponível?" e "veja os horários disponíveis" — implicando uma capacidade que não tem. O lead espera horários; o agente não tem como entregar; a conversa quebra ou o agente inventa.

**Regra de construção:** para cada capacidade que o agente NÃO tem, proíba não só a ação mas **a linguagem que a implica**. "Você não acessa a agenda" é insuficiente; adicione: "nunca dê a entender que vai 'ver os horários' ou 'consultar a disponibilidade'".

**Padrão substituto (handoff com papel claro):**
1. **Colher a preferência** como insumo ("prefere manhã ou tarde? algum dia melhor?") — isso alimenta o resumo do handoff, não é o agente marcando.
2. **Enquadrar quem faz o quê**: "vou passar seu contato pra [pessoa/equipe] que cuida da agenda, ela vê os melhores horários e te retorna pra confirmar."
3. Disparar as tools de transferência.

Isso é a extensão do padrão "verificação em dois passos" do SKILL.md para o caso **capacidade** (não só informação): primeiro verifique se a capacidade existe (tem tool pra isso?); se não existe, o agente coleta insumo e transfere — nunca performa a capacidade.

---

## 5. Tools Acopladas (sempre disparam juntas)

Quando duas tools devem SEMPRE ser chamadas juntas (ex.: `resumo_conversa` + `transferir_humano` em toda transferência), o Gemini pode disparar só uma. Duas alavancas, em ordem de robustez:

1. **Cross-reference nas DUAS descriptions** + regra inviolável. Na description de cada tool: "Sempre que chamar esta tool, chame também `X` na mesma transferência." E nas Regras Invioláveis: "Na transferência, chame `A` e `B` juntas." Resolve a maioria dos casos.
2. **Encadeamento determinístico no N8N** (quando o acoplamento é crítico): em vez de deixar a segunda tool a cargo do LLM, dispare-a automaticamente no fluxo após a primeira (ex.: webhook de transferência chama o resumo em seguida). Trade-off: tool no agente = flexível (o LLM decide o conteúdo/momento); encadeada no fluxo = garantida. Para "o resumo nunca pode faltar", encadeie.

---

## 6. Persona Comercial Saudável e Tom por ICP

**Mentalidade na identidade (não só regras):** dê ao agente o *porquê* comercial e o limite na mesma frase — "pense como alguém comissionado por [conversão]: você genuinamente quer que o lead avance. Mas pressão não [converte] — quem [converte] é quem faz o lead se sentir compreendido e seguro. Seu interesse comercial e o do lead apontam para o mesmo lugar." Isso alinha a persistência (§1) com a ética sem depender só de proibições.

**Tom por ICP:** quando o agente atende públicos distintos (ex.: homem empresário objetivo × mulher com dor sensível), defina os **sinais de identificação** de cada ICP e o **registro** correspondente em Princípios de Decisão — e mostre um exemplo de cada registro. Sem isso, o Gemini usa um tom médio único que não serve bem a nenhum dos dois. Regra de fallback: "quando não estiver claro, pergunte antes de assumir o perfil."
