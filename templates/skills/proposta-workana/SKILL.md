---
name: proposta-workana
description: Cria propostas vencedoras para projetos do Workana. Analisa briefing, pesquisa empresa do cliente, gera proposta personalizada e humaniza o texto final. Suporta Agent Teams para propostas que exigem scraping do site do cliente e pesquisa profunda. Use ao criar propostas para Workana, Upwork, freelancer ou qualquer plataforma freelance.
---

# Proposta Workana — Gerador de Propostas Vencedoras

Projeto alvo: $ARGUMENTS

---

## Fase 0: Coleta de Informacoes

ANTES de qualquer acao, perguntar ao usuario:

1. **Cole a descricao completa do projeto** (briefing do Workana)
2. **Qual sua area?** (dev, design, redacao, marketing, consultoria, outro)
3. **Tem site da empresa do cliente?** (Se sim, informar URL para scraping)
4. **Suas credenciais relevantes** (anos de experiencia, projetos similares, resultados, stack)
5. **Faixa de preco** (valor que pretende cobrar ou "me sugira")
6. **Prazo disponivel** (quando pode comecar e estimativa de entrega)
7. **Tom desejado** (profissional, casual-profissional, tecnico)

Se o usuario ja forneceu parte dessas informacoes nos argumentos, nao repetir a pergunta.

---

## Workflow Padrao (Sem Site do Cliente)

Usar quando: nao tem URL do cliente, briefing e simples, proposta direta.

### Passo 1: Analise do Briefing

Ler o briefing completo e extrair:
- Objetivo principal do projeto
- Requisitos tecnicos ou especificos
- Perguntas que o cliente fez
- Palavras-chave e tom do cliente
- Red flags (escopo vago, prazo impossivel, budget muito baixo)
- Nivel de sofisticacao do cliente (iniciante vs expert)

### Passo 2: Montar Proposta (Estrutura 7 Secoes)

Seguir esta estrutura rigorosamente:

**Secao 1 — Hook Personalizado (2-3 linhas)**
- Reconhecer o projeto especifico (mencionar detalhes do briefing)
- Mostrar que entendeu o desafio real (nao o obvio)
- Transmitir confianca sem arrogancia

Padroes de hook:
- "Vi que voce precisa de [X]. Ja fiz [Y vezes] e o resultado foi [Z]."
- "Li seu projeto e percebi que o desafio principal e [detalhe nao obvio]."
- "Seu projeto de [X] me chamou atencao porque [conexao pessoal/experiencia]."

NUNCA usar: "Ola, sou [nome] e tenho experiencia em..." (generico demais)

**Secao 2 — Compreensao do Problema (1 paragrafo)**
- Resumir o briefing com suas palavras
- Citar 2-3 elementos especificos do projeto
- Se o cliente fez perguntas, responder CADA uma aqui

**Secao 3 — Sua Abordagem/Solucao (2-3 paragrafos)**
- Como voce resolveria o problema
- Metodologia ou stack tecnico (se aplicavel)
- Por que essa abordagem e eficaz
- Diferenciar do que "a maioria dos freelancers faria"

**Secao 4 — Evidencia (1 paragrafo)**
- Projetos similares com resultados mensuaveis
- Numeros concretos (aumento de X%, entregue em Y dias)
- Mencionar portfolio sem colar links externos (politica Workana)

**Secao 5 — Deliverables (lista)**
- Lista clara e especifica do que sera entregue
- Nao usar termos vagos ("design moderno" -> "3 mockups em Figma + guia de estilos")
- Incluir bonus/diferenciais (revisoes, suporte pos-entrega)

**Secao 6 — Preco + Timeline (2-3 linhas)**
- Valor claro com metodologia (fixo/hora/milestones)
- Data de inicio e marcos intermediarios
- Data de conclusao

**Secao 7 — CTA (2-3 linhas)**
- Expressar interesse genuino (nao desesperado)
- Convidar para conversa ("podemos alinhar por aqui?")
- Reforcar disponibilidade ("posso comecar [dia]")
- Tom quente, humano, direto

### Passo 3: Humanizacao Obrigatoria

Aplicar as 5 camadas da skill text-humanizer no texto final:

1. **Diagnostico**: Identificar sinais de IA na proposta gerada
2. **Burstiness**: Variar comprimento das frases (curtas 3-8 palavras + longas 20-35)
3. **Perplexidade**: Trocar palavras previsiveis por escolhas contextuais
4. **Injecao de humanidade**: Opiniao pessoal, referencias concretas, tom emocional variado
5. **Calibracao**: Ajustar ao tom pedido (profissional, casual, tecnico)

**Regras absolutas da humanizacao:**
- NUNCA usar palavras-bandeira de IA (otimizar, robusto, abrangente, holístico, alavancar, implementar solucoes, no cenario atual, vale ressaltar, diante disso, nesse contexto, sendo assim)
- NUNCA usar travessoes (—) para apartes. Usar virgulas, pontos ou parenteses
- NUNCA manter frases com comprimento uniforme
- NUNCA comecar com "No mundo atual" ou equivalentes
- NUNCA usar transicoes mecanicas ("Alem disso", "E importante notar")
- SEMPRE incluir pelo menos uma construcao improvavel para IA
- SEMPRE manter significado original intacto
- O texto deve parecer que alguem sentou e escreveu do zero

### Passo 4: Validacao Final

Checklist antes de entregar:

- [ ] Proposta menciona elementos especificos do briefing?
- [ ] Respondeu todas as perguntas do cliente?
- [ ] Foco em valor do cliente (nao em voce)?
- [ ] Menos de 5 paragrafos / max 1 pagina?
- [ ] Zero erros de ortografia e acentuacao?
- [ ] Nenhuma palavra-bandeira de IA?
- [ ] Nenhum travessao?
- [ ] Frases com tamanhos variados (burstiness)?
- [ ] CTA claro e convidativo?
- [ ] Nao tem links externos (politica Workana)?
- [ ] Tom humano e natural?

### Passo 5: Salvar e Entregar

1. Salvar proposta em `/root/teste-aios/docs/propostas-workana/YYYY-MM-DD_nome-do-projeto.txt`
   - Arquivo .txt com texto plano, pronto pra copiar e colar direto no campo "Detalhes da proposta" do Workana
   - SEM markdown, SEM formatacao rica, SEM blocos de codigo
   - O campo do Workana e textarea simples (texto plano)
   - Listas com hifen (-) funcionam visualmente no texto plano
2. Entregar a proposta pronta para copiar e colar no Workana
3. Informar separadamente o que preencher no campo "De quanto tempo voce precisa para finalizar o trabalho?"

---

## Modo Agent Teams (Com Site do Cliente)

Usar quando: cliente tem site/empresa identificavel, projeto e complexo, quer proposta altamente personalizada baseada em pesquisa profunda.

### Time de Proposta

| Teammate | Tipo | Foco |
|----------|------|------|
| **scraper** | general-purpose (sonnet) | Faz scraping do site do cliente, extrai info da empresa, identifica dores e oportunidades |
| **briefing-analyst** | Explore (sonnet) | Analisa briefing do Workana, pesquisa perfil do cliente na plataforma, identifica o que ele realmente precisa |
| **proposal-writer** | general-purpose (sonnet) | Escreve a proposta seguindo a estrutura 7 secoes, usando dados do scraper e do analyst |
| **humanizer** | general-purpose (sonnet) | Aplica as 5 camadas de humanizacao, elimina palavras-bandeira, calibra tom final |

### Execucao

```
TeamCreate: { team_name: "workana-proposal", description: "Proposta personalizada para [projeto]" }

Wave 1 (paralelo — pesquisa):
- scraper: Executa site-scraper.py no site do cliente
  → Extrai: servicos, equipe, valores, clientes, tecnologia, tom de comunicacao
  → Identifica: dores, gaps, oportunidades onde o freelancer pode agregar
  → Salva em: /root/teste-aios/scraping-output/[nome-cliente]/

- briefing-analyst: Analisa briefing completo do Workana
  → Extrai: objetivo real, requisitos, perguntas, restricoes, budget
  → Identifica: palavras-chave do cliente, nivel de sofisticacao, urgencia
  → Pesquisa web: empresa do cliente, setor, concorrentes (se relevante)
  → Entrega: brief estruturado com insights

Comunicacao Wave 1: scraper avisa analyst se encontrar info relevante
(ex: "site do cliente ja tem blog, mas posts sao fracos" → analyst usa na proposta)

Wave 2 (sequencial — escrita):
- proposal-writer: Recebe dados de scraper + analyst
  → Escreve proposta com a estrutura 7 secoes
  → Personaliza com dados reais do site (mencionar servicos, problemas encontrados)
  → Inclui insights do scraping como diferencial ("vi que seu site [X], posso melhorar [Y]")
  → Envia proposta para humanizer

Wave 3 (sequencial — humanizacao):
- humanizer: Recebe proposta do writer
  → Aplica 5 camadas de humanizacao (diagnostico, burstiness, perplexidade, humanidade, calibracao)
  → Elimina TODAS as palavras-bandeira de IA
  → Elimina TODOS os travessoes
  → Garante frases com tamanhos variados
  → Calibra tom ao contexto (profissional, casual, tecnico)
  → Entrega proposta final pronta

Quality Gate:
- Checklist de validacao final (12 itens)
- Proposta passa por verificacao anti-IA (nenhuma palavra-bandeira)
- Verificacao de tamanho (max 1 pagina, 5 paragrafos)
- Verificacao de personalizacao (menciona 3+ detalhes especificos do projeto)

TeamDelete
```

### Quando NAO usar Agent Teams
- Briefing e curto e simples (1-2 frases)
- Nao tem site do cliente para pesquisar
- Proposta e para projeto pequeno (< R$500)
- Urgencia extrema (precisa enviar em 5 minutos)

Nesses casos, usar o Workflow Padrao (mais rapido, sem scraping).

---

## Principios da Proposta Perfeita

### O Que Converte (Dados da Pesquisa)

| Fator | Impacto | Como Aplicar |
|-------|---------|-------------|
| Velocidade de resposta | 78% escolhem o PRIMEIRO | Enviar em < 2h, idealmente 30min |
| Personalizacao | 31% mais conversao com < 5 paginas | Mencionar 3+ detalhes do briefing |
| Evidencia | 48% mais win rate com IA + toque pessoal | Numeros concretos, projetos similares |
| Tom humano | Detectores de IA = rejeicao imediata | 5 camadas de humanizacao obrigatorias |

### Estrutura de Preco (Referencia)

| Fase do Freelancer | Estrategia |
|-------------------|-----------|
| Iniciante (0-3 avaliacoes) | -30% do mercado, foco em ganhar reviews |
| Intermediario (3-10) | Preco de mercado, destacar resultados |
| Experiente (10+) | +50-100%, voce escolhe clientes |

### Erros Fatais (NUNCA Fazer)

- Copiar/colar proposta generica
- Enviar links externos (Behance, GitHub, portfolio) — viola politica Workana
- Pedir contato fora da plataforma (WhatsApp, email)
- Focar em voce ("tenho 10 anos") em vez do cliente ("seu problema e X")
- Proposta > 5 paragrafos / muito longa
- Preco como primeira informacao
- Nao responder perguntas especificas do briefing

### Exemplos de Transformacao

**Hook generico (RUIM):**
> Ola, sou desenvolvedor web com 10 anos de experiencia. Posso fazer seu site. Preco R$5.000. Obrigado.

**Hook personalizado (BOM):**
> Li seu projeto e vi que voce precisa de um e-commerce que integre com seu sistema de estoque. Ja fiz 3 integracoes desse tipo, a ultima pro setor de suplementos, e o cliente viu as vendas subirem 60% nos primeiros 2 meses. Minha abordagem seria comecar pela API do estoque pra garantir que os dados fluam sem atrito.

**Proposta IA (ANTES da humanizacao):**
> No cenario atual, a experiencia com desenvolvimento web e fundamental. Ao longo da minha trajetoria, tive a oportunidade de trabalhar com diversas ferramentas que me permitiram desenvolver solucoes abrangentes.

**Proposta humanizada (DEPOIS):**
> Trabalho com dev web faz 6 anos. Comecei fazendo sites em WordPress e hoje meu forte e Next.js com integracao de APIs. O que mais me diferencia e que penso na manutencao desde o dia 1, porque ja cansei de ver projeto bonito que ninguem consegue atualizar depois.

---

## Adaptacao por Plataforma

A skill funciona para qualquer plataforma freelance. Diferencas:

| Plataforma | Adaptacao |
|-----------|----------|
| **Workana** | NUNCA links externos, chat interno, escrow obrigatorio |
| **Upwork** | Pode incluir portfolio link, cover letter + proposta, Connects limitados |
| **99Freelas** | Similar ao Workana, mercado BR, links permitidos |
| **Freelancer** | Bids competitivos, destaque em preco + prazo |

---

## Nota sobre Humanizacao

A humanizacao NAO e opcional. Toda proposta gerada DEVE passar pelas 5 camadas antes de ser entregue ao usuario. Propostas com cara de IA sao rejeitadas por clientes e podem resultar em suspensao de conta.

Referencia completa da tecnica: skill `text-humanizer` em `.claude/skills/text-humanizer/SKILL.md`
