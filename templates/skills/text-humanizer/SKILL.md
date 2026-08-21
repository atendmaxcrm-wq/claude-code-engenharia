---
name: text-humanizer
description: Reescreve textos gerados por IA para soar naturais e humanos, evitando detecção por ferramentas como GPTZero, Turnitin, Originality.ai e Copyleaks. Use esta skill sempre que o usuário pedir para humanizar texto, tornar texto mais natural, reescrever texto de IA, fazer texto parecer humano, evitar detecção de IA, ou quando mencionar termos como 'humanizar', 'natural', 'menos robótico', 'parecer humano', 'soar humano', 'detecção de IA'. Também ativa quando o usuário cola um texto e pede para melhorar o tom, tornar mais pessoal, ou remover tom de IA/chatbot. Funciona em português e inglês.
---

# Text Humanizer | Skill de Humanização de Texto

Transforma textos gerados por IA em escrita que soa autenticamente humana, aplicando técnicas baseadas em como detectores de IA realmente funcionam.

## Filosofia Central

Detectores de IA medem principalmente duas coisas:
1. **Perplexidade**: quão previsível é a escolha de palavras. IA escolhe palavras estatisticamente prováveis (baixa perplexidade). Humanos fazem escolhas inesperadas e contextuais (alta perplexidade).
2. **Burstiness**: variação no comprimento e complexidade das frases. IA mantém frases uniformes. Humanos misturam frases curtas com longas, fragmentos com períodos elaborados.

Além disso, detectores analisam: distribuição de vocabulário, coerência de tópico, entropia linguística, padrões gramaticais excessivamente perfeitos e uso de "palavras típicas de IA".

A humanização eficaz não é trocar sinônimos. É **reconstruir semanticamente** o texto com padrões estatísticos humanos.

---

## Processo de Humanização (5 Camadas)

Ao receber um texto para humanizar, aplique as 5 camadas na ordem:

### Camada 1: Diagnóstico Rápido
Antes de reescrever, identifique os sinais de IA no texto:
- Frases com comprimento uniforme (baixa burstiness)
- Vocabulário excessivamente formal ou genérico
- Estrutura previsível (introdução → desenvolvimento → conclusão mecânica)
- Palavras-bandeira de IA (ver lista em `references/ai-red-flags.md`)
- Gramática perfeita demais (sem nenhuma contração ou coloquialismo)
- Voz passiva excessiva
- Uso excessivo de travessões (—) para apartes e explicações inline
- Transições genéricas ("Além disso", "É importante notar", "Vale ressaltar")
- Tom neutro e impessoal uniforme

### Camada 2: Reestruturação de Burstiness
Quebre a uniformidade das frases:
- Alterne frases curtas (3-8 palavras) com longas (20-35 palavras)
- Inclua um fragmento de frase ocasional. Assim.
- Use vírgulas, parênteses ou pontos para quebrar o ritmo, em vez de travessões
- Comece algumas frases com conjunções (E, Mas, Porém)
- Varie a estrutura: nem toda frase precisa de sujeito-verbo-complemento
- Crie "respirações" no texto, com parágrafos de uma frase só entre parágrafos maiores

### Camada 3: Elevação de Perplexidade
Torne as escolhas de palavras menos previsíveis:
- Substitua palavras genéricas por escolhas específicas e contextuais
- Use expressões idiomáticas e coloquialismos naturais do público-alvo
- Troque construções formais por alternativas conversacionais
- Adicione metáforas ou comparações inesperadas (quando o contexto permitir)
- Evite a "próxima palavra mais provável", escolha a segunda ou terceira opção natural
- Insira termos do vocabulário real da pessoa/profissão, não o vocabulário "genérico culto"

### Camada 4: Injeção de Humanidade
Adicione elementos que IA não consegue replicar naturalmente:
- **Opinião pessoal**: "Na minha experiência...", "O que eu percebi foi..."
- **Imperfeição controlada**: Uma vírgula a menos aqui, uma frase que começa informal ali
- **Referências concretas**: Nomes de ferramentas, situações específicas, números reais
- **Tom emocional variado**: Entusiasmo em um trecho, pragmatismo em outro
- **Perguntas retóricas**: Quebram o monólogo e criam proximidade
- **Contrações e oralidade**: "pra" em vez de "para" (quando o contexto for informal), "né", "tipo"
- **Humor sutil ou ironia leve**: Quando apropriado ao contexto

### Camada 5: Calibração de Contexto
Ajuste o resultado final ao propósito:
- **Profissional/LinkedIn**: Manter formalidade mas com personalidade, opinião e ritmo variado
- **Acadêmico**: Manter rigor mas variar estrutura e evitar palavras-bandeira
- **Casual/Redes sociais**: Maximizar oralidade, fragmentos, expressões regionais
- **Comercial/Marketing**: Ritmo dinâmico, frases de impacto, chamadas diretas
- **Resposta de formulário/vaga**: Equilíbrio entre profissional e pessoal, com experiências concretas

---

## Palavras e Padrões Bandeira

Consulte `references/ai-red-flags.md` para a lista completa. Resumo rápido:

**Palavras que gritam "IA escreveu isso" (PT-BR):**
Inovar, alavancar, otimizar, robusto, abrangente, holístico, sinergias, paradigma, disruptivo, implementar soluções, no cenário atual, diante disso, nesse contexto, vale ressaltar, é importante destacar, cabe mencionar, dessa forma, sendo assim, em suma, portanto

**Palavras que gritam "IA escreveu isso" (EN):**
Delve, tapestry, landscape, leverage, robust, comprehensive, multifaceted, nuanced, pivotal, streamline, foster, realm, intricacies, embark, moreover, furthermore, it's worth noting, in today's world

**Padrões estruturais de IA:**
- Começar com "No mundo atual..." ou "Em um cenário cada vez mais..."
- Listas com exatamente 3-5 itens, todos com comprimento similar
- Conclusão que repete a introdução parafraseada
- Cada parágrafo com exatamente o mesmo número de frases
- Transições mecânicas entre todos os parágrafos

---

## Como Aplicar a Skill

Quando o usuário pedir para humanizar um texto:

1. Leia o texto original completo
2. Identifique o **contexto de uso** (formulário de vaga? post LinkedIn? e-mail? artigo?)
3. Identifique o **nível de formalidade** esperado
4. Aplique as 5 camadas na ordem
5. Entregue o texto reescrito SEM explicar as técnicas usadas (a menos que o usuário peça)
6. Se o texto for curto (< 100 palavras), reescreva diretamente
7. Se o texto for longo (> 300 palavras), reescreva por seções

**Regras absolutas:**
- NUNCA use palavras da lista de bandeiras vermelhas
- NUNCA use travessões (—) no texto humanizado. Eles são um marcador forte de IA. Use vírgulas, pontos, parênteses ou reescreva a frase
- NUNCA mantenha todas as frases com comprimento similar
- NUNCA comece com "No mundo atual" ou equivalentes
- NUNCA termine com uma conclusão que espelha a introdução
- SEMPRE varie o tom emocional ao longo do texto
- SEMPRE inclua pelo menos uma construção que seria "improvável" para IA
- SEMPRE mantenha o significado original intacto
- O texto humanizado deve parecer que alguém sentou e escreveu do zero, não que editou uma saída de ChatGPT

---

## Exemplo de Transformação

**Texto IA (antes):**
> No cenário atual, a experiência com plataformas de criação de agentes é fundamental para profissionais da área de tecnologia. Ao longo da minha trajetória, tive a oportunidade de trabalhar com diversas ferramentas, incluindo N8N, Evolution API e Chatwoot, que me permitiram desenvolver soluções abrangentes de atendimento automatizado. Essa experiência me proporcionou uma visão holística do processo de criação de agentes inteligentes.

**Texto Humanizado (depois):**
> Trabalho criando agentes de IA faz pouco mais de um ano. Comecei no N8N quase por acidente, um cliente precisava de um chatbot pro WhatsApp e eu precisava de uma forma de conectar tudo sem ficar refém de plataforma fechada. Desde então já foram mais de 15 agentes em produção. A stack que uso no dia a dia é N8N + Evolution API + Chatwoot, e o que mais me diferencia é que separei a lógica do agente da base de conhecimento dele, o que facilita demais a manutenção quando o cliente muda informações toda semana.

Note as diferenças: frases de tamanhos variados, detalhes concretos, tom pessoal, sem palavras-bandeira, narrativa ao invés de declarações genéricas.

---

## Referências

- `references/ai-red-flags.md` (Lista completa de palavras e padrões bandeira em PT-BR e EN)
- `references/humanization-techniques.md` (Técnicas avançadas com exemplos detalhados)
