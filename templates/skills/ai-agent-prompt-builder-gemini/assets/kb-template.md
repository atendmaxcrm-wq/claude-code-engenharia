# Template de Base de Conhecimento

Use como ponto de partida para novas bases de conhecimento de agente. Substitua todos os placeholders entre colchetes. Adicione tags em toda seção.

---

```markdown
# BASE DE CONHECIMENTO — [NOME DA EMPRESA]

Última atualização: [DATA]
Notas de versão: [Breve descrição das mudanças recentes]

---

## INFO: Dados da Empresa
Tags: endereço, localização, direções, telefone, contato, email, website, estacionamento, horário

**Nome:** [Nome da Empresa]
**Endereço:** [Endereço completo]
**Telefone:** [Telefone]
**Email:** [Email]
**Website:** [URL]
**Redes Sociais:** [Handles]

**Como chegar:**
- [Direção 1]
- [Direção 2]
- **Estacionamento:** [Info de estacionamento]

**Horário de funcionamento:**
- [Faixa de dias]: [Horários]
- [Faixa de dias]: [Horários]
- [Dia fechado]: FECHADO

---

## INFO: Equipe e Autoridade
Tags: equipe, doutor, profissional, experiência, credenciais, autoridade, sobre, quem

**Profissional Principal:** [Nome e título]
**Posicionamento:** "[Frase de posicionamento da empresa]"

**Credenciais:**
- [Credencial 1]
- [Credencial 2]

**Métricas de Autoridade (usar consistentemente):**
- "[Métrica 1, ex: Mais de X anos de experiência]"
- "[Métrica 2, ex: Mais de X clientes atendidos]"
- "[Métrica 3, ex: Mais de X procedimentos realizados]"

**Filosofia:** [Breve declaração de filosofia da equipe]

---

## INFO: Serviços
Tags: serviços, tratamentos, produtos, especialidades, ofertas

**Serviço Principal:** [Serviço/produto carro-chefe]

**Lista Completa de Serviços:**
- **[Serviço 1]** — [Breve descrição]
- **[Serviço 2]** — [Breve descrição]
- **[Serviço 3]** — [Breve descrição]

**Público atendido:**
- [Segmento 1]
- [Segmento 2]
- [Exceções/encaminhamentos]

---

## INFO: Pagamento e Preços
Tags: pagamento, preço, valor, parcela, cartão, pix, financiamento, convênio, plano

**Formas de Pagamento:**
- [Forma 1]
- [Forma 2]
- [Forma 3]

**Política de Convênio/Plano:**
"[Script para lidar com perguntas sobre convênio — linguagem conversacional natural]"

---

## INFO: Diferenciais e Tecnologia
Tags: diferenciais, vantagens, por que escolher, tecnologia, equipamento, moderno

**Diferenciais-Chave:**
1. [Diferencial 1]
2. [Diferencial 2]
3. [Diferencial 3]

**Tecnologia:**
- [Tecnologia 1]
- [Tecnologia 2]

---

## SCRIPT: Oferta Especial / Convite Experiência
Tags: oferta, convite, experiência, cortesia, avaliação, promoção, especial

### Quando Usar
- Lead insiste em saber preços após qualificação adequada
- Lead mostra interesse mas hesita financeiramente
- Após tratamento de objeção de preço, para incentivar agendamento

### Regra
SEMPRE contextualize com a situação específica do lead antes de ofertar. Nunca apresente genericamente.

### O Que Inclui
- [Item 1]
- [Item 2]
- [Item 3]

### Script Completo (após contextualização)
"[Script natural apresentando a oferta, incluindo o que está incluído, o valor normal, e a chamada para ação]"

### Versão Curta (para plataformas de mensagem)
"[Versão condensada para WhatsApp/SMS]"

---

> **Como o agente deve usar as seções OBJEÇÃO:** são matéria-prima, não script. O prompt do agente deve conter a regra "nunca recite o script da KB palavra por palavra" — o agente escolhe UM ângulo que casa com o cenário que o lead trouxe e compõe a fala fresca. Ver skill Gemini, `references/persuasao-e-naturalidade.md` §2.

## OBJEÇÃO: Preço / "Quanto custa?"
Tags: preço, caro, valor, investimento, dinheiro, orçamento, quanto custa

### Contexto
Leads perguntando sobre preço antes de avaliação são muito comuns. O objetivo é redirecionar para qualificação mostrando empatia pela preocupação financeira.

### Ângulos de contorno (matéria-prima — adapte ao que o lead disse, não recite)
- [Ângulo 1: por que o valor depende da avaliação individual]
- [Ângulo 2: o custo de adiar / valor percebido antes do preço]
- [Ângulo 3: o primeiro passo é menor do que parece]

### Perguntas Técnicas (se insistirem)
- "[Pergunta que mostra complexidade]"
- "[Pergunta que mostra complexidade]"

### Fechamento
"[Linha que amarra de volta ao primeiro passo]"

### Transição
"[Como avançar para agendamento após endereçar]"

---

## OBJEÇÃO: Medo / "Tenho medo"
Tags: medo, receio, dor, ansiedade, trauma, nervoso, assustado

### Contexto
Medo é uma emoção legítima que deve ser validada, nunca minimizada.

### Ângulos de contorno (matéria-prima — adapte ao medo específico que o lead trouxe, não recite)
- [Ângulo 1: validar o medo como comum e legítimo]
- [Ângulo 2: o que diferencia a abordagem — técnicas, supervisão, experiência com casos assim]
- [Ângulo 3: separar o cenário temido do cenário real com acompanhamento]

### Linhas de Reforço
- "[Linha alternativa de conforto 1]"
- "[Linha alternativa de conforto 2]"

### Transição para Agendamento
"[Linha que faz ponte do conforto para a ação]"

---

## OBJEÇÃO: Tempo / "Estou sem tempo"
Tags: tempo, ocupado, agenda, sem tempo, depois, correria

### Contexto
Objeções de tempo frequentemente mascaram outras preocupações. Use urgência sutil sobre consequências do adiamento.

### Ângulos de contorno (matéria-prima — adapte à rotina que o lead descreveu, não recite)
- [Ângulo 1: o serviço foi desenhado pra rotina intensa — encaixe e praticidade]
- [Ângulo 2: o custo de adiar — o que continuar como está custa pra ELE]
- [Ângulo 3: o primeiro passo é rápido/simples]

---

## OBJEÇÃO: "Vou pensar" / Pesquisando
Tags: pensar, pensando, considerar, decidir, pesquisar, comparando, indeciso

### Contexto
Esta é frequentemente a objeção mais difícil porque o motivo real está escondido. Investigue antes de responder.

### Ângulos de contorno (matéria-prima — adapte ao que o lead está ponderando, não recite)
- [Ângulo 1: validar a pesquisa/reflexão como decisão responsável]
- [Ângulo 2: a avaliação como coleta de informação pra decidir melhor, não compromisso]
- [Ângulo 3: manter continuidade — deixar o próximo passo encaminhado]

---

## OBJEÇÃO: Experiência Anterior Ruim
Tags: experiência ruim, trauma, decepção, profissional ruim, não gostei

### Contexto
Leads com experiências anteriores ruins carregam frustração e desconfiança. Precisam de empatia extra e diferenciação.

### Ângulos de contorno (matéria-prima — adapte ao que deu errado na experiência dele, não recite)
- [Ângulo 1: acolher a frustração de verdade, sem defender o mercado]
- [Ângulo 2: o que é diferente aqui — sem prometer o que não pode]
- [Ângulo 3: entender o caso dele como chance de corrigir a rota]

Nunca fabricar para reconquistar: sem "já registrei sua reclamação", sem desconto inventado, sem "agendei pra você".

---

## OBJEÇÃO: "Cliquei sem querer"
Tags: sem querer, engano, erro, não queria

### Ângulos de contorno (matéria-prima — leve, sem pressão)
- [Ângulo 1: acolher com humor leve, zero cobrança]
- [Ângulo 2: uma frase só sobre o que o serviço resolve, como porta aberta]
- [Ângulo 3: se não houver interesse, encerrar com elegância na hora — esta objeção não conta pro teto de 3]

---

## TÉCNICA: Perguntas SPIN por Serviço
Tags: spin, qualificação, perguntas, descoberta, necessidade

### Para [Serviço 1]:

**Situação:**
- "[Pergunta sobre estado atual]"
- "[Pergunta sobre histórico]"

**Problema:**
- "[Pergunta sobre pontos de dor]"
- "[Pergunta sobre tentativas anteriores]"

**Implicação:**
- "[Pergunta sobre consequências se não resolver]"
- "[Pergunta sobre impacto no dia a dia]"

**Necessidade:**
- "[Pergunta sobre cenário ideal]"
- "[Pergunta sobre o que traria segurança na decisão]"

### Para [Serviço 2]:
[Mesma estrutura]

---

## TÉCNICA: Gatilhos de Persuasão
Tags: gatilhos, autoridade, escassez, prova social, urgência, exclusividade

**Autoridade:** "[Declaração usando métricas de autoridade]"
**Escassez:** "[Declaração criando escassez sem ser desonesto]"
**Prova Social:** "[Declaração alavancando números e histórico]"
**Urgência:** "[Declaração sobre consequências do adiamento]"
**Exclusividade:** "[Declaração sobre atenção personalizada]"

---

## FAQ: [Tópico 1]
Tags: [termos de busca relevantes]

**P:** "[Pergunta comum]"
**R:** "[Resposta natural]"

---

## FAQ: [Tópico 2]
Tags: [termos de busca relevantes]

**P:** "[Pergunta comum]"
**R:** "[Resposta natural]"

---

## TEMPORAL: Restrições de Agenda
Tags: feriado, fechado, férias, recesso, agenda, restrição

**Restrições Atuais:**
- [Fechamento/restrição com datas]

**Agenda Regular:**
- [Dia]: [Horários]
- [Dia fechado]: FECHADO

*Esta seção deve ser atualizada sempre que houver mudanças na agenda.*
```
